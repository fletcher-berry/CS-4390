from socket import socket, AF_INET, SOCK_DGRAM

from Message import Message



class SrReceiver:

        def __init__(self, windowSize, payloadSize):
                self.windowSize = windowSize * payloadSize # window size in bytes
                self.serverName = "127.0.0.1"
                self.serverPort = 2345
                self.serverSocket = socket(AF_INET, SOCK_DGRAM)
                self.serverSocket.bind(('', self.serverPort))
                self.windowBase = 0
                self.payloadSize = payloadSize
                self.buffer = {}                                # map sequence number to message payload
                self.sentToApplication = []     # bytes sent to application layer
                self.endSequence = False         # sequence number of last packet




        def run(self):
                print('running', flush=True)
                # f = open("test2.txt")
                # f.write("rrr")
                # f.close()
                while True:

                        messageBytes, clientAddress = self.serverSocket.recvfrom(2048)
                        message = Message(messageBytes=messageBytes)
                        if message.checksumValue != message.calcChecksum():     # corrupted message
                                continue
                        #print('received', message.sequenceNumber)
                        # send ack
                        ack = Message(seqNum=0, ackNum=message.sequenceNumber, payload=[])
                        self.serverSocket.sendto(ack.toBytes(), clientAddress)
                        
                        # check if sequence number is in window
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
                        
                        # if in window buffer
                        self.buffer[message.sequenceNumber] = message.payload
                        if message.sequenceNumber == self.windowBase:
                                self.updateBuffer()

                        if self.endSequence and len(self.buffer) == 0:     # all packets received
                                outFile = open("output.txt", "w+")
                                str1 = bytearray(self.sentToApplication).decode('utf-8')
                                outFile.write(str1)
                                outFile.close()
                                print(str1)
                                #exit()

            
                        
                        
        def updateBuffer(self):
                while self.windowBase in self.buffer:   # first message in window has been received
                        self.sentToApplication += self.buffer[self.windowBase]
                        del(self.buffer[self.windowBase])
                        self.windowBase += self.payloadSize

                        

