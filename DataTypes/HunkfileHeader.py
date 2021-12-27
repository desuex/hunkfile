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
    maxsize: int
    type:int

    def pack(self) -> bytes:
        padded = bytes(self.name.encode('utf-8')) + bytearray(64 - len(self.name))
        return padded + struct.pack('ll', self.maxsize*2, self.type) #localization compatibility hack, remove maxsize multiplier to keep size


class HunkfileHeader(NamedTuple):
    mystery0: int
    mystery1: int
    mystery2: int
    mystery3: int
    mystery4: int
    mystery5: int
    mystery6: int
    mystery7: int
    q0: HunkfileHeaderRow
    q1: HunkfileHeaderRow
    q2: HunkfileHeaderRow
    q3: HunkfileHeaderRow
    q4: HunkfileHeaderRow
    q5: HunkfileHeaderRow
    q6: HunkfileHeaderRow
    q7: HunkfileHeaderRow

    def pack(self) -> bytes:
        mystery_data = struct.pack('hhhhhhhh', self.mystery0, self.mystery1, self.mystery2, self.mystery3,
                                   self.mystery4, self.mystery5, self.mystery6, self.mystery7)
        full = mystery_data + self.q0.pack() + self.q1.pack() + self.q2.pack() + self.q3.pack() + self.q4.pack() + \
               self.q5.pack() + self.q6.pack() + self.q7.pack()
        return struct.pack("ii", len(full), 0x040070) + full
