import json
import concurrent.futures as cf

from pathlib import Path
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt

from preprocessing.atmrad.cpu.atmosphere import Atmosphere

from paths import WITHOUT_MM_PATH, H_GRID_PATH, BT_PATH
from frequencies import frequencies

MAX_PROCESSES = 16


def calculate_BT_parallel():
    h_grid = np.load(H_GRID_PATH) / 1000 # km

    arrs = np.load(WITHOUT_MM_PATH)

    freq_to_ind = {}
    for i in range(len(frequencies)):
        freq_to_ind[frequencies[i]] = i

    BT_dict = {}

    with cf.ProcessPoolExecutor(max_workers=MAX_PROCESSES) as executor:
        for key in tqdm(list(arrs.keys())):
            arr = arrs[key]

            p_grid = arr[:, 0] / 100 # hPa
            t_grid = arr[:, 1] # C
            ah_grid = arr[:, 2] # g/m^3

            valid = ~np.isnan(p_grid)

            h_valid = h_grid[valid]
            p_valid = p_grid[valid]
            t_valid = t_grid[valid]
            ah_valid = ah_grid[valid]

            atmosphere = Atmosphere(t_valid, p_valid, AbsoluteHumidity=ah_valid, altitudes=h_valid)

            BT_array = np.empty(len(frequencies), dtype=np.float32)

            futures = {executor.submit(atmosphere.downward.brightness_temperature, frequency=freq, background=True): freq_to_ind[freq] for freq in frequencies}

            for fut in cf.as_completed(futures):
                ind = futures[fut]
                BT = fut.result()
                BT_array[ind] = BT

            BT_dict[key] = BT_array

    np.savez(BT_PATH, **BT_dict)


def main():
    calculate_BT_parallel()

if __name__ == "__main__":
    main()
# Launch with command:
"""
python -m preprocessing.calculate_BT
"""
