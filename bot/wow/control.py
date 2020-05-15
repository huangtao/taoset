import pyautogui
import time
import cv2
import win32gui
import random
import numpy as np
import config


def centerScreen(coord, positioner, fighting):
    if (config.hwnd == 0):
        return True
    if (fighting):
        return True
    (left, top, right, bottom) = win32gui.GetWindowRect(config.hwnd)
    width = right - left

    if (coord > 0):
        # 目标是否在中间位置
        if (abs(width/2-coord) < 150):
            return True

        # 目标是否在右边
        elif (coord > width / 2):
            pyautogui.keyDown('right')
            time.sleep(0.05)
            pyautogui.keyUp('right')
            positioner.updateDirection(positioner.direction + 15)
            return False

        # 目标是否在左边
        elif (coord < width / 2):
            pyautogui.keyDown('left')
            time.sleep(0.05)
            pyautogui.keyUp('left')
            positioner.updateDirection(positioner.direction - 15)
            return False


def releaseControls():
    pyautogui.keyUp('right')
    pyautogui.keyUp('left')


def startMovement(positioner):
    pyautogui.keyDown('w')


def stopMovement(positioner):
    pyautogui.keyUp('w')


def moveSideWays(positioner):
    choice = random.randint(0, 1)
    choice = 0

    if (choice == 1):
        pyautogui.keyDown('left')
        time.sleep(0.15)
        pyautogui.keyUp('left')
        positioner.updateDirection(-45)
    else:
        pyautogui.keyDown('right')
        time.sleep(0.15)
        pyautogui.keyUp('right')
        positioner.updateDirection(45)

    choice = random.randint(0, 100)
    if (choice < 10):
        pyautogui.press('space')


# 是否在攻击范围内
# 我们检查动作条数字是否是红色来判定


def castRangeCheck(img):
    pyautogui.press('1')

    # 动作条文字1是否红色
    inRangeTextImg = img[631:638, 36:38]
    hsv = cv2.cvtColor(inRangeTextImg, cv2.COLOR_BGR2HSV)

    # lower_yellow = np.array([20, 200, 200])
    # upper_yellow = np.array([50, 255, 255])

    lower_red = np.array([0, 200, 200])
    upper_red = np.array([20, 255, 255])

    # yellowMask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    redMask = cv2.inRange(hsv, lower_red, upper_red)
    if (config.debug):
        cv2.imwrite("can_attack.png", inRangeTextImg)
        cv2.imwrite("can_attack_mask.png", redMask)

    # 得到轮廓
    # yellowContours, _ = cv2.findContours(
    #     yellowMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    redContours, _ = cv2.findContours(
        redMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    if (redContours):
        return False
    else:
        return True


# 我们检查动作条数字是否是红色来获取可以释放的技能
def getCastSpell(img):
    spell = 6
    listoffset = [0, 40, 43, 43, 43, 43]
    listwidth = [2, 5, 5, 6, 5, 6]
    x = 0
    for i in range(6):
        # 动作条文字1是否红色
        x += listoffset[i]
        inRangeTextImg = img[631:638, 36 + x:36 + x + listwidth[i]]
        hsv = cv2.cvtColor(inRangeTextImg, cv2.COLOR_BGR2HSV)

        lower_red = np.array([0, 200, 200])
        upper_red = np.array([20, 255, 255])

        redMask = cv2.inRange(hsv, lower_red, upper_red)
        # if (config.debug):
        #     cv2.imwrite("spell" + str(i) + ".png", inRangeTextImg)
        #     cv2.imwrite("spell" + str(i) + "_mask.png", redMask)

        # 得到轮廓
        redContours, _ = cv2.findContours(
            redMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        if redContours:
            spell = 6
        else:
            spell = i + 1
            break

    return spell


def checkMapMovement(img1, img2):
    originalMiniMapImg = img1[25:158, 17:150]
    newMiniMapImg = img2[25:158, 17:150]

    difference = newMiniMapImg - originalMiniMapImg
    distance = (difference.astype(float)**2).sum(axis=2)

    if (distance.sum() > 100000000):
        #val = (abs(100000000 - distance.sum())) / 10
        return True
    else:
        return False

# 发现拾取


def findPickup(img):
    nopickup = True
    return nopickup
