import pyaudio
import wave
import tempfile
import time
import logging

class Recorder:
    def __init__(self):
        self.audio = None
        self.stream = None
        self.frames = []
        self.temp_file = None
        self.is_recording = False
        self.min_duration = 1.0  # Minimum recording duration in seconds
        self.max_duration = 60.0  # Maximum recording duration in seconds

    def start_recording(self):
        logging.debug("Starting audio recording")
        try:
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024, stream_callback=self.callback)
            self.frames = []
            self.is_recording = True
            self.start_time = time.time()
            self.stream.start_stream()

            while self.is_recording and (time.time() - self.start_time) < self.max_duration:
                time.sleep(0.1)

            return self.stop_recording()
        except Exception as e:
            logging.error(f"Error in start_recording: {str(e)}")
            self.is_recording = False
            if self.stream:
                self.stream.close()
            if self.audio:
                self.audio.terminate()
            return None

    def callback(self, in_data, frame_count, time_info, status):
        self.frames.append(in_data)
        return (in_data, pyaudio.paContinue)

    def stop_recording(self):
        logging.debug("Stopping audio recording")
        self.is_recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()

        if not self.frames:
            logging.warning("No audio data recorded")
            return None

        try:
            self.temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            wf = wave.open(self.temp_file.name, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(2)  # Hardcoded to 2 bytes (16 bits) per sample
            wf.setframerate(44100)
            wf.writeframes(b''.join(self.frames))
            wf.close()
            return self.temp_file.name
        except Exception as e:
            logging.error(f"Error saving audio file: {str(e)}")
            return None

    def __del__(self):
        self.stop_recording()
        if self.temp_file:
            try:
                self.temp_file.close()
            except:
                pass