import os
import logging
from moviepy.editor import VideoFileClip

logging.basicConfig(filename="pipeline.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def extract_keyframes(video_path, output_dir, interval_seconds=10):
    """Extracts a frame every X seconds."""
    try:
        os.makedirs(output_dir, exist_ok=True)
        clip = VideoFileClip(video_path)
        
        count = 0
        for t in range(0, int(clip.duration), interval_seconds):
            frame_path = os.path.join(output_dir, f"frame_{t}s.jpg")
            clip.save_frame(frame_path, t=t)
            count += 1
            
        logging.info(f"Successfully extracted {count} keyframes from {video_path} to {output_dir}")
        return True
    except Exception as e:
        logging.error(f"Error extracting frames from {video_path}: {e}")
        return False
    finally:
        try:
            clip.close()
        except:
            pass