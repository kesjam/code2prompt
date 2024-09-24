import pyautogui
import time
import logging

logging.basicConfig(level=logging.DEBUG)
logging.debug("Importing text_inserter.py")

def insert_text(text):
    pyautogui.write(text)

def insert_text_to_active_window(text):
    time.sleep(0.5)  # Give some time for the window to be active
    pyautogui.typewrite(text)
    pyautogui.press('space')  # Add a space after the inserted text

# Add any other necessary functions or imports here
