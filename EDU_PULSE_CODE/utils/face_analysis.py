import cv2
import numpy as np
import threading
import time
from utils.audio_alert import beep
from utils.screenshot import save_screenshot

# Global state
lip_movement_start_time = None
lip_moving = False

def process_blendshapes(image, blendshapes, event_log):
    global lip_movement_start_time, lip_moving

    y = 20
    mood_score = {"drowsy": 0, "attentive": 0}
    lips_moving_now = False

    for category in blendshapes:
        name = category.category_name
        score = category.score

        if name in ["eyeClosedLeft", "eyeClosedRight", "browDownLeft", "browDownRight", "mouthOpen", "cheekPuff"]:
            mood_score["drowsy"] += score
        elif name in ["eyeWideLeft", "eyeWideRight", "browOuterUpLeft", "browOuterUpRight"]:
            mood_score["attentive"] += score

        if name in ["jawOpen1", "mouthClose1", "mouthFunnel1", "mouthPucker"] and score > 0.3:
            lips_moving_now = True

    mood = "Drowsy" if mood_score["drowsy"]  > mood_score["attentive"] + 0.01 else "Attentive"
    cv2.putText(image, f"Mood: {mood}", (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (0, 255, 0) if mood == "Attentive" else (0, 0, 255), 2)
    y += 30

    if mood == "Drowsy":
        event_log["drowsiness"].append(1)
        event_log["attention_score"].append(0)
        threading.Thread(target=beep).start()
    else:
        event_log["drowsiness"].append(0)
        event_log["attention_score"].append(1)

    if lips_moving_now:
        if not lip_moving:
            lip_movement_start_time = time.time()
            lip_moving = True
        elif time.time() - lip_movement_start_time > .5:
            cv2.putText(image, "!!! Talking Detected !!!", (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            event_log["talking"].append(1)
            y += 30
        else:
            event_log["talking"].append(0)
    else:
        lip_moving = False
        lip_movement_start_time = None
        event_log["talking"].append(0)

    return image


def process_face_direction(image, matrix, event_log):
    matrix = np.array(matrix.data).reshape(4, 4)
    rotation_matrix = matrix[:3, :3]

    sy = np.sqrt(rotation_matrix[0, 0] ** 2 + rotation_matrix[1, 0] ** 2)
    singular = sy < 1e-6

    if not singular:
        x = np.arctan2(rotation_matrix[2, 1], rotation_matrix[2, 2])
        y = np.arctan2(-rotation_matrix[2, 0], sy)
        z = np.arctan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
    else:
        x = np.arctan2(-rotation_matrix[1, 2], rotation_matrix[1, 1])
        y = np.arctan2(-rotation_matrix[2, 0], sy)
        z = 0

    pitch, yaw, roll = np.degrees([x, y, z])

    direction = "Straight"
    if yaw > 15:
        direction = "Left"
    elif yaw < -15:
        direction = "Right"
    elif pitch < -15:
        direction = "Up"
    elif pitch > 15:
        direction = "Down"

    cv2.putText(image, f"Direction: {direction}", (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    if direction in ["Left", "Right", "Up"]:
        event_log["distraction"].append(1)
        save_screenshot(image, f"Looking {direction}")
    else:
        event_log["distraction"].append(0)

    return image
