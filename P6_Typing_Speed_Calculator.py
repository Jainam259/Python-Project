# Typing Speed Calculator

from time import *
import random

def mistake(par,user):
    error = 0
    for i in range(len(user)):
        try:
            if par[i] != user[i]:
                error = error + 1
        except:
            error = error + 1
    return error

def speed_time(time_s,time_e,user):
    time_delay = time_e - time_s
    time_r = round(time_delay,2)
    speed = len(user) / time_r
    return round(speed)
        

print("***** Typing Speed Calculator *****")
while True:
    ans = input("Do you want to start the game? (y/n):").lower()
    if ans == 'y':
        test = [
            "The quick brown fox jumps over the lazy dog.",
            "A journey of a thousand miles begins with a single step.",
            "To be or not to be, that is the question.",
            "All that glitters is not gold.",
            "I think, therefore I am.",
            "The only thing we have to fear is fear itself.",
            "In the middle of difficulty lies opportunity."]

        t1 = random.choice(test)
        print(t1)
        print()
        print()

        time1 = time()
        tinput = input("Enter:")
        time2 = time()

        print("Speed :",speed_time(time1,time2,tinput)," W/Sec")
        print("Error :",mistake(t1,tinput))
    elif ans == 'n':
        print("Thank you for using the Typing Speed Calculator.")
        break
    else:
        print("Invalid input. Please enter 'y' or 'n'.")