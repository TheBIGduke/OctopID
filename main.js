// --- DOM Element References ---
const mouth = document.getElementById('mouth');
const leftEye = document.querySelector('#left-eye .eye-background');
const rightEye = document.querySelector('#right-eye .eye-background');
const leftEyeIcon = document.querySelector('#left-eye .eye-icon-container');
const rightEyeIcon = document.querySelector('#right-eye .eye-icon-container');
const statusDiv = document.getElementById('status');
const root = document.documentElement;

// --- State Management ---
let currentExpression = 'neutral';
let webSocket;
let audioListeningInterval;
let restingMouthPath = 'M 60 130 L 140 130'; // Default resting mouth

// --- Expression Definitions ---
// A collection of face configurations for different moods.
const expressions = {
    neutral: {
        color: '#40D4D6',
        mouthPath: 'M 60 130 L 140 130',
        leftEyePath: 'M 5,110 L 5,80 A 15,30 0 0,1 35,80 L 35,110 Z',
        rightEyePath: 'M 165,110 L 165,80 A 15,30 0 0,1 195,80 L 195,110 Z',
        icon: ''
    },
    happy: {
        color: '#6AF2A0',
        mouthPath: 'M 60 130 Q 100 150 140 130',
        leftEyePath: 'M 5,100 A 15,20 0 0,1 35,100', // Curved upper eyelid
        rightEyePath: 'M 165,100 A 15,20 0 0,1 195,100',
        icon: ''
    },
    sad: {
        color: '#5B8DEF',
        mouthPath: 'M 60 140 Q 100 120 140 140',
        leftEyePath: 'M 5,90 A 15,20 0 0,0 35,90', // Curved lower eyelid
        rightEyePath: 'M 165,90 A 15,20 0 0,0 195,90',
        icon: ''
    },
    angry: {
        color: '#E74C3C',
        mouthPath: 'M 60 140 L 140 140',
        // Angled paths to create a frown
        leftEyePath: 'M 5,80 L 35,95 L 35,110 L 5,110 Z',
        rightEyePath: 'M 165,95 L 195,80 L 195,110 L 165,110 Z',
        icon: ''
    },
    surprised: {
        color: '#F1C40F',
        mouthPath: 'M 90 130 A 10 15 0 1 0 110 130 A 10 15 0 1 0 90 130 Z', // O-shape mouth
        // Taller eye paths
        leftEyePath: 'M 5,115 L 5,75 A 15,35 0 0,1 35,75 L 35,115 Z',
        rightEyePath: 'M 165,115 L 165,75 A 15,35 0 0,1 195,75 L 195,115 Z',
        icon: ''
    },
    love: {
        color: '#E87AF2',
        mouthPath: 'M 60 130 Q 100 145 140 130',
        leftEyePath: 'M 5,110 L 5,80 A 15,30 0 0,1 35,80 L 35,110 Z',
        rightEyePath: 'M 165,110 L 165,80 A 15,30 0 0,1 195,80 L 195,110 Z',
        // SVG path for a heart shape
        icon: '<path d="M20,10 C10,0 0,10 0,15 C0,25 10,30 10,30 C10,30 20,25 20,15 C20,10 10,0 10,10 Z" transform="translate(7, 80)" fill="#E87AF2"/>'
    },
    dizzy: {
        color: '#9B59B6',
        mouthPath: 'M 60 135 Q 80 125, 100 135 T 140 135', // Wavy mouth
        leftEyePath: 'M 5,110 L 5,80 A 15,30 0 0,1 35,80 L 35,110 Z',
        rightEyePath: 'M 165,110 L 165,80 A 15,30 0 0,1 195,80 L 195,110 Z',
        // SVG path for a swirl
        icon: '<path d="M15,15 m-10,0 a10,10 0 1,0 20,0 a10,10 0 1,0 -20,0 M15,15 m-6,0 a6,6 0 1,0 12,0 a6,6 0 1,0 -12,0" transform="translate(5, 80)" stroke-width="2.5" stroke="#fff" fill="none"/>'
    },
    thinking: {
        color: '#3498DB',
        mouthPath: 'M 70 135 L 130 125', // Thoughtful slant
        // Shifted pupils to look sideways
        leftEyePath: 'M 15,110 L 15,80 A 15,30 0 0,1 45,80 L 45,110 Z',
        rightEyePath: 'M 175,110 L 175,80 A 15,30 0 0,1 205,80 L 205,110 Z',
        icon: ''
    },
    sleepy: {
        color: '#95A5A6',
        mouthPath: 'M 95 135 A 5 5 0 1 0 105 135 A 5 5 0 1 0 95 135 Z', // Small 'o' mouth
        // Half-closed eyes
        leftEyePath: 'M 5,110 A 15,30 0 0,1 35,110',
        rightEyePath: 'M 165,110 A 15,30 0 0,1 195,110',
        icon: ''
    },
     listening: { // Keep for the button functionality
        color: '#40D4D6'
    }
};

// --- Core Function to Change Expression ---
function setExpression(name) {
    if (name === 'listening') {
        // 'Listen' button now just ensures the connection is active
        if (!webSocket || webSocket.readyState !== WebSocket.OPEN) {
            connectWebSocket();
        }
        return;
    }

    currentExpression = name;
    const expr = expressions[name];

    if (!expr) return;

    // Update CSS variable for color and apply to SVG elements
    root.style.setProperty('--face-color', expr.color);
    mouth.setAttribute('stroke', 'var(--face-color)');
    leftEye.setAttribute('fill', 'var(--face-color)');
    rightEye.setAttribute('fill', 'var(--face-color)');

    // Update resting mouth path
    restingMouthPath = expr.mouthPath;

    // Update SVG paths
    leftEye.setAttribute('d', expr.leftEyePath);
    rightEye.setAttribute('d', expr.rightEyePath);

    // Update icons inside eyes
    if (expr.icon) {
        leftEyeIcon.innerHTML = expr.icon;
        rightEyeIcon.innerHTML = expr.icon;
        // Adjust icon color to match expression
        leftEyeIcon.querySelectorAll('path').forEach(p => {
            if (p.getAttribute('fill') !== 'none') {
                p.setAttribute('fill', expr.color)
            }
        });
        rightEyeIcon.querySelectorAll('path').forEach(p => {
                if (p.getAttribute('fill') !== 'none') {
                    p.setAttribute('fill', expr.color)
                }
        });
    } else {
        leftEyeIcon.innerHTML = '';
        rightEyeIcon.innerHTML = '';
    }
    statusDiv.textContent = `Current mood: ${name}`;
}

// --- WebSocket Logic for Reactive Mouth ---
function connectWebSocket() {
    const serverAddress = 'ws://localhost:1940';
    webSocket = new WebSocket(serverAddress);

    webSocket.onopen = () => {
        console.log('Successfully connected to the WebSocket server');
        statusDiv.textContent = 'Connected! Play some audio...';

        let currentMouthOpenness = 0;
        let targetMouthOpenness = 0;
        const animationSmoothing = 0.2; // Lower is smoother

        webSocket.onmessage = (event) => {
            const audioData = JSON.parse(event.data);
            const bassLevel = audioData.bass;
            const talkingThreshold = 0.1;

            if (bassLevel > talkingThreshold) {
                targetMouthOpenness = bassLevel * 40;
                mouth.style.fill = 'var(--face-color)';
            } else {
                targetMouthOpenness = 0;
                mouth.style.fill = 'transparent';
            }
        };

        // Smoothed mouth animation loop
        const animateMouth = () => {
            currentMouthOpenness += (targetMouthOpenness - currentMouthOpenness) * animationSmoothing;

            if (currentMouthOpenness < 1) {
                mouth.setAttribute('d', restingMouthPath);
            } else {
                const newMouthPath = `M 60 130 A 40 ${currentMouthOpenness} 0 0 0 140 130 Z`;
                mouth.setAttribute('d', newMouthPath);
            }

            audioListeningInterval = requestAnimationFrame(animateMouth);
        };

        if (!audioListeningInterval) {
            audioListeningInterval = requestAnimationFrame(animateMouth);
        }
    };

    webSocket.onclose = () => {
        console.log('Disconnected from the WebSocket server');
        statusDiv.textContent = 'Disconnected. Restart Python server.';
        if (audioListeningInterval) {
            cancelAnimationFrame(audioListeningInterval);
            audioListeningInterval = null;
        }
        setExpression('neutral'); // Revert to neutral on disconnect
    };

    webSocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        statusDiv.textContent = 'Connection Error. Is the Python server running?';
        if (audioListeningInterval) {
            cancelAnimationFrame(audioListeningInterval);
            audioListeningInterval = null;
        }
        setExpression('neutral');
    };
}

// --- Initial Setup ---
window.addEventListener('DOMContentLoaded', () => {
    // Set the initial expression on page load
    setExpression('neutral');
    // Connect to the WebSocket server to enable reactive mouth from the start
    connectWebSocket();
});