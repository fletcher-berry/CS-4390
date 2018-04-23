#!/usr/bin/env python3.6
import selectiveRepeatRunner
from gbn_sender import GbnSender
from gbn_receiver import GbnReceiver
from selective_repeat_receiver import SrReceiver
from sender import Sender
import os
import _thread
from multiprocessing import Process

"""
Allow the user to select window size, payload size, input file, and whether to use GBN or SR
This is the entry point of the program.
"""


# prompts for file name
def prompt_for_file():
   while True:
        file_name = input("Enter a file path>")
        if os.path.exists(file_name):
            return file_name
        print("File %s not found.", file_name)

# prompts for window size
def prompt_for_window():
    while True:
        try:
            window_size = int(input("Enter a window size>"))

            if window_size in range(1,32767):   # window size can be at most half of the sequence number values
                return window_size
            else:
                print("Invalid window size")
                print("Acceptable window sizes: integers between 1 and 32,767")
        except ValueError:
            print("Not a valid integer")

# prompts for payload size
def prompt_for_payload():
    while True:
        try:
            payload_size = int(input("Enter a payload size>"))
            if payload_size in range(10,101):
                return payload_size
            else:
                print("Invalid window size")
                print("Acceptable window sizes: integers between 10 and 100")
        except ValueError:
            print("Not a valid integer")

def main():
    try:
        # user selects between GBN and SR
        decision = ''
        while decision != "x":
            print("Main Menu of RDT UDP:")
            print("Select one of the following")
            print(" 0. Go back N")
            print(" 1. Selective Repeat")
            print(" x. exit")
            decision = input(">")

            if decision == "0":
                # run GBN
                RECV_WINDOW = 1
                filePath = prompt_for_file()
                windowSize = prompt_for_window()
                payloadSize = prompt_for_payload()
                receiver = GbnReceiver(payloadSize)
                sender = Sender(windowSize, payloadSize, filePath, GBN=True)
                _thread.start_new_thread(receiver.run, ())
                _thread.start_new_thread(sender.run, ())
                try: 
                    while True:     # makes sure process doesn't terminate
                        pass
                except KeyboardInterrupt:
                    break

            elif decision == "1":
                # run selective repeat
                filePath = prompt_for_file()
                windowSize = prompt_for_window()
                payloadSize = prompt_for_payload()
                receiver = SrReceiver(windowSize, payloadSize)
                sender = Sender(windowSize, payloadSize, filePath, GBN=False)
                _thread.start_new_thread(receiver.run, ())
                _thread.start_new_thread(sender.run, ())
                try: 
                    while True:     # makes sure process doesn't terminate
                        pass
                except KeyboardInterrupt:
                    break

            elif decision != "x":
                print("Decision not recognized.\n")

    except KeyboardInterrupt:
        print()
    pass

main()
