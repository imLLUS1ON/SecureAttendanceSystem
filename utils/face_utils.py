from deepface import DeepFace
import os
import cv2

def find_matching_roll(frame_path, student_dir="images/"):
    for file in os.listdir(student_dir):
        db_img_path = os.path.join(student_dir, file)
        try:
            result = DeepFace.verify(img1_path=frame_path, img2_path=db_img_path, enforce_detection=False)
            if result['verified']:
                return file.replace(".jpg", "")  # roll number
        except Exception as e:
            continue
    return None
