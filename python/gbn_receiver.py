#!/usr/bin/env python3
import socket
from Message import Message
import time,threading
import _thread

"""
receiver for gbn
"""

class GbnReceiver:
    def __init__(self, packetSize=100, file_name = "output.txt"):
        self.file_name = file_name      # output file
        self.serverPort = 2345
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('127.0.0.1', self.serverPort))

        self.packetSize = packetSize    # size of payload in bytes
        self.cAck = 0                   # sequence number of next expected packet

    def run(self):
        try:
            f = open(self.file_name, "w+")
        except IOError:
            print("Unable to open file.")
            return
        try:
            while True:
                msg, addr = self.socket.recvfrom(2048)  # receive packet
                # print("received")
                msg = Message(messageBytes=msg)

                if msg.checksumValue != msg.calcChecksum(): # check for bit error
                    continue

                if msg.sequenceNumber == self.cAck:     # check if packet is expected next packet
                    # send ack if the packet is in order
                    rsp = Message(seqNum=msg.sequenceNumber, ackNum=self.cAck, payload=[])
                    #print("\tAcking: %d" % self.cAck)
                    self.socket.sendto(rsp.toBytes(), addr)
                    self.cAck += self.packetSize
                    if self.cAck >= 65536:  # loop sequence numbers around
                        self.cAck -= 65536

                    # deal with information received
                    data = msg.payload.decode('utf-8')
                    f.write(data)

                    # if acked packet has payload less than payloadSize, it is the last packet, and all packets have been received
                    if len(msg.payload) < self.packetSize:
                        f.close()
                        print("done at receiver")
                        break
                else:
                    # discard packet out of line and send cAck - 1 as ack
                    ackNum = self.cAck - self.packetSize
                    if ackNum < 0:
                        ackNum += 65536
                    rsp = Message(seqNum=msg.sequenceNumber, ackNum=ackNum, payload=[])
                    self.socket.sendto(rsp.toBytes(), addr)
        except KeyboardInterrupt:
            pass
        finally:
            f.close()
            self.socket.close()

