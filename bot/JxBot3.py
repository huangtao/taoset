# -*- coding: utf-8 -*-
import os
import sys
import webbrowser
import time
import threading
import tkinter as tk
#
import pyautogui
import numpy as np
import cv2
import PIL
#
import win32api
import win32con
import win32gui
import win32print
import win32ui
import win10toast

# 功能
# 使用机器识别电力值，达到300的时候进行鼠标点击
#
# https://github.com/YECHEZ/wow-fish-bot
# 原理步骤(参考https://www.cnblogs.com/lizm166/p/9969647.html)
# 1.截取客户端截图，并将电力数字区域单独保存
# 2.图片处理 - 对图片进行二值化处理(单色黑白)
# 3.切割图片 - 将图片切割成单个数字并保存
# 4.人工标注 - 对切割的数字进行人工标注作为训练集
# 5.训练数据 - 用KNN算法训练数据
# 6.检测结果 - 用上一步的训练结果识别新的数字

# 调试模式会输出中间处理的图片
debug = True

# 是否自动加电力
is_auto_add = 0

# 临时目录
tempDir = "d:/temp/"

# 识别模式
# 0 - 判断黄色进度条是否达到100%
# 1 - 识别数字是否是300
mode = 0

# 成功识别次数
succNum = 0

is_run = 0


def get_screen_size():
    """获取缩放后的分辨率"""
    w = win32api.GetSystemMetrics(0)
    h = win32api.GetSystemMetrics(1)
    return w, h


screen_size = get_screen_size()
print(screen_size)

# 获取当前屏幕分辨率
screenWidth, screenHeight = pyautogui.size()

# 屏幕分辨率缩放
screen_scale_rate = round(screenWidth / screen_size[0], 2)

toaster = win10toast.ToastNotifier()

# GUI
window = tk.Tk(className="京喜工厂助手")
# 居中显示
sw = window.winfo_screenwidth()
sh = window.winfo_screenheight()
ww = 320
wh = 240
window.geometry("%dx%d+%d+%d" % (ww, wh, (sw-ww) / 2, (sh-wh) / 2))
# 不能调整尺寸
window.resizable(0, 0)

# 运行模式
varRadio = tk.StringVar()
radio1 = tk.Radiobutton(window, text="自动收取", value=1, variable=varRadio)
radio1.place(x=0, y=0, anchor=tk.NW)
radio2 = tk.Radiobutton(window, text="提醒模式", value=2, variable=varRadio)
radio2.place(x=120, y=0, anchor=tk.NW)
varRadio.set("2")


def onCheckDebug():
    debug = int(varDebug.get())
    print(debug)


varDebug = tk.IntVar()
cbDebug = tk.Checkbutton(
    window, text="调试模式", variable=varDebug, command=onCheckDebug)
cbDebug.place(x=0, y=70, anchor=tk.NW)
varDebug.set(0)


varBtnTile = tk.Variable()


def onButton():
    global is_run
    threadLock.acquire()
    if is_run > 0:
        is_run = 0
        varBtnTile.set("开始")
    else:
        is_run = 1
        varBtnTile.set("停止")
    threadLock.release()


btnStart = tk.Button(window, textvariable=varBtnTile,
                     width=10, height=2, font=("黑体", 20), command=onButton)
btnStart.place(x=160, y=140, anchor=tk.CENTER)
varBtnTile.set("开始")

# 识别次数
varNumInfo = tk.Variable()
label2 = tk.Label(window, textvariable=varNumInfo, fg="green")
label2.place(x=120, y=75, anchor=tk.NW)
varNumInfo.set("成功收取0次!")

# 识别次数
varDebugInfo = tk.Variable()
label3 = tk.Label(window, textvariable=varDebugInfo)
label3.place(x=0, y=210, anchor=tk.NW)
varDebugInfo.set("#涛我喜欢#")

# # 鼠标移动到屏幕中央
# pyautogui.moveTo(screenWidth / 2, screenHeight / 2)


# 自动模式运行函数
def runAutoMode(hwnd, double):
    global mode, is_auto_add, debug, succNum
    try:
        # 已经运行
        # 解决'No error message is available'

        win32api.keybd_event(13, 0, 0, 0)
        win32gui.SetForegroundWindow(hwnd)
        (left, top, right, bottom) = win32gui.GetWindowRect(hwnd)

        # 对窗口截图
        img = PIL.ImageGrab.grab(bbox=(left, top, right, bottom))
        if debug:
            img.save(os.path.join(tempDir, "JxBotSC.png"))
        img_np = np.array(img)

        if (right-left) < 132 or (bottom - top) < 599:
            raise Exception("没有得到正确的截图")

        varDebugInfo.set("开始分析...")

        # opencv处理
        is_full = False
        if mode == 0:
            # 进度条区域77,579 大小54,18
            roi = img_np[580:598, 77:131]
            img_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
            if debug:
                cv2.imwrite(os.path.join(
                    tempDir, "JxBotRoi.png"), img_roi)
            # 取62,11的像素RBG如果等于(255,177,0) 则已100%
            check_x = 9
            check_y = 52
            if double == 0:
                # 不翻倍
                check_y = 50
            g, b, r = img_roi[check_x, check_y]
            # print(r,g,b)
            varDebugInfo.set("r=" + str(r) + ",g=" + str(g) + ",b=" + str(b))
            if (r ==
                    255 and b == 177 and g == 0):
                varDebugInfo.set("电力已满,准备收取!")
                # 鼠标点击进度条按钮中间
                pyautogui.moveTo(left + 105, top + 589)
                pyautogui.leftClick()
                succNum = succNum + 1
                varNumInfo.set("成功收取" + str(succNum) + "次!")
                is_full = True
        else:
            # 电力数字区域位于92,622 大小56,18
            # img[0:rows, 0:cols]
            roi = img_np[622:640, 92:148]

            # 将图片转化为灰色图片
            img_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            if debug:
                cv2.imwrite(os.path.join(
                    tempDir, "JxBotRoi_gray.png"), img_gray)
            # 降噪处理
            # 二值化处理
            ret, img_inv = cv2.threshold(
                img_gray, 127, 255, cv2.THRESH_BINARY_INV)
            if debug:
                cv2.imwrite(os.path.join(
                    tempDir, "JxBotRoi_inv.png"), img_inv)
            # 得到轮廓
            im2, contours, hierarchy = cv2.findContours(
                img_inv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            result = []
            # if (contours)
            # for contour in contours:

        if is_full:
            time.sleep(2)
            # 已点击，可能出现翻倍和观看广告，继续截屏判定
            win32api.keybd_event(13, 0, 0, 0)
            win32gui.SetForegroundWindow(hwnd)
            (left, top, right, bottom) = win32gui.GetWindowRect(hwnd)
            imgPop = PIL.ImageGrab.grab(
                bbox=(left, top, right, bottom))
            if debug:
                imgPop.save(os.path.join(tempDir, "JxBotSC_pop.png"))
            imgPop_np = np.array(imgPop)
            if (right-left) < 208 or (bottom-top) < 613:
                raise Exception("没有得到正确的截图")

            # 检查2个点符合分享图片取点
            # 弹出对话框大小一致，但是内部黄色按钮的位置是不固定的
            # 我们检测蓝色的关闭按钮，如果有按钮特征则视为有弹窗
            px1_r, px1_g, px1_b = imgPop_np[607, 207]
            px2_r, px2_g, px2_b = imgPop_np[613, 207]
            if (px1_r == 226 and px1_g == 242 and px1_b == 255 and
                    px2_r == 0 and px2_g == 123 and px2_b == 223):
                # 检测到弹出对话框，点击关闭它
                # 知道了、分享加倍、
                pyautogui.moveTo(left + 208, top + 500)
                pyautogui.leftClick()
                time.sleep(10)

            # 自动加下电力
            if is_auto_add:
                time.sleep(2)
                pyautogui.moveTo(left + 240, top + 750)
                pyautogui.leftClick()

        # 10s后继续检测
        varDebugInfo.set("10秒后将再次检查!")
        time.sleep(10)
    except Exception as e:
        varDebugInfo.set(e.args)
        print(e)


# 后台提醒模式
def runTipMode(hwnd):
    global debug, mode
    try:
        (left, top, right, bottom) = win32gui.GetWindowRect(hwnd)
        w = right - left
        h = bottom - top
        # 得到窗口设备环境(包括客户区和非客户区-标题栏、边框)
        hwndDC = win32gui.GetWindowDC(hwnd)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        # 创建内存设备描述表
        saveDC = mfcDC.CreateCompatibleDC()
        # 创建位图对象
        saveBitmap = win32ui.CreateBitmap()
        saveBitmap.CreateCompatibleBitmap(mfcDC, w, h)
        saveDC.SelectObject(saveBitmap)
        # 截图至内存设备描述表
        saveDC.BitBlt((0, 0), (w, h), mfcDC, (0, 0), win32con.SRCCOPY)
        # PIL
        bmpinfo = saveBitmap.GetInfo()
        bmpstr = saveBitmap.GetBitmapBits(True)
        img = PIL.Image.frombuffer(
            'RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
        if debug:
            img.save(os.path.join(tempDir, "JxBotSC.png"))
        img_np = np.array(img)

        if (right-left) < 132 or (bottom - top) < 599:
            raise Exception("没有得到正确的截图")

        varDebugInfo.set("开始分析...")

        # opencv处理
        is_full = False
        if mode == 0:
            # 进度条区域77,580 大小54,18
            roi = img_np[580:598, 77:131]
            img_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
            if debug:
                cv2.imwrite(os.path.join(
                    tempDir, "JxBotRoi.png"), img_roi)
            # 取62,11的像素RBG如果等于(255,177,0) 则已100%
            g, b, r = img_roi[8, 52]
            varDebugInfo.set("r=" + str(r) + ",g=" + str(g) + ",b=" + str(b))
            if (r ==
                    255 and b == 177 and g == 0):
                is_full = True
        else:
            # 电力数字区域位于92,622 大小56,18
            # img[0:rows, 0:cols]
            roi = img_np[622:640, 92:148]

            # 将图片转化为灰色图片
            img_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            if debug:
                cv2.imwrite(os.path.join(
                    tempDir, "JxBotRoi_gray.png"), img_gray)
            # 降噪处理
            # 二值化处理
            ret, img_inv = cv2.threshold(
                img_gray, 127, 255, cv2.THRESH_BINARY_INV)
            if debug:
                cv2.imwrite(os.path.join(
                    tempDir, "JxBotRoi_inv.png"), img_inv)
            # 得到轮廓
            im2, contours, hierarchy = cv2.findContours(
                img_inv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            result = []
            # if (contours)
            # for contour in contours:

        if is_full:
            toaster.show_toast("京喜工厂助手提醒您收电力啦！", duration=5)

    except Exception as e:
        varDebugInfo.set(e.args)
        print(e)
    finally:
        # 释放资源
        win32gui.DeleteObject(saveBitmap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)

        # 30s后继续检测
        varDebugInfo.set("30秒后将再次检查!")
        time.sleep(30)


# 线程函数
def myThread():
    global is_run
    while 1:
        if is_run > 0:
            hwnd = win32gui.FindWindow("Chrome_WidgetWin_0", "京喜")
            if hwnd == 0:
                varDebugInfo.set("京喜工厂没有运行!")
                time.sleep(2)
            else:
                rm = int(varRadio.get())
                if rm == 1:
                    runAutoMode(hwnd, 0)
                else:
                    runTipMode(hwnd)
        else:
            time.sleep(1)
        varDebugInfo.set("完成一次运行!")
        time.sleep(1)


threadLock = threading.Lock()
th = threading.Thread(target=myThread)
th.setDaemon(True)
th.start()

# 进入消息循环体
window.mainloop()
