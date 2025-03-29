#!/usr/bin/bash
set -x
# cd
# cd telemetry-counter
rm -rf dist/ telemetry-counter-0.0.1/ telemetry_counter.egg-info/
python3.11 -m build .
python3.11 -m pip install --force-reinstall dist/telemetry_counter-0.0.1-py3-none-any.whl

for app_id in obd gps wthr imu
do
	rm -f $(python3.11 -m counter.app_counter --app_count_file_location wthr)
	python3.11 -m counter.app_counter --current_app_count wthr 
	python3.11 -m counter.app_counter wthr 
	python3.11 -m counter.app_counter --current_app_count wthr 
	python3.11 -m counter.app_counter wthr 
	python3.11 -m counter.app_counter --current_app_count wthr 
	python3.11 -m counter.app_counter wthr 
	python3.11 -m counter.app_counter --current_app_count wthr 
	python3.11 -m counter.app_counter wthr 
	rm -f $(python3.11 -m counter.app_counter --app_count_file_location wthr)
done

rm -f $(python3.11 -m counter.boot_counter --boot_count_file_location)
python3.11 -m counter.boot_counter --current_boot_count
python3.11 -m counter.boot_counter
python3.11 -m counter.boot_counter --current_boot_count
python3.11 -m counter.boot_counter
python3.11 -m counter.boot_counter --current_boot_count
python3.11 -m counter.boot_counter
python3.11 -m counter.boot_counter --current_boot_count
python3.11 -m counter.boot_counter
rm -f $(python3.11 -m counter.boot_counter --boot_count_file_location)
