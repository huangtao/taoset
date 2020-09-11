# -*- coding: utf-8 -*-
__author__ = 'huangtao'
'''
大宗交易
搜索大单进入的个股
'''

import os
import numpy as np
import tushare as ts
#
from utils import Util


class MonitorStock():
    def __init__(self):
        self.mystock = Util.read_stock('mystock.csv')
        self.base = 

def main():
    currPath = os.getcwd()
    dataPath = os.path.join(currPath, 'data')
    if (os.path.exists(dataPath) == False):
        os.mkdir(dataPath)
    os.chdir(dataPath)

    obj = MonitorStock()
    obj.loops()

main()