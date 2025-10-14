window.addEventListener('DOMContentLoaded', () => {
    const face = document.getElementById('face');
    const mouth = document.getElementById('mouth');
    const eyes = document.querySelectorAll('.eye');
    const statusDiv = document.getElementById('status');
    const serverAddress = 'ws://localhost:1940';

    const restingMouthPath = 'M 60 130 L 140 130';
    let targetMouthPath = restingMouthPath;
    let currentMouthPath = restingMouthPath;
    let isWideEyed = false;

    // --- Blinking Animation ---
    const blink = () => {
        eyes.forEach(eye => {
            eye.style.transform = 'scaleY(0.1)';
        });
        setTimeout(() => {
            if (!isWideEyed) {
                eyes.forEach(eye => {
                    eye.style.transform = 'scaleY(1)';
                });
            }
        }, 150);
    };
    setInterval(blink, Math.random() * 5000 + 2000);

    // --- Eye Panning Animation ---
    const panEyes = () => {
        const panX = Math.random() * 10 - 5;
        const panY = Math.random() * 6 - 3;
        eyes.forEach(eye => {
            eye.style.transform = `translate(${panX}px, ${panY}px)`;
        });
    };
    setInterval(panEyes, Math.random() * 4000 + 3000);

    const websocket = new WebSocket(serverAddress);

    websocket.onopen = () => {
        console.log('Successfully connected to the WebSocket server');
        statusDiv.textContent = 'Connected! Play some audio';
    };

    websocket.onmessage = (event) => {
        const audioData = JSON.parse(event.data);
        const bassLevel = audioData.bass;
        const talkingThreshold = 0.1;

        // --- Mouth talking animation ---
        if (bassLevel > talkingThreshold) {
            const mouthOpenness = bassLevel * 40;
            // Add 'Z' to the end of the path to close the shape
            targetMouthPath = `M 60 130 A 40 ${mouthOpenness} 0 0 0 140 130 Z`;
            mouth.style.fill = '#40D4D6';

        } else {
            targetMouthPath = restingMouthPath;
            mouth.style.fill = 'transparent';
        }
    };

    // --- Smoothed Mouth Animation ---
    const animateMouth = () => {
        const currentPoints = (currentMouthPath.match(/[-+]?[0-9]*\.?[0-9]+/g) || []).map(Number);
        const targetPoints = (targetMouthPath.match(/[-+]?[0-9]*\.?[0-9]+/g) || []).map(Number);
        let newPath;
        if (currentPoints.length !== targetPoints.length) {
            newPath = targetMouthPath;
        } else {
            const newPoints = [];
            for (let i = 0; i < currentPoints.length; i++) {
                newPoints.push(currentPoints[i] + (targetPoints[i] - currentPoints[i]) * 0.3);
            }
            if (newPoints.length === 4) { // Straight line for resting
                newPath = `M ${newPoints[0]} ${newPoints[1]} L ${newPoints[2]} ${newPoints[3]}`;
            } else if (newPoints.length === 9) { // Arc for talking
                 // Reconstruct the arc path and ensure it's closed with 'Z'
                 newPath = `M ${newPoints[0]} ${newPoints[1]} A ${newPoints[2]} ${newPoints[3]} ${newPoints[4]} ${newPoints[5]} ${newPoints[6]} ${newPoints[7]} ${newPoints[8]} Z`;
            } else {
                newPath = targetMouthPath;
            }
        }
        currentMouthPath = newPath;
        mouth.setAttribute('d', newPath);
        requestAnimationFrame(animateMouth);
    };
    animateMouth();

    websocket.onclose = () => {
        console.log('Disconnected from the WebSocket server');
        statusDiv.textContent = 'Disconnected, please restart the Python server';
    };

    websocket.onerror = (error) => {
        console.error('Websocket error:', error);
        statusDiv.textContent = 'Connection Error, check the connectivity of the Python server';
    };
});