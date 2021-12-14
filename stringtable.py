import re

regex = r"(?:<Hash=0x)([0-9a-fA-F]+)(?:>\t)([\w\W]+?(?=\Z|<Hash))"
encoded = u"AßBÚÀEËÐÃÄÅKÑMHOÒPCTÈØXŒÖÕÁÂÝÏÔÛÜÿõùýðeëéâáôóòàãèöpcåyøxñçüæïœîäþê"
decoded = u"АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя"
with open("Dialog.csv", 'r') as fp:
    data = fp.read()
for i in range(0, 66):
    data = data.replace(decoded[i], encoded[i])
matches = re.finditer(regex, data, re.MULTILINE)
matches_list = list(matches)
matches_cnt = len(matches_list)
# print(matches_list[0][2])
# print(0x01000000)
# for matchNum, match in enumerate(matches, start=1):
# print(match.groups())
sig = [0x01, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00]
pointer_base = matches_cnt * 8 + 0x1C
with open('Dialog.bin', 'wb') as fp:
    fp.write(bytearray(sig))
    fp.write(matches_cnt.to_bytes(4, byteorder='little', signed=False))  # records count
    fp.write((0x1C).to_bytes(4, byteorder='little', signed=False))  # pointers loc
    fp.write((matches_cnt * 4 + 0x1C).to_bytes(4, byteorder='little', signed=False))  # hashes loc
    fp.write((0x00).to_bytes(4, byteorder='little', signed=False))  # zeros
    fp.write((0x00).to_bytes(4, byteorder='little', signed=False))  # magic hash of unknown purpose
    for rec in matches_list:
        fp.write(pointer_base.to_bytes(4, byteorder='little', signed=False))  # location of string
        pointer_base += len(bytearray(rec[2][:-1], encoding="UTF8"))+1
    for rec in matches_list:
        fp.write(int("0x" + rec[1], 16).to_bytes(4, byteorder='little', signed=False))  # location of string
    for rec in matches_list:
        fp.write(bytearray(rec[2][:-1], encoding="UTF8"))  # string itself
        fp.write((0x00).to_bytes(1, byteorder='little', signed=False))  # zeros

