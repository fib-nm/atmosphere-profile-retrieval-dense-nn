from pathlib import Path
import json
from zipfile import ZipFile
import humanize as h

from paths import STATION_DICT_FULL_PATH, STATION_DICT_PATH, ZIP_DIR

def get_size_list():
    sid_size_list = []

    for zpath in ZIP_DIR.iterdir():
        fname = zpath.stem

        with ZipFile(zpath, 'r') as myzip:
            total_size = myzip.getinfo(fname).file_size # B
        
        sid = fname.split('-')[0]

        sid_size_list.append((sid, total_size))
    
    sid_size_list_sorted = sorted(sid_size_list, key=lambda x: x[1], reverse=True)
    
    return sid_size_list_sorted

def get_station_dict():
    with open(STATION_DICT_PATH, 'r') as f:
        station_dict = json.load(f)
    
    return station_dict


def create_full_dict():
    station_dict_full = {}

    station_dict = get_station_dict()
    sid_size_list_sorted = get_size_list()

    for i in range(len(sid_size_list_sorted)):
        sid, size = sid_size_list_sorted[i]

        orig_entry = station_dict[sid]

        data_dict = {
            "entry number": i+1,
            "size, B": size,
            "size (human-readable)": h.naturalsize(size, binary=True, format='%.2f'),
            "soundings": orig_entry["soundings"],
            "soundings (human-readable)": orig_entry["soundings (human-readable)"],
            "latitude": orig_entry["latitude"],
            "longitude": orig_entry["longitude"],
            "climate zone": orig_entry["climate zone"],
            "elevation": orig_entry["elevation"]
        }

        station_dict_full[sid] = data_dict
    
    with open(STATION_DICT_FULL_PATH, 'w') as f:
        json.dump(station_dict_full, f, indent=4)
    

def main():
    create_full_dict()

if __name__ == "__main__":
    main()
# Launch with command:
"""
python -m preprocessing.station_dict_full
"""