# telemetry-analysis/telemetry_analysis/vins.py

# All {vin}s with known good data
from private.vehicles import vehicles

def vehicle_vin_list()->list:
    return [vin for vin in vehicles]

def vehicle_name_list()->list:
    return [vehicle['name'] for vin, vehicle in vehicles.items()]

def get_vin_from_vehicle_name(vehicle_name:str)->str:
    for vin, vehicle in vehicles.items():
        if vehicle_name == vehicle['name']:
            return vin
        
    return None

fake_vin = '<vin>'
