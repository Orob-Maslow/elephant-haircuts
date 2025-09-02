#!/usr/bin/python3
#This is for the pendant and led separate thread launch to auto poll the bluetooth and then connect and send to klipper
from gpiozero import RGBLED
import threading
import time
from wii_pendant import WiiPendant
from flask import Flask, request, jsonify
import RPi.GPIO as GPIO
from time import sleep

app = Flask(__name__)

# Shared variable, protected by a Lock for thread-safety
shared_data = {"wii_connect": "none"}
Threadrun = True
data_lock = threading.Lock()
wp = None
# Function for the background thread
def wii_worker():
    global shared_data
    global Threadrun
    while Threadrun == True:
        with data_lock:
            wii_connect = shared_data["wii_connect"]
        if wii_connect != "none":
            print(f"Background worker received command: {wii_connect}")
            # Simulate work based on the command
            if wii_connect  == "true":
                print("Starting connection")
                wp = WiiPendant() # instantiate a wiipendant object named wp
                print("Pendant started")
                wp.read_buttons() # read the buttons in the wp object
            #    print("pendant running")
            #elif wii_connect == "false":
                print("Stopping connection...")
             #   with data_lock:
             #     Threadrun = False
                wp.WiiPendantConnected = False
                print("pendant shutdown complete")
                wp = None
            # Reset the command after processing
            with data_lock:
                shared_data = {"wii_connect":"none"}
        time.sleep(1) # Check for new commands every second

# Start the wii background thread
wii_thread = threading.Thread(target=wii_worker)
wii_thread.daemon = True # Allow the main program to exit even if this thread is running
wii_thread.start()

# Example: RGBLED(red_pin, green_pin, blue_pin)
led = RGBLED(2, 3, 4) # Example: GPIO 17 for Red, 27 for Green, 22 for Blue

def set_pin(pin,state):
  if state == 1:
    GPIO.output(pin, GPIO.HIGH)
  elif state == 0:
    GPIO.output(pin, GPIO.LOW)

@app.route('/set_color', methods=['POST'])
def set_color():
    data = request.get_json()
    print("json data received: ", data)
    red_val =  float(data.get('red')) / 255
    print("red value is : ", red_val)
    green_val = float(data.get('green')) / 255
    print("green value is : ", green_val)
    blue_val = float(data.get('blue')) / 255
    print("blue value is : ", blue_val)
    led.color = (red_val, green_val, blue_val)
    mode = data.get('mode')
    if (mode == "blink"):
     led.blink()
    elif (mode == "pulse1"):
     led.pulse(fade_in_time = 3,fade_out_time = 3)
    elif (mode == "pulse2"):
     led.pulse(fade_in_time= 0.5,fade_out_time = 0.5)
    return "Color set successfully!"

@app.route('/enable_pendant', methods=['POST'])
def enable_pendant():
    wiiPendant = True
    print("kickstart pendant process (TOTALLY SEPARATE)")
    global shared_data
    with data_lock:
      shared_data= {"wii_connect":"true"}
    return "\r\nenabling pendant!\r\n"

@app.route('/disable_pendant', methods=['POST'])
def disable_pendant():
    wiiPendant = False
    print("pendant shutdown")
    global shared_data
    with data_lock:
      shared_data = {"wii_connect":"false"}
    print("thread ending sent")
#    wii_thread.join()
#    print("thread ended")
#    wii_thread.start()
#    print("thread restarted")
    return "\r\ndisabling pendant\r\n"

if __name__ == '__main__':
    try:
      app.run(host='0.0.0.0', port=5000, debug=False)
    finally:
      print("Cleaning up GPIO pins...")
      GPIO.cleanup() # Reset all GPIO pins to their default state
      print("GPIO cleanup complete.")
