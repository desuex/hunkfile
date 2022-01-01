import struct
from typing import NamedTuple

from DataTypes.Serializable import Serializable
class FontDescriptorLine(NamedTuple):
    mystery0: int  #
    mystery1: int  #
    mystery2: int  #
    mystery3: int  #
    mystery4: int  #
    mystery5: int  #
    mystery6: int  #
    mystery7: int  #


class FontDescriptorHeader(NamedTuple):
    mystery0: int # 0
    mystery1: int # 96
    mystery2: int # 65468
    mystery3: int # 28
    mystery4: int # 65496
    count0: int # 322
    count1: int # 3792
    mystery7: int # 0
    mystery8: int # 4
    mystery9: int # 0
    offset0: int # 36
    mystery11: int # 0
    offset1: int # 2612
    mystery13: int # 0
    mystery14: int # 0
    mystery15: int # 0
    offset2: int # 32948
    mystery17: int # 0