import serial

class DobotConnection:
    serial_conn: serial.SerialBase
    def __init__(self, port: str | None = None, serial_conn: serial.Serial | None = None) -> None: ...
