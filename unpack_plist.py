#!/usr/bin/python3

import os,sys
import xml.etree.ElementTree as ET
from PIL import Image

def tree_to_dict(tree):
    "迭代将plist转化为字典"
    d = {}
    for index,item in enumerate(tree):
        if item.tag == "key":
            if tree[index+1].tag == "string":
                d[item.text] = tree[index+1].text
            elif tree[index+1].tag == "true":
                d[item.text] = True
            elif tree[index+1].tag == "false":
                d[item.text] = False
            elif tree[index+1].tag == "dict":
                d[item.text] = tree_to_dict(tree[index+1])
    return d

def get_png_from_plist(plist_filename, png_filename):
    "从plist和拼图中得到所有的图片"
    file_path = plist_filename.replace(".plist", "")
    big_image = Image.open(png_filename)

    # 从plist中获取每个子图信息
    tree = ET.parse(plist_filename)
    #ET.dump(tree)
    root = tree.getroot()
    plist_dict = tree_to_dict(root[0])
    to_list = lambda x: x.replace("{","").replace("}","").split(",")
    for k,v in plist_dict["frames"].items():
        # 子图矩形
        if "textureRect" in v:
            rectlist = to_list(v["textureRect"])
        elif "frame" in v:
            rectlist = to_list(v["frame"])
        # 旋转属性
        rotated = False
        if "rotated" in v:
            if v["rotated"]:
                rotated = True
        if "textureRotated" in v:
            if v["textureRotated"]:
                rotated = True
        if rotated:
            width = int(rectlist[3])
            height = int(rectlist[2])
        else:
            width = int(rectlist[2])
            height = int(rectlist[3])
        #print(v)
        if "spriteSourceSize" in v:
            sizelist = [int(x) for x in to_list(v["spriteSourceSize"])]
        elif "sourceSize" in v:
            sizelist = [int(x) for x in to_list(v["sourceSize"])]
        else:
            sizelist = [int(rectlist[2]),int(rectlist[3])]
        src_rect = (
            int(rectlist[0]),
            int(rectlist[1]),
            int(rectlist[0])+width,
            int(rectlist[1])+height
        )
        rect_on_big = big_image.crop(src_rect)
        if rotated:
            rect_on_big = rect_on_big.transpose(Image.ROTATE_90)
        
        # 建立新图片
        result_image = Image.new("RGBA", sizelist, (0,0,0,0))
        result_box = (0, 0, sizelist[0], sizelist[1])
        result_image.paste(rect_on_big, result_box)

        # 保存到文件
        if not os.path.isdir(file_path):
            os.mkdir(file_path)
        k = k.replace("/", "_")
        outfile = (file_path+"/"+k).replace("gift_","")
        print(outfile,"generated")
        result_image.save(outfile)

def main():
    if len(sys.argv) <= 1:
        print("You must pass filename as the parameter!")
        exit(1)
    filename = sys.argv[1]
    plist_name = filename + ".plist"
    png_name = filename + ".png"
    if (os.path.exists(plist_name) and os.path.exists(png_name)):
        get_png_from_plist(plist_name, png_name)
    else:
        print("Make sure you have both plist and png files in the same directory!")

# 脚本既可以执行也能导入到其他模块中使用
if __name__ == "__main__":        
    main()
