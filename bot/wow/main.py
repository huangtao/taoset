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
    FPS = 10
    fpsClock = pygame.time.Clock()

    pygame.init()
    pygame.font.init()
    myfont = pygame.font.SysFont('SimHei', 16)

    size = width, height = 480, 320
    white = 255, 255, 255
    black = 0, 0, 0
    rangeChecked = False

    # 创建一个窗口
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (1100, 100)
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
                # saveConfig()
                sys.exit()

        # 绘制一个矩形
        pygame.draw.rect(screen, (150, 100, 200), (400, 0, 80, 80))
        mouse = pygame.mouse.get_pos()
        # print(mouse)
        click = pygame.mouse.get_pressed()
        if (mouse[0] >= 400 and mouse[0] <= 480 and mouse[0] >= 0 and mouse[1] <= 80 and click[0] == 1):
            # 如果在矩形区域内单击表示游戏启动
            hwnd = win32gui.FindWindow("GxWindowClass", "魔兽世界")
            if hwnd == 0:
                textImage = myfont.render("魔兽世界没有运行!", True, black)
                screen.blit(textImage, (0, 20))
            else:
                gameStarted = True
        else:
            textImage = myfont.render("程序为研究编写，严禁用于商业目的!", True, black)
            screen.blit(textImage, (0, 20))
        fpsImage = myfont.render("FPS - " + str(FPS), True, black)
        screen.blit(fpsImage, (0, 0))
        pygame.display.flip()
        fpsClock.tick(FPS)

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
    time_start_water = 0
    tab_num = 1

    # tab是比较智能的。优先选取正前方单位
    pyautogui.press('tab')

    while gameStarted:
        # 是否在攻击范围内
        isInRange = False
        # 是否视野范围内
        targetSeen = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # saveConfig()
                sys.exit()

        win32api.keybd_event(13, 0, 0, 0)
        try:
            win32gui.SetForegroundWindow(hwnd)
        except:
            continue

        (left, top, right, bottom) = win32gui.GetWindowRect(hwnd)
        setWinPos(left, top)

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

            # # debug
            # is_fighting = isFighting(playerStatsImg)

            if (target == ""):
                gameState = 'findTarget'
            elif (target == "enemy" or (kill_neutral and target == "neutral")):
                if (gameState == 'findTarget'):
                    enemyHelth, enemyMana = getTargetBar(targetStatsImg)
                    # 能攻击进入尝试攻击状态
                    isInRange = castRangeCheck(worldViewImg)
                    # 目标在攻击范围内
                    if (isInRange and (enemyHelth != '' and int(enemyHelth) > 0)):
                        gameState = 'tryAttack'

            if (gameState == 'findTarget'):
                # 先检查蓝
                if (mana == '' or int(mana) < 30):
                    gameState = 'water'
                    pyautogui.press('-')
                    pyautogui.press('=')
                    time_start_water = datetime.datetime.now()
                else:
                    # TAB三次后才开始移动
                    # 按TAB键
                    if (debug_step):
                        win32api.keybd_event(13, 0, 0, 0)
                        win32gui.SetForegroundWindow(hwnd)
                    pyautogui.press('tab')
                    rangeChecked = False
                    tab_num += 1
                    # for debug
                    tab_num = 0
                    if (tab_num >= 3):
                        # 需要移动了
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

            elif (gameState == 'water'):
                if (int(mana) >= 100):
                    pyautogui.press('space')
                    gameState = 'findTarget'
                else:
                    curr_time = datetime.datetime.now()
                    durn = (curr_time - time_start_water).seconds
                    if (durn >= 18):
                        pyautogui.press('-')
                        pyautogui.press('=')
                        time_start_water = curr_time

            elif (gameState == 'tryAttack'):
                # 停止移动尝试攻击
                stopMovement(positioner)
                pyautogui.press('1')
                time_try_attack = datetime.datetime.now()
                gameState = 'checkAttack'

            elif (gameState == 'checkAttack'):
                # 检查是否进入了战斗状态
                curr_time = datetime.datetime.now()
                durn = (curr_time - time_try_attack).microseconds / 1000
                if (durn > 1800):
                    # 进入战斗状态
                    is_fighting = isFighting(playerStatsImg)
                    if (is_fighting):
                        gameState = 'fighting'
                    else:
                        # 没有进入战斗状态
                        gameState = 'findTarget'
                else:
                    pyautogui.press('1')

            elif (gameState == 'fighting'):
                pyautogui.press('1')

            else:
                print("未知状态")
                gameState = "findTarget"

            # 更新界面
            stateText = myfont.render(
                "阶段: " + gameState, False, (0, 0, 0))
            playerHealthText = myfont.render(
                "我的生命值: " + health + "%", False, (0, 0, 0))
            playerManaText = myfont.render(
                "我的魔法值: " + mana + "%", False, (0, 0, 0))

            screen.fill(white)
            # print(positioner.direction)
            screen.blit(stateText, (0, 0))
            screen.blit(playerHealthText, (0, 20))
            screen.blit(playerManaText, (0, 40))
            # screen.blit(mapSurface, (0, 300))
            pygame.display.flip()
            fpsClock.tick(FPS)


main()
