import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque

# Initialize MediaPipe Face Mesh with optimized settings
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Optimized game settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 90
BALL_SIZE = 15
BALL_SPEED = 6  # Slightly increased for more challenge
PADDLE_SPEED = 5
HEAD_CONTROL_SENSITIVITY = 1.8  # Adjusted for better control

# Game states
START_SCREEN = 0
PLAYING = 1
PAUSED = 2

class PongGame:
    def __init__(self):
        self.ball_pos = [WINDOW_WIDTH//2, WINDOW_HEIGHT//2]
        self.ball_vel = [BALL_SPEED, BALL_SPEED]
        self.left_paddle = WINDOW_HEIGHT//2
        self.right_paddle = WINDOW_HEIGHT//2
        self.left_score = 0
        self.right_score = 0
        self.smooth_head_y = deque(maxlen=5)
        self.game_state = START_SCREEN
        self.player_ready = False
        
    def update(self, head_y=None):
        if self.game_state == PAUSED:
            return
            
        # Improved AI paddle movement with prediction
        predicted_ball_y = self.ball_pos[1] + self.ball_vel[1] * (self.ball_pos[0] / BALL_SPEED)
        self.left_paddle += (predicted_ball_y - self.left_paddle) * 0.08
        
        # Smoother player paddle control
        if head_y is not None:
            self.smooth_head_y.append(head_y)
            avg_head_y = sum(self.smooth_head_y) / len(self.smooth_head_y)
            target_y = avg_head_y * WINDOW_HEIGHT
            self.right_paddle += (target_y - self.right_paddle) * HEAD_CONTROL_SENSITIVITY * 0.1
        
        # Smoother ball movement
        self.ball_pos[0] += self.ball_vel[0]
        self.ball_pos[1] += self.ball_vel[1]
        
        # Enhanced collision detection
        if self.ball_pos[1] <= BALL_SIZE or self.ball_pos[1] >= WINDOW_HEIGHT - BALL_SIZE:
            self.ball_vel[1] *= -1.02  # Slightly increase speed on bounces
            
        paddle_hit_sound = False
        # Left paddle collision with improved physics
        if (self.ball_pos[0] - BALL_SIZE <= PADDLE_WIDTH and 
            self.left_paddle - PADDLE_HEIGHT//2 <= self.ball_pos[1] <= self.left_paddle + PADDLE_HEIGHT//2):
            hit_pos = (self.ball_pos[1] - self.left_paddle) / (PADDLE_HEIGHT/2)
            self.ball_vel[0] = abs(self.ball_vel[0]) * 1.05  # Speed up slightly
            self.ball_vel[1] += hit_pos * 2  # Add angle based on hit position
            paddle_hit_sound = True
            
        # Right paddle collision with improved physics
        if (self.ball_pos[0] + BALL_SIZE >= WINDOW_WIDTH - PADDLE_WIDTH and 
            self.right_paddle - PADDLE_HEIGHT//2 <= self.ball_pos[1] <= self.right_paddle + PADDLE_HEIGHT//2):
            hit_pos = (self.ball_pos[1] - self.right_paddle) / (PADDLE_HEIGHT/2)
            self.ball_vel[0] = -abs(self.ball_vel[0]) * 1.05  # Speed up slightly
            self.ball_vel[1] += hit_pos * 2  # Add angle based on hit position
            paddle_hit_sound = True
            
        # Normalize ball velocity to prevent extreme angles
        speed = np.sqrt(self.ball_vel[0]**2 + self.ball_vel[1]**2)
        if speed > BALL_SPEED * 2:
            self.ball_vel = [v * (BALL_SPEED * 2 / speed) for v in self.ball_vel]
        
        # Score points with visual feedback
        if self.ball_pos[0] <= 0:
            self.right_score += 1
            self.reset_ball(1)  # Launch towards right
        elif self.ball_pos[0] >= WINDOW_WIDTH:
            self.left_score += 1
            self.reset_ball(-1)  # Launch towards left

    def reset_ball(self, direction=None):
        self.ball_pos = [WINDOW_WIDTH//2, WINDOW_HEIGHT//2]
        angle = np.random.uniform(-0.5, 0.5)  # Random angle
        if direction is None:
            direction = 1 if np.random.random() > 0.5 else -1
        self.ball_vel = [
            BALL_SPEED * direction * np.cos(angle),
            BALL_SPEED * np.sin(angle)
        ]

    def draw(self, frame):
        # Use camera feed as background with dimming
        game_frame = cv2.resize(frame, (WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay = game_frame.copy()
        cv2.addWeighted(overlay, 0.6, np.zeros_like(overlay), 0.4, 0, game_frame)
        
        # Draw game elements with enhanced visuals
        # Draw paddles with glow effect
        self.draw_paddle_with_glow(game_frame, 0, self.left_paddle, (200, 200, 200))
        self.draw_paddle_with_glow(game_frame, WINDOW_WIDTH - PADDLE_WIDTH, self.right_paddle, (200, 200, 200))
        
        # Draw ball with motion blur
        self.draw_ball_with_trail(game_frame)
        
        # Draw scores with background
        self.draw_score(game_frame)
        
        return game_frame

    def draw_paddle_with_glow(self, frame, x, y, color):
        # Add glow effect
        for i in range(3):
            alpha = 0.3 - i * 0.1
            thickness = PADDLE_WIDTH - i * 2
            cv2.rectangle(frame,
                         (x, int(y - PADDLE_HEIGHT//2)),
                         (x + thickness, int(y + PADDLE_HEIGHT//2)),
                         color, -1)
            
    def draw_ball_with_trail(self, frame):
        # Draw ball trail
        alpha = 0.3
        for i in range(3):
            pos = [int(self.ball_pos[0] - self.ball_vel[0] * i),
                   int(self.ball_pos[1] - self.ball_vel[1] * i)]
            size = BALL_SIZE - i * 2
            cv2.circle(frame, tuple(pos), size, (255, 255, 255), -1)

    def draw_score(self, frame):
        # Draw score with background
        score_y = 50
        # Left score
        cv2.putText(frame, str(self.left_score),
                    (WINDOW_WIDTH//4, score_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 4)
        cv2.putText(frame, str(self.left_score),
                    (WINDOW_WIDTH//4, score_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)
        
        # Right score
        cv2.putText(frame, str(self.right_score),
                    (3*WINDOW_WIDTH//4, score_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 4)
        cv2.putText(frame, str(self.right_score),
                    (3*WINDOW_WIDTH//4, score_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)

    def draw_start_screen(self, frame):
        screen = cv2.resize(frame, (WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay = np.zeros_like(screen)

        # Create gradient background
        for i in range(WINDOW_HEIGHT):
            alpha = i / WINDOW_HEIGHT
            overlay[i] = [int(40 * alpha), int(100 * alpha), int(40 * alpha)]

        # Blend gradient with camera feed
        cv2.addWeighted(overlay, 0.6, screen, 0.7, 0, screen)

        # Draw title with glow effect
        title_text = "Single Player Pong"
        title_pos = (WINDOW_WIDTH//2 - 180, WINDOW_HEIGHT//2 - 50)
        
        # Draw glow
        for offset in range(3):
            cv2.putText(screen, title_text,
                        (title_pos[0] - offset, title_pos[1]),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5,
                        (0, 255 - offset*30, 0), 5-offset)
        
        # Main text
        cv2.putText(screen, title_text, title_pos,
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
        
        # Draw player status with animation
        status = "Ready!" if self.player_ready else "Stand in front of camera"
        color = (0, 255, 0) if self.player_ready else (0, 165, 255)
        
        # Status text with glow
        status_pos = (WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 + 50)
        cv2.putText(screen, f"Player: {status}", status_pos,
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3)
        cv2.putText(screen, f"Player: {status}", status_pos,
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        # Draw start button when ready
        if self.player_ready:
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
    game = PongGame()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)  # Mirror display
        
        # Process face mesh
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)
        
        # Get head position
        head_y = None
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            nose_tip = face_landmarks.landmark[1]
            head_y = nose_tip.y
            h, w = frame.shape[:2]
            cv2.circle(frame, 
                      (int(nose_tip.x * w), int(nose_tip.y * h)),
                      10, (0, 255, 0), 2)
            
        if game.game_state == START_SCREEN:
            # Update player readiness
            game.player_ready = results.multi_face_landmarks is not None
            
            # Draw start screen
            screen = game.draw_start_screen(frame)
            
            # Check for game start
            if game.player_ready:
                if cv2.waitKey(1) & 0xFF == ord(' '):
                    game.game_state = PLAYING
                    
            cv2.imshow('Pong Game', screen)
            
        elif game.game_state == PLAYING:
            # Update and draw game
            game.update(head_y if results.multi_face_landmarks else None)
            game_frame = game.draw(frame)
            cv2.imshow('Pong Game', game_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
