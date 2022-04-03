# encoding:utf-8
"""
实现四个跟时序有关的硬件
"""
from basic_unit import *

class programCounter(timerUnit):
    """
    程序计数器的实现
    """

    def __init__(self):
        super(programCounter,self).__init__()
        # 程序计数器保存的当前指令地址，在电平没有变化前一直输出
        self.program_address = 0
        self.input_key = ["PC"]
        self.output_key = ["PC"]

    def low2high(self):
        """
        程序计数器在电平从低到高时输出它记录的程序地址
        :return:
        """
        self.output_list["PC"] = self.program_address

    def high2low(self):
        """
        程序计数器在电平从高到低时记录传输到它输入端口的程序地址
        :return:
        """
        if "PC" not in self.input_list:
            raise Exception("PC arg not in PC input_list")
        self.program_address = self.input_list["PC"]

    def init_PC(self,PC):
        self.program_address = PC


class statusRegister(timerUnit):
    """
    条件码寄存器的实现
    """

    def __init__(self):
        super(statusRegister,self).__init__()
        # 零标志 代表上一次算术操作结果为0
        self.ZF = False
        # 符号标志 代表上一次算术操作结果为负数
        self.SF = False
        # 溢出标志 代表上一次算术操作导致一个补码溢出
        self.OF = False
        self.input_key = ['ZF','SF','OF','set_cc']

    def low2high(self):
        """
        电平从低到高时，将输出切换为输入的标志
        :return:
        """
        if self.input_list["set_cc"]:
            self.ZF = self.input_list["ZF"]
            self.SF = self.input_list["SF"]
            self.OF = self.input_list["OF"]
        self.output_list["ZF"] = self.ZF
        self.output_list["SF"] = self.SF
        self.output_list["OF"] = self.OF




class dataMemory(timerUnit):
    """
    数据内存的实现，大小不限，没初始化就报错，没问题的
    """

    def __init__(self):
        super(dataMemory,self).__init__()
        self.memory = {}
        self.input_key = [
            "read_flag",  #读标志
            "write_flag", #写标志
            "mem_addr",   #要操作的内存地址
            "mem_data"    #要写入的内存数据
        ]
        self.output_key = [
            "valM",       #输出数据
            "dmem_error"  #错误标志
        ]
        self.valM = 0
        self.dmem_error = False

    def low2high(self):
        """
        电平切换时，执行的读或者写操作
        :return:
        """
        self.high2low()

    def high2low(self):
        """
        电平切换时，执行的读或者写操作
        :return:
        """
        for key in self.input_key:
            if key not in self.input_list:
                raise Exception("%s not in dataMemory input_list"%(key))

        # TODO:没有考虑read和write都设置为1的情况
        if self.input_list["read_flag"]:
            # 读取数据
            if self.input_list["mem_addr"] not in self.memory:
                # 读取没有初始化的内存，报错
                self.valM = 0
                self.dmem_error = True
            else:
                # 正常输出读取到的内存
                self.valM = self.memory[self.input_list["mem_addr"]]
                self.dmem_error = False
        elif self.input_list["write_flag"]:
            # 写入数据
            self.memory[self.input_list["mem_addr"]] = self.input_list["mem_data"]
        else:
            # 读和写操作都没设置，什么都不做
            pass
        self.output_list["valM"] = self.valM
        self.output_list["dmem_error"] = self.dmem_error

class registerFile(timerUnit):
    """
    寄存器文件的实现
    """
    def __init__(self):
        super(registerFile,self).__init__()
        # 按照Y86-64的编码顺序排列的寄存器编号
        self.register_list = [
            "%rax","%rcx","%rdx","%rbx","%rsp","%rbp","%rsi","%rdi","%r8","%r9","%r10","%r11","%r12","%r13","%r14"
        ]
        # 寄存器保存的位置
        self.register_memory = {}
        self.input_key = [
            "dstE", "valE",
            "dstM", "valM",
            "srcA", "srcB"
        ]
        self.output_key = [
            "valA","valB"
        ]

    def low2high(self):
        """
        寄存器文件在电平从低到高时，开始读取数据
        :return:
        """

        for key in self.input_key:
            if key not in self.input_list:
                raise Exception("%s not in registerFile input_list" % (key))

        if self.input_list["srcA"] == 'F':
            self.output_list["valA"] = "0"
        else:
            register = self.register_list[int(self.input_list["srcA"],16)]
            if register not in self.register_memory:
                raise Exception("%s not in register_memory" % (register))
            else:
                output = self.register_memory[register]
                self.output_list["valA"] = output

        if self.input_list["srcB"] == 'F':
            self.output_list["valB"] = "0"
        else:
            register = self.register_list[int(self.input_list["srcB"], 16)]
            if register not in self.register_memory:
                raise Exception("%s not in register_memory" % (register))
            else:
                output = self.register_memory[register]
                self.output_list["valB"] = output


    def high2low(self):
        """
        寄存器文件从高到低，开始写入数据
        :return:
        """

        for key in self.input_key:
            if key not in self.input_list:
                raise Exception("%s not in registerFile input_list" % (key))

        if self.input_list["dstE"] != "F":
            # 只有为有效的寄存器值才写入
            register = self.register_list[int(self.input_list["dstE"], 16)]
            self.register_memory[register] = self.input_list["valE"]

        if self.input_list["dstM"] != "F":
            # 只有为有效的寄存器值才写入
            register = self.register_list[int(self.input_list["dstM"], 16)]
            self.register_memory[register] = self.input_list["valM"]


class programMemory(timerUnit):
    """
    程序内存的实现，之所以和数据内存分开，是因为要开个后门
    """

    def __init__(self):
        super(programMemory,self).__init__()
        # 使用list模拟内存,每个元素是一个byte，初始化为0x00
        self.memory = []
        self.input_key = [
            "PC"
        ]
        self.output_key = [
            "program_data",
            "imem_error"
        ]

    def low2high(self):
        """
        电平从低到高，读取数据
        :return:
        """
        if "PC" not in self.input_list:
            raise Exception(" PC not in programMemory input_list")

        address = int(self.input_list["PC"], 16)
        if address > len(self.memory):
            self.output_list["program_data"] = ''
            self.output_list["imem_error"] = True
        else:
            self.output_list["program_data"] = self.memory[address:address+10]
            self.output_list["imem_error"] = False

    def load_program_data(self,start_address,program_str):
        """
        初始化程序内存
        :param start_address: 程序的开始地址，十六进制表示
        :param program_str: 程序的代码十六进制表示
        :return:
        """
        start = int(start_address,16)
        # 地址前面的数值初始化为0
        for i in range(start):
            self.memory[i] = "00"

        byte = ""
        double = False
        # 将地址开始后的字符串初始化为输入值
        for bits in program_str:
            byte += bits
            if double:
                double = False
                self.memory.append(byte)
                byte = ""
            else:
                double = True

        # 后面增加10位防止读取内存的时候获取不到
        for i in range(10):
            self.memory.append('00')