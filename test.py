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
trdm.reset()
trdm.connect_tm()
trdm.utouto()
trdm.close()
