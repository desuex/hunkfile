import re


class TorusAssetCodec:
    regex = r"(?:<Hash=0x)([0-9a-fA-F]+)(?:>\t)([\w\W]+?(?=\Z|<Hash))"
    encoded = u"AßBÚÀEËÐÃÄÅKÑMHOÒPCTÈØXŒÖÕÁÂÝÏÔÛÜÿõùýðeëéâáôóòàãèöpcåyøxñçüæïœîäþê"  # Carefully selected extended Latin chars
    decoded = u"АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    custom_charset_size = 66
    stringtable_sig = [0x01, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00]

    def plain2bin(self, filename, output):
        """
        File format (tab separated, LF breaks, last line MUST be empty):

        <Hash=0xB412CAF>	One of us... One of us...
        <Hash=0xA1E882A3>	Wait second!

        :param filename: Plain text file for single TSEStringTable
        :param output: Converted TSEStringTable binary file path
        """
        with open(filename, 'r') as fp:
            data = fp.read()
        data = self.russify(data)
        matches_list = self.parse_lines(data)
        self.write_binary_stringtable(matches_list, output)

    def russify(self, text):
        """

        :param text: Translated text (Russian)
        :return: Translated text with replaced Cyrillic characters
        """
        for i in range(0, self.custom_charset_size):
            text = text.replace(self.decoded[i], self.encoded[i])
        return text

    def parse_lines(self, text):
        """

        :param text: Any lines with hash
        :return: List of matches
        """
        return list(re.finditer(self.regex, text, re.MULTILINE))

    def write_binary_stringtable(self, matches_list, filename):
        """

        :param matches_list: Matches list
        :param filename: Output bin filename
        """
        matches_cnt = len(matches_list)
        pointer_base = matches_cnt * 8 + 0x1C

        with open(filename, 'wb') as fp:
            # First writing a constant signature
            fp.write(bytearray(self.stringtable_sig))
            fp.write(matches_cnt.to_bytes(4, byteorder='little', signed=False))  # records count
            fp.write((0x1C).to_bytes(4, byteorder='little', signed=False))  # pointers loc
            fp.write((matches_cnt * 4 + 0x1C).to_bytes(4, byteorder='little', signed=False))  # hashes loc
            fp.write((0x00).to_bytes(4, byteorder='little', signed=False))  # zeros
            fp.write((0x00).to_bytes(4, byteorder='little', signed=False))  # magic hash of unknown purpose
            for rec in matches_list:
                fp.write(pointer_base.to_bytes(4, byteorder='little', signed=False))  # location of string
                pointer_base += len(bytearray(rec[2][:-1], encoding="UTF8")) + 1
            for rec in matches_list:
                fp.write(int("0x" + rec[1], 16).to_bytes(4, byteorder='little', signed=False))  # location of string
            for rec in matches_list:
                fp.write(bytearray(rec[2][:-1], encoding="UTF8"))  # string itself
                fp.write((0x00).to_bytes(1, byteorder='little', signed=False))  # zeros
