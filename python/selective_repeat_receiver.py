from socket import *

class SrReceiver:

	def __init__(self, windowSize, payloadSize):
		self.windowSize = windowSize * payloadSize # window size in bytes
		self.serverName = "127.0.0.1"
		self.serverPort = 2345;
		self.serverSocket = socket(AF_INET, SOCK_DGRAM)
		serverSocket.bind(('', serverPort))
		self.windowBase = 0
		self.payloadSize = payloadSize
		self.buffer = {}				# map sequence number to message payload
		self.sentToApplication = [] 	# bytes sent to application layer
		
		
	def run():
		while True:
			messageBytes, clientAddress = self.serverSocket.recvFrom(2048)
			message = Message(messageBytes=messageBytes)
			if message.checksumValue != message.calcChecksum():	# corrupted header
				continue;
			# how to determine if payload is corrupted?
			# is there a python method?
			
			# send ack
			ack = Message(seqNum=0, ackNum=message.sequenceNumber, payload=[])
			self.serverSocket.sendTo(ack.toBytes(), clientAddress)
			
			# check if sequence number is in window
			windowMax = self.windowBase + self.windowSize
			if windowMax < 65536:
				inWindow = self.windowBase <= message.sequenceNumber < windowMax
			else:
				inWindow = message.sequenceNumber >= self.windowBase or message.sequenceNumber < windowMax - 65536
			if not inWindow:
				continue
			
			# if in window buffer
			self.buffer[message.sequenceNumber] = message.payload
			if(message.sequenceNumber == self.windowBase):
				updateBuffer()
			
			
	def updateBuffer():
		while self.buffer.has_key(self.windowBase):	# first message in window has been received
			sentToApplication += self.buffer[windowBase]
			del(self.buffer[windowBase])
			self.windowBase += self.payloadSize
			
			
			
