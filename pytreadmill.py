#!/usr/bin/env python
# encoding: utf-8
"""
pytreadmill.py

Created by Tomoyuki Noda on 2013-07-02.
Copyright (c) 2013 . All rights reserved.
"""

import sys
import getopt
from serial import Serial
import struct
import time
import numpy as np 
import scipy.io 

help_message = '''
The help message goes here.
'''
ACK = '\x06'
ENQ = '\x05'
NAK = '\x15'
EOT = '\x04'
STX = '\x02'

class PyTreadmill():
	def __init__(self, port=0,baudrate=9600):
		self.com = Serial(port=port,
					 baudrate=baudrate,
					 bytesize=8,
					 parity='N',
					 stopbits=1,
					 timeout=1,
				  #timeout=0,
				  )
		self.com.flushInput()
		self.com.flushOutput()
		self.strPort =  self.com.portstr
		formats = {
			# '\xCE':{'data_format':'>cfffIH', 'readlen':19, 'printfmt':'0x%02x %3.3f %3.3f %3.3f %3.3f %04x\r'},
			# '\xCF':{'data_format':'>cffffffIH', 'readlen':31, 'printfmt':'0x%02x %3.3f %3.3f %3.3f %3.3f %3.3f %3.3f %3.3f %04x\r'},
			}
		# try:
		# 	xmls = formats[request]
		# 	self.request = request
                # except:
		# 	xmls = formats['\xCE']
		# 	self.request = request

		# self.data_format =  xmls['data_format']
		# self.readlen =  xmls['readlen']
		# self.printfmt =  xmls['printfmt']

		# #  Generate  init data (into dcd)
		# self.dummy_data =  struct.pack('>'+'b'*self.readlen,*np.zeros(self.readlen))
		# self.dcd = list(struct.unpack(self.data_format, self.dummy_data) )
		# self.error = False
	def calc_bcc(self,x):
	   	"""
		BCC calculation 
		input  x  : str size(str) = 18 byte (except space)
		output bcc_h : str size(str)=1byte
		       bcc_l : str size(str)=1byte
		"""
		checksum= 0
		for x1 in x:
			checksum=checksum+int(ord(x1))
		# add ETX
		checksum=checksum+int(0x03) 

		#print hex(checksum)
		bcc=hex(checksum)
		bcc_l = bcc[len(bcc)-1:]
		bcc_h = bcc[len(bcc)-2:len(bcc)-1]

		str2hex = {'0':'0','1':'1','2':'2','3':'3','4':'4','5':'5',\
		      '6':'6','7':'7','8':'8','9':'9','a':':','b':';',\
		      'c':'<','d':'=','e':'>','f':'?'}

		bcc_h = str2hex[bcc_h]
		bcc_l = str2hex[bcc_l]
		
		
		return bcc_h,bcc_l
	def make_transmit_message(self,msg):
		"""
		make message
		input  msg    : size(str) = 18byte (except space)
		output result : size(str) = 22byte
		"""

		h,l=self.calc_bcc(msg)
		# STX 0 00 00 000 000 0000 000 ETX BCC(H) BCC(L)
		result = '\x02'+msg+'\x03'+h+l
		return result

	def message_transmission(self,msg):
		"""
		send to Treadmill due to serial cable
		input msg    : size(str) = 22byte
		"""
		for word in msg:
			print word,
			res_write = self.com.write(word)
	
	def ack_check_from_tm(self,word):
		if(word[0]==ACK):# type(word) = tuple
			print "ok!"
		else:
			print "bad!!"

	def connect_tm(self):
		"""
		Open line to communicate to treadmill (see section 5 in doc)
		 ENQ-->
		   <--ACK read
		 init control msg-->
		   <--ACK read 
		   <--init control msg read 
		 ACK-->  
		"""
		
		# ENQ-->
		print "writing..."
		res_write = self.com.write(ENQ)	 # 0x05 --> ENQ
		print "done ,",res_write

		#   <--ACK read
		print "reading..."
		res_read = self.com.read(1)
		dat = struct.unpack("c", res_read)
		print "dat = ", dat
		self.ack_check_from_tm(dat)
		print "done"
		
		# init control msg-->
		#msg = '0 00 00 000 000 0000 000'
		msg = '000000000000000000'
		msg = self.make_transmit_message(msg)
		print "writing..."
		self.message_transmission(msg)
		print "done"
		
		#   <--ACK read 
		print "reading..."
		res_read = self.com.read(1)
		dat = struct.unpack("c", res_read)
		print "dat = ", dat
		self.ack_check_from_tm(dat)
		print "done"
		

		#   <--init control msg read 
		for count in range(21):
			res_read = self.com.read(1)
			dat = struct.unpack("c",res_read)
			print dat,
		print "done"
		
		# ACK-->  
		print "writing..."
		res_write = self.com.write(ACK)	 # 0x06 --> ACK
		print "done"

		print "connection comp"

		pass

	def utouto(self):
		"""
		Open line to communicate to treadmill (see section 5 in doc)
		   <--msg read
		 ACK msg-->
		 control msg-->
		   <--ACK read 
		"""
		#   <--msg read
		res_read = self.com.read(1)
		for count in range(22):
			res_read = self.com.read(1)
			dat = struct.unpack("c",res_read)
			print dat,
		print "done"
		
		# ACK msg-->
		print "writing..."
		res_write = self.com.write(ACK)	 # 0x06 --> ACK
		print "done"

		# control msg-->
		#msg = '3 01 01 050 150 0000 000'
		msg = '301010501500000000'
		#msg = '3 01 01 030 000 0000 000'
		msg = '301010300000000000'
		msg = self.make_transmit_message(msg)
		print "writing..."
		self.message_transmission(msg)
		print "done"
		
		#   <--ACK read 
		print "reading..."
		res_read = self.com.read(1)
		dat = struct.unpack("c", res_read)
		print "dat = ", dat
		self.ack_check_from_tm(dat)
		print "done"


		pass
		
	def reset(self):
		self.com.flushInput()
		self.com.flushOutput()

	def close(self):
		"""docstring for close"""
		self.com.close()
		
	def ReadData(self):
		"""
		ReadData: 

		"""
		# if self.com.inWaiting() == self.readlen:
		# 	res_read = self.com.read(self.readlen)
		# else:
		# 	return None, 0
		# # Big edian format
		# if self.readlen != len(res_read):
		# 	print res_read
		# 	self.error = True
		# 	#print struct.unpack(self.data_format[0:-1], res_read[0:-2])
		# 	return None, res_read
		# else:
		# 	self.dcd=list(struct.unpack(self.data_format, res_read))
		# 	#self.dcd[-2] = self.dcd[-2]/19660800.0;
		# 	return self.dcd, res_read

class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg


def main(argv=None, exptime=2, freq_ctrl= 25 ):
	# init flags
	
	port = "/dev/ttyUSB0"
	port = "/dev/ttyS1"
	
	# get options
	if argv is None:
		argv = sys.argv
	try:
		try:
			opts, args = getopt.getopt(argv[1:], "ho:p:", ["help", "output=", "port"])
		except getopt.error, msg:
			raise Usage(msg)
	
		# option processing

		for option, value in opts:
			if option == "-v":
				verbose = True
			if option in ("-h", "--help"):
				raise Usage(help_message)
			if option in ("-o", "--output"):
				output = value
			if option in ("-p", "--port"):
				port = value
	
	except Usage, err:
		print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
		print >> sys.stderr, "\t for help use --help"
		return 2

	trdm = PyTreadmill(port=port )
	trdm.reset()
	trdm.connect_tm()
	trdm.utouto()
	trdm.close()
	#return results

if __name__ == "__main__":
	results = main()

