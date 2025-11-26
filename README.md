# OctopID - Animated Expression System

[![HTML5](https://img.shields.io/badge/HTML5-Ready-orange.svg)](https://developer.mozilla.org/en-US/docs/Web/Guide/HTML/HTML5)
[![SVG](https://img.shields.io/badge/SVG-Animated-brightgreen.svg)](https://developer.mozilla.org/en-US/docs/Web/SVG)
[![WebSocket](https://img.shields.io/badge/WebSocket-Enabled-blue.svg)](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
[![Python](https://img.shields.io/badge/Python-3.7+-yellow.svg)](https://www.python.org/)

OctopID is an expressive, animated face system built with **SVG** and **JavaScript**. It features 13 unique emotional expressions with smooth transitions, automatic eye movements (panning and blinking), and a special **audio-reactive "listening" mode** that synchronizes mouth movements with real-time audio input via WebSocket streaming. Perfect for virtual assistants, chatbots, interactive characters, or live audio visualization.

![OctopID Face Animation](face.gif)

## Features

- **13 Unique Expressions** – From neutral to happy, sad, angry, surprised, and more exotic emotions like dizzy or innocent.
- **Real-time Audio Synchronization** – Audio-reactive mode captures system audio via WebSocket and animates the mouth to match speech patterns using FFT frequency analysis.
- **Smooth Animations** – CSS transitions create fluid movements between expressions and eye states with configurable interpolation.
- **Automatic Eye Behaviors** – Eyes blink naturally and pan randomly to simulate lifelike attention.
- **Fully Customizable** – Easily modify colors, shapes, speeds, and audio sensitivity through CSS variables and JavaScript parameters.
- **WebSocket Architecture** – Python backend performs FFT audio analysis and streams normalized frequency data (bass) to the frontend.
- **Spanish Language Optimized** – Audio frequency ranges tuned for Spanish speech patterns (mid-range frequencies 251-2000 Hz for vowel detection).
- **No External Dependencies (Frontend)** – Pure HTML5, CSS3, and vanilla JavaScript. No frameworks required.
- **Remote Control Capable** – Send mood and audio commands via WebSocket from any Python script.
- **Responsive Design** – Fullscreen face display that scales to any viewport size.

---

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Reference](#quick-reference)
- [Quick Start](#quick-start)
  - [Mode 1: Audio Server + HTML (Always Listening Mode)](#mode-1-audio-server--html-always-listening-mode)
  - [Mode 2: Terminal Input + HTML (Interactive Control)](#mode-2-terminal-input--html-interactive-control)
  - [Mode 3: Kiosk Deployment (octopid.sh)](#mode-3-kiosk-deployment-octopidsh)
- [WebSocket API Reference](#websocket-api-reference)
- [Configuration](#configuration)
  - [Visual Customization](#visual-customization)
  - [Audio Configuration](#audio-configuration)
  - [Expression Customization](#expression-customization)
- [Audio Server Deep Dive](#audio-server-deep-dive)
  - [How It Works](#how-it-works)
  - [FFT Analysis Explained](#fft-analysis-explained)
  - [Frequency Band Configuration](#frequency-band-configuration)
  - [Smoothing Algorithm](#smoothing-algorithm)
- [SVG Shape Creation Tutorial](#svg-shape-creation-tutorial)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)

---

## Requirements

### Hardware

- A computer with audio output (speakers/headphones) for audio-reactive mode.

### Software

- **Frontend (face.html):**
  - **Chromium-based browser** (Google Chrome, Microsoft Edge, Brave, etc.) - Required for WebSocket stability
  - Modern browser with SVG and WebSocket support

- **Backend (audioServer.py, terminalInput.py, demo.py):**
  - Python 3.7 or higher
  - Required Python packages:
    ```bash
    pip install websockets soundcard numpy
    ```

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/OctopID.git
cd OctopID
```

### 2. Install Python Dependencies

```bash
pip install websockets==15.0.1 soundcard==0.4.5 numpy==1.21.5
```
---
## Quick Reference

### Available Moods
```
neutral, happy, sad, angry, surprised, love, dizzy,
doubtful, wink, scared, disappointed, innocent, worried
```

### Server Address
```
WebSocket: ws://localhost:8760
```

### File Run Commands
```bash
# Mode 1: Audio Server (standard mode)
python3 audioServer.py
chromium face.html

# Mode 2: Terminal Control (interactive mode)
python3 terminalInput.py
chromium face.html

# Demo (requires Mode 1 running)
python3 audioServer.py
chromium face.html
python3 demo.py  # In separate terminal
```

### JSON Message Format
```json
// Change mood
{"type": "mood", "mood": "happy"}

// Enable/disable audio
{"type": "audio", "command": "on"}
{"type": "audio", "command": "off"}
```
---

## Quick Start

OctopID offers **two modes of operation** depending on your use case:

### Mode 1: Audio Server + HTML (Always Listening Mode)

This is the **standard mode** for audio-reactive applications. The face automatically responds to system audio and accepts remote commands.

**⚠️ IMPORTANT:** Both the audio server and the HTML file must be running simultaneously.

#### Step 1: Start the Audio Server

In a terminal, run:
```bash
python3 audioServer.py
```

You should see:
```
Starting WebSocket server on ws://localhost:8760
Waiting for client connections...
```

#### Step 2: Open the Face Interface

**Using Chromium (Required):**
```bash
chromium face.html

# Or simply open face.html in your Chromium browser
```

The face will automatically:
- Connect to the WebSocket server
- Display in fullscreen
- Start responding to system audio

#### Step 3: Test Audio Response

1. Play any audio on your computer (music, YouTube, TTS, etc.)
2. The mouth will animate in real-time matching the audio intensity
3. Leave both the server and browser running

#### Step 4: Send Remote Commands (Optional)

While the server and face are running, you can send commands from another terminal:

**Option A: Run the demo script** to see an automated demonstration:
```bash
python3 demo.py
```

The demo will:
1. Enable audio for 8 seconds
2. Disable audio
3. Re-enable audio for 2 seconds
4. Cycle through all 13 moods (2 seconds each)
5. Disable audio and disconnect

**Demo Output Example:**
```
Successfully connected to the OctopID server.
------------------------------

Testing the audio-reactive 'listening' mode...
Turning audio ON. Play some speech audio!
Sent command: {'type': 'audio', 'command': 'on'}

Cycling through some moods...
Sent command: {'type': 'mood', 'mood': 'neutral'}
Sent command: {'type': 'mood', 'mood': 'happy'}
...

Demo finished successfully!
```

**Option B: Create your own control script** (see [WebSocket API Reference](#websocket-api-reference) for examples)

---

### Mode 2: Terminal Input + HTML (Interactive Control)

This mode provides **manual control** via terminal commands. Ideal for testing, live performances, and interactive demonstrations.

**⚠️ IMPORTANT:** When using `terminalInput.py`, you do NOT need to run `audioServer.py` or `demo.py`.

#### Step 1: Start Terminal Input Server

In a terminal, run:
```bash
python3 terminalInput.py
```

You should see:
```
Starting WebSocket server on ws://localhost:8760
Waiting for client connection...
```

#### Step 2: Open the Face Interface

**Using Chromium:**
```bash
chromium face.html
```

Once connected, you'll see:
```
Client connected! You can now send commands.

--- Available Commands ---
Moods: neutral, happy, sad, angry, surprised, love, dizzy, doubtful, wink, scared, disappointed, innocent, worried
Actions: audio on, audio off
Type 'exit' to quit.

Enter command:
```

#### Step 3: Send Commands

Type any of the following commands:

**Mood Commands:**
```bash
Enter command: happy
--> Sending command: 'happy'

Enter command: sad
--> Sending command: 'sad'

Enter command: angry
--> Sending command: 'angry'
```

**Audio Commands:**
```bash
Enter command: audio on
--> Audio streaming ENABLED.

Enter command: audio off
--> Audio streaming DISABLED. Sending reset signal.
```
---

### Mode 3: Kiosk Deployment (octopid.sh)

This mode allows you to launch the OctopID face and its corresponding Python server simultaneously in a dedicated kiosk environment on a specific monitor. This is ideal for multi-screen Linux setups.

#### Step 1: Detect Your Screen's Coordinates (Linux Only)

Open a terminal window and run 
```bash
xrandr
```
The output lists all connected monitors. You are looking for the coordinate numbers after the + sign.

Example Output:
```bash
DP-2 connected 1280x768+1080+0
```
##### Interpretation
- Screen name: DP-2
- Resolution: 1280x768
- Coordinates: X=1080, Y=0

##### Action: Find the line for your target monitor and write down its X and Y coordinates.

#### Step 2: Configure the octopid.sh Script

Open the octopid.sh file and edit the configuration variables at the top.

##### Example configuration
```bash
# Path to Python script
PYTHON_SCRIPT="/path/to/audioServer.py"

# Screen coordinates
SCREEN_X=1080
SCREEN_Y=0

# Delay before launching browser (optional)
STARTUP_DELAY=5
```

Note on Python Script: Set PYTHON_SCRIPT to either the absolute path of audioServer.py (for audio-reactive mode) or terminalInput.py (for interactive control).

#### Step 3: Run the Kiosk Script

First, ensure the script is executable:
```bash
chmod +x octopid.sh
```
Then, execute the script from your terminal:
```bash
./octopid.sh
```
The script will first execute the Python server, wait for the optional STARTUP_DELAY (default is 5 seconds), and then launch the Chromium browser on the specified screen in kiosk mode. The terminal will wait until the browser window is closed, and then the script will exit.

---

## WebSocket API Reference

All communication between clients and the server uses JSON messages over WebSocket.

### Server Address

```
ws://localhost:8760
```

### Message Format

All messages are JSON objects with a `type` field that determines the action.

---

### Client → Server Messages

#### **1. Change Mood**

```json
{
    "type": "mood",
    "mood": "happy"
}
```

**Parameters:**
- `type` (string): Must be `"mood"`
- `mood` (string): One of the available moods listed above

**Example (Python):**
```python
import asyncio
import websockets
import json

async def send_mood():
    async with websockets.connect("ws://localhost:8760") as ws:
        await ws.send(json.dumps({"type": "mood", "mood": "happy"}))

asyncio.run(send_mood())
```

---

#### **2. Enable Audio Streaming**

```json
{
    "type": "audio",
    "command": "on"
}
```

**Parameters:**
- `type` (string): Must be `"audio"`
- `command` (string): `"on"` to enable, `"off"` to disable

**Example (Python):**
```python
async def enable_audio():
    async with websockets.connect("ws://localhost:8760") as ws:
        await ws.send(json.dumps({"type": "audio", "command": "on"}))
```

---

#### **3. Disable Audio Streaming**

```json
{
    "type": "audio",
    "command": "off"
}
```

---

### Server → Client Messages

#### **1. Mood Update**

```json
{
    "type": "mood",
    "mood": "happy"
}
```

Sent to all connected clients when any client changes the mood.


Sent continuously (~100 times per second) when audio streaming is enabled.

---

## Configuration

All configuration is done through CSS variables and JavaScript constants within the HTML file.

### Visual Customization

#### **Global Appearance (CSS Variables)**

Open `face.html` and locate the `:root` section in the `<style>` block:

```css
:root {
    --face-color: #40D4D6;        /* Primary face/eye color (cyan) */
    --background-color: black;    /* Page background - change to white for light mode */
    --text-color: #f0f0f0;        /* Status text color */
}
```

**Example: Light Mode Theme**
```css
:root {
    --face-color: #2C3E50;
    --background-color: #ECF0F1;
    --text-color: #2C3E50;
}
```

#### **Animation Speeds**

Find these sections in the `<script>` block:

```javascript
// Eye panning interval (how often eyes look around)
setInterval(panEyes, Math.random() * 4000 + 3000); // 3-7 seconds

// Blinking interval (how often eyes blink)
setInterval(blink, Math.random() * 5000 + 2000);   // 2-7 seconds

// Blink duration (how long eyes stay closed)
setTimeout(() => { /* reopen eyes */ }, 150); // 150ms closed
```

**Make eyes more active:**
```javascript
setInterval(panEyes, Math.random() * 2000 + 1000); // 1-3 seconds
setInterval(blink, Math.random() * 3000 + 1000);   // 1-4 seconds
```

---

### Audio Configuration

The audio system is optimized for **Spanish language speech patterns** with specific frequency range tuning.

#### **Frequency Ranges (audioServer.py / terminalInput.py)**

Spanish speech emphasizes mid-range frequencies where most vowels and consonants occur:

```python
# Frequency ranges for analysis
bassRangeStart = 60      # Low frequencies (body, warmth)
bassRangeEnd = 250

midRangeStart = 251      # Core human voice range (MOST IMPORTANT FOR SPANISH)
midRangeEnd = 2000       # Spanish vowels (a, e, i, o, u) are strongest here

highRangeStart = 2001    # Sibilants and consonants (s, t, c)
highRangeEnd = 6000
```

**Why these ranges matter for Spanish:**
- **Spanish vowels** (a, e, i, o, u) have strong energy in 250-800 Hz
- **Consonants** like "r", "l", "n" are in 500-1500 Hz
- **Sibilants** (s, c, z) are in 2000-6000 Hz

**For English optimization**, adjust to:
```python
midRangeStart = 300
midRangeEnd = 3000  # English has more high-frequency content
```

#### **Sensitivity Tuning**

Control how reactive the mouth is to audio:

```python
# Normalize to 0-1 scale (divisors control sensitivity)
normalizedBass = min(bassEnergy / 30.0, 1.0)   # Lower = more sensitive
```

**Make mouth more reactive:**
```python
normalizedBass = min(bassEnergy / 20.0, 1.0)  # From 30 to 20
```

**Make mouth less reactive (for loud environments):**
```python
normalizedBass = min(bassEnergy / 50.0, 1.0)
```

#### **Smoothing (Reduce Jitter)**

```python
# Store last 5 bass values for smoothing
bass_history = deque(maxlen=5)  # Increase for smoother, decrease for snappier
```

**More smoothing (maxlen=10):**
- Pros: No jitter, very stable mouth
- Cons: Slower response to audio changes

**Less smoothing (maxlen=2):**
- Pros: Instant response, energetic
- Cons: May appear jittery

#### **Mouth Animation Speed (face.html)**

```javascript
const animateMouth = () => {
    const newPoints = currentPoints.map((point, i) => 
        point + (targetPoints[i] - point) * 0.3  // Interpolation factor
    );
    // ...
};
```

**Interpolation factor effects:**
- `0.1` = Very smooth, slow following (dreamy effect)
- `0.3` = Balanced (default, works well for Spanish)
- `0.5` = Snappy, responsive (good for music)
- `1.0` = Instant (no interpolation, can be jittery)

---

### Expression Customization

Each expression is defined in the `moods` object in `face.html`.

#### **Expression Structure**

```javascript
expressionName: {
    color: '#HEXCODE',           // Face color (hex format)
    mouthPath: 'SVG path data',  // Mouth shape (see SVG tutorial below)
    leftEyePath: 'SVG path data', // Left eye shape
    rightEyePath: 'SVG path data', // Right eye shape
}
```

#### **Available Moods**

```javascript
const AVAILABLE_MOODS = [
    'neutral', 'happy', 'sad', 'angry', 'surprised', 'love', 'dizzy',
    'doubtful', 'wink', 'scared', 'disappointed', 'innocent', 'worried'
];
```

#### **Creating a New Expression**

**Example: Adding a "sleepy_smiling" expression**

1. Add to the `moods` object in `face.html`:
```javascript
sleepy_smiling: {
    color: '#FFB84D',  // Warm orange
    mouthPath: 'M 60 130 Q 100 140 140 130',  // Gentle smile
    leftEyePath: 'M 5,100 A 15,20 0 0,1 35,100',  // Half-closed curved eye
    rightEyePath: 'M 165,100 A 15,20 0 0,1 195,100',
}
```

2. Add to `AVAILABLE_MOODS` in Python files:
```python
AVAILABLE_MOODS = (
    'neutral', 'happy', 'sad', 'angry', 'surprised', 'love', 'dizzy',
    'doubtful', 'wink', 'scared', 'disappointed', 'innocent', 'worried',
    'sleepy_smiling'  # Add your new mood here
)
```

#### **Color Psychology Guide**

- **Red (#E74C3C)** - Anger, danger, intensity, passion
- **Blue (#3498DB)** - Calm, trust, sadness, cold
- **Green (#6AF2A0)** - Happiness, nature, health, growth
- **Yellow (#F1C40F)** - Attention, surprise, energy, warning
- **Purple (#9B59B6)** - Mystery, confusion, luxury, magic
- **Orange (#FFB84D)** - Playfulness, warmth, creativity
- **Pink (#E87AF2)** - Love, affection, sweetness, romance
- **Gray (#95A5A6)** - Neutrality, fatigue, boredom, age
- **Cyan (#40D4D6)** - Technology, clarity, communication, calm

---

## Audio Server Deep Dive

### How It Works

The audio server creates a WebSocket server that performs real-time audio analysis and streams frequency data to connected clients. Here's the complete pipeline:

```
System Audio → Audio Capture → FFT Analysis → Frequency Band Extraction → 
Normalization → Smoothing → WebSocket Stream → Frontend Animation
```

#### Architecture Overview

```python
# 1. WebSocket Server Setup
async def mainAsync():
    # Creates server on localhost:8760
    async with websockets.serve(client_handler, "localhost", 8760):
        await asyncio.Future()  # Run forever

# 2. Client Connection Handler
async def client_handler(websocket):
    # Each client gets added to ACTIVE_CLIENTS set
    # Processes incoming commands (mood changes, audio on/off)

# 3. Audio Processing Loop
async def process_audio():
    # Runs continuously in background
    # Captures audio → Analyzes → Broadcasts to all clients
```

#### Data Flow Diagram

```
┌─────────────────────┐
│   System Audio      │ (Music, TTS, Video, etc.)
│   (Speakers/        │
│    Headphones)      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Audio Loopback     │ soundcard library captures output
│  (Virtual Cable)    │ 44100 Hz, mono, 1024 samples/chunk
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   FFT Analysis      │ numpy.fft.rfft()
│   (Time → Freq)     │ Converts waveform to frequency spectrum
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Frequency Bands     │ Extract energy in bass range:
│ 60-250 Hz (bass)    │ - Bass: body, warmth, vowel fundamentals
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Normalization      │ Scale to 0.0-1.0 range
│  (0.0 → 1.0)        │ bassEnergy / 30.0 → normalized bass
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Smoothing Filter   │ Moving average (last 5 bass values)
│  (Reduce Jitter)    │ Prevents mouth from shaking
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  JSON Encoding      │ {"type": "audio", "bass": 0.7}
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  WebSocket Broadcast│ Streams to all clients @ ~100fps
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Frontend (JS)      │ Interpolates mouth position
│  face.html          │ Animates SVG path @ 60fps
└─────────────────────┘
```

---

### FFT Analysis Explained

**Fast Fourier Transform (FFT)** converts audio from the time domain (amplitude over time) to the frequency domain (energy at each frequency).

#### Why FFT?

```python
# Time domain: raw audio samples (hard to interpret)
audio_samples = [0.1, -0.2, 0.3, -0.1, 0.4, ...]  # What do these mean?

# Frequency domain: energy at each frequency (actionable data!)
frequencies = [60Hz: 0.8, 250Hz: 0.5, 1000Hz: 0.9, ...]  # Clear patterns!
```

#### Code Walkthrough

```python
# Capture 1024 audio samples (mono channel)
data = mic.record(numframes=1024)  # Shape: (1024, 1) array

# Perform FFT on the first (and only) channel
fftData = np.fft.rfft(data[:, 0])
# rfft = Real FFT (optimized for real-valued signals, no imaginary input)
# Output: complex numbers representing frequency amplitudes/phases

# Generate frequency labels for each FFT bin
fftFreq = np.fft.rfftfreq(len(data[:, 0]), 1.0 / sampleRate)
# Example output: [0, 43.07, 86.13, 129.20, ...]
# Each value is a frequency in Hz corresponding to an FFT bin
```

#### Example FFT Output

For a 1000 Hz sine wave at 44100 Hz sample rate:

```python
# Input: 1024 samples of pure 1000 Hz tone
# FFT Output (simplified):
fftFreq:  [0,    43,   86,  129, ..., 1000, 1043, ...]  # Hz
fftData:  [0.01, 0.02, 0.05, 0.1, ..., 0.95, 0.1,  ...]  # Magnitude

# Peak at 1000 Hz = strong presence of that frequency
```

---

### Frequency Band Configuration

#### Why These Specific Ranges?

Human speech occupies **80-8000 Hz**, but not evenly. For mouth animation, we focus on **bass frequencies (60-250 Hz)** which capture:

- Fundamental frequencies of vowels
- Body and warmth of voice
- Overall speech energy/volume

| Band | Range | Contains |
|------|-------|----------|
| **Bass** | 60-250 Hz | Fundamental frequencies, vocal warmth, vowel energy |

#### Band Extraction Code

```python
# Find which FFT bins fall into the bass frequency range
bassIndices = np.where((fftFreq >= 60) & (fftFreq <= 250))
# Returns: array of indices where condition is True

# Calculate average energy in that band
bassEnergy = np.mean(np.abs(fftData[bassIndices]))
# np.abs() gets magnitude (ignores phase)
# np.mean() averages across all bass frequencies
```

**Example:**
```python
# If fftFreq = [0, 50, 100, 150, 200, 250, 300, ...]
# And fftData = [0.1, 0.2, 0.5, 0.8, 0.6, 0.3, 0.1, ...]

bassIndices = [2, 3, 4, 5]  # Indices for 100, 150, 200, 250 Hz
bassEnergy = mean([0.5, 0.8, 0.6, 0.3]) = 0.55
```

---

### Normalization

Raw FFT magnitudes vary wildly. Normalization scales them to a consistent 0-1 range.

```python
normalizedBass = min(bassEnergy / 30.0, 1.0)
#                    └─────┬─────┘  └─┬─┘
#                      Scale down    Cap at 1.0
```

#### Divisor Tuning Guide

| Divisor | Effect | Use Case |
|---------|--------|----------|
| **10** | Very sensitive | Quiet speech, ASMR, soft music |
| **20** | Balanced | Normal conversation, podcasts |
| **30** | Less sensitive (default) | Music with bass, louder environments |
| **50** | Minimal | Clubs, concerts, yelling |

**Formula:**
```
Sensitivity = 1 / Divisor
Higher divisor = Less sensitive (mouth opens less for same volume)
```

---

### Smoothing Algorithm

Without smoothing, rapid FFT fluctuations cause jittery mouth movements.

```python
# Circular buffer: stores last N values, auto-discards oldest
bass_history = deque(maxlen=5)

# Each frame:
bass_history.append(normalizedBass)  # Add new value
smoothed_bass = np.mean(bass_history)  # Average all 5 values
```

#### Smoothing Comparison

| maxlen | Frames Averaged | Response Time | Jitter | Best For |
|--------|----------------|---------------|--------|----------|
| 2 | 2 | Instant | High | Music, rhythm games |
| 5 | 5 | Fast | Low | Speech (default) |
| 10 | 10 | Slow | None | Meditation, ambient |

**Visual Example:**
```
Raw data:     [0.1, 0.9, 0.2, 0.8, 0.3, 0.7, ...]  ← Jittery!
Smoothed (5): [0.1, 0.5, 0.4, 0.5, 0.46, 0.58, ...] ← Smooth!
```

---

### Complete Code Flow

```python
async def process_audio():
    bass_history = deque(maxlen=5)  # Smoothing buffer
    
    # Open audio capture from system speakers
    with sc.get_microphone(
        id=str(sc.default_speaker().name),
        include_loopback=True  # Capture output, not input
    ).recorder(samplerate=44100, channels=1) as mic:
        
        while True:
            if not is_audio_enabled:
                await asyncio.sleep(0.1)
                continue
                
            # 1. CAPTURE: Get 1024 audio samples (~23ms of audio)
            data = mic.record(numframes=1024)
            
            # 2. FFT: Convert time → frequency
            fftData = np.fft.rfft(data[:, 0])
            fftFreq = np.fft.rfftfreq(len(data[:, 0]), 1.0 / 44100)
            
            # 3. EXTRACT: Find energy in bass frequency band
            bassIndices = np.where((fftFreq >= 60) & (fftFreq <= 250))
            bassEnergy = np.mean(np.abs(fftData[bassIndices]))
            
            # 4. NORMALIZE: Scale to 0-1
            normalizedBass = min(bassEnergy / 30.0, 1.0)
            
            # 5. SMOOTH: Reduce jitter
            bass_history.append(normalizedBass)
            smoothed_bass = np.mean(bass_history)
            
            # 6. STREAM: Send to all clients
            payload = {"type": "audio", "bass": smoothed_bass}
            await broadcast(json.dumps(payload))
            await asyncio.sleep(0.01)  # ~100 updates/second
```

---

### Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| **Sample Rate** | 44100 Hz | CD quality, captures up to 22050 Hz (Nyquist) |
| **Chunk Size** | 1024 samples | ~23ms latency, good balance |
| **FFT Bins** | 513 | (1024/2 + 1 for real FFT) |
| **Update Rate** | ~100 Hz | 10ms sleep between chunks |
| **Latency** | ~33ms | Capture (23ms) + Processing (5ms) + Network (5ms) |
| **CPU Usage** | ~5-10% | Single core, NumPy-optimized |

#### Latency Breakdown

```
Audio Output → [23ms capture] → [5ms FFT] → [5ms network] → Frontend
Total: ~33ms (imperceptible to humans, <50ms threshold)
```

---

## SVG Shape Creation Tutorial

SVG (Scalable Vector Graphics) uses path commands to draw shapes. Here's how to create and modify them.

### **SVG Path Basics**

An SVG path is a string of commands that tell the browser how to draw a line:

```svg
<path d="M 10 10 L 90 90" stroke="red" fill="none" />
```

- `d` = "data" (the drawing instructions)
- `M` = Move to (starting point)
- `L` = Line to (draw straight line)
- `stroke` = line color
- `fill` = interior color

### **Essential Path Commands**

| Command | Name | Example | Description |
|---------|------|---------|-------------|
| **M x y** | Move to | `M 50 50` | Move pen to coordinates (50,50) without drawing |
| **L x y** | Line to | `L 100 100` | Draw straight line to (100,100) |
| **A rx ry rot large sweep x y** | Arc | `A 20 30 0 0 1 100 50` | Draw curved arc |
| **Q cx cy x y** | Quadratic curve | `Q 75 25 100 50` | Draw smooth curve using control point |
| **C x1 y1 x2 y2 x y** | Cubic curve | `C 50 0 100 0 100 50` | Draw complex curve with 2 control points |
| **Z** | Close path | `Z` | Draw line back to starting point |

### **Coordinate System**

In face.html, the viewBox is `"0 0 200 200"`:
- X axis: 0 (left) to 200 (right)
- Y axis: 0 (top) to 200 (bottom)
- Center: (100, 100)

### **Creating Custom Mouth Shapes**

#### **Simple Straight Line (Neutral)**
```javascript
mouthPath: 'M 60 130 L 140 130'
// Move to (60,130), draw line to (140,130)
// Result: ______
```

#### **Smile (Quadratic Curve)**
```javascript
mouthPath: 'M 60 130 Q 100 150 140 130'
// Move to (60,130), curve through control point (100,150), end at (140,130)
// Result:  \_____/
```

#### **Frown (Inverted Curve)**
```javascript
mouthPath: 'M 60 140 Q 100 120 140 140'
// Control point ABOVE endpoints creates frown
// Result:  /‾‾‾‾‾\
```

#### **Open Mouth (Filled Arc)**
```javascript
mouthPath: 'M 60 130 A 40 20 0 0 0 140 130 Z'
// A = Arc command
// 40 = horizontal radius, 20 = vertical radius
// 0 0 0 = rotation, large-arc flag, sweep flag
// 140 130 = end point, Z = close path
// Result: Filled oval shape
```

#### **Wavy Mouth (Multiple Curves)**
```javascript
mouthPath: 'M 60 135 Q 80 125, 100 135 T 140 135'
// T = smooth curve continuation
// Result: ~~~~~
```

### **Creating Custom Eye Shapes**

#### **Normal Open Eye**
```javascript
leftEyePath: 'M 5,110 L 5,80 A 15,30 0 0,1 35,80 L 35,110 Z'
// Draw left side (5,110 to 5,80)
// Arc across top (radius 15x30)
// Draw right side (35,80 to 35,110)
// Close path
// Result: Rounded vertical oval
```

#### **Closed Eye (Horizontal Line)**
```javascript
leftEyePath: 'M 5,95 A 15,5 0 0,1 35,95'
// Short arc (small vertical radius = 5)
// Result: ———
```

#### **Heart-Shaped Eye**
```javascript
leftEyePath: 'M 10,130 C -20,85 -20,20 10,60 C 40,20 40,85 10,130 Z'
// Two cubic curves forming heart
// C = Cubic Bézier (two control points)
// Result: ♥
```

#### **Spiral Eye (Dizzy)**
```javascript
leftEyePath: 'M 20,95 m -18,0 a18,18 0 1,1 36,0 a12,12 0 1,1 -24,0 a6,6 0 1,1 12,0'
// Multiple circular arcs getting smaller
// m = relative move, a = relative arc
// Result: @
```

### **SVG Path Tool**

For complex shapes, use an online editor:
1. Visit [yqnn.github.io/svg-path-editor](https://yqnn.github.io/svg-path-editor/)
2. Draw your shape visually
3. Copy the generated path data
4. Paste into your expression definition

### **Testing Your Shapes**

Create a test SVG to preview:
```html
<svg viewBox="0 0 200 200" style="border: 1px solid black;">
    <path d="YOUR PATH HERE" fill="cyan" stroke="black" />
</svg>
```

---

## Project Structure

```
OctopID/
├── face.html           # Main frontend interface (HTML + CSS + JavaScript)
│                       # - SVG face rendering (fullscreen)
│                       # - Expression definitions (13 moods)
│                       # - Eye animation logic (panning, blinking)
│                       # - WebSocket client for audio sync
│                       # - Mouth interpolation algorithm
│                       # - Always-listening mode (auto-connects)
│
├── audioServer.py      # Backend WebSocket server for audio capture
│                       # - Audio loopback capture (soundcard)
│                       # - FFT frequency analysis (NumPy)
│                       # - Bass frequency band extraction (60-250 Hz)
│                       # - Normalization and smoothing
│                       # - Real-time WebSocket broadcasting
│                       # - Multi-client support
│                       # - Command processing (mood/audio control)
│
├── terminalInput.py    # Interactive terminal control server
│                       # - All features of audioServer.py
│                       # - Plus: terminal command interface
│                       # - Type mood names to change expression
│                       # - Type "audio on/off" to control streaming
│                       # - Standalone (no need for audioServer.py)
│
├── demo.py             # Automated demonstration script
│                       # - Connects to audioServer.py
│                       # - Cycles through all features
│                       # - Shows how to use WebSocket API
│                       # - Perfect for learning JSON message format
│
└── README.md           # Complete documentation (this file)
```

### File Responsibilities

#### face.html (Frontend - 300+ lines)
- **SVG Rendering:** 200x200 viewBox, 2 eyes, 1 mouth, fullscreen display
- **Expression System:** 13 pre-defined emotion states
- **Animation Engine:**
  - Eye panning: Random translation every 3-7 seconds
  - Blinking: Scale eyes to 0.1 height every 2-7 seconds
  - Mouth interpolation: 60fps smooth transitions
- **WebSocket Client:** Auto-connects to `ws://localhost:8760`
- **Audio Response:** Maps bass energy (0-1) to mouth openness (0-40px)
- **Always Listening:** No manual controls, responds to server commands

#### audioServer.py (Backend - 130 lines)
- **WebSocket Server:** Async server on port 8760
- **Multi-Client Support:** Broadcasts to all connected clients
- **Audio Capture:** System audio loopback (44100 Hz, mono)
- **FFT Analysis:** 1024-sample chunks, 513 frequency bins
- **Band Extraction:** Bass: 60-250 Hz
- **Smoothing:** 5-frame moving average for bass
- **Streaming:** JSON payloads @ ~100 Hz
- **Command Processing:** Receives mood and audio control commands

#### terminalInput.py (Interactive Server - 200+ lines)
- **All features of audioServer.py**
- **Terminal Interface:** Type commands directly
- **Connection Status:** Visual loader while waiting for client
- **Command Validation:** Only accepts valid mood names
- **Help Menu:** Lists all available commands
- **Graceful Exit:** Type "exit" to quit

#### demo.py (Demo Script - 80 lines)
- **WebSocket Client:** Connects to audioServer.py
- **Automated Sequence:** Tests all features in order
- **API Examples:** Shows proper JSON message format
- **Learning Tool:** Copy code patterns for your own scripts
- **Documented:** Clear comments explain each step

---

## Troubleshooting

### **Face Not Displaying**

- **Check Browser Compatibility:**
  - Use Chromium-based browsers (Chrome, Edge, Brave)
  - Avoid Firefox or Safari for best WebSocket stability

- **Check Browser Console (F12)** for JavaScript errors

- **Verify file location:**
  ```bash
  # Must open face.html in same directory as Python files
  ls face.html audioServer.py  # Should list both files
  ```

---

### **Audio Not Working**

**Error: "Connection Error" or face not responding**

1. **Verify both server and browser are running:**
   ```bash
   # Terminal 1: Check if server is running
   python3 audioServer.py
   # Should show: "Starting WebSocket server on ws://localhost:8760"
   
   # Terminal 2 or Browser: Open face.html in Chromium
   chromium face.html
   ```

2. **Check WebSocket connection in browser:**
   - Open Developer Tools (F12)
   - Go to Console tab
   - Should see: "Successfully connected to the WebSocket server"
   - If not, check Network tab → WS → verify connection to localhost:8760

3. **Verify port is not in use:**
   ```bash
   lsof -i:8760
   ```

**Mouth Not Moving Despite Audio Playing**

- **Check audio device capture:**
  ```python
  # In Python console, list available devices:
  import soundcard as sc
  speakers = sc.all_speakers()
  for speaker in speakers:
      print(speaker.name)
  ```

- **Update the capture device in audioServer.py or terminalInput.py:**
  ```python
  with sc.get_microphone(
      id=str(sc.default_speaker().name),  # Change to your device name
      include_loopback=True
  ).recorder(samplerate=sampleRate, channels=1) as mic:
  ```

**Linux Audio Capture**
```bash
# List audio sources
pactl list short sources

# Use a monitor source (system audio loopback)
# Example: alsa_output.pci-0000_00_1f.3.analog-stereo.monitor
```

---

### **Mouth Too Sensitive or Not Sensitive Enough**

**Adjust normalization divisors** in `audioServer.py` or `terminalInput.py`:
```python
# Less sensitive (for loud environments)
normalizedBass = min(bassEnergy / 40.0, 1.0)  # Increase divisor

# More sensitive (for quiet speech)
normalizedBass = min(bassEnergy / 15.0, 1.0)  # Decrease divisor
```

**Adjust interpolation** in `face.html`:
```javascript
// Snappier response
point + (targetPoints[i] - point) * 0.5  // From 0.3 to 0.5

// Smoother, calmer
point + (targetPoints[i] - point) * 0.1  // From 0.3 to 0.1
```

---

### **Mouth Opens But Stays Open (Doesn't Close)**

**Check talking threshold** in `face.html`:
```javascript
const talkingThreshold = 0.1;  // Lower = more sensitive to quiet sounds
// Try 0.15 or 0.2 for better silence detection
```

**Verify normalization** - mouth should close when bass < threshold:
```python
# audioServer.py - add debug prints
print(f"Bass: {smoothed_bass:.2f}")
# Should see values near 0.0 during silence
```

---

### **Server Won't Start**

**Error: "No module named 'soundcard'"**
```bash
pip install soundcard numpy websockets
```

**Error: "Address already in use"**
```bash
# Kill existing process on port 8760
lsof -ti:8760 | xargs kill -9
```

**Error: "No speakers found"**
```python
# List available audio devices
import soundcard as sc
print("Speakers:", [s.name for s in sc.all_speakers()])
print("Microphones:", [m.name for m in sc.all_microphones()])

# Update Python file with correct device name
```

---

### **WebSocket Connection Fails**

**Error: "Connection refused"**
- Ensure server is running: `python3 audioServer.py`
- Check server address in `face.html` matches: `ws://localhost:8760`
- Try `ws://127.0.0.1:8760` if localhost doesn't resolve

**Error: "Mixed content" (HTTPS page)**
- Can't use `ws://` from `https://` pages
- Either:
  - Use `wss://` (requires SSL certificate)
  - Serve page via `http://` instead
  - Open file directly (file:// protocol)

---

### **Demo Script Issues**

**Error: "Connection to ws://localhost:8760 refused"**
- Make sure `audioServer.py` is running FIRST
- Then run `demo.py` in a separate terminal
- The demo script needs an active server to connect to

**Demo runs but face doesn't change**
- Verify `face.html` is open in Chromium
- Check browser console for connection messages
- Ensure all three components are running:
  1. audioServer.py (terminal 1)
  2. face.html (browser)
  3. demo.py (terminal 2)

---

### **Terminal Input Issues**

**Commands not working**
- Check spelling: commands are case-sensitive (lowercase only)
- Valid moods: `neutral`, `happy`, `sad`, `angry`, `surprised`, `love`, `dizzy`, `doubtful`, `wink`, `scared`, `disappointed`, `innocent`, `worried`
- Valid audio commands: `audio on`, `audio off`

**"Waiting for client connection..." stuck**
- Open `face.html` in Chromium browser
- The terminal will detect the connection automatically
- If stuck, restart `terminalInput.py` and refresh browser

---

### **Performance Issues**

- **Reduce animation frame rate:**
  ```javascript
  setTimeout(() => {
      audioAnimationId = requestAnimationFrame(animateMouth);
  }, 33);  // ~30fps instead of 60fps
  ```

- **Simplify eye paths** (use fewer curves)

- **Increase WebSocket sleep** in Python files:
  ```python
  await asyncio.sleep(0.02)  # 50 Hz instead of 100 Hz
  ```

---

### **Audio Debugging Checklist**

1. **Server Status:**
   ```bash
   python3 audioServer.py
   # Should print: "Starting WebSocket server on ws://localhost:8760"
   # Should print: "Waiting for client connections..."
   # No error messages
   ```

2. **Client Connection:**
   - Open Chromium (not Firefox/Safari)
   - Open `face.html`
   - Open browser console (F12)
   - Should see: "Successfully connected to the WebSocket server"
   - Check Network tab → WS → should show active connection

3. **Audio Flow:**
   ```python
   # Add debug prints in audioServer.py
   print(f"Captured: {data.shape}, Energy: {bassEnergy:.2f}")
   # Should print continuously while audio plays
   ```

4. **Mouth Movement:**
   ```javascript
   // Add in face.html animateMouth()
   console.log('Bass:', audioData.bass);
   // Should show changing values during audio
   ```

---

## Credits

**Made with care for Octopy® by TheBIGduke - Kaléin Tamaríz, October 2025**

---