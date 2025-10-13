window.addEventListener('DOMContentLoaded', () => {
    const mouth = document.getElementById('mouth');
    const eyes = document.querySelectorAll('.eye');
    const statusDiv = document.getElementById('status');
    const serverAddress = 'ws://localhost:1940';

    const restingMouthPath = 'M 60 130 Q 100 135 140 130';
    const restingRx = 40;
    const restingRy = 5; // The effective "ry" of our resting curve is small

    let currentRx = restingRx;
    let currentRy = restingRy;
    let targetRx = restingRx;
    let targetRy = restingRy;

    // --- Blinking Animation ---
    const blink = () => {
        eyes.forEach(eye => {
            eye.setAttribute('ry', '1'); // Close eyes
        });
        setTimeout(() => {
            eyes.forEach(eye => {
                eye.setAttribute('ry', '15'); // Open eyes
            });
        }, 150); // Duration of the blink
    };
    setInterval(blink, 4000);

    // --- Animation Loop for Smooth Transitions ---
    const animateMouth = () => {
        // Move a fraction of the distance towards the target each frame
        currentRx += (targetRx - currentRx) * 0.25;
        currentRy += (targetRy - currentRy) * 0.25;

        // Check if we are very close to the resting state, and if so, snap to the clean resting path
        if (Math.abs(currentRx - restingRx) < 0.1 && Math.abs(currentRy - restingRy) < 0.1) {
            mouth.setAttribute('d', restingMouthPath);
        } else {
            // Otherwise, draw the interpolated ellipse shape
            const newPath = `M ${100-currentRx},130 A ${currentRx},${currentRy} 0 1,1 ${100+currentRx},130 A ${currentRx},${currentRy} 0 1,1 ${100-currentRx},130 Z`;
            mouth.setAttribute('d', newPath);
        }

        // Keep the loop running
        requestAnimationFrame(animateMouth);
    };

    // Start the animation loop
    animateMouth();

    console.log(`Connecting to WebSocket server at ${serverAddress}...`);
    const websocket = new WebSocket(serverAddress);

    websocket.onopen = () => {
        console.log('Successfully connected to the WebSocket server');
        statusDiv.textContent = 'Connected! Play some audio';
    };

    websocket.onmessage = (event) => {
        const audioData = JSON.parse(event.data);
        const bassLevel = audioData.bass;
        const talkingThreshold = 0.08;

        if (bassLevel > talkingThreshold) {
            // Set the target shape for talking
            const maxRy = 30;
            const maxRx = 45;
            targetRy = bassLevel * maxRy;
            targetRx = 40 + (bassLevel * (maxRx - 40));
        } else {
            // Set the target shape for resting
            targetRx = restingRx;
            targetRy = restingRy;
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