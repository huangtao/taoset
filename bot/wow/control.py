import pyautogui
import time
import cv2
import win32gui
import random
import mss
from config import *


def centerScreen(coord, positioner):
    (left, top, right, bottom) = win32gui.GetWindowRect(hwnd)
    width = right - left

    if (coord > 0):
        # 目标是否在中间位置
        if (abs(width/2-coord) < 150):
            pyautogui.keyUp('d')
            pyautogui.keyUp('a')
            return True

        # 目标是否在右边
        elif (coord > width / 2):
            pyautogui.keyDown('d')
            time.sleep(0.05)
            pyautogui.keyUp('d')
            positioner.updateDirection(positioner.direction + 15)
            return False

        # 目标是否在左边
        elif (coord < width / 2):
            pyautogui.keyDown('a')
            time.sleep(0.05)
            pyautogui.keyUp('a')
            positioner.updateDirection(positioner.direction - 15)
            return False


def releaseControls():
    pyautogui.keyUp('d')
    pyautogui.keyUp('a')


def moveAboutMap(positioner):
    pyautogui.keyDown('w')


def stopMovement(positioner):
    pyautogui.keyUp('w')


def moveSideWays(positioner):
    choice = random.randint(0, 1)

    if (choice == 1):
        pyautogui.keyDown('a')
        time.sleep(0.15)
        pyautogui.keyUp('a')
        positioner.updateDirection(-45)
    else:
        pyautogui.keyDown('d')
        time.sleep(0.15)
        pyautogui.keyUp('d')
        positioner.updateDirection(45)

# 是否在攻击范围内


def castRangeCheck(img):
    pyautogui.press('1')

    # 提示不在攻击范围红色文字
    inRangeTextImg = img[830:880, 800:1100]
    hsv = cv2.cvtColor(inRangeTextImg cv2.COLOR_BGR2HSV)

    lower_yellow = np.array([20, 200, 200])
    upper_yellow = np.array([50, 255, 255])

    lower_red = np.array([0, 200, 200])
    upper_red = np.array([20, 255, 255])

    yellowMask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    redMask = cv2.inRange(hsv, lower_red, upper_red)

    # 得到轮廓
    yellowContours, _ = cv2.findContours(
        yellowMask, cv2.RETR_THEE, cv2.CHAIN_APPROX_NONE)
    redContours, _ = cv2.findContours(
        redMask, cv2.RETR_THEE, cv2.CHAIN_APPROX_NONE)

    CV2.imshow("castRange", inRangeTextImg)

    if (yellowContours or redContours):
        return True
    else:
        return False
