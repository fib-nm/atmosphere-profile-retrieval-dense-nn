import requests
import time

from pathlib import Path
from datetime import datetime
from zipfile import ZipFile
from tqdm import tqdm
import numpy as np

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from paths import STATIONS_RAW_DIR, ZIP_DIR, CONTROL_FILE_PATH


DATA_URL = "https://www.ncei.noaa.gov/data/integrated-global-radiosonde-archive/access/data-por/"

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Host": "www.ncei.noaa.gov",
    "Priority": "u=0, i",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-GPC": "1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:148.0) Gecko/20100101 Firefox/148.0"
}

"""
Header Record Format:
---------------------------------
Variable   Columns  Type
---------------------------------
HEADREC       1-  1  Character
ID            2- 12  Character
YEAR         14- 17  Integer
MONTH        19- 20  Integer
DAY          22- 23  Integer
HOUR         25- 26  Integer
RELTIME      28- 31  Integer
NUMLEV       33- 36  Integer
P_SRC        38- 45  Character
NP_SRC       47- 54  Character
LAT          56- 62  Integer
LON          64- 71  Integer
---------------------------------

Data Record Format:
-------------------------------
Variable        Columns Type  
-------------------------------
LVLTYP1         1-  1   Integer
LVLTYP2         2-  2   Integer
ETIME           4-  8   Integer
PRESS          10- 15   Integer
PFLAG          16- 16   Character
GPH            17- 21   Integer
ZFLAG          22- 22   Character
TEMP           23- 27   Integer
TFLAG          28- 28   Character
RH             29- 33   Integer
DPDP           35- 39   Integer
WDIR           41- 45   Integer
WSPD           47- 51   Integer
-------------------------------
"""
# For slices you should subtract 1 from left number

# Sounding slices
PRESS_SLICE = slice(9, 15)
GP_HEIGHT_SLICE = slice(16, 21)
TEMP_SLICE = slice(22, 27)
HUMIDITY_SLICE = slice(28, 33)
DEWPOINT_DEPRESSION_SLICE = slice(34, 39)

# Date slices
YEAR_SLICE = slice(13, 17)
MONTH_SLICE = slice(18, 20)
DAY_SLICE = slice(21, 23)
HOUR_SLICE = slice(24, 26)

WAIT_TIME = 1 # seconds

# ================================= scraping =================================

def download_station_zip(station_id, session):
    ZIP_DIR.mkdir(parents=True, exist_ok=True)
    station_file = ZIP_DIR / f"{station_id}-data.txt.zip"

    url = f"{DATA_URL}{station_id}-data.txt.zip"

    retry = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
    )

    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    with session.get(url, headers=HEADERS, stream=True) as r:
        r.raise_for_status()

        total_size = int(r.headers.get('content-length'))

        chunk_size = 1024  # 1 KiB

        with open(station_file, 'wb') as f, tqdm(desc="Fetching", total=total_size, unit='B', unit_scale=True, unit_divisor=1024) as progress_bar:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    progress_bar.update(len(chunk))


# ================================= parsing =================================

def is_sorted(a):
    return np.all(a[:-1] <= a[1:])


def parse_sounding(sounding, station_id, cur_date):
    nrows = len(sounding)
    if nrows == 0:
        return

    # pressure, gp_heights, temperature, relative_humidity, dewpoint_depression
    s_array = np.asarray(sounding, dtype=np.float32)
    if s_array.ndim == 1:
        s_array = s_array.reshape(1, 5)

    # To more convenient units
    pressures = s_array[:, 0] # Pa
    heights = s_array[:, 1] # geometric and geopotential heights are almost the same for heights below 20 km
    temps = s_array[:, 2] / 10 # C
    relative_humidity = s_array[:, 3] / 1000
    dewpoint_depression = s_array[:, 4] / 10 # C

    final_array = np.hstack(
        (heights.reshape(-1, 1), pressures.reshape(-1, 1), temps.reshape(-1, 1), relative_humidity.reshape(-1, 1), dewpoint_depression.reshape(-1, 1))
    )

    if not is_sorted(final_array[:, 0]):
        print(f"{station_id}, {cur_date}: not sorted sounding.")
        final_array = final_array[final_array[:, 0].argsort()]

    return final_array.astype(np.float32)

def parsing_loop(data_stream, station_id, file_size):
    cur_date = None
    cur_rows = []

    date_array_dict = {}

    print("Parsing.")
    with tqdm(total=file_size, unit='B', unit_scale=True, unit_divisor=1024) as progress_bar:
        for line_b in data_stream:
            progress_bar.update(len(line_b))

            line = line_b.decode('utf-8')

            if line[0] == "#":
                if cur_date is not None:
                    arr = parse_sounding(cur_rows, station_id, cur_date)
                    if arr is not None:
                        date_array_dict[cur_date] = parse_sounding(cur_rows, station_id, cur_date)
                cur_rows.clear()

                year = line[YEAR_SLICE]
                month = line[MONTH_SLICE]
                day = line[DAY_SLICE]
                hour = line[HOUR_SLICE]

                cur_date = f"{year}-{month}-{day}-{hour}"
            else:
                pressure = int(line[PRESS_SLICE])
                gp_height = int(line[GP_HEIGHT_SLICE])
                temperature = int(line[TEMP_SLICE])
                relative_humidity = int(line[HUMIDITY_SLICE])
                dewpoint_depression = int(line[DEWPOINT_DEPRESSION_SLICE])

                row = [pressure, gp_height, temperature, relative_humidity, dewpoint_depression]

                no_nans = True
                for i in range(len(row)):
                    if row[i]==-9999 or row[i]==-8888:
                        row[i] = np.nan
                
                if np.isnan(row[0]) or np.isnan(row[1]) or np.isnan(row[2]):
                    continue

                if np.isnan(row[3]) and np.isnan(row[4]):
                    continue
                
                cur_rows.append(row)

        if cur_date is not None:
            arr = parse_sounding(cur_rows, station_id, cur_date)
            if arr is not None:
                date_array_dict[cur_date] = parse_sounding(cur_rows, station_id, cur_date)

    data_path = STATIONS_RAW_DIR / f"{station_id}.npz"
    np.savez(data_path, **date_array_dict)



def parse_station_zip(station_id):
    STATIONS_RAW_DIR.mkdir(parents=True, exist_ok=True)

    data_path = STATIONS_RAW_DIR / f"{station_id}.npz"

    if data_path.exists():
        data_path.unlink()


    zip_path = ZIP_DIR / f"{station_id}-data.txt.zip"
    if not zip_path.exists():
        raise Exception(f"Error: {station_id}-data.txt.zip does not exist!")

    with ZipFile(zip_path, 'r') as myzip:
        filename = f"{station_id}-data.txt"

        total_size = myzip.getinfo(filename).file_size

        with myzip.open(filename, 'r') as myfile:
            parsing_loop(myfile, station_id, total_size)



# ================================= deleting =================================

def delete_zip(station_id):
    print("Deleting")
    station_file = ZIP_DIR / f"{station_id}-data.txt.zip"

    if station_file.exists():
        station_file.unlink()


# ================================= main =================================

def check_line(line):
    if len(line.split()) != 2:
        raise Exception("Wrong control file format")

    command, station_ids = line.split()

    if len(command) == 0:
        raise Exception("Command is empty")
    
    if len(station_ids) == 0:
        raise Exception("Station ID list is empty")
    
    command_set = set(command)

    if len(command_set) != len(command):
        raise Exception("Wrong command format")
    
    allowed_chars = {"f", "p", "d"}
    if not command_set <= allowed_chars:
        raise Exception("Wrong command format")


def main():
    with requests.Session() as s, open(CONTROL_FILE_PATH) as control_f:
        for line in control_f:
            if len(line) == 0 or line[0] == "#":
                continue
            
            check_line(line)

            command, station_ids = line.split()

            station_id_list = station_ids.split(",")

            list_len = len(station_id_list)

            for i in range(list_len):
                print(f"Station {station_id_list[i]} ({i+1}/{list_len}) processing started ==============================")
                
                if "f" in command:
                    time.sleep(WAIT_TIME)
                    download_station_zip(station_id_list[i], s)
                
                if "p" in command:
                    parse_station_zip(station_id_list[i])
                
                if "d" in command:
                    delete_zip(station_id_list[i])
                
                print(f"Station {station_id_list[i]} ({i+1}/{list_len}) processing completed ============================")

if __name__ == "__main__":
    main()
# Launch with command:
"""
python -m preprocessing.soundings
"""
