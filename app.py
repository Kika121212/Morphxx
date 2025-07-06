from flask import Flask, render_template, request, jsonify
import cv2
import mediapipe as mp
import numpy as np
import base64
import os
from datetime import datetime

app = Flask(_name_)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False)
mp_drawing = mp.solutions.drawing_utils

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs("data", exist_ok=True)

# Placeholder for user data storage
def save_user_data(user_id, data):
    user_folder = f"data/{user_id}"
    os.makedirs(user_folder, exist_ok=True)
    with open(f"{user_folder}/session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
        import json
        json.dump(data, f, indent=2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_frame', methods=['POST'])
def process_frame():
    data = request.json
    frame_data = data['frame']
    user_id = data.get('user_id', 'guest')

    # Decode base64 image
    img_data = base64.b64decode(frame_data.split(',')[1])
    nparr = np.frombuffer(img_data, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Run pose detection
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)

    angle = 0
    reps = 0
    phase = "Start"

    if results.pose_landmarks:
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # Calculate left elbow angle
        l_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
        l_elbow = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW]
        l_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]

        def to_xy(landmark):
            return np.array([landmark.x, landmark.y])

        a, b, c = to_xy(l_shoulder), to_xy(l_elbow), to_xy(l_wrist)

        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        if angle > 180.0:
            angle = 360 - angle

    # Convert to base64 to return to frontend
    _, buffer = cv2.imencode('.jpg', frame)
    processed_image = base64.b64encode(buffer).decode('utf-8')

    return jsonify({
        'image': f"data:image/jpeg;base64,{processed_image}",
        'angle': int(angle),
        'reps': reps,
        'phase': phase
    })

if _name_ == '_main_':
    app.run(debug=True)
