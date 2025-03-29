#!/usr/bin/bash
# Requires the following packages installed:
# - ipython
# - nbconvert
export HOME=/mnt/c/Users/runar
export NOTEBOOK_DIR=${HOME}/Dropbox/src/telemetry-analysis/notebooks
export PDF_DIR=${HOME}/Dropbox/src/telemetry-analysis/pdf
if [ ! -d "${PDF_DIR}" ]
then
	echo Creating PDF directory: "${PDF_DIR}"
	mkdir --parents "${PDF_DIR}"
fi

for notebook in "${NOTEBOOK_DIR}"/*.ipynb
do
	echo Converting $(basename "${notebook}") to pdf.
	python3.11 -m jupyter nbconvert "${notebook}" --to pdf --output-dir "${PDF_DIR}"
	echo
done
