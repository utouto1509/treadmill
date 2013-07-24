from scipy import *
from numpy import *
import scipy.io
import getopt
import sys
import time
import string
import struct
import socket
import traceback
import threading

import pytreadmill as tm

port="/dev/ttyS1"
trdm = tm.PyTreadmill(port)

count=1

class ThreadA(threading.Thread):
   	def __init__(self):
		threading.Thread.__init__(self)
		self.setDaemon(True)

	def run(self):
	   	global count
		while 1:
			count=count+1
			time.sleep(0.1)
			print count
		


class ThreadB(threading.Thread):
   	def __init__(self):
		threading.Thread.__init__(self)
		self.setDaemon(True)
	def run(self):
	   	global count
		while 1:
			if(count<50):
				msg='301010300000000000'
			if(count>=50 and count < 100):
				msg='301010500000000000'
			if(count>=100):
				msg='301010400000000000'

			trdm.utouto(msg)


def main():
	thA = ThreadA()
	thB = ThreadB()


	trdm.reset()
	trdm.connect_tm()
	
	thA.start()
	thB.start()
	   	
	time.sleep(20)

	trdm.close()

if __name__ == "__main__":
	main()
