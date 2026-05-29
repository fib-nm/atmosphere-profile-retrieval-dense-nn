from pathlib import Path
import json
from tqdm import tqdm
import subprocess as sp
import numpy as np

from paths import ZIP_DIR, STATION_DICT_PATH, STATIONS_RAW_DIR, PROJECT_DIR, EMPTY_DIR_PATH, SELECTED_DIR


def list_existing_zips():
    sids = []
    for fname in ZIP_DIR.iterdir():
        sid = fname.stem.split('-')[0]
        sids.append(sid)
    
    print(len(sids))
    print(",".join(sids))

def top_n_without_zips(n=None):
    present = set()
    for fname in ZIP_DIR.iterdir():
        sid = fname.stem.split('-')[0]
        present.add(sid)

    res = []
    with open(STATION_DICT_PATH, 'r') as f:
        station_dict = json.load(f)
        sid_list = list(station_dict.keys())

        el_num = min(len(sid_list), n) if n is not None else len(sid_list)
        for i in range(el_num):
            sid = sid_list[i]
            if sid not in present:
                res.append(sid)

    print(len(res))
    print(",".join(res))

def top_n_without_present(n=None):
    present = set()
    for fname in STATIONS_RAW_DIR.iterdir():
        sid = fname.stem
        present.add(sid)

    res = []
    with open(STATION_DICT_PATH, 'r') as f:
        station_dict = json.load(f)
        sid_list = list(station_dict.keys())

        el_num = min(len(sid_list), n) if n is not None else len(sid_list)
        for i in range(el_num):
            sid = sid_list[i]
            if sid not in present:
                res.append(sid)

    print(len(res))
    print(",".join(res))

def delete_dir_fast(dirpath):
    if not EMPTY_DIR_PATH.exists():
        EMPTY_DIR_PATH.mkdir()
    
    sp.run(["rsync", "-a", "--delete", f"{EMPTY_DIR_PATH}/", f"{dirpath}"])

    dirpath.rmdir()


def main():
    pass

if __name__ == "__main__":
    main()
