import cv2
import mediapipe as mp
import numpy as np
from flask import Flask, Response, render_template, jsonify
import datetime
import threading
import time

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Initialize MediaPipe Pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

# Exercise counter variables
exercise_counter = 0
exercise_stage = None
last_timestamp = time.time()
exercise_type = "squat"  # Options: 'squat', 'pushup', 'lunge'

# Landmark data and exercise analysis data
analysis_data = {
    "posture_feedback": "Your posture is correct.",
    "exercise_count": 0,
    "calories_burned": 0,
    "workout_duration": 0
}

# Session start time
session_start_time = datetime.datetime.now()

# Calculate posture accuracy score
def calculate_posture_score(landmarks):
    # Simple posture score calculation
    # In a real implementation, a more complex algorithm would be needed
    score = 100  # Base score
    
    # Check shoulder balance (difference in y-coordinate between left/right shoulder)
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
    shoulder_diff = abs(left_shoulder.y - right_shoulder.y)
    if shoulder_diff > 0.05:  # Threshold setting
        score -= 10
        
    # Check hip balance
    left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
    hip_diff = abs(left_hip.y - right_hip.y)
    if hip_diff > 0.05:
        score -= 10
    
    # Generate feedback based on posture
    if score >= 90:
        feedback = "Your posture is correct."
    elif score >= 70:
        feedback = "Your posture is slightly unbalanced. Pay attention to shoulder and hip alignment."
    else:
        feedback = "Your posture is unbalanced. Please correct your form."
    
    analysis_data["posture_feedback"] = feedback
    
    return score

# Squat movement counting function
def count_squats(landmarks):
    global exercise_counter, exercise_stage
    
    # Calculate joint angles between knee and hip
    left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
    left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
    
    # Calculate knee angle (using vector calculation)
    hip_knee_vec = [left_knee.x - left_hip.x, left_knee.y - left_hip.y]
    knee_ankle_vec = [left_ankle.x - left_knee.x, left_ankle.y - left_knee.y]
    
    # Calculate angle using dot product
    dot_product = hip_knee_vec[0] * knee_ankle_vec[0] + hip_knee_vec[1] * knee_ankle_vec[1]
    hip_knee_magnitude = (hip_knee_vec[0]**2 + hip_knee_vec[1]**2)**0.5
    knee_ankle_magnitude = (knee_ankle_vec[0]**2 + knee_ankle_vec[1]**2)**0.5
    
    # Calculate angle (convert from radians to degrees)
    angle = np.arccos(dot_product / (hip_knee_magnitude * knee_ankle_magnitude))
    angle = angle * 180.0 / np.pi
    
    # Count squat movement
    if angle < 120:  # Knees bent
        exercise_stage = "down"
    elif angle > 160 and exercise_stage == "down":  # Standing back up
        exercise_stage = "up"
        exercise_counter += 1
        analysis_data["exercise_count"] = exercise_counter
        # Simple calorie calculation (would be more complex in reality)
        analysis_data["calories_burned"] = exercise_counter * 0.32
    
    return angle

# Movement classification function
def classify_movement(landmarks):
    # For this simple example, we'll classify based on the ratio of upper to lower body movement
    upper_body_movement = 0
    lower_body_movement = 0
    
    # Upper body movement (shoulders, elbows, wrists)
    landmarks_upper = [
        mp_pose.PoseLandmark.LEFT_SHOULDER.value,
        mp_pose.PoseLandmark.RIGHT_SHOULDER.value,
        mp_pose.PoseLandmark.LEFT_ELBOW.value,
        mp_pose.PoseLandmark.RIGHT_ELBOW.value,
        mp_pose.PoseLandmark.LEFT_WRIST.value,
        mp_pose.PoseLandmark.RIGHT_WRIST.value
    ]
    
    # Lower body movement (hips, knees, ankles)
    landmarks_lower = [
        mp_pose.PoseLandmark.LEFT_HIP.value,
        mp_pose.PoseLandmark.RIGHT_HIP.value,
        mp_pose.PoseLandmark.LEFT_KNEE.value,
        mp_pose.PoseLandmark.RIGHT_KNEE.value,
        mp_pose.PoseLandmark.LEFT_ANKLE.value,
        mp_pose.PoseLandmark.RIGHT_ANKLE.value
    ]
    
    # In a real implementation, we would calculate change from previous frames
    # Here we'll just use a simple logic based on y-coordinate changes
    
    # Determine exercise type (simple logic)
    if lower_body_movement > upper_body_movement * 2:
        return "Lower body exercise (squat/lunge)"
    elif upper_body_movement > lower_body_movement * 2:
        return "Upper body exercise (pushup/plank)"
    else:
        return "Compound exercise"

def generate_frames():
    # Webcam setup
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    with mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as pose:
        
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print("Cannot load webcam.")
                break
                
            # Set image to read-only for better performance
            frame.flags.writeable = False
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(frame)
            
            # Draw pose annotations on image
            frame.flags.writeable = True
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            if results.pose_landmarks:
                # Draw pose landmarks
                mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
                
                # Analyze posture and count exercises
                landmarks = results.pose_landmarks.landmark
                posture_score = calculate_posture_score(landmarks)
                
                if exercise_type == "squat":
                    angle = count_squats(landmarks)
                    
                # Display analysis info on screen
                cv2.putText(frame, f"Posture Score: {posture_score}", (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Exercise Count: {exercise_counter}", (10, 60), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Feedback: {analysis_data['posture_feedback']}", (10, 90), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Update workout time
                current_time = datetime.datetime.now()
                duration = (current_time - session_start_time).seconds
                analysis_data["workout_duration"] = duration
                
                cv2.putText(frame, f"Workout Time: {duration}s", (10, 120), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Encode frame for web streaming
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/analysis_data')
def get_analysis_data():
    return jsonify(analysis_data)

@app.route('/set_exercise_type/<exercise_type_name>')
def set_exercise_type(exercise_type_name):
    global exercise_type
    if exercise_type_name in ['squat', 'pushup', 'lunge']:
        exercise_type = exercise_type_name
        return jsonify({"status": "success", "message": f"Exercise type changed to {exercise_type_name}."})
    return jsonify({"status": "error", "message": "Unsupported exercise type."})

if __name__ == '__main__':
    # Need to create index.html file in templates folder
    app.run(debug=True)