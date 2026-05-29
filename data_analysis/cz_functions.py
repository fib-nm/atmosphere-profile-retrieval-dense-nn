from kgcpy import lookupCZ
import json
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import humanize as h
import numpy as np

from paths import STATION_DICT_PATH, STATION_DICT_FULL_PATH, SELECTED_DIR


def plot_stations():
    with open(STATION_DICT_PATH, 'r') as f:
        station_dict = json.load(f)
    
    fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()}, figsize=(6, 4))
    ax.stock_img()
    ax.set_title("Station locations")
    
    for entry in station_dict.values():
        lon = entry["longitude"]
        lat = entry["latitude"]

        if lon is None or lat is None:
            continue

        ax.scatter(lon, lat, color='blue', s=5)
    
    plt.show()


def zone_size_pychart():
    zone_size = {}
    
    with open(STATION_DICT_FULL_PATH, 'r') as f:
        station_dict = json.load(f)

    for entry in station_dict.values():
        size_b = entry["size, B"]
        cz = entry["climate zone"]

        if cz is None:
            cz = '-'

        if zone_size.get(cz) is None:
            zone_size[cz] = size_b
        else:
            zone_size[cz] += size_b

    zs_list = list(zone_size.items())
    zs_sorted = sorted(zs_list, key=lambda x: x[1], reverse=True)
    zs_h = [(zone, h.naturalsize(size_b, binary=True, format='%.2f')) for zone, size_b in zs_sorted]

    zone_list = [i[0] for i in zs_sorted]
    size_list = [i[1] for i in zs_sorted]

    fig, ax = plt.subplots(layout="constrained", figsize=(6, 4))
    ax.pie(size_list, labels=zone_list)
    ax.set_title("Zone size pie chart")
    plt.show()

    for z, s in zs_h:
        print(f"{z}: {s}")


def plot_selected_stations(name):
    with open(STATION_DICT_PATH, 'r') as f:
        station_dict = json.load(f)
    

    sids = set()

    arrs = np.load(SELECTED_DIR / f"{name}.npz")

    for key in arrs:
        sid = key.split('.')[0]
        sids.add(sid)

    
    fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()}, figsize=(6, 2))
    ax.set_title("Selected stations locations (from selected_400_dd)")
    ax.add_feature(cfeature.LAND, facecolor="lightgray")
    ax.add_feature(cfeature.OCEAN, facecolor="white")
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.7)

    for sid in sids:
        lon = station_dict[sid]["longitude"]
        lat = station_dict[sid]["latitude"]

        ax.scatter(lon, lat, color='blue', s=5)
    
    plt.show()


if __name__ == "__main__":
    plot_selected_stations("selected_400_dd")
# Launch with command:
"""
python -m data_analysis.cz_functions
"""
