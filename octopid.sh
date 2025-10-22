#!/bin/bash

# Define the target file and position variables
TARGET_FILE="/path/to/your/face.html"
TARGET_POSITION="X=YOUR_X_COORDINATE, Y=YOUR_Y_COORDINATE"
PYTHON_SCRIPT="/path/to/your/audioServer.py"

# --- Cleanup function to run on exit (e.g., Ctrl+C) ---
cleanup() {
    echo -e "\nShutting down OctopID processes..."
    # Kill the background Python server
    pkill -f "python3 ${PYTHON_SCRIPT}" 
    # Kill the foreground Chromium process and any related chrome processes
    pkill -f "chromium-browser --kiosk file://${TARGET_FILE}"
    pkill chrome
    echo "Cleanup complete. Exiting."
    exit 0
}

# Trap the INT signal (Ctrl+C) and execute the cleanup function
trap cleanup INT

# 1. Start the Python server in the background
echo "Executing Python script: ${PYTHON_SCRIPT}"
python3 ${PYTHON_SCRIPT} &
SERVER_PID=$!

# Give the server a moment to initialize
sleep 2 

# --- 2. Start Chromium in Kiosk mode ---
echo "Starting Chromium in kiosk mode..."
echo "Target File: ${TARGET_FILE}"
echo "Target Position: ${TARGET_POSITION}"

chromium-browser \
    --kiosk \
    --window-position='${TARGET_POSITION}' \
    "file://${TARGET_FILE}"
echo "Chromium closed. Killing background server (PID: ${SERVER_PID})."
kill ${SERVER_PID}

# Remove the trap just before a clean exit
trap - INT

exit 0