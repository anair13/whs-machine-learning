"""Utilities to transform pictures to 136-len strings
warning: PIL only exists in python-2
"""

from PIL import Image
import glob, os

def get_bits(file, size):
    '''Takes the file path to an image and a size
    Maps the image onto a size x size grid and returns each pixel
    (0 for white, 1 for black) in a string of length size * size
    '''
    im = Image.open(file)
    pix = im.load()
    box = im.getbbox()
    maxx = box[0]
    maxy = box[1]
    minx = box[2]
    miny = box[3]
    for x in range(box[0], box[2]):
        for y in range(box[1], box[3]):
            if pix[x, y] == (0, 0, 0):
                if x < minx:
                    minx = x
                if x > maxx:
                    maxx = x
                if y < miny:
                    miny = y
                if y > maxy:
                    maxy = y
    difx = maxx - minx
    dify = maxy - miny
    if difx > dify:
        dif = difx - dify
        miny -= dif / 2 + dif % 2
        maxy += dif / 2
    else:
        dif = dify - difx
        minx -= dif / 2 + dif % 2
        maxx += dif / 2
    im = im.crop((minx, miny, maxx, maxy))
    im.thumbnail((size, size))
    str = ""
    pix = im.load()
    for x in range(size):
        for y in range(size):
            if pix[x, y] == (0, 0, 0):
                str += "1"
            else:
                str += "0"
    return str

dirs = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "50", "51", "52", "53", "54", "55", "56", "57", "58", "59", "60", "61", "62"]

def get_all_bits():
    results = open("ocr.txt", "w")
    for i in range(len(dirs)):
        path = "characters/Hnd/Img/Sample0" + dirs[i] + "/*.png"
        for file in glob.glob(path):
            try:
                results.write(get_bits(file, 10) + "0" * i + "1" + "0" * (35 - i) + "\n")
            except SyntaxError:
                print("error occurred at " + file)
            
if __name__ == "__main__":
    get_all_bits()
