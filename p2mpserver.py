#!/usr/bin/env python

"""
P2MP Server
Authors: Michael Patel, Surya Penumatcha
Copyright 2017
"""
import sys
from receiver import *
from defs import *

class P2MPServer(object):
    def __init__(self):
        self.hostname = gethostname()
        self.portnumber = DEFAULT_PORT # server port number (well-known port number)
        self.filename = '' # name of written file
        self.p = 0 # packet loss probability

        if(len(sys.argv) != 4): # incorrect number of input arguments
            sys.exit("\nERROR: Please provide 3 arguments: p2mpserver <server port #> <filename> <packet loss probability>\n")

        else: # correct number of input arguments
            self.portnumber = sys.argv[1]
            self.filename = sys.argv[2]
            self.p = float(sys.argv[3])
            if( self.p<0 or self.p>1 ):
                sys.exit('\nERROR: packet loss probability must be [0,1]\n')

# instantiate p2mpserver
server = P2MPServer()
print('\n#############################################\n')
print('\nHostname: ' + str(server.hostname))
print('\nIP address: ' + str(gethostbyname(server.hostname)))
print('\nPort number: ' + str(server.portnumber))
print('\nFilename: ' + str(server.filename))
print('\nPacket Loss Probability: ' + str(server.p))
print('\n#############################################\n')
#sys.exit('\nSTOP\n')

# Create UDP Socket
rcv = receiver(server.hostname, server.portnumber, server.filename, server.p)
rcv.listen()