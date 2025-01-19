import board
import digitalio
import time
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode


keyboard = Keyboard(usb_hid.devices)


mute_pin = board.GP19       # pin to connect button to
record_pin = board.GP7
misc_pin = board.GP10
mute_led_pin = board.GP15   # pin to connect LED to
record_led_pin = board.GP16


# Initializing LED
mute_led = digitalio.DigitalInOut(mute_led_pin)
mute_led.direction = digitalio.Direction.OUTPUT
record_led = digitalio.DigitalInOut(record_led_pin)
record_led.direction = digitalio.Direction.OUTPUT


# Initializing Button
mute = digitalio.DigitalInOut(mute_pin)
mute.direction = digitalio.Direction.INPUT
mute.pull = digitalio.Pull.UP


record = digitalio.DigitalInOut(record_pin)
record.direction = digitalio.Direction.INPUT
record.pull = digitalio.Pull.UP


misc = digitalio.DigitalInOut(misc_pin)
misc.direction = digitalio.Direction.INPUT
misc.pull = digitalio.Pull.UP


mute_bool = False
record_bool = False


while True:
	# Check if button is pressed and if it is, to press the Macros and toggle LED
    if mute.value:  
        print(" mute button Pressed")
        keyboard.press(Keycode.F14)
        time.sleep(0.15)
        keyboard.release(Keycode.F14)
        mute_bool = not mute_bool
        mute_led.value = mute_bool
    if record.value:
        print(" record button Pressed")
        keyboard.press(Keycode.F13)
        time.sleep(0.15)
        keyboard.release(Keycode.F13)
        record_bool = not record_bool
        record_led.value = record_bool
    if misc.value:
        print("misc button Pressed")
        keyboard.press(Keycode.F15)
        time.sleep(0.15)
        keyboard.release(Keycode.F15)
    time.sleep(0.1)