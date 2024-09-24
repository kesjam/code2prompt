import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
import pyaudio
import wave
import threading

class RecorderThread(threading.Thread):
    def __init__(self, filename="minimal_output.wav"):
        super().__init__()
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.recording = False
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.filename = filename

    def run(self):
        print("Initializing recording...")
        try:
            self.stream = self.p.open(format=self.format,
                                      channels=self.channels,
                                      rate=self.rate,
                                      input=True,
                                      frames_per_buffer=self.chunk)
        except Exception as e:
            print(f"Failed to initialize stream: {e}")
            return

        self.recording = True
        print("Recording...")
        while self.recording:
            try:
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                self.frames.append(data)
            except Exception as e:
                print(f"Error during recording: {e}")
                break
        print("Recording finished.")
        self.save()

    def stop(self):
        print("Stopping recording...")
        self.recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.p:
            self.p.terminate()

    def save(self):
        print(f"Saving recording to {self.filename}...")
        try:
            wf = wave.open(self.filename, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.p.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))
            wf.close()
            print("Recording saved.")
        except Exception as e:
            print(f"Error saving recording: {e}")

class MinimalRecorder(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minimal Recorder")
        self.setGeometry(100, 100, 300, 100)

        self.record_button = QPushButton("Record")
        self.record_button.clicked.connect(self.toggle_recording)

        layout = QVBoxLayout()
        layout.addWidget(self.record_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.recorder_thread = None

    def toggle_recording(self):
        if self.recorder_thread and self.recorder_thread.recording:
            self.record_button.setText("Record")
            self.recorder_thread.stop()
            self.recorder_thread.join()
            self.recorder_thread = None
        else:
            self.record_button.setText("Stop")
            self.recorder_thread = RecorderThread(filename="minimal_output.wav")
            self.recorder_thread.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MinimalRecorder()
    window.show()
    sys.exit(app.exec_())