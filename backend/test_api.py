import requests
import uuid

BASE_URL = "http://localhost:8000/api"

def test_conversation():
    session_id = str(uuid.uuid4())
    print(f"Testing with Session ID: {session_id}")
    
    # 1. Test Simple Query
    print("\n[TEST 1] Sending query: 'Do you have anything spicy?'")
    try:
        response = requests.post(
            f"{BASE_URL}/conversation",
            data={"session_id": session_id, "text": "Do you have anything spicy?"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

    # 2. Test Order Placement
    print("\n[TEST 2] Sending order: 'I will take one Volcano Burger please.'")
    try:
        response = requests.post(
            f"{BASE_URL}/conversation",
            data={"session_id": session_id, "text": "I will take one Volcano Burger please."}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

    # 4. Test Audio Upload (Synthesized Sine Wave)
    print("\n[TEST 4] Testing Audio Upload...")
    import wave
    import struct
    
    # Generate a simple 1-second silence/tone WAV
    wav_filename = "test_audio.wav"
    with wave.open(wav_filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        wav_file.writeframes(b'\x00\x00' * 16000) # 1 second of silence
        
    try:
        with open(wav_filename, 'rb') as f:
            files = {'audio': (wav_filename, f, 'audio/wav')}
            data = {'session_id': session_id}
            response = requests.post(f"{BASE_URL}/conversation", data=data, files=files)
            print(f"Status: {response.status_code}")
            resp_json = response.json()
            print(f"Response (Text): {resp_json.get('reply_text')}")
            
            if "audio_base64" in resp_json:
                print("SUCCESS: Audio response received!")
                import base64
                with open("response_audio.wav", "wb") as f:
                    f.write(base64.b64decode(resp_json["audio_base64"]))
                print("Saved response_audio.wav")
            else:
                print("WARNING: No audio_base64 in response.")

            if "user_transcript" in resp_json:
                print(f"SUCCESS: User transcript received: '{resp_json['user_transcript']}'")
            else:
                print("WARNING: No user_transcript in response.")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import json
    test_conversation()
