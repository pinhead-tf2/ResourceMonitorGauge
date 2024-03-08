import asyncio
import json

import RPi.GPIO as GPIO
import board
import serial
from busio import I2C as initialize_i2c
from rich.console import Console

# from adafruit_mcp4725 import MCP4725 as initialize_dac

# configs
serial_port = "/dev/serial0"
available_lights = [18, 17, 27]

# other
i2c = initialize_i2c(board.SCL, board.SDA)  # get the SCL and SDA ports initialized
# dac = initialize_dac(i2c)  # prepare the DAC
console = Console()


async def main():
    serial_connection = serial.Serial(serial_port, 9600)
    console.print(f"Listening on {serial_port}...")

    line_cache = []
    cached_values = None

    while True:
        bytes_in_buffer = serial_connection.in_waiting  # gets the amount of bytes in buffer
        received_data = serial_connection.read(bytes_in_buffer)  # reads all data in the buffer

        if received_data:
            if received_data == b'\n':
                received_string = ''.join(line_cache)
                cached_values = json.loads(received_string)
                line_cache = []
            else:
                line_cache.append(received_data.decode('utf-8'))

        # transmit cached_values to DAC as a form of constant data stream
        print(cached_values)


if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for light in available_lights:
        GPIO.setup(light, GPIO.OUT)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("Exiting...")
