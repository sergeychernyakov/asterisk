from pydub import AudioSegment
from pydub.silence import detect_silence
import os

def detect_silence_in_audio(file_path: str, silence_thresh: int = -30, min_silence_len: int = 1000) -> list:
    """
    Detect silence in an audio file.

    Args:
        file_path (str): The path to the audio file.
        silence_thresh (int): The silence threshold in dBFS. Default is -30 dBFS.
        min_silence_len (int): The minimum length of silence in milliseconds. Default is 1000 ms.

    Returns:
        list: A list of tuples indicating the start and end of detected silence periods.
    """
    try:
        # Load the audio file
        audio = AudioSegment.from_file(file_path)
        # Detect silence
        silence_ranges = detect_silence(audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh)
        return silence_ranges
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def main():
    # Path to your audio file
    audio_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preamble.wav")
    
    # Silence detection parameters
    silence_threshold = -30  # Silence threshold in dBFS
    min_silence_length = 500  # Minimum silence length in milliseconds

    # Detect silence
    silences = detect_silence_in_audio(audio_file_path, silence_thresh=silence_threshold, min_silence_len=min_silence_length)

    # Output the detected silences
    if silences:
        print("Detected silences (in milliseconds):")
        for start, end in silences:
            print(f"Start: {start} ms, End: {end} ms, Duration: {end - start} ms")
    else:
        print("No silence detected.")

if __name__ == "__main__":
    main()
