import pyautogui
import time
import os
import subprocess
from dotenv import load_dotenv
from enum import Enum
from threading import Timer

class RMError(Enum):
   NUMBER = "attempt to call a number"
   TABLE = "attempt to call a table"
   NIL = "attempt to call a nil"
   FUNCTION = "attempt to index a function value"
   DESTROYED = "got destroyed"
   TANDEM = "find cloned RPG7_TANDEM instance"
   SMOKE = "find cloned smokegrenade instance"
   ARTILLERY = "find custom instances for ArtilleryStrike"
   LADDER = "find cloned DLC Knife instance"
   MATERIAL = "to MaterialIndexMap, but it has already been added"
   CLIENT_CRASH = "left the server"


TIME_FOR_SERVER_LOG_TO_POP_UP = 3
TIME_FOR_LOADING_INTO_NEXT_MAP = 30
TIME_FOR_DRM_MODULE_ERROR = 3
NUMBER_OF_TESTS = 1
NUMBER_OF_TESTS_ZERO_INDEXED = NUMBER_OF_TESTS - 1


def logs_directory_exists():
   return os.path.isdir(os.path.join(os.curdir, "logs"))

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

def safe_shutdown(fileObject, serverProcess, clientProcess, currentTestIndexString):
   if currentTestIndexString == str(NUMBER_OF_TESTS_ZERO_INDEXED):
      print(currentTestIndexString + ": Client success. Final test complete.\n")
   else:
      print(currentTestIndexString + ": Client success. Moving to next test iteration...\n")

   fileObject.write(currentTestIndexString + ": Client Success\n")
   fileObject.close()
   serverProcess.kill()
   clientProcess.kill()
   return
   
def server_failed_to_start(fileObject, serverProcess, clientProcess, currentTestIndexString):
      if currentTestIndexString == str(NUMBER_OF_TESTS_ZERO_INDEXED):
         print(currentTestIndexString + ": DOES NOT COUNT. Server failed to start. Final test complete.\n")
      else:
         print(currentTestIndexString + ": DOES NOT COUNT. Server failed to start. Moving to next test iteration...\n")

      fileObject.write(currentTestIndexString + ": DOES NOT COUNT. Server failed to start.\n")
      fileObject.close()
      serverProcess.kill()
      clientProcess.kill()
      return

def start_and_join_server(vuClientLaunch, vuServerLaunch, logFilePath, currentTestIndexString):
  print("-----------------------")
  print("Starting test " + str(currentTestIndexString) + ":\n")

  fileObject = open(logFilePath, "a")

  successTimer = False
  serverReady = False
  secondRoundReady = False
  firstLoad = True 

  print("Starting VU Server...")
  serverProcess = subprocess.Popen(vuServerLaunch, bufsize=1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NEW_CONSOLE, encoding="UTF-8", text=True)

  # If you don't wait, the server log window will be above the client window
  time.sleep(TIME_FOR_SERVER_LOG_TO_POP_UP)

  print("Starting VU Client...")
  clientProcess = subprocess.Popen(vuClientLaunch)

  # trying to catch the DRM Module fail
  serverTimer = Timer(TIME_FOR_DRM_MODULE_ERROR, server_failed_to_start, args=(fileObject, serverProcess, clientProcess, currentTestIndexString))
  serverTimer.start()

  # this loop only executes when something goes to StdOut
  while True:
      output = serverProcess.stdout.readline()
      if output == '' and serverProcess.poll() is not None:
          break

      # if server is printing to stdOut, it's working fine
      if serverTimer:
         serverTimer.cancel()
         serverTimer = False

      if secondRoundReady:
         if not successTimer:
            successTimer = Timer(TIME_FOR_LOADING_INTO_NEXT_MAP, safe_shutdown, args=(fileObject, serverProcess, clientProcess, currentTestIndexString))
            successTimer.start()
      
      if output:
          msg = output.strip()
          if "Game successfully registered with Zeus. The server is now accepting connections." in msg:
              serverReady = True

          if serverReady:
             if "Successfully authenticated server with Hera" in msg:
               print("Second Round is ready.")
               secondRoundReady = True
          
          if secondRoundReady:
             if RMError.CLIENT_CRASH.value in msg:
               if currentTestIndexString == str(NUMBER_OF_TESTS_ZERO_INDEXED):
                  print(currentTestIndexString + ": Client Crash. Final test complete.\n")
               else:
                  print(currentTestIndexString + ": Client Crash. Moving to next test iteration...\n")

               fileObject.write(currentTestIndexString + ": Client Crash\n")
               fileObject.close()
               if successTimer:
                  successTimer.cancel()
               serverProcess.kill()
               return
          
          for item in RMError:
             if item.value in msg:
                fileObject.write(currentTestIndexString + ": " + msg + "\n")
          
          if firstLoad and serverReady:
            print("Loading is complete. Joining the game")
            try:
               res = pyautogui.locateOnScreen("soldier.png")
               coordinates = pyautogui.center(res)
               pyautogui.click(coordinates.x, coordinates.y, 1)
               firstLoad = False
            except: 
               print("[Error]: pyautogui could not find soldier image! Resolution wrong, or client failed to start for some reason.")
               if currentTestIndexString == str(NUMBER_OF_TESTS_ZERO_INDEXED):
                  print(currentTestIndexString + ": DOES NOT COUNT. Client never connected to server. Final test complete.\n")
               else:
                  print(currentTestIndexString + ": DOES NOT COUNT. Client never connected to server. Moving to next test iteration...\n")

               fileObject.write(currentTestIndexString + ": DOES NOT COUNT. Client never connected to server.\n")
               fileObject.close()
               clientProcess.kill()
               serverProcess.kill()
               return

def say_hello():
   print("hello")

def main():
  load_dotenv()

  if not can_run_program():
    return

  vuPath = os.getenv("VU_Exe_Location")

  vuClientParameters = os.getenv("Client_Parameters")
  vuServerParameters = " -dedicated -highResTerrain -skipChecksum -updateBranch prod"

  if not logs_directory_exists():
     os.mkdir(os.path.join(os.curdir, "logs"))

  logFilePath = os.path.join(os.curdir, "logs", time.strftime("%Y%m%d-%H%M%S") + ".txt")
  
  vuClientLaunch = vuPath + vuClientParameters
  vuServerLaunch = vuPath + vuServerParameters

  for currentTestIndex in range (NUMBER_OF_TESTS):
    start_and_join_server(vuClientLaunch, vuServerLaunch, logFilePath, str(currentTestIndex))

  return

main()