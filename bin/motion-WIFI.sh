#!/usr/bin/bash
# vehicle-telemetry-system/bin/motion-WIFI.sh
#
# Runs IMU Logger

export APP_ID="imu"

while date '+%Y/%m/%d %H:%M:%S'
do
	# WIFI sensor connectivity
	${APP_PYTHON} -m imu_logger.imu_logger "${APP_BASE_PATH}"

	export RtnVal="$?"
	echo imu_logger returns "${RtnVal}"

    sleep "${APP_RESTART_DELAY}"

done

