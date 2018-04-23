
import threading
from socket import socket, AF_INET, SOCK_DGRAM
#from _thread import
from threading import Thread
import random
import _thread
import time
from Message import Message

"""
Sender for both GBN and selective repeat.  A single class is used for the sender because both senders
share some common functionality, such as threading
"""


class Sender:

    def __init__(self, windowSize, payloadSize, filePath, GBN=False):
        self.windowSize = windowSize * payloadSize  # window size in bytes
        self.serverName = "127.0.0.1"
        self.serverPort = 2345
        self.clientPort = 2346          # the client must run on a specific port so it can receive ACKs
        self.clientSocket = socket(AF_INET, SOCK_DGRAM)
        self.clientSocket.bind(('', self.clientPort))
        self.payloadSize = payloadSize      # number of bytes of the payload
        self.windowBase = 0                 # the starting window base
        self.file = open(filePath, "r")     # the input file
        self.doneReading = False  # whether or not end of file to transmit has been seen
        self.window = {}  # maps sequence number to bytes of message (including header)
        self.messageQueue = []  # array of message objects to send
        self.queueUse = threading.Semaphore(1)  # used to enforce mutual exclusion on window and messageQueue
        self.nextSequenceNumber = 0             # the sequence number of the first unACKed packet
        self.numRetransmits = 0                 # number of retransmits
        self.GBN = GBN                          # boolean for whether GBN is used

        self.getMoreData()
        self.timeoutInterval = 0.1


    # starts the send and receive ack threads
    def run(self):
        self.startTime = time.time()
        _thread.start_new_thread(self.sendFunc, ())
        _thread.start_new_thread(self.receiveFunc, ())

    # continuously sends pending packets, run as a thread
    def sendFunc(self):
        while True:
            if len(self.messageQueue) > 0:
                self.queueUse.acquire()     # prevent other threads from accessing messageQueue
                message = self.messageQueue[0]  # retrieve and remove packet at head of queue
                del (self.messageQueue[0])
                seqNum = message.sequenceNumber
                messageBytes = message.toBytes()
                # if gbn, only start timer if packet is first in window
                startTimer = True
                if self.GBN:
                    for x in self.window:
                        if x < seqNum and x + 50000 > seqNum:   # 2nd condition handles cycling of sequence numbers
                            startTimer = False
                # if(seqNum == 0):
                #     print("working?", startTimer)
                self.queueUse.release()
                # timer is started after queueUse.release() b/c it sometimes takes a long time to start
                if startTimer:
                    timer = threading.Timer(self.timeoutInterval, self.timeout, [seqNum])
                    #print("start", float(time.time() - self.startTime))
                    timer.start()
                    #print("end", float(time.time() - self.startTime))

                self.maybeSend(messageBytes, (self.serverName, self.serverPort), num=message.sequenceNumber)

                #self.clientSocket.sendto(messageBytes, (self.serverName, self.serverPort))

    # used for testing proposes.  Emulates packet loss and delay
    def maybeSend(self, mbytes, serv, num=0):
        DROP_CHANCE = 0.03   # chance of loss
        PING_MIN = 0.01     # min and max delay values in seconds
        PING_MAX = 0.04
        drop = (random.random() <= DROP_CHANCE)
        if not drop:
            ping = random.uniform(PING_MIN, PING_MAX)
            timer = threading.Timer(ping, self.clientSocket.sendto,
                [mbytes, serv])
            self.clientSocket.sendto(mbytes, serv)
        else:
            print("Dropping ", num)

    # receives ACKs, run as a thread
    def receiveFunc(self):
        while True:
            messageBytes, _serverAddress = self.clientSocket.recvfrom(1024) # retrieve packet
            message = Message(messageBytes=messageBytes)
            if message.checksumValue == message.calcChecksum():     # check for bit errors
                ackNum = message.acknowledgmentNumber
                if ackNum in self.window:
                    self.process_ack(ackNum)
                else:
                    pass
                    #print("duplicate ack")
                if (ackNum == self.windowBase):     # if ACK is for first packet in window, the window slides
                    self.getMoreData()
                #print(self.window.keys())
                if self.doneReading and len(self.window) == 0:  # last packet received
                    print("done at sender")
                    print("time:", float(time.time() - self.startTime))
                    print("num retransmits:", self.numRetransmits)
                    break

    # processes an ACK
    def process_ack(self, ackNum):
        self.queueUse.acquire()     # prevent other threads from accessing the window
        to_remove = []
        if self.GBN:                # for GBN, cumulative ACK, so remove from window everything that came before the ACKed packet
            for key in self.window:
                if key <= ackNum and key + 50000 > ackNum:
                    to_remove.append(key)
            for entry in to_remove:
                del (self.window[entry])
        else:                       # for selective repeat, just remove the ACKed packet
            del (self.window[ackNum])
        self.queueUse.release()

    # handles a timeout
    def timeout(self, sequenceNumber):
        if sequenceNumber in self.window:
            if not self.GBN:
                self.queueUse.acquire()
                # have to check again b/c she sequence number may have been taken out of the window by another thread
                # I could place the acquire() outside the if, but that would require a lock every time timeout() is called
                if sequenceNumber in self.window:
                    self.numRetransmits += 1
                    print("retransmitting", sequenceNumber)
                    retransmitMessage = Message(messageBytes=self.window[sequenceNumber])
                    self.messageQueue.insert(0, retransmitMessage)      # add retransmit message to head of the queue so it is resent as soon as possible
                    timer = threading.Timer(self.timeoutInterval, self.timeout, [retransmitMessage.sequenceNumber])
                    timer.start()   # start new timer for the packet
                self.queueUse.release()
            else:   # gbn: clear messageQueue and resend all messages in window
                self.queueUse.acquire()
                self.messageQueue.clear()
                for seqNum in self.window:
                    retransmitMessage = Message(messageBytes=self.window[seqNum])
                    self.numRetransmits += 1
                    self.messageQueue.append(retransmitMessage)
                self.queueUse.release()
        elif self.GBN:   # if gbn and already received packet times out, start timer for oldest packet in window
            self.queueUse.acquire()
            if len(self.window) == 0:
                return
            min = -1        # find sequence number of oldest packet
            for x in self.window:
                if min == -1:
                    min = x
                elif x < min and x + 50000 > min:   # handles cycling of sequence numbers
                    min = x
            self.queueUse.release()
            timer = threading.Timer(self.timeoutInterval, self.timeout, [min])
            timer.start()       # start timer for unacked packet



    # read file to fill window if window is not full
    def getMoreData(self):
        if self.doneReading:
            return
        nextToRead = self.nextSequenceNumber  # all packets up to this point have been stored in window
        # find first unACKed packet in window
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

        # nextNotReceived would be unchanged if the window was empty
        self.windowBase = self.nextSequenceNumber if nextNotReceived >= 100000 else nextNotReceived
        max = (self.windowBase + self.windowSize) % 65536     # sequence number of last packet in the window

        # read from the file to fill the unused window
        self.queueUse.acquire()     # prevent other threads from accessing the message queue
        while nextToRead + self.payloadSize <= max or nextToRead + self.payloadSize - 32000 > max:  # check if another packet should be added to the window
            newBytes = bytearray(self.file.read(self.payloadSize), 'utf-8')     # read bytes from the file
            packet = Message(seqNum=nextToRead, payload=newBytes)
            self.window[nextToRead] = packet.toBytes()
            self.messageQueue.append(packet)        # add packet to end of queue to be sent
            nextToRead += self.payloadSize          # update next sequence number, wrapping around if necessary
            if nextToRead >= 65536:
                nextToRead -= 65536
            if len(newBytes) < self.payloadSize:  # check for last packet
                print("seq num where I am stopping:", packet.sequenceNumber)
                print("max", max)
                self.doneReading = True
                self.file.close()
                break
        self.queueUse.release()
        self.nextSequenceNumber = nextToRead


