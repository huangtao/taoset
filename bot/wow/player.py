import time
import os
import numpy as np
import cv2
import mss
from PIL import Image

# 血满时血条面积
maxHealth = 781.5
# 蓝满时蓝条面积
maxMana = 795.5


def getCurrentBar(img):
    global debug, maxHealth, maxMana

    # 得到血条和蓝条区域图片
    img_bar = img[30:52, 65:186]
    #cv2.imshow("bar", img_bar)

    hsv = cv2.cvtColor(img_bar, cv2.COLOR_BGR2HSV)

    mana = ""
    health = ""

    lower_blue = np.array([100, 200, 80])
    upper_blue = np.array([120, 255, 255])

    lower_green = np.array([60, 80, 80])
    upper_green = np.array([90, 255, 255])

    blueMask = cv2.inRange(hsv, lower_blue, upper_blue)
    greenMask = cv2.inRange(hsv, lower_green, upper_green)

    # manaBar = cv2.bitwise_and(img, img, mask=blueMask)
    # healthBar = cv2.bitwise_and(img, img, mask=greenMask)

    # 得到魔法值轮廓
    blueContours, _ = cv2.findContours(
        blueMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    for contour in blueContours:
        manaArea = cv2.contourArea(contour)
        if manaArea > maxMana:
            maxMana = manaArea
        mana = str(int((manaArea / maxMana) * 100))

    greenContours, _ = cv2.findContours(
        greenMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    for contour in greenContours:
        healthArea = cv2.contourArea(contour)
        if healthArea > maxHealth:
            maxHealth = healthArea
        health = str(int((healthArea / maxHealth) * 100))

    return health, mana

# 检查是否有战斗标记(交叉的剑)
def isFighting(img):
    img_check = img[45:64, 4:22]
    #cv2.imshow("bar", img_check)

    hsv = cv2.cvtColor(img_check, cv2.COLOR_BGR2HSV)

    lower_white = np.array([0, 0, 221])
    upper_white = np.array([180, 30, 255])

    whiteMask = cv2.inRange(hsv, lower_white, upper_white)

    # 得到魔法值轮廓
    whiteContours, _ = cv2.findContours(
        whiteMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    if (whiteContours):
        return True
    else:
        return False
