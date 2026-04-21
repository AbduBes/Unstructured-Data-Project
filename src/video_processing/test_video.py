import os;
import json;
from loader import inspect_and_extract_audio
from frame_extractor import extract_keyframes
from transcriber import load_whisper_model, transcribe_audio

def run_video_tests():
    # 1. Define paths according to lab structure
    raw_video_dir = "data/raw/video"
    processed_audio_dir = "data/processed/audio"
    processed_frames_dir = "data/processed/frames"
    processed_transcripts_dir = "data/processed/transcripts"
    
    # Create necessary output directories 
    os.makedirs(processed_audio_dir, exist_ok=True)
    os.makedirs(processed_frames_dir, exist_ok=True)
    os.makedirs(processed_transcripts_dir, exist_ok=True)

    # Use a dummy path for the test (replace "sample.mp4" with your actual file name)
    video_path = os.path.join(raw_video_dir, "sample.mp4")
    extracted_audio_path = os.path.join(processed_audio_dir, "extracted_sample.mp3")

    if not os.path.exists(video_path):
        print(f"Please place a video file named 'sample.mp4' in {raw_video_dir} to run this test.")
        return

    # 2. Load Video, Inspect Properties, and Extract Audio
    print("\n--- Step 1: Inspecting Video & Extracting Audio ---")
    inspect_and_extract_audio(video_path, extracted_audio_path)

    # 3. Extract Keyframes (e.g., every 10 seconds)
    print("\n--- Step 2: Extracting Keyframes ---")
    extract_keyframes(video_path, processed_frames_dir, interval_seconds=10)

    # 4. Transcribe Extracted Audio
    print("\n--- Step 3: Transcribing Extracted Audio ---")
    if os.path.exists(extracted_audio_path):
        print("Loading Whisper model (this might take a few seconds)...")
        model = load_whisper_model(model_size="tiny") # Using 'tiny' for faster testing
        
        print("Transcribing...")
        transcript_results = transcribe_audio(model, extracted_audio_path)
        
        if transcript_results:
            # Save transcript to JSON
            transcript_file = os.path.join(processed_transcripts_dir, "sample_transcript.json")
            with open(transcript_file, "w", encoding="utf-8") as f:
                json.dump(transcript_results, f, indent=4, ensure_ascii=False)
            print(f"Transcript saved successfully to {transcript_file}")
    else:
        print("Skipping transcription: Extracted audio file not found.")

    print("\nVideo processing complete! Check your pipeline.log and data/processed/ folders.")

if __name__ == "__main__":
    run_video_tests()