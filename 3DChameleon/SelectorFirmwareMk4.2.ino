/*  major changes from 4.1a to 4.2 by Rob Owings Dec 2024
//  OLED 128x32
//  added manual jog commands for pulse 9+
//  change from button to command pin mode for klipper board direct wire
//  first pin only selects filament or mode
//  second pin loads but only when "activated"
//  third pin unloads but only when "activated"
//  
*/

// November 28, 2024

/* 3DChameleon Mk4.1a Firmware

Copyright 2024 William J. Steele

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated 
documentation files (the “Software”), to deal in the Software without restriction, including without limitation 
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, 
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions 
of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED 
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF 
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
DEALINGS IN THE SOFTWARE.

Pin1 command mode selector

#1 - 1 select
#2 - 2 select
#3 - 3 select
#4 - 4 select
#5 - home and Load filament
#6 - Unload and home
#7 - Home - go to neutral position
#8 - cut
#9 - activate 0 and enable jogging
#10 - activate 1 and enable jogging
#11 - activate 2 and enable jogging
#12 - activate 3 and enable jogging
*/
//#include <SSD1306Ascii.h> //i2C OLED
//#include <SSD1306AsciiWire.h> //i2C OLED
//#include <SparkFunSX1509.h> // sparkfun i/o expansion board - used for additional filament sensors as well as communications with secondary boards
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Wire.h>
#include <SPI.h>
#include <Servo.h>

#define SCREEN_WIDTH 128 // OLED display width, in pixels
//#define SCREEN_HEIGHT 64 // OLED display height, in pixels
#define SCREEN_HEIGHT 32 // OLED display height, in pixels
// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
#define OLED_RESET  -1 // Reset pin # (or -1 if sharing Arduino reset pin)
#define OLED_I2C_ADDRESS 0x3C
//SSD1306AsciiWire oled;
Adafruit_SSD1306 oled(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// define sparkfun io expansion
const byte SX1509_ADDRESS = 0x3E; // SX1509 I2C address
#define SX1509_FILAMENT_0 0
#define SX1509_FILAMENT_1 1
#define SX1509_FILAMENT_2 2
#define SX1509_FILAMENT_3 3
#define SX1509_OUTPUT 4
//SX1509 io;                        // Create an SX1509 object to be used throughout
// defines pins numbers - 3D Chameleon Board
#define extEnable 0
#define extStep 1
#define extDir 2
#define selEnable A0
#define selStep A1
#define selDir A2
#define trigger A3          // button
#define s_limit A4
#define filament A5
#define load_switch 12      //MISO
#define unload_switch 13    //SCK

const int counterclockwise = HIGH;
const int clockwise = !counterclockwise;
const int stepsPerRev = 200;
const int microSteps = 16;
const int speedDelay = 170;
const int fastSpeed = speedDelay/2; // double time
const int defaultBackoff = 10;
Servo filamentCutter;               // create servo object to control a servo
int cutterPos = 0;                  // variable to store the servo position
bool reverseServo = true;
int currentExtruder = -1;
int nextExtruder = 0;
int lastExtruder = -1;
//int tempExtruder = -1;
int seenCommand = 0;
int prevCommand = 0;
int loaderMode = 2;                  //(0= direct drive, 1=loader/unloader, 2=loader/unloader with press)
int jogMode = 0;                     // this is for when channels are activated..  0 is disabled, 1 is enabled
int jog_channel;                     // this is the jog channel
//long triggerTime = 300;
long triggerTime = 30;
long pulseTime = (triggerTime / 2);
long distance = 10;
int direction = 0;
long unloadDistance = stepsPerRev * microSteps * distance;  // this is 10 revs - about 10"
long loadDistance   = unloadDistance * 1.1;           // this is 11 revs - about 11"
int address = 0;
byte value;
long idleCount = 0;
bool logoActive = false;
bool T0Loaded = false;
bool T1Loaded = false;
bool T2Loaded = false;
bool T3Loaded = false;
bool displayEnabled = false;
bool ioEnabled = false;   //int sensorEnabled = 0;
long randomNumber = 0;

void setup(){
  Wire.begin(); //start i2C  
	Wire.setClock(400000L); //set clock
 /* if (io.begin(SX1509_ADDRESS) == true)  // set up IO expander
  {
    io.pinMode(SX1509_FILAMENT_0, INPUT_PULLUP);
    io.pinMode(SX1509_FILAMENT_1, INPUT_PULLUP);
    io.pinMode(SX1509_FILAMENT_2, INPUT_PULLUP);
    io.pinMode(SX1509_FILAMENT_3, INPUT_PULLUP);
    io.pinMode(SX1509_OUTPUT, OUTPUT);
    ioEnabled = true;
  }*/
  // enable OLED display
  oled.begin(SSD1306_SWITCHCAPVCC, OLED_I2C_ADDRESS);
  // wait for it to start up
  delay(50);
  // welcome screen
  oled.clearDisplay();
  oled.setTextSize(1);                // Normal 1:1 pixel scale
  oled.setTextColor(SSD1306_WHITE);   // Draw white text
  oled.setCursor(0, 0);               // Start at top-left corner
  oled.cp437(true); 
  oled.clearDisplay();
  oled.println("   Johnny 5 colors!"); //print a welcome message  
  oled.println("  3DChameleon Mk4");   //print a welcome message
  oled.println("     Pro v4.2");
  oled.println("  - R. Owings -");
  oled.display();
  delay(3000);
  displayText(9, "       Ready!");
  oled.display();
  seenCommand = 0;
  pinMode(extEnable, OUTPUT);
  pinMode(extStep, OUTPUT);
  pinMode(extDir, OUTPUT);
  pinMode(selEnable, OUTPUT);
  pinMode(selStep, OUTPUT);
  pinMode(selDir, OUTPUT);
  // set up the button / switches
  pinMode(trigger, INPUT_PULLDOWN);       // selector
  pinMode(load_switch, INPUT_PULLDOWN);   // load
  pinMode(unload_switch, INPUT_PULLDOWN); // unload
  // a little override here... we're using the two inputs as I2C instead
  pinMode(s_limit, OUTPUT);             // I2C for display
  pinMode(filament, OUTPUT);            // I2C for display
  // lock the selector by energizing it
  digitalWrite(selEnable, HIGH);
  //connectGillotine();                 // make sure filament isn't blocked by gillotine
  //cutFilament();
  //disconnectGillotine();
  prevCommand = 0;
}

int lastLoop = 0;

void loop(){
  static uint32_t lastTime = 0;
  seenCommand = 0;
  idleCount++;
  // process button press
  if (digitalRead(trigger) == 0){
    idleCount = 0;
    logoActive = false;
    unsigned long nextPulse;
    unsigned long pulseCount = 0;
    unsigned long commandCount = 0;
    while (digitalRead(trigger) == 0){ // keep counting (and pulsing) until button is released
      if(pulseCount<pulseTime){
        pulseCount++;
        displayCommand(pulseCount);
        if(pulseCount>1) vibrateMotor();
        if(jogMode == 1){
          jogMode == 0;
          digitalWrite(extEnable, HIGH);// ok, done pressing button, so make sure we're not energized (high is no, low is yes)
        }
      }
      delay(40);  // each pulse is 40+ milliseconds apart 
    }
    processCommand(pulseCount); // ok... execute whatever command was caught (by pulse count)
    pulseCount = 0;
  }
  if (jogMode == 1){
    if (digitalRead(load_switch == 0)){
      if(currentExtruder<2){
        direction = counterclockwise;
      }else{
        direction = clockwise;
      }
      digitalWrite(extDir, direction); // Enables the motor to move in a particular direction
      while (digitalRead(load_switch == 0))     {
         // this is how we pulse the motor to get it to step
        digitalWrite(extStep, HIGH);
        delayMicroseconds(fastSpeed);
        digitalWrite(extStep, LOW);
        delayMicroseconds(fastSpeed);
      }
    }
    if (digitalRead(unload_switch == 0)){
      if(currentExtruder<2){
        direction = clockwise;
      }else{
        direction = counterclockwise;
      }
      digitalWrite(extDir, direction); // Enables the motor to move in a particular direction
      while (digitalRead(unload_switch == 0)){
         // this is how we pulse the motor to get it to step
        digitalWrite(extStep, HIGH);
        delayMicroseconds(fastSpeed);
        digitalWrite(extStep, LOW);
        delayMicroseconds(fastSpeed);
      }
    }
  }
  // updates IO block, duh!  No really, grabs the state of the sparkfun gpio expansion
  //updateIOBlock();
  // each loop adds 50ms delay, so that gets added AFTER the command is processed before the next one can start
  delay(30);
}
/*void updateIOBlock(){ // read the sparkfun SX1509 io
    if(ioEnabled)    {
      T0Loaded = io.digitalRead(SX1509_FILAMENT_0);
      T1Loaded = io.digitalRead(SX1509_FILAMENT_1);
      T2Loaded = io.digitalRead(SX1509_FILAMENT_2);
      T3Loaded = io.digitalRead(SX1509_FILAMENT_3);
    }
}*/
// display command for each button pulse
void displayCommand(long commandCount){
  switch(commandCount){
  case 2: // 180
    displayText(9, "  Selected T0");
    break;
  case 3: // 220
    displayText(9, "  Selected T1");
    break;
  case 4: // 285
    displayText(9, "  Selected T2");
    break;
  case 5: // 395
    displayText(9, "  Selected T3");
    break;
  case 6: // 505
    displayText(9, " Home/Load/T0");
    break;
  case 7: // 610
    displayText(9, "  Unload/Home");
    break;
  case 8: // 715
    displayText(9, "     Home");
    break;  
  case 9: //    820
    displayText(9, "      Cut");
    break;
  case 10: //   880
    displayText(9, "  Activate 0"); // this is not for load / unload, but jogging  use home to deactivate
    break;
  case 11: //   925
    displayText(9, "  Activate 1"); // this is not for load / unload, but jogging  use home to deactivate
    break;
  case 12: //   1030
    displayText(9, "  Activate 2"); // this is not for load / unload, but jogging  use home to deactivate
    break;
  case 13: //  1135
    displayText(9, "  Activate 3"); // this is not for load / unload, but jogging  use home to deactivate
    break;
  case 14: // 9 * 30 = 270 // NEXT
    displayText(9, "    Next");
    break;
  default:
    displayText(9, "  No Command");
    break;
  }
  
   // oled.display();
}
// execute the pulse count command
void processCommand(long commandCount){ 
  switch (commandCount){  // select case for commands
  case 2: // unload current, switch to #0, load
    displayText(17, "   T0 Selected");
    currentExtruder = 0;
    processMoves();
    displayText(25, "     Idle - T0");
    break;
  case 3: // unload current, switch to #1, load
    displayText(17, "   T1 Selected");
    currentExtruder = 1;
    processMoves();
    displayText(25, "     Idle - T1");
    break;
  case 4: // unload current, switch to #3, load
    displayText(17, "   T2 Selected");
    currentExtruder = 2;
    processMoves();
    displayText(25, "     Idle - T2");
    break;
  case 5: // unload current, switch to #4, load
    displayText(17, "    T3 Selected");
    currentExtruder = 3;
    processMoves();
    displayText(25, "      Idle - T3");
    break;
  case 6: //home and reload #1
    displayText(17, "      Homing...");
    homeSelector();
    displayText(9, "   Press to Load T0");
    gotoExtruder(0, 0);
    if(loaderMode>0)rotateExtruder(clockwise, loadDistance);
    if(loaderMode>0)gotoExtruder(0, 1);
    currentExtruder = 0;
    lastExtruder = 0;
    displayText(25, "      Idle - T0");
    break;
  case 7: // unload current and rehome selector
    displayText(17, "     Cutting...");
    connectGillotine();
    cutFilament();
    switch(lastExtruder){
      case 0:
        displayText(9, "  Press to Unload T0");
        break;
      case 1:
        displayText(9, "  Press to Unload T1");
        break;
      case 2:
        displayText(9, "  Press to Unload T2");
        break;
      case 3:
        displayText(9, "  Press to Unload T3");
        break;
    } 
    if(loaderMode>0)gotoExtruder((lastExtruder==3?2:lastExtruder+1),lastExtruder);
    if(lastExtruder<2){
      if(loaderMode>0)rotateExtruder(counterclockwise, unloadDistance);
    }else{
      if(loaderMode>0)rotateExtruder(clockwise, unloadDistance);
    }
    disconnectGillotine();
    displayText(25, "        Idle");
    break;
  case 8:
    displayText(17, "     Homing...");
    homeSelector();
    displayText(25, "        Idle");
    break;
  case 9: // cut filament
    displayText(17, "     Cutting...");
    connectGillotine();
    cutFilament();
    displayText(25, "        Idle");
    break;
  case 10: // activate current extruder for jogging (no cutting)
    displayText(25, "   no cut...");
    //connectGillotine();
    //cutFilament();
    displayText(25, "   Jogging 0");
    jogMode = 1;
    jogHome();
    processJog(0);
    displayText(25, "        Idle");
    break;
  case 11: // activate current extruder for jogging (no cutting)
    displayText(25, "   no cut...");
    //connectGillotine();
    //cutFilament();
    displayText(25, "   Jogging 1");
    jogMode = 1;
    processJog(1);
    displayText(25, "        Idle");
    break;
  case 12: // activate current extruder for jogging (no cutting)
    displayText(25, "   no cut...");
    //connectGillotine();
    //cutFilament();
    displayText(25, "   Jogging 2");
    jogMode = 1;
    processJog(2);
    displayText(25, "        Idle");
    break;
  case 13: // activate current extruder for jogging (no cutting)
    displayText(25, "   no cut...");
    //connectGillotine();
    //cutFilament();
    displayText(25, "   Jogging 3");
    jogMode = 1;
    processJog(3);
    displayText(25, "        Idle");
    break;
  case 14: // next filament selection
    displayText(30, "     Cutting...");
    connectGillotine();
    cutFilament();
    displayText(30, "     Next Tool");
    currentExtruder++;
    if(currentExtruder==4)currentExtruder=0;
    processMoves();
    displayText(35, "        Idle");
    break;
  default:
    displayText(25, "       Clear");
    delay(2000);
    displayText(25, "        Idle");
    break;
  }
}

void displayText(int offset, String str){  // just the routine to update the OLED
  oled.clearDisplay();
  oled.setCursor(0, 0);     // Start at top-left corner
  oled.println(" 3DChameleon Mk4.2"); //print a welcome message
  oled.setCursor(0,offset);     // Start at top-left corner
  oled.println(str);
  if(ioEnabled){
    if(T0Loaded){
      oled.print("0  ");
    }else{
      oled.print("+  ");
    }
    if(T1Loaded){
      oled.print("1  ");
    }else{
      oled.print("+  ");
    }
    if(T2Loaded){
      oled.print("2  ");
    }else{
      oled.print("+  ");
    }
    if(T3Loaded){
      oled.println("3");
    }else{
      oled.println("+");
    }
  }else{
    oled.setCursor(0,25);
    oled.println("-  -  -  -  -  -  -");
  }
  oled.display();
}
void processJog(int channel_number){
  switch(channel_number){
      case 0:
        displayText(9, "  C0 Active");
        jog_channel = 0;
        break;
      case 1:
        displayText(9, "  C1 Active");
        jog_channel = 1;
        break;
      case 2:
        displayText(9, "  C2 Active");
        jog_channel = 2;
        break;
      case 3:
        displayText(9, "  C3 Active");
        jog_channel = 3;
        break;
    }
  jogHome();
  gotoExtruder(-2,channel_number);
  digitalWrite(extEnable, LOW);  // lock the motor
}
// real work is here
void processMoves(){
  // make sure we have a real extruder selected
  if(lastExtruder>-1){
    displayText(17, "     Cutting...");
    connectGillotine();
    cutFilament();
    // ok... then wait for the 2nd button press to unload it
    switch(lastExtruder){
      case 0:
        displayText(9, "  Press to Unload C0");
        break;
      case 1:
        displayText(9, "  Press to Unload C1");
        break;
      case 2:
        displayText(9, "  Press to Unload C2");
        break;
      case 3:
        displayText(9, "  Press to Unload C3");
        break;
    } 
    // roll over to first if on last
    if( loaderMode>0 ) gotoExtruder( ( lastExtruder==3 ? 2 : (lastExtruder+1)), lastExtruder);
    // this determines which direction to move the motor, 0-1 : counterclockwise, 2-3 : clockwise
    if(lastExtruder<2){
      if(loaderMode>0)rotateExtruder(counterclockwise, unloadDistance);
    }else{
      if(loaderMode>0)rotateExtruder(clockwise, unloadDistance);
    } 
  }else{
    lastExtruder = 0;
  }
  disconnectGillotine();
  // tell it to actually execute that command now
  gotoExtruder(lastExtruder, currentExtruder);
  // ok... filament unloaded, time to load the new... so tell the user
  switch(currentExtruder){
    case 0:
      displayText(9, "   Press to Load C0");
      break;
    case 1:
      displayText(9, "   Press to Load C1");
      break;
    case 2:
      displayText(9, "   Press to Load C2");
      break;
    case 3:
      displayText(9, "   Press to Load C3");
      break;
  }
  // same (but inversed) logic for motor direction
  if(currentExtruder<2){
    if(loaderMode>0)rotateExtruder(clockwise, loadDistance);
  }else{
    if(loaderMode>0)rotateExtruder(counterclockwise, loadDistance);
  }
  // if we're loading, then load it now
  if(loaderMode>0)gotoExtruder(currentExtruder, (currentExtruder==3?2:currentExtruder+1));
  // everybody remember where we parked!
  lastExtruder = currentExtruder;
}
// this function simply moves from the currentCog to the targetCog is the best way
void gotoExtruder(int currentCog, int targetCog){
  int newCog = targetCog - currentCog;
  // ok... which way
  int newDirection = counterclockwise;
  if(newCog<0){
    // we need to move the other way
    newDirection = clockwise;
    //and since we know we went too far... let's go the other way in steps as well
    newCog = currentCog - targetCog;
  }
  // if we're already on the current cog, then do nothing
  if(newCog > 0){    
    // advance tool targetCog times
    for(int i=0; i<newCog; i++){
      rotateSelector(newDirection, (stepsPerRev / 4) * microSteps);
    }
  }
}
// move the extruder motor in a specific direction for a specific distance (unless it's a "until button is not pressed")
void rotateExtruder(bool direction, long moveDistance){
  // note to bill:  make this acecelerate so it's very fast!!!
  digitalWrite(extEnable, LOW);  // lock the motor
  digitalWrite(extDir, direction); // Enables the motor to move in a particular direction
  const int fastSpeed = speedDelay/2; // double time
  if(loaderMode==2){
   // keep waiting until button is pressed
   while (digitalRead(trigger) != 0){
      delay(40);
    }
    // Move while button is pressed
    while (digitalRead(trigger) == 0){
      // this is how we pulse the motor to get it to step
      digitalWrite(extStep, HIGH);
      delayMicroseconds(fastSpeed);
      digitalWrite(extStep, LOW);
      delayMicroseconds(fastSpeed);
    }
  }
  // ok, done pressing button, so make sure we're not energized (high is no, low is yes)
  digitalWrite(extEnable, HIGH);
}
// similar to extruder, but only stepping 50 (of 200) at a time
void rotateSelector(bool direction, int moveDistance){
  // while we are at it... can we make this faster using the magic you invented above?  
  digitalWrite(selEnable, LOW); // lock the selector
  digitalWrite(selDir, direction); // Enables the motor to move in a particular direction
    // Makes 50 pulses for making one full cycle rotation
    for (int x = 0; x < (moveDistance-1); x++){
      digitalWrite(selStep, HIGH);
      delayMicroseconds(speedDelay);
      digitalWrite(selStep, LOW);
      delayMicroseconds(speedDelay);
    }
}

void cutFilament(){  // this cycles the servo between two positions
  digitalWrite(selEnable, LOW); // disable stepper so we have power!
  if(reverseServo==false){
    openGillotine();
    closeGillotine();
  }else{
    closeGillotine();
    openGillotine();
  }
  digitalWrite(selEnable, HIGH);
}

void connectGillotine(){ // enable the servo
  filamentCutter.attach(11);                    // this is the same pin as the OLED display... Need to connect the I2C servo shield on the I2C to get it to work
}

void disconnectGillotine(){// disable the servo - so it doesn't chatter when not in use
  filamentCutter.detach();
}

void openGillotine(){ // cycle servo from 135 and 180
    for (int pos = 115; pos <= 170; pos += 1) { // goes from 0 degrees to 180 degrees
    // in steps of 1 degree
    filamentCutter.write(pos);                  // tell servo to go to position in variable 'pos'
    delayMicroseconds(25000);                   // waits 15ms for the servo to reach the position
  }
  //filamentCutter.write(3.5);                  // tell servo to go to position in variable 'pos'
  delay(50);                                    // waits 15ms for the servo to reach the position
}

void closeGillotine(){ // reverse cycle servo from 180 back to 135
  for (int pos = 170; pos >= 115; pos -= 1){   // goes from 180 degrees to 0 degrees
    filamentCutter.write(pos);                  // tell servo to go to position in variable 'pos'
    delayMicroseconds(25000);                   // waits 15ms for the servo to reach the position
  }
  delay(50);                                    // waits 15ms for the servo to reach the position
}
// rotate the selector clockwise too far from 4, so it'll grind on the bump stop
void homeSelector(){
  // rotate counter clockwise to hard stop
  rotateSelector(clockwise, stepsPerRev * microSteps);
  // move just slightly to extruder 1 (this backs off a little from the hard stop)
  rotateSelector(counterclockwise, defaultBackoff * microSteps);
  currentExtruder = 0;
  lastExtruder = -2;
}
void jogHome(){
  // rotate counter clockwise to hard stop
  rotateSelector(clockwise, stepsPerRev * microSteps);
  // move just slightly to extruder 1 (this backs off a little from the hard stop)
  rotateSelector(counterclockwise, defaultBackoff * microSteps);
}  
// buzz buzz buzz
void vibrateMotor(){
  // oscillate selector 1 time
  rotateSelector(clockwise, 2 * 16);
  rotateSelector(!clockwise, 2 * 16);
}