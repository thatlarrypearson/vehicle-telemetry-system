#!/usr/bin/bash
# Install_obd_log_to_csv.sh
#

export APP_HOME="/home/$(whoami)/telemetry-obd-log-to-csv"
export APP_PYTHON="/home/$(whoami)/.local/bin/python3.11"
export DEBUG="True"

# Debugging support
if [ "${DEBUG}" = "True" ]
then
	# enable shell debug mode
	set -x
fi

cd ${APP_HOME}

if [ -d "${APP_HOME}/dist" ]
then
	rm -rf "${APP_HOME}/dist"
fi

${APP_PYTHON} -m pip uninstall -y telemetry-obd-log-to-csv

${APP_PYTHON} -m build .
ls -l dist/*.whl
${APP_PYTHON} -m pip install dist/*.whl

${APP_PYTHON} -m obd_log_to_csv.obd_log_to_csv --help
${APP_PYTHON} -m obd_log_to_csv.obd_log_evaluation --help
${APP_PYTHON} -m obd_log_to_csv.csv_to_delta_csv --help
${APP_PYTHON} -m obd_log_to_csv.csv_to_ratio_csv --help
