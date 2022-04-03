# encoding:utf-8
"""
指令编码
"""

byte2command = {
    '0':"IHALT",
    '1':"INOP",
    '2':"IRRMOVQ",
    '3':"IIRMOVQ",
    '4':"IRMMOVQ",
    '5':"IMRMOVQ",
    "6":'IOPQ',
    '7':'IJXX',
    '8':'ICALL',
    '9':'IRET',
    'A':'IPUSHQ',
    'B':'IPOPQ'
}