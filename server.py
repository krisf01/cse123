from flask import Flask, request, jsonify, render_template, redirect, session, flash
import json
from functools import wraps
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore, db
import secrets
import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from datetime import datetime

# Initialize Firebase Admin
cred = credentials.Certificate('/Users/kfout/cse123_test/cse123/cse123-bac2c-firebase-adminsdk-cj30n-c9082dc2a9.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://cse123-bac2c-default-rtdb.firebaseio.com/'
})

firebase_db = db.reference()

# Directory where the files will be written and saved
UPLOAD_FOLDER_TEXTS = '/Users/kfout/storage/text'
UPLOAD_FOLDER_IMAGES = '/Users/kfout/storage/images'
COMMANDS_FOLDER = '/Users/kfout/uploads'
COMMANDS_FILE = 'instructions.json'
DATA_JSON_FILE = os.path.join(UPLOAD_FOLDER_TEXTS, 'data.json')

# Ensure the necessary folders exist
# Ensure the necessary folders exist
if not os.path.exists(UPLOAD_FOLDER_TEXTS):
    os.makedirs(UPLOAD_FOLDER_TEXTS)
if not os.path.exists(COMMANDS_FOLDER):
    os.makedirs(COMMANDS_FOLDER)
if not os.path.exists(UPLOAD_FOLDER_IMAGES):
    os.makedirs(UPLOAD_FOLDER_IMAGES)

if not os.path.exists(DATA_JSON_FILE):
    with open(DATA_JSON_FILE, 'w') as file:
        json.dump([], file)

def validate_token(auth_token):
    # Retrieve the expected token from environment variables
    expected_token = os.environ.get("BEARER_TOKEN")
    if not expected_token:
        raise EnvironmentError("Bearer token not set in the environment variables")
    return auth_token == expected_token

from functools import wraps

def require_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]  # Get the token part of the header
            if validate_token(token):
                return f(*args, **kwargs)
            else:
                return jsonify({"message": "Unauthorized"}), 401
        return jsonify({"message": "Authorization token not provided"}), 401
    return decorated_function


app = Flask(__name__)
#CORS(app, resources={r"/*": {"origins": "https://cse123petfeeder.com"}})  # Adjust this as needed
CORS(app, resources={r"/*": {"origins": "*"}})  # Adjust this as needed

app.secret_key = secrets.token_urlsafe(16)  # Generates a new key


@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')


# Main dashboard page
@app.route('/')
def home():
    print("Session content:", session)  # Debug print to see what's inside the session
    if 'api_key' not in session:
        print("No API key found, redirecting to login")
        return redirect('/login')
    print("Rendering index.html with API Key:", session['api_key'])  # Debug print
    return render_template('index.html')

# NEWEST
@app.route('/api/food_level', methods=['GET'])
def get_food_level():
    try:
        ref = db.reference('users/cse123petfeeder')
        entries = ref.get()
        
        if entries:
            # Directly checking if 'food_level' is in the dictionary, as it seems there's only one entry
            if 'food_level' in entries:
                return jsonify({"food_level": entries['food_level']}), 200
            else:
                return jsonify({"error": "No food level data found"}), 404
        else:
            return jsonify({"error": "No data found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# NEWEST
@app.route('/api/water_level', methods=['GET'])
def get_water_level():
    try:
        ref = db.reference('users/cse123petfeeder')
        entries = ref.get()
        
        if entries:
            # Directly checking if 'food_level' is in the dictionary, as it seems there's only one entry
            if 'water_level' in entries:
                return jsonify({"water_level": entries['water_level']}), 200
            else:
                return jsonify({"error": "No water level data found"}), 404
        else:
            return jsonify({"error": "No data found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# This route may need to be adjusted or removed based on your app's needs
@app.route('/', methods=['POST'])
def handle_buttons():
    content = request.get_data(as_text=True)
    print(content)

    if "Water Level" in content:
        return jsonify({"response": "Water Level Checked"})
    elif "Food Level" in content:
        return jsonify({"response": "Food Level Checked"})
    else:
        return jsonify({"response": "Unknown Action"}), 400
    
def generate_api_key():
    return secrets.token_urlsafe(16)  # Adjust the length as needed

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('Authorization')
        if validate_api_key(api_key):
            return f(*args, **kwargs)
        return jsonify({"message": "Unauthorized"}), 401
    return decorated_function

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        user = firebase_db.child('users').child(username).get()
        if user and user.get('password') == password:
            session['api_key'] = user.get('api_key')
            print("API Key set in session:", session['api_key'])  # Debug print
            return jsonify({"api_key": session['api_key']}), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    return render_template('login.html')

def validate_api_key(key):
    users_dict = firebase_db.child('users').get()
    if users_dict:
        for user_id, user_info in users_dict.items():
            if user_info.get('api_key') == key:
                return True
    return False

    
# API to update levels, requiring API key
@app.route('/api/update_levels', methods=['POST'])
@require_api_key
def update_levels():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    try:
        ref = firebase_db.child(f'users/{user_id}/food_water_levels')
        ref.push(data)
        return jsonify({"status": "Data updated in Firebase"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/get_levels', methods=['GET'])
@require_api_key
def get_levels():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        ref = db.reference(f'users/{user_id}/food_water_levels')
        data = ref.get()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/live_feed', methods=['GET'])
def get_pic():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        ref = db.reference(f'users/{user_id}')
        entries = ref.get()

        if entries and 'image_url' in entries:
            return jsonify({"image_url": entries['image_url']}), 200
        else:
            return jsonify({"error": "No image data found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/receive_data', methods=['POST'])
@require_api_key  # This uses your predefined require_api_key decorator
def receive_data():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        ref = db.reference(f'users/{user_id}/food_water_levels')
        ref.push(data)
        return jsonify({"status": "Data successfully received"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload', methods=['POST'])
@require_token
def upload_content():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    content = request.data.decode('utf-8').strip()
    if not content:
        return jsonify({"error": "Empty content received"}), 400

    try:
        key, value = content.split(':', 1)
        key = key.strip().lower()
        value = value.strip().lower()

        ref = db.reference(f'users/{user_id}')
        ref.update({key: value})
    except ValueError:
        return jsonify({"error": "Invalid content format, expected 'key: value'"}), 400

    return jsonify({"status": "success", "message": f"Data updated in Firebase for {key} with value {value}"}), 200


@app.route('/api/upload_picture', methods=['POST'])
@require_token
def upload_pic():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = uploaded_file.filename.lower()

    if filename.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.bmp', '.tiff')):
        try:
            # Upload to Firebase Storage (if configured)
            bucket = storage.bucket()
            blob = bucket.blob(f'images/{user_id}/{filename}')
            blob.upload_from_file(uploaded_file)
            blob.make_public()

            file_url = blob.public_url
            ref = db.reference(f'users/{user_id}')
            ref.update({'image_url': file_url})
        except Exception as e:
            return jsonify({"error": f"Failed to upload image to Firebase: {str(e)}"}), 500
    else:
        return jsonify({"error": "Unsupported file type"}), 400

    return jsonify({"status": "success", "message": f"File {filename} received and processed successfully", "url": file_url}), 200


@app.route('/api/commands', methods=['GET', 'POST'])
@require_token
def handle_commands():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    command_path = os.path.join(COMMANDS_FOLDER, f"{user_id}_{COMMANDS_FILE}")
    if request.method == 'POST':
        data = request.json
        if not data or 'command' not in data:
            return jsonify({"error": "No command provided"}), 400
        command = data['command']
        timestamp = datetime.now().isoformat()
        try:
            with open(command_path, "r") as file:
                commands = json.load(file)
        except FileNotFoundError:
            commands = []
        commands.append({"timestamp": timestamp, "command": command})
        with open(command_path, "w") as file:
            json.dump(commands, file)
        return jsonify({"message": "Command received and written"}), 200
    elif request.method == 'GET':
        last_timestamp = request.args.get('last_timestamp')
        try:
            with open(command_path, "r") as file:
                commands = json.load(file)
            if last_timestamp:
                filtered_commands = [cmd for cmd in commands if cmd['timestamp'] > last_timestamp]
                return jsonify({"commands": filtered_commands}), 200
            return jsonify({"commands": commands}), 200
        except FileNotFoundError:
            commands = []
            with open(command_path, "w") as file:
                json.dump(commands, file)
            return jsonify({"commands": commands}), 200

@app.route('/api/device_status', methods=['GET'])
def get_device_status():
    try:
        ref = db.reference('device_status')
        status = ref.get()
        if status and 'online' in status:
            return jsonify({"online": status['online']}), 200
        else:
            return jsonify({"online": False}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/timer', methods=['GET', 'POST'])
@require_api_key
def handle_timer():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    ref = db.reference(f'users/{user_id}/timer')
    if request.method == 'POST':
        data = request.json
        try:
            ref.set(data)
            return jsonify({"status": "Timer updated successfully"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    elif request.method == 'GET':
        try:
            timer = ref.get()
            if timer:
                return jsonify(timer), 200
            else:
                return jsonify({"error": "No timer data found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
