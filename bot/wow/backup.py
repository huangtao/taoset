# -*- coding: utf-8 -*-
#
# 魔兽世界机器人
# 设置要求：
# 1. 魔兽世界必须运行在WIN10窗口模式且分辨率调整为1024*768(系统=>窗口尺寸)
# 2. 系统分辨率设置不能有缩放，必须设置100%
# 3. 人物头像状态文字选择无，禁止所有大脚类插件
# 4. 只支持Farm敌对怪(中立怪不支持，1级的时候手工练一下)
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
from config import *
from control import *


def main():
    pygame.init()
    pygame.font.init()
    myfont = pygame.font.SysFont('SimHei', 16)

    size = width, height = 1000, 1000
    white = 255, 255, 255
    black = 0, 0, 0
    rangeChecked = False

    # 创建一个窗口
    screen = pygame.display.set_mode(size)

    targetCoord = 0
    gameStarted = False
    initialMove = False
    hwnd = 0

    gameState = 'findTarget'

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
        pygame.display.flip()

    config.setHwnd(hwnd)
    # 初始化示意表面
    win32api.keybd_event(13, 0, 0, 0)
    win32gui.SetForegroundWindow(hwnd)
    (left, top, right, bottom) = win32gui.GetWindowRect(hwnd)
    mapSurface = pygame.Surface((right-left, bottom-top))
    mapSurface.fill((100, 100, 100))
    pygame.display.flip()
    screen.blit(mapSurface, (0, 300))
    positioner = Positioner(mapSurface)

    is_water = False
    count_notview = 0
    is_fighting = False
    midY = 0
    time_try_attack = 0

    # tab是比较智能的。优先选取正前方单位
    pyautogui.press('tab')

    while gameStarted:
        # 是否在攻击范围内
        isInRange = False
        # 是否视野范围内
        targetSeen = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        win32api.keybd_event(13, 0, 0, 0)
        try:
            win32gui.SetForegroundWindow(hwnd)
        except:
            continue

        (left, top, right, bottom) = win32gui.GetWindowRect(hwnd)

        # 游戏窗口尺寸
        window_w = right - left - sc_offset_left - sc_offset_right
        window_h = bottom - top - sc_offset_top - sc_offset_bottom

        # 游戏区域尺寸
        game_w = window_w - 2 * frameSize
        game_h = window_h - titleHeight - 2 * frameSize

        # 游戏区域左上角参考点
        left_top_x = left + sc_offset_left + frameSize
        left_top_y = top + sc_offset_top + frameSize + titleHeight

        with mss.mss() as sct:
            # 头像
            playerStats = {"top": left_top_y + 15, "left": left_top_x + 21,
                           "width": 188, "height": 68}
            targetStats = {"top": left_top_y + 15, "left": left_top_x + 254,
                           "width": 188, "height": 68}
            # 去掉头像部分
            worldView = {"top": left_top_y + 100, "left": left_top_x,
                         "width": game_w, "height": game_h - 100}
            miniMapView = {"top": left_top_y, "left": left_top_x + 852,
                           "width": 170, "height": 175}

            playerStatsSC = sct.grab(playerStats)
            playerStatsImg = np.array(playerStatsSC)
            targetStatsSC = sct.grab(targetStats)
            targetStatsImg = np.array(targetStatsSC)
            worldViewSC = sct.grab(worldView)
            worldViewImg = np.array(worldViewSC)
            miniMapSC1 = sct.grab(miniMapView)
            miniMapImg1 = np.array(miniMapSC1)
            miniMapSC2 = sct.grab(miniMapView)
            miniMapImg2 = np.array(miniMapSC2)
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
                mss.tools.to_png(miniMapSC1.rgb,
                                 miniMapSC1.size, output="minimap.png")

            # 得到生命值和魔法值
            health, mana = getCurrentBar(playerStatsImg)
            # 目标
            target = getTargetStats(targetStatsImg)

            playerHealthText = myfont.render(
                "我的生命值: " + health + "%", False, (0, 0, 0))
            playerManaText = myfont.render(
                "我的魔法值: " + mana + "%", False, (0, 0, 0))

            if (target == ""):
                gameState = 'findTarget'
                if (target == "enemy" or (kill_neutral and target == "neutral")):
                    # 得到目标坐标
                    coord, canSeeTarget, midY = getTargetCoor(worldViewImg)
                    targetCoord = coord
                    targetSeen = canSeeTarget
                else:
                    targetSeen = False
            else:
                is_fighting = False

            if (not is_fighting):
                # 是否喝水
                if (mana == '' or int(mana) < 30):
                    gamestate = 'water'
                    pyautogui.press('-')
                    pyautogui.press('=')
                    is_water = True
                    time_start_water = datetime.datetime.now()
                    continue
                if (is_water):
                    if (health == 100 and mana == 100):
                        is_water = False
                        continue
                    curr_time = datetime.datetime.now()
                    durn = (curr_time - time_start_water).seconds
                    if (durn > 18):
                        is_water = False
                    continue

            screen.fill(white)

            if (target == "enemy" or (kill_neutral and target == "neutral")):
                stopMovement(positioner)

                playerCurrentTarget = myfont.render(
                    "当前目标: " + target, False, (0, 0, 0))
                enemyHelth, enemyMana = getTargetBar(targetStatsImg)
                currTargetStats = myfont.render(
                    "目标生命: " + enemyHelth, False, (0, 0, 0))
                screen.blit(currTargetStats, (0, 80))
                screen.blit(playerCurrentTarget, (0, 40))

                # 尝试攻击
                if (gamestate == 'findTarget'):
                    # 能攻击吗
                    if (not rangeChecked):
                        isInRange = castRangeCheck(worldViewImg)
                    # 目标在攻击范围内
                    if (isInRange):
                        rangeChecked = True
                        pyautogui.press('1')
                        gameState = 'tryAttack'
                        time_try_attack = int(round(time.time()*1000)
                        # 1.5s后检查有没有进入战斗状态
                elif (gamestate == 'tryAttack'):
                    curr_time = int(round(time.time()*1000)
                    durn = (curr_time - time_start_water)
                    if (durn > 1600):
                        # 进入战斗状态
                        is_fighting = isFighting(playerStatsImg)
                        if (is_fighting):
                            gamestate == 'fighting'
                        else:
                            # 没有进入战斗状态
                            gamestate = 'findTarget'
                    continue
                elif (gamestate == 'fighting')
                    pyautogui.press('1')

                if (targetSeen and (target == "enemy" or (kill_neutral and target == "neutral"))):
                    losText = myfont.render("目标在视野中", False, (0, 0, 0))
                    screen.blit(losText, (0, 60))

                    # 能攻击吗
                    if (not rangeChecked):
                        isInRange = castRangeCheck(worldViewImg)
                    # 目标在攻击范围内
                    if (isInRange):
                        rangeChecked = True
                        pyautogui.press('1')
                        is_fighting = True

                    else:
                        pyautogui.keyDown('w')
                        time.sleep(0.25)
                        pyautogui.keyUp('w')
                        positioner.updatePosition()
                        positioner.drawLinesFromData()
                    # # 镜头只调整一次
                    # isCentered = centerScreen(targetCoord, positioner, is_fighting)
                    # if (isCentered):

                elif (not targetSeen):
                    is_fighting = False
                    losText = myfont.render("目标不在视野中", False, (0, 0, 0))
                    screen.blit(losText, (0, 60))
                    # 取消目标
                    pyautogui.press('esc')
                    pyautogui.press('tab')

            # 没有敌对目标
            else:
                is_fighting = False
                # 按TAB键w
                if (debug_step):
                    win32api.keybd_event(13, 0, 0, 0)
                    win32gui.SetForegroundWindow(hwnd)
                pyautogui.press('tab')
                rangeChecked = False
                releaseControls()

                # 继续检查目标
                target = getTargetStats(targetStatsImg)

                if (target != "enemy" or (kill_neutral and target != "neutral")):
                    if (debug_step):
                        win32api.keybd_event(13, 0, 0, 0)
                        win32gui.SetForegroundWindow(hwnd)
                    moveAboutMap(positioner)
                    # 我们已经在移动了(没有卡住),继续调用移动w
                    # moving = checkMapMovement(miniMapImg1, miniMapImg2)
                    moving = positioner.isMoved()
                    if (moving):
                        positioner.updatePosition()
                        positioner.drawLinesFromData()
                        isLeave = positioner.isMustBack()
                        if (isLeave):
                            moveSideWays(positioner)
                    else:
                        # 没有移动或者太远了转向
                        moveSideWays(positioner)

            # print(positioner.direction)
            screen.blit(playerHealthText, (0, 0))
            screen.blit(playerManaText, (0, 20))
            screen.blit(mapSurface, (0, 300))
            pygame.display.flip()

        screen.fill(white)


main()
