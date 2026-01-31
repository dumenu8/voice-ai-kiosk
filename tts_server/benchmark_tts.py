import requests
import time

URL = "http://localhost:8001/synthesize"
TEXT = "The quick brown fox jumps over the lazy dog."

def benchmark():
    print(f"Benchmarking TTS with text: '{TEXT}'")
    
    payload = {
        "text": TEXT,
        "voice": "Vivian",
        "language": "English"
    }
    
    try:
        # Warm-up (network etc)
        print("Sending request...")
        req_start = time.time()
        response = requests.post(URL, json=payload, timeout=30)
        req_end = time.time()
        
        if response.status_code == 200:
            gen_time = response.headers.get("X-Generation-Time", "N/A")
            total_time = req_end - req_start
            
            print("-" * 30)
            print(f"Status: {response.status_code}")
            print(f"Total Request Latency: {total_time:.4f}s")
            print(f"Model Generation Time: {gen_time}s")
            print("-" * 30)
            
            if gen_time != "N/A":
                gen_float = float(gen_time)
                if gen_float < 0.5:
                    print("CONCLUSION: Performance is EXCELLENT (Sub-500ms).")
                elif gen_float < 1.0:
                    print("CONCLUSION: Performance is GOOD.")
                else:
                    print("CONCLUSION: Performance could be improved.")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Connection Error: {e}")
        print("Ensure tts_server.py is running on localhost:8001")

if __name__ == "__main__":
    benchmark()
