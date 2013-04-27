"""Utilities to transform pictures to 136-len strings
warning: PIL only exists in python-2

Data from:
- http://mldata.org/repository/data/viewslug/chars74k-english-hnd/
"""

from PIL import Image
from itertools import product
import glob, os

def get_bits(file, size):
    image = Image.open(file)
    return image_to_bits(image, size)

def image_to_bits(image, size):
    '''Takes an image and a size
    Maps the image onto a size x size grid and returns each pixel
    (0 for white, 1 for black) in a string of length size * size
    '''
    pix = image.load()
    box = image.getbbox()
    minx = box[0]
    miny = box[1]
    maxx = box[2]
    maxy = box[3]
    for x, y in product(range(minx, maxx), range(miny, maxy)):
        if pix[x, y] == (0, 0, 0):
            minx = x
            break
    for x, y in product(range(box[2] - 1, minx, -1), range(miny, maxy)):
        if pix[x, y] == (0, 0, 0):
            maxx = x
            break
    for y, x in product(range(miny, maxy), range(minx, maxx)):
        if pix[x, y] == (0, 0, 0):
            miny = y
            break
    for y, x in product(range(box[3] - 1, miny, -1), range(minx, maxx)):
        if pix[x, y] == (0, 0, 0):
            maxy = y
            break
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
    image = image.crop((minx, miny, maxx, maxy))
    image.thumbnail((size, size))
    str = ""
    pix = image.load()
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
        print("starting folder", dirs[i])
        path = "characters/Hnd/Img/Sample0" + dirs[i] + "/*.png"
        for file in glob.glob(path):
            try:
                results.write(get_bits(file, 10) + "0" * i + "1" + "0" * (35 - i) + "\n")
            except SyntaxError:
                print("error occurred at " + file)
            
if __name__ == "__main__":
    get_all_bits()
