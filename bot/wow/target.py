import time
import os
import numpy as np
import cv2
import mss
from config import *

'''
hsv黄色范围[26,43,46]~[34,255,255]
'''

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
        yellowMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    for contour in yellowContours:
        yellowArea = cv2.contourArea(contour)
        if (yellowArea > 20):
            # 目标中立
            # print("Looking at neutral unit")
            target = "neutral"

    redContours, _ = cv2.findContours(
        redMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    for contour in redContours:
        redArea = cv2.contourArea(contour)
        if (redArea > 20):
            # 目标敌对
            # print("Looking at enemy unit")
            target = "enemy"

    return target


def getTargetCoor(img):
    # 动作条，人物后面不用检测
    img_check = img[0:380, 0:990]

    mid_x = 0
    mid_y = 0
    coord = 0
    canSeeTarget = False

    hsv = cv2.cvtColor(img_check, cv2.COLOR_BGR2HSV)

    lower_red = np.array([0, 200, 200])
    upper_red = np.array([20, 255, 255])

    # 敌对
    redMask = cv2.inRange(hsv, lower_red, upper_red)
    enemyTarget = cv2.bitwise_and(img_check, img_check, mask=redMask)
    # if debug:
    #     cv2.imwrite("target_red_mask.png", redMask)

    bFind = False
    redContours, _ = cv2.findContours(
        redMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    for contour in redContours:
        redArea = cv2.contourArea(contour)
        redRect = cv2.boundingRect(contour)
        # print(redArea,redRect)
        # 有时候目标脚下是一条线，面积为1.0
        # 目标脚下的圈圈外接矩形长度比较长可以区别名字产生的面积
        if (redArea > 0 and redRect[2] > 10):
            canSeeTarget = True
            indices = np.where(enemyTarget != [0])
            coordinates = list(zip(indices[0], indices[1]))
            coord = coordinates[0][1]
            M = cv2.moments(contour)
            mid_x = int(M["m10"] / M["m00"])
            mid_y = int(M["m01"] / M["m00"])
            bFind = True

    if (not bFind and kill_neutral):
        lower_yellow = np.array([26, 150, 150])
        upper_yellow = np.array([34, 255, 255])
        yellowMask = cv2.inRange(hsv, lower_yellow, upper_yellow)
        neutralTarget = cv2.bitwise_and(img_check, img_check, mask=yellowMask)
        # if debug:
        #     cv2.imwrite("target_yellow_mask.png", yellowMask)
        #     cv2.imwrite("target_yellow.png", neutralTarget)
        yellowContours, _ = cv2.findContours(
            yellowMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        for contour in yellowContours:
            yellowArea = cv2.contourArea(contour)
            yellowRect = cv2.boundingRect(contour)
            # print(yellowArea,yellowRect)a
            if (yellowArea > 0 and yellowRect[2] > 10):
                bFind = True
                canSeeTarget = True
                indices = np.where(neutralTarget != [0])
                zipped = zip(indices[0], indices[1])
                coordinates = list(zipped)
                coord = coordinates[0][1]
                M = cv2.moments(contour)
                mid_x = int(M["m10"] / M["m00"])
                mid_y = int(M["m01"] / M["m00"])

    return coord, canSeeTarget, mid_y


def getTargetBar(img):
    global debug, maxHealth, maxMana

    # 得到血条和蓝条区域图片
    img_bar = img[30:52, 1:121]
    hsv = cv2.cvtColor(img_bar, cv2.COLOR_BGR2HSV)

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
