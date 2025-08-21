import os
import base64
import json
from io import BytesIO
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from PIL import Image
import re
import numpy as np

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# In-memory user storage (no default user)
users = {}

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def save_image(base64_string, username):
    # Remove data URL prefix
    base64_data = base64_string.split(',')[1]
    
    # Decode base64
    image_data = base64.b64decode(base64_data)
    
    # Process image with PIL for better quality
    image = Image.open(BytesIO(image_data))
    
    # Convert to RGB if needed
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Save image with high quality
    filename = secure_filename(f"{username}.jpg")
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(filepath, 'JPEG', quality=95)
    
    return filepath

def compare_images(image1_path, image2_base64):
    try:
        # Process stored image
        with open(image1_path, 'rb') as f:
            stored_image = Image.open(BytesIO(f.read()))
        
        # Process captured image
        base2_data = image2_base64.split(',')[1]
        captured_image = Image.open(BytesIO(base64.b64decode(base2_data)))
        
        # Convert to same size and format for comparison
        stored_image = stored_image.convert('RGB').resize((256, 256))
        captured_image = captured_image.convert('RGB').resize((256, 256))
        
        # Convert to numpy arrays for easier comparison
        stored_array = np.array(stored_image)
        captured_array = np.array(captured_image)
        
        # Calculate the absolute difference between images
        diff = np.abs(stored_array - captured_array)
        
        # Count pixels that are similar (within a threshold)
        threshold = 50  # Allow some variation in color
        similar_pixels = np.sum(diff < threshold)
        
        # Calculate similarity percentage
        total_pixels = stored_array.size
        similarity = (similar_pixels / total_pixels) * 100
        
        # Return True if similarity is at least 10%
        return similarity >= 10
    except Exception as e:
        print(f"Image comparison error: {e}")
        return False

@app.route('/')
def index():
    return redirect(url_for('signup'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = request.form.get('email')
        image_data = request.form.get('image')
        
        # Validation
        if not username or not password or not confirm_password or not email or not image_data:
            return jsonify({"success": False, "message": "All fields are required"})
        
        if password != confirm_password:
            return jsonify({"success": False, "message": "Passwords do not match"})
        
        if not validate_email(email):
            return jsonify({"success": False, "message": "Invalid email format"})
        
        if username in users:
            return jsonify({"success": False, "message": "Username already exists"})
        
        # Save user data
        image_path = save_image(image_data, username)
        users[username] = {
            'password': generate_password_hash(password),
            'email': email,
            'image_path': image_path
        }
        
        session['username'] = username
        return jsonify({"success": True, "message": "Signup successful"})
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        image_data = request.form.get('image')
        
        # Validation
        if not username or not password or not image_data:
            return jsonify({"success": False, "message": "All fields are required"})
        
        if username not in users:
            return jsonify({"success": False, "message": "Username not found"})
        
        user = users[username]
        
        # Check password
        if not check_password_hash(user['password'], password):
            return jsonify({"success": False, "message": "Incorrect password"})
        
        # Check image with 10% match threshold
        if not compare_images(user['image_path'], image_data):
            return jsonify({"success": False, "message": "Face does not match. Please try again.", "retry": True})
        
        session['username'] = username
        return jsonify({"success": True, "message": "Login successful"})
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Create signup.html template with enhanced CSS
    with open('templates/signup.html', 'w', encoding='utf-8') as f:
        f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Smart Signup</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background-color: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            padding: 30px;
            width: 100%;
            max-width: 600px;
            animation: fadeIn 0.8s ease-in-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 25px;
            font-weight: 600;
        }
        
        .form-group {
            margin-bottom: 20px;
            position: relative;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 500;
        }
        
        input {
            width: 100%;
            padding: 12px 15px;
            box-sizing: border-box;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        
        input:focus {
            border-color: #4CAF50;
            box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.2);
            outline: none;
        }
        
        button {
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
            padding: 14px 20px;
            border: none;
            cursor: pointer;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            width: 100%;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(76, 175, 80, 0.3);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        #camera-container {
            text-align: center;
            margin: 25px 0;
            position: relative;
        }
        
        #video {
            display: none;
            max-width: 100%;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        
        #canvas {
            display: none;
        }
        
        .camera-btn {
            background: linear-gradient(45deg, #2196F3, #0b7dda);
            margin: 8px;
            padding: 12px 20px;
            border-radius: 8px;
            transition: all 0.3s ease;
            width: 45%;
        }
        
        .camera-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(33, 150, 243, 0.3);
        }
        
        .notification {
            padding: 15px;
            margin: 15px 0;
            border-radius: 8px;
            animation: slideIn 0.5s ease-out;
        }
        
        @keyframes slideIn {
            from { transform: translateX(-100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        .error {
            background: #ffdddd;
            color: #f44336;
            border-left: 4px solid #f44336;
        }
        
        .success {
            background: #ddffdd;
            color: #4CAF50;
            border-left: 4px solid #4CAF50;
        }
        
        #photo-preview {
            max-width: 100%;
            display: none;
            margin-top: 15px;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            animation: fadeIn 0.5s ease-in-out;
        }
        
        p {
            text-align: center;
            margin-top: 20px;
            color: #666;
        }
        
        a {
            color: #2196F3;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s ease;
        }
        
        a:hover {
            color: #0b7dda;
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Create Account</h1>
        <div id="notification"></div>
        
        <form id="signup-form">
            <div class="form-group">
                <label for="username">Username:</label>
                <input type="text" id="username" name="username" required>
            </div>
            
            <div class="form-group">
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <div class="form-group">
                <label for="confirm_password">Confirm Password:</label>
                <input type="password" id="confirm_password" name="confirm_password" required>
            </div>
            
            <div class="form-group">
                <label for="email">Email:</label>
                <input type="email" id="email" name="email" required>
            </div>
            
            <div id="camera-container">
                <video id="video" width="640" height="480" autoplay></video>
                <canvas id="canvas" width="640" height="480"></canvas>
                <div>
                    <button type="button" id="start-camera" class="camera-btn">Start Camera</button>
                    <button type="button" id="capture-photo" class="camera-btn">Capture Photo</button>
                </div>
                <img id="photo-preview">
            </div>
            
            <button type="submit">Sign Up</button>
        </form>
        
        <p>Already have an account? <a href="/login">Login</a></p>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const video = document.getElementById('video');
            const canvas = document.getElementById('canvas');
            const context = canvas.getContext('2d');
            const startButton = document.getElementById('start-camera');
            const captureButton = document.getElementById('capture-photo');
            const photoPreview = document.getElementById('photo-preview');
            const form = document.getElementById('signup-form');
            const notification = document.getElementById('notification');
            
            let stream = null;
            let capturedImage = null;
            
            startButton.addEventListener('click', async function() {
                try {
                    const constraints = {
                        video: {
                            width: { ideal: 640 },
                            height: { ideal: 480 },
                            facingMode: 'user'
                        }
                    };
                    
                    stream = await navigator.mediaDevices.getUserMedia(constraints);
                    video.srcObject = stream;
                    video.style.display = 'block';
                    startButton.disabled = true;
                    captureButton.disabled = false;
                } catch (err) {
                    showNotification('Camera access denied or not available', 'error');
                }
            });
            
            captureButton.addEventListener('click', function() {
                context.drawImage(video, 0, 0, canvas.width, canvas.height);
                const imageData = canvas.toDataURL('image/jpeg', 0.9);
                capturedImage = imageData;
                
                photoPreview.src = imageData;
                photoPreview.style.display = 'block';
                
                // Stop the camera stream
                if (stream) {
                    stream.getTracks().forEach(track => track.stop());
                }
                video.style.display = 'none';
                captureButton.disabled = true;
            });
            
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                if (!capturedImage) {
                    showNotification('Please capture a photo', 'error');
                    return;
                }
                
                const formData = new FormData(form);
                formData.append('image', capturedImage);
                
                fetch('/signup', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showNotification(data.message, 'success');
                        setTimeout(() => window.location.href = '/dashboard', 1500);
                    } else {
                        showNotification(data.message, 'error');
                    }
                })
                .catch(error => {
                    showNotification('An error occurred. Please try again.', 'error');
                });
            });
            
            function showNotification(message, type) {
                notification.textContent = message;
                notification.className = `notification ${type}`;
                notification.style.display = 'block';
                
                setTimeout(() => {
                    notification.style.display = 'none';
                }, 5000);
            }
        });
    </script>
</body>
</html>
        ''')
    
    # Create login.html template with enhanced CSS
    with open('templates/login.html', 'w', encoding='utf-8') as f:
        f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Smart Login</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background-color: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            padding: 30px;
            width: 100%;
            max-width: 600px;
            animation: fadeIn 0.8s ease-in-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 25px;
            font-weight: 600;
        }
        
        .form-group {
            margin-bottom: 20px;
            position: relative;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 500;
        }
        
        input {
            width: 100%;
            padding: 12px 15px;
            box-sizing: border-box;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        
        input:focus {
            border-color: #4CAF50;
            box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.2);
            outline: none;
        }
        
        button {
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
            padding: 14px 20px;
            border: none;
            cursor: pointer;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            width: 100%;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(76, 175, 80, 0.3);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        #camera-container {
            text-align: center;
            margin: 25px 0;
            position: relative;
        }
        
        #video {
            display: none;
            max-width: 100%;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        
        #canvas {
            display: none;
        }
        
        .camera-btn {
            background: linear-gradient(45deg, #2196F3, #0b7dda);
            margin: 8px;
            padding: 12px 20px;
            border-radius: 8px;
            transition: all 0.3s ease;
            width: 45%;
        }
        
        .camera-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(33, 150, 243, 0.3);
        }
        
        .notification {
            padding: 15px;
            margin: 15px 0;
            border-radius: 8px;
            animation: slideIn 0.5s ease-out;
        }
        
        @keyframes slideIn {
            from { transform: translateX(-100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        .error {
            background: #ffdddd;
            color: #f44336;
            border-left: 4px solid #f44336;
        }
        
        .success {
            background: #ddffdd;
            color: #4CAF50;
            border-left: 4px solid #4CAF50;
        }
        
        #photo-preview {
            max-width: 100%;
            display: none;
            margin-top: 15px;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            animation: fadeIn 0.5s ease-in-out;
        }
        
        p {
            text-align: center;
            margin-top: 20px;
            color: #666;
        }
        
        a {
            color: #2196F3;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s ease;
        }
        
        a:hover {
            color: #0b7dda;
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Login</h1>
        <div id="notification"></div>
        
        <form id="login-form">
            <div class="form-group">
                <label for="username">Username:</label>
                <input type="text" id="username" name="username" required>
            </div>
            
            <div class="form-group">
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <div id="camera-container">
                <video id="video" width="640" height="480" autoplay></video>
                <canvas id="canvas" width="640" height="480"></canvas>
                <div>
                    <button type="button" id="start-camera" class="camera-btn">Start Camera</button>
                    <button type="button" id="capture-photo" class="camera-btn">Capture Photo</button>
                </div>
                <img id="photo-preview">
            </div>
            
            <button type="submit">Login</button>
        </form>
        
        <p>Don't have an account? <a href="/signup">Sign Up</a></p>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const video = document.getElementById('video');
            const canvas = document.getElementById('canvas');
            const context = canvas.getContext('2d');
            const startButton = document.getElementById('start-camera');
            const captureButton = document.getElementById('capture-photo');
            const photoPreview = document.getElementById('photo-preview');
            const form = document.getElementById('login-form');
            const notification = document.getElementById('notification');
            
            let stream = null;
            let capturedImage = null;
            
            // Function to start camera
            async function startCamera() {
                try {
                    const constraints = {
                        video: {
                            width: { ideal: 640 },
                            height: { ideal: 480 },
                            facingMode: 'user'
                        }
                    };
                    
                    stream = await navigator.mediaDevices.getUserMedia(constraints);
                    video.srcObject = stream;
                    video.style.display = 'block';
                    startButton.disabled = true;
                    captureButton.disabled = false;
                    photoPreview.style.display = 'none';
                } catch (err) {
                    showNotification('Camera access denied or not available', 'error');
                }
            }
            
            startButton.addEventListener('click', startCamera);
            
            captureButton.addEventListener('click', function() {
                context.drawImage(video, 0, 0, canvas.width, canvas.height);
                const imageData = canvas.toDataURL('image/jpeg', 0.9);
                capturedImage = imageData;
                
                photoPreview.src = imageData;
                photoPreview.style.display = 'block';
                
                // Stop the camera stream
                if (stream) {
                    stream.getTracks().forEach(track => track.stop());
                }
                video.style.display = 'none';
                captureButton.disabled = true;
            });
            
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                if (!capturedImage) {
                    showNotification('Please capture a photo', 'error');
                    return;
                }
                
                const formData = new FormData(form);
                formData.append('image', capturedImage);
                
                fetch('/login', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showNotification(data.message, 'success');
                        setTimeout(() => window.location.href = '/dashboard', 1500);
                    } else {
                        showNotification(data.message, 'error');
                        
                        // If face doesn't match, restart camera for retry
                        if (data.retry) {
                            capturedImage = null;
                            setTimeout(() => {
                                startCamera();
                            }, 2000);
                        }
                    }
                })
                .catch(error => {
                    showNotification('An error occurred. Please try again.', 'error');
                });
            });
            
            function showNotification(message, type) {
                notification.textContent = message;
                notification.className = `notification ${type}`;
                notification.style.display = 'block';
                
                setTimeout(() => {
                    notification.style.display = 'none';
                }, 5000);
            }
        });
    </script>
</body>
</html>
        ''')
    
    # Create dashboard.html template with enhanced CSS
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background-color: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            padding: 40px;
            width: 100%;
            max-width: 800px;
            margin-top: 40px;
            animation: fadeIn 0.8s ease-in-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 1px solid #eee;
        }
        
        .logo {
            font-size: 24px;
            font-weight: 700;
            color: #4CAF50;
        }
        
        .user-info {
            display: flex;
            align-items: center;
        }
        
        .user-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: linear-gradient(45deg, #4CAF50, #45a049);
            display: flex;
            justify-content: center;
            align-items: center;
            color: white;
            font-weight: 600;
            margin-right: 12px;
        }
        
        .username {
            font-weight: 600;
            color: #333;
        }
        
        h1 {
            color: #333;
            margin-bottom: 25px;
            font-weight: 600;
            text-align: center;
        }
        
        .welcome-message {
            text-align: center;
            font-size: 24px;
            color: #555;
            margin-bottom: 40px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .dashboard-card {
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
            text-align: center;
            border: 1px solid #eee;
        }
        
        .dashboard-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        }
        
        .card-icon {
            font-size: 40px;
            margin-bottom: 15px;
            color: #4CAF50;
        }
        
        .card-title {
            font-size: 18px;
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
        }
        
        .card-description {
            color: #666;
            font-size: 14px;
        }
        
        .logout-btn {
            background: linear-gradient(45deg, #f44336, #d32f2f);
            color: white;
            padding: 12px 25px;
            border: none;
            cursor: pointer;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
            margin-top: 20px;
            display: block;
            margin-left: auto;
            margin-right: auto;
        }
        
        .logout-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(244, 67, 54, 0.3);
        }
        
        footer {
            margin-top: 30px;
            text-align: center;
            color: #666;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">SmartLogin</div>
            <div class="user-info">
                <div class="user-avatar">{{ username[0].upper() }}</div>
                <div class="username">{{ username }}</div>
            </div>
        </header>
        
        <h1>Dashboard</h1>
        
        <div class="welcome-message">
            Welcome to the dashboard, {{ username }}!
        </div>
        
        <div class="dashboard-grid">
            <div class="dashboard-card">
                <div class="card-icon">👤</div>
                <div class="card-title">Profile</div>
                <div class="card-description">Manage your account settings</div>
            </div>
            
            <div class="dashboard-card">
                <div class="card-icon">🔒</div>
                <div class="card-title">Security</div>
                <div class="card-description">Update your security settings</div>
            </div>
            
            <div class="dashboard-card">
                <div class="card-icon">📊</div>
                <div class="card-title">Analytics</div>
                <div class="card-description">View your activity statistics</div>
            </div>
            
            <div class="dashboard-card">
                <div class="card-icon">⚙️</div>
                <div class="card-title">Settings</div>
                <div class="card-description">Customize your experience</div>
            </div>
        </div>
        
        <a href="/logout" class="logout-btn">Logout</a>
        
        <footer>
            © 2023 SmartLogin. All rights reserved.
        </footer>
    </div>
</body>
</html>
        ''')
    
    app.run(debug=True)