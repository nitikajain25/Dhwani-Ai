import wave
import struct

with wave.open("test_audio.wav", "w") as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(44100)
    for i in range(44100):
        value = int(32767.0)
        data = struct.pack("<h", value)
        f.writeframesraw(data)
