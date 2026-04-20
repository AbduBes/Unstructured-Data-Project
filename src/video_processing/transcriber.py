import os
import logging
from faster_whisper import WhisperModel
from pydub import AudioSegment

logging.basicConfig(filename="pipeline.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def load_whisper_model(model_size="small"):
    """Initializes the faster-whisper model."""
    try:
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        logging.info(f"Successfully loaded WhisperModel (size: {model_size})")
        return model
    except Exception as e:
        logging.error(f"Error loading WhisperModel: {e}")
        return None

def transcribe_audio(model, audio_path):
    """Transcribes short audio files."""
    try:
        segments, info = model.transcribe(audio_path, beam_size=5)
        logging.info(f"Started transcribing {audio_path} (Detected language: {info.language})")
        
        results = []
        for segment in segments:
            results.append({"start": segment.start, "end": segment.end, "text": segment.text})
            
        logging.info(f"Successfully transcribed short audio: {audio_path}")
        return results
    except Exception as e:
        logging.error(f"Error transcribing {audio_path}: {e}")
        return None

def chunked_transcribe(model, audio_path, chunk_length_ms=300000):
    """Transcribes long audio files by splitting them into chunks."""
    try:
        audio = AudioSegment.from_file(audio_path)
        chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]
        logging.info(f"Split long audio {audio_path} into {len(chunks)} chunks")
        
        all_transcripts = []
        time_offset = 0.0

        for idx, chunk in enumerate(chunks):
            temp_chunk_path = f"temp_chunk_{idx}.wav"
            try:
                chunk.export(temp_chunk_path, format="wav")
                segments, _ = model.transcribe(temp_chunk_path, beam_size=5)
                
                for s in segments:
                    all_transcripts.append({
                        "start": s.start + time_offset,
                        "end": s.end + time_offset,
                        "text": s.text
                    })
                
                time_offset += (len(chunk) / 1000.0)
                logging.info(f"Successfully transcribed chunk {idx + 1}/{len(chunks)} for {audio_path}")
            except Exception as chunk_e:
                logging.error(f"Error processing chunk {idx} of {audio_path}: {chunk_e}")
            finally:
                if os.path.exists(temp_chunk_path):
                    os.remove(temp_chunk_path) 
        
        logging.info(f"Finished chunked transcription for {audio_path}")
        return all_transcripts
        
    except Exception as e:
        logging.error(f"Fatal error in chunked transcription of {audio_path}: {e}")
        return None