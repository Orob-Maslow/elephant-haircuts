import board
import digitalio
import time
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

keyboard = Keyboard(usb_hid.devices)

esc_pin = board.GP17  # pin to connect button to
space_pin = board.GP16
up_pin = board.GP18
left_pin = board.GP19
right_pin = board.GP21
down_pin = board.GP20
view_pin = board.GP22
ride_on_pin = board.GP28
enter_pin = board.GP27
screen_capture_pin = board.GP26

# Initializing Button
esc = digitalio.DigitalInOut(esc_pin)
esc.direction = digitalio.Direction.INPUT
esc.pull = digitalio.Pull.UP

space = digitalio.DigitalInOut(space_pin)
space.direction = digitalio.Direction.INPUT
space.pull = digitalio.Pull.UP

up = digitalio.DigitalInOut(up_pin)
up.direction = digitalio.Direction.INPUT
up.pull = digitalio.Pull.UP

left = digitalio.DigitalInOut(left_pin)
left.direction = digitalio.Direction.INPUT
left.pull = digitalio.Pull.UP

right = digitalio.DigitalInOut(right_pin)
right.direction = digitalio.Direction.INPUT
right.pull = digitalio.Pull.UP

down = digitalio.DigitalInOut(down_pin)
down.direction = digitalio.Direction.INPUT
down.pull = digitalio.Pull.UP

view = digitalio.DigitalInOut(view_pin)
view.direction = digitalio.Direction.INPUT
view.pull = digitalio.Pull.UP
view_number = 1

ride_on = digitalio.DigitalInOut(ride_on_pin)
ride_on.direction = digitalio.Direction.INPUT
ride_on.pull = digitalio.Pull.UP

enter = digitalio.DigitalInOut(enter_pin)
enter.direction = digitalio.Direction.INPUT
enter.pull = digitalio.Pull.UP

screen_capture = digitalio.DigitalInOut(screen_capture_pin)
screen_capture.direction = digitalio.Direction.INPUT
screen_capture.pull = digitalio.Pull.UP

while True:
    # Check if button is pressed and if it is, to press the Macros and toggle LED
    if not esc.value:
        print(" esc button Pressed")
        keyboard.press(Keycode.ESCAPE)
        time.sleep(0.15)
        keyboard.release(Keycode.ESCAPE)
    if not space.value:
        print(" space button Pressed")
        keyboard.press(Keycode.SPACE)
        time.sleep(0.15)
        keyboard.release(Keycode.SPACE)
    if not up.value:
        print("up arrow Pressed")
        keyboard.press(Keycode.UP_ARROW)
        time.sleep(0.15)
        keyboard.release(Keycode.UP_ARROW)
    if not left.value:
        print("left arrow Pressed")
        keyboard.press(Keycode.LEFT_ARROW)
        time.sleep(0.15)
        keyboard.release(Keycode.LEFT_ARROW)
    if not right.value:
        print("right arrow Pressed")
        keyboard.press(Keycode.RIGHT_ARROW)
        time.sleep(0.15)
        keyboard.release(Keycode.RIGHT_ARROW)
    if not down.value:
        print("down arrow Pressed")
        keyboard.press(Keycode.DOWN_ARROW)
        time.sleep(0.15)
        keyboard.release(Keycode.DOWN_ARROW)
    if not ride_on.value:
        print(" ride_on button Pressed")
        keyboard.press(Keycode.F3)
        time.sleep(0.15)
        keyboard.release(Keycode.F3)
    if not enter.value:
        print(" ENTER button Pressed")
        keyboard.press(Keycode.ENTER)
        time.sleep(0.15)
        keyboard.release(Keycode.ENTER)
    if not screen_capture.value:
        print(" screen capture button Pressed")
        keyboard.press(Keycode.F10)
        time.sleep(0.15)
        keyboard.release(Keycode.F10)
    if not view.value:
        print(" view button Pressed")
        if view_number == 2:
            keyboard.press(Keycode.TWO)
            time.sleep(0.15)
            keyboard.release(Keycode.TWO)
        elif view_number == 3:
            keyboard.press(Keycode.THREE)
            time.sleep(0.15)
            keyboard.release(Keycode.THREE)
        elif view_number == 4:
            keyboard.press(Keycode.FOUR)
            time.sleep(0.15)
            keyboard.release(Keycode.FOUR)
        elif view_number == 5:
            keyboard.press(Keycode.FIVE)
            time.sleep(0.15)
            keyboard.release(Keycode.FIVE)
        elif view_number == 6:
            keyboard.press(Keycode.SIX)
            time.sleep(0.15)
            keyboard.release(Keycode.SIX)
        elif view_number == 7:
            keyboard.press(Keycode.SEVEN)
            time.sleep(0.15)
            keyboard.release(Keycode.SEVEN)
        elif view_number == 8:
            keyboard.press(Keycode.EIGHT)
            time.sleep(0.15)
            keyboard.release(Keycode.EIGHT)
        elif view_number == 9:
            keyboard.press(Keycode.NINE)
            time.sleep(0.15)
            keyboard.release(Keycode.NINE)
        elif view_number == 0:
            keyboard.press(Keycode.ZERO)
            time.sleep(0.15)
            keyboard.release(Keycode.ZERO)
        elif view_number == 1:
            keyboard.press(Keycode.ONE)
            time.sleep(0.15)
            keyboard.release(Keycode.ONE)
        view_number = view_number + 1
        if view_number > 9:
            view_number = 0
    time.sleep(0.1)
