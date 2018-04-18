#!/bin/python
import socket
import sys
import pickle
import os

import gifToPF

renderOutputPath = "rendered/"
renderedFileSuffix = ".pkl"


def saveConvertedImage(obj, filename):
    with open(filename, 'wb') as output:
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)


def loadConvertedImage(filename):
    with open(filename, 'rb') as input:
        return pickle.load(input)


def getConvertedImage(imgPath):
    # remove powershell autocomplete prefix
    if(imgPath.startswith('.\\')):
        imgPath = imgPath[2:]

    if imgPath.endswith(renderedFileSuffix):  # load cached file directly
        data = loadConvertedImage(imgPath)
    else:
        foundCachedImage = False
        # load cached version of file if exists
        for f in os.listdir(renderOutputPath):
            if(f.startswith(imgPath)):
                foundCachedImage = True
                print("Already found a converted image for \"" + imgPath +
                      "\". Using the cached version: " + renderOutputPath + f)
                print("If you do not want to load that file or update the cached version, simply delete the " +
                      renderedFileSuffix + " file.")
                data = loadConvertedImage(renderOutputPath + f)
                break
        if(not foundCachedImage):  # convert image, if no cached file exists
            data = gifToPF.main(imgPath)
            print("saving converted image... ", end='')
            saveConvertedImage(data, renderOutputPath +
                               imgPath + renderedFileSuffix)
            print("done.")

    return data




def main(host, port, imgPath):
    if not os.path.exists(renderOutputPath):
        os.makedirs(renderOutputPath)

    data = getConvertedImage(imgPath)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
