#!/usr/bin/env python3
import selectiveRepeatRunner
import os

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

            if window_size in range(1,65535):
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
                print("Go back N currently unsupported")
                decision = "x"
            elif decision == "1":
                filepath = prompt_for_file()
                window_size = prompt_for_window()
                #selectiveRepeatRunner.run()
                decision = "x"
            elif decision != "x":
                print("Decision not recognized.\n")

    except KeyboardInterrupt:
        print()
    pass

    
main()
