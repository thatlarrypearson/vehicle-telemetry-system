#!/usr/bin/bash
# Install_telemetry-imu.sh
#

export APP_HOME="/home/$(whoami)/telemetry-imu"
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

${APP_PYTHON} -m pip uninstall -y telemetry-imu

${APP_PYTHON} -m build .
ls -l dist/*.whl
${APP_PYTHON} -m pip install dist/*.whl

${APP_PYTHON} -m imu_logger.imu_logger --help
${APP_PYTHON} -m imu_logger.usb_devices --help
