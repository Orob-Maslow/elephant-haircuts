from gpiozero import RGBLED
from time import sleep

#app = Flask(__name__)

# Define the GPIO pins for your RGB LED (replace with your actual pin numbers)
# Example: RGBLED(red_pin, green_pin, blue_pin)
led = RGBLED(2, 3, 4) # Example: GPIO 2 for Red, 3 for Green, 4 for Blue

#@app.route('/')
#def index():
#    return render_template('index.html')

#@app.route('/set_color', methods=['POST'])
def set_color(r,g,b):
    red_val = float(r) / 255
    green_val = float(g) / 255
    blue_val = float(b) / 255
    
    led.color = (red_val, green_val, blue_val)
#    return "Color set successfully!"
    print("Color set successfully!")

#@app.route('/turn_off', methods=['POST'])
def turn_off():
    led.off()
#    return "LED turned off!"
    print("LED turned off!")

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=5000, debug=True)
    while (1):
      inputtext = input("enter 1 for green 2 for blue and 3 fore red:")
      if(inputtext == '1'):
          set_color(0,255,0)
      elif(inputtext == '2'):
          set_color(0,0,255)
      elif(inputtext == '3'):
          set_color(255,0,0)
