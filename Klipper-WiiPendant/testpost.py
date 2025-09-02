import requests 
import json 

def Indicate(setting):
  URL = "http://localhost:5000/set_color"
    
    # first decipher the setting / alarm : color connecting - orange connected - white moving - blue Zzero - yellow connect-error - red 
    # xhomed - green yhomed - green zhomed - green probing - yellow probed - purple communication error - cyan
  colors = { 
      "connecting":{"red":"0", "green":"0", "blue":"255"}, 
      "connected":{"red":"255", "green":"255", "blue":"255"}, 
      "moving":{"red":"0", "green":"0", "blue":"255"}, 
      "Zzero":{"red":"0", "green":"255", "blue":"127"}, 
      "connect-error":{"red":"255", "green":"0", "blue":"0"}, 
      "xhomed":{"red":"0", "green":"255","blue":"50"}, 
      "yhomed":{"red":"0", "green":"255", "blue":"100"}, 
      "zhomed":{"red":"0", "green":"255", "blue":"150"}, 
      "probing":{"red":"0", "green":"0", "blue":"127"}, 
      "probed":{"red":"255", "green":"0", "blue":"200"}, 
      "communication error":{"red":"0", "green":"200", "blue":"200"}
    }
  try: 
    value = colors[setting] 
    print("json value is : ", value) 
    r=requests.post(URL,json =value) 
    print(r.status_code) 
    if(r.status_code == 200):
      print(f'data sent {value}') 
    else: 
      print(f'message not sent. code: {r.status_code}, details: {r.text}') 
  except requests.exceptions.HTTPError as errh:
    print ("Http Error:",errh) 
  except requests.exceptions.ConnectionError as errc: 
    print ("Error Connecting:",errc) 
  except requests.exceptions.Timeout as errt:
    print ("Timeout Error:",errt)
  except requests.exceptions.RequestException as err: 
    print ("request error",err)

if __name__ == '__main__':
   while(1):
     setting = input("Enter test send numbers: \r\n1 for connected\r\n2 for moving\r\n3 for connect-error\r\n> ")
     if(setting == "1"):
       Indicate("connected")
     elif (setting == "2"):
       Indicate("moving")
     elif (setting == "3"):
       Indicate( "communication error")
