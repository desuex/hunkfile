import struct
from typing import NamedTuple


class FileHeader(NamedTuple):
    mystery0: int
    data_type: int
    parts: int
    folder_len: int
    filename_len: int
    folder: str
    filename: str

    def pack(self) -> bytes:
        h = struct.pack('hhhhh', self.mystery0, self.data_type, self.parts, len(self.folder)+1, len(self.filename)+1)
        full = h + bytes(self.folder.encode('utf-8')) + b'\x00' + bytes(self.filename.encode('utf-8')) + b'\x00'
        return struct.pack("ii", len(full), 0x040071) + full
