

def convert64(bits):
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
        return hex(number)
    else:
        base = list(hex(number+(1<<63)))
        base[2] = hex(int(base[2],16)+8)
        return "".join(base[4:-1])






if __name__ == "__main__":
    test = "FFFFFFFFFFFFFFFF"
    number = -3
    print convert2hex(number)