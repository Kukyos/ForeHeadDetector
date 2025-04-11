import os
import cv2
import numpy as np

class FaceDatabase:
    def __init__(self, friendly_dir="friendly", cache_duration=1.0):
        self.friendly_dir = friendly_dir
        self.face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.friendly_faces = []
        self.face_cache = {}
        self.cache_duration = cache_duration
        self.min_face_size = (60, 60)
        self.trained = False
        self.load_friendly_faces()
        
    @property
    def friendly_embeddings(self):
        return {str(i): face for i, face in enumerate(self.friendly_faces)}

    def load_friendly_faces(self):
        if not os.path.exists(self.friendly_dir):
            os.makedirs(self.friendly_dir)
            return

        faces = []
        labels = []
        label = 0

        for img_file in os.listdir(self.friendly_dir):
            if img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                img_path = os.path.join(self.friendly_dir, img_file)
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    faces.append(img)
                    labels.append(label)
                    label += 1

        if faces:
            self.friendly_faces = faces
            try:
                faces_resized = [cv2.resize(face, (100, 100)) for face in faces]
                self.face_recognizer.train(faces_resized, np.array(labels))
                self.trained = True
            except Exception as e:
                self.trained = False

    def is_friendly(self, face_img, face_id=None):
        if not self.trained or not self.friendly_faces:
            return False

        try:
            gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
            faces = self.face_detector.detectMultiScale(gray, 1.3, 5)
            
            if len(faces) > 0:
                (x, y, w, h) = faces[0]
                face_roi = gray[y:y+h, x:x+w]
                face_roi = cv2.resize(face_roi, (100, 100))
                
                label, confidence = self.face_recognizer.predict(face_roi)
                return confidence < 70  # Lower confidence is better match
        except Exception:
            pass
            
        return False
