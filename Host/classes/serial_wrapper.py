import json
import time
import serial
import hashlib


class SerialWrapper:
    def __init__(self, device, baudrate):
        self.serial_connection = serial.Serial(device, baudrate)

    def send_data(self, data: str):
        to_transmit = bytes(data + '\r', 'utf-8')
        self.serial_connection.write(to_transmit)
