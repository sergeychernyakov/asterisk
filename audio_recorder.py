import pyaudio
import numpy as np
import wave
from scipy.io.wavfile import write

class AudioRecorder:
    """
    A class to handle audio recording and automatically stop when silence is detected.
    """
    
    CHUNK: int = 1024  # Number of frames per buffer
    FORMAT: int = pyaudio.paInt16  # Sample format
    CHANNELS: int = 1  # Number of channels
    RATE: int = 44100  # Sample rate
    SILENCE_THRESHOLD: int = 500  # Silence threshold
    SILENCE_DURATION: int = 2  # Seconds of silence to stop recording

    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=self.FORMAT,
                                      channels=self.CHANNELS,
                                      rate=self.RATE,
                                      input=True,
                                      frames_per_buffer=self.CHUNK)
        self.frames = []

    @staticmethod
    def is_silent(data: np.ndarray) -> bool:
        """
        Check if the audio data is below the silence threshold.

        Args:
            data (np.ndarray): The audio data.

        Returns:
            bool: True if silent, False otherwise.
        """
        return np.abs(data).mean() < AudioRecorder.SILENCE_THRESHOLD

    def record(self, filename: str) -> None:
        """
        Record audio from the microphone and save it to a file.

        Args:
            filename (str): The name of the file to save the recording.
        """
        print("Recording...")

        silence_counter = 0

        while True:
            data = self.stream.read(self.CHUNK)
            numpy_data = np.frombuffer(data, dtype=np.int16)
            self.frames.append(data)

            if self.is_silent(numpy_data):
                silence_counter += 1
            else:
                silence_counter = 0

            if silence_counter > self.SILENCE_DURATION * (self.RATE / self.CHUNK):
                print("Silence detected, stopping recording...")
                break

        self.stop_recording()
        self.save_recording(filename)

    def stop_recording(self) -> None:
        """
        Stop the audio stream and terminate the audio interface.
        """
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

    def save_recording(self, filename: str) -> None:
        """
        Save the recorded audio to a file.

        Args:
            filename (str): The name of the file to save the recording.
        """
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()

if __name__ == "__main__":
    recorder = AudioRecorder()
    recorder.record("output.wav")
