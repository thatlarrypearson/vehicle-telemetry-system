# distance.sh

# Change following line to get the desired data directory
export DATA_DIR=../telemetry-obd/data

# Change following line to get the desired path to distance.py
export DISTANCE_PY="../telemetry-obd-log-to-csv/examples/distance.py"


for fname in $(find ${DATA_DIR} -name '*.json' | grep -v TEST)
do
    # echo input file is "${fname}"
    export base_fname=$(basename "${fname}" .json)
    python3.8 -m obd_log_to_csv.obd_log_to_csv --csv tmp.csv --commands 'DISTANCE_SINCE_DTC_CLEAR,SPEED' "${fname}"
    export RETURN_VALUE=$?

    if [ "${RETURN_VALUE}" -ne 0 ]
    then
        exit 1
    fi

    echo output file is ${base_fname}.csv
    python3.8 "${DISTANCE_PY}" --csv "${base_fname}.csv" tmp.csv
    export RETURN_VALUE=$?

    if [ "${RETURN_VALUE}" -ne 0 ]
    then
        exit 1
    fi
    rm tmp.csv 
done
