import uvicorn
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
import sys
import os
import io
import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel

# USER INSTRUCTION:
# Ensure you have activated your conda environment: `conda activate qwen3-tts`
# Then run this script: `python tts_server.py`

app = FastAPI()

# -----------------------------------------------------------------------------
# Qwen3-TTS Integration
# -----------------------------------------------------------------------------
print("Loading Qwen3-TTS Model (Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice)...")
try:
    model = Qwen3TTSModel.from_pretrained(
        "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice",
        device_map="auto",
        dtype=torch.bfloat16,
    )
    print("Qwen3-TTS Model Loaded Successfully.")
    
    if hasattr(model, 'device'):
         print(f"Model Device: {model.device}")
         
    try:
        # Check first parameter if possible
        if hasattr(model, 'parameters'):
             print(f"First Param Device: {next(model.parameters()).device}")
    except:
        pass
except Exception as e:
    print(f"Error loading Qwen3-TTS Model: {e}")
    print("Ensure you have 'qwen_tts', 'torch', 'soundfile' installed and CUDA available.")
    model = None

class SynthesisRequest(BaseModel):
    text: str
    voice: str = "Vivian" # Default to Vivian as requested
    language: str = "English" # Default to English, can be "Chinese"

@app.post("/synthesize")
def synthesize(req: SynthesisRequest):
    print(f"Synthesizing: '{req.text}' | Voice: '{req.voice}' | Lang: '{req.language}'")
    
    if model is None:
        raise HTTPException(status_code=500, detail="TTS Model is not loaded.")

    try:
        import time
        start_time = time.time()
        
        # Run Inference with inference_mode for speed
        with torch.inference_mode():
            wavs, sr = model.generate_custom_voice(
                text=req.text,
                language=req.language, 
                speaker=req.voice,
                instruct="" # Optional instruction
            )
        
        generation_time = time.time() - start_time
        print(f"Generation took: {generation_time:.4f}s")
        
        # Convert to WAV bytes in memory
        with io.BytesIO() as buffer:
            sf.write(buffer, wavs[0], sr, format='WAV')
            audio_bytes = buffer.getvalue()
            
        return Response(
            content=audio_bytes, 
            media_type="audio/wav",
            headers={"X-Generation-Time": str(generation_time)}
        )
            
    except Exception as e:
        print(f"Synthesis Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
def status():
    return {"status": "ok", "service": "tts_host_server", "model_loaded": model is not None}

if __name__ == "__main__":
    # Host 0.0.0.0 is important to be reachable from Docker container via host.docker.internal
    uvicorn.run(app, host="0.0.0.0", port=8001)
