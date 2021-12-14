import struct
from typing import NamedTuple


class StringTableRow(NamedTuple):
    def pack(self) -> bytes:
        pass

    offset: int
    hash: int
    string: str


class StringTable(NamedTuple):
    sig_p1: int
    sig_p2: int
    total: int
    offset_home: int
    hashes_home: int
    hash0: int
    hash1: int

    strings: list[StringTableRow]

    def pack(self) -> bytes:
        hashes = self.all_hashes()
        hashes_home = 0x1C+len(hashes)
        offset_home = len(hashes) * 2 + 0x1C
        h = struct.pack('IIIIIII', self.sig_p1, self.sig_p2,  len(self.strings), 0x1C, hashes_home, self.hash0,
                        self.hash1)

        for row in self.strings:
            h += struct.pack("I", offset_home)
            offset_home += len(bytearray(row.string, encoding="UTF8"))+1

        h += hashes

        for row in self.strings:
            current_str = bytearray(row.string, encoding="UTF8") + (0x00).to_bytes(1, byteorder='little', signed=False)
            h += current_str

        return struct.pack("ii", len(h), 0x4100F) + h

    def all_hashes(self):
        h = bytes()
        for row in self.strings:
            h += struct.pack("I", row.hash)
        return h
