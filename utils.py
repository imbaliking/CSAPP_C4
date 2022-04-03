# encoding:utf-8

def convert64(bits):
    if len(bits) == 0:
        return 0
    ret = 0
    sign = int(bits[0],16) > 7
    index = 0
    for byte in reversed(bits):
        if index == 60:
            break
        ret += int(byte,16)*(1<<index)
        index += 4
    if sign:
        ret += (int(bits[0],16) - 8)*(1<<60)
        return ret - (1<<63)
    else:
        ret += int(bits[0],16)*(1<<60)
        return ret

def convert2hex(number):
    if number >= 0:
        base = list(hex(number))[2:]
        if base[-1] == 'L':
            base = base[:-1]
        # 补齐16位
        while len(base) < 16:
            base.insert(0,'0')
        return "".join(base)
    else:
        base = list(hex(number+(1<<63)))
        base[2] = hex(int(base[2],16)+8)
        return "".join(base[4:-1])






if __name__ == "__main__":
    test = "0000000000000003"
    number = 3
    print convert2hex(8)