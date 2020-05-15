# -*- coding: utf-8 -*-
#
# 魔兽世界机器人(后台运行即可)
# 原地打怪、不拾取
#

import os
import sys
import time
import datetime
#
import pyautogui
import numpy as np
import cv2
import PIL
import mss
import mss.tools
#
import msvcrt
import win32api
import win32con
import win32gui
import win32print
import win32ui
import win10toast
#
from config import *
from player import *
from target import *
from position import *
from config import *
from control import *


def main():

    rangeChecked = False
    targetCoord = 0
    initialMove = False
    hwnd = 0
    gameState = 'findTarget'

    positioner = Positioner()

    loop_count = 0
    water_num = 0
    count_notview = 0
    is_fighting = False
    midY = 0
    time_try_attack = datetime.datetime.now()
    is_moving = False
    time_moving = 0
    tab_num = 1
    time_add_buffer = time_try_attack
    oldMana = 0
    target_x = 0
    target_y = 0

    # 主循环
    while 1:
        if msvcrt.kbhit():
            key = msvcrt.getch().decode()
            if key == 'q':
                exit(0)

        hwnd = win32gui.FindWindow("GxWindowClass", "魔兽世界")
        if hwnd == 0:
            time.sleep(1)
            continue

        win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, 49, 0)
        time.sleep(0.2)
        win32api.PostMessage(hwnd, win32con.WM_KEYUP, 49, 0)


        time.sleep(1)


main()
