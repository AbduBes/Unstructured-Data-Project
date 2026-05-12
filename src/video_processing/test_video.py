import os
import sys
import json

import pytest

# Add src to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from video_processing.loader import inspect_and_extract_audio
from video_processing.frame_extractor import extract_keyframes
from video_processing.transcriber import load_whisper_model, transcribe_audio

def test_video_pipeline():
    # 1. Define paths according to lab structure
    raw_video_dir = os.path.join("data", "raw", "video")
    processed_audio_dir = os.path.join("data", "processed", "audio")
    processed_frames_dir = os.path.join("data", "processed", "frames")
    processed_transcripts_dir = os.path.join("data", "processed", "transcripts")
    
    # Create necessary output directories 
    os.makedirs(processed_audio_dir, exist_ok=True)
    os.makedirs(processed_frames_dir, exist_ok=True)
    os.makedirs(processed_transcripts_dir, exist_ok=True)

    # Use existing video file
    video_filename = "harry_potter_video.mp4"
    video_path = os.path.join(raw_video_dir, video_filename)
    extracted_audio_path = os.path.join(processed_audio_dir, f"extracted_{os.path.splitext(video_filename)[0]}.mp3")

    if not os.path.exists(video_path):
        print(f"Please place a video file named '{video_filename}' in {raw_video_dir} to run this test.")
        return

    # 2. Load Video, Inspect Properties, and Extract Audio
    print("\n--- Step 1: Inspecting Video & Extracting Audio ---")
    inspect_and_extract_audio(video_path, extracted_audio_path)
    assert os.path.exists(extracted_audio_path), "Audio extraction failed"

    # 3. Extract Keyframes (e.g., every 10 seconds)
    print("\n--- Step 2: Extracting Keyframes ---")
    success = extract_keyframes(video_path, processed_frames_dir, interval_seconds=10)
    assert success, "Keyframe extraction failed"
    assert len(os.listdir(processed_frames_dir)) > 0, "No keyframes extracted"

    # 4. Transcribe Extracted Audio
    print("\n--- Step 3: Transcribing Extracted Audio ---")
    if os.path.exists(extracted_audio_path):
        print("Loading Whisper model (this might take a few seconds)...")
        model = load_whisper_model(model_size="tiny") # Using 'tiny' for faster testing
        assert model is not None, "Whisper model failed to load"
        
        print("Transcribing...")
        transcript_results = transcribe_audio(model, extracted_audio_path)
        assert transcript_results is not None, "Transcription failed"
        
        if transcript_results:
            # Save transcript to JSON
            transcript_file = os.path.join(processed_transcripts_dir, f"{os.path.splitext(video_filename)[0]}_transcript.json")
            with open(transcript_file, "w", encoding="utf-8") as f:
                json.dump(transcript_results, f, indent=4, ensure_ascii=False)
            print(f"Transcript saved successfully to {transcript_file}")
            assert os.path.exists(transcript_file), "Transcript file not saved"
    else:
        pytest.fail("Skipping transcription: Extracted audio file not found.")

    print("\nVideo processing complete! Check your pipeline.log and data/processed/ folders.")

if __name__ == "__main__":
    test_video_pipeline()