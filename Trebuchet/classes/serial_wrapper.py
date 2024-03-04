import serial


class SerialWrapper:
    def __init__(self, device, baudrate):
        self.serial_connection = serial.Serial(device, baudrate, timeout=1)

    def send_data(self, data):
        data = bytes(data + '\n', 'utf-8')
        self.serial_connection.write(data)

