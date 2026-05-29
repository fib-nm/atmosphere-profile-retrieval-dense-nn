import shutil
import json
import humanize as h
from tqdm import tqdm
from pathlib import Path
import numpy as np
import random
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from paths import WITHOUT_MM_PATH, BT_PATH, STATION_DICT_PATH, WITH_AH_PATH, MM_PROFILES_PATH, INPUTS_DIR, AH_INPUTS_TRAIN_PATH, BT_INPUTS_TRAIN_PATH, CZ_INPUTS_TRAIN_PATH, DATE_INPUTS_TRAIN_PATH, GHEIGHT_INPUTS_TRAIN_PATH, GAH_INPUTS_TRAIN_PATH, MM_INPUTS_TRAIN_PATH, AH_INPUTS_TEST_PATH, BT_INPUTS_TEST_PATH, CZ_INPUTS_TEST_PATH, DATE_INPUTS_TEST_PATH, GHEIGHT_INPUTS_TEST_PATH, GAH_INPUTS_TEST_PATH, MM_INPUTS_TEST_PATH

# Utility functions
def train_test_split(array_list, test_prop):
    N = array_list[0].shape[0]
    ind = int((1 - test_prop) * N)

    train_list = [arr[:ind, :] for arr in array_list]
    test_list = [arr[ind:, :] for arr in array_list]

    return train_list, test_list

def normalize(X_train, X_test):
    scaler = StandardScaler()

    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    return X_train, X_test

def one_hot_encode(X_train, X_test):
    enc = OneHotEncoder(sparse_output=False, handle_unknown='ignore', dtype=np.float32)
    X_train = enc.fit_transform(X_train)
    X_test = enc.transform(X_test)

    return X_train, X_test


def cyclical_encode(values, period):
    angles = 2 * np.pi * values / period

    sin_component = np.sin(angles)
    cos_component = np.cos(angles)

    return np.stack([sin_component, cos_component], axis=1)

def encode_date(x):
    months = x[:, 0]
    hours = x[:, 1]

    month_encoded = cyclical_encode(months, 12)
    hour_encoded = cyclical_encode(hours, 24)

    return np.concatenate(
        [month_encoded, hour_encoded],
        axis=1
    )

# Getters
def get_ah_dict():
    profiles_archieve = np.load(WITHOUT_MM_PATH)

    ah_dict = {}
    for key in tqdm(list(profiles_archieve.keys()), desc="ah_dict"):
        ah = profiles_archieve[key][:, 2]
        ah_dict[key] = ah
    
    return ah_dict

def get_cz_dict(keys):
    with open(STATION_DICT_PATH, 'r') as f:
        station_dict = json.load(f)
    
    cz_dict = {}
    for key in tqdm(keys, desc="cz_dict"):
        sid = key.split('.')[0]
        cz = station_dict[sid]["climate zone"]

        cz_dict[key] = np.array([cz])
    
    return cz_dict


def is_leap_year(year):
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

def get_date_dict(keys):
    with open(STATION_DICT_PATH, 'r') as f:
        station_dict = json.load(f)
            
    date_dict = {}
    for key in tqdm(keys, desc="date_dict"):
        sid, date = key.split('.')
        _, month, _, utc_hour = date.split('-')
        
        month_int = int(month) - 1

        lon = station_dict[sid]["longitude"]
        local_hour = (int(hour) + lon/15) % 24
        
        date_dict[key] = np.array([month_int, local_hour], dtype=np.float32)

    return date_dict

def get_gheight_dict(keys):
    with_ah_archieve = np.load(WITH_AH_PATH)

    gheight_dict = {}
    for key in tqdm(keys, desc="gheight_dict"):
        gheight = with_ah_archieve[key][0, 0]
        gheight_dict[key] = np.array([gheight])
    
    return gheight_dict

def get_gah_dict(keys):
    with_ah_archieve = np.load(WITH_AH_PATH)

    gah_dict = {}
    for key in tqdm(keys, desc="gah_dict"):
        gah = with_ah_archieve[key][0, 3]
        gah_dict[key] = np.array([gah])
    
    return gah_dict

def get_mm_dict(keys):
    with open(STATION_DICT_PATH, 'r') as f:
        station_dict = json.load(f)

    mm_archieve = np.load(MM_PROFILES_PATH)

    mm_dict = {}
    for key in tqdm(keys, desc="mm_dict"):
        sid, date = key.split('.')
        cz = station_dict[sid]["climate zone"]
        lon = station_dict[sid]["longitude"]

        year, month, day, utc_hour = date.split('-')
        local_hour = (int(hour) + lon/15) % 24
        daytime = "day" if 6 <= local_hour < 18 else "night"

        mm_key = f"{cz}.{month}.{daytime}"

        mm_profile = mm_archieve[mm_key]

        idx = np.argmax(~np.isnan(mm_profile))
        mm_profile[:idx] = mm_profile[idx]

        mm_dict[key] = mm_profile
    
    return mm_dict


# Generator
def generate_datasets():
    ah_dict = get_ah_dict()
    BT_archieve = np.load(BT_PATH)
    keys_list = list(BT_archieve.keys())

    cz_dict = get_cz_dict(keys_list)
    date_dict = get_date_dict(keys_list)
    ground_height_dict = get_gheight_dict(keys_list)
    ground_ah_dict = get_gah_dict(keys_list)
    mm_dict = get_mm_dict(keys_list)


    random.shuffle(keys_list)

    dataset_size = len(keys_list)

    dict_list = [ah_dict, BT_archieve, cz_dict, date_dict, ground_height_dict, ground_ah_dict, mm_dict]

    dataset_list = []
    for d in dict_list:
        cur = np.empty((dataset_size, d[keys_list[0]].shape[0]), dtype=np.float32)
        dataset_list.append(cur)
    
    dataset_list[2] = dataset_list[2].astype(str)

    for i in tqdm(range(len(keys_list))):
        for j in range(len(dataset_list)):
            dataset_list[j][i, :] = dict_list[j][keys_list[i]]
    

    dataset_list[3] = encode_date(dataset_list[3])
    
    train_list, test_list = train_test_split(dataset_list, 0.2)

    train_list[2], test_list[2] = one_hot_encode(train_list[2], test_list[2])

    train_list[1], test_list[1] = normalize(train_list[1], test_list[1])
    train_list[4], test_list[4] = normalize(train_list[4], test_list[4])
    train_list[5], test_list[5] = normalize(train_list[5], test_list[5])
    train_list[6], test_list[6] = normalize(train_list[6], test_list[6])
    

    INPUTS_DIR.mkdir(parents=True, exist_ok=True)

    train_path_list = [AH_INPUTS_TRAIN_PATH, BT_INPUTS_TRAIN_PATH, CZ_INPUTS_TRAIN_PATH, DATE_INPUTS_TRAIN_PATH, GHEIGHT_INPUTS_TRAIN_PATH, GAH_INPUTS_TRAIN_PATH, MM_INPUTS_TRAIN_PATH]
    test_path_list = [AH_INPUTS_TEST_PATH, BT_INPUTS_TEST_PATH, CZ_INPUTS_TEST_PATH, DATE_INPUTS_TEST_PATH, GHEIGHT_INPUTS_TEST_PATH, GAH_INPUTS_TEST_PATH, MM_INPUTS_TEST_PATH]

    for i in range(len(dataset_list)):
        np.save(train_path_list[i], train_list[i])
        np.save(test_path_list[i], test_list[i])


# Main =======================================================================================================
def main():
    generate_datasets()

if __name__ == "__main__":
    main()
# Launch with command:
"""
python -m preprocessing.generate_inputs
"""
