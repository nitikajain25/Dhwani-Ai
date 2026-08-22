import os
import sys
import argparse
import time
from pathlib import Path

# Try importing SDKs gracefully
try:
    import dotenv
except ImportError:
    print("python-dotenv SDK is missing. Install with:\npython -m pip install python-dotenv")
    sys.exit(1)

try:
    import sarvamai
    from sarvamai import SarvamAI
except ImportError:
    print("Sarvam SDK is missing. Install with:\npython -m pip install sarvamai")
    sys.exit(1)

try:
    from google import genai
except ImportError:
    print("Gemini SDK is missing. Install with:\npython -m pip install google-genai")
    sys.exit(1)

def print_separator(title):
    print("-" * 50)
    print(title.upper())
    print("-" * 50)

def main():
    parser = argparse.ArgumentParser(description="Dhawani Sarvam + Gemini Integration Test")
    parser.add_argument("audio_file", nargs="?", help="Path to the audio file for STT testing")
    parser.add_argument("--text", help="Text input to bypass Sarvam STT and test Gemini directly")
    
    args = parser.parse_args()

    if not args.audio_file and not args.text:
        parser.print_help()
        sys.exit(1)

    # 1. Environment Variables
    dotenv.load_dotenv()
    sarvam_key = os.getenv("SARVAM_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    print(f"Sarvam API key: {'SET' if sarvam_key else 'MISSING'}")
    print(f"Gemini API key: {'SET' if gemini_key else 'MISSING'}")

    if not sarvam_key and not args.text:
        print("\nERROR: SARVAM_API_KEY is missing from .env")
        sys.exit(1)
        
    if not gemini_key:
        print("\nERROR: GEMINI_API_KEY is missing from .env")
        sys.exit(1)

    audio_bytes = None
    if args.audio_file:
        audio_path = Path(args.audio_file)
        if not audio_path.exists():
            print(f"\nERROR: Audio file '{args.audio_file}' does not exist.")
            sys.exit(1)
        
        try:
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()
        except Exception as e:
            print(f"\nERROR: Failed to read audio file: {str(e)}")
            sys.exit(1)

    stt_pass = False
    gemini_pass = False
    
    transcript = ""
    language = "unknown"
    answer = ""
    
    stt_ms = 0.0
    gemini_ms = 0.0
    total_ms = 0.0

    total_t0 = time.perf_counter()

    # 4. SARVAM STT TEST
    if not args.text:
        print_separator("SARVAM STT")
        try:
            sarvam_client = SarvamAI(api_subscription_key=sarvam_key)
            stt_t0 = time.perf_counter()
            
            response = sarvam_client.speech_to_text.transcribe(
                file=audio_bytes,
                model="saaras:v3",
                mode="transcribe"
            )
            
            stt_ms = (time.perf_counter() - stt_t0) * 1000.0
            
            if hasattr(response, 'data') and response.data:
                data = response.data[0] if isinstance(response.data, list) else response.data
                transcript = getattr(data, 'transcript', getattr(data, 'text', ''))
                language = getattr(data, 'language_code', language)
            elif hasattr(response, 'transcript'):
                transcript = response.transcript
                language = getattr(response, 'language_code', language)
                
            transcript = transcript.strip()
            
            if not transcript:
                print("Status: FAILED")
                print("Error: Empty transcript received from Sarvam")
                sys.exit(1)
                
            print("Status: SUCCESS")
            print(f"Transcript: {transcript}")
            print(f"Language: {language}")
            print(f"STT latency: {stt_ms:.2f} ms\n")
            stt_pass = True
            
        except Exception as e:
            print("Status: FAILED")
            print(f"Error calling Sarvam API: {str(e)}")
            sys.exit(1)
    else:
        transcript = args.text.strip()
        print_separator("STT BYPASSED")
        print(f"Using provided text: {transcript}\n")
        stt_pass = True

    # 5. GEMINI TEST
    print_separator("GEMINI")
    try:
        genai_client = genai.Client(api_key=gemini_key)
        
        prompt = (
            "You are a helpful multilingual assistant. Answer the user's question clearly and concisely.\n\n"
            f"User question:\n{transcript}"
        )
        
        gemini_t0 = time.perf_counter()
        gemini_response = genai_client.models.generate_content(
            model=gemini_model,
            contents=prompt
        )
        gemini_ms = (time.perf_counter() - gemini_t0) * 1000.0
        
        answer = (gemini_response.text or "").strip()
        
        if not answer:
            print("Status: FAILED")
            print("Error: Empty response received from Gemini")
            sys.exit(1)
            
        print("Status: SUCCESS")
        print(f"Model: {gemini_model}")
        print("Answer:")
        print(answer)
        print(f"\nGemini latency: {gemini_ms:.2f} ms\n")
        gemini_pass = True
        
    except Exception as e:
        print("Status: FAILED")
        print(f"Error calling Gemini API: {str(e)}")
        sys.exit(1)

    total_ms = (time.perf_counter() - total_t0) * 1000.0

    # 7. RESULT SUMMARY
    overall_pass = stt_pass and gemini_pass
    
    print("==================================================")
    print("DHAWANI SARVAM + GEMINI TEST")
    print("==================================================")
    print(f"Sarvam STT: {'PASS' if stt_pass else 'FAIL'}")
    print(f"Gemini: {'PASS' if gemini_pass else 'FAIL'}\n")
    
    print("Transcript:")
    print(transcript)
    print("\nAnswer:")
    print(answer)
    print("\nLatency:")
    if not args.text:
        print(f"STT: {stt_ms:.2f} ms")
    print(f"Gemini: {gemini_ms:.2f} ms")
    print(f"Total: {total_ms:.2f} ms\n")
    
    print("Overall:")
    print("PASS" if overall_pass else "FAIL")
    
    if not overall_pass:
        sys.exit(1)

if __name__ == "__main__":
    main()
