import json
import numpy as np
from kgcpy import lookupCZ
from tqdm import tqdm

from paths import SELECTED_DIR, STATION_DICT_PATH, CRITERIA_PATH, STATIONS_RAW_DIR


NO_CZ_STATIONS = set()

def no_cz_stations():
    with open(STATION_DICT_PATH, 'r') as f:
        station_dict = json.load(f)
    
    for sid, entry in station_dict.items():
        lon = entry["longitude"]
        lat = entry["latitude"]

        if lon is None or lat is None:
            NO_CZ_STATIONS.add(sid)
        else:
            lat_f = max(lat, -89.999)
            kg_zone = lookupCZ(lat_f, lon)
            if kg_zone == "Ocean":
                NO_CZ_STATIONS.add(sid)


def select(crit_dict):
    with open(STATION_DICT_PATH, 'r') as f:
        station_dict = json.load(f)
    
    max_hstep_crit = crit_dict["max_hstep"]
    if isinstance(max_hstep_crit, int):
        max_hstep_crit = [max_hstep_crit]
    
    ah_src_str = "dd" if crit_dict["abs_humidity_source"] == "dewpoint_depression" else "rh"
    names = {i: f"selected_{i}_{ah_src_str}.npz" for i in max_hstep_crit}
    data_dicts = {i: {} for i in max_hstep_crit} # Each entry is a dict {sid-date: array}

    for stpath in tqdm(list(STATIONS_RAW_DIR.iterdir())):
        data = np.load(stpath, allow_pickle=True)

        sid = stpath.stem

        if sid in NO_CZ_STATIONS:
            continue

        if station_dict[sid]["elevation"] is None:
            continue

        for date in data:
            hour = date.split('-')[-1]

            if hour == "99":
                continue

            arr = data[date]
            if arr.ndim == 0:
                continue
        
            heights = arr[:, 0] # m
            if len(heights) < 2:
                continue

            gap_height = heights[0] - station_dict[sid]["elevation"]

            if gap_height < crit_dict["gap_height"][0] or gap_height > crit_dict["gap_height"][1]:
                continue

            if heights[-1] < crit_dict["upper_bound"]:
                continue


            right = np.searchsorted(heights, crit_dict["upper_bound"], side='left') + 1
            needed = arr[:right, :]

            if crit_dict["abs_humidity_source"] == "dewpoint_depression":
                dd = needed[:, 4]
                if np.isnan(dd).any():
                    continue
            elif crit_dict["abs_humidity_source"] == "relative_humidity":
                rh = needed[:, 3]
                if np.isnan(rh).any():
                    continue
            else:
                raise Exception("Wrong AH source.")


            heights_needed = needed[:, 0]
            hsteps = np.diff(heights_needed)
            max_hstep = np.max(hsteps)

            if crit_dict["abs_humidity_source"] == "dewpoint_depression":
                new_array = np.hstack((needed[:, :3], needed[:, 4].reshape(-1, 1)))
            else:
                new_array = needed[:, :4]

            code = f"{sid}.{date}"
            for i in max_hstep_crit:
                if max_hstep <= i:
                    data_dicts[i][code] = needed


    SELECTED_DIR.mkdir(parents=True, exist_ok=True)
    for i in max_hstep_crit:
        arch_path = SELECTED_DIR / names[i]

        np.savez(arch_path, **data_dicts[i])



def main():
    no_cz_stations()
    select()

if __name__ == "__main__":
    main()
# Launch with command:
"""
python -m preprocessing.select_soundings
"""
