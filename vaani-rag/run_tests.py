import subprocess
import time
import requests

print("Starting backend...")
proc = subprocess.Popen([r".\.venv\Scripts\python.exe", "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"])
time.sleep(5)

try:
    print("Testing /health")
    r1 = requests.get("http://127.0.0.1:8000/health")
    print(r1.json())
    
    print("\nTesting /api/demo/text (KNOWN)")
    r2 = requests.post("http://127.0.0.1:8000/api/demo/text", json={"question": "What is mediation?"})
    print(r2.json())
    
    print("\nTesting /api/demo/voice (KNOWN)")
    with open("test_audio.wav", "rb") as f:
        r3 = requests.post("http://127.0.0.1:8000/api/demo/voice", files={"file": f})
    print("Voice response headers:", r3.headers.get("x-rag-metadata"))
    
    print("\nTesting /api/demo/text (UNKNOWN)")
    r4 = requests.post("http://127.0.0.1:8000/api/demo/text", json={"question": "What is the capital of France?"})
    print(r4.json())

except Exception as e:
    print("Error:", e)
finally:
    proc.terminate()
