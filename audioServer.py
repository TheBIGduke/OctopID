import asyncio
import json
import websockets
import soundcard as sc
import numpy as np

# Audio Processing Parameters
sampleRate = 44100 # Audio sampler rate
chunkSize = 1024 # Number of frames per buffer

# Frequency Analysis Parameters
bassRangeStart = 60
bassRangeEnd = 250

async def audioStreamHandler(websocket, path):
    """
    Handles the Websocket connection, captures system audio,
    analizes it and sends data to the client.
    """
    print("Client connected --- Starting audio stream...")

    # Find the default speaker's monitor source (loopback)
    try:
        with sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True).recorder(samplerate=sampleRate, channels=1) as mic:
            while True:
                # Record a small chunk of audio data
                data = mic.record(numframes=chunkSize)
                # If there's no audio, continue
                if data.size == 0:
                    continue

                # Perform a Fast Fourier Transform (FFT)
                # We use rfft for real-valued input, which is more efficient
                fftData = np.fft.rfft(data[:,0])
                fftFreq = np.fft.rfftfreq(len(data))