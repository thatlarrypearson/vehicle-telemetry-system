#!/usr/bin/bash
# vehicle-telemetry-system/bin/utilitiy.sh
#
# Runs file_system_info and if the correct drive (volume name or volume label) is found it will sync
# the data directory on the host to the USB drive identified by volume name.

export APP_ID="utility"

# Identifier for the correct volume/drive name/label
export VOLUME_LABEL="M2-256"

# environment variables starting with "VTS_" come from /root/bin/vts.root.profile
# environment variables starting with "APP_" come from bin/vts.user.profile
source ${VTS_SOURCE_DIR}/bin/vts.user.profile

${APP_PYTHON} -m u_tools.file_system_info --verbose

export MOUNT_POINT="$(${APP_PYTHON} -m u_tools.file_system_info --match_field volume_label --match_value ${VOLUME_LABEL} --print_field mount_point)"

if [ -z  "${MOUNT_POINT}" ]
then
	echo Did not find a match for volume_label ${VOLUME_LABEL}
	exit 0
fi

echo Match Found mount_point ${MOUNT_POINT} for volume_label ${VOLUME_LABEL}

echo syncing "${APP_HOME}" to "${MOUNT_POINT}/${HOSTNAME}/"
rsync -rv "${APP_HOME}" "${MOUNT_POINT}/${HOSTNAME}/"

echo rsync returned status code $?

exit 0
