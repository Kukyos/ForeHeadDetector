import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque

# Initialize MediaPipe Face Mesh with optimized settings
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=2,
    refine_landmarks=True,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

# Optimized game settings
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 90
BALL_SIZE = 15
BALL_SPEED = 7
HEAD_CONTROL_SENSITIVITY = 1.8

# Game states
START_SCREEN = 0
PLAYING = 1
PAUSED = 2

class TwoPlayerPong:
    def __init__(self):
        self.ball_pos = [WINDOW_WIDTH//2, WINDOW_HEIGHT//2]
        self.ball_vel = [BALL_SPEED, BALL_SPEED]
        self.left_paddle = WINDOW_HEIGHT//2
        self.right_paddle = WINDOW_HEIGHT//2
        self.left_score = 0
        self.right_score = 0
        self.game_state = START_SCREEN
        self.left_player_ready = False
        self.right_player_ready = False
        self.smooth_left_y = deque(maxlen=5)
        self.smooth_right_y = deque(maxlen=5)
        
    def update(self, left_y=None, right_y=None):
        if self.game_state == PAUSED:
            return
            
        # Smooth paddle movement
        if left_y is not None:
            self.smooth_left_y.append(left_y)
            avg_left_y = sum(self.smooth_left_y) / len(self.smooth_left_y)
            target_left_y = avg_left_y * WINDOW_HEIGHT
            self.left_paddle += (target_left_y - self.left_paddle) * HEAD_CONTROL_SENSITIVITY * 0.1
            
        if right_y is not None:
            self.smooth_right_y.append(right_y)
            avg_right_y = sum(self.smooth_right_y) / len(self.smooth_right_y)
            target_right_y = avg_right_y * WINDOW_HEIGHT
            self.right_paddle += (target_right_y - self.right_paddle) * HEAD_CONTROL_SENSITIVITY * 0.1
            
        # Ball movement with trail effect
        self.ball_pos[0] += self.ball_vel[0]
        self.ball_pos[1] += self.ball_vel[1]
        
        # Enhanced collision detection with better physics
        if self.ball_pos[1] <= BALL_SIZE or self.ball_pos[1] >= WINDOW_HEIGHT - BALL_SIZE:
            self.ball_vel[1] *= -1.02  # Slightly increase speed on bounces
            
        # Left paddle collision with improved physics
        if (self.ball_pos[0] - BALL_SIZE <= PADDLE_WIDTH and 
            self.left_paddle - PADDLE_HEIGHT//2 <= self.ball_pos[1] <= self.left_paddle + PADDLE_HEIGHT//2):
            hit_pos = (self.ball_pos[1] - self.left_paddle) / (PADDLE_HEIGHT/2)
            self.ball_vel[0] = abs(self.ball_vel[0]) * 1.05  # Speed up slightly
            self.ball_vel[1] += hit_pos * 2  # Add angle based on hit position
            
        # Right paddle collision with improved physics
        if (self.ball_pos[0] + BALL_SIZE >= WINDOW_WIDTH - PADDLE_WIDTH and 
            self.right_paddle - PADDLE_HEIGHT//2 <= self.ball_pos[1] <= self.right_paddle + PADDLE_HEIGHT//2):
            hit_pos = (self.ball_pos[1] - self.right_paddle) / (PADDLE_HEIGHT/2)
            self.ball_vel[0] = -abs(self.ball_vel[0]) * 1.05  # Speed up slightly
            self.ball_vel[1] += hit_pos * 2  # Add angle based on hit position
            
        # Normalize ball velocity to prevent extreme angles
        speed = np.sqrt(self.ball_vel[0]**2 + self.ball_vel[1]**2)
        if speed > BALL_SPEED * 2:
            self.ball_vel = [v * (BALL_SPEED * 2 / speed) for v in self.ball_vel]
            
        # Score points
        if self.ball_pos[0] <= 0:
            self.right_score += 1
            self.reset_ball(-1)  # Launch towards left
        elif self.ball_pos[0] >= WINDOW_WIDTH:
            self.left_score += 1
            self.reset_ball(1)  # Launch towards right

    def reset_ball(self, direction=None):
        self.ball_pos = [WINDOW_WIDTH//2, WINDOW_HEIGHT//2]
        angle = np.random.uniform(-0.5, 0.5)  # Random angle
        if direction is None:
            direction = 1 if np.random.random() > 0.5 else -1
        self.ball_vel = [
            BALL_SPEED * direction * np.cos(angle),
            BALL_SPEED * np.sin(angle)
        ]

    def draw_paddle_with_glow(self, game_frame, x, y, color):
        # Create paddle glow effect
        for i in range(3):
            alpha = 0.3 - i * 0.1
            thickness = PADDLE_WIDTH - i * 2
            cv2.rectangle(game_frame,
                         (x, int(y - PADDLE_HEIGHT//2)),
                         (x + thickness, int(y + PADDLE_HEIGHT//2)),
                         color, -1)

    def draw_ball_with_trail(self, game_frame):
        # Draw ball trail effect
        for i in range(3):
            pos = [int(self.ball_pos[0] - self.ball_vel[0] * i),
                   int(self.ball_pos[1] - self.ball_vel[1] * i)]
            size = BALL_SIZE - i * 2
            cv2.circle(game_frame, tuple(pos), size, (255, 255, 255), -1)

    def draw_score(self, game_frame):
        score_y = 50
        # Left score with shadow
        cv2.putText(game_frame, str(self.left_score),
                    (50, score_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 4)
        cv2.putText(game_frame, str(self.left_score),
                    (50, score_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)
        
        # Right score with shadow
        cv2.putText(game_frame, str(self.right_score),
                    (WINDOW_WIDTH-80, score_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 4)
        cv2.putText(game_frame, str(self.right_score),
                    (WINDOW_WIDTH-80, score_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)

    def draw(self, frame, face_positions=None):
        # Use camera feed as background with dimming
        game_frame = cv2.resize(frame, (WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay = game_frame.copy()
        cv2.addWeighted(overlay, 0.6, np.zeros_like(overlay), 0.4, 0, game_frame)
        
        # Draw game elements with enhanced visuals
        self.draw_paddle_with_glow(game_frame, 0, self.left_paddle, (200, 200, 200))
        self.draw_paddle_with_glow(game_frame, WINDOW_WIDTH - PADDLE_WIDTH, self.right_paddle, (200, 200, 200))
        self.draw_ball_with_trail(game_frame)
        self.draw_score(game_frame)
        
        return game_frame

    def draw_start_screen(self, frame, players_detected):
        screen = cv2.resize(frame, (WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay = np.zeros_like(screen)

        # Create gradient background
        for i in range(WINDOW_HEIGHT):
            alpha = i / WINDOW_HEIGHT
            overlay[i] = [int(40 * alpha), int(100 * alpha), int(40 * alpha)]

        # Blend gradient with camera feed
        cv2.addWeighted(overlay, 0.6, screen, 0.7, 0, screen)

        # Draw title with glow effect
        title_text = "Two Player Pong"
        title_pos = (WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 - 50)
        
        # Draw glow
        for offset in range(3):
            cv2.putText(screen, title_text,
                        (title_pos[0] - offset, title_pos[1]),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5,
                        (0, 255 - offset*30, 0), 5-offset)
        
        # Main title
        cv2.putText(screen, title_text, title_pos,
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
        
        # Draw player status with visual feedback
        left_status = "Ready!" if self.left_player_ready else "Stand on left"
        right_status = "Ready!" if self.right_player_ready else "Stand on right"
        
        # Left player status
        left_color = (0, 255, 0) if self.left_player_ready else (0, 165, 255)
        status_pos = (50, WINDOW_HEIGHT//2 + 50)
        cv2.putText(screen, f"Player 1: {left_status}", status_pos,
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3)
        cv2.putText(screen, f"Player 1: {left_status}", status_pos,
                    cv2.FONT_HERSHEY_SIMPLEX, 1, left_color, 2)
        
        # Right player status
        right_color = (0, 255, 0) if self.right_player_ready else (0, 165, 255)
        status_pos = (WINDOW_WIDTH - 350, WINDOW_HEIGHT//2 + 50)
        cv2.putText(screen, f"Player 2: {right_status}", status_pos,
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3)
        cv2.putText(screen, f"Player 2: {right_status}", status_pos,
                    cv2.FONT_HERSHEY_SIMPLEX, 1, right_color, 2)

        # Draw start button when both players ready
        if self.left_player_ready and self.right_player_ready:
            btn_y = WINDOW_HEIGHT - 150
            cv2.rectangle(screen,
                         (WINDOW_WIDTH//2 - 100, btn_y),
                         (WINDOW_WIDTH//2 + 100, btn_y + 60),
                         (0, 200, 0), -1)
            cv2.rectangle(screen,
                         (WINDOW_WIDTH//2 - 100, btn_y),
                         (WINDOW_WIDTH//2 + 100, btn_y + 60),
                         (0, 255, 0), 2)
            cv2.putText(screen, "SPACE to Start",
                        (WINDOW_WIDTH//2 - 90, btn_y + 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        return screen

def main():
    cap = cv2.VideoCapture(0)
    game = TwoPlayerPong()
    
    print("Two Player Pong - Use your heads to control the paddles!")
    print("Player 1: Stand on left side")
    print("Player 2: Stand on right side")
    print("Press 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)  # Mirror display
        
        # Process faces
        results = face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        frame_h, frame_w = frame.shape[:2]
        
        # Track faces and determine positions
        faces = []
        if results.multi_face_landmarks:
            for face_lm in results.multi_face_landmarks:
                nose_tip = face_lm.landmark[1]
                x_pos = int(nose_tip.x * frame_w)
                y_pos = nose_tip.y
                faces.append((x_pos, y_pos))
                cv2.circle(frame, (x_pos, int(y_pos * frame_h)), 5, (0, 255, 0), -1)
        
        if game.game_state == START_SCREEN:
            # Update player readiness
            if len(faces) >= 2:
                faces.sort(key=lambda x: x[0])  # Sort by x position
                # Mark players as ready if they're on correct sides
                game.left_player_ready = faces[0][0] < frame_w * 0.4
                game.right_player_ready = faces[1][0] > frame_w * 0.6
            else:
                game.left_player_ready = False
                game.right_player_ready = False
            
            # Draw start screen
            screen = game.draw_start_screen(frame, len(faces))
            
            # Check for game start
            if game.left_player_ready and game.right_player_ready:
                if cv2.waitKey(1) & 0xFF == ord(' '):
                    game.game_state = PLAYING
                    
            cv2.imshow('Two Player Pong', screen)
            
        elif game.game_state == PLAYING:
            # Get player positions
            left_y = right_y = None
            if len(faces) >= 2:
                faces.sort(key=lambda x: x[0])
                left_y, right_y = faces[0][1], faces[1][1]
            
            # Update and draw game
            game.update(left_y, right_y)
            game_frame = game.draw(frame)
            cv2.imshow('Two Player Pong', game_frame)
        
        # Show player view
        cv2.imshow('Players View', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
