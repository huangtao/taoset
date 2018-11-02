#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os,sys

def main():
    if len(sys.argv) <= 1:
        print("You must pass position to convert!")
        exit(1)
    x = float(sys.argv[1])
    y = float(sys.argv[2])
    # 我们的设计分辨率是1334*750
    # x,y为cocosstudio的坐标系统
    # 将它转为cocos creator的坐标系统
    cx = 1334.0 / 2.0
    cy = 750.0 / 2.0
    if x > cx:
        tx = x - cx
    else:
        tx = -(cx - x)
    if y > cy:
        ty = y - cy
    else:
        ty = -(cy - y)
    print(tx,ty)

# 脚本既可以执行也能导入到其他模块中使用
if __name__ == "__main__":        
    main()
