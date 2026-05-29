import json
import shutil
import random
import argparse

from pathlib import Path
import numpy as np
from tqdm import tqdm

from paths import MM_CONF_PATH, INTERPOLATED_PATH, H_GRID_PATH, STATION_DICT_PATH, CZ_DICT_PATH, MM_DICT_PATH, WITHOUT_MM_PATH, MM_PROFILES_PATH


def generate_cz_dict():
    with open(STATION_DICT_PATH, 'r') as f:
        station_dict = json.load(f)
    
    arrs = np.load(INTERPOLATED_PATH)


    sid_set = set()
    for key in arrs.keys():
        sid = key.split('.')[0]
        sid_set.add(sid)
    

    cz_station = {}
    for sid in sid_set:
        entry = station_dict[sid]

        cz = entry["climate zone"]

        if cz is None:
            cz = '-'

        if cz_station.get(cz) is None:
            cz_station[cz] = [sid]
        else:
            cz_station[cz].append(sid)
        

    with open(CZ_DICT_PATH, 'w') as f:
        json.dump(cz_station, f, indent=4)



def generate_mm_dict(): # mm = monthly mean
    with open(STATION_DICT_PATH, 'r') as f:
        station_dict = json.load(f)
    
    with open(MM_CONF_PATH, 'r') as f:
        mm_conf = json.load(f)

    with open(CZ_DICT_PATH, 'r') as f:
        cz_dict = json.load(f)
    
    arrs = np.load(INTERPOLATED_PATH)


    cz_list = list(cz_dict.keys())

    arr_keys = list(arrs.keys())

    # mm_key = cz.month.daytime
    mm_dict = {}

    random.shuffle(arr_keys)

    for arr_key in arr_keys:
        sid, date = arr_key.split('.')

        cz = station_dict[sid]["climate zone"]
        lon = station_dict[sid]["longitude"]

        year, month, day, hour = date.split('-')
        local_hour = (int(hour) + lon/15) % 24
        daytime = "day" if 6 <= local_hour < 18 else "night"

        mm_key = f"{cz}.{month}.{daytime}"


        if mm_dict.get(mm_key) is None:
            mm_dict[mm_key] = []


        if len(mm_dict[mm_key]) < mm_conf["max_soundings"]:
            mm_dict[mm_key].append(arr_key)

    to_delete = []
    for mm_key, mm_list in mm_dict.items():
        if len(mm_list) < mm_conf["min_soundings"]:
            to_delete.append(mm_key)
    
    for mm_key in to_delete:
        del mm_dict[mm_key]

    with open(MM_DICT_PATH, 'w') as f:
        json.dump(mm_dict, f, indent=4)



def generate_without_mm():
    with open(STATION_DICT_PATH, 'r') as f:
        station_dict = json.load(f)

    with open(MM_DICT_PATH, 'r') as f:
        mm_dict = json.load(f)
    
    arrs = np.load(INTERPOLATED_PATH)


    used_keys = set()

    for mm_key, key_list in mm_dict.items():
        used_keys.update(key_list)

    mm_keys = set(mm_dict.keys())
    

    without_mm_dict = {}

    for key in tqdm(list(arrs.keys())):
        sid, date = key.split('.')

        if key in used_keys:
            continue
        
        cz = station_dict[sid]["climate zone"]
        year, month, day, hour = date.split('-')
        lon = station_dict[sid]["longitude"]
        local_hour = (int(hour) + lon/15) % 24
        daytime = "day" if 6 <= local_hour < 18 else "night"

        cur_key = f"{cz}.{month}.{daytime}"

        if cur_key not in mm_keys:
            continue

        without_mm_dict[key] = arrs[key]
    
    np.savez(WITHOUT_MM_PATH, **without_mm_dict)
    


def generate_mm_profiles():
    with open(MM_DICT_PATH, 'r') as f:
        mm_dict = json.load(f)

    with open(MM_CONF_PATH, 'r') as f:
        mm_conf = json.load(f)

    arrs = np.load(INTERPOLATED_PATH)

    mm_profiles_dict = {}

    for mm_key, mm_keys_list in mm_dict.items():
        if len(mm_keys_list) < mm_conf["min_soundings"]:
            raise Exception(f"Too little paths in mm_dict[{mm_key}].")

        if len(mm_keys_list) > mm_conf["max_soundings"]:
            raise Exception(f"Too many paths in mm_dict[{mm_key}].")
        
        ah_list = [arrs[key][:, 2] for key in mm_keys_list]
        ah_array = np.asarray(ah_list)

        numerator = np.nansum(ah_array, axis=0)
        denomenator = np.sum(~np.isnan(ah_array), axis=0)

        mean_profile = np.full_like(numerator, np.nan)

        valid = denomenator > 0

        mean_profile[valid] = numerator[valid] / denomenator[valid]

        mm_profiles_dict[mm_key] = mean_profile
    
    np.savez(MM_PROFILES_PATH, **mm_profiles_dict)


def main():
    generate_without_mm()
    generate_mm_profiles()

if __name__ == "__main__":
    main()
# Launch with command:
"""
python -m preprocessing.monthly_mean
"""
