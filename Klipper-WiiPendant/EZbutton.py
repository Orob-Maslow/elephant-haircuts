#!/usr/bin/python3
from gpiozero import Button
from signal import pause
import requests
import time
import subprocess
from subprocess import check_call
import json
import os
from os import system, name   # import only system from os 

print("setting up button")
runpause = 0
wiiPendantPresent = False
clidisplay = False
flag = '0'
Buttons = []
index = 0
moving = False
    
def Exit():
    print ("EXIT")
    #Send("system:exit")
    os._exit(0)

def Shutdown():
    print ("shutting down system from button press")
    check_call(['sudo', 'poweroff'])

def startPendant():  
    if (wiiPendantPresent):
        print("kickstart pendant process (TOTALLY SEPARATE)")
        try:
            subprocess.run(['sudo','/home/pi/EZpendant-start.sh'])
            print ('subprocess started Pendant service')
	    wiiPendantPresent = True
        except:
            print ('error starting pendant sub process')
            wiiPendantPresent = False
            continue

def setup():
    #retdata = Get("GPIO", "GPIO")
    button = Button(27)
    button.when_pressed = startPendant
    
setup()

bad_chars = "'"
#btnWiimote.when_pressed = Wii
print("waiting for button press")
while True:
    time.sleep (3)
    try:
        if (wiiPendantPresent == True):
            if (wiiconnected == True):
                print("wiimote: attached")
            else:
                print("wiimote: none")                   
    exception as e:
        print(e)
        continue
