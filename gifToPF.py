#!/bin/python

import sys
from PIL import Image, ImageSequence


def main(imgPath, offsetX=0, offsetY=0):
    img = Image.open(imgPath)
    duration = img.info.get('duration', -1)
    if not hasattr(img, 'n_frames'):
        img.n_frames = 1
    print("converting image... 0/" + str(img.n_frames) + " done", end='\r')
    imageBuffer = []
    i = 0
    ii = ImageSequence.Iterator(img)
    for frame in ii:
        frame.save('rendered/test_%02d.png' % i, 'PNG')
        imageBuffer.append(generatePFLines(frame, offsetX, offsetY))
        i += 1
        print("converting image... " + str(i) + "/" + str(img.n_frames) + " done", end='\r')
    print()
    return {'frameBuffer': imageBuffer, 'duration': duration}


#returns array of pixelflut commands for whole line
def generatePFLines(img, offX, offY):
    # convert gif to rgb format (with respect to transparency)
    if img.format == "GIF":
        if img.info.get('transparency', -1) >= 0:
            img = img.convert('RGBA')
        else:
            img = img.convert('RGB')
    # check for existence of alpha channel based on length of pixel array
    hasAlpha = len(img.getpixel((0, 0))) == 4
    # iterate through all pixels in frame
    lines = []
    for y in range(img.size[1]):
        line = ""
        for x in range(img.size[0]):
            rgb = img.getpixel((x, y))
            if hasAlpha:
                hexColor = '%02x%02x%02x%02x' % rgb
            else:
                hexColor = '%02x%02x%02x' % rgb
            line += 'PX %d %d %s\n' % (x + offX, y + offY, hexColor)
        lines.append(line)
    return lines


if __name__ == "__main__":
    main(sys.argv[1])
