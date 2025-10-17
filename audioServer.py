import asyncio
import json
import websockets
import soundcard as sc
import numpy as np
from collections import deque
import time
import sys

# Central list of all valid moods, synchronized with the HTML file
AVAILABLE_MOODS = (
    'neutral', 'happy', 'sad', 'angry', 'surprised', 'love', 'dizzy',
    'doubtful', 'wink', 'scared', 'disappointed', 'innocent', 'worried'
)

# --- Global state trackers for a single client ---
ACTIVE_CLIENT = None
is_audio_enabled = False
is_demo_running = False

# --- Audio settings ---
sampleRate = 44100
chunkSize = 1024
bassRangeStart, bassRangeEnd = 60, 250
midRangeStart, midRangeEnd = 251, 2000
highRangeStart, highRangeEnd = 2001, 6000


async def send_mood(mood_name):
    """Sends a mood command to the single active client."""
    if ACTIVE_CLIENT:
        try:
            payload = json.dumps({"type": "mood", "mood": mood_name})
            await ACTIVE_CLIENT.send(payload)
        except websockets.exceptions.ConnectionClosed:
            pass # The main handler will perform cleanup

async def send_audio_off_signal():
    """Sends a reset audio signal to the single active client."""
    if ACTIVE_CLIENT:
        try:
            payload = json.dumps({"type": "audio", "bass": 0})
            await ACTIVE_CLIENT.send(payload)
        except websockets.exceptions.ConnectionClosed:
            pass

async def run_demo_mode():
    """Cycles through all available moods for the single client."""
    global is_demo_running
    
    try:
        print("--> Demo mode started via WebSocket.")
        demo_moods = [mood for mood in AVAILABLE_MOODS if mood != 'neutral']
        
        for mood in demo_moods:
            if not is_demo_running: break
            await send_mood(mood)
            
            # Interruptible 3-second delay
            for _ in range(30):
                if not is_demo_running: break
                await asyncio.sleep(0.1)
    finally:
        is_demo_running = False
        print("--> Demo finished or interrupted. Resetting to 'neutral'.")
        await send_mood('neutral')

async def process_audio():
    """
    Captures system audio, performs FFT analysis, and sends the frequency
    data to the single active client.
    """
    global is_audio_enabled
    bass_history = deque(maxlen=5)
    try:
        with sc.get_microphone(
            id=str(sc.default_speaker().name),
            include_loopback=True
        ).recorder(samplerate=sampleRate, channels=1) as mic:
            while True:
                if not is_audio_enabled or not ACTIVE_CLIENT:
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
                
                payload = json.dumps({"type": "audio", "bass": smoothed_bass})
                try:
                    await ACTIVE_CLIENT.send(payload)
                except websockets.exceptions.ConnectionClosed:
                    pass # The client_handler will manage the disconnect
                await asyncio.sleep(0.01)

    except Exception as e:
        print(f"Audio processing error: {e}. Audio streaming will stop.")
        is_audio_enabled = False


async def client_handler(websocket):
    """
    Handles a client connection, listening for commands and managing state.
    Ensures only one client is connected at a time.
    """
    global ACTIVE_CLIENT, is_audio_enabled, is_demo_running
    
    if ACTIVE_CLIENT:
        print("New client connected, replacing the previous one.")
        await ACTIVE_CLIENT.close(code=1000, reason="New connection established")
    else:
        print("Client connected! Server is now controlled via WebSocket messages.")
        
    ACTIVE_CLIENT = websocket
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                command_type = data.get("type")

                if command_type != "demo" and is_demo_running:
                    print("--> Demo interrupted by new command.")
                    is_demo_running = False
                    await asyncio.sleep(0.1)

                if command_type == "mood":
                    mood = data.get("mood")
                    if mood in AVAILABLE_MOODS:
                        print(f"<-- Received command: '{mood}'")
                        await send_mood(mood)
                
                elif command_type == "audio":
                    command = data.get("command")
                    if command == "on" and not is_audio_enabled:
                        is_audio_enabled = True
                        print("<-- Audio streaming ENABLED.")
                    elif command == "off" and is_audio_enabled:
                        is_audio_enabled = False
                        print("<-- Audio streaming DISABLED.")
                        await send_audio_off_signal()

                elif command_type == "demo":
                    command = data.get("command")
                    if command == "start" and not is_demo_running:
                        is_demo_running = True
                        asyncio.create_task(run_demo_mode())
                    elif command == "stop" and is_demo_running:
                        print("<-- Received command: stop demo")
                        is_demo_running = False

            except json.JSONDecodeError:
                print("Error: Received invalid JSON message.")
            except Exception as e:
                print(f"An error occurred while processing a message: {e}")
    finally:
        # Check if the disconnected client is the one we were tracking
        if ACTIVE_CLIENT == websocket:
            ACTIVE_CLIENT = None
            print("Client disconnected.")
            print("Waiting for a new connection...")


async def mainAsync():
    """Starts the WebSocket server and the background audio processing task."""
    serverAddress = "localhost"
    serverPort = 8760
    print(f"Starting WebSocket server on ws://{serverAddress}:{serverPort}")
    print("Waiting for client connection...")

    asyncio.create_task(process_audio())

    async with websockets.serve(client_handler, serverAddress, serverPort):
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(mainAsync())
    except KeyboardInterrupt:
        print("\nServer stopped")