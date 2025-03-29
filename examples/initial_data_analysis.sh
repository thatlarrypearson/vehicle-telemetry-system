# telemetry-obd-log-to-csv/examples/initial_data_analysis.sh

# The following might be modified to make this program easier to run.
# export CONFIG_FILE=../telemetry-obd/config/<VIN>.cfg

# The following might be modified to match the target system's file system layout.
export LOG_TO_CSV_DIR="../telemetry-obd-log-to-csv"
export PYTHON3="python3.8"

# See EXAMPLES-data-analysis.md or run ```python3.8 examples/initial_data_analysis.py --help``` for argument explanation
# As it is, the following arguments turn on all capabilities except for plots being displayed on the desktop.
export PY_ARGUMENTS="--forward_fill --backward_fill --general_info --general_stats --correlations --covariances --line_graphs --normalized_line_graphs --histograms --scatter_plots --3d_scatter_plots --kernel_density"

if [ $# -lt 1 ]
then
    echo "$0: USAGE:"
    echo "  telemetry-obd-output-file_1.json [telemetry-obd-output-file_2.json ... telemetry-obd-output-file_n]"
    echo "Environment Variables:"
    echo "  CONFIG_FILE: configuration file used by telemetry_obd.obd_logger to collect data."
    exit 1
fi

if [ "${CONFIG_FILE}_nothing" == "_nothing" ]
then
    echo "$0: CONFIG_FILE enviornment variable missing."
    echo "$0 CONFIG_FILE: configuration file used by telemetry_obd.obd_logger to collect data."
    exit 2
fi

${PYTHON3} "${LOG_TO_CSV_DIR}"/examples/load_config_file.py --housekeeping --cycle "${CONFIG_FILE}" > ida-cfg-file-$$.tmp
export Return_Value=$?

if [ ${Return_Value} -ne 0 ]
then
    echo Following Command Failed With Code: ${Return_Value}
    echo ${PYTHON3} "${LOG_TO_CSV_DIR}"/examples/load_config_file.py --housekeeping --cycle "${CONFIG_FILE}"
    exit 3
fi

${PYTHON3} -m obd_log_to_csv.obd_log_to_csv --csv initial_data_analysis.csv --commands $(cat ida-cfg-file-$$.tmp) $(ls -1 ${*})
export Return_Value=$?

if [ ${Return_Value} -ne 0 ]
then
    echo Following Command Failed With Code: ${Return_Value}
    echo ${PYTHON3} -m obd_log_to_csv.obd_log_to_csv --csv initial_data_analysis.csv --commands $(cat ida-cfg-file-$$.tmp) ${*}
    exit 4
fi

if [ ! -d analysis ]
then
    mkdir --parents analysis
fi

${PYTHON3} "${LOG_TO_CSV_DIR}"/examples/initial_data_analysis.py ${PY_ARGUMENTS} initial_data_analysis.csv
export Return_Value=$?

if [ ${Return_Value} -ne 0 ]
then
    echo Following Command Failed With Code: ${Return_Value}
    echo ${PYTHON3} "${LOG_TO_CSV_DIR}"/examples/initial_data_analysis.py initial_data_analysis.csv
    exit 5
fi

rm ida-cfg-file-$$.tmp
