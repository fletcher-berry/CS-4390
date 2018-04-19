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
        self.cAck = 0

    def run(self):
        try:
            f = open(self.file_name,"w")
        except IOError:
            print("Unable to open file.")
            return
        try:
            while True:
                msg, addr = self.socket.recvfrom(self.packetSize)
                msg = Message(messageBytes=msg)

                #if msg.checksumValue == msg.calcChecksum():
                #print("\tReceived : %d Expected : %d" % (msg.sequenceNumber, self.cAck))
                if msg.sequenceNumber == self.cAck:
                    # send ack if the packet is in order
                    rsp = Message(msg.sequenceNumber, self.cAck, [])
                    #print("\tAcking: %d" % self.cAck)
                    self.socket.sendto(rsp.toBytes(), addr)
                    self.cAck += 1

                    # deal with information received
                    data = msg.payload.decode('utf-8')
                    f.write(data)
                else:
                    # discard packet out of line and send cAck - 1 as ack
                    rsp = Message(msg.sequenceNumber,self.cAck-1,[])
                    self.socket.sendto(rsp.toBytes(), addr)
                #else: pass
        except KeyboardInterrupt:
            print()
        finally:
            f.close()
            self.socket.close()



