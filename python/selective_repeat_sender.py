
import threading
from socket import *
from _thread import *
from threading import Semaphore

import _thread

from Message import Message



class SrSender:

	def __init__(self, windowSize, payloadSize, filePath):
		self.windowSize = windowSize * payloadSize  # window size in bytes
		self.serverName = "127.0.0.1"
		self.serverPort = 2345
		self.clientPort = 2346
		self.clientSocket = socket(AF_INET, SOCK_DGRAM)
		self.clientSocket.bind(('', self.clientPort))
		self.payloadSize = payloadSize
		self.windowBase = 0
		self.file = open(filePath, "r")
		self.doneReading = False  # whether or not end of file to transmit has been seen
		self.window = {}  # maps sequence number to bytes of message (including header)
		self.messageQueue = []  # array of messages to send
		self.queueUse = threading.Semaphore(1)
		self.getMoreData()

	def run(self):

		_thread.start_new_thread(self.sendFunc, ())
		_thread.start_new_thread(self.receiveFunc, ())

	def sendFunc(self):

		while True:

			self.queueUse.acquire()
			if len(self.messageQueue) > 0:
				message = self.messageQueue[0]
				self.clientSocket.sendto(message.toBytes(), (self.serverName, self.serverPort))

				del (self.messageQueue[0])
				timer = threading.Timer(0.1, timeout, message.sequenceNumber)
				timer.start()
			self.queueUse.release()

	def receiveFunc(self):
		while True:
			messageBytes, serverAddress = self.clientSocket.recvfrom(1024)
			message = Message(messageBytes=messageBytes)
			if message.checksumValue == message.calcChecksum():
				seqNum = message.sequenceNumber
				del (self.window[seqNum])
				if (seqNum == self.windowBase):
					self.getMoreData()

	def timeout(self, sequenceNumber):
		self.queueUse.acquire()
		retransmitMessage = Message(messageBytes=self.window[sequenceNumber])
		self.messageQueue.insert(0, retransmitMessage)
		self.queueUse.release()
		timer = threading.Timer(0.1, timeout, (retransmitMessage.sequenceNumber))
		timer.start()

	# read file to fill window if window is not full
	def getMoreData(self):
		if self.doneReading:
			return
		nextToRead = self.windowBase + self.windowSize  # all packets up to this point have been stored in window
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
			newBytes = bytearray(self.file.read(self.payloadSize), 'utf-8')
			self.window[nextToRead] = newBytes
			packet = Message(messageBytes=newBytes)
			self.messageQueue.append(packet)
			nextToRead += self.payloadSize
			if nextToRead >= 65536:
				nextToRead -= 65536
			if len(newBytes) < self.payloadSize:  # last packet
				self.doneReading = True
				self.file.close()
				break
		self.queueUse.release()

