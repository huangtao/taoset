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
# a.是出现一个箭头滑块，鼠标到滑块或滑动进度条上才出现图片。
# b.需要拼的小图片出现在大图片的左上方。大图片一般由若干张小图片组成(偶尔也有一张的)。图片资源采用base64传给浏览器。
# c.a和b的结合体,大图做了放破解水印，下方滑动块为胶囊型
# 两种类型采用了完全不同的结构
# 这里因为时间有限只实现a

debug = True

# 这里设定两张图片的尺寸
cut_width = 60
cut_height = 160
back_width = 320
back_height = 160


class Howzf(object):

    def __init__(self):
        self.url = ''
        self.back_img = None
        self.cut_img = None
        if debug:
            # 打开浏览器
            self.browser = webdriver.Chrome()
        else:
            # 打开浏览器(不弹出浏览器页面)
            opt = webdriver.ChromeOptions()
            opt.set_headless()
            self.browser = webdriver.Chrome(options=opt)

    def get_page_type(self):
        # 识别页面情况
        # 0 - 验证码页面
        # 1 - 目标数据页面
        # -1 - 错误
        try:
            # 判断是否有<div class='info ip'
            soup = BeautifulSoup(self.browser.page_source, 'lxml')
            tag = soup.find_all('div', class_='info ip')
            if len(tag) > 0:
                # 是验证页面
                return 0
            else:
                return 1
        except BaseException as msg:
            if debug == True:
                print(msg)
            return -1
        return -1

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
                    distance = get_distance(back_img=back_image, cut_img=cut_image)
                    self.auto_drag(distance)
                    time.sleep(2)
                    # 这里应该已经验证通过了，我们检查一下如果没有通过验证
                    # 把图片保存起来供分析使用
                    page_type2 = self.get_page_type()
                    if page_type2 == 0:
                        print('主人:滑块验证失败了')
                        cv2.imwrite('cut_img_failed.png', cut_image)
                        cv2.imwrite('back_img_failed.jpg', back_image)
                elif ctype == 'b':
                    # TODO
                    print('尚未实现b类型验证')
                    self.browser.get(url)
                elif ctype == 'c':
                    # TODO
                    print('尚未实现b类型验证')
                    self.browser.get(url)
            elif page_type == 1:
                print(self.browser.page_source)
                # 演示用，延迟10S后刷新页面
                time.sleep(10)
                self.browser.get(url)
            else:
                # 错误了，刷新
                self.browser.get(url)

    def get_captcha_type(self):
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
            if debug == True:
                print(msg)
            return ''

    def get_image(self):
        # # 等待加载
        # WebDriverWait(self.browser, 10, 0.5).until(
        #     EC.visibility_of_element_located((By.CLASS_NAME, 'yidun_bg-img')))
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
        # 让cut_img高度和back相同，高度不同计算距离会产生错误
        layer1 = Image.open("cut_img.png")
        final1 = Image.new("RGBA", (cut_width, cut_height))
        final1.paste(layer1, (0, 2), layer1)
        final1.save("cut_final.png")
        # opencv读取图片
        self.back_img = cv2.imread("back_img.jpg")
        self.cut_img = cv2.imread("cut_final.png")
        return self.cut_img, self.back_img

    def auto_drag(self, distance):
        element = self.browser.find_element_by_class_name("yidun_slider")

        # 这里就是根据移动进行调试，计算出来的位置不是百分百正确的，加上一点偏移
        # distance -= element.size.get('width') / 2
        distance += 13
        has_gone_dist = 0
        remaining_dist = distance
        # distance += randint(-10, 10)

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


def get_distance(back_img, cut_img, slider_width=20):
    back_canny = get_back_canny(back_img)
    operator = get_operator(cut_img)
    pos_x, max_value = best_match(back_canny, operator)

    # 魔术调整
    pos_x = pos_x - 3
    return pos_x


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

    # if debug == True:
    #     cv2.imshow('Canny', img_canny)
    #     cv2.waitKey(0)
    #     cv2.destroyAllWindows()
    return img_canny


def get_operator(cut_img):

    cut_gray = cv2.cvtColor(cut_img, cv2.COLOR_BGR2GRAY)

    _, cut_binary = cv2.threshold(cut_gray, 127, 255, cv2.THRESH_BINARY)
    # 获取边界
    contours, hierarchy = cv2.findContours(
        cut_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # 获取最外层边界
    contour = contours[-1]
    # operator矩阵
    operator = np.zeros((cut_height, cut_width))
    # 根据 contour填写operator
    for point in contour:
        operator[point[0][1]][point[0][0]] = 1

    # if debug == True
    #     cv2.imshow('operator', operator)
    #     cv2.waitKey(0)
    #     cv2.destroyAllWindows()
    return operator


if __name__ == '__main__':
    # 测试计算距离函数
    # cut_image, back_image = read_img_file('cut_final.png', 'back_img.jpg')
    # distance = get_distance(back_img=back_image, cut_img=cut_image)
    # print(distance)

    page = Howzf()
    page.visit('http://www.howzf.com/esf/xq_index_474467462.htm')
    cut_image, back_image = page.get_image()
    distance = get_distance(back_img=back_image, cut_img=cut_image)
    page.auto_drag(distance)
