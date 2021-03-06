import os
import pyautogui
import configparser
import win32gui

# 是否调试
debug = True

# 是否单步调试
debug_step = True

# 魔兽窗口句柄
hwnd = 0

# 是否拾取(极大影响升级效率)
doPickup = False

# 是否后台运行(只在原地刷怪升级)
backrun = False

# 是否自动吃喝
doWater = True

# 获取当前屏幕分辨率
screenWidth, screenHeight = pyautogui.size()

# 截图调整参数
# 截图额外调整参数(根据hwnd截图有额外的部分并非精确的窗口区域)
# 到新的机器需要检查调整=
sc_offset_left = 7
sc_offset_top = 0
sc_offset_right = 7
sc_offset_bottom = 7
titleHeight = 30
frameSize = 1

# 是否杀中立怪
kill_neutral = True

def setHwnd(h):
    global hwnd
    hwnd = h


def getZhiye():
    return zhiye

def setWinPos(left, top):
    global win_x,win_y

    win_x = left
    win_y = top

def saveConfig():
    conf.set("config", "win_x", str(win_x))
    conf.set("config", "win_y", str(win_y))
    conf.write(open(config_path), 'w')
