# encoding:utf-8
from timer_unit import *
from combain_logic_unit import *

class mother_board(object):

    def __init__(self):
        self.logic_comp_list = [Split,Align,instr_valid,Need_valC,Need_regids,PC_Increment,
                                dstE,dstM,srcA,srcB,
                                SetCC,ALU,aluA,aluB,ALUfun,Cond,
                                memRead,memWrite,memAddr,memData,Stat,
                                newPC]
        self.timer_comp_list = [programCounter,statusRegister,dataMemory,registerFile,programMemory]
        # 硬件实例化，保证每一个硬件只有一个对象，通过字典定位
        self.logic_comp = {}
        for logic_class in self.logic_comp_list:
            self.logic_comp[logic_class.__name__] = logic_class()
        self.timer_comp = {}
        for timer_class in self.timer_comp_list:
            self.timer_comp[timer_class.__name__] = timer_class()
        # 所有线路的名称，方便展示
        self.mother_line = ["PC","icode","ifun","rA","rB","valC","valP","valA","valB",'dstE',"dstM","srcA","srcB","valE",
                            "Cnd","valM","Stat","instr_valid","imem_error","dmem_error","need_valC","need_regids","set_cc",
                            "aluA","aluB","alufun","ZF","OF","SF","mem_read","mem_write","mem_addr","mem_data","new_pc"]

        # 线路实例化成属性，储存当前值，方便查看
        self.PC = ""
        self.icode = '0'
        self.ifun = '0'
        self.rA = '0'
        self.rB = '0'
        self.valC = ""
        self.valP = ""
        self.valA = ""
        self.valB = ""
        self.dstE = ""
        self.dstM = ""
        self.srcA = ""
        self.srcB = ""
        self.valE = ""
        self.Cnd = False
        self.valM = ""
        self.Stat = "0"
        self.instr_valid = False
        self.imem_error = False
        self.dmem_error = False
        # 存储变化用的
        self.last_data = {}

    def display(self):
        dirty_value = []
        clean_value = []
        for attr in dir(self):
            if attr not in self.mother_line:
                continue
            if attr not in self.last_data:
                self.last_data[attr] = getattr(self,attr)
                dirty_value.append((attr,getattr(self,attr)))
            elif self.last_data[attr] != getattr(self,attr):
                self.last_data[attr] = getattr(self,attr)
                dirty_value.append((attr,getattr(self,attr)))
            else:
                clean_value.append((attr,getattr(self,attr)))

        dirty = ""
        clean = ""
        for attr_name,attr_value in dirty_value:
            dirty += "%s:%s "%(attr_name,attr_value)
        for attr_name,attr_value in clean_value:
            clean += "%s:%s "%(attr_name,attr_value)

        print "变化的值如下："
        print dirty
        print "没有变化的值如下:"
        print clean

    def display_mem(self):
        print "内存值如下："
        print self.timer_comp["dataMemory"].memory

    def display_reg(self):
        print "寄存器值如下："
        print self.timer_comp["registerFile"].register_memory

    def pause(self):
        a = raw_input()

    def run(self):
        """
        CPU主要运行函数
        :return:
        """

        # 暂时，当状态为HALT时停止运行
        while(self.Stat != 4):
            # 时钟周期开始的上升沿
            # 第一阶段 取指
            self.timer_comp["programCounter"].switch_state()
            self.PC = self.timer_comp["programCounter"].output_signal()["PC"]
            self.timer_comp["programMemory"].input_signal(PC=self.PC)
            self.timer_comp["programMemory"].switch_state()
            self.program_data = self.timer_comp["programMemory"].output_signal()["program_data"]
            self.imem_error = self.timer_comp["programMemory"].output_signal()["imem_error"]
            # 指令分解
            self.logic_comp["Split"].input_signal(program_data=self.program_data,imem_error=self.imem_error)
            self.icode = self.logic_comp["Split"].output_signal()["icode"]
            self.ifun = self.logic_comp["Split"].output_signal()["ifun"]
            # 检查合法性
            self.logic_comp["instr_valid"].input_signal(icode=self.icode)
            self.instr_valid = self.logic_comp["instr_valid"].output_signal()["instr_valid"]
            self.logic_comp["Need_valC"].input_signal(icode=self.icode)
            self.need_valC = self.logic_comp["Need_valC"].output_signal()["need_valC"]
            self.logic_comp["Need_regids"].input_signal(icode=self.icode)
            self.need_regids = self.logic_comp["Need_regids"].output_signal()["need_regids"]
            # 参数值分解
            self.logic_comp["Align"].input_signal(program_data=self.program_data,need_regids=self.need_regids)
            self.rA = self.logic_comp["Align"].output_signal()["rA"]
            self.rB = self.logic_comp["Align"].output_signal()["rB"]
            self.valC = self.logic_comp["Align"].output_signal()["valC"]
            # PC增加
            self.logic_comp["PC_Increment"].input_signal(need_valC = self.need_valC,need_regids = self.need_regids,PC=self.PC)
            self.valP = self.logic_comp["PC_Increment"].output_signal()["valP"]

            print "阶段1："
            self.display()
            self.pause()

            # 第二阶段 译码
            # 写回是发生在下降沿的时刻，现在阶段是上升沿
            self.logic_comp["dstE"].input_signal(Cnd=self.Cnd,icode=self.icode,rB=self.rB)
            self.dstE = self.logic_comp["dstE"].output_signal()["dstE"]
            self.logic_comp["dstM"].input_signal(icode=self.icode,rA=self.rA)
            self.dstM = self.logic_comp["dstM"].output_signal()["dstM"]
            self.logic_comp["srcA"].input_signal(icode=self.icode,rA=self.rA)
            self.srcA = self.logic_comp["srcA"].output_signal()["srcA"]
            self.logic_comp["srcB"].input_signal(icode=self.icode,rB=self.rB)
            self.srcB = self.logic_comp["srcB"].output_signal()["srcB"]
            self.timer_comp["registerFile"].input_signal(dstE=self.dstE,dstM=self.dstM,srcA=self.srcA,srcB=self.srcB,
                                                         valM=self.valM,valE=self.valE)
            self.timer_comp["registerFile"].switch_state()
            self.valA = self.timer_comp["registerFile"].output_signal()["valA"]
            self.valB = self.timer_comp["registerFile"].output_signal()["valB"]

            print "阶段2："
            self.display()
            self.pause()

            # 第三阶段 执行
            self.logic_comp["SetCC"].input_signal(icode=self.icode)
            self.set_cc = self.logic_comp["SetCC"].output_signal()["set_cc"]
            self.logic_comp["aluA"].input_signal(icode=self.icode,valC=self.valC,valA=self.valA)
            self.aluA = self.logic_comp["aluA"].output_signal()["aluA"]
            self.logic_comp["aluB"].input_signal(icode=self.icode,valB=self.valB)
            self.aluB = self.logic_comp["aluB"].output_signal()["aluB"]
            self.logic_comp["ALUfun"].input_signal(icode=self.icode,ifun=self.ifun)
            self.alufun = self.logic_comp["ALUfun"].output_signal()["alufun"]
            self.logic_comp["ALU"].input_signal(aluA=self.aluA,aluB=self.aluB,alufun=self.alufun)
            self.valE = self.logic_comp["ALU"].output_signal()["valE"]
            self.ZF = self.logic_comp["ALU"].output_signal()["ZF"]
            self.OF = self.logic_comp["ALU"].output_signal()["OF"]
            self.SF = self.logic_comp["ALU"].output_signal()["SF"]
            self.timer_comp["statusRegister"].input_signal(ZF=self.ZF,OF=self.OF,SF=self.SF,set_cc=self.set_cc)
            self.timer_comp["statusRegister"].switch_state()
            self.ZF = self.timer_comp["statusRegister"].output_signal()["ZF"]
            self.OF = self.timer_comp["statusRegister"].output_signal()["OF"]
            self.SF = self.timer_comp["statusRegister"].output_signal()["SF"]
            self.logic_comp["Cond"].input_signal(ZF=self.ZF,OF=self.OF,SF=self.SF,ifun=self.ifun)
            self.Cnd = self.logic_comp["Cond"].output_signal()["Cnd"]

            print "阶段3："
            self.display()
            self.pause()

            # 第四阶段 访存
            self.logic_comp["memRead"].input_signal(icode=self.icode)
            self.mem_read = self.logic_comp["memRead"].output_signal()["mem_read"]
            self.logic_comp["memWrite"].input_signal(icode=self.icode)
            self.mem_write = self.logic_comp["memWrite"].output_signal()["mem_write"]
            self.logic_comp["memAddr"].input_signal(icode=self.icode,valE=self.valE,valA=self.valA)
            self.mem_addr = self.logic_comp["memAddr"].output_signal()["mem_addr"]
            self.logic_comp["memData"].input_signal(icode=self.icode,valA = self.valA,valP=self.valP)
            self.mem_data = self.logic_comp["memData"].output_signal()["mem_data"]
            self.timer_comp["dataMemory"].input_signal(read_flag=self.mem_read,write_flag=self.mem_write,
                                                       mem_addr = self.mem_addr,mem_data=self.mem_data)
            self.timer_comp["dataMemory"].switch_state()
            self.valM = self.timer_comp["dataMemory"].output_signal()["valM"]
            self.dmem_error = self.timer_comp["dataMemory"].output_signal()["dmem_error"]
            self.logic_comp["Stat"].input_signal(imem_error=self.imem_error,dmem_error=self.dmem_error,icode=self.icode,instr_valid=self.instr_valid)
            self.Stat = self.logic_comp["Stat"].output_signal()["Stat"]

            print "阶段4："
            self.display()
            self.display_mem()
            self.pause()

            # 第五阶段 写回
            # 时钟切换到下降沿
            # 二阶段的代码原封不动抄过来
            self.logic_comp["dstE"].input_signal(Cnd=self.Cnd, icode=self.icode, rB=self.rB)
            self.dstE = self.logic_comp["dstE"].output_signal()["dstE"]
            self.logic_comp["dstM"].input_signal(icode=self.icode, rA=self.rA)
            self.dstM = self.logic_comp["dstM"].output_signal()["dstM"]
            self.logic_comp["srcA"].input_signal(icode=self.icode, rA=self.rA)
            self.srcA = self.logic_comp["srcA"].output_signal()["srcA"]
            self.logic_comp["srcB"].input_signal(icode=self.icode, rB=self.rB)
            self.srcB = self.logic_comp["srcB"].output_signal()["srcB"]
            self.timer_comp["registerFile"].input_signal(dstE=self.dstE, dstM=self.dstM, srcA=self.srcA, srcB=self.srcB,
                                                         valM=self.valM, valE=self.valE)
            self.timer_comp["registerFile"].switch_state()
            self.valA = self.timer_comp["registerFile"].output_signal()["valA"]
            self.valB = self.timer_comp["registerFile"].output_signal()["valB"]

            # 时钟切换到下降沿，但是下面这三个在下降沿时都没有需要执行的逻辑
            self.timer_comp["dataMemory"].switch_state()
            self.timer_comp["programMemory"].switch_state()
            self.timer_comp["statusRegister"].switch_state()

            print "阶段5："
            self.display()
            self.display_reg()
            self.pause()

            # 第六阶段 更新PC
            self.logic_comp["newPC"].input_signal(icode=self.icode,Cnd=self.Cnd,valC=self.valC,valM=self.valM,valP=self.valP)
            self.new_pc = self.logic_comp["newPC"].output_signal()["new_pc"]
            # 将新的PC写入寄存器
            self.timer_comp["programCounter"].input_signal(PC=self.new_pc)
            self.timer_comp["programCounter"].switch_state()

            print "阶段6："
            self.display()
            self.pause()

    def load_data(self,start_address,program_str):
        self.timer_comp["programCounter"].init_PC(start_address)
        self.timer_comp["programMemory"].load_program_data(start_address,program_str)