import re
import openpyxl
from pandas import DataFrame

regex = r"(?:<Hash=0x)([0-9a-fA-F]+)(?:>\t)([\w\W]+?(?=\Z|<Hash))"
with open("common.csv", 'r') as fp:
    data = fp.read()
matches = re.finditer(regex, data, re.MULTILINE)
matches_list = list(matches)
matches_cnt = len(matches_list)
hashes = []
strings = []
#
for match in matches_list:
    hashes.append(match[1])
    strings.append(match[2])

df = DataFrame({'Hash': hashes, 'English': strings})
df.to_excel('common.xlsx', sheet_name='sheet1', index=False)