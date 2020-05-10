import time
import os
import numpy as np
import cv2
import mss
from PIL import Image

# 魔兽世界任务状态文字选择无(避免识别时中间文字干扰)
maxHealth = 1
maxMana = 1

img = cv2.imread("player.png", 1)

# 两个条位置
img_bar = img[30:52, 65:186]

cv2.imshow("bar", img_bar)

hsv = cv2.cvtColor(img_bar, cv2.COLOR_BGR2HSV)

mana = ""
health = ""

lower_blue = np.array([100, 200, 80])
upper_blue = np.array([120, 255, 255])

lower_green = np.array([60, 80, 80])
upper_green = np.array([90, 255, 255])

blueMask = cv2.inRange(hsv, lower_blue, upper_blue)
greenMask = cv2.inRange(hsv, lower_green, upper_green)
cv2.imshow("mask", greenMask)

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

print(health,mana)

cv2.waitKey(0)
