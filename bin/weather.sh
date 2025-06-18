#!/usr/bin/bash
# vehicle-telemetry-system/bin/weather.sh
#
# Runs Weather Logger

export APP_ID="wthr"

# environment variables starting with "VTS_" come from /root/bin/vts.root.profile
# environment variables starting with "APP_" come from bin/vts.user.profile
source ${VTS_SOURCE_DIR}/bin/vts.user.profile

while date '+%Y/%m/%d %H:%M:%S'
do
	${APP_PYTHON} -m wthr_logger.wthr_logger --log_file_directory "${APP_BASE_PATH}"

	export RtnVal="$?"
	echo wthr_logger returns "${RtnVal}"

	sleep "${APP_RESTART_DELAY}"
done
