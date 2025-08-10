import os

# Directories
SCREENSHOT_DIR = "screenshots"
REPORT_DIR = "reports"

# Ensure directories exist
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# Audio alert settings
BEEP_FREQ = 500  # in Hz
BEEP_DURATION = 500  # in milliseconds
