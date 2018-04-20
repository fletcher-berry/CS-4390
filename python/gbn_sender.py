#!/usr/bin/env python3
import socket
from Message import Message
import time
from threading import Semaphore, Timer
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
        self.windowSize = windowSize

        self.ackLock = Semaphore(1)

        self.currentPkt = 0
        self.retransmitted = 0

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

        except IOError:
            print("Cannot open file.")
            return
        finally:
            f.close()

    def timeout(self, seqNum):
        # if the packet hasn't been acknowledged yet
        if seqNum < self.cAck:
            # retransmit whole window
            for packet in self.packets[seqNum:seqNum+self.windowSize]:

                self.socket.sendto(packet.toBytes(),self.destAddr)
                timer = Timer(0.1, self.timeout, [seqNum])
                timer.start()

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

            # shrink windowSize if we are approaching the end
            if (self.cAck + self.windowSize) > numPackets:
                self.windowSize = numPackets-self.cAck

            # only transmit new packets if the window has shifted
            if seqNum < (self.cAck + self.windowSize):
                # transmit all packets in the window
                for packet in self.packets[seqNum:seqNum+self.windowSize]:

                    self.socket.sendto(self.packets[seqNum].toBytes(),self.destAddr)
                    seqNum += 1

                # set a timer for packets from current cumulativeAck+1 to window size
                timer = Timer(0.1, self.timeout, self.cAck+1 )

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
                if msg.checksumValue == msg.calcChecksum():
                    # if the received acknowledgment is lower than the current packet we're 
                    # trying to transmit
                    if self.cAck <= msg.acknowledgmentNumber:
                        self.ackLock.acquire()

                        # maybe replace this with cAck += (msg.ack-cAck)?
                        self.cAck += (msg.acknowledgmentNumber - self.cAck)

                        self.ackLock.release()

        except KeyboardInterrupt:
            pass
