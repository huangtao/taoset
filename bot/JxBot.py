# -*- coding: utf-8 -*-
import os
import sys
import webbrowser
import time
#
import pyautogui
import numpy as np
import cv2
#
import win32api
import win32con
import win32gui
import win10toast
import infi.systray
import PIL

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

# 获取当前屏幕分辨率
screenWidth, screenHeight = pyautogui.size()

# 鼠标移动到屏幕中央
pyautogui.moveTo(screenWidth / 2, screenHeight / 2)

# 调试模式会输出中间处理的图片
debug = True

# 临时目录
tempDir = "d:/temp/"

# 识别模式
# 0 - 判断黄色进度条是否达到100%
# 1 - 识别数字是否是300
mode = 0


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def app_pause(systray):
    global is_stop
    is_stop = False if is_stop is True else True
    if is_stop is True:
        systray.update(hover_text=app + " - 暂停")
    else:
        systray.update(hover_text=app)


def app_destroy(systray):
    sys.exit()


def app_about(systray):
    webbrowser.open('http://www.jd.com')


def main():
    is_stop = False
    flag_exit = False
    wait_mes = 0
    app = "京喜工厂助手"
    app_ico = resource_path('game.ico')
    link = "访问京东"
    menu_options = (("开始/停止", None, app_pause),
                    (link, None, app_about),)
    systray = infi.systray.SysTrayIcon(
        app_ico, app, menu_options, on_quit=app_destroy)
    systray.start()

    toaster = win10toast.ToastNotifier()
    toaster.show_toast(app, link, icon_path=app_ico, duration=5)

    while flag_exit is False:
        if is_stop == False:
            hwnd = win32gui.FindWindow("Chrome_WidgetWin_0", "京喜")
            if hwnd == 0:
                if wait_mes == 5:
                    wait_mes = 0
                    toaster.show_toast(app,
                                       "等待京喜工厂运行", icon_path='game.ico',
                                       duration=5)
                # print("Waiting for target app window")
                systray.update(hover_text=app + " - 等待京喜工厂运行")
                wait_mes += 1
                time.sleep(2)
            else:
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

                # opencv处理
                is_full = False
                if mode == 0:
                    # 进度条区域90,620 大小63,22
                    roi = img_np[619:640, 89:152]
                    img_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
                    if debug:
                        cv2.imwrite(os.path.join(
                            tempDir, "JxBotRoi.png"), img_roi)
                    # 取62,11的像素RBG如果等于(255,177,0) 则已100%
                    g, b, r = img_roi[11, 61]
                    if (r ==
                            255 and b == 177 and g == 0):
                        # 鼠标点击进度条按钮中间
                        pyautogui.moveTo(left + 120, top + 631)
                        pyautogui.leftClick()
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
                    imgPop = PIL.ImageGrab.grab(
                        bbox=(left, top, right, bottom))
                    if debug:
                        imgPop.save(os.path.join(tempDir, "JxBotSC_pop.png"))
                    imgPop_np = np.array(imgPop)
                    # 检查2个点符合分享图片取点
                    # 弹出对话框大小一致，但是内部黄色按钮的位置是不固定的
                    # 我们检测蓝色的关闭按钮，如果有按钮特征则视为有弹窗
                    # 109,196,252
                    px1_r, px1_g, px1_b = imgPop_np[660, 240]
                    # 226,242,255
                    px2_r, px2_g, px2_b = imgPop_np[672, 240]
                    if (px1_r == 109 and px1_g == 196 and px1_b == 252 and
                            px2_r == 226 and px2_g == 242 and px2_b == 255):
                        # 检测到弹出对话框，点击关闭它
                        # 知道了、分享加倍、
                        pyautogui.moveTo(left + 240, top + 560)
                        pyautogui.leftClick()
                        time.sleep(10)
                        
                    # 自动加下电力
                    # time.sleep(2)
                    # pyautogui.moveTo(left + 240, top + 750)
                    # pyautogui.leftClick()

                # 一分钟后继续检测
                time.sleep(60)
        else:
            # print("Pause")
            systray.update(hover_text=app + " - 暂停")
            time.sleep(2)


if __name__ == '__main__':
    main()
