#!/usr/bin/bash
# wthr_logger.sh
#
# Runs Weather Logger

# Need time for Weather interface recover after failure
export RESTART_DELAY=10

export APP_ID="wthr"
export APP_HOME="/home/$(whoami)/telemetry-data"
export APP_TMP_DIR="${APP_HOME}/tmp"
export APP_BASE_PATH="${APP_HOME}/data"
export APP_PYTHON="/home/$(whoami)/.local/bin/python3.11"
export DEBUG="True"

# get next application startup counter
export APP_COUNT=$(${APP_PYTHON} -m tcounter.app_counter ${APP_ID})

# get current system startup counter
export BOOT_COUNT=$(${APP_PYTHON} -m tcounter.boot_counter --current_boot_count)

export APP_LOG_FILE="telemetry-${BOOT_COUNT}-${APP_ID}-${APP_COUNT}.log"

# Debugging support
if [ "${DEBUG}" == "True" ]
then
	# enable shell debug mode
	set -x
fi

if [ ! -d "${APP_TMP_DIR}" ]
then
	mkdir --parents "${APP_TMP_DIR}"
fi

# turn off stdin
0<&-

# redirect all stdout and stderr to file
exec &> "${APP_TMP_DIR}/${APP_LOG_FILE}"

if [ ! -d "${APP_BASE_PATH}" ]
then
	mkdir --parents "${APP_BASE_PATH}"
fi

cd "${APP_HOME}"

while date '+%Y/%m/%d %H:%M:%S'
do
	${APP_PYTHON} -m wthr_logger.wthr_logger \
        --log_file_directory "${APP_BASE_PATH}"

	export RtnVal="$?"
	echo wthr_logger returns "${RtnVal}"

	sleep "${RESTART_DELAY}"
done
