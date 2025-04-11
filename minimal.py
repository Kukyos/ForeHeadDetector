import cv2
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=False,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    if not ret:
        break
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)
    
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            h, w = frame.shape[:2]
            face_points = []
            key_points = [10, 234, 454, 152]  # top, left, right, bottom
            for idx in key_points:
                point = face_landmarks.landmark[idx]
                x = int(point.x * w)
                y = int(point.y * h)
                face_points.append((x, y))
            
            if face_points:
                x_coords = [p[0] for p in face_points]
                y_coords = [p[1] for p in face_points]
                center_x = int((max(x_coords) + min(x_coords)) / 2)
                center_y = int((max(y_coords) + min(y_coords)) / 2)
                radius = int((max(x_coords) - min(x_coords)) / 2)

                cv2.circle(frame, (center_x, center_y), radius, (0, 255, 0), 2)
    
    cv2.imshow('Minimal', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
face_mesh.close()