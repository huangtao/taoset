# -*- coding: utf-8 -*-
#
# 爬取http://www.howzf.com/esf/xq_index_474467462.htm页面数据
# 参考文章:
# 1. https://blog.csdn.net/Jeeson_Z/article/details/82047685
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


def cv2_crop(im, box):
    '''cv2实现类似PIL的裁剪

    :param im: cv2加载好的图像
    :param box: 裁剪的矩形，(left, upper, right, lower)元组
    '''
    return im.copy()[box[1]:box[3], box[0]:box[2], :]


def get_transparency_location(image):
    '''获取基于透明元素裁切图片的左上角、右下角坐标

    :param image: cv2加载好的图像
    :return: (left, upper, right, lower)元组
    '''
    # 1. 扫描获得最左边透明点和最右边透明点坐标
    height, width, channel = image.shape  # 高、宽、通道数
    assert channel == 4  # 无透明通道报错
    first_location = None  # 最先遇到的透明点
    last_location = None  # 最后遇到的透明点
    first_transparency = []  # 从左往右最先遇到的透明点，元素个数小于等于图像高度
    last_transparency = []  # 从左往右最后遇到的透明点，元素个数小于等于图像高度
    for y, rows in enumerate(image):
        for x, BGRA in enumerate(rows):
            alpha = BGRA[3]
            if alpha != 0:
                if not first_location or first_location[1] != y:  # 透明点未赋值或为同一列
                    first_location = (x, y)  # 更新最先遇到的透明点
                    first_transparency.append(first_location)
                last_location = (x, y)  # 更新最后遇到的透明点
        if last_location:
            last_transparency.append(last_location)

    # 2. 矩形四个边的中点
    top = first_transparency[0]
    bottom = first_transparency[-1]
    left = None
    right = None
    for first, last in zip(first_transparency, last_transparency):
        if not left:
            left = first
        if not right:
            right = last
        if first[0] < left[0]:
            left = first
        if last[0] > right[0]:
            right = last

    # 3. 左上角、右下角
    upper_left = (left[0], top[1])  # 左上角
    bottom_right = (right[0], bottom[1])  # 右下角

    return upper_left[0], upper_left[1], bottom_right[0], bottom_right[1]


# 模式匹配识别
# 找出图片中的最佳匹配位置
# 返回需要移动的距离
def findPic(type_str):
    # 读取滑块背景图片
    img_bg = cv.imread('yz_bg.png')
    img_bg_gray = cv.cvtColor(image_bg, cv.COLOR_BGR2GRAY)
    # 读取滑块图片(灰度模式)
    image_slider = cv.imread('yz_slider.png', 0)
    slider_h, slider_w = image_slider.shape[:2]
    # 在滑块背景图中匹配滑块
    result = cv.matchTemplate(image_bg_gray, image_slider, cv.TM_SQDIFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    # CV_TM_SQDIFF和CV_TM_SQDIFF_NORMED模式min_val越接近0匹配度越好，匹配位置取min_loc
    # 其他方法max_val越接近1匹配度越好，匹配位置取max_loc
    if debug == True:
        # 目标位置绘制一个红色矩形
        cv.rectangle(image_bg, min_loc,
                     (min_loc[0]+slider_w, min_loc[1]+slider_h), (0, 0, 255), 2)
        strmin_val = str(min_val)
        cv.imshow('MatchResult---MatchingValue='+strmin_val, image_bg)
        cv.imshow('slider', image_slider)
        cv.waitKey(0)

    value = cv.minMaxLoc(result)
    # 获取x坐标
    return value[2:][0][0], value[2:][1][0]


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
            with open('yz_slider.png', 'wb') as f:
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
            with open('yz_slider.png', 'wb') as f:
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
