#!/usr/bin/env python

"""
Sender Class
Authors: Michael Patel, Surya Penumatcha
Copyright 2017
"""
import ctypes
import json
import threading
from socket import *
from defs import *
from time import sleep

class sender(object):

    def __init__(self, servers, serverPort, MSS):
        self.servers = servers # list of servers
        self.serverPort = int(serverPort)
        self.MSS = int(MSS)
        self.clientSocket = socket(AF_INET, SOCK_DGRAM)
        self.clientSocket.settimeout(TIMER)  # for recv side
        self.header = ""
        self.segment = "" # data segment, SAW protocol, so only 1 data segment at a time
        self.curSegSize = 0
        self.seqNum = ctypes.c_uint32()
        self.checkSum = ctypes.c_uint16()
        self.field = DATA_FIELD # default is 'data'
        self.endTimer = 0
        self.ACKs = {} # ACKs = {hostname1 : {'ack' : ack1}, hostname2 : {'ack' : ack2}}
        self.numOutstandingACKs = len(self.servers)
        self.recvField = ctypes.c_uint16() # received field used to check if rx an 'ACK_FIELD'
        
    def handshake(self):
        self.clientSocket.sendto("handshake", (self.serverName, self.serverPort))
        response, serverAddress = self.clientSocket.recvfrom(BUFFER_SIZE)
        print(str(serverAddress) + " is " + response)

    def rdt_send(self, byte, endFile=0):
        self.segment += byte # add current data byte to segment
        self.curSegSize += 1
        if(self.curSegSize == self.MSS or endFile == 1): # wait until have full data segment before tx
            if(endFile == 1):
                self.field = LAST_FIELD # indicates that is 'last'
            else:
                self.field = DATA_FIELD # indicates that is 'data'

            # Make packet
            self.make_packet()
            self.endTimer = 0 # initialize for first broadcast
            self.initACKs() # initialize such that have yet to receive ACK messages from servers
            thread = threading.Thread(target=self.send_start_timer, args=())
            thread.start()  # broadcast data segment
            #broadcastThread = threading.Timer(TIMER, self.broadcast)
            #broadcastThread.start()

            #self.broadcast()

            # End the timer since ACK received
            #self.endTimer = 1


            while(self.endTimer == 0):
                #self.broadcast()
                try:
                    #self.broadcast()
                    response, serverAddress = self.clientSocket.recvfrom(BUFFER_SIZE)  # response should be ACK from receiver
                    response = json.loads(response)
                    self.checkACKfromWho(response, serverAddress)
                    #sleep(TIMER)
                except:
                    print('\nTimeout, sequence number = ' + str(self.seqNum.value))
                    #sleep(TIMER)
                    continue
                #print('\nendtimer: ' + str(self.endTimer))
                #sleep(TIMER)

            #
            thread.join()
            # Reset segment values
            self.resetSegValues()
            #print('\ndone\n')


    def make_packet(self):
        self.checkSum.value = self.calculate_checksum()
        #print("SeqNum: " + str(self.seqNum.value) + " checkSum: " + str(self.checkSum.value) + " field: " + str(self.field))
        self.header = [self.seqNum.value, self.checkSum.value, self.field]

    def udt_send(self, address, port):
        packet = json.dumps({"header" : self.header, "data" : self.segment})
        self.clientSocket.sendto(packet.encode(), (address, port))

    def send_start_timer(self):
        while(self.endTimer == 0): # implementing SAW protocol, so 1 timer per tx data segment
            # Send packet
            #self.udt_send()
            self.broadcast()
            #response, serverAddress = self.clientSocket.recvfrom(BUFFER_SIZE)  # response should be ACK from receiver
            #self.checkACKfromWho(response.decode(), serverAddress)
            sleep(TIMER)

    def broadcast(self): # send out made data segment to only servers that have NOT_ACKED
        for i in range(len(self.servers)):
            if(self.ACKs[self.servers[i]]['ack'] == NOT_ACKED):
                self.udt_send(self.servers[i], self.serverPort) # tx data segment (serverPort is same for all servers)

    def initACKs(self):
        for i in range(len(self.servers)):
            self.servers[i] = str(self.servers[i]).upper() # convert hostnames to uppercase
            self.ACKs.update({self.servers[i] : {'ack' : NOT_ACKED}}) # initialize to NOT_ACKED

        self.numOutstandingACKs = len(self.servers)
        #print('\ninitial ACKs: ' + str(self.ACKs))

    def resetSegValues(self):
        self.header = ""
        self.segment = ""
        self.curSegSize = 0
        self.seqNum.value += 1
        self.endTimer = 0

    def checkACKfromWho(self, response, recvAddress):
        recvAddress = str(gethostbyaddr(recvAddress[0])[0]).upper() # translate rx IP address into hostname
        self.recvField = response[2] # should be 'ACK_FIELD' field value

        if(self.recvField == ACK_FIELD): # check if response is an 'ACK_FIELD'
            self.ACKs.update({recvAddress : {'ack' : ACKED}}) # update ack info for particular server
            #print('\nACKs: ' + str(self.ACKs))
            self.numOutstandingACKs -= 1 # decrement total number of outstanding ACKs
            #print('\nnumOutACKs: ' + str(self.numOutstandingACKs))
            if(self.numOutstandingACKs == 0): # check if have any remaining outstanding ACKs
                self.endTimer = 1 # rx all ACKs, so stop SAW timer
            else:
                self.endTimer = 0
        # if not ACK_FIELD, then do nothing

    def carry_around_add(self, a, b):
        c = a + b
        return (c & 0xffff) + (c >> 16)

    def calculate_checksum(self):
        s = 0
        for i in range(0, len(self.segment), 2):
            if (i + 1 < len(self.segment)):
                w = ord(self.segment[i]) + (ord(self.segment[i + 1]) << 8)
            else:
                w = ord(self.segment[i]) & 0x00ff
            s = self.carry_around_add(s, w)
        return ~s & 0xffff

    def close(self):
        packet = json.dumps({"header": "EMPTY", "data": "EMPTY"})
        self.clientSocket.sendto(packet, (self.serverName, self.serverPort))
        print("Finished")