from flask import Flask, render_template, request
from gpiozero import RGBLED
import RPi.GPIO as GPIO
from time import sleep
import subprocess

app = Flask(__name__)

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
     led.pulse(fade_in_time = 1,fade_out_time = 0.5)
    elif (mode == "pulse2"):
     led.pulse(fade_in_time= 0.5,fade_out_time = 0.5)
    return "Color set successfully!"

@app.route('/enable_pendant', methods=['POST'])
def enable_pendant():
    wiiPendant = True
    print("kickstart pendant process (TOTALLY SEPARATE)")
    try:
      #result = subprocess.run(['sudo','/home/pi/wp/wp.sh'],capture_output=True,text=True,check=True)
      #set a flag here and return a response then start the program
      subprocess.run(['sudo','/home/pi/wp/wp.sh'],capture_output=True,text=True,check=True)
      print('subprocess started Pendant program... not service')
      #print('output:')
      #print(result.stdout)
      wiiPendantPresent = True
      #if result.stderr:
      #  print("\r\nstd error:")
      #  print(result.stderr)
    except subprocess.CalledProcessError as e:
      print (f"Command failed iwth exit code ",e.returncode)
      print (f"Standard Output: {e.stdout}")
      print (f"Standard Error: {e.stderr}")
      wiiPendantPresent = False
      #continue

    return "enabling pendant!\r\n"

@app.route('/disable_pendant', methods=['POST'])
def disable_pendant():
  pass

@app.route('/turn_off', methods=['POST'])
def turn_off():
    led.off()
    return "LED turned off!"

if __name__ == '__main__':
    try:
      app.run(host='0.0.0.0', port=5000, debug=False)
    finally:
      print("Cleaning up GPIO pins...")
      GPIO.cleanup() # Reset all GPIO pins to their default state
      print("GPIO cleanup complete.")
