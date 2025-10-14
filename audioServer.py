import asyncio
import json
import websockets
import soundcard as sc
import numpy as np
from collections import deque

# Audio Processing Parameters
sampleRate = 44100
chunkSize = 1024

# Expanded Frequency Analysis Parameters for Speech
bassRangeStart = 60
bassRangeEnd = 250
midRangeStart = 251
midRangeEnd = 2000  # Core range for human voice
highRangeStart = 2001
highRangeEnd = 6000 # Range for consonants and sibilance

async def audioStreamHandler(websocket):
    """
    Handles the Websocket connection, captures system audio,
    analyzes it and sends data to the client.
    """
    print("Client connected --- Starting audio stream...")
    bass_history = deque(maxlen=5) # Store the last 5 bass values for smoothing

    try:
        with sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True).recorder(samplerate=sampleRate, channels=1) as mic:
            while True:
                data = mic.record(numframes=chunkSize)
                if data.size == 0:
                    continue

                fftData = np.fft.rfft(data[:, 0])
                fftFreq = np.fft.rfftfreq(len(data[:, 0]), 1.0 / sampleRate)

                # --- Feature Extraction for Bass, Mids, and Highs ---
                bassIndices = np.where((fftFreq >= bassRangeStart) & (fftFreq <= bassRangeEnd))
                midIndices = np.where((fftFreq >= midRangeStart) & (fftFreq <= midRangeEnd))
                highIndices = np.where((fftFreq >= highRangeStart) & (fftFreq <= highRangeEnd))

                bassEnergy = np.mean(np.abs(fftData[bassIndices])) if bassIndices[0].size > 0 else 0
                midEnergy = np.mean(np.abs(fftData[midIndices])) if midIndices[0].size > 0 else 0
                highEnergy = np.mean(np.abs(fftData[highIndices])) if highIndices[0].size > 0 else 0

                # Normalize each value. These divisors are tuned for sensitivity.
                normalizedBass = min(bassEnergy / 30.0, 1.0)
                
                # --- Smoothing ---
                bass_history.append(normalizedBass)
                smoothed_bass = np.mean(bass_history)

                normalizedMids = min(midEnergy / 20.0, 1.0)  # Mids are most important for voice
                normalizedHighs = min(highEnergy / 35.0, 1.0)

                payload = {
                    "bass": smoothed_bass, # Use the smoothed value
                    "mids": normalizedMids,
                    "highs": normalizedHighs
                }

                await websocket.send(json.dumps(payload))
                await asyncio.sleep(0.01)
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
    except Exception as e:
        print(f"An error occurred: {e}")

async def mainAsync():
    """Starts the WebSocket server"""
    serverAddress = "localhost"
    serverPort = 1940
    print(f"Starting WebSocket server on ws://{serverAddress}:{serverPort}")

    async with websockets.serve(audioStreamHandler, serverAddress, serverPort):
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(mainAsync())
    except KeyboardInterrupt:
        print("Server stopped")