import logging
from moviepy import VideoFileClip

logging.basicConfig(filename="pipeline.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def inspect_and_extract_audio(video_path, output_audio_path):
    """Loads video, prints properties, and extracts audio."""
    clip = None
    try:
        clip = VideoFileClip(video_path)
        
        print("--- Video Properties ---")
        print(f"Duration: {clip.duration} seconds")
        print(f"FPS: {clip.fps}")
        print(f"Resolution: {clip.size}")
        logging.info(f"Inspected video properties for {video_path}")
        
        # Extract audio track
        print("Extracting audio...")
        clip.audio.write_audiofile(output_audio_path, logger=None) # logger=None stops moviepy from cluttering terminal
        logging.info(f"Successfully extracted audio from video to {output_audio_path}")
        
    except Exception as e:
        logging.error(f"Error inspecting or extracting audio from {video_path}: {e}")
    finally:
        try:
            clip.close()
        except:
            pass