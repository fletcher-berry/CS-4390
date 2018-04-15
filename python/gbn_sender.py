#!/usr/bin/env python3
import socket
from Message import Message
import time,threading
import _thread

class GbnSender:
    def __init__(self, windowSize, filePath):
        self.addr = "127.0.0.1"
        self.serverPort = 2346
        self.clientPort = 2345
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.filePath = filePath
        self.payLoadSize = 10
        self.packetTimers = {}
        self.timerLock = threading.Semaphore(1)
        self.window = []
        self.windowLock = threading.Semaphore(1)
        self.windowBase = 0
        self.windowSize = windowSize
        self.windowSizeBytes = windowSize * self.payLoadSize

        self.retransmitted = 0

    def run(self):
        _thread.start_new_thread(self.send, ())
        _thread.start_new_thread(self.receive, ())
        try:
            while True:
                pass
        except KeyboardInterrupt:
            print()

    def transmit_packet(self, packet):
        print('Sending message %d : %s' % (packet.sequenceNumber, packet.toBytes()))
        self.socket.sendto(packet.toBytes(), (self.addr, self.serverPort))

    def packet_timeout(self, pkt):
        print("TIMED OUT: status of packetTimers: ")
        print(self.packetTimers[pkt.sequenceNumber])
        if self.packetTimers[pkt.sequenceNumber]:
            print("  Packet number %d timed out " % pkt.sequenceNumber)
            self.transmit_packet(pkt)
            self.retransmitted += 1
            threading.Timer(5,self.packet_timeout,[pkt]).start()

    def send(self):
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
                    print("-------------SENDING info")
                    self.windowLock.acquire()
                    self.window.append(pkt)
                    self.windowLock.release()
                    # package up into message and send to receiver
                    msg = Message(seqNum  = seqNum,
                                  ackNum  = ackNum,
                                  payload = pkt )
                    self.transmit_packet(msg)

                    # Set new packet timer with ID ack
                    self.timerLock.acquire()
                    self.packetTimers[ackNum] = True
                    print("just added to packet timers")
                    print(self.packetTimers)
                    threading.Timer(5, self.packet_timeout, [msg]).start()
                    self.timerLock.release()

                    # load next section of data
                    pkt = inputFile.read(self.payLoadSize)
                    seqNum += 1


    def receive(self):
        # look for an ACK to further along the window
        print("-------------LISTENING FOR ACKS")
        while True:
            msgBytes, Addr = self.socket.recvfrom(1024)
            msg = Message(messageBytes=msgBytes)
            # successfully received uncorrupted packet
            #if msg.checksumValue == msg.calcChecksum():
            # move window base along, remove packet from front
            # and remove timer for packet.
            print("Received ack for %d" % msg.acknowledgmentNumber)
            self.timerLock.acquire()
            print(self.packetTimers)
            if msg.acknowledgmentNumber in self.packetTimers.keys():
                del self.packetTimers[msg.acknowledgmentNumber]
            self.timerLock.release()

            self.windowLock.acquire()
            self.windowBase = self.windowBase + 1
            if self.window:
                del self.window[0]
            self.windowLock.release()
            # add logic to remove timers prior to the received ack as well

# Dummy receiver class to test sender 
class GbnReceiver:
    def __init__(self, windowSize):
        self.addr = "127.0.0.1"
        self.serverPort = 2346
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', self.serverPort))
        self.payLoadSize = 10
        self.cumulativeAck = 0

    def run(self):
        # receive
        print("Starting up...")
        while True:
            print("\tReceiver waiting on packets... ")
            msgBytes, clientAddress = self.socket.recvfrom(1024)
            msg = Message(messageBytes=msgBytes)

            #if msg.checksumValue == msg.calcChecksum():
            print("\tReceiving %d : %s" % (msg.sequenceNumber, str(msgBytes)))
            if msg.sequenceNumber == self.cumulativeAck:
                receiverAckNum = msg.sequenceNumber

                # send ack if the packet 
                msg = Message(receiverAckNum, receiverAckNum, [])
                print("\tAcking: %d" % receiverAckNum)
                self.socket.sendto(msg.toBytes(), clientAddress)
                self.cumulativeAck += 1
            else:
                # discard packet out of line
                print('\tMessage discarded, out of order...')
                pass
            #else:
            #    print('Corrupted message')



