# compare_distance.sh
# compares distance calcualted by rate X time = distance to DISTANCE_SINCE_DTC_CLEAR

# Change following line to get the desired data directory and data files
export DATA_DIR="/c/Users/runar/Dropbox/src/telemetry-obd/data/MAJ6S3KL0KC284184"
export DATA_FILES='MAJ6S3KL0KC284184-2022031[456]*-utc.json'

# Change following line to get the desired path to distance.py
export DISTANCE_PY="../telemetry-obd-log-to-csv/examples/distance.py"

echo input_file_name,first_distance,last_distance,DISTANCE_SINCE_DTC_CLEAR_difference,distance_calculated_from_SPEED_X_duration,difference,difference_percent
for fname in $(find ${DATA_DIR} -name "${DATA_FILES}" | grep -v TEST)
do
    export base_fname=$(basename "${fname}" .json)
    python3.8 -m obd_log_to_csv.obd_log_to_csv --csv tmp.csv --commands 'DISTANCE_SINCE_DTC_CLEAR,SPEED' "${fname}"
    export RETURN_VALUE=$?

    if [ "${RETURN_VALUE}" -ne 0 ]
    then
        echo ERROR IN obd_log_to_csv.obd_log_to_csv
        exit 1
    fi

    python3.8 "${DISTANCE_PY}" --csv "${base_fname}.csv" tmp.csv
    export RETURN_VALUE=$?

    if [ "${RETURN_VALUE}" -ne 0 ]
    then
        echo ERROR IN "${DISTANCE_PY}"
        exit 1
    fi

    # get the first and last DISTANCE_SINCE_DTC_CLEAR values
    egrep -v '^,' "${base_fname}.csv" | grep -v DISTANCE_SINCE_DTC_CLEAR > tmp.csv
    if [ $(cat tmp.csv | wc -l) -lt 2 ]
    then
        continue
    fi
    awk -F ',' '// {print $1 * 0.62137119}' < tmp.csv > distance_list.txt
    export first_distance=$(head --lines=1 distance_list.txt)
    export last_distance=$(tail --lines=1 distance_list.txt)
    export difference_distance=$(echo ${last_distance},${first_distance} | awk -F ',' '// {print $1 - $2}')

    # calculated distance sums
    export calculated_distance=$(awk -F ',' '// {print $7 * 0.62137119}' tmp.csv | tail --lines=1)

    # delta between difference_distance and calculated_distance
    export delta=$(echo ${difference_distance},${calculated_distance} | awk -F ',' '// {print $1 - $2}')
    export percent=$(echo ${difference_distance},${delta} | awk -F ',' '// {print ($2/$1)*100.0}')

    rm tmp.csv distance_list.txt "${base_fname}.csv"

    echo "$(basename ${fname})",${first_distance},${last_distance},${difference_distance},${calculated_distance},${delta},${percent}'%'
done
