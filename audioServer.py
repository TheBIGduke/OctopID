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

async def audioStreamHandler(websocket):
    """
    Handles the Websocket connection, captures system audio,
    analyzes it and sends data to the client.
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
                fftFreq = np.fft.rfftfreq(len(data[:, 0]), 1.0 / sampleRate)

                # Feature Extraction: Calculate Bass Energy
                # Find the indices corresponding to our defined bass range
                bassIndices = np.where((fftFreq >= bassRangeStart) & (fftFreq <= bassRangeEnd))

                # Calculate the average magnitude in the bass range
                bassEnergy = np.mean(np.abs(fftData[bassIndices]))

                # Normalize the value to a 0-1 range (simple normalization)
                normalizedBass = min(bassEnergy / 50.0, 1.0) # Adjust to your system's volume

                payload = {
                    "bass": normalizedBass
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