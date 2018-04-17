#!/usr/bin/env python3
import socket
from Message import Message
import time,threading
import _thread

class GbnReceiver:
    def __init__(self, packetSize=100, file_name = "output.txt"):
        self.file_name = file_name

        self.serverPort = 2346
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('127.0.0.1', self.serverPort))

        self.packetSize = packetSize
        self.cumulativeAck = 0

    def run(self):
        try:
            f = open(self.file_name,"w")
        except IOError:
            print("Unable to open file.")
            return

        while True:
            msg, addr = self.socket.recvfrom(self.packetSize)
            msg = Message(messageBytes=msg)

            #if msg.checksumValue == msg.calcChecksum():
            #print("\tReceiving %d : %s" % (msg.sequenceNumber, str(msgBytes)))
            if msg.sequenceNumber == self.cumulativeAck:
                # deal with information received
                data = msg.payload.decode('utf-8')
                f.write(data)
                #print(data.encode('unicode_escape').decode('utf-8'), file=f)

                # send ack if the packet is in order
                rsp = Message(msg.sequenceNumber, self.cumulativeAck, [])
                #print("\tAcking: %d" % self.cumulativeAck)
                self.socket.sendto(rsp.toBytes(), addr)
                self.cumulativeAck += 1
            else:
                # discard packet out of line and send cumulative - 1 as ack
                #print("\tAcking: %d" % self.cumulativeAck-1)
                response = Message(msg.sequenceNumber,self.cumulativeAck-1,[])
                self.socket.send(response.toBytes(), sock, addr)
        self.socket.close()



