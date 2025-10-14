window.addEventListener('DOMContentLoaded', () => {
    const face = document.getElementById('face');
    const mouth = document.getElementById('mouth');
    const eyes = document.querySelectorAll('.eye');
    const pupils = document.querySelectorAll('.pupil');
    const pupilHighlights = document.querySelectorAll('.pupil-highlight'); // Select the highlights
    const statusDiv = document.getElementById('status');
    const serverAddress = 'ws://localhost:1940';

    const restingMouthPath = 'M 60 130 Q 100 135 140 130';
    let targetMouthPath = restingMouthPath;
    let currentMouthPath = restingMouthPath;
    let isWideEyed = false; // Flag to prevent rapid re-triggering of eye animation

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

    // --- Eye Panning Animation (pupils and highlights) ---
    const panEyes = () => {
        const panX = Math.random() * 8 - 4;
        const panY = Math.random() * 10 - 5;

        // Move Pupils
        pupils.forEach(pupil => {
            const originalCx = pupil.getAttribute('data-original-cx') || pupil.getAttribute('cx');
            const originalCy = pupil.getAttribute('data-original-cy') || pupil.getAttribute('cy');
            if (!pupil.getAttribute('data-original-cx')) {
                pupil.setAttribute('data-original-cx', originalCx);
                pupil.setAttribute('data-original-cy', originalCy);
            }
            pupil.setAttribute('cx', parseFloat(originalCx) + panX);
            pupil.setAttribute('cy', parseFloat(originalCy) + panY);
        });

        // Move Highlights
        pupilHighlights.forEach(highlight => {
            const originalCx = highlight.getAttribute('data-original-cx') || highlight.getAttribute('cx');
            const originalCy = highlight.getAttribute('data-original-cy') || highlight.getAttribute('cy');
            if (!highlight.getAttribute('data-original-cx')) {
                highlight.setAttribute('data-original-cx', originalCx);
                highlight.setAttribute('data-original-cy', originalCy);
            }
            highlight.setAttribute('cx', parseFloat(originalCx) + panX);
            highlight.setAttribute('cy', parseFloat(originalCy) + panY);
        });
    };
    setInterval(panEyes, Math.random() * 4000 + 3000);

    // --- Mouth Breathing Animation ---
    const breathe = () => {
        if (targetMouthPath === restingMouthPath) {
            const breathAmount = Math.random() * 2;
            targetMouthPath = `M 60 130 Q 100 ${135 + breathAmount} 140 130`;
        }
    };
    setInterval(breathe, 1500);

    const websocket = new WebSocket(serverAddress);

    websocket.onopen = () => {
        console.log('Successfully connected to the WebSocket server');
        statusDiv.textContent = 'Connected! Play some audio';
    };

    websocket.onmessage = (event) => {
        const audioData = JSON.parse(event.data);
        const bassLevel = audioData.bass;
        const highLevel = audioData.highs;
        const talkingThreshold = 0.1;
        const highThreshold = 0.5;

        // --- Mouth talking animation ---
        if (bassLevel > talkingThreshold) {
            const maxRy = 25;
            const maxRx = 45;
            const ry = bassLevel * maxRy;
            const rx = 40 + (bassLevel * (maxRx - 40));
            targetMouthPath = `M ${100-rx},130 A ${rx},${ry} 0 1,1 ${100+rx},130 A ${rx},${ry} 0 1,1 ${100-rx},130 Z`;
        } else {
            targetMouthPath = restingMouthPath;
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
            if (newPoints.length === 6) {
                newPath = `M ${newPoints[0]} ${newPoints[1]} Q ${newPoints[2]} ${newPoints[3]} ${newPoints[4]} ${newPoints[5]}`;
            } else if (newPoints.length === 16) {
                newPath = `M ${newPoints[0]},${newPoints[1]} A ${newPoints[2]},${newPoints[3]} ${newPoints[4]} ${newPoints[5]},${newPoints[6]} ${newPoints[7]},${newPoints[8]} A ${newPoints[9]},${newPoints[10]} ${newPoints[11]} ${newPoints[12]},${newPoints[13]} ${newPoints[14]},${newPoints[15]} Z`;
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