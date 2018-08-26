#!/usr/bin/env python

"""
P2MP Client
Authors: Michael Patel, Surya Penumatcha
Copyright 2017
"""
import sys
from defs import *
from sender import *
from datetime import  datetime
'''
6 commandline arguments:
0: server-1
1: server-2
2: server-3
3: ... (for i servers)
server-port number
filename
MSS
'''

class P2MPClient(object):
    def __init__(self):
        self.servers = [] # ['server-1 hostname', 'server-2 hostname', '...']
        self.serverPort = DEFAULT_PORT # server port number (well-known port number)
        self.recvPortnumber = False # boolean used to help parse commandline arguments
        self.fileName = '' # name of tx file
        self.MSS = DEFAULT_MSS

        if(len(sys.argv) < 5): # don't have enough input arguments
            sys.exit("\nERROR: Please provide at least 4 arguments: p2mpclient <server-i> <server port #> <filename> <MSS>\n")
        else: # have enough input arguments
            for i in range(1, len(sys.argv)):
                if(sys.argv[i].isdigit()): # check if input argument is a digit
                    if(not self.recvPortnumber): # check if already received server port input argument
                        self.serverPort = sys.argv[i]
                        self.recvPortnumber = True
                    else:
                        self.MSS = sys.argv[i]
                else: # input argument is not a digit
                    if(not self.recvPortnumber): # check if already received server port input argument
                        self.servers.append(sys.argv[i]) # add server-i to servers[]
                    else:
                        self.fileName = sys.argv[i]
                        if(not os.path.isfile(CURR_DIR + self.fileName)): # Verify the file provided exists
                            sys.exit("ERROR: File does not exist in: " + CURR_DIR)

# instantiate p2mpclient
client = P2MPClient()
print('\n#############################################\n')
print('\nservers: ' + str(client.servers))
for i in range(len(client.servers)):
    print('\nHostname: ' + str(gethostbyname(client.servers[i])))
print('\nserverPort: ' + str(client.serverPort))
print('\nfilename: ' + str(client.fileName))
print('\nMSS: ' + str(client.MSS))
print('\n#############################################\n')
#sys.exit('\nSTOP\n')

# instantiate sender
sender = sender(client.servers, client.serverPort, client.MSS)

'''
# Setup connection to the server (receiver)
serverName = 'localhost'
serverPort = 12000
client = sender(serverName, serverPort)
#client.handshake()
'''

# Read the file
with open(CURR_DIR + client.fileName, 'r') as dataFile:
    start = datetime.now()
    byte = dataFile.read(NUM_BYTES)
    while byte != "":
        sender.rdt_send(byte) # tx data to servers
        byte = dataFile.read(NUM_BYTES)
    sender.rdt_send("", 1)
    end = datetime.now()
    diff = end - start
    diff = diff.total_seconds()
    print('\nTotal time(s): ' + str(diff))
    print('\n')
# Perform closing operations
#client.close()
