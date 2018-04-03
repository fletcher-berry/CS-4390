#!/usr/bin/env python3
import socket
import Message

class GbnSender:
    def __init__(self, windowSize, payloadSize, filePath):
        self.serverAddr = "127.0.0.1"
        self.serverPort = 2345
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.payloadSize = payloadSize
        self.filePath = filePath

        self.window = []        
        self.windowBase = 0
        self.windowSize = windowSize
        self.windowSizeBytes = windowSize * payloadSize

        self.retransmitted = 0

    def run(self):
        # retrieve x bytes from file and send 
        with open(self.filePath, "rb") as inputFile:
            pkt = inputFile.read(self.payloadSize)
            sendSeqNum = 1
            sendAckNum = 0
            while pkt:
                # if the window isn't full yet
                if seqNum + 1 < self.windowBase + self.windowSize:
                    seqNum = seqNum + 1

                    # package up into message and send to receiver
                    msg = Message(sendSeqNum, sendAckNum, pkt)
                    self.socket.sendTo(msg, (serverAddr, serverPort))

                    # Read more from file
                    pkt = inputFile.read(self.payloadSize)
                    self.window.append(pkt)

                # look for an ACK to further along the window
                else:
                    msgBytes, Addr = self.socket.recvFrom(2048)
                    msg = Message(msgBytes)

                    # successfully received uncorrupted packet
                    if msg.checksumValue == msg.calcChecksum():
                        ReceivedSeqNum = msg.ackNum
                        # move window base along, remove packet from front
                        self.windowBase = self.WindowBase + 1
                        del self.window[0]
                    
                # probably put timeout here

