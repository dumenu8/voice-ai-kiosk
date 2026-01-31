from faster_whisper import WhisperModel
import os
import shutil
from fastapi import UploadFile

# Configuration
MODEL_SIZE = "distil-large-v3"
DEVICE = "cuda" # Default to CPU, can be "cuda" if GPU is available
COMPUTE_TYPE = "float16" # Quantization for CPU speed int8 for cpu, float16 for cuda

print(f"Loading Whisper Model: {MODEL_SIZE} on {DEVICE}...")
# Load model once at startup
try:
    model = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)
    print("Whisper Model Loaded.")
except Exception as e:
    print(f"Error loading Whisper Model: {e}")
    model = None

def transcribe(audio_file: UploadFile) -> str:
    if model is None:
        return "Error: STT Model not loaded."

    # Save to temp file because faster-whisper needs a file path or binary stream
    # It supports binary stream, so we can try that first to avoid disk I/O
    try:
        # Read file into memory
        # segments, info = model.transcribe(audio_file.file, beam_size=5)
        
        # NOTE: faster-whisper sometimes has issues with raw file-like objects from FastAPI 
        # depending on the version. Safer to save to temp file.
        temp_filename = f"temp_{audio_file.filename}"
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)
            
        segments, info = model.transcribe(temp_filename, beam_size=5)
        
        text = " ".join([segment.text for segment in segments])
        
        # Cleanup
        os.remove(temp_filename)
        
        return text.strip()
    except Exception as e:
        print(f"Transcription Error: {e}")
        return ""
