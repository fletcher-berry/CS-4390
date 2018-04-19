from selective_repeat_sender import *
from selective_repeat_receiver import *
import _thread

def run(windowSize, payloadSize, filePath):
    receiver = SrReceiver(windowSize, payloadSize)
    sender = SrSender(windowSize, payloadSize, filePath)
    _thread.start_new_thread(receiver.run, ())
    _thread.start_new_thread(sender.run, ())
    while True:
        pass
    # what to do after file is transmitted?

if __name__ == '__main__':
    run(32, 100, 'test.txt')
    #input("fdsfd")
    #while True:
        #x = 0

