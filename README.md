# atmosphere-profile-retrieval-dense-nn
Project about downloading radiosonde data from 'Integrated Global Radiosonde Archive' (IGRA), creating brightness temperature, absolute humidity and some additional datasets, and training dense neural networks on (brightness temperature - absolute humidity) pairs.
## Requirements
```
ipykernel
ipympl
jupyterlab-widgets
numpy
matplotlib
scikit-learn
tqdm
humanize
torch
torchvision
tensorboard
cartopy
kgcpy
requests
```
## Preprocessing
To download data and generate datasets, follow the steps below in order:
1. Launch `preprocessing` / `station_dict.py`
2. Set needed commands in `preprocessing` / `control` / `soundings_control_file.txt`
3. Launch `preprocessing` / `soundings.py`
4. Launch `preprocessing` / `station_dict_full.py`
5. Set needed data criteria in `preprocessing` / `control` / `criteria.json`
6. Launch `preprocessing` / `select_soundings.py`
7. Set absolute hunidity source file in `preprocessing` / `control` / `ah_source_file.json`
8. Launch `preprocessing` / `calculate_ah.py`
9. Configure interpolation in `preprocessing` / `control` / `interp_conf.json`
10. Launch `preprocessing` / `interpolate.py`
11. Configure monthly mean generation in `preprocessing` / `control` / `mm_conf.json`
12. Launch `preprocessing` / `monthly_mean.py`
13. Launch `preprocessing` / `calculate_BT.py`
14. Launch `preprocessing` / `generate_inputs.py`
## Data analysis
Notebook for using data analysis functions is in `data_analysis` / `analysis.ipynb`.

Use functions from `data_analysis` / `suites.py` for statistical analysis of data.

Use functions from `data_analysis` / `cz_functions.py` for climate zone analysis.

Use functions from `data_analysis` / `plot_random_profiles.py` to plot various random profiles.
## Training
Main notebook for training models is in `training` / `train_model.ipynb`.

Model definitions are in `training` / `models.py`.

Use `training` / `analyze_logs.ipynb` to analyze eval loss.

Use `training` / `rand_profile.ipynb` to predict random profiles.
