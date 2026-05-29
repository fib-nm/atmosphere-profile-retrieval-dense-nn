from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
TRAINING_DIR = PROJECT_DIR / "training"
ANALYSIS_DIR = PROJECT_DIR / "data_analysis"
PREPROCESSING_DIR = PROJECT_DIR / "preprocessing"
EMPTY_DIR_PATH = PROJECT_DIR / "empty_dir"

FIGURES_DIR = ANALYSIS_DIR / "figures"
ATMRAD_DIR = PREPROCESSING_DIR / "atmrad"
CONTROL_DIR = PREPROCESSING_DIR / "control"
METADATA_DIR = PREPROCESSING_DIR / "metadata"

STATION_DICT_PATH = METADATA_DIR / "station_dict.json"
STATION_DICT_FULL_PATH = METADATA_DIR / "station_dict_full.json"
CZ_DICT_PATH = METADATA_DIR / "cz_dict.json"
MM_DICT_PATH = METADATA_DIR / "mm_dict.json"
RAW_LIST_PATH = METADATA_DIR / "raw_station_list.txt"

CRITERIA_PATH = CONTROL_DIR / "criteria.json"
CONTROL_FILE_PATH = CONTROL_DIR / "soundings_control_file.txt"
INTERP_CONF_PATH = CONTROL_DIR / "interp_conf.json"
MM_CONF_PATH = CONTROL_DIR / "mm_conf.json"
AH_SRC_CONF_PATH = CONTROL_DIR / "ah_source_file.json"

LOG_DIR = PREPROCESSING_DIR / "logs"


DATA_DIR = PROJECT_DIR / "data"
RAW_DATA_INFO_PATH = DATA_DIR / "raw_data_info.npz"
H_GRID_PATH = DATA_DIR / "h_grid.npy"
WITH_AH_PATH = DATA_DIR / "with_AH.npz"
INTERPOLATED_PATH = DATA_DIR / "interpolated.npz"
WITHOUT_MM_PATH = DATA_DIR / "without_mm.npz"
MM_PROFILES_PATH = DATA_DIR / "mm_profiles.npz"
BT_PATH = DATA_DIR / "BT_dataset.npz"

ZIP_DIR = DATA_DIR / "ZIPs"
STATIONS_RAW_DIR = DATA_DIR / "stations_raw"
SELECTED_DIR = DATA_DIR / "selected"
INPUTS_DIR = DATA_DIR / "inputs"

AH_INPUTS_TRAIN_PATH = INPUTS_DIR / "AH_inputs_train.npy"
BT_INPUTS_TRAIN_PATH = INPUTS_DIR / "BT_inputs_train.npy"
CZ_INPUTS_TRAIN_PATH = INPUTS_DIR / "CZ_inputs_train.npy"
DATE_INPUTS_TRAIN_PATH = INPUTS_DIR / "date_inputs_train.npy"
GHEIGHT_INPUTS_TRAIN_PATH = INPUTS_DIR / "gheight_inputs_train.npy"
GAH_INPUTS_TRAIN_PATH = INPUTS_DIR / "gah_inputs_train.npy"
MM_INPUTS_TRAIN_PATH = INPUTS_DIR / "mm_inputs_train.npy"

AH_INPUTS_TEST_PATH = INPUTS_DIR / "AH_inputs_test.npy"
BT_INPUTS_TEST_PATH = INPUTS_DIR / "BT_inputs_test.npy"
CZ_INPUTS_TEST_PATH = INPUTS_DIR / "CZ_inputs_test.npy"
DATE_INPUTS_TEST_PATH = INPUTS_DIR / "date_inputs_test.npy"
GHEIGHT_INPUTS_TEST_PATH = INPUTS_DIR / "gheight_inputs_test.npy"
GAH_INPUTS_TEST_PATH = INPUTS_DIR / "gah_inputs_test.npy"
MM_INPUTS_TEST_PATH = INPUTS_DIR / "mm_inputs_test.npy"

LOG_DIR = TRAINING_DIR / "runs"
CHECKPOINT_DIR = TRAINING_DIR / "checkpoints"
