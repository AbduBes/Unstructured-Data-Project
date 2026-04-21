import logging
from pydub import AudioSegment

logging.basicConfig(filename="pipeline.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def trim_audio(audio, start_ms, end_ms, label="audio"):
    """Trims audio to a specific segment."""
    try:
        trimmed = audio[start_ms:end_ms]
        logging.info(f"Trimmed {label} from {start_ms}ms to {end_ms}ms")
        return trimmed
    except Exception as e:
        logging.error(f"Error trimming {label}: {e}")
        return None

def concatenate_audio(audio1, audio2, label="audio clips"):
    """Concatenates two audio clips."""
    try:
        combined = audio1 + audio2
        logging.info(f"Successfully concatenated {label}")
        return combined
    except Exception as e:
        logging.error(f"Error concatenating {label}: {e}")
        return None

def adjust_volume_and_fade(audio, db_change, fade_in_ms, fade_out_ms, label="audio"):
    """Adjusts volume (+/- dB) and applies fade-in/fade-out effects."""
    try:
        adjusted = audio + db_change
        faded = adjusted.fade_in(fade_in_ms).fade_out(fade_out_ms)
        logging.info(f"Adjusted volume by {db_change}dB and applied fades to {label}")
        return faded
    except Exception as e:
        logging.error(f"Error adjusting volume/fades for {label}: {e}")
        return None

def convert_audio(audio, output_path, format="mp3"):
    """Converts and exports audio to a specific format."""
    try:
        audio.export(output_path, format=format)
        logging.info(f"Exported audio to {output_path} in {format.upper()} format")
        return output_path
    except Exception as e:
        logging.error(f"Error exporting audio to {output_path}: {e}")
        return None