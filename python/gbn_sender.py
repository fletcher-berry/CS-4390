#!/usr/bin/env python3
import socket
from Message import Message
import time
from threading import *
from multiprocessing import Process
import _thread

class GbnSender:
    def __init__(self, windowSize, filePath, packetSize=100):
        self.ip = "127.0.0.1"
        self.serverPort = 2346
        self.clientPort = 2346
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.destAddr = (self.ip, self.serverPort)
        #self.socket.bind((self.ip, self.clientPort))

        self.filePath = filePath
        self.cAck = 0

        self.packets = []
        self.packetSize = packetSize

        self.ackLock = Semaphore(1)

        self.windowSize = windowSize

        self.currentPkt = 0
        self.retransmitted = 0

        self.dbg = 0

    def loadpackets(self):
        try:
            with open(self.filePath, "r") as f:
                # go ahead and read all packets into memory
                data = bytearray(f.read(self.packetSize-6), 'utf-8')
                seqNum = 0
                while data:
                    msg = Message(seqNum = seqNum,
                                  ackNum = 0,
                                  payload = data)
                    data = bytearray(f.read(self.packetSize-6), 'utf-8')
                    self.packets.append(msg)
                    seqNum+=1 
                #for p in self.packets:
                #    print("payload %s" %s p.payload)

        except IOError:
            print("Cannot open file.")
            return
        finally:
            f.close()

    def run(self):
        print("Starting up...")
        self.loadpackets()

        #print("sending %d packets" % len(self.packets))
        start_time = time.time()
        
        _thread.start_new_thread(self.receive, ())
        numPackets = len(self.packets)-1
        seqNum = 0

        # loop through all packets
        while self.cAck < numPackets:
            self.ackLock.acquire()

            while seqNum < self.cAck + self.windowSize:

                if seqNum > numPackets:
                    self.cAck = numPackets+1
                    break
                self.socket.sendto(self.packets[seqNum].toBytes(),self.destAddr)
                seqNum += 1

            #TODO implement a better timer here

            # Start timer here
            # wait until either timeout or we're told there are more packets
            # if timeout, then set the seqNum value to be the cumulative Ack
            #    ie seqNum = self.cAck
            # then add the window size to the total retransmitted count
            #    self.retransmitted += self.windowSize

            self.ackLock.release()

        # final packet
        msg = Message(seqNum = seqNum,
                      ackNum = 1,
                      payload = [])

        end_time = time.time()
        print("Finished transmitting file. in %.3f seconds" % float(end_time - start_time))
        print("Packets retrasnmitted: %d" % self.retransmitted)


    def receive(self):
        # look for an ACK to further along the window
        try:
            while True:
                msgBytes, addr = self.socket.recvfrom(self.packetSize)
                msg = Message(messageBytes=msgBytes)
                # successfully received uncorrupted packet
                #if msg.checksumValue == msg.calcChecksum():

                # if the received acknowledgment is lower than the current packet we're 
                # trying to transmit
                if self.cAck <= msg.acknowledgmentNumber:
                    self.ackLock.acquire()

                    #TODO stop the timer for the sender here

                    # instead of crawling along at +1 every time, 
                    # maybe replace this with cAck += (msg.ack-cAck)?
                    self.cAck += 1

                    self.ackLock.release()

        except KeyboardInterrupt:
            pass
