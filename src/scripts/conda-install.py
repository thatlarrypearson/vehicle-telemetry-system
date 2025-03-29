# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
# run these in the terminal before starting
# conda update -n base -c defaults conda
# conda install ipywidgets

# %%
# !conda install -c conda-forge matplotlib

# %%
# !conda install ipywidgets

# %%
# !conda install pandas numpy scikit-learn seaborn

# %%
# !conda install scikit-learn-intelex

# %%
# !python -m pip install jupyter-ui-poll haversine rich nbimport

# %%
# install telemetry applications

# %%
python3.11 -m pip install --upgrade --force-reinstall --user pip
python3.11 -m pip install --upgrade --force-reinstall --user wheel setuptools markdown build

# telemetry-counter
# NOTE: you may need to remove the UltraDict dependency (pyproject.toml and setup.cfg) to build this on Windows
# cd telemetry-counter
python3.11 -m build .
python3.11 -m pip install dist/telemetry_counter-0.0.1-py3-none-any.whl
# cd ..

# telemetry-obd-log-to-csv
# cd telemetry-obd-log-to-csv
python3.11 -m build
python3.11 -m pip install --user dist/telemetry_obd_log_to_csv-0.3.3-py3-none-any.whl
# cd ..

# telemetry-obd
# cd telemetry-obd
python -m build
python -m pip install --user dist/telemetry_obd-0.4.2-py3-none-any.whl
# cd ..

# %%
# !conda env export > environment.yml

# %%
# !conda env create -f environment.yml
