from socket import *

class SrSender:
	
	
	def __init__(self, windowSize, payloadSize, filePath):
		self.windowSize = windowSize * payloadSize	# window size in bytes
		self.serverName = "127.0.0.1"
		self.serverPort = 2345;
		self.clientSocket = socket(AF_INET, SOCK_DGRAM)
		self.payloadSize = payloadSize
		self.windowBase = 0
		self.file = open(filePath, "r")
		self.doneReading = False	# whether or not end of file to transmit has been seen
		self.window = {}			# array of sequence numbers of unreceived messages
		self.messageQueue = []		# array of messages to send
		self.queueUse = Semaphore(1)
		
		
	def run():
		thread.start_new_thread(sendFunc, ())
		thread.start_new_thread(receiveFunc, ())
		
	
	
	
	def sendFunc():
		while True:
			queueUse.acquire()
			if len(messageQueue) > 0:
				message = messageQueue[0]
				self.clientSocket.sendTo(message.toBytes(), (serverName, serverPort))
				del(messageQueue[0])
			queueUse.release()
			
	def receiveFunc()
		while(true):
			messageBytes, serverAddress = self.clientSocket.recvFrom(2048)
			message = Message(messageBytes)
			if message.checksumValue == message.calcChecksum():
				seqNum = message.sequenceNumber
				del(self.window[seqNum])
				if(seqNum == self.windowBase):
					getMoreData()
				
		
		

	#sendMessage(self, message):
	
	# read file to fill window if window is not full
	def getMoreData():
		if self.doneReading:
			return
		nextToRead = self.windowBase + self.windowSize		# all packets up to this point have been stored in window
		# find smallest sequence number in window
		wrap = self.windowBase + self.windowSize >= 65536
		nextNotReceived = 100000
		for val in self.window:
			seqNum = val
			if wrap and seqNum < self.windowBase + self.windowSize:
				seqNum += 65536
			if seqNum < nextNotReceived:
				nextNotReceived = seqNum
		if nextNotReceived >= 65536:
			nextNotReceived -= 65536
		self.windowBase = nextNotReceived
		max = self.windowBase + self.windowSize
		self.queueUse.acquire()
		# read from the file to fill the unused window
		while nextToRead + self.payloadSize <= max or nextToRead + self.payloadSize - 32000 > max:
			newBytes = bytearray(file.read(self.payloadSize))
			self.window[nextToRead] = newBytes
			packet = Message(newBytes)
			messageQueue.append(packet)
			nextToRead += payloadSize
			if nextToRead >= 65536:
				nextToRead -= 65536
			if len(newBytes) < payloadSize:	# last packet
				self.doneReading = true
				self.file.close()
		self.queueUse.release()
				
				
		
