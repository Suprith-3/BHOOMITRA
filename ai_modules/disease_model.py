import cv2
import numpy as np
import os

class DiseaseModel:

    # -----------------------------
    # IMAGE FILE DETECTION
    # -----------------------------
    def detect_disease(self, image_path):

        print("OpenCV image processing started")

        img = cv2.imread(image_path)

        if img is None:
            return "Invalid Image", 0

        return self.process_frame(img)


    # -----------------------------
    # PROCESS FRAME (used for camera)
    # -----------------------------
    def process_frame(self, img):

        img = cv2.resize(img, (256,256))

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        lower = np.array([10,50,50])
        upper = np.array([35,255,255])

        mask = cv2.inRange(hsv, lower, upper)

        infected_pixels = cv2.countNonZero(mask)

        total_pixels = img.shape[0] * img.shape[1]

        ratio = infected_pixels / total_pixels

        highlighted = img.copy()

        highlighted[mask > 0] = [0,0,255]


        # Disease prediction
        if ratio > 0.15:
            disease = "Leaf Blight"
            confidence = round(ratio*100,2)

        elif ratio > 0.07:
            disease = "Powdery Mildew"
            confidence = round(ratio*100,2)

        else:
            disease = "Healthy Leaf"
            confidence = 95.0


        return disease, confidence


    # -----------------------------
    # LIVE CAMERA DETECTION
    # -----------------------------
    def start_camera_detection(self):

        print("Starting OpenCV Camera...")

        cap = cv2.VideoCapture(0)

        while True:

            ret, frame = cap.read()

            if not ret:
                break

            disease, confidence = self.process_frame(frame)

            # Display prediction text
            cv2.putText(
                frame,
                f"{disease} ({confidence}%)",
                (20,40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0,255,0),
                2
            )

            cv2.imshow("Crop Disease Detection - Live", frame)

            # Press Q to exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


        cap.release()
        cv2.destroyAllWindows()