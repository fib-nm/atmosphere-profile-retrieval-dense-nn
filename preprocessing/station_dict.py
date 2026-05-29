import argparse
import requests
import time
import re
import json
import shutil

from pathlib import Path
from kgcpy import lookupCZ
from bs4 import BeautifulSoup
import humanize as h

from paths import RAW_LIST_PATH, STATION_DICT_PATH


LIST_URL = "https://www.ncei.noaa.gov/data/integrated-global-radiosonde-archive/doc/igra2-station-list.txt"

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
I. FORMAT OF "igrav2.2-station-list.txt"
------------------------------
Variable   Columns   Type
------------------------------
ID            1-11   Character
LATITUDE     13-20   Real
LONGITUDE    22-30   Real
ELEVATION    32-37   Real
STATE        39-40   Character
NAME         42-71   Character
FSTYEAR      73-76   Integer
LSTYEAR      78-81   Integer
NOBS         83-88   Integer
------------------------------
"""

# Station list slices
LIST_ID_SLICE = slice(0, 11)
LIST_LATITUDE_SLICE = slice(12, 20)
LIST_LONGITUDE_SLICE = slice(21, 30)
ELEVATION_SLICE = slice(31, 37)
LIST_SOUNDINGS_SLICE = slice(82, 88)


def download_raw_data():
    # Downloading station list
    print("Started downloading raw station list")
    RAW_LIST_PATH.parent.mkdir(parents=True, exist_ok=True)

    with requests.get(LIST_URL, headers=HEADERS) as r:
        r.raise_for_status()

        with open(RAW_LIST_PATH, 'wb') as f:
            for chunk in r.iter_content(chunk_size=128):
                f.write(chunk)
    print("Finished downloading raw station list")


def parse_station_list():
    id_data = {}

    with open(RAW_LIST_PATH) as f:
        for line in f:

            stid = line[LIST_ID_SLICE].strip()
            lat = line[LIST_LATITUDE_SLICE].strip()
            lon = line[LIST_LONGITUDE_SLICE].strip()
            elevation = line[ELEVATION_SLICE].strip()
            s_number = line[LIST_SOUNDINGS_SLICE].strip()

            if len(stid) == 0:
                continue

            if elevation == "-999.9":
                continue

            lat_f = None if lat=="-98.8888" else max(float(lat), -89.999)
            lon_f = None if lon=="-998.8888" else min(float(lon), 179.999)
            elevation_f = None if elevation=="-998.8" else float(elevation)

            kg_zone = None if lat_f is None or lon_f is None else lookupCZ(lat_f, lon_f)

            s_number_int = int(s_number)

            if len(stid) > 0:
                id_data[stid] = (s_number_int, lat_f, lon_f, kg_zone, elevation_f)
    
    return id_data

def parse_station_metadata():
    if not RAW_LIST_PATH.exists():
        raise Exception("station_list.txt does not exist")
    
    id_data = parse_station_list()

    data_list = []
    for stid, stdata in id_data.items():
        data_list.append((stid, *stdata))

    data_sorted = sorted(data_list, key=lambda x: x[1], reverse=True)


    data_dict = {data_sorted[i][0]: {
        "entry number": i+1,
        "soundings": data_sorted[i][1],
        "soundings (human-readable)": h.intcomma(data_sorted[i][1]),
        "latitude": data_sorted[i][2],
        "longitude": data_sorted[i][3],
        "climate zone": data_sorted[i][4],
        "elevation": data_sorted[i][5]
    } for i in range(len(data_sorted))}


    with open(STATION_DICT_PATH, 'w') as f:
        json.dump(data_dict, f, indent=4)



def main():
    download_raw_data()
    parse_station_metadata()

if __name__ == "__main__":
    main()
# Launch with command:
"""
python -m preprocessing.station_dict
"""
