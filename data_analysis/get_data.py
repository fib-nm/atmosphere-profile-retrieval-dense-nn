from pathlib import Path
import json
from zipfile import ZipFile
import numpy as np
from tqdm import tqdm
from datetime import datetime

from paths import STATION_DICT_PATH, STATION_DICT_FULL_PATH, RAW_DATA_INFO_PATH, STATIONS_RAW_DIR


def get_station_soundings():
    sounding_number_list = []

    with open(STATION_DICT_PATH, 'r') as f:
        station_dict = json.load(f)

    for entry in station_dict.values():
        s_number = entry["soundings"]
        sounding_number_list.append(s_number)
    
    return np.asarray(sounding_number_list)

def get_elevations():
    elevations = []

    with open(STATION_DICT_PATH, 'r') as f:
        station_dict = json.load(f)
    
    for entry in station_dict.values():
        elevation = entry["elevation"]
        if elevation is not None:
            elevations.append(elevation)
    
    return np.asarray(elevations)


def get_raw_station_sizes():
    with open(STATION_DICT_FULL_PATH, 'r') as f:
        station_dict = json.load(f)

    size_list = []

    for entry in station_dict.values():
        size = entry["size, B"]
        size_list.append(size)
    
    return np.asarray(size_list)



def gather_non_nan_data():
    # This list is calculated for all stations
    soundings = []

    # Lists below are calculated for all soundings
    max_heights = []
    min_heights = []
    min_min_height_minus_elevation = []
    max_hstep = []
    measurements = []

    not_nan_rh = 0
    not_nan_dd = 0


    with open(STATION_DICT_PATH, 'r') as f:
        station_dict = json.load(f)


    for stpath in tqdm(list(STATIONS_RAW_DIR.iterdir())):
        data = np.load(stpath, allow_pickle=True)
        soundings.append(len(data))

        for date in data:
            arr = data[date]
            if arr.ndim == 0:
                continue
            
            heights = arr[:, 0]

            min_heights.append(heights[0])
            max_heights.append(heights[-1])

            elevation = station_dict[stpath.stem]["elevation"]
            if elevation is not None:
                min_height_minus_elevation.append(heights[0]-elevation)

            hsteps = np.diff(heights)
            if len(hsteps) > 0:
                max_hstep.append(np.max(hsteps))
            
            measurements.append(len(heights))


            rh = arr[:, 3]
            dd = arr[:, 4]

            not_nan_rh += np.sum(~np.isnan(rh))
            not_nan_dd += np.sum(~np.isnan(dd))



    dt = datetime.now()
    print(f"Started writing data: {dt.strftime("%H:%M:%S")}")

    np.savez(RAW_DATA_INFO_PATH, soundings=np.asarray(soundings), max_heights=np.asarray(max_heights),
        min_heights=np.asarray(min_heights), min_height_minus_elevation=np.asarray(min_height_minus_elevation),
        max_hstep=np.asarray(max_hstep), measurements=np.asarray(measurements), not_nan_rh=np.asarray(not_nan_rh), not_nan_dd=np.asarray(not_nan_dd))

    print(f"Finished writing data: {dt.strftime("%H:%M:%S")}")

def load_non_nan_data():
    data = np.load(RAW_DATA_INFO_PATH)
    return data


if __name__ == "__main__":
    gather_non_nan_data()
# Launch with command:
"""
python -m data_analysis.get_data
"""
