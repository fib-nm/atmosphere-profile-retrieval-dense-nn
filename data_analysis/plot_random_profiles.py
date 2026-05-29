from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import json
import cartopy.crs as ccrs

from paths import STATION_DICT_PATH, STATIONS_RAW_DIR, SELECTED_DIR, WITH_AH_PATH, INTERPOLATED_PATH, H_GRID_PATH, MM_PROFILES_PATH, BT_PATH
from frequencies import frequencies

num_to_month = {
    "01": "January",
    "02": "February",
    "03": "March",
    "04": "April",
    "05": "May",
    "06": "June",
    "07": "July",
    "08": "August",
    "09": "September",
    "10": "October",
    "11": "November",
    "12": "December"
}

RNG = np.random.default_rng()


def choose_rand_file(dir_path, file_suffix):
    path_list = list(dir_path.rglob(f"*{file_suffix}"))
    rand_path_ind = RNG.integers(len(path_list))
    rand_path = path_list[rand_path_ind]
    
    return rand_path

def choose_rand_array(npz):
    rand_ind = RNG.integers(len(npz))

    rand_key = list(npz.keys())[rand_ind]

    rand_array = npz[rand_key]

    return rand_key, rand_array

def plot_location(lon, lat, sid):
    fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()}, figsize=(6, 4))
        
    ax.stock_img()
    
    ax.scatter(lon, lat, color='blue', s=5)

    ax.set_title(f"Station {sid} Location")
    
    plt.show()

def plot_profile(ax, h, profile, color, title, xlabel):
    ax.scatter(profile, h, color=color, s=10)
    ax.plot(profile, h, color=color)
    ax.axvline(x=0, color="black", linewidth=1, linestyle="--")
    ax.set_title(title)
    ax.set_xlabel(xlabel)



def plot_random_raw_profile():
    plt.close("all")

    with open(STATION_DICT_PATH, 'r') as f:
        station_dict = json.load(f)


    rand_sounding = np.array(None)
    while rand_sounding.ndim == 0:
        rand_station_path = choose_rand_file(STATIONS_RAW_DIR, ".npz")

        rand_sid = rand_station_path.stem
        rand_dataset = np.load(rand_station_path, allow_pickle=True)

        rand_date, rand_sounding = choose_rand_array(rand_dataset)

    year, month, day, hour = rand_date.split('-')
    time_s = f"{year} {num_to_month[month]} {day}, {hour}:00:00"

    print(f"Station ID: {rand_sid}")
    print(f"Sounding datetime: {time_s}")
    print(f"Station elevation: {station_dict[rand_sid]["elevation"]} m")
    print(f"Measurements: {len(rand_sounding)}")


    # Plot station location
    lon = station_dict[rand_sid]["longitude"]
    lat = station_dict[rand_sid]["latitude"]

    if lon is not None:
        plot_location(lon, lat, rand_sid)
    else:
        print("Station location is not known.")
    
    # Plot profiles
    heights = rand_sounding[:, 0]
    pressures = rand_sounding[:, 1]
    temps = rand_sounding[:, 2]
    rel_hums = rand_sounding[:, 3]
    dewp_depr = rand_sounding[:, 4]
    
    fig, ax = plt.subplots(1, 4, figsize=(11, 5), sharey=True, layout="constrained")

    for a in ax:
        a.grid(True, axis="y", linestyle="--", alpha=0.4)
    
    plot_profile(ax[0], heights, pressures, "blue", "Pressure profile", "Pressure, Pa")
    plot_profile(ax[1], heights, temps, "red", "Temperature profile", "Temperature, C")
    plot_profile(ax[2], heights, rel_hums, "green", "Relative humidity profile", "Relative humidity")
    plot_profile(ax[3], heights, dewp_depr, "orange", "Dewpoint depression profile", "Dewpoint depression, C")

    ax[0].set_ylabel("Height, m")
        
    plt.show()


def plot_random_selected_profile(name):
    plt.close("all")

    with open(STATION_DICT_PATH, 'r') as f:
        station_dict = json.load(f)
    
    dataset = np.load(SELECTED_DIR / f"{name}.npz")

    key, rand_sounding = choose_rand_array(dataset)

    sid, date = key.split('.')

    year, month, day, hour = date.split('-')
    time_s = f"{year} {num_to_month[month]} {day}, {hour}:00:00"

    print(f"Station ID: {sid}")
    print(f"Sounding datetime: {time_s}")
    print(f"Station elevation: {station_dict[sid]["elevation"]} m")
    print(f"Measurements: {len(rand_sounding)}")


    # Plot station location
    lon = station_dict[sid]["longitude"]
    lat = station_dict[sid]["latitude"]

    if lon is not None:
        plot_location(lon, lat, sid)
    else:
        print("Station location is not known.")
    
    # Plot profiles
    heights = rand_sounding[:, 0]
    pressures = rand_sounding[:, 1]
    temps = rand_sounding[:, 2]
    ah_source = rand_sounding[:, 3]
    
    fig, ax = plt.subplots(1, 3, figsize=(11, 5), sharey=True, layout="constrained")

    for a in ax:
        a.grid(True, axis="y", linestyle="--", alpha=0.4)
    
    plot_profile(ax[0], heights, pressures, "blue", "Pressure profile", "Pressure, Pa")
    plot_profile(ax[1], heights, temps, "red", "Temperature profile", "Temperature, C")
    if name.split('_')[-1] == "rh":
        plot_profile(ax[2], heights, ah_source, "green", "Relative humidity profile", "Relative humidity")
    else:
        plot_profile(ax[2], heights, ah_source, "orange", "Dewpoint depression profile", "Dewpoint depression, C")


    ax[0].set_ylabel("Height, m")
        
    plt.show()


def plot_random_with_ah():
    plt.close("all")

    with open(STATION_DICT_PATH, 'r') as f:
        station_dict = json.load(f)
    
    dataset = np.load(WITH_AH_PATH)

    key, rand_sounding = choose_rand_array(dataset)

    sid, date = key.split('.')

    year, month, day, hour = date.split('-')
    time_s = f"{year} {num_to_month[month]} {day}, {hour}:00:00"

    print(f"Station ID: {sid}")
    print(f"Sounding datetime: {time_s}")
    print(f"Station elevation: {station_dict[sid]["elevation"]} m")
    print(f"Measurements: {len(rand_sounding)}")


    # Plot station location
    lon = station_dict[sid]["longitude"]
    lat = station_dict[sid]["latitude"]

    if lon is not None:
        plot_location(lon, lat, sid)
    else:
        print("Station location is not known.")
    
    # Plot profiles
    heights = rand_sounding[:, 0]
    pressures = rand_sounding[:, 1]
    temps = rand_sounding[:, 2]
    ah = rand_sounding[:, 3]
    
    fig, ax = plt.subplots(1, 3, figsize=(11, 5), sharey=True, layout="constrained")

    for a in ax:
        a.grid(True, axis="y", linestyle="--", alpha=0.4)
    
    plot_profile(ax[0], heights, pressures, "blue", "Pressure profile", "Pressure, Pa")
    plot_profile(ax[1], heights, temps, "red", "Temperature profile", "Temperature, C")
    plot_profile(ax[2], heights, ah, "green", "Absolute humidity profile", r"Absolute humidity, $g/m^3$")


    ax[0].set_ylabel("Height, m")
        
    plt.show()


def plot_random_interpolated():
    plt.close("all")

    with open(STATION_DICT_PATH, 'r') as f:
        station_dict = json.load(f)
    
    dataset = np.load(INTERPOLATED_PATH)

    key, rand_sounding = choose_rand_array(dataset)

    sid, date = key.split('.')

    year, month, day, hour = date.split('-')
    time_s = f"{year} {num_to_month[month]} {day}, {hour}:00:00"

    print(f"Station ID: {sid}")
    print(f"Sounding datetime: {time_s}")
    print(f"Station elevation: {station_dict[sid]["elevation"]} m")
    print(f"Measurements: {len(rand_sounding)}")


    # Plot station location
    lon = station_dict[sid]["longitude"]
    lat = station_dict[sid]["latitude"]

    if lon is not None:
        plot_location(lon, lat, sid)
    else:
        print("Station location is not known.")
    
    # Plot profiles
    heights = np.load(H_GRID_PATH)
    pressures = rand_sounding[:, 0]
    temps = rand_sounding[:, 1]
    ah = rand_sounding[:, 2]
    
    fig, ax = plt.subplots(1, 3, figsize=(11, 5), sharey=True, layout="constrained")

    for a in ax:
        a.grid(True, axis="y", linestyle="--", alpha=0.4)
    
    plot_profile(ax[0], heights, pressures, "blue", "Pressure profile", "Pressure, Pa")
    plot_profile(ax[1], heights, temps, "red", "Temperature profile", "Temperature, C")
    plot_profile(ax[2], heights, ah, "green", "Absolute humidity profile", r"Absolute humidity, $g/m^3$")


    ax[0].set_ylabel("Height, m")
        
    plt.show()


def plot_random_mm():
    plt.close("all")
    
    dataset = np.load(MM_PROFILES_PATH)

    key, ah = choose_rand_array(dataset)

    cz, month, daytime = key.split('.')

    print(f"Climate zone: {cz}")
    print(f"Month: {num_to_month[month]}")
    print(f"Daytime: {daytime}")

    
    # Plot profiles
    heights = np.load(H_GRID_PATH)
    
    fig, ax = plt.subplots(1, 1, figsize=(3, 5), layout="constrained")

    ax.grid(True, axis="y", linestyle="--", alpha=0.4)
    plot_profile(ax, heights, ah, "green", "Absolute humidity profile", r"Absolute humidity, $g/m^3$")
    ax.set_ylabel("Height, m")
        
    plt.show()


def plot_random_BT():
    plt.close("all")

    with open(STATION_DICT_PATH, 'r') as f:
        station_dict = json.load(f)
    
    dataset = np.load(BT_PATH)

    key, BT = choose_rand_array(dataset)

    sid, date = key.split('.')

    year, month, day, hour = date.split('-')
    time_s = f"{year} {num_to_month[month]} {day}, {hour}:00:00"

    print(f"Station ID: {sid}")
    print(f"Sounding datetime: {time_s}")

    
    # Plot profiles    
    fig, ax = plt.subplots(figsize=(6, 4), layout="constrained")

    ax.scatter(frequencies, BT, color="orange", s=10)
    ax.set_title('Brightness temperatures')
    ax.set_xlabel("Frequency, GHz")
    ax.set_ylabel('Brightness temperature, K')
        
    plt.show()