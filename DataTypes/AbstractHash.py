import struct
from typing import NamedTuple

from DataTypes.Serializable import Serializable


class AbstractHash(NamedTuple):
    hashes: list[int]

    def pack(self) -> bytes:
        h = struct.pack("B"*(len(self.hashes)),*self.hashes)
        # header_data = bytes()
        # for h in self.hashes:
        #     header_data += struct.pack('B', h)
        return struct.pack("II", len( h ), 0x40002) +  h
