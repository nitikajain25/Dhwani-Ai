import os
from google import genai
from dotenv import load_dotenv
import time

load_dotenv()

def test_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Failure: GEMINI_API_KEY environment variable is not set.")
        return
        
    try:
        client = genai.Client(api_key=api_key)
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        t0 = time.time()
        response = client.models.generate_content(
            model=model,
            contents="Reply with exactly: GEMINI_OK"
        )
        lat = (time.time() - t0) * 1000
        
        print("Success: True")
        print("Model:", model)
        print(f"Latency (ms): {lat:.2f}")
        print("Response:", response.text.strip())
    except Exception as e:
        print("Failure:", e)

if __name__ == "__main__":
    test_gemini()
