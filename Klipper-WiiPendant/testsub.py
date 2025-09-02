#usr/bin/python3

import subprocess
import sys

while(1):
  try:
    cmd = input("1 for launch pendant\r\n2 for exit\r\n")
    if (cmd == "1"):
      subprocess.run(['sudo','/home/pi/wp/wp.sh']) 
      #subprocess launch
    elif(cmd == "2"):
      sys.exit(0)
  except:
    print("oh no, something broke... ")
    sys.exit(1)
