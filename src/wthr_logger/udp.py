# telemetry-wthr/wthr_logger/udp.py
"""
Telemetry Weather Logger - UDP Communications Module

Implements Client for WeatherFlow Tempest UDP Reference - v171
https://weatherflow.github.io/Tempest/api/udp/v171
"""
import socket
import logging
import json
from datetime import datetime, timezone

DEFAULT_LOCAL_HOST_INTERFACE_ADDRESS = "0.0.0.0"
DEFAULT_LOCAL_HOST_UDP_PORT_NUMBER   = 50222
BUFFER_SIZE  = 8192

WEATHER_REPORT_EXCLUDE_LIST = []

logger = logging.getLogger("wthr_logger")

class WeatherReports(object):
    """
    Listen on UDP port for WeatherFlow Tempest weather reports.

    Parse each JSON encoded weather report and return dictionary
    """
    message_count = 0
    weather_station = None
    logger = None
    types = {}
    stations = {}
    hubs = {}
    firmware_revision = {}
    # serial_number': 'ST-00052725', 'type': 'rapid_wind', 'hub_sn': 'HB-00079118', 

    def __init__(
        self,
        logger,
        local_host_interface_address=DEFAULT_LOCAL_HOST_INTERFACE_ADDRESS,
        local_host_udp_port_number=DEFAULT_LOCAL_HOST_UDP_PORT_NUMBER,
    ):
        self.local_host_interface_address = local_host_interface_address
        self.local_host_udp_port_number = local_host_udp_port_number
        self.weather_station = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.weather_station.bind((local_host_interface_address, local_host_udp_port_number))
        self.logger = logger
        self.logger.info(f"UDP client ready on {local_host_interface_address} port {local_host_udp_port_number}")

    def __iter__(self):
        """Start iterator."""
        return self

    def __next__(self):
        """
        Get the next iterable.  returns raw_weather_report and weather_report
        """
        # message is type bytes, JSON encoded
        # ip_address_info is list [Sender IP Address:str, Sender Port Number int]
        message, ip_address_info = self.weather_station.recvfrom(BUFFER_SIZE)
        self.message_count += 1

        self.logger.debug(f"{self.message_count} address: {ip_address_info}")
        self.logger.debug(f"{self.message_count} message: {message}")

        try:
            # if weird decode errors, then use 'ignore' in: message.decode('utf-8', 'ignore')
            # weather_record = json.loads(message.decode('utf-8'))
            weather_record = json.loads(message)

        except json.decoder.JSONDecodeError as e:
            # improperly closed JSON file
            self.logger.error(f"{self.message_count}: Corrupted JSON info in message {message}\n{e}")
            return None, None

        if not isinstance(weather_record, dict):
            self.logger.error(f"{self.message_count}: JSON decode didn't return a dict: {weather_record}")
            return None, None

        if 'type' in weather_record:
            if weather_record['type'] in self.types:
                self.types[weather_record['type']] += 1
            else:
                self.types[weather_record['type']] = 1
                self.logger.info(f"{self.message_count}: Weather Record Type {weather_record['type']}")

        if 'serial_number' in weather_record:
            if weather_record['serial_number'] in self.stations:
                self.stations[weather_record['serial_number']] += 1
            else:
                self.stations[weather_record['serial_number']] = 1
                if 'firmware_revision' in weather_record:
                    self.firmware_revision[weather_record['serial_number']] = weather_record['serial_number']
                self.logger.info(f"{self.message_count}: Weather Station Serial Number {weather_record['serial_number']}")

        if 'hub_sn' in weather_record:
            if weather_record['hub_sn'] in self.hubs:
                self.hubs[weather_record['hub_sn']] += 1
            else:
                self.hubs[weather_record['hub_sn']] = 1
                if 'firmware_revision' in weather_record:
                    self.firmware_revision[weather_record['serial_number']] = weather_record['serial_number']
                self.logger.info(f"{self.message_count}: Hub Serial Number {weather_record['hub_sn']}")

        return weather_record, self.parse(weather_record)

    def parse(self, raw_weather_record:dict) -> dict:
        """
        Reformat weather record so that all (embedded) fields are represented as keys.

        Example - Rain Start Event [type = evt_precip]
        INPUT: {"serial_number": "SK-00001234", "type": "evt_precip", "hub_sn": "HB-12345", "evt": [1493322445]}
        OUTPUT: {"serial_number": "SK-00001234", "type": "evt_precip", "hub_sn": "HB-12345", "time_epoch": datetime(2022,7,6,13,31,55)}
        """
        if 'type' not in raw_weather_record:
            self.logger.error(f"{self.message_count}: parse failure, 'type' not in {raw_weather_record}")
            return None

        self.logger.debug(f"{self.message_count}: parse {raw_weather_record['type']}")

        if raw_weather_record['type'] == 'evt_precip':              # rain start event
            return {
                'message_type': "rain start event",
                'serial_number': raw_weather_record['serial_number'],
                'type': raw_weather_record['type'],
                'hub_sn': raw_weather_record['hub_sn'],
                'time_epoch': raw_weather_record['evt'][0],         # Unix Time, unknown TZ
            }

        if raw_weather_record['type'] == 'evt_strike':              # lightning strike event
            return {
                'message_type': "lightning strike event",
                'serial_number': raw_weather_record['serial_number'],
                'type': raw_weather_record['type'],
                'hub_sn': raw_weather_record['hub_sn'],
                'time_epoch': raw_weather_record['evt'][0],         # Unix Time, unknown TZ
                'distance': raw_weather_record['evt'][1],           # km
                'energy': raw_weather_record['evt'][2],             # ?
            }

        if raw_weather_record['type'] == 'rapid_wind':              # rapid wind
            return {
                'message_type': "rapid wind",
                'serial_number': raw_weather_record['serial_number'],
                'type': raw_weather_record['type'],
                'hub_sn': raw_weather_record['hub_sn'],
                'time_epoch': raw_weather_record['ob'][0],          # Unix Time, unknown TZ
                'wind_speed': raw_weather_record['ob'][1],          # meters per second
                'wind_direction': raw_weather_record['ob'][2],      # degrees
            }

        if raw_weather_record['type'] == 'obs_air':                     # Observation (Air)
            return {
                'message_type': "observation (air)",
                'serial_number': raw_weather_record['serial_number'],
                'type': raw_weather_record['type'],
                'hub_sn': raw_weather_record['hub_sn'],
                'firmware_revision': raw_weather_record['firmware_revision'],
                'time_epoch': raw_weather_record['obs'][0][0],          # Unix Time, unknown TZ
                'station_pressure': raw_weather_record['obs'][0][1],    # MB (millibars)
                'air_temperature': raw_weather_record['obs'][0][2],     # Celsius
                'relative_humidity': raw_weather_record['obs'][0][3],   # percent
                'lightning_strike_count': raw_weather_record['obs'][0][4],     # count
                'lightning_strike_average_distance': raw_weather_record['obs'][0][5],     # km
                'battery': raw_weather_record['obs'][0][6],             # ?
                'report_interval': raw_weather_record['obs'][0][7],     # minutes
            }

        if raw_weather_record['type'] == 'obs_sky':                     # Observation (Sky)
            return {
                'message_type': "observation (sky)",
                'serial_number': raw_weather_record['serial_number'],
                'type': raw_weather_record['type'],
                'hub_sn': raw_weather_record['hub_sn'],
                'firmware_revision': raw_weather_record['firmware_revision'],
                'time_epoch': raw_weather_record['obs'][0][0],          # Unix Time, unknown TZ
                'illuminance': raw_weather_record['obs'][0][1],         # Lux
                'uv': raw_weather_record['obs'][0][2],                  # index
                'rain_over_previous_minute': raw_weather_record['obs'][0][3],   # mm (millimeter)
                'wind_lull': raw_weather_record['obs'][0][4],           # meters per second
                'wind_average': raw_weather_record['obs'][0][5],        # meters per second
                'wind_gust': raw_weather_record['obs'][0][6],           # meters per second
                'wind_direction': raw_weather_record['obs'][0][7],      # degrees
                'battery': raw_weather_record['obs'][0][8],             # volts
                'report_interval': raw_weather_record['obs'][0][9],     # minutes
                'solar_radiation': raw_weather_record['obs'][0][10],     # W/m^2 (watts per square meter)
                'local_day_rain_accumulation': raw_weather_record['obs'][0][11], # mm (millimeter)
                'precipitation_type': raw_weather_record['obs'][0][12],  # 0: none, 1: rain, 2: hail
                'wind_sample_interval': raw_weather_record['obs'][0][13],    # seconds
            }

        if raw_weather_record['type'] == 'obs_st':                      # Observation (Tempest)
            return {
                'message_type': "observation (tempest)",
                'serial_number': raw_weather_record['serial_number'],
                'type': raw_weather_record['type'],
                'hub_sn': raw_weather_record['hub_sn'],
                'firmware_revision': raw_weather_record['firmware_revision'],
                'time_epoch': raw_weather_record['obs'][0][0],          # Unix Time, unknown TZ
                'wind_lull': raw_weather_record['obs'][0][1],           # meters per second
                'wind_average': raw_weather_record['obs'][0][2],        # meters per second
                'wind_gust': raw_weather_record['obs'][0][3],           # meters per second
                'wind_direction': raw_weather_record['obs'][0][4],      # degrees
                'wind_sample_interval': raw_weather_record['obs'][0][5],    # seconds
                'station_pressure': raw_weather_record['obs'][0][6],    # MB (millibars)
                'air_temperature': raw_weather_record['obs'][0][7],     # Celsius
                'relative_humidity': raw_weather_record['obs'][0][8],   # percent
                'illuminance': raw_weather_record['obs'][0][9],         # lux
                'uv': raw_weather_record['obs'][0][10],                 # index
                'solar_radiation': raw_weather_record['obs'][0][11],    # W/m^2 (watts per square meter)
                'rain_amount_over_previous_minute': raw_weather_record['obs'][0][12],   # mm (millimeter)
                'precipitation_type': raw_weather_record['obs'][0][13], # 0: none, 1: rain, 2: hail, 3: rain & hail
                'lightning_strike_average_distance': raw_weather_record['obs'][0][14],  # km
                'lightning_strike_count': raw_weather_record['obs'][0][15], # count
                'battery': raw_weather_record['obs'][0][16],            # volts
                'report_interval': raw_weather_record['obs'][0][17],    # minutes
            }

        if raw_weather_record['type'] == 'device_status':               # Status (Device)
            return {
                'message_type': "status (device)",
                'serial_number': raw_weather_record['serial_number'],
                'type': raw_weather_record['type'],
                'hub_sn': raw_weather_record['hub_sn'],
                'timestamp': raw_weather_record['timestamp'],           # Unix Time, unknown TZ
                'uptime': raw_weather_record['uptime'],                 # seconds
                'voltage': raw_weather_record['voltage'],               # volts
                'firmware_revision': raw_weather_record['firmware_revision'],
                'rssi': raw_weather_record['rssi'],
                'hub_rssi': raw_weather_record['hub_rssi'],
                'sensor_status': raw_weather_record['sensor_status'],
                'debug': raw_weather_record['debug'],
            }

        if raw_weather_record['type'] == 'hub_status':               # Status (Hub)
            return {
                'message_type': "status (hub)",
                'serial_number': raw_weather_record['serial_number'],
                'type': raw_weather_record['type'],
                'firmware_revision': raw_weather_record['firmware_revision'],
                'uptime': raw_weather_record['uptime'],                 # seconds
                'rssi': raw_weather_record['rssi'],
                'timestamp': raw_weather_record['timestamp'],           # Unix Time, unknown TZ
                'reset_flags': raw_weather_record['reset_flags'],
                'seq': raw_weather_record['seq'],
                # fs - undocumented
                'radio_version': raw_weather_record['radio_stats'][0],
                'radio_reboot_count': raw_weather_record['radio_stats'][1],
                'radio_i2c_bus_error_count': raw_weather_record['radio_stats'][2],
                'radio_status': raw_weather_record['radio_stats'][3],
                'radio_network_id': raw_weather_record['radio_stats'][4],
                # mqtt_stats - undocumented
            }

        self.logger.error(f"{self.message_count}: unknown weather record type {raw_weather_record['type']}")

        return None
