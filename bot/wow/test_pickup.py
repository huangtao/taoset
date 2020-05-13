import time
import os
import numpy as np
import cv2
import mss
from PIL import Image

img = cv2.imread("testpick.png", 1)

mid_x = 0
mid_y = 0
coord = 0
canSeeTarget = False

hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

lower_yellow = np.array([45, 60, 50])
upper_yellow = np.array([35, 21, 100])
yellowMask = cv2.inRange(hsv, lower_yellow, upper_yellow)

neutralTarget = cv2.bitwise_and(img, img, mask=yellowMask)
cv2.imshow("mask", yellowMask)
cv2.imshow("out", neutralTarget)

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


cv2.waitKey(0)
