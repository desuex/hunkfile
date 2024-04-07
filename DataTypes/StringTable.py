import struct
from typing import NamedTuple
import xlwt
from mmap import mmap,ACCESS_READ
from xlrd import open_workbook
from tempfile import TemporaryFile

class StringTableRow(NamedTuple):
    def pack(self) -> bytes:
        pass

    id: int
    offset: int
    hash: int
    string: bytes


class StringTable(NamedTuple):
    sig_p1: int
    sig_p2: int
    total: int
    offset_home: int
    hashes_home: int
    hash0: int
    hash1: int
    size: int

    strings: list[StringTableRow]

    def pack(self) -> bytes:
        data = bytes(self.find_size())
        replace = lambda a, b, s: a[:s] + b + a[s + len(b):]
        h = struct.pack('IIIIIII', self.sig_p1, self.sig_p2, len(self.strings), 0x1C, 0x1C + self.total * 4, self.hash0,
                        self.hash1)
        data = replace(data, h, 0)
        for i in range(0, self.total):
            row = self.strings[i]
            offset = struct.pack("I", row.offset)
            data = replace(data, offset, self.offset_home + 4 * i)
            hash = struct.pack("I", row.hash)
            data = replace(data, hash, self.hashes_home + 4 * i)
            data = replace(data, row.string, row.offset)
        # with open('output.bin', 'wb') as f:
        #     f.write(data)
        return struct.pack("II", self.find_size(), 0x4100F) + data

    def pack_(self) -> bytes:
        hashes = self.all_hashes()
        hashes_home = 0x1C + len(hashes)
        offset_home = len(hashes) * 2 + 0x1C
        h = struct.pack('IIIIIII', self.sig_p1, self.sig_p2, len(self.strings), 0x1C, hashes_home, self.hash0,
                        self.hash1)

        for row in self.strings:
            h += struct.pack("I", offset_home)
            offset_home += len(bytearray(row.string, encoding="UTF8")) + 1

        h += hashes

        for row in self.strings:
            current_str = bytearray(row.string, encoding="UTF8") + (0x00).to_bytes(1, byteorder='little', signed=False)
            h += current_str

        return struct.pack("II", len(h), 0x4100F) + h

    def all_hashes(self):
        h = bytes()
        for row in self.strings:
            h += struct.pack("I", row.hash)
        return h

    def find_size(self):
        largest = 0
        for elem in self.strings:
            attempt = elem.offset + len(elem.string)
            if attempt > largest:
                largest = attempt
        return largest+1

    def update_strings(self, str_hash: int, string: bytes):
        strings = list(self.replace_string(str_hash, string))
        return StringTable(self.sig_p1, self.sig_p2, self.total, self.offset_home, self.hashes_home, self.hash0,
                           self.hash1, self.find_size(), strings)

    def update_stringtable(self, strings):

        return StringTable(self.sig_p1, self.sig_p2, self.total, self.offset_home, self.hashes_home, self.hash0,
                           self.hash1, self.find_size(), strings)

    def replace_string(self, str_hash: int, string: bytes):
        found_elem = None

        for elem in self.strings:
            if elem.hash == str_hash:
                found_elem = elem
                break
        if not found_elem:
            raise ValueError("Hash not found")
        # if string != found_elem.string:
        #     raise ValueError(string)
        diff = len(string) - len(found_elem.string)
        # if diff == 0 and string == found_elem.string:
        #     return self.strings
        for elem in self.strings:
            offset_new = elem.offset
            if diff !=0 and offset_new>found_elem.offset:
                offset_new+=diff
            string_new = elem.string
            if elem.hash == found_elem.hash:
                string_new = string
            yield StringTableRow(elem.id, offset_new, elem.hash, string_new)
            # if elem.offset > found_elem.offset:
            #     yield StringTableRow(elem.id, elem.offset + diff+1, elem.hash, elem.string)
            # # elif elem.hash == found_elem.hash:
            # #     yield StringTableRow(elem.id, elem.offset, elem.hash, string)
            # else:
            #     yield elem



    def export_excel(self, filename):
        book = xlwt.Workbook()
        sheet1 = book.add_sheet('sheet1')

        for row in self.strings:
            print(hex(row.hash))
            sheet1.write(row.id, 0, row.id)
            sheet1.write(row.id, 1, row.offset)
            sheet1.write(row.id, 2, row.hash)
            sheet1.write(row.id, 3, hex(row.hash))
            sheet1.write(row.id, 4, row.string.decode("windows-1252", errors="ignore"))
            sheet1.write(row.id, 5, len(row.string))



        name = filename
        book.save(name)
        book.save(TemporaryFile())

