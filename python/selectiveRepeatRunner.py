import selective_repeat_sender
import selective_repeat_receiver


def run(windowSize, payloadSize, filePath):
	receiver = SrReceiver(windowSize, payloadSize)
	sender = SrSender(windowSize, payloadSize, filePath)
	thread.start_new_thread(receiver.run, ())
	thread.start_new_thread(sender.run, ())
	# what to do after file is transmitted?