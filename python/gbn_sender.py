#!/usr/bin/env python3
import socket
from Message import Message
import time,threading
import _thread

class GbnSender:
    def __init__(self, windowSize, filePath, packetSize=100):
        self.addr = "127.0.0.1"
        self.serverPort = 2346
        self.clientPort = 2345
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.addr, self.clientPort))

        self.filePath = filePath
        self.cumulativeAck = 0
        self.packetSize = packetSize
        self.packetTimers = {}
        self.timerLock = threading.Semaphore(1)

        self.window = []
        self.windowLock = threading.Semaphore(1)
        self.windowBase = 0
        self.windowSize = windowSize
        self.windowSizeBytes = windowSize * self.packetSize

        self.retransmitted = 0

        self.dbg = 0

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
        if pkt.sequenceNumber in self.packetTimers.keys():
            if self.packetTimers[pkt.sequenceNumber] != False:
                if pkt.sequenceNumber > self.cumulativeAck:
                    # if timeout, retransmit packet n and all higher seq # packets in window
                    print("  Packet timed out %d" % pkt.sequenceNumber)
                    for i in self.window:
                        self.transmit_packet(i)
                        self.retransmitted += 1
                    threading.Timer(1,self.packet_timeout,[pkt]).start()
            else:
                del self.packetTimers[pkt.sequenceNumber]

    def send(self):
        print("Starting up...")
        start_time = time.time()
        # retrieve x bytes from file and send 
        with open(self.filePath, "r") as f:
            # read -6 to account for the header size
            data = bytearray(f.read(self.packetSize-6), 'utf-8')
            seqNum = 0
            ackNum = 0
            while data:
                msg = Message(seqNum  = seqNum,
                              ackNum  = ackNum,
                              payload = data )
                self.socket.sendto(msg.toBytes(), (self.addr, self.serverPort))
                data = bytearray(f.read(self.packetSize-6), 'utf-8')
                seqNum+=1

            # final packet
            msg = Message(seqNum = seqNum,
                          ackNum = 1,
                          payload = "")
# TESTING -------------------------------------
            #data = f.read(self.packetSize)
            #while data:
            #    s = time.time()
            #    self.socket.sendto(bytes(data, 'utf-8'), (self.addr, self.serverPort))
            #    e = time.time()
            #    self.dbg += (e-s)
            #    data = f.read(self.packetSize-6)

            #self.socket.sendto(bytes('haltzen','utf-8'), (self.addr,self.serverPort))
            #print("time spent on sento: %f" %self.dbg)

                # if the window isn't full yet
                #if seqNum + 1 <= self.windowBase + self.windowSize:
                #    print("\n-------------SENDING info")
                #    # package up into message and send to receiver
                #    msg = Message(seqNum  = seqNum,
                #                  ackNum  = ackNum,
                #                  payload = data )

                #    #self.windowLock.acquire()
                #    self.window.append(msg)
                #    #self.windowLock.release()
                #    self.transmit_packet(msg)

                #    #self.timerLock.acquire()
                #    #if seqNum not in self.packetTimers.keys():
                #    #    self.transmit_packet(msg)
                #    #    self.packetTimers[seqNum] = True
                #    #    threading.Timer(1, self.packet_timeout, [msg]).start()
                #    #print("Packet Timer statuses: ",self.packetTimers)
                #    #self.timerLock.release()

                #    # load next section of data
                #    pkt = inputFile.read(self.packteSize-6)
                #    seqNum += 1

        end_time = time.time()
        print("Finished transmitting file. in %.3f seconds" % float(end_time - start_time))
        print("Packets retrasnmitted: %d" % self.retransmitted)


    def receive(self):
        # look for an ACK to further along the window
        print("-------------LISTENING FOR ACKS")
        while True:
            msgBytes, addr = self.socket.recvfrom(self.packetSize)
            msg = Message(messageBytes=msgBytes)
            # successfully received uncorrupted packet
            #if msg.checksumValue == msg.calcChecksum():
            # move window base along, remove packet from front
            # and remove timer for packet.

            #print("Received ack for %d" % msg.acknowledgmentNumber)
            self.cumulativeAck = msg.acknowledgmentNumber
            #self.timerLock.acquire()
            #if msg.acknowledgmentNumber in self.packetTimers.keys():
            #    self.packetTimers[msg.acknowledgmentNumber] = False
            #self.timerLock.release()

            #self.windowLock.acquire()
            #self.windowBase = self.windowBase + 1
            #if self.window:
            #    del self.window[0]
            #self.windowLock.release()
        # add logic to remove timers prior to the received ack as well

