from flask import Flask, request, jsonify
import json
from functools import wraps
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore, db
import secrets
import os

# Initialize Firebase Admin
cred = credentials.Certificate('/Users/kfout/cse123_test/cse123/cse123-bac2c-firebase-adminsdk-cj30n-c9082dc2a9.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://cse123-bac2c-default-rtdb.firebaseio.com/'
})

firebase_db = db.reference()

UPLOAD_FOLDER_TEXTS = '/Users/kfout/uploads'
COMMANDS_FOLDER = '/Users/kfout/uploads'
COMMANDS_FILE = 'instructions.txt'

# Ensure the necessary folders exist
if not os.path.exists(UPLOAD_FOLDER_TEXTS):
    os.makedirs(UPLOAD_FOLDER_TEXTS)
if not os.path.exists(COMMANDS_FOLDER):
    os.makedirs(COMMANDS_FOLDER)

# Reference to your database
#ref = db.reference('server/saving-data/fireblog')
#db = firestore.client()
#users_ref = db.collection('users')
#users_ref.add({'username': 'johndoe', 'email': 'johndoe@example.com'})


app = Flask(__name__)
#CORS(app, resources={r"/api/*": {"origins": "https://cse123petfeeder.com"}})
CORS(app, resources={r"/*": {"origins": "*"}})  # This will allow all routes


@app.route('/', methods=['GET'])
def home():
    # Serve the HTML file for the homepage
    with open('index.html', 'r') as file:
        return file.read()


@app.route('/api/food_level', methods=['GET'])
def get_food_level():
    try:
        with open('status.json', 'r') as file:
            status = json.load(file)
        return jsonify({"food_level": status.get("food_level", "Unknown")}), 200
    except (FileNotFoundError, json.JSONDecodeError):
        return jsonify({"error": "Status file not found or is empty"}), 404

@app.route('/api/water_level', methods=['GET'])
def get_water_level():
    try:
        with open('status.json', 'r') as file:
            status = json.load(file)
        return jsonify({"water_level": status.get("water_level", "Unknown")}), 200
    except (FileNotFoundError, json.JSONDecodeError):
        return jsonify({"error": "Status file not found or is empty"}), 404

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
        auth_header = request.headers.get('Authorization')
        if auth_header:
            token = auth_header.split(' ')[1]
            if validate_api_key(token):
                return f(*args, **kwargs)
        return jsonify({"message": "Unauthorized"}), 401
    return decorated_function

def validate_api_key(key):
    users_dict = firebase_db.child('users').get()
    if users_dict:
        for user_id, user_info in users_dict.items():
            if user_info.get('api_key') == key:
                return True
    return False

    
@app.route('/api/update_levels', methods=['POST'])
@require_api_key
def update_levels():
    data = request.json
    if not data or 'food_level' not in data or 'water_level' not in data:
        return jsonify({"error": "Invalid data provided"}), 400
    try:
        ref = db.reference('food_water_levels')
        ref.push(data)
        return jsonify({"status": "Data updated in Firebase"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@app.route('/api/get_levels', methods=['GET'])
@require_api_key
def get_levels():
    try:
        ref = db.reference('food_water_levels')
        # Assuming you want to get the latest entry or customize as needed
        data = ref.get()  
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#THIS WILL BE ENDPOINT TO RECEIVE DATA FROM PI
@app.route('/api/receive_data', methods=['POST'])
@require_api_key  # This uses your predefined require_api_key decorator
def receive_data():
    data = request.json  # Get JSON data sent by the hardware
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Process the data here (e.g., save to Firebase)
    # Example of saving to Firebase:
    ref = db.reference('food_water_levels')
    ref.push(data)
    
    return jsonify({"status": "Data successfully received"}), 200

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')  # Ensure this is securely hashed before storage
    api_key = generate_api_key()
    
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    # Attempt to save the user data
    try:
        firebase_db.child('users').child(username).set({
            'password': password,  # This should be a hashed password
            'api_key': api_key
        })
        return jsonify(api_key=api_key), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    user = firebase_db.child('users').child(username).get()
    if user and user.get('password') == data.get('password'):  # Placeholder for password check
        return jsonify(api_key=user.get('api_key')), 200
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Process and append each received line to a file
    file_path = os.path.join(UPLOAD_FOLDER_TEXTS, file.filename)

    # Open the file in append mode, if it doesn't exist it will be created
    with open(file_path, 'a') as f:
        f.write(file.read().decode('utf-8') + '\n')  # Decode as utf-8 and append a newline character

    print(f"Received line for file: {file.filename}")
    return jsonify({"status": "success", "message": f"Line added to file {file.filename} successfully"})

@app.route('/api/commands', methods=['GET', 'POST'])
def handle_commands():
    command_path = os.path.join(COMMANDS_FOLDER, COMMANDS_FILE)
    if request.method == 'POST':
        # Receive and store a command
        data = request.json
        if not data or 'command' not in data:
            return jsonify({"error": "No command provided"}), 400

        command = data['command']
        # Append the command to the instructions file
        with open(command_path, "a") as file:
            file.write(command + "\n")
        return jsonify({"message": "Command received and written"}), 200

    elif request.method == 'GET':
        # Send the current commands to the client
        if os.path.exists(command_path):
            with open(command_path, "r") as file:
                commands = file.read()
            return jsonify({"commands": commands}), 200
        return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    app.run(host='172.20.10.9', port=8080, debug=True)