import struct
from typing import NamedTuple


class Empty(NamedTuple):
    v:str
    def pack(self) -> bytes:
        return struct.pack("II", 0, 0x040072)
