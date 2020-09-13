# -*- coding: utf-8 -*-
#
# 爬取http://www.howzf.com/esf/xq_index_474467462.htm页面数据
# 参考文章:
# 1. https://blog.csdn.net/Jeeson_Z/article/details/82047685
#
#opencv模板匹配----单目标匹配
import cv2
#读取目标图片
target = cv2.imread("yz_bg.png")
img_bg_gray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
# 目标图二值化(阀值)，过滤掉暗的那个
ret, img_bg_fa = cv2.threshold(img_bg_gray, 127, 255, cv2.THRESH_BINARY)
cv2.imwrite('yz_bg_gray.png', img_bg_fa)
#读取模板图片
template = cv2.imread("yz_slider.png")
img_s_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
ret, img_s_fa = cv2.threshold(img_s_gray, 0, 255, cv2.THRESH_BINARY)
#获得模板图片的高宽尺寸
theight, twidth = template.shape[:2]
#执行模板匹配，采用的匹配方式cv2.TM_SQDIFF_NORMED
result = cv2.matchTemplate(img_bg_fa,img_s_fa,cv2.TM_SQDIFF)
#归一化处理
cv2.normalize( result, result, 0, 1, cv2.NORM_MINMAX, -1 )
#寻找矩阵（一维数组当做向量，用Mat定义）中的最大值和最小值的匹配结果及其位置
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
#匹配值转换为字符串
#对于cv2.TM_SQDIFF及cv2.TM_SQDIFF_NORMED方法min_val越趋近与0匹配度越好，匹配位置取min_loc
#对于其他方法max_val越趋近于1匹配度越好，匹配位置取max_loc
strmin_val = str(min_val)
#绘制矩形边框，将匹配区域标注出来
#min_loc：矩形定点
#(min_loc[0]+twidth,min_loc[1]+theight)：矩形的宽高
#(0,0,225)：矩形的边框颜色；2：矩形边框宽度
cv2.rectangle(target,min_loc,(min_loc[0]+twidth,min_loc[1]+theight),(0,0,225),2)
#显示结果,并将匹配值显示在标题栏上
cv2.imshow('1', img_bg_fa)
cv2.imshow('2', img_s_fa)
cv2.imshow("MatchResult----MatchingValue="+strmin_val,target)
cv2.waitKey()
cv2.destroyAllWindows()
