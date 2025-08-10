import os
import cv2
from datetime import datetime
from config import SCREENSHOT_DIR

def save_screenshot(image, reason):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{reason}_{timestamp}.jpg"
    path = os.path.join(SCREENSHOT_DIR, filename)
    cv2.imwrite(path, image)
