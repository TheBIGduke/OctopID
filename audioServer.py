import asyncio
import json
import websockets
import soundcard as sc
import numpy as np
from collections import deque
import threading
import time
import sys

# Central list of all valid moods
AVAILABLE_MOODS = (
    'neutral', 'happy', 'sad', 'angry', 'surprised', 'love', 'dizzy',
    'thinking', 'wink', 'scared', 'confused', 'innocent', 'worried'
)

# --- Global state trackers ---
ACTIVE_CONNECTIONS = set()
initial_connection_made = False

# --- Audio settings ---
sampleRate = 44100
chunkSize = 1024
bassRangeStart, bassRangeEnd = 60, 250
midRangeStart, midRangeEnd = 251, 2000
highRangeStart, highRangeEnd = 2001, 6000


async def audioStreamHandler(websocket):
    """
    Handles a new client connection. Sets the global state and starts the
    audio processing loop, ensuring silent clean-up on disconnection.
    """
    global initial_connection_made
    if not initial_connection_made:
        initial_connection_made = True

    ACTIVE_CONNECTIONS.add(websocket)
    try:
        await process_audio(websocket)
    finally:
        # Silently remove the connection. The terminal loop handles all UI.
        if websocket in ACTIVE_CONNECTIONS:
            ACTIVE_CONNECTIONS.remove(websocket)


async def process_audio(websocket):
    """
    Captures system audio, performs FFT analysis, and sends the frequency
    data to a connected client in a continuous loop.
    """
    bass_history = deque(maxlen=5)
    try:
        with sc.get_microphone(
            id=str(sc.default_speaker().name),
            include_loopback=True
        ).recorder(samplerate=sampleRate, channels=1) as mic:
            while True:
                data = mic.record(numframes=chunkSize)
                if data.size == 0: continue

                # --- Frequency Analysis & Processing ---
                fftData = np.fft.rfft(data[:, 0])
                fftFreq = np.fft.rfftfreq(len(data[:, 0]), 1.0 / sampleRate)
                bassIndices = np.where((fftFreq >= bassRangeStart) & (fftFreq <= bassRangeEnd))
                midIndices = np.where((fftFreq >= midRangeStart) & (fftFreq <= midRangeEnd))
                highIndices = np.where((fftFreq >= highRangeStart) & (fftFreq <= highRangeEnd))
                bassEnergy = np.mean(np.abs(fftData[bassIndices])) if bassIndices[0].size > 0 else 0
                midEnergy = np.mean(np.abs(fftData[midIndices])) if midIndices[0].size > 0 else 0
                highEnergy = np.mean(np.abs(fftData[highIndices])) if highIndices[0].size > 0 else 0
                normalizedBass = min(bassEnergy / 30.0, 1.0)
                normalizedMids = min(midEnergy / 20.0, 1.0)
                normalizedHighs = min(highEnergy / 35.0, 1.0)
                bass_history.append(normalizedBass)
                smoothed_bass = np.mean(bass_history)
                
                payload = {"type": "audio", "bass": smoothed_bass, "mids": normalizedMids, "highs": normalizedHighs}
                await websocket.send(json.dumps(payload))
                await asyncio.sleep(0.01)

    except websockets.exceptions.ConnectionClosed:
        # Catch any disconnection error silently.
        pass


async def sendMood(websocket, mood_name):
    """Formats and sends a mood command to a client."""
    try:
        payload = {"type": "mood", "mood": mood_name}
        await websocket.send(json.dumps(payload))
        print(f"--> Sent command: '{mood_name}'")
    except websockets.exceptions.ConnectionClosed:
        pass


def terminal_input_loop(loop):
    """
    Runs in a background thread to provide a robust command-line interface.
    This function is the single source of truth for all status messages.
    """
    options_text = ", ".join(AVAILABLE_MOODS)
    loader_chars = ['|', '/', '-', '\\']

    while True:
        # --- 1. Wait for a connection and display loading/reconnecting screen ---
        if not ACTIVE_CONNECTIONS:
            i = 0
            message = "Connection lost. Reconnecting... " if initial_connection_made else "Waiting for client connection... "
            # Clear the line where input might have been, in case of a disconnect
            sys.stdout.write("\r" + " " * 80 + "\r")
            while not ACTIVE_CONNECTIONS:
                print(f"\r{message}{loader_chars[i % len(loader_chars)]}", end="")
                sys.stdout.flush()
                i += 1
                time.sleep(0.2)

            print(f"\rClient connected! You can now send moods.")
            print("\n--- Available Moods ---")
            print(options_text)
        
        # --- 2. Get user input ---
        mood_name = input("Enter mood to send: ").strip().lower()

        # --- 3. This is the crucial fix for a disconnect during input() ---
        if not ACTIVE_CONNECTIONS:
            continue 

        if not mood_name:
            print("\n--- Available Moods ---")
            print(options_text)
            continue

        if mood_name not in AVAILABLE_MOODS:
            print(f"Error: '{mood_name}' is not a valid mood.")
            print("\n--- Available Moods ---")
            print(options_text)
            continue

        # --- 4. Send the command ---
        futures = [
            asyncio.run_coroutine_threadsafe(sendMood(ws, mood_name), loop)
            for ws in list(ACTIVE_CONNECTIONS)
        ]
        for future in futures:
            future.result()
        
        if ACTIVE_CONNECTIONS:
            print("\n--- Available Moods ---")
            print(options_text)


async def mainAsync():
    """Starts the WebSocket server and the background terminal input thread."""
    serverAddress = "localhost"
    serverPort = 1940

    print(f"Starting WebSocket server on ws://{serverAddress}:{serverPort}")

    loop = asyncio.get_running_loop()
    input_thread = threading.Thread(target=terminal_input_loop, args=(loop,), daemon=True)
    input_thread.start()

    async with websockets.serve(audioStreamHandler, serverAddress, serverPort):
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(mainAsync())
    except KeyboardInterrupt:
        print("\nServer stopped")