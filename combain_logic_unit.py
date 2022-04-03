# encoding:utf-8

"""
各个阶段组合逻辑的实现
"""

from basic_unit import *
from Command import byte2command
from utils import *

"""
stage 1
"""

class Split(logicUnit):
    """
    取指阶段里面的分割逻辑，将icode和ifun分开的逻辑
    和icode，ifun逻辑合到一起了，增加了imem_error 的判断
    """

    def __init__(self):
        super(Split,self).__init__()
        self.icode = '0'
        self.ifun = '0'
        self.input_key = ["program_data","imem_error"]
        self.output_key = ["icode",'ifun']

    def exc_logic(self):
        if "program_data" not in self.input_list:
            raise Exception("program_data not in Split input_list")

        if "imem_error" not in self.input_list:
            raise Exception("imem_error not in Split input_list")

        byte = self.input_list["program_data"][0]
        self.icode = byte[0]
        self.ifun = byte[1]
        if not self.input_list["imem_error"]:
            self.output_list["icode"] = self.icode
            self.output_list["ifun"] = self.ifun
        else:
            # 出错时将指令设置为nop
            self.output_list["icode"] = '1'
            self.output_list["ifun"] = '0'


class Align(logicUnit):
    """
    取值阶段里的分割逻辑，将rA，rB，valC分别取出
    """

    def __init__(self):
        super(Align,self).__init__()
        self.rA = '0'
        self.rB = '0'
        self.valC = '0000000000000000'
        self.input_key = ["program_data","need_regids"]
        self.output_key = ["rA","rB","valC"]

    def exc_logic(self):
        if self.input_list["need_regids"]:
            byte = self.input_list["program_data"][1]
            valC_list = self.input_list["program_data"][2:10]
        else:
            byte = 'FF'
            valC_list = self.input_list["program_data"][1:9]
        self.rA = byte[0]
        self.rB = byte[1]
        self.valC = ""
        for single_byte in valC_list:
            self.valC += single_byte

class instr_valid(logicUnit):
    """
    判断指令是否合法的逻辑
    """

    def __init__(self):
        super(instr_valid,self).__init__()
        self.input_key = ["icode"]
        self.output_key = ["instr_valid"]

    def exc_logic(self):
        if int(self.input_list["icode"],16) > 11:
            self.output_list["instr_valid"] = True
        else:
            self.output_list["instr_valid"] = False

class Need_valC(logicUnit):
    """
    判断指令是否需要直接数
    """

    def __init__(self):
        super(Need_valC,self).__init__()
        self.input_key = ["icode"]
        self.output_key = ["need_valC"]

    def exc_logic(self):
        if self.input_list['icode'] not in byte2command:
            # 指令不合法，直接置为False
            self.output_list['need_valC'] = False
        else:
            command_name = byte2command[self.input_list['icode']]
            # 只有下面这些指令用得到直接数
            self.output_list["need_valC"] = \
                command_name in ['IIRMOVQ','IRMMOVQ','IMRMOVQ','IJXX','ICALL']


class Need_regids(logicUnit):
    """
    判断指令是否需要寄存器
    """

    def __init__(self):
        super(Need_regids,self).__init__()
        self.input_key = ['icode']
        self.output_key = ['need_regids']

    def exc_logic(self):
        if self.input_list["icode"] not in byte2command:
            self.output_list["need_regids"] = False
        else:
            command_name = byte2command[self.input_list['icode']]
            self.output_list["need_regids"] = \
                command_name in ['IRRMOVQ','IOPQ','IPUSHQ','IPOPQ','IIRMOVQ','IRMMOVQ','IMRMOVQ']

class PC_Increment(logicUnit):
    """
    PC增加器
    """

    def __init__(self):
        super(PC_Increment,self).__init__()
        self.input_key = ["need_valC",'need_regids','PC']
        self.output_key = ['valP']

    def exc_logic(self):

        r = int(self.input_list["need_valC"])
        i = int(self.input_list["need_regids"])
        p = int(self.input_list["PC"],16)
        valP = p + 1 + r + 8*i
        self.output_list["valP"] = hex(valP)


"""
stage 2
"""

class dstE(logicUnit):
    """
    寄存器文件的其中一个写入地址
    """

    def __init__(self):
        super(dstE,self).__init__()
        self.input_key = ["Cnd","icode","rB"]
        self.output_key = ["dstE"]
        # 默认值不写入任何寄存器
        self.dstE = 'F'

    def exc_logic(self):

        command_name = byte2command[self.input_list["icode"]]
        if command_name == "IRRMOVQ" and self.input_list["Cnd"]:
            self.dstE = self.input_list['rB']
        if command_name in ['IIRMOVQ','IOPQ']:
            self.dstE = self.input_list['rB']
        if command_name in ['IPUSHQ','IPOPQ','ICALL','IRET']:
            # %rsp
            self.dstE = '4'
        self.output_list["dstE"] = self.dstE

class dstM(logicUnit):

    def __init__(self):
        super(dstM,self).__init__()
        self.input_key = ["icode",'rA']
        self.output_key = ['dstM']
        self.dstM = 'F'

    def exc_logic(self):

        command_name = byte2command[self.input_list['icode']]
        if command_name in ['IMRMOVQ','IPOPQ']:
            self.dstM = self.input_list['rA']

        self.output_list["dstM"] = self.dstM


class srcA(logicUnit):

    def __init__(self):
        super(srcA,self).__init__()
        self.input_key = ['icode','rA']
        self.output_key = ['srcA']
        self.srcA = 'F'

    def exc_logic(self):

        command_name = byte2command[self.input_list['icode']]
        if command_name in ['IRRMOVQ','IRMMOVQ','IOPQ','IPUSHQ']:
            self.srcA = self.input_list['rA']
        if command_name in ['IPOPQ','IRET']:
            self.srcA = '4'
        self.output_list['srcA'] = self.srcA


class srcB(logicUnit):

    def __init__(self):
        super(srcB,self).__init__()
        self.input_key = ['icode','rB']
        self.output_key = ['srcB']
        self.srcB = 'F'

    def exc_logic(self):
        command_name = byte2command[self.input_list['icode']]
        if command_name in ['IOPQ','IRMMOVQ','IMRMOVQ']:
            self.srcB = self.input_list['rB']
        if command_name in ['IPUSHQ','IPOPQ','ICALL','IRET']:
            self.srcB = '4'

        self.output_list['srcB'] = self.srcB

"""
stage 3
"""

class SetCC(logicUnit):
    """
    判断是否需要设置标志位的逻辑
    """
    def __init__(self):
        super(SetCC,self).__init__()
        self.input_key = ['icode']
        self.output_key = ['set_cc']

    def exc_logic(self):
        command_name = byte2command[self.input_list["icode"]]
        self.output_list['set_cc'] = command_name == 'IOPQ'

class ALU(logicUnit):
    """
    ALU单元实现,第一个操作数是B，第二个是A，都是八字节数
    """
    def __init__(self):
        super(ALU,self).__init__()
        self.input_key = ['aluA','aluB','alufun']
        self.output_key = ['valE','ZF','SF','OF']
        self.B = 0
        self.A = 0
        self.fun = 0
        self.max_overflow = (1<<64) - 1
        self.min_overflow = -(1<<64)
        self.ZF = False
        self.SF = False
        self.OF = False

    def exc_logic(self):
        valE = 0
        self.B = convert64(self.input_list["aluB"])
        self.A = convert64(self.input_list["aluA"])
        self.fun = self.input_list["alufun"]
        if self.fun == '0':
            valE = self.B + self.A
        if self.fun == '1':
            valE = self.B - self.A
        if self.fun == '2':
            valE = self.B & self.A
        if self.fun == '3':
            valE = self.B ^ self.A
        if valE == 0:
            self.OF = True
        if valE < 0:
            self.SF = True
        if valE > self.max_overflow or valE < self.min_overflow:
            self.OF = True
            # 溢出处理，不过对负溢出可能有问题
            valE = valE & 0xFFFFFFFFFFFFFFFF

        self.output_list["valE"] = valE


class aluA(logicUnit):
    """
    alu的第二个操作数
    """
    def __init__(self):
        super(aluA,self).__init__()
        self.input_key = ['icode','valC','valA']
        self.output_key = ['aluA']
        self.alu_A = ''

    def exc_logic(self):
        command_name = byte2command[self.input_list['icode']]
        if command_name in ["IRRMOVQ",'IOPQ']:
            self.alu_A = self.input_list["valA"]
        if command_name in ["IIRMOVQ",'IRMMOVQ','IMRMOVQ']:
            self.alu_A = self.input_list['valC']
        if command_name in ['ICALL','IPUSHQ']:
            self.alu_A = convert2hex(-8)
        if command_name in ['IRET','IPOPQ']:
            self.alu_A = convert2hex(8)
        self.output_list['aluA'] = self.alu_A

class aluB(logicUnit):
    """
    alu的第一个操作数
    """
    def __init__(self):
        super(aluB,self).__init__()
        self.input_key = ["icode",'valB']
        self.output_key = ['aluB']
        self.aluB = ''

    def exc_logic(self):
        command_name = byte2command[self.input_list["icode"]]
        if command_name in ['IRMMOVQ','IMRMOVQ','IOPQ','ICALL','IPUSHQ','IRET','IPOPQ']:
            self.aluB = self.input_list["valB"]
        if command_name in ["IRRMOVQ",'IIRMOVQ']:
            self.aluB = '0'
        self.output_list["aluB"] = self.aluB


class ALUfun(logicUnit):

    def __init__(self):
        super(ALUfun,self).__init__()
        self.input_key = ['icode','ifun']
        self.output_key = ["alufun"]

    def exc_logic(self):
        if self.input_list['icode'] == '6':
            self.output_list['alufun'] = self.input_list['ifun']
        else:
            self.output_list['alufun'] = '0'


class Cond(logicUnit):

    def __init__(self):
        super(Cond,self).__init__()
        self.input_key = ["ZF","SF","OF","ifun"]
        self.output_key = ["Cnd"]
        self.cnd = False

    def exc_logic(self):
        self.ZF = self.input_list["ZF"]
        self.SF = self.input_list["SF"]
        self.OF = self.input_list["OF"]
        self.ifun = self.input_list["ifun"]
        if self.ifun == '0':
            self.cnd = True
        if self.ifun == '1':
            self.cnd = (self.SF ^ self.OF)|self.ZF
        if self.ifun == "2":
            self.cnd = self.SF ^ self.OF
        if self.ifun == "3":
            self.cnd = self.ZF
        if self.ifun == "4":
            self.cnd = not self.ZF
        if self.ifun == "5":
            self.cnd = not (self.SF ^ self.OF)
        if self.ifun == "6":
            self.cnd = not((self.SF ^ self.OF)|self.ZF)

        self.output_list["Cnd"] = self.cnd

"""
stage 4
"""

class memRead(logicUnit):

    def __init__(self):
        super(memRead,self).__init__()
        self.input_key = ["icode"]
        self.output_key = ["mem_read"]

    def exc_logic(self):
        command_name = byte2command[self.input_list["icode"]]
        self.output_list["mem_read"] = command_name in ["IMRMOVQ","IPOPQ",'IRET']


class memWrite(logicUnit):

    def __init__(self):
        super(memWrite,self).__init__()
        self.input_key = ["icode"]
        self.output_key = ["mem_write"]

    def exc_logic(self):
        command_name = byte2command[self.input_list["icode"]]
        self.output_list['mem_write'] = command_name in ["IRMMOVQ",'IPUSHQ','ICALL']


class memAddr(logicUnit):

    def __init__(self):
        super(memAddr,self).__init__()
        self.input_key = ["icode","valE",'valA']
        self.output_key = ["mem_addr"]
        self.addr = ""

    def exc_logic(self):
        command_name = byte2command[self.input_list["icode"]]
        if command_name in ["IRMMOVQ","IPUSHQ","ICALL","IMRMOVQ"]:
            self.addr = self.input_list["valE"]
        if command_name in ["IPOPQ","IRET"]:
            self.addr = self.input_list["valA"]
        self.output_list["mem_addr"] = self.addr


class memData(logicUnit):

    def __init__(self):
        super(memData,self).__init__()
        self.input_key = ["valA","valP","icode"]
        self.output_key = ["mem_data"]
        self.data = ""

    def exc_logic(self):
        command_name = byte2command[self.input_list["icode"]]
        if command_name in ["IRMMOVQ","IPUSHQ"]:
            self.data = self.input_list["valA"]
        if command_name == "ICALL":
            self.data = self.input_list["valP"]
        self.output_list["mem_data"] = self.data

class Stat(logicUnit):

    def __init__(self):
        super(Stat,self).__init__()
        self.input_key = ["imem_error","dmem_error",'instr_valid',"icode"]
        self.output_key = ["Stat"]
        self.stat = 0

    def exc_logic(self):
        if self.input_list["imem_error"] | self.input_list["dmem_error"]:
            self.stat = 2
        if not self.input_list["instr_valid"]:
            self.stat = 3
        if byte2command[self.input_list["icode"]] == "IHALT":
            self.stat = 4
        self.output_list["SAOK"] = self.stat


"""
stage 5
"""

class newPC(logicUnit):

    def __init__(self):
        super(newPC,self).__init__()
        self.input_key = ["icode","Cnd","valC","valM","valP"]
        self.output_key = ["new_pc"]
        self.pc = ""

    def exc_logic(self):
        command_name = byte2command[self.input_list["icode"]]
        self.pc = self.input_list["valP"]
        if command_name == "ICALL":
            self.pc = self.output_list["valC"]

        if command_name == "IJXX" and self.input_list["Cnd"]:
            self.pc = self.output_list["valC"]

        if command_name == "IRET":
            self.pc = self.output_list["valM"]

        self.output_list["new_pc"] = self.pc
