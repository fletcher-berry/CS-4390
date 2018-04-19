#!/usr/bin/env python3.6
import selectiveRepeatRunner
from gbn_sender import GbnSender
from gbn_receiver import GbnReceiver
import os
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
                #filePath = prompt_for_file()
                #windowSize = prompt_for_window()
                filePath = "a.txt"
                windowSize = 32

                # temporary setup 
                gbns = GbnSender(windowSize, filePath, packetSize = 100)
                gbnr = GbnReceiver(packetSize = 100)

                ps = Process(target=gbns.run, args=())
                pr = Process(target=gbnr.run, args=())

                ps.start()
                pr.start()

                pr.join()
                ps.join()
            
                break

            elif decision == "1":
                filepath = prompt_for_file()
                windowSize = prompt_for_window()
                selectiveRepeatRunner.run(windowSize, 50, filepath)
                while True:     # makes sure process doesn't terminate
                    pass

            elif decision != "x":
                print("Decision not recognized.\n")

    except KeyboardInterrupt:
        print()
    pass

main()
