#!/usr/bin/bash
# Requires the following packages installed:
# - ipython
# - nbconvert
export HOME=/mnt/c/Users/runar
export NOTEBOOK_DIR=${HOME}/Dropbox/src/telemetry-analysis/notebooks
export PYTHON_DIR=${HOME}/Dropbox/src/telemetry-analysis/python
if [ ! -d "${PYTHON_DIR}" ]
then
	echo Creating python directory: "${PYTHON_DIR}"
	mkdir --parents "${PYTHON_DIR}"
fi

for notebook in "${NOTEBOOK_DIR}"/*.ipynb
do
	echo Converting $(basename "${notebook}") to python program.
	python3.11 -m jupyter nbconvert "${notebook}" --to python --output-dir "${PYTHON_DIR}"
	echo
done
