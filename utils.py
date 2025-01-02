
import re
from collections.abc import Iterable
import z3


K1, K2, K3, K4, K5, K6, K7, K8, K9, K10 = z3.BitVecs(["K1", "K2", "K3", "K4", "K5", "K6", "K7", "K8", "K9", "K10"], 1)
K11, K12, K13, K14, K15, K16, K17, K18, K19, K20 = z3.BitVecs(["K11", "K12", "K13", "K14", "K15", "K16", "K17", "K18", "K19", "K20"], 1)
K21, K22, K23, K24, K25, K26, K27, K28, K29, K30 = z3.BitVecs(["K21", "K22", "K23", "K24", "K25", "K26", "K27", "K28", "K29", "K30"], 1)
K31, K32, K33, K34, K35, K36, K37, K38, K39, K40 = z3.BitVecs(["K31", "K32", "K33", "K34", "K35", "K36", "K37", "K38", "K39", "K40"], 1)
K41, K42, K43, K44, K45, K46, K47, K48, K49, K50 = z3.BitVecs(["K41", "K42", "K43", "K44", "K45", "K46", "K47", "K48", "K49", "K50"], 1)
K51, K52, K53, K54, K55, K56, K57, K58, K59, K60 = z3.BitVecs(["K51", "K52", "K53", "K54", "K55", "K56", "K57", "K58", "K59", "K60"], 1)
K61, K62, K63, K64, K65, K66, K67, K68, K69, K70 = z3.BitVecs(["K61", "K62", "K63", "K64", "K65", "K66", "K67", "K68", "K69", "K70"], 1)
K71, K72, K73, K74, K75, K76, K77, K78, K79, K80 = z3.BitVecs(["K71", "K72", "K73", "K74", "K75", "K76", "K77", "K78", "K79", "K80"], 1)

V1, V2, V3, V4, V5, V6, V7, V8, V9, V10 = z3.BitVecs(["V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8", "V9", "V10"], 1)
V11, V12, V13, V14, V15, V16, V17, V18, V19, V20 = z3.BitVecs(["V11", "V12", "V13", "V14", "V15", "V16", "V17", "V18", "V19", "V20"], 1)
V21, V22, V23, V24, V25, V26, V27, V28, V29, V30 = z3.BitVecs(["V21", "V22", "V23", "V24", "V25", "V26", "V27", "V28", "V29", "V30"], 1)
V31, V32, V33, V34, V35, V36, V37, V38, V39, V40 = z3.BitVecs(["V31", "V32", "V33", "V34", "V35", "V36", "V37", "V38", "V39", "V40"], 1)
V41, V42, V43, V44, V45, V46, V47, V48, V49, V50 = z3.BitVecs(["V41", "V42", "V43", "V44", "V45", "V46", "V47", "V48", "V49", "V50"], 1)
V51, V52, V53, V54, V55, V56, V57, V58, V59, V60 = z3.BitVecs(["V51", "V52", "V53", "V54", "V55", "V56", "V57", "V58", "V59", "V60"], 1)
V61, V62, V63, V64, V65, V66, V67, V68, V69, V70 = z3.BitVecs(["V61", "V62", "V63", "V64", "V65", "V66", "V67", "V68", "V69", "V70"], 1)
V71, V72, V73, V74, V75, V76, V77, V78, V79, V80 = z3.BitVecs(["V71", "V72", "V73", "V74", "V75", "V76", "V77", "V78", "V79", "V80"], 1)


def flatten(xs):  # reference: https://stackoverflow.com/questions/2158395/flatten-an-irregular-arbitrarily-nested-list-of-lists
    for x in xs:
        if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
            yield from flatten(x)
        else:
            yield x


def human_seconds(seconds, display='.2f'):  # reference: https://github.com/facebookresearch/demucs/blob/v2/demucs/utils.py
    value = seconds * 1e6
    ratios = [1e3, 1e3, 60, 60, 24]
    names = ['us', 'ms', 's', 'min', 'hrs', 'days']
    last = names.pop(0)
    for name, ratio in zip(names, ratios):
        if value / ratio < 0.3:
            break
        value /= ratio
        last = name
    return f"{format(value, display)} {last}"



def atoi(text):  # reference: https://stackoverflow.com/questions/5967500/how-to-correctly-sort-a-string-with-a-number-inside
    return int(text) if text.isdigit() else text


def natural_keys(text):  # reference: https://stackoverflow.com/questions/5967500/how-to-correctly-sort-a-string-with-a-number-inside
    return [atoi(c) for c in re.split(r'(\d+)', str(text))]


def numbering(idx, hyphen=False):
    if idx%10==1:
        return f"{idx}{'-' if hyphen else ''}st"
    elif idx%10==2:
        return f"{idx}{'-' if hyphen else ''}nd"
    elif idx%10==3:
        return f"{idx}{'-' if hyphen else ''}rd"
    else:
        return f"{idx}{'-' if hyphen else ''}th"


def LOAD_IV(iv):
  
    state = [1]*3 + [0]*285
    
    iv_bits = byte2bit(iv[::-1], inv=False)
    state[-173:-93] = iv_bits
    
    return state


def xor_str(eq_list):
    return ' + '.join((sorted(eq_list, key=natural_keys)))


def XOR(a, b):
    if a==["0"]:
        return b
    elif b==["0"]:
        return a
    else:
        new_a = [a_ele for a_ele in a if not a_ele in b]
        new_b = [b_ele for b_ele in b if not b_ele in a]
        return new_a + new_b
    
    
def AND(a, b):
    if a==["0"] or b==["0"] or a==[] or b==[]:
        return ["0"]
    elif a==["1"]:
        return b
    elif b==["1"]:
        return a    
    elif len(a)==1 and len(b)==1:
        return [f"({a[0]}*{b[0]})"]
    elif len(a)==1:
        return [f"({a[0]}*({' + '.join(b)}))"]
    elif len(b)==1:
        return [f"(({' + '.join(a)})*{b[0]})"]
    else:
        return [f"(({' + '.join(a)})*({' + '.join(b)}))"]


def get_set(tar_list):
    return sorted(set(flatten(tar_list)) - {""}, key=natural_keys)


def linearize_res(linear_sig, linear_rst, linear=0):
    if linear==2:
        return ', '.join(re.findall(r'k[0-9]+', ''.join(get_set(linear_sig))))
    elif linear_rst[0]==['']:
        return ' + '.join(linear_sig[0])
    elif linear_rst[1]==['']:
        return ' + '.join(linear_sig[1])
    elif linear_sig[0]==[]:
        return ' + '.join(XOR(linear_sig[1], ['1']))
    elif linear_sig[1]==[]:
        return ' + '.join(XOR(linear_sig[0], ['1']))
    else:
        return ' + '.join(XOR(XOR(linear_sig[0], linear_sig[1]), ['1']))


def bit2byte(total_bit):
    if type(total_bit[0])!=str:
        total_bit = "".join([str(bit) for bit in total_bit])
    return [int(total_bit[byte*8:(byte+1)*8][::-1], 2) for byte in range(10)]


def byte2bit(total_byte, inv=True):
    if inv:
        total_bit = [format(byte, '08b')[::-1] for byte in total_byte]
    else:
        total_bit = [format(byte, '08b') for byte in total_byte]
        
    return [eval(bit) for bit in ''.join(total_bit)]


def str2z3(eq, mode="v"):
    return eval(eq.replace(mode, "V" if mode=="v" else "K").replace("+", "^").replace("*", "&"))
