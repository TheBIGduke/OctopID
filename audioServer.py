import asyncio
import json
import websockets
import soundcard as sc
import numpy as np
from collections import deque
import threading
import time
import sys

# Central list of all valid moods, synchronized with the HTML file
AVAILABLE_MOODS = (
    'neutral', 'happy', 'sad', 'angry', 'surprised', 'love', 'dizzy',
    'thinking', 'sleepy', 'wink', 'scared', 'confused', 'sick', 'innocent', 'worried'
)

# --- Global state trackers ---
ACTIVE_CONNECTIONS = set()
initial_connection_made = False
is_audio_enabled = True

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
        if websocket in ACTIVE_CONNECTIONS:
            ACTIVE_CONNECTIONS.remove(websocket)


async def process_audio(websocket):
    """
    Captures system audio, performs FFT analysis, and sends the frequency
    data to a connected client in a continuous loop.
    """
    global is_audio_enabled
    bass_history = deque(maxlen=5)
    try:
        with sc.get_microphone(
            id=str(sc.default_speaker().name),
            include_loopback=True
        ).recorder(samplerate=sampleRate, channels=1) as mic:
            while True:
                if not is_audio_enabled:
                    await asyncio.sleep(0.1)
                    continue

                data = mic.record(numframes=chunkSize)
                if data.size == 0: continue

                fftData = np.fft.rfft(data[:, 0])
                fftFreq = np.fft.rfftfreq(len(data[:, 0]), 1.0 / sampleRate)
                bassIndices = np.where((fftFreq >= bassRangeStart) & (fftFreq <= bassRangeEnd))
                bassEnergy = np.mean(np.abs(fftData[bassIndices])) if bassIndices[0].size > 0 else 0
                normalizedBass = min(bassEnergy / 30.0, 1.0)
                bass_history.append(normalizedBass)
                smoothed_bass = np.mean(bass_history)
                
                payload = {"type": "audio", "bass": smoothed_bass}
                await websocket.send(json.dumps(payload))
                await asyncio.sleep(0.01)

    except websockets.exceptions.ConnectionClosed:
        pass


async def sendMood(websocket, mood_name):
    """Formats and sends a mood command to a client."""
    try:
        payload = {"type": "mood", "mood": mood_name}
        await websocket.send(json.dumps(payload))
        print(f"--> Sent command: '{mood_name}'")
    except websockets.exceptions.ConnectionClosed:
        pass

async def send_audio_off_signal(websocket):
    """Sends a zero-value audio packet to reset the client's mouth animation."""
    try:
        payload = {"type": "audio", "bass": 0}
        await websocket.send(json.dumps(payload))
    except websockets.exceptions.ConnectionClosed:
        pass


def terminal_input_loop(loop):
    """
    Runs in a background thread to provide a robust command-line interface.
    """
    global is_audio_enabled
    options_text = ", ".join(AVAILABLE_MOODS)
    loader_chars = ['|', '/', '-', '\\']

    while True:
        if not ACTIVE_CONNECTIONS:
            i = 0
            message = "Connection lost. Reconnecting... " if initial_connection_made else "Waiting for client connection... "
            sys.stdout.write("\r" + " " * 80 + "\r")
            while not ACTIVE_CONNECTIONS:
                print(f"\r{message}{loader_chars[i % len(loader_chars)]}", end="")
                sys.stdout.flush()
                i += 1
                time.sleep(0.2)
            
            # --- FIX: Corrected f-string for initial display ---
            print(f"\rClient connected! You can now send commands.      ")
            print(f"\n--- Available Commands ---\nMoods: {options_text}\nAudio: audio on, audio off")
        
        command = input("Enter command: ").strip().lower()

        if not ACTIVE_CONNECTIONS:
            continue

        if command == 'audio on':
            if not is_audio_enabled:
                is_audio_enabled = True
                print("--> Audio streaming ENABLED.")
        elif command == 'audio off':
            if is_audio_enabled:
                is_audio_enabled = False
                print("--> Audio streaming DISABLED.")
                # --- FIX: Send a reset signal to the client to close its mouth ---
                futures = [
                    asyncio.run_coroutine_threadsafe(send_audio_off_signal(ws), loop)
                    for ws in list(ACTIVE_CONNECTIONS)
                ]
                for future in futures:
                    future.result()
        elif command in AVAILABLE_MOODS:
            futures = [
                asyncio.run_coroutine_threadsafe(sendMood(ws, command), loop)
                for ws in list(ACTIVE_CONNECTIONS)
            ]
            for future in futures:
                future.result()
        elif command:
            print(f"Error: '{command}' is not a valid command.")
        
        if ACTIVE_CONNECTIONS and command:
             print(f"\n--- Available Commands ---\nMoods: {options_text}\nAudio: audio on, audio off")


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