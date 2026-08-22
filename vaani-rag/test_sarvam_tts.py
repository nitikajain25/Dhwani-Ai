from backend.services.sarvam_service import get_sarvam_service
import sys

def test_tts():
    try:
        sarvam = get_sarvam_service()
    except ValueError as e:
        print("Failure:", e)
        sys.exit(0)

    try:
        audio_out, lat = sarvam.synthesize("Welcome to Dhawani.", language_code="en-IN")
        if audio_out:
            with open("test_out.wav", "wb") as f:
                f.write(audio_out)
        print("Success: True")
        print("Output file: test_out.wav")
        print("TTS Latency (ms):", lat)
    except Exception as e:
        print("Failure:", e)

if __name__ == "__main__":
    test_tts()
