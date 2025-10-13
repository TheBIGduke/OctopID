window.addEventListener('DOMContentLoaded', () => {
    const mouth = document.getElementById('mouth');
    const statusDiv = document.getElementById('status');
    const serverAddress = 'ws://localhost:1940';

    console.log(`Connecting to WebSocket server at ${serverAddress}...`);
    const websocket = new WebSocket(serverAddress);

    websocket.onopen = () => {
        console.log('Successfully connected to the WebSocket server');
        statusDiv.textContent = 'Connected! Play some audio';
    };

    websocket.onmessage = (event) => {
        // Parse the incoming JSON data from server
        const audioData = JSON.parse(event.data);
        const bassLevel = audioData.bass;

        // Animate the mouth
        // The curve of the smile is modified based on the bass level
        // Attribute 'd' of the SVG path defines the shape
        // Command "Q" creates a quadratic Bezier curve
        // We are animating the 'y' coordinate of the curve's control point

        const baseHeight = 130;
        const maxOpen = 40;
        const mouthOpenness = baseHeight + (bassLevel * maxOpen);

        const baseWidth = 60;
        const maxWidthDisplacement = 20;
        const mouthWidth = baseWidth - (bassLevel * maxWidthDisplacement);

        const newPath = `M ${mouthWidth} 130 Q 100 ${mouthOpenness} ${200-mouthWidth} 130`;

        mouth.setAttribute('d', newPath);
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