#
# Keyboard Emulator Using Maker Pi Pico and CircuitPython
#
# References and credit to
# . https://learn.adafruit.com/circuitpython-essentials/circuitpython-hid-keyboard-and-mouse
#
# Raspberry Pi Pico
# . [Maker Pi Pico] https://my.cytron.io/p-maker-pi-pico?tracking=idris
#
# Additional Libraries
# . adafruit_hid
#
# Update:
# 12 Feb 2021 . Tested with CircuitPython Pico 6.2.0-beta.2
#

import time

import board
import digitalio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

# A simple neat keyboard demo in CircuitPython

# The pins we'll use, each will have an internal pullup
keypress1_pin = board.GP28
keypress2_pins = [
    board.GP27,
    board.GP26,
    board.GP22,
    board.GP16,
    board.GP17,
    board.GP18,
    board.GP19,
    board.GP20,
    board.GP21
    ]
# Our array of key objects
key2_pin_array = []
# The Keycode sent for each button, will be paired with a control key
keys1_pressed = [
    Keycode.ONE,
    Keycode.TWO,
    Keycode.THREE,
    Keycode.FOUR,
    Keycode.FIVE,
    Keycode.SIX,
    Keycode.SEVEN,
    Keycode.EIGHT,
    Keycode.NINE,
    Keycode.ZERO,
    ]
keys2_pressed = [
    Keycode.F3,
    Keycode.F8,
    Keycode.F10,
    Keycode.ESCAPE,
    Keycode.SPACE,
    Keycode.UP,
    Keycode.RIGHT,
    Keycode.LEFT,
    Keycode.DOWN
    ]
#control_key = KeyCode.

# The keyboard object!
time.sleep(1)  # Sleep for a bit to avoid a race condition on some systems
keyboard1 = Keyboard(usb_hid.devices)
keyboard2 = Keyboard(usb_hid.devices)
keyboard1_layout = KeyboardLayoutUS(keyboard1)  # We're in the US ..
keyboard2_layout = KeyboardLayoutUS(keyboard2)
# Make all pin objects inputs with pullups
key1_pin = digitalio.DigitalInOut(keypress1_pin)
key1_pin.direction = digitalio.Direction.INPUT
key1_pin.pull = digitalio.Pull.UP
for pin in keypress2_pins:
    key2_pin = digitalio.DigitalInOut(pin)
    key2_pin.direction = digitalio.Direction.INPUT
    key2_pin.pull = digitalio.Pull.UP
    key2_pin_array.append(key2_pin)
# For most CircuitPython boards:
#led = digitalio.DigitalInOut(board.GP28)
# For QT Py M0:
# led = digitalio.DigitalInOut(board.SCK)
#led.direction = digitalio.Direction.OUTPUT
control_key = 0
#control_key = Keycode.SHIFT
print("Waiting for key pin.")
key1pin = 0
while True:
    # Check each pin
    if not key1_pin.value:  # Is it grounded?
        print("kbd1 Pin #{} is grounded.".format(i))

            # Turn on the red LED
            #led.value = True

            #while not key1_pin.value:
            #    pass  # Wait for it to be ungrounded!
            # "Type" the Keycode or string
        key = keys1_pressed[key1pin]  # Get the corresponding Keycode or string
        print("key1: ", key)
        if isinstance(key, str):  # If it's a string.
            keyboard1_layout.write(key)  # .Print the string
        else:  # If it's not a string. 
            keyboard1.press(control_key, key)  # "Press".
        keyboard1.release_all()  # ."Release"!

            # Turn off the red LED
            #led.value = False
    for key2_pin in key2_pin_array:
        if not key2_pin.value:  # Is it grounded?
            i = key2_pin_array.index(key2_pin)
            print("kbd2 Pin #{} is grounded.".format(i))

            # Turn on the red LED
            #led.value = True

            #while not key2_pin.value:
            #    pass  # Wait for it to be ungrounded!
            # "Type" the Keycode or string
            key = keys2_pressed[i]  # Get the corresponding Keycode or string
            print("key2: ",key)
            if isinstance(key, str):  # If it's a string.
                keyboard2_layout.write(key)  # .Print the string
            else:  # If it's not a string.
                keyboard2.press(control_key, key)  # "Press".
            keyboard2.release_all()  # ."Release"!

            # Turn off the red LED
            #led.value = False

    time.sleep(0.01)

    