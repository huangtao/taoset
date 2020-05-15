# -*- coding: utf-8 -*-
#
# 魔兽世界机器人
# 设置要求：
# 1. 魔兽世界必须运行在WIN10窗口模式且分辨率调整为1024*768(系统=>窗口尺寸)
# 2. 系统分辨率设置不能有缩放，必须设置100%
# 3. 人物头像状态文字选择无
# 4. 魔兽世界窗口不能最小化
# 5. 无论什么职业1号键位必须是远程技能(近战为弓箭)
# 6. 动作栏除了1号键。2号开始按优先级排列。自动检测到6号为止。6号必须放普通攻击
#

import os
import sys
import time
import datetime
#
import numpy as np
import cv2
import mss
import mss.tools
#
import msvcrt
import win32api
import win32con
import win32gui
import win32print
import win32ui
#
from config import *
from player import *
from target import *
from position import *
from config import *
from control import *


def main():

    rangeChecked = False
    targetCoord = 0
    initialMove = False
    hwnd = 0
    gameState = 'findTarget'

    loop_count = 0
    water_num = 0
    count_notview = 0
    is_fighting = False
    midY = 0
    time_try_attack = datetime.datetime.now()
    is_moving = False
    time_moving = 0
    tab_num = 1
    time_add_buffer = time_try_attack
    oldMana = 0

    # 主循环
    while 1:
        if msvcrt.kbhit():
            key = msvcrt.getch().decode()
            if key == 'q':
                exit(0)

        hwnd = win32gui.FindWindow("GxWindowClass", "魔兽世界")
        if hwnd == 0:
            time.sleep(1)
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
            if (doWater == True and gameState == 'findTarget'):
                # 是否喝水
                if (mana == '' or mana < 30):
                    gamestate = 'water'
                    # =按钮绑定吃喝宏
                    win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, '=', 0)
                    win32api.PostMessage(hwnd, win32con.WM_KEYUP, '=', 0)
                    water_num += 1
                    gameState = 'water'
                    print("进入吃喝状态")
                    oldMana = mana
                    time_start_water = datetime.datetime.now()

            # 目标
            enemyHelth = 0
            target = ''
            enemyHelth, enemyMana = getTargetBar(targetStatsImg)
            if (enemyHelth > 0):
                target = getTargetStats(targetStatsImg)

            if (target == ""):
                gameState = 'findTarget'
            elif (target == "enemy" or (kill_neutral and target == "neutral")):
                if (gameState == 'findTarget'):
                    print("发现有效目标")
                    # 能攻击进入尝试攻击状态
                    isInRange = castRangeCheck(worldViewImg)
                    # 目标在攻击范围内
                    if (isInRange):
                        gameState = 'tryAttack'
                        print("进入尝试攻击状态")
                    else:
                        print("太远不能攻击,重新发现目标")
                        win32api.PostMessage(
                            hwnd, win32con.WM_KEYDOWN, win32con.VK_ESCAPE, 0)
                        win32api.PostMessage(
                            hwnd, win32con.WM_KEYUP, win32con.VK_ESCAPE, 0)
                        gameState = "findTarget"

            if (gameState == 'findTarget'):
                # 按TAB键
                win32api.PostMessage(
                    hwnd, win32con.WM_KEYDOWN, win32con.VK_TAB, 0)
                win32api.PostMessage(
                    hwnd, win32con.WM_KEYUP, win32con.VK_TAB, 0)
                rangeChecked = False
                tab_num += 1
                if (tab_num > 3):
                    # 转方向再TAB
                    print("转方向")
                    win32api.PostMessage(
                        hwnd, win32con.WM_KEYDOWN, win32con.VK_RIGHT, 0)
                    time.sleep(0.2)
                    win32api.PostMessage(
                        hwnd, win32con.WM_KEYUP, win32con.VK_RIGHT, 0)
                    tab_num = 0
                    time.sleep(2)

            elif (gameState == 'tryAttack'):
                # 尝试攻击
                # 49 - 1键
                win32api.PostMessage(
                    hwnd, win32con.WM_KEYDOWN, 49, 0)
                time.sleep(0.2)
                win32api.PostMessage(hwnd, win32con.WM_KEYUP, 49, 0)
                print("尝试攻击")
                time_try_attack = datetime.datetime.now()
                gameState = 'checkAttack'

            elif (gameState == 'checkAttack'):
                # 检查是否进入了战斗状态
                curr_time = datetime.datetime.now()
                durn = (curr_time - time_try_attack).seconds
                if (durn > 2):
                    time_try_attack = curr_time
                    # 进入战斗状态
                    is_fighting = isFighting(playerStatsImg)
                    if (is_fighting):
                        tab_num = 0
                        gameState = 'fighting'
                        print("进入战斗状态")
                    else:
                        # 如果目标的血量是100
                        if enemyHelth == 100:
                            # 没有进入战斗状态
                            win32api.PostMessage(
                                hwnd, win32con.WM_KEYDOWN, win32con.VK_ESCAPE, 0)
                            win32api.PostMessage(
                                hwnd, win32con.WM_KEYUP, win32con.VK_ESCAPE, 0)
                            gameState = 'findTarget'
                            print("没有进入战斗状态，切换到寻找目标状态")
                else:
                    # 根据技能条一个一个检测,最后一个必须是普通攻击
                    spell = getCastSpell(worldViewImg)
                    key_code = int(spell) - 1 + 49
                    win32api.PostMessage(
                        hwnd, win32con.WM_KEYDOWN, key_code, 0)
                    win32api.PostMessage(1
                        hwnd, win32con.WM_KEYUP, key_code, 0)

            elif (gameState == 'fighting'):
                # 如果目标没有少血,换目标
                if (enemyHelth == 100):
                    gameState = 'findTarget'
                else:
                    # 根据技能条一个一个检测,最后一个必须是普通攻击
                    spell = getCastSpell(worldViewImg)
                    key_code = int(spell) - 1 + 49
                    win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, key_code, 0)
                    win32api.PostMessage(hwnd, win32con.WM_KEYUP, key_code, 0)

            elif (gameState == 'water'):
                if (health == 100 and mana == 100):
                    if water_num >= 16:
                        print("做水")
                        water_num = 0
                        # 做水
                        win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, '-', 0)
                        win32api.PostMessage(hwnd, win32con.WM_KEYUP, '-', 0)
                        time.sleep(3)
                        win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, '0', 0)
                        win32api.PostMessage(hwnd, win32con.WM_KEYUP, '0', 0)
                        time.sleep(3)
                        win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, '0', 0)
                        win32api.PostMessage(hwnd, win32con.WM_KEYUP, '0', 0)
                        time.sleep(3)

                        # 继续吃喝
                        win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, '=', 0)
                        win32api.PostMessage(hwnd, win32con.WM_KEYUP, '=', 0)
                        water_num += 1
                    else:
                        curr_time = datetime.datetime.now()
                        durn = (curr_time - time_add_buffer).seconds
                        if (durn > 1500):
                            time_add_buffer = curr_time
                            # 加buffer
                            win32api.PostMessage(
                                hwnd, win32con.WM_KEYDOWN, '9', 0)
                            win32api.PostMessage(
                                hwnd, win32con.WM_KEYUP, '9', 0)
                            time.sleep(1)
                            win32api.PostMessage(
                                hwnd, win32con.WM_KEYDOWN, '8', 0)
                            win32api.PostMessage(
                                hwnd, win32con.WM_KEYUP, '8', 0)
                            time.sleep(1)
                        gameState = 'findTarget'
                        print("进入发现目标状态")
                else:
                    # 如果恢复很慢则做水
                    curr_time = datetime.datetime.now()
                    durn = (curr_time - time_start_water).seconds
                    if (durn > 2 and (mana - oldMana) < 10):
                        water_num = 16

            time.sleep(1)


main()
