import cv2
import time
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from config import *
from utils.drawing import draw_landmarks_on_image
from utils.face_analysis import process_blendshapes, process_face_direction
from utils.screenshot import save_screenshot
from utils.report import generate_report_pdf

event_log = {
    "timestamps": [],
    "drowsiness": [],
    "talking": [],
    "distraction": [],
    "no_face": [],
    "multiple_faces": [],
    "attention_score": []
}

def main():
    base_options = python.BaseOptions(model_asset_path='face_landmarker.task')
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        output_face_blendshapes=True,
        output_facial_transformation_matrixes=True,
        num_faces=2)
    detector = vision.FaceLandmarker.create_from_options(options)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Error: Could not open webcam.")
        return

    print("🎥 Press 'q' to quit monitoring.")
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)

        try:
            detection_result = detector.detect(mp_image)
        except Exception as e:
            print(f"⚠️ Detection error: {e}")
            continue

        num_faces = len(detection_result.face_landmarks)
        event_log["timestamps"].append(int(time.time()))

        if num_faces == 0:
            cv2.putText(frame, "No faces detected", (10, 420),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            save_screenshot(frame, "no_face")
            event_log["no_face"].append(1)
            event_log["multiple_faces"].append(0)
        elif num_faces > 1:
            cv2.putText(frame, "Multiple faces detected", (10, 420),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            save_screenshot(frame, "multiple_faces")
            event_log["multiple_faces"].append(1)
            event_log["no_face"].append(0)
        else:
            event_log["no_face"].append(0)
            event_log["multiple_faces"].append(0)

        # Annotate and analyze face
        if detection_result.face_landmarks:
            annotated = draw_landmarks_on_image(rgb_image, detection_result.face_landmarks)
            if detection_result.face_blendshapes:
                annotated = process_blendshapes(annotated, detection_result.face_blendshapes[0], event_log)
            if detection_result.facial_transformation_matrixes:
                annotated = process_face_direction(annotated, detection_result.facial_transformation_matrixes[0], event_log)
        else:
            annotated = rgb_image

        # Display
        bgr_image = cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR)
        cv2.imshow('EduPulse Attentiveness Monitor', bgr_image)

        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

    # Cleanup
    cap.release()  
    cv2.destroyAllWindows()
    generate_report_pdf(event_log)

if __name__ == "__main__":
    main()
