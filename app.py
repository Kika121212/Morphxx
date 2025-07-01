from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import mediapipe as mp
import base64

app = Flask(__name__)

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

def process_frame(image_np):
    image_rgb = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(image_np, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    _, buffer = cv2.imencode('.jpg', image_np)
    return base64.b64encode(buffer).decode('utf-8')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    data = request.json['image']
    image_data = base64.b64decode(data.split(',')[1])
    np_arr = np.frombuffer(image_data, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    processed_image = process_frame(frame)
    return jsonify({'image': processed_image})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
