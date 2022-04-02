# encoding:utf-8

"""
各个阶段组合逻辑的实现
"""

from basic_unit import *

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
        self.input_key = ["program_data"]
        self.output_key = ["rA","rB","valC"]

    def exc_logic(self):
        if "program_data" not in self.input_list:
            raise Exception("program_data not in Align input_list")

        byte = self.input_list["program_data"][1]
        valC_list = self.input_list["program_data"][2:]
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
