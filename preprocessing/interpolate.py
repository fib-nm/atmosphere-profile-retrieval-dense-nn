import json
from pathlib import Path
from tqdm import tqdm
import numpy as np

from paths import WITH_AH_PATH, INTERP_CONF_PATH, INTERPOLATED_PATH, H_GRID_PATH


def interpolate_data():
    with open(INTERP_CONF_PATH) as f:
        interp_conf = json.load(f)
    
    interp_points = interp_conf["grid_points"]
    
    h_grid = np.linspace(interp_conf["left"], interp_conf["right"], interp_points, dtype=np.float32)
    np.save(H_GRID_PATH, h_grid)

    arrs = np.load(WITH_AH_PATH)

    arrs_new = {}

    for key in tqdm(list(arrs.keys())):
        arr = arrs[key]
    
        heights = arr[:, 0]
        pressures = arr[:, 1]
        temps = arr[:, 2]
        ah = arr[:, 3]

        first_real = np.searchsorted(h_grid, heights[0], side="left")

        p_grid = np.full(interp_points, np.nan)
        t_grid = np.full(interp_points, np.nan)
        ah_grid = np.full(interp_points, np.nan)

        p_grid[first_real:] = np.interp(h_grid[first_real:], heights, pressures)
        t_grid[first_real:] = np.interp(h_grid[first_real:], heights, temps)
        ah_grid[first_real:] = np.interp(h_grid[first_real:], heights, ah)

        new_arr = np.hstack((p_grid.reshape(-1, 1), t_grid.reshape(-1, 1), ah_grid.reshape(-1, 1)))

        arrs_new[key] = new_arr

    np.savez(INTERPOLATED_PATH, **arrs_new)


def main():
    interpolate_data()

if __name__ == "__main__":
    main()
# Launch with command:
"""
python -m preprocessing.interpolate
"""
