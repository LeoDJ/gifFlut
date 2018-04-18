#!/bin/python
import socket
import sys
import pickle
import os
import threading
import time

import gifToPF

renderOutputPath = "rendered/"
renderedFileSuffix = ".pkl"

reconnectInterval = 1


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


def sendData():
    while(running):
        for lineNum in range(len(frameBuffer[curFrame])):
            if running:
                try:
                    sock.sendall(frameBuffer[curFrame]
                                 [lineNum].encode("ascii"))
                except (ConnectionResetError, ConnectionAbortedError, OSError):
                    time.sleep(0.1)
                    connect()


def connect():
    global sock, lastTimeCalled
    if time.time() - lastTimeCalled >= reconnectInterval:
        lastTimeCalled = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((pxHost, int(pxPort)))
        except ConnectionRefusedError:
            print("Connection refused")


def main(host, port, imgPath, numThreads=1):
    global pxHost, pxPort, lastTimeCalled
    pxHost = host
    pxPort = port
    lastTimeCalled = 0

    if not os.path.exists(renderOutputPath):
        os.makedirs(renderOutputPath)

    data = getConvertedImage(imgPath)
    global frameBuffer, running, curFrame
    frameBuffer = data['frameBuffer']
    frameTime = data['duration']
    running = True
    curFrame = 0

    connect()

    threads = []
    for t in range(numThreads):
        thrd = threading.Thread(target=sendData)
        threads.append(thrd)
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
    main(sys.argv[1], sys.argv[2], sys.argv[3], 1)
