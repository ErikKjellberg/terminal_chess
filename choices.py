import time
import sys

def alt_choice(message, alternatives, responses=None):
    print(message)
    for i, alt in enumerate(alternatives):
        print(str(i+1)+". "+alt)
    chosen = False
    while not chosen:
        c = input("> ")
        try:
            if c.upper() == "QUIT":
                return -1
            if int(c) >= 1 and int(c) <= len(alternatives):
                c = int(c)-1
                chosen = True
            else:
                print("I don't understand.")
        except ValueError:
            print("Enter a number please.")
    if responses != None:
        responses[c]()
    else:
        return c

def text_file_input(message):
    print(message)
    chosen = False
    while not chosen:
        file_name = input("> ")
        if all(ord(s) < 128 for s in file_name):
            chosen = True
        else:
            print("Enter only ASCII characters please.")
    file = file_name+".txt"
    return file
