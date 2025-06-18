#!/usr/bin/bash
# vehicle-telemetry-system/bin/motion-USB.sh
#
# Runs IMU Logger

export APP_ID="imu"

${APP_PYTHON} -m imu_logger.usb_devices
export RtnCode=$?

if [ "${RtnCode}" -gt 0 ]
then
	exit 1
fi

while date '+%Y/%m/%d %H:%M:%S'
do
	# USB sensor connectivity
	${APP_PYTHON} -m imu_logger.imu_logger --usb "${APP_BASE_PATH}"

	export RtnVal="$?"
	echo imu_logger returns "${RtnVal}"

    sleep "${APP_RESTART_DELAY}"

done

