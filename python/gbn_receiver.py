#!/usr/bin/env python3
import socket
from Message import Message
import time,threading
import _thread

class GbnReceiver:
    def __init__(self, packetSize=100, file_name = "output.txt"):
        self.file_name = file_name

        self.serverPort = 2345
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('127.0.0.1', self.serverPort))

        self.packetSize = packetSize
        self.cAck = 0

    def run(self):
        #try:
        f = open("output.txt", "w+")
        #except IOError:
            #print("Unable to open file.")
            #return
        try:
            while True:
                msg, addr = self.socket.recvfrom(2048)
                # print("received")
                msg = Message(messageBytes=msg)

                if msg.checksumValue != msg.calcChecksum(): # check for bit error
                    continue

                if msg.sequenceNumber == self.cAck:
                    # send ack if the packet is in order
                    rsp = Message(seqNum=msg.sequenceNumber, ackNum=self.cAck, payload=[])
                    print("\tAcking: %d" % self.cAck)
                    self.socket.sendto(rsp.toBytes(), addr)
                    self.cAck += self.packetSize

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
                    rsp = Message(seqNum=msg.sequenceNumber, ackNum=self.cAck - self.packetSize, payload=[])
                    self.socket.sendto(rsp.toBytes(), addr)
                #else: pass
        except KeyboardInterrupt:
            pass
        finally:
            f.close()
            self.socket.close()

