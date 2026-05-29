import json
import numpy as np
from tqdm import tqdm

from paths import SELECTED_DIR, DATA_DIR, WITH_AH_PATH, AH_SRC_CONF_PATH


def calculate_from_rh(temp, rh):
    raise NotImplementedError

def calculate_from_dd(temp, dd):
    T_d = temp - dd
    e = 6.112 * np.exp(17.67 * T_d / (T_d + 243.5))
    ah = 216.7 * e / (temp + 273.15)
    return ah



def create_ah_dataset(name):
    arrs = np.load(SELECTED_DIR / f"{name}.npz")

    arrs_new = {}

    for key in tqdm(list(arrs.keys())):
        arr = arrs[key]

        ah_src_str = name.split('_')[-1]
        ah_src = arr[:, 3]
        temp = arr[:, 2]


        ah = calculate_from_rh(temp, ah_src) if ah_src_str == "rh" else calculate_from_dd(temp, ah_src)

        new_arr = np.hstack((arr[:, :3], ah.reshape(-1, 1)))

        arrs_new[key] = new_arr


    np.savez(WITH_AH_PATH, **arrs_new)

def main():
    with open(AH_SRC_CONF_PATH, 'r') as f:
        ah_src_conf = json.load(f)
    
    create_ah_dataset(ah_src_conf["filename"])

if __name__ == "__main__":
    main()
# Launch with command:
"""
python -m preprocessing.calculate_ah
"""
