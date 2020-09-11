# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# text = "黄若绮"
text = """
仙女若绮
短跑高手 西湖区 五年级四班 逃跑吧少年爱好者
要当农场主 爱我你就抱抱我 数学不好
妈妈表扬我吖 喜欢小动物 幻想有一只喵或者汪
"""


x, y = np.ogrid[:300, :300]

mask = (x-150) ** 2 + (y-150) ** 2 > 130 ** 2
mask = 255 * mask.astype(int)

font = r'C:\Windows\Fonts\simhei.ttf'
wc = WordCloud(background_color="white", font_path=font, repeat=True, mask=mask)
wc.generate(text)

plt.axis("off")
plt.imshow(wc, interpolation="bilinear")
plt.show()
