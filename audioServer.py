import asyncio
import json
import websockets
import soundcard as sc
import numpy as np
from collections import deque

# Audio capture settings
sampleRate = 44100      # Samples per second
chunkSize = 1024        # Samples per analysis chunk

# Frequency ranges for analysis
bassRangeStart = 60
bassRangeEnd = 250
midRangeStart = 251
midRangeEnd = 2000      # Core human voice range
highRangeStart = 2001
highRangeEnd = 6000


async def audioStreamHandler(websocket):
    """
    Handles WebSocket connection: captures audio, analyzes frequencies,
    sends real-time audio data to client.
    """
    
    print("Client connected --- Starting audio stream...")
    
    # Store last 5 bass values for smoothing (prevents jitter)
    bass_history = deque(maxlen=5)
    
    try:
        # Capture system audio from speaker
        with sc.get_microphone(
            id=str(sc.default_speaker().name),
            include_loopback=True
        ).recorder(samplerate=sampleRate, channels=1) as mic:
            
            while True:
                # Capture audio chunk
                data = mic.record(numframes=chunkSize)
                if data.size == 0:
                    continue
                
                # Convert to frequency domain (FFT analysis)
                fftData = np.fft.rfft(data[:, 0])
                fftFreq = np.fft.rfftfreq(len(data[:, 0]), 1.0 / sampleRate)
                
                # Find which frequencies fall into each range
                bassIndices = np.where((fftFreq >= bassRangeStart) & (fftFreq <= bassRangeEnd))
                midIndices = np.where((fftFreq >= midRangeStart) & (fftFreq <= midRangeEnd))
                highIndices = np.where((fftFreq >= highRangeStart) & (fftFreq <= highRangeEnd))
                
                # Calculate energy (magnitude) in each frequency band
                bassEnergy = np.mean(np.abs(fftData[bassIndices])) if bassIndices[0].size > 0 else 0
                midEnergy = np.mean(np.abs(fftData[midIndices])) if midIndices[0].size > 0 else 0
                highEnergy = np.mean(np.abs(fftData[highIndices])) if highIndices[0].size > 0 else 0
                
                # Normalize to 0-1 scale (divisors tuned for sensitivity)
                normalizedBass = min(bassEnergy / 30.0, 1.0)
                normalizedMids = min(midEnergy / 20.0, 1.0)
                normalizedHighs = min(highEnergy / 35.0, 1.0)
                
                # Smooth bass to reduce animation jitter
                bass_history.append(normalizedBass)
                smoothed_bass = np.mean(bass_history)
                
                # Send audio features to client
                payload = {
                    "bass": smoothed_bass,
                    "mids": normalizedMids,
                    "highs": normalizedHighs
                }
                await websocket.send(json.dumps(payload))
                await asyncio.sleep(0.01)
                
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")


async def mainAsync():
    """Start WebSocket server on localhost:1940"""
    
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