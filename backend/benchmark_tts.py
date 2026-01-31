import requests
import time

# Use host.docker.internal to reach the host machine from inside Docker container
URL = "http://host.docker.internal:8001/synthesize"
TEXT = "The quick brown fox jumps over the lazy dog."

def benchmark():
    print(f"Benchmarking TTS with text: '{TEXT}'")
    
    payload = {
        "text": TEXT,
        "voice": "Vivian",
        "language": "English"
    }
    
    for i in range(1, 4):
        print(f"\n--- Iteration {i}/3 ---")
        try:
            req_start = time.time()
            response = requests.post(URL, json=payload, timeout=30)
            req_end = time.time()
            
            if response.status_code == 200:
                gen_time = response.headers.get("X-Generation-Time", "N/A")
                total_time = req_end - req_start
                
                print(f"Status: {response.status_code}")
                print(f"Total Request Latency: {total_time:.4f}s")
                print(f"Model Generation Time: {gen_time}s")
                
                if gen_time != "N/A":
                    gen_float = float(gen_time)
                    if gen_float < 0.2:
                        print("CONCLUSION: BLAZING FAST (Sub-200ms).")
                    elif gen_float < 1.0:
                        print("CONCLUSION: FAST (Sub-1s).")
                    else:
                        print("CONCLUSION: SLOW (>1s).")
            else:
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"Connection Error: {e}")

if __name__ == "__main__":
    benchmark()
