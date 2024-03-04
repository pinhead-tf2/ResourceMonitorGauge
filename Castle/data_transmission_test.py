import asyncio

import serial

serial_port = "/dev/serial0"


async def main():
    connection = serial.Serial(serial_port, 9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                               bytesize=serial.EIGHTBITS)
    print(f"Listening on {serial_port}...")

    line_cache = []

    while True:
        bytes_in_buffer = connection.in_waiting  # gets the amount of bytes in buffer
        received_data = connection.read(bytes_in_buffer)  # reads all data in the buffer

        if received_data:
            # connection.write(received_data)

            if received_data == b'\n':
                # transmit to DAC
                received_string = ''.join(line_cache)
                line_cache = []
                print(f"String: {received_string}")
            else:
                line_cache.append(received_data.decode('utf-8'))


if __name__ == '__main__':
    asyncio.run(main())
