import requests
import json

def Indicate(self,setting):
    ledurl = "http://localhost:5000/set_color
    
    # first decipher the setting / alarm : color
    # connecting - orange
    # connected - white
    # moving -  blue
    # Zzero - yellow
    # connect-error - red
    # xhomed - green
    # yhomed - green
    # zhomed - green
    # probing - yellow
    # probed - purple
    # communication error - cyan 
    colors {
      "connecting":{"red":0, "green":0, "blue":1},
      "connected":{"red":1, "green":1, "blue":1},
      "moving":{"red":0, "green":0, "blue":1},
      "Zzero":{"red":0, "green":0, "blue":1},
      "connect-error":{"red":1, "green":0, "blue":0},
      "xhomed":{"red":0, "green":1, "blue":0},
      "yhomed":{"red":0, "green":1, "blue":0},
      "zhomed":{"red":0, "green":1, "blue":0},
      "probing":{"red":0, "green":0, "blue":1},
      "probed":{"red":1, "green":0, "blue":1},
      "communication error":{"red":0, "green":1, "blue":1}
    }
    try: 
      print("command: ")
      value = json.dump(colors("connecting"))
      print(value)
      r=requests.post(URL,command=cmd) 
      print(r.status_code)
      if (r.status_code == 200):
         print(f'data sent {cmd}')
      else: 
         print(f'message not sent. code: {r.status_code}, details: {r.text}') 
    except requests.exceptions.HTTPError as errh: 
      print ("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
      print ("Error Connecting:",errc) 
    except requests.exceptions.Timeout as errt:
      print ("Timeout Error:",errt)
    except requests.exceptions.RequestException as err: 