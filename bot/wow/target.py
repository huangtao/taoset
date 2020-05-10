import time
import os
import numpy as np
import cv2
import mss

# 血满时血条面积
maxHealth = 781.5
# 蓝满时蓝条面积
maxMana = 795.5

# 判定目标属性


def getTargetStats(img):
    target = ""

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower_yellow = np.array([20, 200, 200])
    upper_yellow = np.array([50, 255, 255])

    lower_red = np.array([0, 200, 200])
    upper_red = np.array([20, 255, 255])

    # 敌对
    redMask = cv2.inRange(hsv, lower_red, upper_red)
    # enemyTarget = cv2.bitwise_and(img, img, mask=redMask)

    # 中立怪
    yellowMask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    # neutralTarget = cv2.bitwise_and(img, img, mask=yellowMask)

    # 得到轮廓
    yellowContours, _ = cv2.findContours(
        yellowMask, cv2.RETR_THEE, cv2.CHAIN_APPROX_NONE)
    for contour in yellowContours:
        yellowArea = cv2.contourArea(contour)
        if (yellowArea > 20):
            # 目标中立
            print("Looking at neutral unit")
            target = "neutral"

    redContours, _ = cv2.findContours(
        redMask, cv2.RETR_THEE, cv2.CHAIN_APPROX_NONE)
    for contour in redContours:
        redArea = cv2.contourArea(contour)
        if (redArea > 20):
            # 目标敌对
            print("Looking at enemy unit")
            target = "enemy"

    return target


def getTargetCoor(img):
    coord = 0
    canSeeTarget = False

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower_red = np.array([0, 200, 200])
    upper_red = np.array([20, 255, 255])

    # 敌对
    redMask = cv2.inRange(hsv, lower_red, upper_red)
    enemyTarget = cv2.bitwise_and(img, img, mask=redMask)

    redContours, _ = cv2.findContours(
        redMask, cv2.RETR_THEE, cv2.CHAIN_APPROX_NONE)
    for contour in redContours:
        redArea = cv2.contourArea(contour)
        if (redArea > 1):
            canSeeTarget = True
            indices = np.where(enemyTarget != [0])
            coordinates = list(zip(indices[0], indices[1]))
            coord = coordinates[0][1]

    return coord, canSeeTarget


def getTargetBar(img):
    global debug, maxHealth, maxMana

    # 得到血条和蓝条区域图片
    img_bar = img[30:52, 1:121]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    mana = ""
    health = ""

    lower_blue = np.array([100, 200, 80])
    upper_blue = np.array([120, 255, 255])

    lower_green = np.array([60, 80, 80])
    upper_green = np.array([90, 255, 255])

    blueMask = cv2.inRange(hsv, lower_blue, upper_blue)
    greenMask = cv2.inRange(hsv, lower_green, upper_green)

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
