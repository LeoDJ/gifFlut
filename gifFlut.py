#!/bin/python
import socket
import sys
import pickle

import gifToPF

result = gifToPF.main(sys.argv[1])
print(len(result[0]), result[1])


# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.connect((sys.argv[1], int(sys.argv[2])))