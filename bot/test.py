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


def main():
    image = cv.imread('yz_hk.png')
    cv.imshow('img', image)
    cv.waitKey(0)
    cv.destroyAllWindows()


if __name__ == '__main__':
    main()
