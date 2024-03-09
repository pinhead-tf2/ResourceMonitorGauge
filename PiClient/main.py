import asyncio
import json
import threading
from datetime import datetime

import RPi.GPIO as GPIO
import board
import serial
from busio import I2C as initialize_i2c
from rich.console import Console
from adafruit_mcp4725 import MCP4725 as initialize_dac

# configs
serial_port = "/dev/serial0"
available_lights = [17, 27, 22, 23]
display_rotate_timer = 15

# other
i2c = initialize_i2c(board.SCL, board.SDA)  # get the SCL and SDA ports initialized
dac = initialize_dac(i2c)  # prepare the DAC
console = Console()

cached_values = None
current_display_value = None
led_position = 0


def current_time():
    # prints out the colored current time with ms for console-like output
    return f"[aquamarine3][{datetime.now().strftime('%T.%f')[:-3]}][/aquamarine3] "


def display_values():
    global cached_values, current_display_value, led_position  # i know repeat creation of global is bad but ¯\_(ツ)_/¯

    if cached_values is not None:
        all_keys = list(cached_values.keys())

        if current_display_value is not None:
            current_index = all_keys.index(current_display_value)

            if len(all_keys) == current_index + 1:
                led_position = 0
                current_display_value = all_keys[led_position]
            else:
                led_position = current_index + 1
                current_display_value = all_keys[led_position]
        else:
            led_position = 0
            current_display_value = all_keys[led_position]

    try:
        console.print(f"{current_time()}"
                      f"Displaying {current_display_value}, LED {available_lights[led_position]} at {led_position}\n"
                      f"Current Values: {cached_values}")
        threading.Timer(display_rotate_timer, display_values).start()
    except RuntimeError or KeyboardInterrupt:
        console.print(f"{current_time()}Bye!")


async def exercise_gauges():
    console.print(f"{current_time()}Exercising gauges...")

    for i in range(4095):
        dac.raw_value = i

    await asyncio.sleep(1)

    for i in range(4095, -1, -1):
        dac.raw_value = i


async def main():
    await exercise_gauges()

    serial_connection = serial.Serial(serial_port, 9600)
    console.print(f"{current_time()}Listening on {serial_port}...")
    threading.Timer(5.0, display_values).start()

    line_cache = []
    global cached_values, current_display_value, led_position

    while True:
        bytes_in_buffer = serial_connection.in_waiting  # gets the amount of bytes in buffer
        received_data = serial_connection.read(bytes_in_buffer)  # reads all data in the buffer

        if received_data:
            if received_data == b'\r':
                received_string = ''.join(line_cache)
                try:
                    cached_values = json.loads(received_string)
                except json.decoder.JSONDecodeError:
                    console.print(f"{current_time()}[bold red]DecodeError:[/bold red] {received_string}")
                line_cache = []
            else:
                line_cache.append(received_data.decode('utf-8'))

        if cached_values and current_display_value and led_position is not None:  # basic exist check
            dac.raw_value = cached_values[current_display_value]
            try:
                GPIO.output(available_lights[led_position], GPIO.HIGH)

                if led_position < 0:
                    GPIO.output(available_lights[-1], GPIO.LOW)
                else:
                    GPIO.output(available_lights[led_position - 1], GPIO.LOW)
            except IndexError:  # led position list might be too short, avoid issues
                console.print(f"{current_time()}[bold red]led_position array length mismatch[/bold red]\n"
                              f"Data point count too large for available_lights list")
                exit(1)


if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for light in available_lights:
        GPIO.setup(light, GPIO.OUT)
        GPIO.output(light, GPIO.LOW)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print(f"\n{current_time()}Exiting...")
        dac.raw_value = 0
        for light in available_lights:
            GPIO.output(light, GPIO.LOW)
