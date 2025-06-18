#!/usr/bin/bash
# trlr_logger.sh
#
# Runs Weather Logger

export APP_ID="trlr"

while date '+%Y/%m/%d %H:%M:%S'
do
	${APP_PYTHON} -m trlr_logger.trlr_logger --log_file_directory "${APP_BASE_PATH}"

	export RtnVal="$?"
	echo trlr_logger returns "${RtnVal}"

	sleep "${APP_RESTART_DELAY}"
done
