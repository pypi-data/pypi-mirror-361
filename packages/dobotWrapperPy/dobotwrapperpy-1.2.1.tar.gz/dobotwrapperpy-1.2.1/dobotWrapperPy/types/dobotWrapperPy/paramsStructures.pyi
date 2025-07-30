from .enums.CPMode import CPMode as CPMode
from .enums.EMotorIndex import EMotorIndex as EMotorIndex
from .enums.IOFunction import IOFunction as IOFunction
from .enums.jogCmd import JogCmd as JogCmd
from .enums.jogMode import JogMode as JogMode
from .enums.level import Level as Level
from .enums.ptpMode import PTPMode as PTPMode
from .enums.realTimeTrack import RealTimeTrack as RealTimeTrack
from .enums.tagVersionColorSensorAndIR import TagVersionColorSensorAndIR as TagVersionColorSensorAndIR
from .enums.tagVersionRail import tagVersionRail as tagVersionRail
from .enums.triggerCondition import TriggerCondition as TriggerCondition
from .enums.triggerMode import TriggerMode as TriggerMode
from dataclasses import dataclass

@dataclass
class tagWithL:
    is_with_rail: bool
    version: tagVersionRail
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagWithL: ...

@dataclass
class tagWithLReturn:
    is_with_rail: bool
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagWithLReturn: ...

@dataclass
class tagPose:
    x: float
    y: float
    z: float
    r: float
    jointAngle: list[float]
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagPose: ...

@dataclass
class tagHomeParams:
    x: float
    y: float
    z: float
    r: float
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagHomeParams: ...

@dataclass
class tagHomeCmd:
    reserved: int
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagHomeCmd: ...

@dataclass
class tagAutoLevelingParams:
    isAutoLeveling: bool
    accuracy: float
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagAutoLevelingParams: ...

@dataclass
class tagEndEffectorParams:
    xBias: float
    yBias: float
    zBias: float
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagEndEffectorParams: ...

@dataclass
class tagJOGJointParams:
    velocity: list[float]
    acceleration: list[float]
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagJOGJointParams: ...

@dataclass
class tagJOGCoordinateParams:
    velocity: list[float]
    acceleration: list[float]
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagJOGCoordinateParams: ...

@dataclass
class tagJOGCommonParams:
    velocityRatio: float
    accelerationRatio: float
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagJOGCommonParams: ...

@dataclass
class tagJOGCmd:
    isJoint: JogMode
    cmd: JogCmd
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagJOGCmd: ...

@dataclass
class tagJOGLParams:
    velocity: float
    acceleration: float
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagJOGLParams: ...

@dataclass
class tagPTPJointParams:
    velocity: list[float]
    acceleration: list[float]
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagPTPJointParams: ...

@dataclass
class tagPTPCoordinateParams:
    xyzVelocity: float
    rVelocity: float
    xyzAcceleration: float
    rAcceleration: float
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagPTPCoordinateParams: ...

@dataclass
class tagPTPJumpParams:
    jumpHeight: float
    zLimit: float
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagPTPJumpParams: ...

@dataclass
class tagPTPCommonParams:
    velocityRatio: float
    accelerationRatio: float
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagPTPCommonParams: ...

@dataclass
class tagPTPCmd:
    ptpMode: PTPMode
    x: float
    y: float
    z: float
    r: float
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagPTPCmd: ...

@dataclass
class tagPTPLParams:
    velocity: float
    acceleration: float
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagPTPLParams: ...

@dataclass
class tagPTPWithLCmd:
    ptpMode: PTPMode
    x: float
    y: float
    z: float
    r: float
    l: float
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagPTPWithLCmd: ...

@dataclass
class tagPTPJump2Params:
    startJumpHeight: float
    endJumpHeight: float
    zLimit: float
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagPTPJump2Params: ...

@dataclass
class tagPOCmd:
    ratio: int
    address: int
    level: int
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagPOCmd: ...

@dataclass
class tagCPParams:
    planAcc: float
    junctionAcc: float
    acceleratio_or_period: float
    realTimeTrack: RealTimeTrack
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagCPParams: ...

@dataclass
class tagCPCmd:
    cpMode: CPMode
    x: float
    y: float
    z: float
    velocity_or_power: float
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagCPCmd: ...

@dataclass
class tagARCParams:
    xyzVelocity: float
    rVelocity: float
    xyzAcceleration: float
    rAcceleration: float
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagARCParams: ...

@dataclass
class tagARCCmd:
    @dataclass
    class Point:
        x: float
        y: float
        z: float
        r: float
        def __init__(self, x: float, y: float, z: float, r: float) -> None: ...
        def pack(self) -> bytes: ...
        @classmethod
        def unpack(cls, data: bytes) -> tagARCCmd.Point: ...
    circPoint: Point
    toPoint: Point
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagARCCmd: ...
    def __init__(self, circPoint, toPoint) -> None: ...
    def __replace__(self, *, circPoint, toPoint) -> None: ...

@dataclass
class tagWAITCmd:
    timeout: int
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagWAITCmd: ...

@dataclass
class tagTRIGCmd:
    address: int
    mode: TriggerMode
    condition: TriggerCondition
    threshold: int
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagTRIGCmd: ...

@dataclass
class tagIOMultiplexing:
    address: int
    multiplex: IOFunction
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagIOMultiplexing: ...

@dataclass
class tagIODO:
    address: int
    level: Level
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagIODO: ...

@dataclass
class tagIOPWM:
    address: int
    frequency: float
    dutyCycle: float
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagIOPWM: ...

@dataclass
class tagIODI:
    address: int
    level: Level
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagIODI: ...

@dataclass
class IOADC:
    address: int
    value: int
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> IOADC: ...

@dataclass
class tagEMOTOR:
    address: EMotorIndex
    insEnabled: bool
    speed: int
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagEMOTOR: ...

@dataclass
class tagDevice:
    isEnabled: bool
    port: int
    version: TagVersionColorSensorAndIR
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagDevice: ...

@dataclass
class tagColor:
    red: int
    green: int
    blue: int
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagColor: ...

@dataclass
class tagWIFIIPAddress:
    dhcp: bool
    addr: list[int]
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagWIFIIPAddress: ...

@dataclass
class tagWIFINetmask:
    addr: list[int]
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagWIFINetmask: ...

@dataclass
class tagWIFIGateway:
    addr: list[int]
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagWIFIGateway: ...

@dataclass
class tagWIFIDNS:
    addr: list[int]
    def pack(self) -> bytes: ...
    @classmethod
    def unpack(cls, data: bytes) -> tagWIFIDNS: ...
