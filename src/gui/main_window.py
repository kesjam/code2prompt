from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QListWidget, QListWidgetItem, QTextEdit, QMessageBox, QLabel, QProgressDialog, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QIcon
import logging
import os
from openai import OpenAI, BadRequestError
from pynput import keyboard
from src.audio.recorder import Recorder
from src.api.whisper_api import transcribe_audio
from src.api.gpt4_api import clean_up_transcription
from src.data.data_manager import save_dictation, get_all_dictations, delete_dictation, get_dictation_by_id
from src.utils.text_inserter import insert_text_to_active_window
import threading
import pyautogui
import time
import re
import sys

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class TranscriptionThread(QThread):
    finished = pyqtSignal(str, str, str)
    progress = pyqtSignal(int)

    def __init__(self, audio_file_path):
        super().__init__()
        self.audio_file_path = audio_file_path

    def run(self):
        try:
            self.progress.emit(25)
            logging.debug("Starting audio transcription")
            transcription = transcribe_audio(self.audio_file_path)
            logging.debug(f"Raw transcription: {transcription[:100]}...")  # Log first 100 chars
            self.progress.emit(50)
            logging.debug("Starting transcription cleanup")
            cleaned_transcription, suggested_title = clean_up_transcription(transcription, "General")
            logging.debug(f"Cleaned transcription: {cleaned_transcription[:100]}...")  # Log first 100 chars
            self.progress.emit(100)
            logging.debug(f"Transcription process completed. Suggested title: {suggested_title}")
            self.finished.emit(cleaned_transcription, suggested_title, self.audio_file_path)
        except Exception as e:
            logging.error(f"Error in transcription thread: {str(e)}")
            self.finished.emit("", "Error in transcription", self.audio_file_path)

class HotkeyListener(QThread):
    hotkey_pressed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.listener = None
        self.ctrl_pressed = False
        self.shift_pressed = False

    def run(self):
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as self.listener:
            self.listener.join()

    def on_press(self, key):
        if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            self.ctrl_pressed = True
        elif key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
            self.shift_pressed = True
        elif key == keyboard.KeyCode.from_char('d') and self.ctrl_pressed and self.shift_pressed:
            self.hotkey_pressed.emit()

    def on_release(self, key):
        if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            self.ctrl_pressed = False
        elif key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
            self.shift_pressed = False

    def stop(self):
        if self.listener:
            self.listener.stop()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        logging.info("Initializing MainWindow")
        try:
            self.setWindowTitle("DictationApp")
            self.setGeometry(100, 100, 800, 600)
            logging.info("Window properties set")
            
            # Create main widget and layout
            main_widget = QWidget()
            self.setCentralWidget(main_widget)
            main_layout = QVBoxLayout(main_widget)

            # Create countdown label
            self.countdown_label = QLabel("Countdown", self)
            self.countdown_label.setStyleSheet("""
                background-color: rgba(255, 255, 255, 200);
                padding: 10px;
                border-radius: 5px;
                font-size: 24px;
                color: red;
            """)
            self.countdown_label.setAlignment(Qt.AlignCenter)
            self.countdown_label.hide()  # Initially hidden

            # Add countdown label to the layout
            main_layout.addWidget(self.countdown_label)

            # Add hotkey instructions
            hotkey_label = QLabel("Hotkey: Press Ctrl+Shift+D to start/stop dictation in any application")
            hotkey_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(hotkey_label)

            # Content layout (list and transcription)
            content_layout = QHBoxLayout()

            # Left side (list and buttons)
            left_layout = QVBoxLayout()
            self.dictations_list = QListWidget()
            self.dictations_list.itemClicked.connect(self.on_dictation_selected)
            left_layout.addWidget(self.dictations_list)

            # Button layout
            button_layout = QHBoxLayout()
            self.record_button = QPushButton("Start Recording", self)
            self.record_button.clicked.connect(self.toggle_recording)
            button_layout.addWidget(self.record_button)

            self.delete_button = QPushButton("Delete")
            self.delete_button.clicked.connect(self.delete_selected_dictation)
            button_layout.addWidget(self.delete_button)

            left_layout.addLayout(button_layout)

            # Right side (transcription window)
            self.transcription_window = QTextEdit()
            self.transcription_window.setReadOnly(True)

            # Add layouts to content layout
            content_layout.addLayout(left_layout, 1)
            content_layout.addWidget(self.transcription_window, 2)

            # Add content layout to main layout
            main_layout.addLayout(content_layout)

            self.load_dictations()

            # Set up hotkey listener
            self.hotkey_listener = HotkeyListener()
            self.hotkey_listener.hotkey_pressed.connect(self.toggle_recording)
            self.hotkey_listener.start()

            logging.debug("Hotkey listener started")

            self.is_recording = False
            self.recorder = Recorder()  # Make sure this is initialized

            # Initialize the countdown timer
            self.countdown_timer = QTimer(self)
            self.countdown_timer.timeout.connect(self.update_countdown)

            # Ensure the button is green on startup
            self.update_button_state("Start Recording", "green")

            self.setup_tray()
            logging.info("Tray setup complete")
        except Exception as e:
            logging.error(f"Error in MainWindow initialization: {str(e)}", exc_info=True)

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        icon_path = resource_path("MyIcon.icns")  # Use the .icns file directly
        print(f"Resolved icon path: {icon_path}")  # Debug statement
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            self.tray_icon.setIcon(icon)
            print(f"Icon set from path: {icon_path}")
        else:
            print(f"Icon file not found at: {icon_path}")
        self.tray_icon.show()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "DictationApp",
            "Application was minimized to tray",
            QSystemTrayIcon.Information,
            2000
        )

    def quit_application(self):
        self.tray_icon.hide()
        QApplication.quit()

    def on_dictation_selected(self, item):
        dictation_id = item.data(Qt.UserRole)
        dictation = get_dictation_by_id(dictation_id)
        if dictation:
            self.transcription_window.setText(dictation.content)
        else:
            self.transcription_window.setText("Error: Could not load dictation content.")

    def toggle_recording(self):
        logging.debug("Toggle recording called")
        if self.is_recording:
            self.stop_dictation()
        else:
            self.start_dictation()

    def start_dictation(self):
        logging.debug("Starting dictation")
        try:
            self.is_recording = True
            self.update_button_state("Recording...", "red")
            self.recording_thread = threading.Thread(target=self.recorder.start_recording)
            self.recording_thread.start()
            logging.debug("Dictation started")
        except Exception as e:
            logging.error(f"Error in start_dictation: {str(e)}")
            self.is_recording = False
            QMessageBox.critical(self, "Error", f"Failed to start recording: {str(e)}")

    def stop_dictation(self):
        logging.debug("Stopping dictation")
        try:
            self.is_recording = False
            self.update_button_state("Processing...", "yellow")
            self.recorder.is_recording = False
            if self.recording_thread:
                self.recording_thread.join(timeout=5)
            
            audio_file_path = self.recorder.stop_recording()
            if audio_file_path:
                logging.debug(f"Recording stopped, file path: {audio_file_path}")
                
                # Start transcription in background
                self.transcription_thread = TranscriptionThread(audio_file_path)
                self.transcription_thread.finished.connect(self.on_transcription_finished)
                self.transcription_thread.start()
            else:
                logging.warning("No audio file was created")
                QMessageBox.warning(self, "Warning", "No audio was recorded.")
        except Exception as e:
            logging.error(f"Error in stop_dictation: {str(e)}")
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def cancel_transcription(self):
        if hasattr(self, 'transcription_thread') and self.transcription_thread.isRunning():
            self.transcription_thread.terminate()
            self.transcription_thread.wait()
        self.update_button_state("Start Recording", "green")

    def update_button_state(self, text, color):
        logging.debug(f"Updating button state: text='{text}', color='{color}'")
        self.record_button.setText(text)
        if color == "green":
            self.record_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    border: none;
                    color: white;
                    padding: 15px 32px;
                    text-align: center;
                    text-decoration: none;
                    font-size: 16px;
                    margin: 4px 2px;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
        elif color == "red":
            self.record_button.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    border: none;
                    color: white;
                    padding: 15px 32px;
                    text-align: center;
                    text-decoration: none;
                    font-size: 16px;
                    margin: 4px 2px;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background-color: #d32f2f;
                }
            """)
        elif color == "yellow":
            self.record_button.setStyleSheet("""
                QPushButton {
                    background-color: #FFC107;
                    border: none;
                    color: black;
                    padding: 15px 32px;
                    text-align: center;
                    text-decoration: none;
                    font-size: 16px;
                    margin: 4px 2px;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background-color: #FFA000;
                }
            """)

    def show_insertion_countdown(self):
        self.countdown = 3
        self.countdown_label.setText(f"Inserting in: {self.countdown}")
        self.countdown_label.show()
        self.countdown_timer.start(1000)  # Update every second

    def update_countdown(self):
        self.countdown -= 1
        if self.countdown > 0:
            self.countdown_label.setText(f"Inserting in: {self.countdown}")
        elif self.countdown == 0:
            self.countdown_label.setText("Working My Magic")
            self.countdown_timer.stop()
            QTimer.singleShot(1000, self.perform_text_insertion)  # 1 second delay before insertion
        else:
            self.countdown_label.hide()

    def perform_text_insertion(self):
        self.insert_text_to_active_window(self.last_transcription)
        self.countdown_label.hide()

    def insert_text_to_active_window(self, text):
        logging.debug(f"Inserting text: {text[:30]}...")
        time.sleep(0.5)  # Give time to switch to the target application
        text_with_space = text + " "  # Add a space at the end of the text
        pyautogui.write(text_with_space)
        logging.debug("Text insertion complete")
        self.update_button_state("Start Recording", "green")

    def load_dictations(self):
        self.dictations_list.clear()
        dictations = get_all_dictations()
        for dictation in dictations:
            item = QListWidgetItem(f"{dictation.subject} - {dictation.date_time.strftime('%Y-%m-%d %H:%M:%S')}")
            item.setData(Qt.UserRole, dictation.id)
            self.dictations_list.addItem(item)

    def delete_selected_dictation(self):
        current_item = self.dictations_list.currentItem()
        if current_item:
            dictation_id = current_item.data(Qt.UserRole)
            reply = QMessageBox.question(self, 'Delete Dictation',
                                         'Are you sure you want to delete this dictation?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                if delete_dictation(dictation_id):
                    self.load_dictations()
                    self.transcription_window.clear()
                    QMessageBox.information(self, "Success", "Dictation deleted successfully.")
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete dictation.")
        else:
            QMessageBox.warning(self, "No Selection", "Please select a dictation to delete.")

    def closeEvent(self, event):
        self.hotkey_listener.stop()
        if hasattr(self, 'transcription_thread') and self.transcription_thread.isRunning():
            self.transcription_thread.terminate()
            self.transcription_thread.wait()
        super().closeEvent(event)

    def update_progress(self, value):
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.setValue(value)

    def on_transcription_finished(self, cleaned_transcription, suggested_title, audio_file_path):
        save_dictation(suggested_title, cleaned_transcription, audio_file_path, "General")
        self.load_dictations()
        self.transcription_window.setText(cleaned_transcription)
        logging.debug("Transcription saved and displayed")
        self.last_transcription = cleaned_transcription  # Remove the space at the end
        self.show_insertion_countdown()
