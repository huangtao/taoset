# -*- coding: utf-8 -*-
#
# 魔兽世界机器人
# 设置要求：
# 1. 魔兽世界必须运行在WIN10窗口模式且分辨率调整为1024*768(系统=>窗口尺寸)
# 2. 人物头像状态文字选择无，如果安装了大脚需关闭目标信息-开启目标生命
# 3. 只支持Farm敌对怪(中立怪不支持，1级的时候手工练一下)
#

import os
import sys
import time
import datetime
#
import pyautogui
import numpy as np
import cv2
import PIL
import pygame
import mss
import mss.tools
#
import win32api
import win32con
import win32gui
import win32print
import win32ui
import win10toast
#
from config import *
from player import *
from target import *
from position import *


def main():

    pygame.init()
    pygame.font.init()
    myfont = pygame.font.SysFont('SimHei', 16)

    size = width, height = 1000, 1000
    white = 255, 255, 255
    black = 0, 0, 0

    # 创建一个窗口
    screen = pygame.display.set_mode(size)

    targetCoord = 0
    gameStarted = False
    initialMove = False
    hwnd = 0

    # 主循环
    while (not gameStarted):
        screen.fill(white)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        # 绘制一个矩形
        pygame.draw.rect(screen, (150, 100, 200), (700, 100, 200, 100))
        mouse = pygame.mouse.get_pos()
        # print(mouse)
        click = pygame.mouse.get_pressed()
        if (mouse[0] >= 700 and mouse[0] <= 900 and mouse[0] >= 100 and mouse[1] <= 200 and click[0] == 1):
            # 如果在矩形区域内单击表示游戏启动
            hwnd = win32gui.FindWindow("GxWindowClass", "魔兽世界")
            if hwnd == 0:
                print("魔兽世界没有运行!")
            else:
                gameStarted = True

        textImage = myfont.render("程序为研究编写，严禁用于商业目的!", True, black)
        screen.blit(textImage, (0, 0))

        screen.blit(mapSurface, (0, 300))
        pygame.display.flip()

    # 初始化示意表面
    win32api.keybd_event(13, 0, 0, 0)
    win32gui.SetForegroundWindow(hwnd)
    (left, top, right, bottom) = win32gui.GetWindowRect(hwnd)
    mapSurface = pygame.Surface((right-left, bottom-top))
    mapSurface.fill((100, 100, 100))
    positioner = Positioner(mapSurface)

    while gameStarted:
        targetSeen = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        win32api.keybd_event(13, 0, 0, 0)
        win32gui.SetForegroundWindow(hwnd)
        (left, top, right, bottom) = win32gui.GetWindowRect(hwnd)

        left_top_x = left + sc_offset_x
        left_top_y = top + sc_offset_y + titleHeight

        with mss.mss() as sct:
            # 头像
            playerStats = {"top": left_top_y + 15, "left": left_top_x + 21,
                           "width": 188, "height": 68}
            targetStats = {"top": left_top_y + 15, "left": left_top_x + 254,
                           "width": 188, "height": 68}
            # 减去标题栏和系统任务栏高度
            worldView = {"top": top + titleHeight + 100, "left": left,
                         "width": right - left, "height": bottom - top - titleHeight - 100}
            miniMapView = {"top": top + titleHeight, "left": left,
                           "width": right - left, "height": bottom - top}

            playerStatsSC = sct.grab(playerStats)
            playerStatsImg = np.array(playerStatsSC)
            targetStatsSC = sct.grab(targetStats)
            targetStatsImg = np.array(targetStatsSC)
            worldViewSC = sct.grab(worldView)
            worldViewImg = np.array(worldViewSC)
            miniMapSC = sct.grab(miniMapView)
            miniMapImg = np.array(miniMapSC)
            if debug:
                allStats = {"top": top, "left": left,
                            "width": right - left, "height": bottom - top}
                allSC = sct.grab(allStats)
                mss.tools.to_png(allSC.rgb,
                                 allSC.size, output="wow.png")

                mss.tools.to_png(playerStatsSC.rgb,
                                 playerStatsSC.size, output="player.png")
                mss.tools.to_png(targetStatsSC.rgb,
                                 targetStatsSC.size, output="target.png")
                mss.tools.to_png(worldViewSC.rgb,
                                 worldViewSC.size, output="world.png")
                mss.tools.to_png(miniMapSC.rgb,
                                 miniMapSC.size, output="minimap.png")

            # 得到生命值和魔法值
            health, mana = getCurrentBar(playerStatsImg)
            # 目标
            target = getTargetStats(targetStatsImg)

            playerHealthText = myfont.render(
                "我的生命值: " + health + "%", False, (0, 0, 0))
            playerManaText = myfont.render(
                "我的魔法值: " + mana + "%", False, (0, 0, 0))

            if (target != ""):
                if (target == "enemy"):
                    # 得到目标坐标
                    coord, canSeeTarget = findTarget(worldViewImg)
                    targetCoord = coord
                    targetSeen = canSeeTarget
                else:
                    targetSeen = False

            screen.fill(white)

            if (target == "enemy"):
                stopMovement(positioner)

                playerCurrentTarget = myfont.render(
                    "当前目标: " + target, False, (0, 0, 0))
                enemyHelth, enemyMana = getTargetBar(targetStatsImg)
                currTargetStats = myfont.render(
                    "目标生命: " + enemyHelth, False, (0, 0, 0))
                screen.blit(currTargetStats, (0, 80))

                screen.blit(playerCurrentTarget, (0, 40))

                if (targetSeen and target == "enemy"):
                    losText = myfont.render("目标在视野中", False, (0, 0, 0))
                    screen.blit(losText, (0, 60))

                    isCentered = centerScreen(targetCoord, positioner)
                    if (isCentered):
                        if (not rangeChecked):
                            isInRange = castRangeCheck(worldViewImg)

                        # 目标在攻击范围内
                        if (isInRange):
                            rangeChecked = True
                            pyautogui.press('1')
                        else:
                            pyautogui.keyDown('w')
                            time.sleep(0.25)
                            pyautogui.keyUp('w')
                            positioner.updatePosition()
                            positioner.drawLinesFromData()

                elif (not targetSeen):
                    losText = myfont.render("目标不在视野中", False, (0, 0, 0))
                    screen.blit(losText, (0, 60))

            # 没有敌对目标
            else:
                # 按TAB键
                pyautogui.press('tab')
                rangeChecked = False
                releaseControls()

                # 检查目标
                target = getTargetStats(targetStatsImg)

                if (target != "enemy"):
                    moveAboutMap(positioner)
                    # 我们已经在移动了(没有卡住),继续调用移动
                    moving = checkMapMovement(miniMapImg)
                    if (moving):
                        positioner.updatePosition()
                        positioner.drawLinesFromData()

                    else:
                        pyautogui.press('space')
                        moveSideWays(positioner)

            print(positioner.direction)
            screen.blit(playerHealthText, (0, 20))
            screen.blit(playerManaText, (0, 40))
            screen.blit(mapSurface, (0, 300))
            pygame.display.flip()

        screen.fill(white)


main()
