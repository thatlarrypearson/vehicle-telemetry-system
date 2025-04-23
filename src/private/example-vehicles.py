# telemetry-analysis/private/vehicles.py

from math import pi
from datetime import datetime
import pytz

# Vehicle Data
vehicles = {
    '<VIN>': {
        'name': 'What you call this vehicle - should be unique to your set of vehicles',
        # Transmission should be auto or manual
        'transmission': 'auto',
        # Number of forward gears
        # Don't count low range on 4X4 vehicles that have a low range transfer case unless you regularly use low range
        # The more gears you have, the more data you need to collect before the algorithm can identify all of the gears.
        # This advice goes for 'gears' and for 'forward_gear_ratios'.
        # No allowance is made for having more than one 'reverse_gear_ratio'.
        'gears': 5,
        'forward_gear_ratios': {
            1: 3.59,
            2: 2.19,
            3: 1.41,
            4: 1.00,
            5: 0.83,
        },
        'reverse_gear_ratio': 3.165,
        # 'final_gear_ratio' refers to the drive axle differential gear ratio.
        'final_gear_ratio': 4.10,
        # Not using '4L_transfer_case_gear_ratio' yet.
        '4L_transfer_case_gear_ratio': 4.00,
        # Tire data is used to compare milage to RPM based distance traveled.
        'tires': {
            'label': 'LT265/70R17 121/118S Load Range E',
            'wheel_diameter': 17.0 * 0.0254,                          # meters
            'side_wall_length': 0.70 * 265.0 / 1000,                  # meters
            'diameter': (17.0 * 0.0254) + (2 * 0.70 * 265.0 / 1000),  # meters
            'circumference': pi * ((17.0 * 0.0254) + (2 * 0.70 * 265.0 / 1000)),     # meters
        },
        # Known good OBD commands that the OBD interface responds to.
        'command_list': [
            'ABSOLUTE_LOAD', 'ACCELERATOR_POS_D', 'ACCELERATOR_POS_E', 'AMBIANT_AIR_TEMP', 'BAROMETRIC_PRESSURE',
            'CATALYST_TEMP_B1S1', 'CATALYST_TEMP_B2S1', 'COMMANDED_EQUIV_RATIO', 
            'CONTROL_MODULE_VOLTAGE', 'COOLANT_TEMP', 
            'DISTANCE_SINCE_DTC_CLEAR', 'DISTANCE_W_MIL',
            'ELM_VOLTAGE', 'ENGINE_LOAD', 'EVAPORATIVE_PURGE', 
            'EVAP_VAPOR_PRESSURE', 'FUEL_LEVEL',
            'INTAKE_PRESSURE', 'INTAKE_TEMP', 
            'LONG_FUEL_TRIM_1', 'LONG_FUEL_TRIM_2', 
            'O2_B1S1', 'O2_B1S2', 'O2_B2S1', 'O2_B2S2', 
            'ODOMETER',
            'RELATIVE_THROTTLE_POS', 'RPM', 'RUN_TIME', 
            'SHORT_FUEL_TRIM_1', 'SHORT_FUEL_TRIM_2', 
            'SPEED', 'THROTTLE_ACTUATOR', 'THROTTLE_POS', 
            'THROTTLE_POS_B', 'TIMING_ADVANCE', 
        ],
        # 'fuel_type' is 'Gasoline' or 'Diesel'
        'fuel_type': 'Gasoline',
    },
    'C4HJ----------': {
        'name': '2013 Jeep Wrangler Rubicon 2 Door',
        'transmission': 'auto',
        # There appears to be some uncertainty around number of gears and gear ratios.
        # https://www.quadratec.com/c/reference/2013-jeep-wrangler-jk-specs
        # http://www.wanderingtrail.com/Trails/2012Trail/First_Impression/transmission.html
        # https://www.jeeperz-creeperz.com/article/rubicon-rock-trac-4wd-system-worth-your-money
        # 
        # The Quadratec and WanderingTrail sources are likely correct.
        'gears': 5,
        'forward_gear_ratios': {
            1: 3.59,
            2: 2.19,
            3: 1.41,
            4: 1.00,
            5: 0.83,
        },
        'reverse_gear_ratio': 3.165,
        'final_gear_ratio': 4.10,
        '4L_transfer_case_gear_ratio': 4.00,
        'tires': {
            'label': 'LT265/70R17 121/118S Load Range E',
            'wheel_diameter': 17.0 * 0.0254,                          # meters
            'side_wall_length': 0.70 * 265.0 / 1000,                  # meters
            'diameter': (17.0 * 0.0254) + (2 * 0.70 * 265.0 / 1000),  # meters
            'circumference': pi * ((17.0 * 0.0254) + (2 * 0.70 * 265.0 / 1000)),     # meters
        },
        'command_list': [
            'ABSOLUTE_LOAD', 'ACCELERATOR_POS_D', 'ACCELERATOR_POS_E', 'AMBIANT_AIR_TEMP', 'BAROMETRIC_PRESSURE',
            'CATALYST_TEMP_B1S1', 'CATALYST_TEMP_B2S1', 'COMMANDED_EQUIV_RATIO', 
            'CONTROL_MODULE_VOLTAGE', 'COOLANT_TEMP', 
            'DISTANCE_SINCE_DTC_CLEAR', 'DISTANCE_W_MIL',
            'ELM_VOLTAGE', 'ENGINE_LOAD', 'EVAPORATIVE_PURGE', 
            'EVAP_VAPOR_PRESSURE', 'FUEL_LEVEL',
            'INTAKE_PRESSURE', 'INTAKE_TEMP', 
            'LONG_FUEL_TRIM_1', 'LONG_FUEL_TRIM_2', 
            'O2_B1S1', 'O2_B1S2', 'O2_B2S1', 'O2_B2S2', 
            'ODOMETER',
            'RELATIVE_THROTTLE_POS', 'RPM', 'RUN_TIME', 
            'SHORT_FUEL_TRIM_1', 'SHORT_FUEL_TRIM_2', 
            'SPEED', 'THROTTLE_ACTUATOR', 'THROTTLE_POS', 
            'THROTTLE_POS_B', 'TIMING_ADVANCE', 
        ],
        'fuel_type': 'Gasoline',
    },
    'MAJ6-------------': {
        'name': '2019 Ford EcoSport Platinum',
        # Data from Ford Owners Manual
        'transmission': 'auto',
        'gears': 6,
        'forward_gear_ratios': {
            1: 4.584,
            2: 2.964,
            3: 1.912,
            4: 1.446,
            5: 1.000,
            6: 0.746,
        },
        'reverse_gear_ratio': 2.943,
        'final_gear_ratio': 3.51,
        'tires': {
            'label': '205/50R17 93V',
            'wheel_diameter': 17.0 * 0.0254,
            'side_wall_length': 0.50 * 265.0 / 1000,
            'diameter': (17.0 * 0.0254) + (2 * 0.50 * 265.0 / 1000),
            'circumference': pi * ((17.0 * 0.0254) + (2 * 0.50 * 265.0 / 1000)),
        },
        'command_list': [
            'ABSOLUTE_LOAD', 'ACCELERATOR_POS_D', 'ACCELERATOR_POS_E', 'AMBIANT_AIR_TEMP', 
            'BAROMETRIC_PRESSURE', 'CATALYST_TEMP_B1S1', 
            'COMMANDED_EQUIV_RATIO', 'CONTROL_MODULE_VOLTAGE', 'COOLANT_TEMP', 'ELM_VOLTAGE', 'ENGINE_LOAD', 
            'EVAPORATIVE_PURGE', 
            'EVAP_VAPOR_PRESSURE_ALT', 'FUEL_LEVEL', 'FUEL_RAIL_PRESSURE_DIRECT', 
            'INTAKE_TEMP', 'LONG_FUEL_TRIM_1', 'LONG_O2_TRIM_B1',
            'MAF', 'NMEA_GNGNS', 'NMEA_GNGNS-HDOP', 'NMEA_GNGNS-alt', 'NMEA_GNGNS-lat', 
            'NMEA_GNGNS-lon', 'NMEA_GNGNS-numSV', 'NMEA_GNGNS-sep', 'NMEA_GNGST', 
            'NMEA_GNGST-rangeRms', 'NMEA_GNVTG', 'NMEA_GNVTG-cogt', 'NMEA_GNZDA', 
            'NMEA_GNZDA-day', 'NMEA_GNZDA-ltzh', 'NMEA_GNZDA-ltzn', 'NMEA_GNZDA-month', 'NMEA_GNZDA-year', 
            'O2_B1S2', 'O2_S1_WR_CURRENT', 
            'OIL_TEMP', 
            'RELATIVE_THROTTLE_POS', 'RPM', 
            'RUN_TIME', 'SHORT_FUEL_TRIM_1', 'SPEED', 
            'THROTTLE_ACTUATOR', 'THROTTLE_POS', 'THROTTLE_POS_B', 'TIMING_ADVANCE', 
            'WARMUPS_SINCE_DTC_CLEAR'
        ],
        'fuel_type': 'Gasoline',
    },
    # The following vehicle VIN number as reported through the OBD software starts with '1FT8W4' not 'FT8W4'.
    # This doesn't really matter so long as you know that on some vehicles, if the first character in the VIN
    # is a digit, it might not show up.
    'FT8W4-----------': {
        'name': '2017 Ford F-450 Platinum',
        # https://www.cars.com/research/ford-f_450-2017/specs/
        'transmission': 'auto',
        'gears': 6,
        'forward_gear_ratios': {
            1: 3.97,
            2: 2.32,
            3: 1.52,
            4: 1.15,
            5: 0.86,
            6: 0.67,
        },
        'reverse_gear_ratio': 3.13,
        'final_gear_ratio': 4.3,
        'tires': {
            'label': '225/70R19.5G 128/126N Load Range G',
            'wheel_diameter': 19.5 * 0.0254,                                # meters
            'side_wall_length': (225.0 / 1000.0) * 0.70,                    # meters
            'diameter': (19.5 * 0.0254) + (2 * (225.0 / 1000.0) * 0.70),    # meters
            'circumference': pi * ((19.5 * 0.0254) + (2 * (225.0 / 1000.0) * 0.70)),   # meters
        },
        'command_list': [
            'ACCELERATOR_POS_D', 'ACCELERATOR_POS_E', 
            'AMBIANT_AIR_TEMP', 'BAROMETRIC_PRESSURE', 
            'CACT', 'CACT-cact_bank_1_sensor_1', 
            'CACT-cact_bank_1_sensor_1_supported', 'CACT-cact_bank_1_sensor_2', 'CACT-cact_bank_1_sensor_2_supported', 
            'CACT-cact_bank_2_sensor_1', 'CACT-cact_bank_2_sensor_1_supported', 'CACT-cact_bank_2_sensor_2', 
            'CACT-cact_bank_2_sensor_2_supported', 'CATALYST_TEMP_B1S1', 
            'CATALYST_TEMP_B1S2', 'COMMANDED_DIESEL_AIR_INTAKE', 
            'COMMANDED_DIESEL_AIR_INTAKE-commanded_intake_air_flow_a_control', 
            'COMMANDED_DIESEL_AIR_INTAKE-commanded_intake_air_flow_a_control_supported', 
            'COMMANDED_DIESEL_AIR_INTAKE-commanded_intake_air_flow_b_control', 
            'COMMANDED_DIESEL_AIR_INTAKE-commanded_intake_air_flow_b_control_supported', 
            'COMMANDED_DIESEL_AIR_INTAKE-relative_intake_air_flow_a_position', 
            'COMMANDED_DIESEL_AIR_INTAKE-relative_intake_air_flow_a_position_supported', 
            'COMMANDED_DIESEL_AIR_INTAKE-relative_intake_air_flow_b_position', 
            'COMMANDED_DIESEL_AIR_INTAKE-relative_intake_air_flow_b_position_supported', 'COMMANDED_EGR', 'COMMANDED_EGR_2', 
            'COMMANDED_EGR_2-actual_egr_a_duty_cycle', 'COMMANDED_EGR_2-actual_egr_a_duty_cycle_supported', 
            'COMMANDED_EGR_2-actual_egr_b_duty_cycle', 'COMMANDED_EGR_2-actual_egr_b_duty_cycle_supported', 
            'COMMANDED_EGR_2-commanded_egr_a_duty_cycle', 'COMMANDED_EGR_2-commanded_egr_a_duty_cycle_supported', 
            'COMMANDED_EGR_2-commanded_egr_b_duty_cycle', 'COMMANDED_EGR_2-commanded_egr_b_duty_cycle_supported', 
            'COMMANDED_EGR_2-egr_a_error', 'COMMANDED_EGR_2-egr_a_error_supported', 'COMMANDED_EGR_2-egr_b_error', 
            'COMMANDED_EGR_2-egr_b_error_supported', 'CONTROL_MODULE_VOLTAGE', 'COOLANT_TEMP',
            'CYLENDER_FUEL_RATE', 'DEF_SENSOR', 'DEF_SENSOR-def_concentration', 
            'DEF_SENSOR-def_concentration_supported', 'DEF_SENSOR-def_level', 'DEF_SENSOR-def_level_supported', 
            'DEF_SENSOR-def_temp', 'DEF_SENSOR-def_temp_supported', 'DEF_SENSOR-def_type', 'DEF_SENSOR-def_type_supported', 
            'DISTANCE_SINCE_DTC_CLEAR', 'DISTANCE_W_MIL', 'DPF_BANK_1', 'DPF_BANK_1-delta_pressure', 
            'DPF_BANK_1-delta_pressure_supported', 'DPF_BANK_1-inlet_pressure', 'DPF_BANK_1-inlet_pressure_supported', 
            'DPF_BANK_1-outlet_pressure', 'DPF_BANK_1-outlet_pressure_supported', 
            'EGR_ERROR', 'EGR_TEMP', 
            'EGR_TEMP-egr_temp_bank_1_sensor_1', 'EGR_TEMP-egr_temp_bank_1_sensor_1_supported', 
            'EGR_TEMP-egr_temp_bank_1_sensor_1_wide_range', 'EGR_TEMP-egr_temp_bank_1_sensor_1_wide_range_supported', 
            'EGR_TEMP-egr_temp_bank_1_sensor_2', 'EGR_TEMP-egr_temp_bank_1_sensor_2_supported', 
            'EGR_TEMP-egr_temp_bank_1_sensor_2_wide_range', 'EGR_TEMP-egr_temp_bank_1_sensor_2_wide_range_supported', 
            'EGR_TEMP-egr_temp_bank_2_sensor_1', 'EGR_TEMP-egr_temp_bank_2_sensor_1_supported', 
            'EGR_TEMP-egr_temp_bank_2_sensor_1_wide_range', 'EGR_TEMP-egr_temp_bank_2_sensor_1_wide_range_supported', 
            'EGR_TEMP-egr_temp_bank_2_sensor_2', 'EGR_TEMP-egr_temp_bank_2_sensor_2_supported', 
            'EGR_TEMP-egr_temp_bank_2_sensor_2_wide_range', 'EGR_TEMP-egr_temp_bank_2_sensor_2_wide_range_supported', 
            'EGT_BANK_1_TEMP', 'EGT_BANK_1_TEMP-00', 'EGT_BANK_1_TEMP-01', 'EGT_BANK_1_TEMP-02', 'EGT_BANK_1_TEMP-03', 
            'EGT_BANK_1_TEMP-04', 'EGT_BANK_1_TEMP-05', 'EGT_BANK_1_TEMP-06', 'EGT_BANK_1_TEMP-07', 
            'ELM_VOLTAGE', 'ENGINE_COOLANT_TEMPERATURE', 'ENGINE_COOLANT_TEMPERATURE-sensor_a', 
            'ENGINE_COOLANT_TEMPERATURE-sensor_b', 'ENGINE_EXHAUST_FLOW_RATE', 'ENGINE_EXHAUST_FLOW_RATE-00', 
            'ENGINE_EXHAUST_FLOW_RATE-01', 'ENGINE_FRICTION_PERCENT_TORQUE', 'ENGINE_LOAD', 'ENGINE_RUN_TIME', 
            'ENGINE_RUN_TIME-total_engine_run_time', 'ENGINE_RUN_TIME-total_idle_run_time', 
            'ENGINE_RUN_TIME-total_pto_run_time', 
            'EXHAUST_PRESSURE', 'EXHAUST_PRESSURE-exhaust_pressure_sensor_bank_1', 
            'EXHAUST_PRESSURE-exhaust_pressure_sensor_bank_1_supported', 'EXHAUST_PRESSURE-exhaust_pressure_sensor_bank_2', 
            'EXHAUST_PRESSURE-exhaust_pressure_sensor_bank_2_supported', 'FUEL_INJECT_TIMING', 'FUEL_LEVEL', 
            'FUEL_PRESSURE_CONTROL', 'FUEL_PRESSURE_CONTROL-commanded_fuel_rail_pressure_a', 
            'FUEL_PRESSURE_CONTROL-commanded_fuel_rail_pressure_a_supported', 
            'FUEL_PRESSURE_CONTROL-commanded_fuel_rail_pressure_b', 
            'FUEL_PRESSURE_CONTROL-commanded_fuel_rail_pressure_b_supported', 'FUEL_PRESSURE_CONTROL-fuel_rail_pressure_a', 
            'FUEL_PRESSURE_CONTROL-fuel_rail_pressure_a_supported', 'FUEL_PRESSURE_CONTROL-fuel_rail_pressure_b', 
            'FUEL_PRESSURE_CONTROL-fuel_rail_pressure_b_supported', 'FUEL_PRESSURE_CONTROL-fuel_temperature_a', 
            'FUEL_PRESSURE_CONTROL-fuel_temperature_a_supported', 'FUEL_PRESSURE_CONTROL-fuel_temperature_b', 
            'FUEL_PRESSURE_CONTROL-fuel_temperature_b_supported', 'FUEL_RAIL_PRESSURE_ABS', 'FUEL_RAIL_PRESSURE_DIRECT', 
            'FUEL_RATE', 'FUEL_RATE_2', 'FUEL_RATE_2-engine_fuel_rate', 'FUEL_RATE_2-vehicle_fuel_rate', 
            'INTAKE_AIR_TEMPERATURE_SENSOR', 
            'INTAKE_AIR_TEMPERATURE_SENSOR-sensor_a', 'INTAKE_AIR_TEMPERATURE_SENSOR-sensor_b', 'INTAKE_MANIFOLD_PRESSURE', 
            'INTAKE_MANIFOLD_PRESSURE-pressure_a', 'INTAKE_MANIFOLD_PRESSURE-pressure_a_supported', 
            'INTAKE_MANIFOLD_PRESSURE-pressure_b', 'INTAKE_MANIFOLD_PRESSURE-pressure_b_supported', 'INTAKE_PRESSURE', 
            'INTAKE_TEMP', 'MAF',
            'NMEA_GNGNS', 'NMEA_GNGNS-HDOP', 
            'NMEA_GNGNS-alt', 'NMEA_GNGNS-lat', 'NMEA_GNGNS-lon', 'NMEA_GNGNS-numSV',
            'NMEA_GNGNS-sep', 'NMEA_GNGST', 'NMEA_GNGST-rangeRms', 'NMEA_GNVTG', 
            'NMEA_GNVTG-cogt', 'NMEA_GNZDA', 'NMEA_GNZDA-day', 'NMEA_GNZDA-ltzh', 'NMEA_GNZDA-ltzn', 
            'NMEA_GNZDA-month', 'NMEA_GNZDA-year', 'NOX_SENSOR', 
            'NOX_SENSOR-concentration_bank_1_sensor_1_data', 'NOX_SENSOR-concentration_bank_1_sensor_1_data_availability', 
            'NOX_SENSOR-concentration_bank_1_sensor_1_supported', 'NOX_SENSOR-concentration_bank_1_sensor_2_data', 
            'NOX_SENSOR-concentration_bank_1_sensor_2_data_availability', 'NOX_SENSOR-concentration_bank_1_sensor_2_supported',
            'NOX_SENSOR-concentration_bank_2_sensor_1_data', 'NOX_SENSOR-concentration_bank_2_sensor_1_data_availability', 
            'NOX_SENSOR-concentration_bank_2_sensor_1_supported', 'NOX_SENSOR-concentration_bank_2_sensor_2_data', 
            'NOX_SENSOR-concentration_bank_2_sensor_2_data_availability', 'NOX_SENSOR-concentration_bank_2_sensor_2_supported',
            'NOX_SENSOR_2', 'NOX_SENSOR_2-concentration_bank_1_sensor_3', 
            'NOX_SENSOR_2-concentration_bank_1_sensor_3_data_availability', 
            'NOX_SENSOR_2-concentration_bank_1_sensor_3_supported', 'NOX_SENSOR_2-concentration_bank_1_sensor_4', 
            'NOX_SENSOR_2-concentration_bank_1_sensor_4_data_availability', 
            'NOX_SENSOR_2-concentration_bank_1_sensor_4_supported', 'NOX_SENSOR_2-concentration_bank_2_sensor_3', 
            'NOX_SENSOR_2-concentration_bank_2_sensor_3_data_availability', 
            'NOX_SENSOR_2-concentration_bank_2_sensor_3_supported', 'NOX_SENSOR_2-concentration_bank_2_sensor_4', 
            'NOX_SENSOR_2-concentration_bank_2_sensor_4_data_availability', 
            'NOX_SENSOR_2-concentration_bank_2_sensor_4_supported', 'NOX_SENSOR_CORRECTED', 
            'NOX_SENSOR_CORRECTED-concentration_bank_1_sensor_1', 
            'NOX_SENSOR_CORRECTED-concentration_bank_1_sensor_1_data_availability', 
            'NOX_SENSOR_CORRECTED-concentration_bank_1_sensor_1_supported', 
            'NOX_SENSOR_CORRECTED-concentration_bank_1_sensor_2', 
            'NOX_SENSOR_CORRECTED-concentration_bank_1_sensor_2_data_availability', 
            'NOX_SENSOR_CORRECTED-concentration_bank_1_sensor_2_supported', 
            'NOX_SENSOR_CORRECTED-concentration_bank_2_sensor_1', 
            'NOX_SENSOR_CORRECTED-concentration_bank_2_sensor_1_data_availability', 
            'NOX_SENSOR_CORRECTED-concentration_bank_2_sensor_1_supported', 
            'NOX_SENSOR_CORRECTED-concentration_bank_2_sensor_2', 
            'NOX_SENSOR_CORRECTED-concentration_bank_2_sensor_2_data_availability', 
            'NOX_SENSOR_CORRECTED-concentration_bank_2_sensor_2_supported', 'NOX_SENSOR_CORRECTED_2', 
            'NOX_SENSOR_CORRECTED_2-concentration_bank_1_sensor_3', 
            'NOX_SENSOR_CORRECTED_2-concentration_bank_1_sensor_3_data_availability', 
            'NOX_SENSOR_CORRECTED_2-concentration_bank_1_sensor_3_supported', 
            'NOX_SENSOR_CORRECTED_2-concentration_bank_1_sensor_4', 
            'NOX_SENSOR_CORRECTED_2-concentration_bank_1_sensor_4_data_availability', 
            'NOX_SENSOR_CORRECTED_2-concentration_bank_1_sensor_4_supported', 
            'NOX_SENSOR_CORRECTED_2-concentration_bank_2_sensor_3', 
            'NOX_SENSOR_CORRECTED_2-concentration_bank_2_sensor_3_data_availability', 
            'NOX_SENSOR_CORRECTED_2-concentration_bank_2_sensor_3_supported', 
            'NOX_SENSOR_CORRECTED_2-concentration_bank_2_sensor_4', 
            'NOX_SENSOR_CORRECTED_2-concentration_bank_2_sensor_4_data_availability', 
            'NOX_SENSOR_CORRECTED_2-concentration_bank_2_sensor_4_supported', 'NOX_SYSTEM', 
            'NOX_SYSTEM-average_demanded_reagent_consumption', 'NOX_SYSTEM-average_demanded_reagent_consumption_support', 
            'NOX_SYSTEM-average_reagent_consumption', 'NOX_SYSTEM-average_reagent_consumption_support', 
            'NOX_SYSTEM-minutes_engine_run_while_nox_warning_mode_is_activated', 
            'NOX_SYSTEM-minutes_engine_run_while_nox_warning_mode_is_activated_support', 'NOX_SYSTEM-reagent_tank_level', 
            'NOX_SYSTEM-reagent_tank_level_supported', 'O2_SENSOR_WIDE', 
            'O2_SENSOR_WIDE-o2_sensor_concentration_bank_1_sensor_1', 
            'O2_SENSOR_WIDE-o2_sensor_concentration_bank_1_sensor_1_supported', 
            'O2_SENSOR_WIDE-o2_sensor_concentration_bank_1_sensor_2', 
            'O2_SENSOR_WIDE-o2_sensor_concentration_bank_1_sensor_2_supported', 
            'O2_SENSOR_WIDE-o2_sensor_concentration_bank_2_sensor_1', 
            'O2_SENSOR_WIDE-o2_sensor_concentration_bank_2_sensor_1_supported', 
            'O2_SENSOR_WIDE-o2_sensor_concentration_bank_2_sensor_2', 
            'O2_SENSOR_WIDE-o2_sensor_concentration_bank_2_sensor_2_supported', 
            'O2_SENSOR_WIDE-o2_sensor_lambda_bank_1_sensor_1', 'O2_SENSOR_WIDE-o2_sensor_lambda_bank_1_sensor_1_supported', 
            'O2_SENSOR_WIDE-o2_sensor_lambda_bank_1_sensor_2', 'O2_SENSOR_WIDE-o2_sensor_lambda_bank_1_sensor_2_supported', 
            'O2_SENSOR_WIDE-o2_sensor_lambda_bank_2_sensor_1', 'O2_SENSOR_WIDE-o2_sensor_lambda_bank_2_sensor_1_supported', 
            'O2_SENSOR_WIDE-o2_sensor_lambda_bank_2_sensor_2', 'O2_SENSOR_WIDE-o2_sensor_lambda_bank_2_sensor_2_supported', 
            'ODOMETER', 'OIL_TEMP', 'PERCENT_TORQUE', 'PERCENT_TORQUE-Engine_Point_1', 'PERCENT_TORQUE-Engine_Point_2', 
            'PERCENT_TORQUE-Engine_Point_3', 'PERCENT_TORQUE-Engine_Point_4', 'PERCENT_TORQUE-Idle', 
            'PM_SENSOR_OUTPUT', 
            'PM_SENSOR_OUTPUT-active_status_bank_1_sensor_1', 'PM_SENSOR_OUTPUT-active_status_bank_2_sensor_1', 
            'PM_SENSOR_OUTPUT-normalized_output_value_bank_1_sensor_1', 
            'PM_SENSOR_OUTPUT-normalized_output_value_bank_2_sensor_1', 
            'PM_SENSOR_OUTPUT-operating_status_bank_1_sensor_1_supported', 
            'PM_SENSOR_OUTPUT-operating_status_bank_2_sensor_1_supported', 'PM_SENSOR_OUTPUT-regen_status_bank_1_sensor_1', 
            'PM_SENSOR_OUTPUT-regen_status_bank_2_sensor_1', 'PM_SENSOR_OUTPUT-signal_bank_1_sensor_1_supported', 
            'PM_SENSOR_OUTPUT-signal_bank_1_sensor_2_supported', 'REFERENCE_TORQUE', 'RELATIVE_ACCEL_POS', 'RPM', 'RUN_TIME', 
            'SPEED', 
            'TORQUE', 'TORQUE_DEMAND',
            'WARMUPS_SINCE_DTC_CLEAR', 
        ],
        'fuel_type': 'Diesel',
    },
    '3FTT-------------': {
        'name': '2023 Ford Maverick Lariat',
        # https://www.cars.com/research/ford-f_450-2017/specs/
        'transmission': 'auto',
        'gears': 8,
        'forward_gear_ratios': {
            1: 4.69,
            2: 3.31,
            3: 3.01,
            4: 1.92,
            5: 1.45,
            6: 1.00,
            7: 0.75,
            8: 0.62,
        },
        'reverse_gear_ratio': 2.96,
        'final_gear_ratio': 3.81,
        # A tire with the size 235/65R17 has a diameter of 29.0 inches.
        # The first number, 235, is the cross-section width of the tire in millimeters.
        # The second number, 65, is the ratio of the sidewall height to the cross-section width.
        # The letter R stands for radial, which is the type of construction of the tire.
        # The last number, 17, is the wheel diameter in inches.
        # To calculate the diameter of the tire, you can use the following formula:
        # Diameter = 25.4 * (cross-section width + sidewall height)
        # Plugging in the values for the tire size 235/65R17, we get the following:
        # Diameter = 25.4 * (235 mm + 65 mm) = 25.4 * 290 mm = 29.0 inches
        # Diameter = 29 inches * 0.0254 m/inch = 0.737 m
        'tires': {
            'label': '235/65R17 104H',
            'diameter': 0.737,                                              # meters
            'circumference': pi * 0.737,                                    # meters
        },
        'command_list': [
            'ABSOLUTE_LOAD', 'ACCELERATOR_POS_D',
            'ACCELERATOR_POS_E', 'AMBIANT_AIR_TEMP',
            'BAROMETRIC_PRESSURE', 'CALIBRATION_ID',
            'CATALYST_TEMP_B1S1', 'COMMANDED_EGR_2',
            'COMMANDED_EGR_2-actual_egr_a_duty_cycle',
            'COMMANDED_EGR_2-actual_egr_a_duty_cycle_supported',
            'COMMANDED_EGR_2-actual_egr_b_duty_cycle',
            'COMMANDED_EGR_2-actual_egr_b_duty_cycle_supported',
            'COMMANDED_EGR_2-commanded_egr_a_duty_cycle',
            'COMMANDED_EGR_2-commanded_egr_a_duty_cycle_supported',
            'COMMANDED_EGR_2-commanded_egr_b_duty_cycle',
            'COMMANDED_EGR_2-commanded_egr_b_duty_cycle_supported',
            'COMMANDED_EGR_2-egr_a_error', 'COMMANDED_EGR_2-egr_a_error_supported',
            'COMMANDED_EGR_2-egr_b_error',
            'COMMANDED_EGR_2-egr_b_error_supported', 'COMMANDED_EQUIV_RATIO',
            'CONTROL_MODULE_VOLTAGE', 'COOLANT_TEMP', 'CVN',
            'DISTANCE_SINCE_DTC_CLEAR', 'DISTANCE_W_MIL',
            'ECU_NAME', 'EGR_TEMP', 'EGR_TEMP-egr_temp_bank_1_sensor_1',
            'EGR_TEMP-egr_temp_bank_1_sensor_1_supported',
            'EGR_TEMP-egr_temp_bank_1_sensor_1_wide_range',
            'EGR_TEMP-egr_temp_bank_1_sensor_1_wide_range_supported',
            'EGR_TEMP-egr_temp_bank_1_sensor_2',
            'EGR_TEMP-egr_temp_bank_1_sensor_2_supported',
            'EGR_TEMP-egr_temp_bank_1_sensor_2_wide_range',
            'EGR_TEMP-egr_temp_bank_1_sensor_2_wide_range_supported',
            'EGR_TEMP-egr_temp_bank_2_sensor_1',
            'EGR_TEMP-egr_temp_bank_2_sensor_1_supported',
            'EGR_TEMP-egr_temp_bank_2_sensor_1_wide_range',
            'EGR_TEMP-egr_temp_bank_2_sensor_1_wide_range_supported',
            'EGR_TEMP-egr_temp_bank_2_sensor_2',
            'EGR_TEMP-egr_temp_bank_2_sensor_2_supported',
            'EGR_TEMP-egr_temp_bank_2_sensor_2_wide_range',
            'EGR_TEMP-egr_temp_bank_2_sensor_2_wide_range_supported',
            'ENGINE_EXHAUST_FLOW_RATE',
            'ENGINE_FRICTION_PERCENT_TORQUE', 'ENGINE_LOAD',
            'EVAPORATIVE_PURGE', 'EVAP_SYS_VAPOR_PRESSURE',
            'EVAP_SYS_VAPOR_PRESSURE-esvp_a',
            'EVAP_SYS_VAPOR_PRESSURE-esvp_a_supported',
            'EVAP_SYS_VAPOR_PRESSURE-esvp_a_wide_range',
            'EVAP_SYS_VAPOR_PRESSURE-esvp_a_wide_range_supported',
            'EVAP_SYS_VAPOR_PRESSURE-esvp_b',
            'EVAP_SYS_VAPOR_PRESSURE-esvp_b_supported',
            'EVAP_SYS_VAPOR_PRESSURE-esvp_b_wide_range',
            'EVAP_SYS_VAPOR_PRESSURE-esvp_b_wide_range_supported',
            'EVAP_VAPOR_PRESSURE_ALT', 'FUEL_LEVEL',
            'FUEL_RAIL_PRESSURE_DIRECT', 'FUEL_RATE_2',
            'FUEL_RATE_2-engine_fuel_rate', 'FUEL_RATE_2-vehicle_fuel_rate',
            'FUEL_STATUS', 'FUEL_STATUS-00', 'FUEL_STATUS-01',
            'FUEL_TYPE', 'INTAKE_AIR_TEMPERATURE_SENSOR',
            'INTAKE_AIR_TEMPERATURE_SENSOR-sensor_a',
            'INTAKE_AIR_TEMPERATURE_SENSOR-sensor_b', 'INTAKE_PRESSURE',
            'INTAKE_TEMP', 'LONG_FUEL_TRIM_1', 'LONG_O2_TRIM_B1',
            'O2_B1S2', 'O2_S1_WR_CURRENT', 
            'ODOMETER',
            'REFERENCE_TORQUE',
            'RELATIVE_THROTTLE_POS', 'RPM', 'RUN_TIME', 'SHORT_FUEL_TRIM_1',
            'SPEED',
            'THROTTLE', 'THROTTLE-commanded_throttle_actuator_a_control',
            'THROTTLE-commanded_throttle_actuator_a_control_supported',
            'THROTTLE-commanded_throttle_actuator_b_control',
            'THROTTLE-commanded_throttle_actuator_b_control_supported',
            'THROTTLE-relative_throttle_a_position',
            'THROTTLE-relative_throttle_a_position_supported',
            'THROTTLE-relative_throttle_b_position',
            'THROTTLE-relative_throttle_b_position_supported',
            'THROTTLE_ACTUATOR', 'THROTTLE_POS', 'TIMING_ADVANCE', 'TORQUE',
            'VEHICLE_OPERATION_DATA',
            'VEHICLE_OPERATION_DATA-lifetime_distance_traveled',
            'VEHICLE_OPERATION_DATA-lifetime_fuel_consumed',
            'VEHICLE_OPERATION_DATA-recent_distance_traveled',
            'VEHICLE_OPERATION_DATA-recent_fuel_consumed', 'VIN',
            'WARMUPS_SINCE_DTC_CLEAR', 'WWH_OBD_VEHICLE_INFO',
            'WWH_OBD_VEHICLE_INFO-cumulative_continuous_malfunction_indicator_counter',
            'WWH_OBD_VEHICLE_INFO-cumulative_continuous_malfunction_indicator_counter_supported'
        ],
        'fuel_type': 'Gasoline',
    },
}

# This gets filled in programatically by fuel-study-* notebooks.
vehicle_fueling = {
    # Jeep - 'C4HJ----------'
    # EcoSport - 'MAJ6----------'
    # F-450 - 'FT8W----------'
    # Maverick - '3FTT-------------'

    # Timestamp
    # datetime(year, month, day, hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
    datetime(2024, 3, 18, hour=13, minute=23, second=20, tzinfo=pytz.timezone('US/Central')): {
        'vehicle': '3FTT-------------',
        'mpg': 25.32,
        'odometer': 3679.2,
        'gallons': 11.771,
        'price_per_gallon':	2.899,
        'vendor':	'HEB',
        'address':  "HEB #18 (00585), 1520 Austin Hwy Bldg A, San Antonio, TX 78218",
    },
}
