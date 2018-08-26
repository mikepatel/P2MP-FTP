#!/usr/bin/env python

"""
Receiver Class
Authors: Michael Patel, Surya Penumatcha
Copyright 2017
"""
import ctypes
import json
import base64
from socket import *
from defs import *
import random
import sys

class receiver(object):

    """
    Initialize receiver
    Arguments:
    1. hostName: The current host where server is started
    2. serverPort: The port number where the server is listening
    Returns: None
    """            
    def __init__(self, hostName, serverPort, filename, p):
        self.hostName = hostName
        self.serverPort = int(serverPort)
        self.filename = filename
        self.p = float(p)
        self.serverSocket = socket(AF_INET, SOCK_DGRAM)
        self.serverSocket.bind((self.hostName, self.serverPort))
        self.serverSeqNum = ctypes.c_uint32() # expected SN
        self.field = ACK_FIELD  # default is 'ACK'
           
    """
    Listen for incoming packets
    Arguments: None
    Returns: None
    """        
    def listen(self):
        print("\nUDP Server is listening...\n")
        while True:
            packet, clientAddress = self.serverSocket.recvfrom(BUFFER_SIZE)
            packet = json.loads(packet)
            header = packet["header"]
            # Header: [seqNum, checkSum, field]
            seqNum = ctypes.c_uint32(header[0])
            #print('incoming SN: ' + str(seqNum.value))
            #print('expected SN: ' + str(self.serverSeqNum.value))

            if(self.getRndValue() > self.p): # accept packet
                if(self.serverSeqNum.value == seqNum.value): # check if expected SN is same as rx SN
                    checkSum = ctypes.c_uint16(header[1])
                    field = ctypes.c_uint16(header[2])
                    # print("SeqNum: " + str(seqNum.value) + " checkSum: " + str(checkSum.value) + " field: " + str(field.value))
                    data = packet['data']
                    calCheckSum = self.calculate_checksum(data)
                    # print("ch: " + str(checkSum.value) + " cal: " + str(calCheckSum))
                    if (checkSum.value == calCheckSum): # Valid checksum
                        # Send ACK
                        reply = json.dumps(self.makeACKsegment(seqNum))
                        self.serverSocket.sendto(reply.encode(), clientAddress)
                        # Save Data
                        self.write(data)
                        self.serverSeqNum.value += 1

                        if(field.value == LAST_FIELD):
                            sys.exit('\n') # terminate server process once done
                        # else field == DATA_FIELD, so continue server process
                    # do nothing if checksum is invalid

                else: # reply with last received in-sequence ACK
                    print('\nOut-of-order arrival: Replying with last in-sequence ACK' + str(self.serverSeqNum.value - 1))
                    reply = ACK_MSG + str(self.serverSeqNum.value) # reply with expected SN
                    self.serverSocket.sendto(reply.encode(), clientAddress)

            else: # discard packet (do nothing)
                print('\nPacket loss, sequence number = ' + str(seqNum.value)) # incoming packet that was discarded
            
    def write(self, data):
        f = open(self.filename, "a+")
        f.write(data)
        f.close()
                    
    def carry_around_add(self, a, b):
        c = a + b
        return (c & 0xffff) + (c >> 16)

    def calculate_checksum(self, segment):
        s = 0
        for i in range(0, len(segment), 2):
            if(i+1 < len(segment)):
                w = ord(segment[i]) + (ord(segment[i+1]) << 8)
            else:
                w = ord(segment[i]) & 0x00ff
            s = self.carry_around_add(s, w)
        return ~s & 0xffff

    def getRndValue(self):
        value = random.uniform(0, 1)
        return value

    def makeACKsegment(self, SN):
        segment = [SN.value, ZEROES, ACK_FIELD] # [32-bits SN, 16-bits all zeroes, 16-bit ACK_FIELD]
        return segment
    """
    Perform closing functions
    Arguments: None
    Returns: None
    """
    #def close(self):
