import asyncio

import RPi.GPIO as GPIO
import board
import serial
from busio import I2C as initialize_i2c

# from adafruit_mcp4725 import MCP4725 as initialize_dac

# configs
serial_port = "/dev/serial0"

# other
i2c = initialize_i2c(board.SCL, board.SDA)  # get the SCL and SDA ports initialized
# dac = initialize_dac(i2c)  # prepare the DAC

cached_values = None


async def main():
    connection = serial.Serial(serial_port, 9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                               bytesize=serial.EIGHTBITS)
    print(f"Listening on {serial_port}...")

    line_cache = []
    global cached_values

    while True:
        bytes_in_buffer = connection.in_waiting  # gets the amount of bytes in buffer
        received_data = connection.read(bytes_in_buffer)  # reads all data in the buffer

        if received_data:
            if received_data == b'\n':
                received_string = ''.join(line_cache)
                cached_values = received_string.split(sep=',')
                line_cache = []
            else:
                line_cache.append(received_data.decode('utf-8'))

        # transmit cached_values to DAC as a form of constant data stream
        print(cached_values)


if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(18, GPIO.OUT)
    asyncio.run(main())
