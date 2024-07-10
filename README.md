# VUTestingTools

An attempt to make VU/RM stability easier to quantify.

# Required Language/Packages

- Python
- `pip install pyautogui`
- `pip install python-dotenv`

# Required Environment Variables inside .env:

- VU_EXE_Location = ".../VeniceUnleashed/client/vu.exe"
- Client_Parameters = " -username yourUsername -password yourPassword vu://join/yourServerGuid/yourServerPassword"

# Required image 'soldier.png'

- A screenshot from the soldier menu of the soldier you want to be selected.
- The image resolution of the soldier must be perfect. If you plan to test at fullscreen, take the screenshot at fullscreen.
- If you do not have the perfect resolution, pyautogui will not find it.
