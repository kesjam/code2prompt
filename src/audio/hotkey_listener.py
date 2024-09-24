from pynput import keyboard
from PyQt5.QtCore import pyqtSignal, QObject
import logging

class HotkeyListener(QObject):
    start_recording_signal = pyqtSignal()
    stop_recording_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )
        self.listener.start()
        self.ctrl_pressed = False
        self.shift_pressed = False
        self.r_pressed = False

    def on_press(self, key):
        if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            self.ctrl_pressed = True
        if key == keyboard.Key.shift:
            self.shift_pressed = True
        if key == keyboard.KeyCode.from_char('r'):
            self.r_pressed = True
        if self.ctrl_pressed and self.shift_pressed and self.r_pressed:
            self.start_recording_signal.emit()

    def on_release(self, key):
        if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            self.ctrl_pressed = False
        if key == keyboard.Key.shift:
            self.shift_pressed = False
        if key == keyboard.KeyCode.from_char('r'):
            self.r_pressed = False
        if not (self.ctrl_pressed and self.shift_pressed and self.r_pressed):
            self.stop_recording_signal.emit()

def on_activate():
    logging.debug("Hotkey activated.")
    # Start/stop recording logic here

def for_canonical(f):
    return lambda k: f(l.canonical(k))

hotkey = keyboard.HotKey(
    keyboard.HotKey.parse('<cmd>+<shift>+1'), on_activate)

with keyboard.Listener(
        on_press=for_canonical(hotkey.press),
        on_release=for_canonical(hotkey.release)) as l:
    l.join()
