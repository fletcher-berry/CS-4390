from socket import socket, AF_INET, SOCK_DGRAM
import time
from Message import Message

"""
receiver for selective repeat.
"""


class SrReceiver:

    def __init__(self, windowSize, payloadSize):
        self.windowSize = windowSize * payloadSize # window size in bytes
        self.serverName = "127.0.0.1"
        self.serverPort = 2345
        self.serverSocket = socket(AF_INET, SOCK_DGRAM)
        self.serverSocket.bind(('', self.serverPort))
        self.windowBase = 0             # base of the receiver window
        self.payloadSize = payloadSize  # size of the payload in bytes
        self.buffer = {}                # map sequence number to message payload
        self.sentToApplication = []     # bytes sent to application layer
        self.endSequence = False        # whether last packet has been received



    # runs the receiver as a thread
    def run(self):
        while True:

            messageBytes, clientAddress = self.serverSocket.recvfrom(2048)  # receive packet

            message = Message(messageBytes=messageBytes)
            if message.checksumValue != message.calcChecksum():     # check for bit error
                continue

            # send ack regardless of whether received packet is duplicate
            ack = Message(seqNum=0, ackNum=message.sequenceNumber, payload=[])
            self.serverSocket.sendto(ack.toBytes(), clientAddress)

            # check if sequence number is in window, if not, do no further processing
            windowMax = self.windowBase + self.windowSize
            if windowMax < 65536:
                inWindow = self.windowBase <= message.sequenceNumber < windowMax
            else:
                inWindow = message.sequenceNumber >= self.windowBase or message.sequenceNumber < windowMax - 65536
            if not inWindow:
                continue

            # if payload is shorter than payload size, it is the last packet
            if len(message.payload) < self.payloadSize:
                self.endSequence = True

            # buffer the packet
            self.buffer[message.sequenceNumber] = message.payload
            if message.sequenceNumber == self.windowBase:
                self.updateBuffer()

            if self.endSequence and len(self.buffer) == 0:     # all packets received
                outFile = open("output.txt", "w+")          # write received data to file
                str1 = bytearray(self.sentToApplication).decode('utf-8')
                outFile.write(str1)
                outFile.close()
                print("done at receiver")
                #print(str1)
                break

    # slides window if next expected packet has been received
    def updateBuffer(self):
        while self.windowBase in self.buffer:   # first message in window has been received
            self.sentToApplication += self.buffer[self.windowBase]  # send to application layer
            del(self.buffer[self.windowBase])   # remove packet from buffer
            self.windowBase += self.payloadSize # update window
            if self.windowBase >= 65536:
                self.windowBase -= 65536


