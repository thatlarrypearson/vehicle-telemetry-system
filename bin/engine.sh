#!/usr/bin/bash
# vehicle-telemetry-system/engine.sh
#
# Runs OBD Logger

export APP_ID="obd"

# environment variables starting with "VTS_" come from /root/bin/vts.root.profile
# environment variables starting with "APP_" come from bin/vts.user.profile
source ${VTS_SOURCE_DIR}/bin/vts.user.profile

# Need time for the system to startup the Bluetooth connection
export STARTUP_DELAY=10

# Need extra time for system/vehicle OBD interface recover after failure
export APP_RESTART_DELAY=60

export APP_CONFIG_DIR="${APP_HOME}/config"
export APP_FULL_CYCLES=10000
export APP_TEST_CYCLES=100
export TIMEOUT=4.0

# Run Command Tester one time if following file exists
export COMMAND_TESTER="${APP_HOME}/RunCommandTester"
export COMMAND_TESTER_DELAY=60

if [ ! -d "${APP_CONFIG_DIR}" ]
then
	mkdir --parents "${APP_CONFIG_DIR}"
fi

cd "${APP_HOME}"

sleep ${STARTUP_DELAY}

if [ -f "${COMMAND_TESTER}" ]
then
	# get next application startup counter
	export TEST_APP_COUNT=$(${APP_PYTHON} -m tcounter.app_counter 'engine-test')
	echo ${TEST_APP_COUNT}

	${APP_PYTHON} -m telemetry_obd.obd_command_tester \
		--timeout "${TIMEOUT}" \
		--no_fast \
		--cycle "${APP_TEST_CYCLES}" \
		"${APP_BASE_PATH}"

	export RtnVal="$?"
	echo obd_command_tester returns "${RtnVal}"

	rm -f "${COMMAND_TESTER}"
	sleep "${COMMAND_TESTER_DELAY}"
fi

while date '+%Y/%m/%d %H:%M:%S'
do
	${APP_PYTHON} -m telemetry_obd.obd_logger \
		--timeout "${TIMEOUT}" \
		--no_fast \
		--config_dir "${APP_CONFIG_DIR}" \
		--full_cycles "${APP_FULL_CYCLES}" \
		"${APP_BASE_PATH}"

	export RtnVal="$?"
	echo obd_logger returns "${RtnVal}"

	sleep "${APP_RESTART_DELAY}"
done

