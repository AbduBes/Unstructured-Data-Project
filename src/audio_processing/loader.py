import os
import logging
from pydub import AudioSegment

logging.basicConfig(filename="pipeline.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def load_audio(file_path, format=None):
    """Loads an audio file into a pydub AudioSegment."""
    try:
        if format:
            audio = AudioSegment.from_file(file_path, format=format)
        else:
            audio = AudioSegment.from_file(file_path)
        logging.info(f"Successfully loaded audio: {file_path}")
        return audio
    except Exception as e:
        logging.error(f"Error loading audio file {file_path}: {e}")
        return None

def print_audio_info(file_path, audio_segment):
    """Prints technical properties of the loaded audio and logs the inspection."""
    try:
        duration_sec = len(audio_segment) / 1000.0
        channels = audio_segment.channels
        channel_type = "Stereo" if channels == 2 else "Mono"
        frame_rate_hz = audio_segment.frame_rate
        bit_depth = audio_segment.sample_width * 8
        file_size_kb = os.path.getsize(file_path) / 1024

        print(f"filename             : {os.path.basename(file_path)}")
        print(f"format               : {file_path.split('.')[-1].upper()}")
        print(f"duration_sec         : {duration_sec:.2f}")
        print(f"channels             : {channels}")
        print(f"channel_type         : {channel_type}")
        print(f"frame_rate_hz        : {frame_rate_hz}")
        print(f"bit_depth            : {bit_depth}")
        print(f"file_size_kb         : {file_size_kb:.1f}")
        print("-" * 30)
        
        logging.info(f"Inspected audio file properties: {file_path}")
    except Exception as e:
        logging.error(f"Error inspecting audio file {file_path}: {e}")