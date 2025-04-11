import cv2
import mediapipe as mp
import time
import numpy as np
from collections import deque
import json

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=config['tracking']['max_faces'],
    refine_landmarks=True,
    min_detection_confidence=config['tracking']['detection_confidence'],
    min_tracking_confidence=config['tracking']['tracking_confidence']
)

# Expanded face outline including more hair coverage
FACE_OUTLINE_POINTS = [
    10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377,
    # Top of head and hair
    10, 108, 67, 103, 54, 21, 162, 127, 234, 93, 132, 58, 172, 136, 150, 149, 176, 148, 152,
    # Sides of head (including hair area)
    447, 366, 401, 435, 367, 364, 394, 395, 369, 396, 175, 171, 140, 170, 169, 135, 138, 215,
    # Extra hair volume points
    54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74
]

# Key landmarks for head center calculation
HEAD_CENTER_POINTS = {
    'front': 168,    # Nose bridge
    'back': 8,       # Back of head approximation
    'left': 234,     # Left ear
    'right': 454,    # Right ear
    'top': 10,       # Top of head
    'bottom': 152    # Bottom of chin
}

def calculate_brain_center(landmarks, frame_w, frame_h):
    """Calculate approximate brain center position"""
    left_ear = landmarks.landmark[HEAD_CENTER_POINTS['left']]
    right_ear = landmarks.landmark[HEAD_CENTER_POINTS['right']]
    top_head = landmarks.landmark[HEAD_CENTER_POINTS['top']]
    
    # Calculate brain center using ears and top of head
    center_x = (left_ear.x + right_ear.x) / 2
    center_y = (left_ear.y + right_ear.y + top_head.y) / 3  # Weight towards top of head
    center_z = (left_ear.z + right_ear.z) / 2
    
    return np.array([center_x * frame_w, center_y * frame_h, center_z * frame_w])

# Add calibration constants
KNOWN_DISTANCE = 60.0  # Distance for calibration in cm
REAL_WIDTH = 15.0      # Average human head width in cm
FOCAL_LENGTH = None    # Will be calculated during calibration

# Initialize tracking variables
current_targets = 0
position_buffers = []
radius_buffers = []
distance_buffers = []

# Set camera to maximum resolution
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, config['display']['width'])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config['display']['height'])
cap.set(cv2.CAP_PROP_FPS, 60)  # Try to get 60fps if camera supports it

# Initialize font settings
FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = config['display']['font_scale']
LINE_THICKNESS = config['display']['line_thickness']
CROSS_SIZE = config['crosshair']['size']  # Add this line

# Add anti-aliasing to circles and lines
cv2.LINE_AA = cv2.LINE_AA if hasattr(cv2, 'LINE_AA') else 16

# Initialize FPS counter
prev_frame_time = 0
new_frame_time = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Apply subtle image enhancement
    frame = cv2.bilateralFilter(frame, 5, 75, 75)  # Reduce noise while preserving edges
    
    # Adjust brightness and contrast
    frame = cv2.convertScaleAbs(frame, alpha=1.1, beta=5)
    
    # Use high-quality resize with Lanczos interpolation
    frame = cv2.resize(frame, (config['display']['width'], config['display']['height']), 
                      interpolation=cv2.INTER_LANCZOS4)
    
    # Convert to RGB and process with MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    # Calculate FPS
    new_frame_time = time.time()
    fps = 1/(new_frame_time-prev_frame_time) if prev_frame_time > 0 else 0
    prev_frame_time = new_frame_time

    if results.multi_face_landmarks:
        current_targets = len(results.multi_face_landmarks)
        frames_since_detection = 0

        # Initialize buffers for new faces
        while len(position_buffers) < current_targets:
            position_buffers.append(deque(maxlen=5))
        while len(radius_buffers) < current_targets:
            radius_buffers.append(deque(maxlen=5))
        while len(distance_buffers) < current_targets:
            distance_buffers.append(deque(maxlen=5))

        # Process each face
        for idx, face_landmarks in enumerate(results.multi_face_landmarks):
            frame_h, frame_w = frame.shape[:2]
            
            # Calculate brain center as target
            brain_center = calculate_brain_center(face_landmarks, frame_w, frame_h)
            target_point_2d = (int(brain_center[0]), int(brain_center[1]))

            # Get face outline points for head circle
            face_points = []
            for landmark_id in FACE_OUTLINE_POINTS:
                landmark = face_landmarks.landmark[landmark_id]
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                face_points.append((x, y))

            if len(face_points) > 0:
                face_points = np.array(face_points, dtype=np.int32)
                (x, y), radius = cv2.minEnclosingCircle(face_points)
                radius = int(radius * 1.15)

                # Calculate distance for this face
                perceived_width = radius * 2
                if FOCAL_LENGTH is None:
                    FOCAL_LENGTH = (perceived_width * KNOWN_DISTANCE) / REAL_WIDTH
                
                distance = (FOCAL_LENGTH * REAL_WIDTH) / perceived_width if FOCAL_LENGTH else None
                if distance:
                    distance_buffers[idx].append(distance)
                    smooth_distance = np.mean(distance_buffers[idx])

                # Use separate buffers for each face
                position_buffers[idx].append((int(x), int(y)))
                radius_buffers[idx].append(radius)

                # Calculate smoothed values for this face
                smooth_center = (int(np.mean([p[0] for p in position_buffers[idx]])),
                               int(np.mean([p[1] for p in position_buffers[idx]])))
                smooth_radius = int(np.mean(radius_buffers[idx]))

                # Draw circle and crosshair
                cv2.circle(frame, smooth_center, smooth_radius, 
                          tuple(config['colors']['circle']), LINE_THICKNESS, cv2.LINE_AA)
                
                # Draw crosshair
                for offset in range(config['crosshair']['glow_intensity']):
                    cv2.line(frame, 
                            (target_point_2d[0] - CROSS_SIZE, target_point_2d[1]),
                            (target_point_2d[0] + CROSS_SIZE, target_point_2d[1]),
                            (200, 0, 0), LINE_THICKNESS + offset, cv2.LINE_AA)
                    cv2.line(frame,
                            (target_point_2d[0], target_point_2d[1] - CROSS_SIZE),
                            (target_point_2d[0], target_point_2d[1] + CROSS_SIZE),
                            (200, 0, 0), LINE_THICKNESS + offset, cv2.LINE_AA)

                # Display distance above the target
                if distance:
                    distance_text = f"{smooth_distance:.1f}cm"
                    text_position = (smooth_center[0] - 30, smooth_center[1] - smooth_radius - 10)
                    cv2.putText(frame, distance_text, text_position,
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, tuple(config['colors']['distance_text']), 2)

    # Enhanced text rendering with background
    def draw_text_with_background(text, pos, scale=FONT_SCALE):
        thickness = LINE_THICKNESS
        text_size = cv2.getTextSize(text, FONT, scale, thickness)[0]
        
        # Draw background rectangle
        cv2.rectangle(frame,
                     (pos[0] - 5, pos[1] - text_size[1] - 5),
                     (pos[0] + text_size[0] + 5, pos[1] + 5),
                     (0, 0, 0), -1)
        
        # Draw text
        cv2.putText(frame, text, pos, FONT, scale,
                   tuple(config['colors']['text']), thickness, cv2.LINE_AA)

    # Apply enhanced text rendering to all text elements
    draw_text_with_background(f"FPS: {int(fps)}", (10, 30))
    draw_text_with_background(f"Targets: {current_targets}", (10, 70))

    # Show instructions
    draw_text_with_background("Press 'q' to quit", (10, frame.shape[0] - 10))

    # Add frame rate limiter
    time.sleep(0.01)  # Limit to ~100 FPS max

    # Display frame
    cv2.imshow('Forehead Detector', frame)

    # Update key handling
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
face_mesh.close()
