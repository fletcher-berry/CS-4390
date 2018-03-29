import selective_repeat_sender
import selective_repeat_receiver


def run(windowSize, payloadSize, filePath):
	receiver = SrReceiver(windowSize, payloadSize)
	reciever.run()
	sender = SrSender(windowSize, payloadSize, filePath)
	# run the sender