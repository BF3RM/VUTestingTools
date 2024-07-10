import pyautogui
import time
import os
import subprocess
from dotenv import load_dotenv

def soldier_image_exists():
  return os.path.isfile("soldier.png")    

def environment_variables_exist():
  vuLocation = os.getenv("VU_Exe_Location")
  clientParameters = os.getenv("Client_Parameters")
  if vuLocation and clientParameters:
     return True
  return False

def can_run_program():
  if not environment_variables_exist():
     print("[Error]: Invalid or missing environment variables!")
     time.sleep(3)
     return False
  
  if not soldier_image_exists():
      print("[Error]: No soldier image found!")
      time.sleep(3)
      return False
  
  return True
   

def start_and_join_server():
  load_dotenv()

  if not can_run_program():
     return

  vuPath = os.getenv("VU_Exe_Location")

  vuClientParameters = os.getenv("Client_Parameters")
  vuServerParameters = " -dedicated -highResTerrain -skipChecksum -updateBranch prod"

  vuClientLaunch = vuPath + vuClientParameters
  vuServerLaunch = vuPath + vuServerParameters

  firstLoad = True

  TIME_FOR_SERVER_LOG_TO_POP_UP = 3

  print("Starting VU Server...")
  serverProcess = subprocess.Popen(vuServerLaunch, bufsize=1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NEW_CONSOLE, encoding="UTF-8", text=True)

  # If you don't wait, the server log window will be above the client window
  time.sleep(TIME_FOR_SERVER_LOG_TO_POP_UP)

  print("Starting VU Client...")
  clientProcess = subprocess.Popen(vuClientLaunch)

  # # Read the stdout line by line as it updates
  while True:
      output = serverProcess.stdout.readline()
      if output == '' and serverProcess.poll() is not None:
          break
      if output:
          isDoneLoading = "Game successfully registered with Zeus. The server is now accepting connections." in output.strip()
          if isDoneLoading:
              print("Loading is complete. Joining the game")
              if firstLoad:
                try:
                  res = pyautogui.locateOnScreen("soldier.png")
                  coordinates = pyautogui.center(res)
                  pyautogui.click(coordinates.x, coordinates.y, 1)
                  firstLoad = False
                except: 
                    print("[Error]: pyautogui could not find soldier image! Take a screenshot at the resolution you are going to test with.")
                    clientProcess.kill()
                    serverProcess.kill()
                    return

start_and_join_server()