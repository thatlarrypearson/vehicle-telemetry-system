#!/usr/bin/bash
#
# /bin/vts.user.profile
#
# Assumes this process started (runuser) by root with /root/bin/vts.root.profile
# and has gained basic environmental variables from the calling scripts.

# environment variables starting with "VTS_" come from /root/bin/vts.root.profile
# environment variables starting with "APP_" come from bin/vts.user.profile

# make this value the current username as set by root using runuser command
export APP_USER="$(whoami)"

# only change the following if you are comfortable making
# changes to UNIX/Linux systems
# VTS_HOME defined in root/bin/vts.root.profile
# VTS_GROUP normally defined in root/bin/vts.root.profile

export APP="vehicle-telemetry-system"

cd ${VTS_HOME}/${APP}

# activate uv and Python virtual environment
source ./.venv/Scripts/activate

# failure restart interval in seconds
export APP_RESTART_DELAY=10

export APP_PYTHON="uv run"
export APP_HOME="${VTS_HOME}/telemetry-data"
export APP_TMP_DIR="${APP_HOME}/tmp"
export APP_BASE_PATH="${APP_HOME}/data"
export DEBUG="True"

if [ ! -d "${APP_HOME}" ]
then
    mkdir --parents "${APP_HOME}"
fi

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
exec &>> "${APP_TMP_DIR}/${APP_LOG_FILE}"

date '+%Y/%m/%d %H:%M:%S'

if [ ! -d "${APP_BASE_PATH}" ]
then
	mkdir --parents "${APP_BASE_PATH}"
fi

cd "${APP_HOME}"
