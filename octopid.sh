#!/bin/bash
  
# ==============================================================================
# Universal Kiosk Script (Single Launch)
# ==============================================================================
  
# --- CONFIGURE THESE FOUR VARIABLES ---
  
# 1. Set the absolute path to the HTML file you want to open.
HTML_FILE="/path/to/your/file.html"
  
# 2. Set the absolute path to the Python file you want to run.
#    (Use 'python3' if your system uses it instead of 'python')
PYTHON_SCRIPT="/path/to/your/script.py"

# 3. Set the X coordinate you found in Step 1.
SCREEN_X=YOUR_X_COORDINATE
  
# 4. Set the Y coordinate you found in Step 1.
SCREEN_Y=YOUR_Y_COORDINATE
  
# --- (Optional) Adjust delay in seconds ---
STARTUP_DELAY=5
# --- END CONFIGATION ---
  
# --- RUN PYTHON SCRIPT ---
echo "Executing Python script: $PYTHON_SCRIPT"
# The 'python' command will wait here until the script finishes.
# Use 'python3' instead of 'python' if required by your environment.
python "$PYTHON_SCRIPT"
echo "Python script finished execution."
# -------------------------

# This optional delay only happens once, when the script first starts.
sleep $STARTUP_DELAY
  
echo "Starting Chromium in kiosk mode..."
echo "Target File: $HTML_FILE"
echo "Target Position: X=$SCREEN_X, Y=$SCREEN_Y"
  
# Launch Chromium browser with all the required settings.
# The script will wait here until the browser window is closed, and then it will exit.
chromium-browser --kiosk \
                 --window-position=$SCREEN_X,$SCREEN_Y \
                 --disable-features=TranslateUI \
                 --app="file://$HTML_FILE"
  
echo "Chromium closed. Script finished."