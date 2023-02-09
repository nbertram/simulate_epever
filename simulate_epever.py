import logging

from argparse import ArgumentParser

from pymodbus import pymodbus_apply_logging_config
from pymodbus.datastore import (
    ModbusSparseDataBlock,
    ModbusSlaveContext,
    ModbusServerContext,
)
from pymodbus.constants import Endian
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.server import StartSerialServer
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.framer.rtu_framer import ModbusRtuFramer

from typing import Dict

argparser = ArgumentParser(description="Simulate an ePever modbus interface")
argparser.add_argument(
    "port", action="store", help="Which port to listen on, eg. /dev/ttyS0"
)
args = argparser.parse_args()


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
pymodbus_apply_logging_config(logging.DEBUG)


class FakeDevice:
    array_rated_voltage = 60
    array_rated_current = 30
    array_rated_power = array_rated_voltage * array_rated_current
    battery_rated_voltage = 12
    battery_rated_current = 10
    battery_rated_power = battery_rated_voltage * battery_rated_current
    charging_mode = 2  # MPPT
    rated_current_load = 2
    pv_array_input_voltage = 50
    pv_array_input_current = 6
    pv_array_input_power = pv_array_input_voltage * pv_array_input_current
    load_voltage = 11.8
    load_current = 0.8
    load_power = load_voltage * load_current
    battery_charging_power = pv_array_input_power - load_power
    battery_temperature = 23
    temperature_inside_equipment = 35
    battery_soc = (load_voltage / battery_rated_voltage) * 100
    battery_remote_temperature = battery_temperature
    battery_real_rated_power = 1200
    battery_status = 0b0000000000000000
    charging_equipment_status = 0b0000000000000000
    discharging_equipment_status = 0x0000000000000000
    max_pv_voltage_today = 53
    min_pv_voltage_today = 5
    max_battery_voltage_today = 14.5
    min_battery_voltage_today = 10.7
    consumed_energy_today = 2.1
    consumed_energy_month = consumed_energy_today * 30
    consumed_energy_year = consumed_energy_month * 12
    total_consumed_energy = consumed_energy_year * 1.2
    generated_energy_today = 1.9
    generated_energy_month = generated_energy_today * 30
    generated_energy_year = generated_energy_month * 12
    total_generated_energy = generated_energy_year * 1.2
    battery_voltage = load_voltage
    battery_current = (pv_array_input_power - load_power) / battery_voltage
    battery_type = 0x0003  # flooded
    battery_capacity = 7
    temperature_compensation_coefficient = 3
    high_voltage_disconnect = 15
    charging_limit_voltage = 14.5
    over_voltage_reconnect = 14.5
    equalization_voltage = 14.0
    boost_voltage = 11
    float_voltage = 14
    boost_reconnect_voltage = 13.8
    low_voltage_reconnect = 10.7
    under_voltage_recover = 11
    under_voltage_warning = 10.9
    low_voltage_disconnect = 10.6
    discharging_limit_voltage = 11
    real_time_clock = [0, 0, 0]
    battery_temperature_warning_upper_limit = 50
    battery_temperature_warning_lower_limit = 5
    battery_temperature_upper_limit_recover = 45
    controller_temperature_upper_limit = 60
    controller_temperature_upper_limit_recover = 55
    sundown_threshold_volts = 10
    sundown_threshold_delay = 30
    sunup_threshold_volts = 15
    sunup_threshold_delay = 30
    load_controlling_modes = 0b0000000000000000
    working_time_length_1 = 0
    working_time_length_2 = 0
    turn_on_timing_1 = [0, 0, 0]
    turn_off_timing_1 = [0, 0, 0]
    turn_on_timing_2 = [0, 0, 0]
    turn_off_timing_2 = [0, 0, 0]
    backlight_time = 5
    length_of_night = 0
    battery_rated_voltage_code = 0
    # ... some missing registers here
    over_temp = False
    is_night = False

    def __init__(self):
        pass

    def get_registers(self) -> Dict[int, bytearray]:
        def uint16(input):
            builder = BinaryPayloadBuilder(byteorder=Endian.Big)
            builder.add_16bit_uint(int(input))
            return builder.to_registers()

        def uint32(input):
            builder = BinaryPayloadBuilder(byteorder=Endian.Big)
            builder.add_32bit_uint(int(input))
            return builder.to_registers()

        return {
            0x3000: uint16(self.array_rated_voltage * 100),
            0x3001: uint16(self.array_rated_current * 100),
            0x3002: uint32(self.array_rated_power * 100),
            0x3004: uint16(self.battery_rated_voltage * 100),
            0x3005: uint16(self.battery_rated_current * 100),
            0x3006: uint32(self.battery_rated_power * 100),
            0x3008: uint16(self.charging_mode),
            0x300E: uint16(self.rated_current_load * 100),
            0x3100: uint16(self.pv_array_input_voltage * 100),
            0x3101: uint16(self.pv_array_input_current * 100),
            0x3102: uint32(self.pv_array_input_current * 100),
            0x3106: uint32(self.battery_charging_power * 100),
            0x310C: uint16(self.load_voltage * 100),
            0x310D: uint16(self.load_current * 100),
            0x310E: uint32(self.load_power * 100),
            0x3110: uint16(self.battery_temperature * 100),
            0x3111: uint16(self.temperature_inside_equipment * 100),
            0x311A: uint16(self.battery_soc * 100),
            0x311B: uint16(self.battery_remote_temperature * 100),
            0x311D: uint16(self.battery_real_rated_power),
            0x3200: uint16(self.battery_status),
            0x3201: uint16(self.charging_equipment_status),
            0x3202: uint16(self.discharging_equipment_status),
            0x3300: uint16(self.max_pv_voltage_today * 100),
            0x3301: uint16(self.min_pv_voltage_today * 100),
            0x3302: uint16(self.max_battery_voltage_today * 100),
            0x3303: uint16(self.min_battery_voltage_today * 100),
            0x3304: uint32(self.consumed_energy_today * 100),
            0x3306: uint32(self.consumed_energy_month * 100),
            0x3308: uint32(self.consumed_energy_year * 100),
            0x330A: uint32(self.total_consumed_energy * 100),
            0x330C: uint32(self.generated_energy_today * 100),
            0x330E: uint32(self.generated_energy_month * 100),
            0x3310: uint32(self.generated_energy_year * 100),
            0x3312: uint32(self.total_generated_energy * 100),
            0x331A: uint16(self.battery_voltage * 100),
            0x331B: uint32(self.battery_current * 100),
            0x9000: uint16(self.battery_type),
            0x9001: uint16(self.battery_capacity),
            0x9002: uint16(self.temperature_compensation_coefficient * 100),
            0x9003: uint16(self.high_voltage_disconnect * 100),
            0x9004: uint16(self.charging_limit_voltage * 100),
            0x9005: uint16(self.over_voltage_reconnect * 100),
            0x9006: uint16(self.equalization_voltage * 100),
            0x9007: uint16(self.boost_voltage * 100),
            0x9008: uint16(self.float_voltage * 100),
            0x9009: uint16(self.boost_reconnect_voltage * 100),
            0x900A: uint16(self.low_voltage_reconnect * 100),
            0x900B: uint16(self.under_voltage_recover * 100),
            0x900C: uint16(self.under_voltage_warning * 100),
            0x900D: uint16(self.low_voltage_disconnect * 100),
            0x900E: uint16(self.discharging_limit_voltage * 100),
            0x9013: uint16(self.real_time_clock[0]),
            0x9014: uint16(self.real_time_clock[1]),
            0x9015: uint16(self.real_time_clock[2]),
            0x9017: uint16(self.battery_temperature_warning_upper_limit * 100),
            0x9018: uint16(self.battery_temperature_warning_lower_limit * 100),
            0x9019: uint16(self.controller_temperature_upper_limit * 100),
            0x901A: uint16(self.controller_temperature_upper_limit_recover * 100),
            0x901E: uint16(self.sundown_threshold_volts * 100),
            0x901F: uint16(self.sundown_threshold_delay),
            0x9020: uint16(self.sunup_threshold_volts * 100),
            0x9021: uint16(self.sunup_threshold_delay),
            0x903D: uint16(self.load_controlling_modes),
            0x903E: uint16(self.working_time_length_1),
            0x903F: uint16(self.working_time_length_2),
            0x9042: uint16(self.turn_on_timing_1[0]),
            0x9043: uint16(self.turn_on_timing_1[1]),
            0x9044: uint16(self.turn_on_timing_1[2]),
            0x9045: uint16(self.turn_off_timing_1[0]),
            0x9046: uint16(self.turn_off_timing_1[1]),
            0x9047: uint16(self.turn_off_timing_1[2]),
            0x9048: uint16(self.turn_on_timing_2[0]),
            0x9049: uint16(self.turn_on_timing_2[1]),
            0x904A: uint16(self.turn_on_timing_2[2]),
            0x904B: uint16(self.turn_off_timing_2[0]),
            0x904C: uint16(self.turn_off_timing_2[1]),
            0x904D: uint16(self.turn_off_timing_2[2]),
            0x9063: uint16(self.backlight_time),
            0x9065: uint16(self.length_of_night),
            0x9067: uint16(self.battery_rated_voltage),
            # bunch missing here in the middle
            0x2000: uint16(1 if self.over_temp else 0),
            0x200C: uint16(1 if self.is_night else 0),
        }


device = FakeDevice()

datablock = ModbusSparseDataBlock(device.get_registers())

context = ModbusServerContext(
    slaves=ModbusSlaveContext(
        di=datablock, co=datablock, hr=datablock, ir=datablock, unit=1, zero_mode=True
    ),
    single=True,
)

identity = ModbusDeviceIdentification(
    info_name={
        "VendorName": "Fake EPever",
        "ProductCode": "AN",
    }
)

logger.info("Starting server")

server = StartSerialServer(
    context=context,
    identity=identity,
    port=args.port,
    framer=ModbusRtuFramer,
    stopbits=1,
    bytesize=8,
    parity="N",
    baudrate=115200,
    logger=logger,
)
