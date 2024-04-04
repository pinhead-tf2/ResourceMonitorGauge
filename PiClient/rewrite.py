import asyncio
import time
from datetime import datetime

import board
from adafruit_mcp4725 import MCP4725 as initialize_dac
from busio import I2C as initialize_i2c
from rich.console import Console

# configs
serial_port = "/dev/serial0"
available_lights = [17, 27, 22, 23]
display_rotate_timer = 15
announce_display = True

# other
i2c = initialize_i2c(board.SCL, board.SDA)  # get the SCL and SDA ports initialized
dac = initialize_dac(i2c)  # prepare the DAC
console = Console()


def current_time():
    # prints out the colored current time with ms for console-like output
    return f"[aquamarine3][{datetime.now().strftime('%T.%f')[:-3]}][/aquamarine3] "


async def exercise_gauge():
    console.print(f"{current_time()}Exercising gauge...")

    for i in range(4095):
        dac.raw_value = i

    await asyncio.sleep(1)

    for i in range(4095, -1, -1):
        dac.raw_value = i


async def main():
    await exercise_gauges()

    serial_connection = None
    while not serial_connection:
        try:
            serial_connection = serial.Serial(serial_port, 9600)
            console.print(f"{current_time()}Listening on {serial_port}...")
        except serial.SerialException:
            console.printf(
                f"{current_time()}[bold red][violet]{serial_port}[/violet] not found! Retrying in 15 seconds...")
            await asyncio.sleep(15)

    next_rotation = 0
    active_light = 0  # will only be none if lights aren't configured/misconfigured
    used_lights = []

    while True:
        bytes_in_buffer = serial_connection.in_waiting  # gets the amount of bytes in buffer
        received_data = serial_connection.read(bytes_in_buffer)  # reads all data in the buffer

        # data receiving
        if received_data:
            # check and see if we hit the end of the transferred string, append it to cache if not ended yet
            if received_data == b'\r':
                received_string = ''.join(line_cache)  # combine cache with end of string to get full block of data

                try:
                    cached_values = json.loads(received_string)
                except json.decoder.JSONDecodeError:  # handles occasional string endings that got missed
                    console.print(f"{current_time()}[bold red]DecodeError:[/bold red] {received_string}")

                line_cache = []
            else:
                line_cache.append(received_data.decode('utf-8'))  # decode so it doesn't have to be decoded later

        # gauge & led handling
        if time.time() > next_rotation:
            all_keys = list(cached_values.keys())

            # setting up leds
            if len(all_keys) > len(available_lights):
                console.print(
                    f"{current_time()}"
                    f"[orange]Number of keys ({len(all_keys)}) exceeds available lights ({len(available_lights)})! "
                    f"Lights will not be used.[/orange]")
                active_light = None
            elif len(all_keys) != len(used_lights):
                bindings = []
                for index, key in enumerate(all_keys):
                    used_lights.append(available_lights[index])
                    bindings.append([key, available_lights[index]])

                console.print(f"{current_time()}[green]Light Bindings: [/green]{bindings}")

            if active_light is not None:


            # finally, set the next timer
            next_rotation = time.time() + display_rotate_timer


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
