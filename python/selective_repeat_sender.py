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
		self.window = {}			# map sequence number to message payload
		
		

	#sendMessage(self, message):
	
	# read file to fill window if window is not full
	def readFile():
		if doneReading:
			return
		while len(self.window) < self.windowSize / self.payloadSize:
			newBytes = bytearray(file.read(self.payloadSize))
			seqNum = self.windowBase + self.payloadSize * len(self.window)
			self.window[seqNum] = newBytes
			if len(newBytes) < payloadSize:
				doneReading = true
				self.file.close()
				return
				
		
