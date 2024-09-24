from PyQt5.QtCore import QThread, pyqtSignal
import pyaudio
import wave
import os

class RecorderThread(QThread):
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.audio_file_path = "output.wav"

    def run(self):
        self.is_recording = True
        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
        frames = []

        while self.is_recording:
            data = stream.read(1024)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        audio.terminate()

        wf = wave.open(self.audio_file_path, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(frames))
        wf.close()

        self.finished.emit()

    def stop(self):
        self.is_recording = False

    def get_audio_file_path(self):
        return self.audio_file_path