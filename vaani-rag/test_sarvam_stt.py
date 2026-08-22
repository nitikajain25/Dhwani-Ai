from backend.services.sarvam_service import get_sarvam_service
import sys
sys.stdout.reconfigure(encoding='utf-8')

def test_stt():
    try:
        sarvam = get_sarvam_service()
    except ValueError as e:
        print("Failure:", e)
        sys.exit(0)

    try:
        with open("test_out.wav", "rb") as f:
            audio_bytes = f.read()
            
        transcript, lang, lat = sarvam.transcribe(audio_bytes, language_code="hi-IN")
        print("Success: True")
        print("Transcript:", transcript)
        print("Language:", lang)
        print("STT Latency (ms):", lat)
    except Exception as e:
        print("Failure:", e)

if __name__ == "__main__":
    test_stt()


