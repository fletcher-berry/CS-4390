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
        print('Sending message %d : %s' % (packet.sequenceNumber, packet.toBytes()))
        self.socket.sendto(packet.toBytes(), (self.serverAddr, self.serverPort))

    def packet_timeout(self, pkt):
        print("  Packet number %d timed out " % pkt.sequenceNumber)
        self.transmit_packet(pkt)

    def run(self):
        print("Starting up...")
        # retrieve x bytes from file and send 
        with open(self.filePath, "rb") as inputFile:
            pkt = inputFile.read(self.payLoadSize)
            # -1 because we start with a packet loaded
            seqNum = -1
            ackNum = 0
            while pkt:
                # if the window isn't full yet
                if seqNum + 1 <= self.windowBase + self.windowSize:
                    self.window.append(pkt)
                    seqNum = seqNum + 1

                    # package up into message and send to receiver
                    msg = Message(seqNum  = seqNum,
                                  ackNum  = ackNum,
                                  payload = pkt )
                    self.transmit_packet(msg)

                    # Set new packet timer with ID ack
                    self.packetTimers[ackNum] = Timer(.1, self.packet_timeout, [msg] )
                    self.packetTimers[ackNum].start()

                    # load next section of data
                    pkt = inputFile.read(self.payLoadSize)

                # look for an ACK to further along the window
                else:
                    msgBytes, Addr = self.socket.recvfrom(2048)
                    msg = Message.setMessage(msgBytes)

                    # successfully received uncorrupted packet
                    if msg.checksumValue == msg.calcChecksum():
                        # move window base along, remove packet from front
                        # and remove timer for packet.
                        del self.packetTimers[msg.ReceivedAckNum]
                        self.windowBase = self.WindowBase + 1
                        del self.window[0]
                        # add logic to remove timers prior to the received ack as well

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
        while True:
            print("\tReceiver waiting on packets... ")
            msgBytes, Addr = self.socket.recvfrom(2048)
            msgBytes, clientAddress = self.socket.recvfrom(2048)
            msg = Message(messageBytes=msgBytes)

            #if msg.checksumValue == msg.calcChecksum():
            print("\tReceiving %d : %s" % (msg.sequenceNumber, str(msgBytes)))
            #print("\tSEQ %d : CUMULATIVE %d" % (msg.sequenceNumber,self.cumulativeAck))
            if msg.sequenceNumber == self.cumulativeAck:
                receiverAckNum = msg.acknowledgmentNumber
                receiverSeqNum = msg.sequenceNumber

                # send acknowledgement if the packet 
                msg = Message(receiverSeqNum, receiverAckNum, [])
                print("\tAcking: %d" % receiverAckNum)
                self.socket.sendto(msg.toBytes(), (self.serverAddr, self.serverPort))
                self.cumulativeAck += 1
            else:
                # discard packet out of line
                print('\tMessage discarded, out of order...')
                pass
            #else:
            #    print('Corrupted message')

            time.sleep(1)





