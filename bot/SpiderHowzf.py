# -*- coding: utf-8 -*-
#
# 爬取http://www.howzf.com/esf/xq_index_474467462.htm页面数据
# huangtao117@yeah.net
#

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import random
import time
import requests
from io import BytesIO
from bs4 import BeautifulSoup
from PIL import Image
import cv2
import numpy as np

# 验证码有两种类型:
# a.是出现一个箭头滑块，鼠标到滑动进度条上才出现图片
# b.直接图片和需要拼的小图片
# 两种类型采用了完全不同的结构
# 这里因为时间有限只实现a


class Howzf(object):

    def __init__(self):
        self.debug = True
        self.url = ''
        self.back_img = None
        self.cut_img = None
        self.cut_width = 91
        self.cut_height = 240
        self.back_width = 480
        self.back_height = 240
        self.scaling_ratio = 1.0
        if debug:
            # 打开浏览器
            self.browser = webdriver.Chrome()
        else:
            # 打开浏览器(不弹出浏览器页面)
            self.browser = webdriver.PhantomJS()

    def visit(self, url):
        self.url = url
        self.browser.get(url)

        # 直到通过验证拿到HTML为止
        while True:
            time.sleep(2)
            # 判定页面类型
            page_type = self.get_page_type()
            if page_type == 0:
                # 去过验证码
                ctype = self.get_captcha_type()
                if ctype == 'a':
                    cut_image, back_image = self.get_image()
                    distance = self.get_distance()
                    self.auto_drag(distance)
                    time.sleep(2)
                elif ctype == 'b'
                    # TODO
                    print('尚未实现b类型验证')
            elif page_type == 1:
                print(browser.page_source)
                # 演示用，延迟10S后刷新页面
                time.sleep(10)
                self.browser.get(url)
            else:
                # 错误了，刷新
                self.browser.get(url)

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

    def get_captcha_type():
        try:
            frame = self.browser.find_element_by_xpath('//iframe')
            # 进入iframe页面
            self.browser.switch_to_frame(frame)
            soupFrame = BeautifulSoup(self.browser.page_source, 'lxml')
            tagRet = soupFrame.find_all('div', class_='yidun_slider')
            if len(tagRet) > 0:
                # a类型
                return 'a'
            tagRet = soupFrame.find_all('center', class_='textcontent')
            if len(tagRet) > 0:
                # b类型
                return 'b'
            print("主人:对方添加了新的验证页面类型，请匹配!")
            return ''
        except BaseException as msg:
            print(msg)
            return ''


    def get_image(self):
        # 等待加载
        WebDriverWait(self.browser, 10, 0.5).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'yidun_bgimg')))
        back_url = self.browser.find_element_by_class_name(
            "yidun_bg-img").get_attribute('src')
        cut_url = self.browser.find_element_by_class_name(
            "yidun_jigsaw").get_attribute('src')
        # 从url获取图片并保存到本地
        resq = requests.get(back_url)
        file = BytesIO(resq.content)
        back_img = Image.open(file)
        back_img.save("back_img.jpg")
        resq = requests.get(cut_url)
        file = BytesIO(resq.content)
        cut_img = Image.open(file)
        cut_img.save("cut_img.png")
        # opencv读取图片
        self.back_img = cv2.imread("back_img.jpg")
        self.cut_img = cv2.imread("cut_img.png")
        self.scaling_ratio = self.browser.find_element_by_class_name(
            "yidun_bg-img").size['width'] / back_width
        return self.cut_img, self.back_img

    def get_distance(self):
        back_canny = get_back_canny(self.back_img)
        operator = get_operator(self.cut_img)
        pos_x, max_value = best_match(back_canny, operator)
        distance = pos_x * self.scaling_ratio
        return distance

    def auto_drag(self, distance):
        element = self.browser.find_element_by_class_name("yidun_slider")

        # 这里就是根据移动进行调试，计算出来的位置不是百分百正确的，加上一点偏移
        #distance -= element.size.get('width') / 2
        distance += 13
        has_gone_dist = 0
        remaining_dist = distance
        #distance += randint(-10, 10)

        # 按下鼠标左键
        ActionChains(self.browser).click_and_hold(element).perform()
        time.sleep(0.5)
        while remaining_dist > 0:
            ratio = remaining_dist / distance
            if ratio < 0.2:
                # 开始阶段移动较慢
                span = random.randint(5, 8)
            elif ratio > 0.8:
                # 结束阶段移动较慢
                span = random.randint(5, 8)
            else:
                # 中间部分移动快
                span = random.randint(10, 16)
            ActionChains(self.browser).move_by_offset(
                span, random.randint(-5, 5)).perform()
            remaining_dist -= span
            has_gone_dist += span
            time.sleep(random.randint(5, 20)/100)

        ActionChains(self.browser).move_by_offset(
            remaining_dist, random.randint(-5, 5)).perform()
        ActionChains(self.browser).release(on_element=element).perform()


def read_img_file(cut_dir, back_dir):
    cut_image = cv2.imread(cut_dir)
    back_image = cv2.imread(back_dir)
    return cut_image, back_image


def best_match(back_canny, operator):
    max_value, pos_x = 0, 0
    for x in range(cut_width, back_width - cut_width):
        block = back_canny[:, x:x + cut_width]
        value = (block * operator).sum()
        if value > max_value:
            max_value = value
            pos_x = x
    return pos_x, max_value


def get_back_canny(back_img):
    img_blur = cv2.GaussianBlur(back_img, (3, 3), 0)
    img_gray = cv2.cvtColor(img_blur, cv2.COLOR_BGR2GRAY)
    img_canny = cv2.Canny(img_gray, 100, 200)
    return img_canny


def get_operator(cut_img):

    cut_gray = cv2.cvtColor(cut_img, cv2.COLOR_BGR2GRAY)

    _, cut_binary = cv2.threshold(cut_gray, 127, 255, cv2.THRESH_BINARY)
    # 获取边界
    _, contours, hierarchy = cv2.findContours(
        cut_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # 获取最外层边界
    contour = contours[-1]
    # operator矩阵
    operator = np.zeros((cut_height, cut_width))
    # 根据 contour填写operator
    for point in contour:
        operator[point[0][1]][point[0][0]] = 1
    return operator


if __name__ == '__main__':
    page = Howzf()
    page.visit('http://game.academy.163.com/minigame/2018/showcase/detail/143')
    cut_image, back_image = page.get_image()
    distance = page.get_distance()
    page.auto_drag(distance)

