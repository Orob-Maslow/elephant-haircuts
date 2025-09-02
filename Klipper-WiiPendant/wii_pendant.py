#!/usr/bin/python
import requests
import cwiid
import time
import json
import sys

class WiiPendant():
 '''
    This class will connect to the wiimode with the Bluetooth address specified in the input file
    This class relies on the setpoints in the /etc/cwiid/wminput/ folder of files that has the names of the input fields sent by the wiimote
    'BTN_1', 'BTN_2', 'BTN_A', 'BTN_B', 'BTN_DOWN', 'BTN_HOME', 'BTN_LEFT', 'BTN_MINUS', 'BTN_PLUS', 'BTN_RIGHT', 'BTN_UP', etc.
    Commands (with wiimote readable)
      move xy
        UP: 1 + right
        DOWN: 1 + left
        LEFT: 1 + up
        RIGHT: 1 + down
        Home: endstop and square all axes
      move Z
        UP: 2 + RIGHT
        DOWN: 2 + LEFT
      LED_Test
        LED_RED: A + UP
        LED_BLUE: A + DOWN
        LED_GREEN: A + LEFT
        LED_WHITE: A + RIGHT
      supervisory
        Set xy zero: 1 + HOME -> then A
        Set Z axis zero: 2 + HOME -> then A
        Disconnect wiimote: A + Z
        PLAY: Z + RIGHT
        PAUSE: Z + UP
        RESUME: Z + DOWN
        STOP: Z + LEFT       
 '''
 def __init__(self):
    '''
    init sets up the object properties that are used with the various functions below
    A, trigger, ztrigger, confirm, home, a, b, all help with making the buttons single press
    wm is the wiimote object
    wiiPendantConnect is the flag that lets the class know to try and reconnect
    '''   
    self.L = [1,2,4,8]
    self.DISTANCE = [0.1,1,10,100]
    self.Z = [0.1, 0.5, 1, 5]
    self.LED_ON = 2 # default is 10 mm.  range is  = 0.1, 1, 10, 100  Z_LED = 1 # default is 1 m.  range is 0.1, 0.5, 1, 5
    self.MINUS = 0
    self.PLUS = 0
    self.TRIGGER = 0
    self.ZTRIGGER = 0
    self.CONFIRM = -10
    self.StartTime = time.time()
    self.HOME = 0
    self.A = 0
    self.B = 0
    self.wm = None
    self.wiiPendantConnected = False
    self.ipaddress = "192.168.1.61"
    print("pendant initialized")
    if self.connect():
      self.Send("gcode","M117 pendant connect")
      self.Indicate("connected")
    else:
      print("no controllers found")
 
 def Send(self,set,command):
    '''
    sends a put request to the moonraker (web part of klipper) server at port 7125
    the /printer/gcode/script in the address directs the server what commands to interpret
    input is the command that is set by the wiimote button press
    '''
    #URL = "http://localhost:7125/printer/gcode/script"
    URL = "http://192.168.1.61:7125/printer/gcode/script"
    try:
      print("command: ")
      print(set, command)
      cmd = {"script":command}
      #print("cmd: ")
      #print(cmd)
      r=requests.post(URL,json=cmd)
      print (r.status_code)
      if (r.status_code == 200):
        print(f'data sent {command}')
      else:
        print(f'message not sent. code: {r.status_code}, details: {r.text}')
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else",err)
 
 def Indicate(self,setting):
    ledurl = "http://localhost:5000/set_color"
    
    # first decipher the setting / alarm : color
    # connecting - orange
    # connected - white
    # disconnecting - red
    # disconnected - OFF
    # moving -  blue
    # Zzero - yellow
    # connect-error - red
    # xhomed - green
    # yhomed - green
    # zhomed - green
    # probing - yellow
    # probed - purple
    # communication error - cyan
    colors = {
      "connecting":         {"red":"0",  "green":"0",  "blue":"127", "mode": "blink"},
      "connected":          {"red":"0",  "green":"0",  "blue":"127", "mode":"pulse1"},
      "disconnecting":      {"red":"255", "green":"0", "blue":"0"  , "mode": ""},
      "disconnected":       {"red":"0",  "green":"0",  "blue":"0"  , "mode": ""},
      "moving":             {"red":"0",  "green":"127","blue":"0"  , "mode": "blink"},
      "Zzero":              {"red":"0",  "green":"255","blue":"127", "mode":"pulse2"},
      "connect-error":      {"red":"255","green":"0",  "blue":"0"  , "mode": "blink"},
      "xhomed":             {"red":"0",  "green":"255","blue":"50" , "mode":"pulse2"},
      "yhomed":             {"red":"0",  "green":"255","blue":"100", "mode":"pulse2"},
      "zhomed":             {"red":"0",  "green":"255","blue":"150", "mode":"pulse2"},
      "probing":            {"red":"0",  "green":"255","blue":"127", "mode": "blink"},
      "probed":             {"red":"255","green":"0",  "blue":"200", "mode":"pulse2"},
      "communication error":{"red":"0",  "green":"200","blue":"200", "mode": "blink"}
    }
    try:
      data = colors[setting]
      print("command: ")
      print({setting}," ", data)
      r=requests.post(ledurl,json = data)
      print(r.status_code)
      if (r.status_code == 200):
         print(f'data sent {data}')
      else:
         print(f'message not sent. code: {r.status_code}, details: {r.text}')
      return(True)
    except requests.exceptions.HTTPError as errh:
      print ("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
      print ("Error Connecting:",errc) 
    except requests.exceptions.Timeout as errt:
      print ("Timeout Error:",errt)
    except requests.exceptions.RequestException as err: 
      print ("Request error",err)
    return(True)

 def connect(self):
      '''
      try to establish bluetooth communication with wii controller
      once connected, set LED to indicate distance
      set to button mode or it won't work at all
      if no connection, count and then return
      
      function returns 
         True when it connects
         False after 10 timeouts
      '''
      i=1
      while not self.wm:
        try:
          self.Indicate("connecting")
          self.wm=cwiid.Wiimote()
          self.wiiPendantConnected = True
          self.Indicate("connected")
          self.wm.led = self.L[self.LED_ON]
          self.wm.rpt_mode = cwiid.RPT_BTN
          return(True)
        except RuntimeError:
          if (i>10):
            return(False)
          #print ("Error opening wiimote connection" )
          self.Indicate("connect-error")
          time.sleep(5)
          print ("attempt " + str(i))
          i += 1
      return(True)
#end init
 def disconnect(self):
    print("Wiimote Disconnect")
    self.Indicate("disconnecting")
    #self.Send("system","disconnect")
    #self.wm = None
    self.wiiPendantConnected = False
    self.rumble(0)
    self.Indicate("disconnected")
    r=requests.post("http://localhost:5000/disable_pendant","command")
    self.wm = None
    #break
    #sys.exit(0)
    #return

 def rumble(self,mode=0):
  '''
  rumble shakes the wiimote when called.  short time delays vary the shake pattern
  '''
  if mode == 0: # start up heartbeat = 2 quick rumbles / prompt for confirmation
    self.wm.rumble=True
    time.sleep(.3)
    self.wm.rumble = False
    time.sleep(0.2)
    self.wm.rumble=True
    time.sleep(.3)
    self.wm.rumble = False
  if mode == 1: # shutdown or timeout
    self.wm.rumble=True
    time.sleep(.2)
    self.wm.rumble = False
    time.sleep(0.2)
    self.wm.rumble=True
    time.sleep(.6)
    self.wm.rumble = False
  if mode == 2: # shutdown or timeout
    self.wm.rumble=True
    time.sleep(.6)
    self.wm.rumble = False
    time.sleep(0.2)
    self.wm.rumble=True
    time.sleep(.2)
    self.wm.rumble = False
  if mode >= 30: # shutdown or timeout
    self.wm.rumble=True
    time.sleep(.8)
    self.wm.rumble = False
#end rumble
 def read_buttons(self):
   if (self.wiiPendantConnected == False):
      time.sleep(10)
      print ("connecting")
      self.Indicate("connecting")
      if (self.connect()):
          print("connected")
      return(True)
   while(self.wiiPendantConnected == True):
      # not using classic, this is if the remote is standing up though you hold it sideways
      if (self.CONFIRM > 0):
        elapsed = 1 - (time.time() - self.startTime)
        if elapsed > 5:
          self.rumble(1)  # cancelled due to timeout
          self.CONFIRM = - 10 # go back to normal
      if (self.wm.state['buttons'] & cwiid.BTN_A):
          if self.TRIGGER == 1:
            if self.CONFIRM > 0:
              self.TRIGGER = 0
              print("HOME POSITION CONFIRMED")
              self.rumble(1)
              self.Send("gcode","ZERO_XY")
              self.Indicate("Homed")
          elif self.ZTRIGGER == 1:
            self.ZTRIGGER = 0
            if self.CONFIRM > 0:
              print("Z PLUNGE RESET CONFIRMED")
              self.rumble(2)
              self.Send("gcode","ZERO_Z")
              self.Indicate("Zzero")
          elif (self.wm.state['buttons'] & cwiid.BTN_B):
            self.disconnect()
            break
          elif (self.wm.state['buttons'] & cwiid.BTN_RIGHT):
            print("LED WHITE")
            self.Send("gcode","LED_WHITE")
          elif (self.wm.state['buttons'] & cwiid.BTN_UP):
            print("LED RED")
            self.Send("gcode","LED_RED")
          elif (self.wm.state['buttons'] & cwiid.BTN_DOWN):
            print("LED BLUE")
            self.Send("gcode","LED_BLUE")
          elif (self.wm.state['buttons'] & cwiid.BTN_LEFT):
            print("LED GREEN")
            self.Send("gcode","LED_GREEN")
          else:
            self.A = 1
      else:
        self.A = 0
      if (self.wm.state['buttons'] & cwiid.BTN_B):
        if (self.B == 0):
            if (self.wm.state['buttons'] & cwiid.BTN_RIGHT):
                print("Wiimote Start")
                self.rumble(1)
                self.B = 1
                self.Send("gcode","startRun")
            if (self.wm.state['buttons'] & cwiid.BTN_UP):
                print("Wiimote Pause")
                self.rumble(1)
                self.B = 1
                self.Send("gcode","pauseRun")
            if (self.wm.state['buttons'] & cwiid.BTN_DOWN):
                print("Wiimote Resume")
                self.rumble(1)
                self.B = 1
                self.Send("gcode","resumeRun")
            if (self.wm.state['buttons'] & cwiid.BTN_LEFT):
                print("Wiimote Stop")
                self.rumble(1)
                self.B = 1
                self.Send("gcode","stopRun")
            elif (self.wm.state['buttons'] & cwiid.BTN_A):
                self.disconnect()
                break
        else:
          self.B = 0
      if (self.wm.state['buttons'] & cwiid.BTN_1):
        if self.TRIGGER == 0:
          if (self.wm.state['buttons'] & cwiid.BTN_UP):
            print("Wiimote Move -X")
            self.rumble(1)
            self.TRIGGER = 1
            self.Send("gcode","LEFT:" + str(self.DISTANCE[self.LED_ON]))
          if (self.wm.state['buttons'] & cwiid.BTN_DOWN):
            print("Wiimote Move +X")
            self.rumble(1)
            self.TRIGGER = 1
            self.RIGHT = 0
            self.Send("gcode","RIGHT:" + str(self.DISTANCE[self.LED_ON]))
          if (self.wm.state['buttons'] & cwiid.BTN_RIGHT):
            print("Wiimote Move +Y")
            self.rumble(1)
            self.TRIGGER = 1
            self.UP = 0
            self.Send("gcode","UP:" + str(self.DISTANCE[self.LED_ON]))
          if (self.wm.state['buttons'] & cwiid.BTN_LEFT):
            print("Wiimote Move -Y")
            self.rumble(1)
            self.TRIGGER = 1
            self.DOWN = 0
            self.Send("gcode","DOWN:" + str(self.DISTANCE[self.LED_ON]))
          if (self.wm.state['buttons'] & cwiid.BTN_HOME):
            print("Wiimote SET NEW Y HOME")
            self.rumble(1)
            self.TRIGGER = 1
            self.rumble(0)
            self.CONFIRM = 500
            self.startTime = time.perf_counter()
      else:
        self.TRIGGER = 0
      if (self.wm.state['buttons'] & cwiid.BTN_2):
        if self.ZTRIGGER == 0:
          self.TRIGGER = 0
          if (self.wm.state['buttons'] & cwiid.BTN_RIGHT):
            print("Wiimote MOVE +Z")
            self.rumble(2)
            self.ZTRIGGER = 1
            self.Send("gcode","RAISE:" + str(self.Z[self.LED_ON]))
          if (self.wm.state['buttons'] & cwiid.BTN_LEFT):
            print("Wiimote MOVE -Z")
            self.rumble(2)
            self.ZTRIGGER = 1
            self.Send("gcode","LOWER:"+ str(self.Z[self.LED_ON]))
          if (self.wm.state['buttons'] & cwiid.BTN_UP):
            print("Wiimote stop Z axis")
            self.rumble(2)
            self.ZTRIGGER = 1
            self.Send("gcode","STOPZ")
          if (self.wm.state['buttons'] & cwiid.BTN_HOME):
            print("Wiimote Reset Z AXIS to 0")
            self.rumble(2)
            self.ZTRIGGER = 1
            self.rumble(0)
            self.CONFIRM = 200
            self.startTime = time.perf_counter()
      else:
        self.ZTRIGGER = 0
        if (self.wm.state['buttons'] & cwiid.BTN_HOME):
          if self.HOME == 0:
            self.HOME = 1
            print ("Wiimote MOVE SLED TO HOME")
            self.Send("gcode","GO_HOME")
            self.rumble(1)
        else:
          self.HOME = 0
      if (self.wm.state['buttons'] & cwiid.BTN_MINUS):
        if self.MINUS == 0:
          self.MINUS = 1
          self.LED_ON = self.LED_ON - 1
          if self.LED_ON < 0:
            self.LED_ON = 3
          print("Sled Move Distance is ", self.DISTANCE[self.LED_ON])
          print("Z Distance is ", self.Z[self.LED_ON])
          self.wm.led = self.L[self.LED_ON]
      else:
        self.MINUS = 0
      if (self.wm.state['buttons'] & cwiid.BTN_PLUS):
        if self.PLUS == 0:
          self.PLUS = 1
          self.LED_ON = self.LED_ON + 1
          if self.LED_ON > 3:
            self.LED_ON = 0
          print("Sled move Distance is ", self.DISTANCE[self.LED_ON])
          print("Z Distance is ", self.Z[self.LED_ON])
          self.wm.led = self.L[self.LED_ON]
      else:
        self.PLUS = 0
   #return True
  #end button scan
#END class


#def main():
#  wp = WiiPendant() # instantiate a wiipendant object named wp
#  wp.read_buttons() # read the buttons in the wp object
#  if __name__ == "__main__":
#    main()
