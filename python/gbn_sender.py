#!/usr/bin/env python3
import socket
from Message import Message
import time
from threading import Timer

class GbnSender:
    def __init__(self, windowSize, filePath):
        self.serverAddr = "127.0.0.1"
        self.serverPort = 2345
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.filePath = filePath
        self.payLoadSize = 10
        self.packetTimers = {}
        self.window = []
        self.windowBase = 0
        self.windowSize = windowSize
        self.windowSizeBytes = windowSize * self.payLoadSize

        self.retransmitted = 0

    def transmit_packet(self, packet):
        print('Send: %s', packet.toBytes())
        self.socket.sendto(packet.toBytes(), (self.serverAddr, self.serverPort))

    def packet_timeout(self, packet):
        print("I have timed oout")
        #self.transmit_packet(packet)

    def run(self):
        print("Starting up...")
        time.sleep(1)
        # retrieve x bytes from file and send 
        with open(self.filePath, "rb") as inputFile:
            pkt = inputFile.read(self.payLoadSize)
            seqNum = 0
            ackNum = 0
            while pkt:
                # if the window isn't full yet
                if seqNum + 1 <= self.windowBase + self.windowSize:
                    seqNum = seqNum + 1

                    # package up into message and send to receiver
                    msg = Message(seqNum  = seqNum,
                                  ackNum  = ackNum,
                                  payload = pkt )
                    self.transmit_packet(msg)

                    # Read more from file
                    pkt = inputFile.read(self.payLoadSize)
                    self.window.append(pkt)

                    # Set new packet timer with ID ack
                    self.packetTimers[ackNum] = Timer(0.1, self.packet_timeout, ackNum, pkt)

                # look for an ACK to further along the window
                else:
                    msgBytes, Addr = self.socket.recvfrom(2048)
                    msg = Message.setMessage(msgBytes)

                    # successfully received uncorrupted packet
                    if msg.checksumValue == msg.calcChecksum():
                        # move window base along, remove packet from front
                        # and remove timer for packet
                        del self.packetTimers[msg.ReceivedAckNum]
                        self.windowBase = self.WindowBase + 1
                        del self.window[0]

# Dummy receiver class to test sender 
class GbnReceiver:
    def __init__(self, windowSize):
        self.serverAddr = "127.0.0.1"
        self.serverPort = 2345
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.payLoadSize = 10
        self.cumulativeAck = 0
        self.window = []
        self.windowBase = 0
        self.windowSize = windowSize
        self.windowSizeBytes = windowSize * self.payLoadSize

    def run(self):
        # receive
        print("Starting up...")
        self.socket.bind((self.serverAddr, self.serverPort))
        time.sleep(1)
        while True:
            print(" I am waiting on packets... ")
            msgBytes, Addr = self.socket.recvfrom(2048)
            #msg = Message.fromBytes(msgBytes)
            print('Received: %s', msgBytes)

            msgBytes, clientAddress = self.socket.recvfrom(2048)
            msg = Message(messageBytes=msgBytes)

            if msg.checksumValue == msg.calcChecksum():
                if msg.acknowledgmentNumber == (self.cumulativeAck + 1):
                    ReceivedAckNum = msg.acknowledgmentNumber
                    ReceivedSeqNum = msg.sequenceNumber

                    # send acknowledgement if the packet 
                    msg = Message(ReceivedSeqNum, ReceivedAckNum+1, pkt)
                    print('Received: %s', msg.payload)

                    self.socket.sendto(msg, (self.serverAddr, self.serverPort))

                else:
                    # discard packet out of line
                    print('Message discarded, out of order...')
                    pass

            time.sleep(1)





