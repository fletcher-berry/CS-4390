#!/usr/bin/env python3.6
import selectiveRepeatRunner
from gbn_sender import GbnSender
from gbn_receiver import GbnReceiver
from selective_repeat_receiver import SrReceiver
from sender import Sender
import os
import _thread
from multiprocessing import Process

def prompt_for_file():
   while True:
        file_name = input("Enter a file path>")
        if os.path.exists(file_name):
            return file_name
        print("File %s not found.", file_name)

def prompt_for_window():
    while True:
        try:
            window_size = int(input("Enter a window size>"))

            if window_size in range(1,65555):
                return window_size
            else:
                print("Invalid window size")
                print("Acceptable window sizes: integers between 1 and 65,535") 
        except ValueError:
            print("Not a valid integer")

def main():
    try:
        decision = ''
        while decision != "x":
            print("Main Menu of RDT UDP:")
            print("Select one of the following")
            print(" 0. Go back N")
            print(" 1. Selective Repeat")
            print(" x. exit")
            decision = input(">")

            if decision == "0":
                RECV_WINDOW = 1
                PAYLOAD_SIZE = 100
                filePath = prompt_for_file()
                windowSize = prompt_for_window()
                receiver = GbnReceiver(PAYLOAD_SIZE)
                sender = Sender(windowSize, PAYLOAD_SIZE, filePath, GBN=True)
                _thread.start_new_thread(receiver.run, ())
                _thread.start_new_thread(sender.run, ())
                try: 
                    while True:     # makes sure process doesn't terminate
                        pass
                except KeyboardInterrupt:
                    break

            elif decision == "1":
                PAYLOAD_SIZE = 100
                filePath = prompt_for_file()
                windowSize = prompt_for_window()
                receiver = SrReceiver(windowSize, PAYLOAD_SIZE)
                sender = Sender(windowSize, PAYLOAD_SIZE, filePath, GBN=False)
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
