"""
represents a packet and its header values.  This class is used as an abstraction of the physical
structure of a packet
"""

class Message:

	# attributes:
	# sequenceNumber: 		stored as number
	# acknowledgmentNumber: stored as number
	# checksumValue: 		When a message is received, the checksum header is parsed into
	# 						this value.  Bit can be detected by comparing this value to the result
	# 						of calcChecksum().  stored as number.
	# payload: message payload not including headers, stored as byte array


	# messageBytes is the bytes of the entire message
	def __init__(self, seqNum=0, ackNum=0, payload=None, messageBytes=None):
		if messageBytes is None:		# building message from header values and payload
			self.sequenceNumber = seqNum
			self.acknowledgmentNumber = ackNum
			self.payload = payload
			self.checksumValue = self.calcChecksum()
		else:			# building message from received packet
			self.sequenceNumber = messageBytes[0] * 256 + messageBytes[1]
			self.acknowledgmentNumber = messageBytes[2] * 256 + messageBytes[3]
			self.checksumValue = messageBytes[4] * 256 + messageBytes[5]
			self.payload = messageBytes[6:]	

	# convert message to bytes
	def toBytes(self):
		seqNum = bytearray([self.sequenceNumber // 256, self.sequenceNumber % 256])
		ackNum = bytearray([self.acknowledgmentNumber // 256, self.acknowledgmentNumber % 256])
		checksumInt = self.calcChecksum()
		checksumBytes = bytearray([checksumInt // 256, checksumInt % 256])
		return seqNum + ackNum + checksumBytes + bytearray(self.payload)

	# calculate the checksum of the message
	def calcChecksum(self):
		sum = self.sequenceNumber + self.acknowledgmentNumber
		isNewValue = True
		nextValue = 0
		for byte in self.payload:
			if isNewValue:
				nextValue += byte * 256
				isNewValue = False
			else:
				nextValue += byte
				sum += nextValue
				isNewValue = False
		sum %= 65536
		return sum
		
	# length of payload in bytes
	def getLength(self):
		return len(self.payload)
		
