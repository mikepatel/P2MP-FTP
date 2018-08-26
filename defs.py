#!/usr/bin/env python

"""
Definitions
Authors: Michael Patel, Surya Penumatcha
Copyright 2017
"""

import os

DEFAULT_MSS = 4096
BUFFER_SIZE = 8192
NUM_BYTES = 1
ACK_MSG = "ACK"
CURR_DIR = os.getcwd() + '/'
TIMER = 0.100
DEFAULT_PORT = 65450 # NCSU only allows ports 65400 to 65500
ACKED = True
NOT_ACKED = False
ACK_FIELD = int('1010101010101010', 2)
DATA_FIELD = int('0101010101010101', 2)
LAST_FIELD = int('1100110011001100', 2)
ZEROES = int('0000000000000000', 2)

