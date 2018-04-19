
import threading
from socket import socket, AF_INET, SOCK_DGRAM
#from _thread import
#from threading import Semaphore
import random

import _thread

import time

from Message import Message



class SrSender:

    def __init__(self, windowSize, payloadSize, filePath):
        self.windowSize = windowSize * payloadSize  # window size in bytes
        self.serverName = "127.0.0.1"
        self.serverPort = 2345
        self.clientPort = 2346
        self.clientSocket = socket(AF_INET, SOCK_DGRAM)
        self.clientSocket.bind(('', self.clientPort))
        self.payloadSize = payloadSize
        self.windowBase = 0
        self.file = open(filePath, "r")
        self.doneReading = False  # whether or not end of file to transmit has been seen
        self.window = {}  # maps sequence number to bytes of message (including header)
        self.messageQueue = []  # array of messages to send
        self.queueUse = threading.Semaphore(1)
        self.nextSequenceNumber = 0
        self.numRetransmits = 0
        self.getMoreData()
        self.timeoutInterval = 0.1



    def run(self):
        self.startTime = time.time()
        _thread.start_new_thread(self.sendFunc, ())
        _thread.start_new_thread(self.receiveFunc, ())

    def sendFunc(self):
        while True:
            if len(self.messageQueue) > 0:

                self.queueUse.acquire()

                message = self.messageQueue[0]
                del (self.messageQueue[0])
                seqNum = message.sequenceNumber
                bytes = message.toBytes()

                self.queueUse.release()
                timer = threading.Timer(self.timeoutInterval, self.timeout, [seqNum])
                #print("start", float(time.time() - self.startTime))
                timer.start()
                #print("end", float(time.time() - self.startTime))

                # if(random.randint(0, 10) != 2):
                #     self.clientSocket.sendto(bytes, (self.serverName, self.serverPort))

                self.clientSocket.sendto(bytes, (self.serverName, self.serverPort))


    def receiveFunc(self):
        while True:
            messageBytes, serverAddress = self.clientSocket.recvfrom(1024)
            message = Message(messageBytes=messageBytes)
            if message.checksumValue == message.calcChecksum():
                ackNum = message.acknowledgmentNumber
                if ackNum in self.window:
                    self.queueUse.acquire()
                    del (self.window[ackNum])
                    self.queueUse.release()
                else:
                    print("duplicate ack")
                if (ackNum == self.windowBase):
                    self.getMoreData()
                if self.doneReading and len(self.window) == 0:
                    print("done at sender")
                    print("time:", float(time.time() - self.startTime))
                    print("num retransmits:", self.numRetransmits)

    def timeout(self, sequenceNumber):

        if sequenceNumber in self.window:
            print("timeout")
            self.queueUse.acquire()
            # have to check again b/c she sequence number may have been taken out of the window by another thread
            # I could place the acquire() outside the if, but that would require a lock every time timeout() is called
            if(sequenceNumber in self.window):  # have to check a
                self.numRetransmits += 1
            #print(self.window)
                print("retransmitting", sequenceNumber)
                retransmitMessage = Message(messageBytes=self.window[sequenceNumber])
                self.messageQueue.insert(0, retransmitMessage)
                timer = threading.Timer(self.timeoutInterval, self.timeout, [retransmitMessage.sequenceNumber])
                timer.start()
            self.queueUse.release()



    # read file to fill window if window is not full
    def getMoreData(self):
        if self.doneReading:
            return
        nextToRead = self.nextSequenceNumber  # all packets up to this point have been stored in window
        # find smallest sequence number in window
        wrap = self.windowBase + self.windowSize >= 65536
        nextNotReceived = 1000000
        for val in self.window:
            seqNum = val
            if wrap and seqNum < self.windowBase + self.windowSize:
                seqNum += 65536
            if seqNum < nextNotReceived:
                nextNotReceived = seqNum
        if nextNotReceived >= 65536:
            nextNotReceived -= 65536
        self.windowBase = self.nextSequenceNumber if nextNotReceived >= 100000 else nextNotReceived
        max = self.windowBase + self.windowSize


        # read from the file to fill the unused window
        while nextToRead + self.payloadSize <= max or nextToRead + self.payloadSize - 32000 > max:
            newBytes = bytearray(self.file.read(self.payloadSize), 'utf-8')

            self.queueUse.acquire()
            packet = Message(seqNum=nextToRead, payload=newBytes)
            self.window[nextToRead] = packet.toBytes()
            self.messageQueue.append(packet)
            self.queueUse.release()
            nextToRead += self.payloadSize
            if nextToRead >= 65536:
                nextToRead -= 65536
            if len(newBytes) < self.payloadSize:  # last packet
                self.doneReading = True
                self.file.close()
                break
        self.nextSequenceNumber = nextToRead


