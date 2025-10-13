window.addEventListener('DOMContentLoaded', () => {
    const mouth = document.getElementById('mouth');
    const eyes = document.querySelectorAll('.eye');
    const statusDiv = document.getElementById('status');
    const serverAddress = 'ws://localhost:1940';

    const restingMouthPath = 'M 60 130 Q 100 135 140 130';

    // --- Blinking Animation ---
    const blink = () => {
        eyes.forEach(eye => {
            eye.setAttribute('ry', '1');
        });
        setTimeout(() => {
            eyes.forEach(eye => {
                eye.setAttribute('ry', '15');
            });
        }, 150);
    };
    setInterval(blink, 4000);

    const websocket = new WebSocket(serverAddress);

    websocket.onopen = () => {
        console.log('Successfully connected to the WebSocket server');
        statusDiv.textContent = 'Connected! Play some audio';
    };

    websocket.onmessage = (event) => {
        const audioData = JSON.parse(event.data);
        const bassLevel = audioData.bass;
        const talkingThreshold = 0.1;

        if (bassLevel > talkingThreshold) {
            // This is the proven, working animation logic
            const maxRy = 25;
            const maxRx = 45;
            const ry = bassLevel * maxRy;
            const rx = 40 + (bassLevel * (maxRx - 40));

            const newPath = `M ${100-rx},130 A ${rx},${ry} 0 1,1 ${100+rx},130 A ${rx},${ry} 0 1,1 ${100-rx},130 Z`;
            mouth.setAttribute('d', newPath);
        } else {
            // Return to the resting semi-happy face
            mouth.setAttribute('d', restingMouthPath);
        }
    };

    websocket.onclose = () => {
        console.log('Disconnected from the WebSocket server');
        statusDiv.textContent = 'Disconnected, please restart the Python server';
    };

    websocket.onerror = (error) => {
        console.error('Websocket error:', error);
        statusDiv.textContent = 'Connection Error, check the connectivity of the Python server';
    };
});