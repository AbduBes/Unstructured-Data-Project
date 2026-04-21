import os
from loader import load_audio, print_audio_info
from processor import trim_audio, concatenate_audio, adjust_volume_and_fade, convert_audio

def run_audio_tests():
    # Define paths (Ensure these files exist in your data/raw/audio folder)
    raw_dir = "data/raw/audio"
    processed_dir = "data/processed/audio"
    os.makedirs(processed_dir, exist_ok=True)


    wav_path = os.path.join(raw_dir, "harry_potter_audio_wav.wav")
    mp3_path = os.path.join(raw_dir, "harry_potter_audio_mp3.mp3")

    if not os.path.exists(wav_path) or not os.path.exists(mp3_path):
        print("Please place samples in data/raw/audio to run this test.")
        return

    # 1. Load and Inspect 
    print("--- Inspecting Audio ---")
    wav_audio = load_audio(wav_path)
    mp3_audio = load_audio(mp3_path)
    print_audio_info(wav_path, wav_audio)
    print_audio_info(mp3_path, mp3_audio)

    # 2. Trim Audio 
    print("--- Trimming Audio ---")
    trimmed = trim_audio(wav_audio, 0, 10000) # First 10 seconds
    convert_audio(trimmed, os.path.join(processed_dir, "trimmed.mp3"), "mp3")

    # 3. Concatenate 
    print("--- Concatenating Audio ---")
    combined = concatenate_audio(trimmed, mp3_audio[:5000])
    convert_audio(combined, os.path.join(processed_dir, "combined.mp3"), "mp3")

    # 4. Fade and Volume
    print("--- Applying Effects ---")
    effect_audio = adjust_volume_and_fade(combined, db_change=5, fade_in_ms=2000, fade_out_ms=2000)
    convert_audio(effect_audio, os.path.join(processed_dir, "effects.mp3"), "mp3")
    print("Audio processing complete! Check data/processed/audio/")

if __name__ == "__main__":
    run_audio_tests()