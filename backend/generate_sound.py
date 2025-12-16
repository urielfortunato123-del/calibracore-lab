import wave
import math
import struct

def generate_beep(filename="beep.wav", duration=0.5, frequency=440.0):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    amplitude = 16000
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for i in range(n_samples):
            value = int(amplitude * math.sin(2 * math.pi * frequency * i / sample_rate))
            data = struct.pack('<h', value)
            wav_file.writeframes(data)

if __name__ == "__main__":
    # Create output directory
    import os
    os.makedirs("../frontend/assets", exist_ok=True)
    
    # Generate alert sound
    generate_beep("../frontend/assets/alert.wav", duration=0.5, frequency=880.0)
    print("Sound file created.")
