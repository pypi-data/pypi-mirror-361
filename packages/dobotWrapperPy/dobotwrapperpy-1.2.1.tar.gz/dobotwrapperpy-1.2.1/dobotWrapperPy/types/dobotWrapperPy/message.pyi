from .enums.CommunicationProtocolIDs import CommunicationProtocolIDs as CommunicationProtocolIDs
from .enums.ControlValues import ControlValues as ControlValues

class Message:
    header: bytes
    len: int
    ctrl: ControlValues
    params: bytes
    checksum: int | None
    id: CommunicationProtocolIDs
    def __init__(self, b: bytes | None = None) -> None: ...
    def refresh(self) -> None: ...
    def verify_checksum(self) -> bool: ...
    def bytes(self) -> bytes: ...
