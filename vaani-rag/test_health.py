import requests
import time
import subprocess
import os

proc = subprocess.Popen([r".\.venv\Scripts\python.exe", "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8001"])
time.sleep(3)

try:
    r = requests.get("http://127.0.0.1:8001/health")
    print("Health:", r.json())
except Exception as e:
    print("Error:", e)
finally:
    proc.terminate()
