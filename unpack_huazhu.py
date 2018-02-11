#!python
import os,sys
from xml.etree import ElementTree
from PIL import Image

def tree_to_dict(tree):
    d = {}
    for index, item in enumerate(tree):
        if item.tag == 'key':
            if tree[index+1].tag == 'string':
                d[item.text] = tree[index + 1].text
            elif tree[index + 1].tag == 'true':
                d[item.text] = True
            elif tree[index + 1].tag == 'false':
                d[item.text] = False
            elif tree[index+1].tag == 'dict':
                d[item.text] = tree_to_dict(tree[index+1])
    return d 
    
def gen_png_from_plist(plist_filename, png_filename):
    file_path = plist_filename.replace('.plist', '')
    big_image = Image.open(png_filename)
    root = ElementTree.fromstring(open(plist_filename, 'r').read())
    plist_dict = tree_to_dict(root[0])
    to_list = lambda x: x.replace('{','').replace('}','').split(',')
    for k,v in plist_dict['frames'].items():
        if v.has_key('textureRect'):
            rectlist = to_list(v['textureRect'])
        elif v.has_key('frame'):
            rectlist = to_list(v['frame'])
        if v.has_key('rotated'):
            width = int( rectlist[3] if v['rotated'] else rectlist[2] )
            height = int( rectlist[2] if v['rotated'] else rectlist[3] )        
        else:
            width = int( rectlist[2] )
            height = int( rectlist[3] )
        #print v
        sizelist = [width,height]
        #print sizelist
        box=( 
            int(rectlist[0]),
            int(rectlist[1]),
            int(rectlist[0]) + width,
            int(rectlist[1]) + height,
            )
        rect_on_big = big_image.crop(box)
        result_image = Image.new('RGBA', sizelist, (0,0,0,0))
        
        if not os.path.isdir(file_path):
            os.mkdir(file_path)
        k = k.replace('/', '_')
        outfile = (file_path+'/' + k).replace('gift_', '')
        #print k
        if outfile.find('.png') == -1:
            outfile = outfile + '.png'
        result_box=(0, 0, width, height)
        result_image.paste(rect_on_big, result_box, mask=0)
        print outfile, "generated"
        result_image.save(outfile)

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print("You must pass filename as the parameter!")
        exit(1)
    filename = sys.argv[1]
    plist_filename = filename + '.plist'
    png_filename = filename + '.png'
    if (os.path.exists(plist_filename) and os.path.exists(png_filename)):
        gen_png_from_plist( plist_filename, png_filename )
    else:
        print "make sure you have both plist and png files in the same directory"
