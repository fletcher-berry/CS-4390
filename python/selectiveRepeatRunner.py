from selective_repeat_sender import *
from selective_repeat_receiver import *
import _thread

def run(windowSize, payloadSize, filePath):
	receiver = SrReceiver(windowSize, payloadSize)
	sender = SrSender(windowSize, payloadSize, filePath)
	_thread.start_new_thread(receiver.run, ())
	_thread.start_new_thread(sender.run, ())
	# what to do after file is transmitted?

run(32, 50, 'data.txt')
while True:
	x = 0
