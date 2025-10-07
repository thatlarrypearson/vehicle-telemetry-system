#!/usr/bin/bash
# vehicle-telemetry-system/bin/location.sh

export APP_ID="gps"

# environment variables starting with "VTS_" come from /root/bin/vts.root.profile
# environment variables starting with "APP_" come from bin/vts.user.profile
source ${VTS_SOURCE_DIR}/bin/vts.user.profile

export GPS_LOGGER="adafruit_ultimate_gps_logger"

# Uncommment the following when using the ORIGINAL GPS HARDWARE (u-blox)
#
# export GPS_LOGGER="gps_logger"
# ${APP_PYTHON} -m gps_logger.usb_devices
# export RtnCode=$?

# if [ "${RtnCode}" -gt 0 ]
# then
# 	# The known GPS USB device is not present.
# 	# Use the output from "${APP_TMP_DIR}/${APP_LOG_FILE}" set in vts.user.profile
# 	# to figure out what USB devices are present.
# 	# The solution may require changes to vehicle-telemetry-system/src/gps_logger/usb_devices.py.
# 	exit 1
# fi

while date '+%Y/%m/%d %H:%M:%S'
do
	# Uncommment the following when using the ORIGINAL GPS HARDWARE (u-blox)
	${APP_PYTHON} -m gps_logger.${GPS_LOGGER} \
		--serial "${VTS_DEFAULT_GPS_SERIAL_DEVICE}" \
        "${APP_BASE_PATH}"

	export RtnVal="$?"
	echo gps_logger returns "${RtnVal}"

	sleep "${RESTART_DELAY}"
done
