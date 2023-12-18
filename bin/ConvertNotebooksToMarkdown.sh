#!/usr/bin/bash
# Requires the following packages installed:
# - ipython
# - nbconvert
export HOME=/mnt/c/Users/runar
export NOTEBOOK_DIR=${HOME}/Dropbox/src/telemetry-analysis/notebooks
export MARKDOWN_DIR=${HOME}/Dropbox/src/telemetry-analysis/markdown
if [ ! -d "${MARKDOWN_DIR}" ]
then
	echo Creating markdown directory: "${MARKDOWN_DIR}"
	mkdir --parents "${MARKDOWN_DIR}"
fi

for notebook in "${NOTEBOOK_DIR}"/*.ipynb
do
	echo Converting $(basename "${notebook}") to markdown.
	python3.11 -m jupyter nbconvert "${notebook}" --to markdown --output-dir "${MARKDOWN_DIR}"
	echo
done
