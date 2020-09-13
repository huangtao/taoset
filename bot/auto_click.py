# -*- coding: utf-8 -*-
#
# 自动验证此网站的滑块验证码:http://www.howzf.com/esf/xq_index_474467462.htm
# 参考文章:
# 1. https://blog.csdn.net/Jeeson_Z/article/details/82047685
# 2. https://www.cnblogs.com/ohahastudy/p/11493971.html
# 3. https://blog.csdn.net/jingjing_94/article/details/80555511
#

import os
import base64
import time
import io
import numpy as np
import cv2 as cv
import requests

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from urllib.request import urlretrieve
from bs4 import BeautifulSoup
from PIL import Image


def init():
    # 全局变量
    global url, browser, wait, debug
    debug = True
    url = 'http://www.howzf.com/esf/xq_index_474467462.htm'
    if debug:
        # 打开浏览器
        browser = webdriver.Chrome()
    else:
        # 打开浏览器(不弹出浏览器页面)
        browser = webdriver.PhantomJS()
    wait = WebDriverWait(browser, 20)


# 识别页面情况
# 0 - 验证码页面
# 1 - 目标数据页面
# -1 - 错误
def get_page_type():
    try:
        # 判断是否有<div class='info ip'
        soup = BeautifulSoup(browser.page_source, 'lxml')
        tag = soup.find_all('div', class_='info ip')
        if len(tag) > 0:
            # 是验证页面
            return 0
        else:
            return 1
    except BaseException as msg:
        print(msg)
        return -1


# 对滑块进行二值化处理
def handle_hk():
    image = cv.imread('yz_hk.png')
    kernel = np.ones((8, 8), np.uint8)  # 去滑块的前景噪声内核
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    width, height = gray.shape
    for h in range(height):
        for w in range(width):
            if gray[w, h] == 0:
                gray[w, h] = 96
    # if debug == True:
    #     cv.imshow('gray', gray)
    #     cv.waitKey(0)
    binary = cv.inRange(gray, 96, 96)
    res = cv.morphologyEx(binary, cv.MORPH_OPEN, kernel)
    # if debug == True:
    #     cv.imshow('res', res)
    #     cv.waitKey(0)
    return res


# 模式匹配识别
def template_match(type_str):
    tpl = handle_hk()
    image_pin = cv.imread('yz_bg.png')
    # 目标图高斯滤波
    # blurred = cv.GaussianBlur(image_pin, (3, 3), 0)
    gray = cv.cvtColor(image_pin, cv.COLOR_BGR2GRAY)
    # 目标图二值化
    ret, target = cv.threshold(gray, 127, 255, cv.THRESH_BINARY)
    # if debug == True:
    #     cv.imshow('template', tpl)
    #     cv.imshow('target', target)
    #     cv.waitKey(0)
    method = cv.TM_CCOEFF_NORMED
    width, height = tpl.shape[:2]
    result = cv.matchTemplate(target, tpl, method)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    left_up = max_loc
    right_down = (left_up[0] + height, left_up[1] + width)
    cv.rectangle(image_pin, left_up, right_down, (0, 0, 255), 2)
    # if debug == True:
    #     cv.imshow('res', image_pin)
    #     cv.waitKey(0)
    cv.imwrite('yz_target.png', image_pin)
    x = 0
    y = 0
    if type_str == 'a':
        # 返回x方向距离即可
        x = left_up[0] + width / 2
    else:
        # 返回中心点
        x = left_up[0] + width / 2
        y = left_up[1] + height / 2
        # 偏移修正
        x += width / 2
        y -= height / 2
    return x, y


# 模拟鼠标进行滑块验证
# 验证码有两种类型:
# a.是出现一个箭头滑块，鼠标到滑动进度条上才出现图片
# b.直接图片和需要拼的小图片
# 我们取中间的一个正方形区域，如果此区域都是白色那么我们认定是a，否则是b
def do_identify():
    try:
        frame = browser.find_element_by_xpath('//iframe')
        # 进入iframe页面
        browser.switch_to_frame(frame)
        soupFrame = BeautifulSoup(browser.page_source, 'lxml')
        tagRet = soupFrame.find_all('div', class_='yidun_slider')
        if len(tagRet) > 0:
            # a类型
            # 获取滑块和拼图URL下载保存
            tagBg = soupFrame.find_all('img', class_='yidun_bg-img')
            brUrl = tagBg[0].get('src')
            tagJigsaw = soupFrame.find_all('img', class_='yidun_jigsaw')
            JigsawUrl = tagJigsaw[0].get('src')
            if len(brUrl) == 0 or len(JigsawUrl) == 0:
                return False
            re = requests.get(brUrl)
            with open('yz_bg.png', 'wb') as f:
                f.write(re.content)
            re = requests.get(JigsawUrl)
            with open('yz_hk.png', 'wb') as f:
                f.write(re.content)
            # 滑块和拼图高度是相同的,只要计算出x方向需要移动的距离即可
            move_x, move_y = template_match('a')
            # 将鼠标移动到滑块上
            elHk = browser.find_elements_by_class_name('yidun_slider')
            webdriver.ActionChains(browser).move_to_element(elHk[0]).perform()
            webdriver.ActionChains(browser).drag_and_drop_by_offset(
                elHk[0], move_x, 0).perform()
            return True
        tagRet = soupFrame.find_all('center', class_='textcontent')
        if len(tagRet) > 0:
            # b类型
            # 滑块和拼图为base64信息，拿到base64保存
            # 注意!!!
            # b类型还有一种可能是将背景图分为24张小图片(24个div)拼接
            # 一排12张分两排,这种情况下需要将24张base64图片数据自己拼成一张大的
            # 此处仅做演示，返回False让他刷新吧
            tagImg = soupFrame.find_all('center', class_='imgcontent')
            lxIC = tagImg[0]
            tagICDiv = lxIC.find_all('div')
            lxICD = tagICDiv[0]
            tagTarget = lxICD.find_all('div')
            # 得到滑块图片
            tagHk = tagTarget[0]
            styleStr = tagHk.attrs['style']
            pat = 'data:image/png;base64,'
            posStart = styleStr.find(pat)
            posEnd = styleStr.rfind('");')
            if posStart == -1 or posEnd == -1:
                return False
            hkBase64 = styleStr[posStart+len(pat):posEnd]
            with open('yz_hk.png', 'wb') as f:
                f.write(base64.b64decode(hkBase64))
            # 为了统一应对，使用截图方式得到拼图图片
            # # 得到拼图图片
            # tagBg = tagTarget[1]
            # styleStr = tagBg.attrs['style']
            # posStart = styleStr.find(pat)
            # posEnd = styleStr.rfind('");')
            # if posStart == -1 or posEnd == -1:
            #     return False
            # bgBase64 = styleStr[posStart+len(pat):posEnd]
            # with open('yz_bg.png', 'wb') as f:
            #     f.write(base64.b64decode(hkBase64))

            browser.get_screenshot_as_file('sc.png')
            sc_img = Image.open('sc.png')
            box = (sc_img.width/2-123, sc_img.height/2-58,
                   sc_img.width/2+137, sc_img.height/2+60)
            center_img = sc_img.crop(box)
            center_img.save('yz_bg.png')

            move_x, move_y = template_match('b')
            # 将鼠标移动到滑块上
            elImgContent = browser.find_elements_by_class_name('imgcontent')
            elContent = elImgContent[0].find_elements_by_tag_name('div')
            elDiv = elContent[0].find_elements_by_tag_name('div')
            webdriver.ActionChains(browser).move_to_element(elDiv[0]).perform()
            webdriver.ActionChains(browser).drag_and_drop_by_offset(
                elDiv[0], move_x, move_y).perform()
            return True
        print("主人:对方添加了新的验证页面类型，请匹配!")
        return False
    except BaseException as msg:
        print(msg)
        return False


# 主程序
def main():
    # 初始化
    init()
    # 打开页面
    browser.get(url)
    time.sleep(2)
    while True:
        # 判定页面类型
        page_type = get_page_type()
        if page_type == 0:
            do_identify()
        elif page_type == 1:
            print(browser.page_source)
            # 演示用，延迟10S后刷新页面
            time.sleep(10)
            browser.get(url)
        else:
            browser.get(url)
        time.sleep(2)


# 入口
if __name__ == '__main__':
    main()
