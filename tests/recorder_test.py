import sys
import pyaudio
import wave
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtCore import QThread, pyqtSignal

class RecorderThread(QThread):
    finished = pyqtSignal()

    def __init__(self, filename="test_recording.wav"):
        super().__init__()
        self.filename = filename
        self.is_recording = False

    def run(self):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100

        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        frames = []

        self.is_recording = True
        while self.is_recording:
            data = stream.read(CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(self.filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        self.finished.emit()

    def stop(self):
        self.is_recording = False

class RecorderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.recorder_thread = None

    def initUI(self):
        layout = QVBoxLayout()
        
        self.status_label = QLabel('Ready to record', self)
        layout.addWidget(self.status_label)

        self.record_button = QPushButton('Start Recording', self)
        self.record_button.clicked.connect(self.toggle_recording)
        layout.addWidget(self.record_button)

        self.setLayout(layout)
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Recorder Test')
        self.show()

    def toggle_recording(self):
        if self.recorder_thread is None or not self.recorder_thread.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.recorder_thread = RecorderThread()
        self.recorder_thread.finished.connect(self.on_recording_finished)
        self.recorder_thread.start()
        self.status_label.setText('Recording...')
        self.record_button.setText('Stop Recording')

    def stop_recording(self):
        if self.recorder_thread:
            self.recorder_thread.stop()
            self.status_label.setText('Processing...')
            self.record_button.setEnabled(False)

    def on_recording_finished(self):
        self.status_label.setText('Recording saved as test_recording.wav')
        self.record_button.setText('Start Recording')
        self.record_button.setEnabled(True)
        self.recorder_thread = None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = RecorderApp()
    sys.exit(app.exec_())
