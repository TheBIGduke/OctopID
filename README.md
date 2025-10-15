# OctopID - Animated Expression System

[![HTML5](https://img.shields.io/badge/HTML5-Ready-orange.svg)](https://developer.mozilla.org/en-US/docs/Web/Guide/HTML/HTML5)
[![SVG](https://img.shields.io/badge/SVG-Animated-brightgreen.svg)](https://developer.mozilla.org/en-US/docs/Web/SVG)
[![WebSocket](https://img.shields.io/badge/WebSocket-Enabled-blue.svg)](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
[![Python](https://img.shields.io/badge/Python-3.7+-yellow.svg)](https://www.python.org/)

OctopID is an expressive, animated face system built with **SVG** and **JavaScript**. It features 15 unique emotional expressions with smooth transitions, automatic eye movements (panning and blinking), and a special **audio-reactive "listening" mode** that synchronizes mouth movements with real-time audio input. Perfect for virtual assistants, chatbots, or interactive characters.

---

## Features

- **15 Unique Expressions** – From neutral to happy, sad, angry, surprised, and more exotic emotions like dizzy, sick, and innocent.
- **Real-time Audio Synchronization** – The "listening" mode captures system audio and animates the mouth to match speech patterns.
- **Smooth Animations** – CSS transitions create fluid movements between expressions and eye states.
- **Automatic Eye Behaviors** – Eyes blink naturally and pan randomly to simulate lifelike attention.
- **Fully Customizable** – Easily modify colors, shapes, speeds, and audio sensitivity through CSS variables and JavaScript parameters.
- **WebSocket Integration** – Connects to a Python audio server for live audio analysis and visualization.
- **Spanish Language Optimized** – Audio frequency ranges tuned for Spanish speech patterns (mid-range frequencies 251-2000 Hz).

---

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
  - [Visual Customization](#visual-customization)
  - [Audio Configuration](#audio-configuration)
  - [Expression Customization](#expression-customization)
- [Usage](#usage)
- [SVG Shape Creation Tutorial](#svg-shape-creation-tutorial)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## Requirements

### Hardware

- A computer with audio output (speakers/headphones) for "listening" mode.
- A microphone or system audio loopback for capturing audio.

### Software

- **Frontend (face.html):**
  - A modern web browser with SVG and WebSocket support (Chrome, Firefox, Edge, Safari).
  - A local web server (optional but recommended).

- **Backend (audioServer.py):**
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
pip install websockets soundcard numpy
```

### 3. Set Up Local Server (Optional)

For the best experience, serve `face.html` from a local web server:

**Using Python:**
```bash
python -m http.server 1940
```

**Using VS Code Live Server:**
Install the Live Server extension and click "Go Live" in the status bar.

### 4. Start the Audio Server

In a terminal, run:
```bash
python audioServer.py
```

You should see:
```
Starting WebSocket server on ws://localhost:1940
```

### 5. Open the Face Interface

Navigate to:
```
http://localhost:1940/face.html
```

Or simply open `face.html` directly in your browser if not using a server.

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
    --button-bg: #2c2c2c;         /* Button background color */
    --button-hover-bg: #3c3c3c;   /* Button hover state */
    --shadow-color: rgba(0, 0, 0, 0.2); /* Shadow effects */
}
```

**Example: Light Mode Theme**
```css
:root {
    --face-color: #2C3E50;
    --background-color: #ECF0F1;
    --text-color: #2C3E50;
    --button-bg: #BDC3C7;
    --button-hover-bg: #95A5A6;
    --shadow-color: rgba(0, 0, 0, 0.1);
}
```

#### **Spacing and Layout**

```css
.container {
    gap: 20px;  /* Space between face, buttons, and status (increase for more breathing room) */
}

.controls {
    gap: 10px;  /* Space between buttons (reduce for tighter layout) */
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

#### **Frequency Ranges (audioServer.py)**

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
normalizedMids = min(midEnergy / 20.0, 1.0)    # Tuned for Spanish voice
normalizedHighs = min(highEnergy / 35.0, 1.0)
```

**Make mouth more reactive:**
```python
normalizedBass = min(bassEnergy / 20.0, 1.0)  # From 30 to 20
normalizedMids = min(midEnergy / 15.0, 1.0)   # From 20 to 15
```

**Make mouth less reactive (for loud environments):**
```python
normalizedBass = min(bassEnergy / 50.0, 1.0)
normalizedMids = min(midEnergy / 40.0, 1.0)
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

Each expression is defined in the `expressions` object in `face.html`.

#### **Expression Structure**

```javascript
expressionName: {
    color: '#HEXCODE',           // Face color (hex format)
    mouthPath: 'SVG path data',  // Mouth shape (see SVG tutorial below)
    leftEyePath: 'SVG path data', // Left eye shape
    rightEyePath: 'SVG path data', // Right eye shape
    icon: '<svg>...</svg>'        // Optional: inner eye icon (pupils, etc.)
}
```

#### **Creating a New Expression**

**Example: Adding a "sleepy_smiling" expression**

```javascript
sleepy_smiling: {
    color: '#FFB84D',  // Warm orange
    mouthPath: 'M 60 130 Q 100 140 140 130',  // Gentle smile
    leftEyePath: 'M 5,100 A 15,20 0 0,1 35,100',  // Half-closed curved eye
    rightEyePath: 'M 165,100 A 15,20 0 0,1 195,100',
}
```

Add a button to trigger it:
```html
<button onclick="setExpression('sleepy_smiling')">Sleepy Smile</button>
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

## Usage

### **1. Manual Expression Control**

Click any button to change the expression:
- **Neutral** - Default calm state
- **Happy** - Positive, friendly
- **Sad** - Melancholic, down
- **Angry** - Aggressive, frustrated
- **Surprised** - Shocked, amazed
- **Love** - Affectionate (heart eyes!)
- **Dizzy** - Disoriented (spiral eyes)
- **Thinking** - Contemplative
- **Sleepy** - Tired, drowsy
- **Wink** - Playful, flirty
- **Scared** - Fearful, anxious
- **Confused** - Puzzled, uncertain
- **Sick** - Unwell, nauseous (X eyes)
- **Innocent** - Pure, naive
- **Worried** - Anxious, stressed

### **2. Audio-Reactive Mode**

1. Start the Python server: `python audioServer.py`
2. Click the **"Listen"** button
3. Play audio on your computer (music, TTS, video, etc.)
4. The mouth will animate in sync with the audio

**Note:** On Windows/macOS, you may need to configure a virtual audio cable to capture system audio. On Linux, use `pavucontrol` to redirect audio.

### **3. Programmatic Control**

**From Browser Console:**
```javascript
setExpression('happy');
setExpression('listening');
```

**From External JavaScript:**
```javascript
window.setExpression = (name) => {
    window.dispatchEvent(new CustomEvent('expressionChange', { 
        detail: { expression: name } 
    }));
};
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

In our face.html, the viewBox is `"0 0 200 200"`:
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
├── audioServer.py      # Backend WebSocket server for audio capture
└── README.md           # This file
```

---

## Troubleshooting

### **Face Not Displaying**

- **Check Browser Console (F12)** for JavaScript errors
- Ensure SVG viewBox is correct: `viewBox="0 0 200 200"`
- Verify all path data is properly quoted

### **Audio Not Working (Listening Mode)**

**Error: "Connection Error. Is the Python server running?"**
- Start the server: `python audioServer.py`
- Check server output for errors
- Verify WebSocket address: `ws://localhost:1940`

**Mouth Not Moving Despite Audio Playing**
- **Check audio device capture:**
  ```python
  # In audioServer.py, print available devices:
  speakers = sc.all_speakers()
  for speaker in speakers:
      print(speaker.name)
  ```
- Update the capture device:
  ```python
  with sc.get_microphone(
      id=str(sc.default_speaker().name),  # Change to your device name
      include_loopback=True
  ).recorder(samplerate=sampleRate, channels=1) as mic:
  ```

**Windows/macOS Audio Capture**
- Install virtual audio cable software:
  - Windows: [VB-CABLE](https://vb-audio.com/Cable/)
  - macOS: [BlackHole](https://github.com/ExistentialAudio/BlackHole)
- Set it as your default output device
- Update `audioServer.py` to capture from the virtual cable

**Linux Audio Capture**
```bash
# List audio sources
pactl list short sources

# Use a monitor source (system audio loopback)
# Example: alsa_output.pci-0000_00_1f.3.analog-stereo.monitor
```

### **Mouth Too Sensitive or Not Sensitive Enough**

**Adjust normalization divisors** in `audioServer.py`:
```python
# Less sensitive (for loud environments)
normalizedMids = min(midEnergy / 40.0, 1.0)  # Increase divisor

# More sensitive (for quiet speech)
normalizedMids = min(midEnergy / 10.0, 1.0)  # Decrease divisor
```

**Adjust interpolation** in `face.html`:
```javascript
// Snappier response
point + (targetPoints[i] - point) * 0.5  // From 0.3 to 0.5

// Smoother, calmer
point + (targetPoints[i] - point) * 0.1  // From 0.3 to 0.1
```

### **Eyes Blinking During Wide-Eyed Expressions**

Check the `isWideEyed` flag in `setExpression()`:
```javascript
isWideEyed = (name === 'surprised' || name === 'scared');
```

### **Poor Performance**

- **Reduce animation frame rate:**
  ```javascript
  setTimeout(() => {
      audioAnimationId = requestAnimationFrame(animateMouth);
  }, 33);  // ~30fps instead of 60fps
  ```

- **Simplify eye paths** (use fewer curves)
- **Disable panning/blinking** temporarily to test

---

## Contributing

Contributions are welcome! Here are some ideas:

- **New Expressions** - Add more emotions (confused, bored, excited)
- **Lip Sync Modes** - Different mouth animations for singing vs speaking
- **Eye Tracking** - Make eyes follow mouse cursor
- **Expression Sequences** - Chain expressions for storytelling
- **Voice Activity Detection** - Auto-detect speech vs silence
- **Multi-language Optimization** - Frequency tuning for other languages

### **How to Contribute**

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-expression`
3. Make your changes
4. Test thoroughly (all expressions + audio mode)
5. Commit: `git commit -m 'Add excited expression'`
6. Push: `git push origin feature/new-expression`
7. Open a Pull Request

---

**Made for the creative community**