import enum

class IOFunction(enum.Enum):
    DUMMY = 0
    DO = 1
    PWM = 2
    DI = 3
    ADC = 4
    DIPU = 5
    DIPD = 6
