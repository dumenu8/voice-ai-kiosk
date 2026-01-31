import requests
import os

# Connect to the host machine from inside Docker
TTS_API_URL = os.getenv("TTS_API_URL", "http://host.docker.internal:8001")

def synthesize(text: str) -> bytes:
    """
    Sends text to the external TTS server (running on host) and returns audio bytes.
    """
    try:
        url = f"{TTS_API_URL}/synthesize"
        payload = {
            "text": text,
            "voice": "vivian"
        }
        response = requests.post(url, json=payload, timeout=30.0)
        
        if response.status_code == 200:
            return response.content
        else:
            print(f"TTS Error {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"TTS Connection Error: {e}")
        return None
