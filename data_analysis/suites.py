import humanize as h
import numpy as np

from data_analysis.set_functions import set_stats, hist, rank_size_plot, cumulative_plot
from data_analysis.get_data import get_station_soundings, get_raw_station_sizes, load_non_nan_data, get_elevations
from paths import WITH_AH_PATH

def soundings_suite():
    soundings = get_station_soundings()
    set_stats(soundings, "soundings", "soundings", lambda x: h.intcomma(int(x)))
    hist(soundings, 100, 100, "Soundings histogram", "Soundings")
    rank_size_plot(soundings, "Soundings rank-size plot", "Soundings")
    cumulative_plot(soundings, "Soundings cumulative plot")

def elevation_suite():
    elevations = get_elevations()
    set_stats(elevations, "elevation", None)
    hist(elevations, 100, 100, "Elevation histogram", "Elevation, m")

def raw_size_suite():
    size = get_raw_station_sizes()
    set_stats(size, "size", "size", lambda x: h.naturalsize(x, binary=True, format='%.2f'))
    hist(size, 100, 100, "Raw dataset size histogram", "Size, MiB", lambda x, pos: f"{x / (1024**2):.1f}")
    rank_size_plot(size, "Size rank-size plot", "Size, MiB", lambda x, pos: f"{x / (1024**2):.1f}")
    cumulative_plot(size, "Size cumulative plot")


def non_nan_suite():
    data = load_non_nan_data()

    soundings = data["soundings"]

    max_heights = data["max_heights"]
    min_heights = data["min_heights"]
    min_height_minus_elevation = data["min_height_minus_elevation"]
    max_hstep = data["max_hstep"]
    measurements = data["measurements"]

    not_nan_rh = data["not_nan_rh"]
    not_nan_dd = data["not_nan_dd"]

    print("Soundings.")
    set_stats(soundings, "soundings", "soundings", lambda x: h.intcomma(int(x)))
    hist(soundings, 100, 100, "Non NaN soundings histogram", "Soundings")

    print("Max heights.")
    set_stats(max_heights, "max height", None)
    hist(max_heights, 100, 100, "Max height histogram", "Max Height")

    print("Min heights.")
    set_stats(min_heights, "min height", None)
    hist(min_heights, 100, 100, "Min height histogram", "Min Height")

    print("Gap height.")
    set_stats(min_height_minus_elevation, "gap height", None)
    hist(min_height_minus_elevation, 1000, 100, "Gap height histogram", "Gap height")

    print("Max hstep.")
    set_stats(max_hstep, "max hstep", None)
    hist(max_hstep, 100, 100, "Max hstep histogram", "Max hstep")

    print("Measurements.")
    set_stats(measurements, "measurements", "measurements", lambda x: h.intcomma(int(x)))
    hist(measurements, 100, 100, "Measurements histogram", "Measurements")

    print(f"Not NaN relative humidities: {h.intcomma(not_nan_rh)}")
    print(f"Not NaN dewpoint depressions: {h.intcomma(not_nan_dd)}")


def ah_suite():
    arrs = np.load(WITH_AH_PATH)

    min_heights = []

    for key in arrs:
        arr = arrs[key]
        heights = arr[:, 0]

        min_heights.append(heights[0])
    
    min_h = np.asarray(min_heights)
    print(f"Min height: {np.min(min_h)}")


if __name__ == "__main__":
    ah_suite()
# Launch with command:
"""
python -m data_analysis.suites
"""
