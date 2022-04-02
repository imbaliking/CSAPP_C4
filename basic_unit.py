# encoding:utf-8

"""
基础逻辑模块，定义硬件运行的一些操作
"""

class logicUnit(object):
    """
    组合逻辑电路的基础定义
    需要实现的接口：输入，输出
    """

    def __init__(self):
        self.input_list = {}
        self.output_list = {}

    def input_signal(self,**kwargs):
        """
        传入信号的通用接口
        :param kwargs: 传入类型为字典型，key=value key为信号名，value为信号值
        :return:
        """
        for key in kwargs:
            self.input_list[key] = kwargs[key]

    def output_signal(self):
        """
        输出信号的通用接口
        :return: 字典型，包含应该输出的所有数值
        """
        return self.output_list

    def exc_logic(self):
        """
        组合逻辑的执行函数，必须覆盖
        :return:
        """
        pass


class timerUnit(logicUnit):
    """
    时序硬件单元的基本定义
    包括四种：程序计数器，条件码寄存器，数据内存，寄存器文件
    """

    def __init__(self):
        super(timerUnit,self).__init__()
        # 电平状态，False为低电平，True为高电平
        self.state = False

    def low2high(self):
        """
        低电平转到高电平时触发的功能，需要硬件自行实现
        :return:
        """
        pass

    def high2low(self):
        """
        高电平转到低电平时触发的功能，需要硬件自行实现
        :return:
        """
        pass

    def switch_state(self):
        """
        状态转换时触发的功能
        :return:
        """
        if self.state:
            self.high2low()
        else:
            self.low2high()
        self.state = not self.state
