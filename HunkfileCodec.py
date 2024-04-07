import re
import struct
import pickle

from xlrd import open_workbook

from DataTypes.AbstractHash import AbstractHash
from DataTypes.Empty import Empty
from DataTypes.FileHeader import FileHeader
from DataTypes.HunkfileHeader import HunkfileHeader, HunkfileHeaderRow, Quad
from DataTypes.Serializable import Serializable
from DataTypes.StringTable import StringTable, StringTableRow


class HunkfileCodec:
    hnkdir: str
    xlsdir: str

    def __init__(self, hnkdir, xlsdir):
        self.hnkdir = hnkdir
        self.xlsdir = xlsdir

    def read_hunkfile(self, filename):
        with open(filename, 'rb') as fp:
            while True:
                int1 = fp.read(4)
                if not int1:
                    break
                int2 = fp.read(4)
                if not int2:
                    break
                record_size = struct.unpack('I', int1)[0]
                record_type = struct.unpack('I', int2)[0]
                data = fp.read(record_size)

                yield record_size, record_type, data

    def print_record(self, record_size, record_type, data: str):
        match record_type:
            case 0x40070:
                print("HUNKFILE header")

            case 0x40071:
                print("FILENAME header")
                print(data)
            case 0x40072:
                print("EMPTY")
            case 0x40002:
                print("Abstract hash identifier")
            case 0x4100F:
                print("TSEStringTable main")

            case 0x45100:
                print("ClankBodyTemplate main")
            case 0x402100:
                print("ClankBodyTemplate secondary")
            case 0x43100:
                print("ClankBodyTemplate name")
            case 0x44100:
                print("ClankBodyTemplate data")
            case 0x404100:
                print("ClankBodyTemplate data 2")

            case 0x4300c:
                print("LiteScript main")
            case 0x4200c:
                print("LiteScript data")
            case 0x4100c:
                print("LiteScript data 2")

            case 0x204090:
                print("SqueakSample data")

            case 0x41150:
                print("TSETexture header")
            case 0x40151:
                print("TSETexture data")
            case 0x801151:
                print("TSETexture data 2")

            case 0x101050:
                print("RenderModelTemplate header")
            case 0x40054:
                print("RenderModelTemplate data")
            case 0x20055:
                print("RenderModelTemplate data table")

            case 0x42005:
                print("Animation data")
            case 0x41005:
                print("Animation data 2")

            case 0x41007:
                print("RenderSprite data")
            case 0x43112:
                print("EffectsParams data")

            case 0x43087:
                print("TSEFontDescriptor data")

            case 0x43083:
                print("TSEDataTable data 1")
            case 0x4008a:
                print("TSEDataTable data 2")

            case 0x43088:
                print("StateFlowTemplate data")
            case 0x42088:
                print("StateFlowTemplate data 2")

            case 0x204092:
                print("SqueakStream data")
            case 0x201092:
                print("SqueakStream data 2")

            case 0x42009:
                print("EntityPlacement data")
            case 0x103009:
                print("EntityPlacement data 2")
            case 0x101009:
                print("EntityPlacement BCC data")
            case 0x102009:
                print("EntityPlacement level data")

            case 0x101008:
                print("EntityTemplate data")

            case _:
                print(hex(record_type))
                print("UNK!")

        print(record_size)
        print(len(data))
        print("\n")

    def look_through_all_hunkfiles(self, listing_filename):
        with open(listing_filename, 'r') as filep:
            lines = filep.readlines()
            for line in lines:
                res = self.read_hunkfile(line.rstrip("\n"))
                for r in res:
                    self.print_record(*r)

    def parse_all_hunkfiles(self, listing_filename):
        with open(listing_filename, 'r') as filep:
            lines = filep.readlines()
            for line in lines:
                yield self.parse_single_file(line.rstrip("\n"))
                # for r in res:
                #     yield self.parse_single_file(r[0])

    def look_single_file(self, filename):
        res = self.read_hunkfile(filename.rstrip("\n"))
        for r in res:
            self.print_record(*r)

    def parse_single_file(self, filename):
        res = self.read_hunkfile(filename.rstrip("\n"))
        for r in res:
            yield self.parse_record(*r)

    def parse_hunkfile_header(self, data):
        values = struct.unpack('hhhhhhhh', data[0:16])
        rows = self.parse_hunkfile_rows(data)
        return HunkfileHeader(*values, *rows)

    def parse_hunkfile_rows(self, data):
        for i in range(0, 8):
            ifrom = 16 + (64 + 8) * i
            ito = 16 + (64 + 8) * i + 64
            val = data[ifrom:ito].decode('utf-8').rstrip('\x00')

            maxsize, type = struct.unpack('ii', data[ito:ito + 8])
            yield HunkfileHeaderRow(val, maxsize, type)

    def parse_filename_header(self, data):
        values = struct.unpack('hhhhh', data[0:10])
        folder = data[10:10 + values[3]][:-1]
        filename = data[10 + values[3]:10 + values[3] + values[4]][:-1]
        return FileHeader(*values, folder.decode('utf-8'), filename.decode('utf-8'))

    def parse_abstract_hash(self, data):
        hashes = struct.unpack("B" * (len(data)), data)
        return AbstractHash(list(hashes))

    def parse_empty(self, data):
        return Empty(data)

    def parse_stringtable_alt(self, data, size):
        values = struct.unpack('IIIIIII', data[0:28])
        offsets = struct.unpack('I' * values[2], data[values[3]:values[4]])
        hashes = struct.unpack('I' * values[2], data[values[4]:(values[4] + 4 * values[2])])
        rows = self.parse_rows_alt(data, offsets, hashes)
        return StringTable(*values, size, list(rows))

    def parse_rows_alt(self, data, offsets, hashes):
        for i in range(0, len(offsets)):
            offset = offsets[i]
            hash = hashes[i]
            s = 0
            single_str = bytes()
            while True:
                c = data[offset + s]

                if c == 0:
                    break
                single_str += c.to_bytes(1, "little")
                s += 1
            yield StringTableRow(i, offset, hash, single_str)

    def parse_record(self, record_size, record_type, data: str):
        match record_type:
            case 0x40070:
                return self.parse_hunkfile_header(data)

            case 0x40071:
                return self.parse_filename_header(data)

            case 0x40072:
                return self.parse_empty(data)
            case 0x40002:
                h = self.parse_abstract_hash(data)
                return h
            case 0x4100F:
                return self.parse_stringtable_alt(data, record_size)

            # case 0x45100:
            #     print("ClankBodyTemplate main")
            # case 0x402100:
            #     print("ClankBodyTemplate secondary")
            # case 0x43100:
            #     print("ClankBodyTemplate name")
            # case 0x44100:
            #     print("ClankBodyTemplate data")
            # case 0x404100:
            #     print("ClankBodyTemplate data 2")
            #
            # case 0x4300c:
            #     print("LiteScript main")
            # case 0x4200c:
            #     print("LiteScript data")
            # case 0x4100c:
            #     print("LiteScript data 2")
            #
            # case 0x204090:
            #     print("SqueakSample data")
            #
            # case 0x41150:
            #     print("TSETexture header")
            # case 0x40151:
            #     print("TSETexture data")
            # case 0x801151:
            #     print("TSETexture data 2")
            #
            # case 0x101050:
            #     print("RenderModelTemplate header")
            # case 0x40054:
            #     print("RenderModelTemplate data")
            # case 0x20055:
            #     print("RenderModelTemplate data table")
            #
            # case 0x42005:
            #     print("Animation data")
            # case 0x41005:
            #     print("Animation data 2")
            #
            # case 0x41007:
            #     print("RenderSprite data")
            # case 0x43112:
            #     print("EffectsParams data")
            #
            # case 0x43087:
            #     print("TSEFontDescriptor data")
            #
            # case 0x43083:
            #     print("TSEDataTable data 1")
            # case 0x4008a:
            #     print("TSEDataTable data 2")
            #
            # case 0x43088:
            #     print("StateFlowTemplate data")
            # case 0x42088:
            #     print("StateFlowTemplate data 2")
            #
            # case 0x204092:
            #     print("SqueakStream data")
            # case 0x201092:
            #     print("SqueakStream data 2")
            #
            # case 0x42009:
            #     print("EntityPlacement data")
            # case 0x103009:
            #     print("EntityPlacement data 2")
            # case 0x101009:
            #     print("EntityPlacement BCC data")
            # case 0x102009:
            #     print("EntityPlacement level data")
            #
            # case 0x101008:
            #     print("EntityTemplate data")

            case _:
                # print("Record of current type doesn't have an implemented parser")
                # return data
                return self.parse_empty(data)
                # raise ValueError("Record of current type doesn't have an implemented parser")

    def parse(self, filename):
        return list(self.parse_single_file(self.hnkdir + filename))

    def parse_and_store(self, filename):
        with open(filename + '.pickle', 'wb') as f:
            data = self.parse(filename)
            pickle.dump(data, f)

    def load_stored(self, filename):
        """

        :param filename:
        :return:
        """
        with open(filename + '.pickle', 'rb') as f:
            return pickle.load(f)

    def pack(self, data, filename):
        with open(self.hnkdir + filename, 'wb') as fp:
            row: Serializable
            for row in data:
                fp.write(row.pack())

    def encode_cyrillic(self, cyr) -> bytes:
        # encoded = u"AßBÚÀEËÐÃÄÅKÑMHOÒPCTÈØXŒÖÕÁÂÝÏÔÛÜÿõùýðeëéâáôóòàãèöpcåyøxñçüæïœîäþê"
        encoded = u"AßBÚÀEËÐÃÄÅKÑMHOÒPCTÈØXŒÖÕÁÂÝÏÔÛÜÿõùýðeëéâáôóòàãèöpcåyøxñçüæïœîäþê"
        decoded = u"АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя"
        # encoded = u"A6BrDEEW3NNKnMHOnPCTYFXu4wWbibEURa6Brdeew3uuknMHonpctyfxu4wwbibeuR"
        for i in range(0, 66):
            cyr = cyr.replace(decoded[i], encoded[i])
        # return bytearray(cyr)
        return cyr.encode("ANSI")

    def hex2int(self, hex: str) -> int:
        if hex[1] == "x":
            return int(hex, 0)
        return int(hex, 16)

    def open_csv(self, filename):
        with open(filename, 'r', newline='\n') as csvfile:
            test_str = csvfile.read()
            regex = r"([0-9A-F]+)(?:\t)(?:(?:\")([^\"]+)(?:[\"]{1}))*"
            matches = re.finditer(regex, test_str, re.MULTILINE)

            for matchNum, match in enumerate(matches, start=1):
                yield match.groups()

    def build_stringtable(self, sheet):
        total = len(sheet)
        base_offset = (total * 8) + 28
        current_offset = base_offset
        next_id = 0
        next_offset = current_offset
        for line in sheet:
            id = next_id
            current_offset = next_offset

            h = self.hex2int(line[0])
            t = line[1]
            # t = self.encode_cyrillic(line[1])
            print("Hash: " + hex(h))
            print("String: " + t.decode("UTF-8"))
            print("Offset: " + str(current_offset))
            if len(t) < 1:
                raise ValueError("Empty string on hash " + hex(h))
            next_id += 1
            next_offset += len(t) + 1
            yield StringTableRow(id, current_offset, h, t)

    def dump_loca(self, hunkfile):
        data = self.parse(hunkfile)
        print(data[2].export_excel(self.xlsdir + "Common.xls"))
        print(data[6].export_excel(self.xlsdir + "Dialog.xls"))
        print(data[10].export_excel(self.xlsdir + "lcCommon.xls"))
        print(data[14].export_excel(self.xlsdir + "lcPc.xls"))

    def dump_global_en(self, hunkfile):
        data = self.parse(hunkfile)
        print(data[2].export_excel(self.xlsdir + "Credits.xls"))
        print(data[6].export_excel(self.xlsdir + "lcCommon_global_en.xls"))
        print(data[10].export_excel(self.xlsdir + "lcPc_global_en.xls"))

    def build_excel_rows(self, sheet):
        base_offset = sheet.nrows * 8 + 28
        next_offset = base_offset
        for i in range(0, sheet.nrows):
            offset = next_offset
            # print(int(sheet.cell_value(i, 2)))
            # print(hex(int(sheet.cell_value(i, 2))))
            # encoded_str = str(sheet.cell_value(i, 6));
            # encoded_str = self.encode_cyrillic(str(sheet.cell_value(i, 6))) # You probably don't need cyrillization
            next_offset += len(sheet.cell_value(i, 4))+1
            yield StringTableRow(int(sheet.cell_value(i, 0)), offset, int(sheet.cell_value(i, 2)),
                                 str(sheet.cell_value(i, 4)).encode("utf-8"))
    def build_excel_rows_rus(self, sheet):
        for i in range(0, sheet.nrows):
            yield StringTableRow(int(sheet.cell_value(i, 0)), int(sheet.cell_value(i, 1)), int(sheet.cell_value(i, 2)),
                                 self.encode_cyrillic(str(sheet.cell_value(i, 6)))+b'\0')

    def import_excel(self, filename, sheet_id):

        wb = open_workbook(filename)
        sheet = wb.sheet_by_index(sheet_id)
        rows = list(self.build_excel_rows(sheet))
        return StringTable(1, 2, sheet.nrows, 28, sheet.nrows * 4 + 28, 0, 178778297, 0, rows)
