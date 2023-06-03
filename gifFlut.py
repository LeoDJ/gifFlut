#!/bin/python

################## GIF to Pixelflut sender ########################
#
# Author: LeoDJ
# Repository: https://github.com/LeoDJ/gifFlut
#
# Compliant with Pixelflut servers from defnull (https://github.com/defnull/pixelflut)
#
# ToDo:
#   - find out why PILlow fucks up some .GIF files
#   - improve performance of data sending (if necessary)
#   - OPTIONAL: improve performance of image conversion
#
###################################################################

import socket
import sys
import pickle
import os
import threading
import time
import lzma
import ntpath
import argparse

import gifToPF


renderOutputPath = "rendered/"
renderedFileSuffix = ".pkl"
renderedFileSuffixCompr = ".pklz"

reconnectInterval = 0.1


# appends file extension based on compression
def saveConvertedImage(obj, filename, compressed=True):
    if not os.path.exists(renderOutputPath):
        os.makedirs(renderOutputPath)

    if compressed:
        filename += renderedFileSuffixCompr
    else:
        filename += renderedFileSuffix

    with open(filename, 'wb') as output:
        if(compressed):
            with lzma.LZMAFile(output, "w", filters=[{'id': lzma.FILTER_LZMA2, 'preset': 1}]) as lzf:
                lzf.write(pickle.dumps(obj, pickle.HIGHEST_PROTOCOL))
        else:
            pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)


def loadConvertedImage(filename):
    compressed = filename.endswith(renderedFileSuffixCompr)
    with open(filename, 'rb') as input:
        if(compressed):
            with lzma.LZMAFile(input, "r") as lzf:
                return pickle.loads(lzf.read())
        else:
            return pickle.load(input)


def getConvertedImage(imgPath, xoff=0, yoff=0, compr=True, regen=False, noCache=False, algo=0):
    imgFileName = ntpath.basename(imgPath)

    # load cached file directly
    if imgFileName.endswith(renderedFileSuffix) or imgFileName.endswith(renderedFileSuffixCompr):
        data = loadConvertedImage(imgPath)
    else:
        foundCachedImage = False
        # load cached version of file if exists
        for f in os.listdir(renderOutputPath):
            if(f.startswith(imgFileName)):
                foundCachedImage = True
                cachedFile = f
                break
        if(not foundCachedImage or regen):  # convert image, if no cached file exists
            data = gifToPF.main(imgPath, xoff, yoff, algo)
            if not noCache:
                print("saving converted image... ")
                saveConvertedImage(data, renderOutputPath + imgFileName, compr)
                print("done.")
        else:
            print("Already found a converted image for \"" + imgFileName +
                  "\". Using the cached version: " + renderOutputPath + cachedFile)
            print(
                "If you do not want to load the cached file, simply set the regeneration parameter \"-r\"")
            print("Loading cached file...")
            data = loadConvertedImage(renderOutputPath + cachedFile)
            print("done.")

    return data


def sendData(part=0, numParts=1):
    frameLen = len(frameBuffer[curFrame])
    partLen = int(frameLen / numParts)
    partStart = part * partLen
    partEnd = partStart + partLen - 1
    if part == numParts - 1: ##last frame must be handled extra
        partEnd += (frameLen % numParts)
    # print(frameLen, partLen, partStart, partEnd)
    while(running):
        for lineNum in range(partStart, partEnd + 1):
            if running:
                try:
                    sock[part].sendall(frameBuffer[curFrame]
                                 [lineNum].encode("ascii"))
                except (ConnectionResetError, ConnectionAbortedError, OSError, NameError, IndexError, TimeoutError):
                    time.sleep(0.1)
                    connect(part)


def connect(socketId=0):
    global sock, lastTimeCalled, currentlyConnecting
    # prevent multiple reconnects from threads and also do reconnect interval timing
    if time.time() - lastTimeCalled >= reconnectInterval or not currentlyConnecting:
        currentlyConnecting = True
        lastTimeCalled = time.time()
        if pxHost.count(":") < 2:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.insert(socketId, s)
        try:
            print("connect " + str(socketId))
            if pxHost.count(":") < 2:
                sock[socketId].connect((pxHost, int(pxPort)))
            else:
                sock[socketId].connect((pxHost, int(pxPort), 0, 0))
            currentlyConnecting = False
        except (ConnectionRefusedError, TimeoutError):
            print("Connection refused")
            currentlyConnecting = False
        except socket.gaierror as e:
            print("Socket error", e, e.reason)
            currentlyConnecting = False



def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("host")
    parser.add_argument("port", type=int)
    parser.add_argument("imageFile")

    parser.add_argument("-x", "--xoffset", type=int, default=0)
    parser.add_argument("-y", "--yoffset", type=int, default=0)
    parser.add_argument("-t", "--threads", type=int, default=1,
                        help="number of threads for data sending")
    parser.add_argument("-u", "--nocompression", action='store_const', const=True,
                        default=False, help="save cache file uncompressed")
    parser.add_argument("-r", "--regenerate", action='store_const', const=True,
                        default=False, help="overwrite cached file")
    parser.add_argument("-n", "--nocache", action='store_const', const=True,
                        default=False, help="disable writing cache file")
    parser.add_argument("-a", "--algorithm", type=int, default=0,
                        help="algorithm selection 0=lineByLine, 1=randomPixel")

    args = parser.parse_args()
    return args


def main():
    args = parseArgs()

    global pxHost, pxPort, lastTimeCalled, sock, currentlyConnecting
    pxHost = args.host
    pxPort = args.port
    lastTimeCalled = 0
    sock = []
    currentlyConnecting = False

    global frameBuffer, running, curFrame
    data = getConvertedImage(args.imageFile, args.xoffset, args.yoffset,
                             not args.nocompression, args.regenerate, args.nocache, args.algorithm)
    frameBuffer = data['frameBuffer']
    frameTime = data['duration']
    running = True
    curFrame = 0

    threads = []
    for t in range(args.threads):
        thrd = threading.Thread(target=sendData, args=(t, args.threads))
        threads.append(thrd)
        time.sleep(0.15)
        thrd.start()

    try:
        while(running):
            if(frameTime > 0):
                i = curFrame + 1
                # safely increment curFrame, because is global and might cause out of bounds exception if read at the wrong time
                if i >= len(frameBuffer):
                    i = 0
                curFrame = i
                time.sleep(frameTime / 1000)

    except KeyboardInterrupt:
        running = False
        print("stopping...")


if __name__ == "__main__":
    main()
