#!/usr/bin/bash
# vehicle-telemetry-system/bin/audit.sh
#
# Update boot count

export APP_ID="audit"

# environment variables starting with "VTS_" come from /root/bin/vts.root.profile
# environment variables starting with "APP_" come from bin/vts.user.profile
source ${VTS_SOURCE_DIR}/bin/vts.user.profile

echo Current BOOT_COUNT = $(${APP_PYTHON} -m tcounter.boot_counter --current_boot_count)

exit 0
