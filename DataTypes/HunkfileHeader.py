import struct
from typing import NamedTuple


class Quad(NamedTuple):
    mystery0: int
    mystery1: int
    mystery2: int
    mystery3: int

    def pack(self) -> bytes:
        return struct.pack('hhhh', self.mystery0, self.mystery1, self.mystery2, self.mystery3)


class HunkfileHeaderRow(NamedTuple):
    name: str
    quad: Quad

    def pack(self) -> bytes:
        padded = bytes(self.name.encode('utf-8')) + bytearray(64 - len(self.name))
        return padded + self.quad.pack()


class HunkfileHeader(NamedTuple):
    mystery0: int
    mystery1: int
    mystery2: int
    mystery3: int
    mystery4: int
    mystery5: int
    mystery6: int
    mystery7: int
    q0: Quad
    q1: Quad
    q2: Quad
    q3: Quad
    q4: Quad
    q5: Quad
    q6: Quad
    q7: Quad

    def pack(self) -> bytes:
        mystery_data = struct.pack('hhhhhhhh', self.mystery0, self.mystery1, self.mystery2, self.mystery3,
                                   self.mystery4, self.mystery5, self.mystery6, self.mystery7)
        full = mystery_data + self.q0.pack() + self.q1.pack() + self.q2.pack() + self.q3.pack() + self.q4.pack() + \
               self.q5.pack() + self.q6.pack() + self.q7.pack()
        return struct.pack("ii", len(full), 0x040070) + full
