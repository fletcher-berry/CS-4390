class Message:

	# attributes:
	# sequenceNumber: stored as number
	# acknowledgmentNumber: stored as number
	# checksumValue: When a message is received, the checksum header is parsed into 
	# this value.  Bit can be detected by comparing this value to the result 
	# of calcChecksum().  stored as number.
	# payload: message payload not including headers, stored as byte array

	def __init__(self, seqNum=None, ackNum=None, payload=None, messageBytes=None):
		if messageBytes is None:
			self.sequenceNumber = seqNum
			self.acknowledgmentNumber = ackNum
			self.checksumValue = self.calcChecksum()
			self.payload = payload
		else:
			self.sequenceNumber = messageBytes[0] * 256 + messageBytes[1]
			self.ackNum = messageBytes[2] * 256 + messageBytes[3]
			self.checksumValue = messageBytes[4] * 256 + messageBytes[5]
			self.payload = messageBytes[6:]	

	def toBytes(self):
		seqNum = [self.sequenceNumber // 256, self.sequenceNumber % 256]
		ackNum = [self.acknowledgmentNumber // 256, self.acknowledgmentNumber % 256]
		checksumInt = self.calcChecksum()
		checksumBytes = [checkSumInt // 256, checksumInt % 256]
		return seqNum + ackNum + checksumBytes + self.payload

	def calcChecksum(self):
		sum = sequenceNumber + acknowledgmentNumber
		isNewValue = True
		nextValue = 0
		for byte in payload:
			if isNewValue:
				nextValue += byte * 256
				isNewValue = false
			else:
				nextValue += byte
				sum += nextValue
				isNewValue = false
			
		sum %= 65536
		return sum
		
	# length of payload in bytes
	def getLength(self):
		return len(payload)
		
