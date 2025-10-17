import asyncio
import websockets
import json
import random
import time

# A list of all available moods from your server files.
AVAILABLE_MOODS = [
    'neutral', 'happy', 'sad', 'angry', 'surprised', 'love', 'dizzy',
    'doubtful', 'wink', 'scared', 'disappointed', 'innocent', 'worried'
]

async def send_command(websocket, command_type, params):
    """Sends a JSON command to the WebSocket server."""
    payload = {"type": command_type, **params}
    await websocket.send(json.dumps(payload))
    print(f"Sent command: {payload}")

async def octopid_controller_demo():
    """
    A demonstration script that connects to the OctopID server and
    sends a sequence of commands to showcase its functionality.
    """
    uri = "ws://localhost:8760"
    try:
        async with websockets.connect(uri) as websocket:
            print("Successfully connected to the OctopID server.")
            print("-" * 30)

            # --- Demonstrate Audio-Reactive Mode ---
            print("\nTesting the audio-reactive 'listening' mode...")
            print("Turning audio ON. Play some audio!")
            await send_command(websocket, "audio", {"command": "on"})
            await asyncio.sleep(8)  # Listen for 8 seconds

            print("\nTurning audio OFF.")
            await send_command(websocket, "audio", {"command": "off"})
            await asyncio.sleep(2)

            print("\nTurning audio ON.")
            await send_command(websocket, "audio", {"command": "on"})
            await asyncio.sleep(2)

            # --- Demonstrate Changing Moods ---
            print("\nCycling through some moods...")
            for mood in [AVAILABLE_MOODS[i] for i in range(len(AVAILABLE_MOODS))]:
                await send_command(websocket, "mood", {"mood": mood})
                await asyncio.sleep(2)

            print("\nTurning audio OFF.")
            await send_command(websocket, "audio", {"command": "off"})
            await asyncio.sleep(2)

            # --- Demonstrate the Built-in Demo Mode ---
            print("\nStarting the automatic demo mode...")
            await send_command(websocket, "demo", {"command": "start"})
            await asyncio.sleep(10) # Let the demo run for 10 seconds

            print("\nStopping the demo mode.")
            await send_command(websocket, "demo", {"command": "stop"})
            await asyncio.sleep(2)

            print("-" * 30)
            print("Demo finished successfully!")

    except ConnectionRefusedError:
        print(f"Connection to {uri} refused. Is the audioServer.py running?")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(octopid_controller_demo())