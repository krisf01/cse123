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
from datetime import datetime

from datetime import datetime

# Initialize Firebase Admin
cred = credentials.Certificate('/Users/sriharshamaddala/cse123github/cse123/cse123-bac2c-firebase-adminsdk-cj30n-c9082dc2a9.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://cse123-bac2c-default-rtdb.firebaseio.com/'
})

firebase_db = db.reference()

# Directory where the files will be written and saved
UPLOAD_FOLDER_TEXTS = '/Users/sriharshamaddala/storage/text'
UPLOAD_FOLDER_IMAGES = '/Users/sriharshamaddala/storage/images'
COMMANDS_FOLDER = '/Users/sriharshamaddala/uploads'
COMMANDS_FILE = 'instructions.json'

DATA_TEXT_FILE = 'data.txt'

# Ensure the necessary folders exist
if not os.path.exists(UPLOAD_FOLDER_TEXTS):
    os.makedirs(UPLOAD_FOLDER_TEXTS)
if not os.path.exists(COMMANDS_FOLDER):
    os.makedirs(COMMANDS_FOLDER)

if not os.path.exists(DATA_TEXT_FILE):
    with open(DATA_TEXT_FILE, 'w') as file:
        json.dump([], file)

if not os.path.exists(UPLOAD_FOLDER_IMAGES):
    os.makedirs(UPLOAD_FOLDER_IMAGES)

# Reference to your database
#ref = db.reference('server/saving-data/fireblog')
#db = firestore.client()
#users_ref = db.collection('users')
#users_ref.add({'username': 'johndoe', 'email': 'johndoe@example.com'})

def validate_token(auth_token):
    expected_token = "AuPvJrbUlcueojGQLNE6RA"  # This should ideally be stored securely or generated dynamically
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
#CORS(app, resources={r"/api/*": {"origins": "https://cse123petfeeder.com"}})
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


# @app.route('/api/food_level', methods=['GET'])
# def get_food_level():
#     try:
#         with open('status.json', 'r') as file:
#             status = json.load(file)
#         return jsonify({"food_level": status.get("food_level", "Unknown")}), 200
#     except (FileNotFoundError, json.JSONDecodeError):
#         return jsonify({"error": "Status file not found or is empty"}), 404



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

# @app.route('/api/food_level', methods=['GET'])
# def get_food_level():
#     try:
#         # Fetch all entries from Firebase under the specified node
#         ref = db.reference('users/cse123petfeeder')
#         entries = ref.get()
        
#         # Check if entries exist
#         if entries:
#             # Iterate over each entry
#             for entry_key, entry_value in entries.items():
#                 # Check if 'food_level' exists in this entry
#                 if 'food_level' in entry_value:
#                     # Return the first entry that has 'food_level'
#                     return jsonify({"food_level": entry_value['food_level']}), 200
            
#             # If no entries have 'food_level'
#             return jsonify({"error": "No food level data found"}), 404
#         else:
#             return jsonify({"error": "No data found"}), 404
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


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
    
#for the water level
# @app.route('/api/water_level', methods=['GET'])
# def get_water_level():
#     try:
#         # Fetch all entries from Firebase under the specified node
#         ref = db.reference('users/cse123petfeeder')
#         entries = ref.get()
        
#         # Check if entries exist
#         if entries:
#             # Iterate over each entry
#             for entry_key, entry_value in entries.items():
#                 # Check if 'food_level' exists in this entry
#                 if 'water_level' in entry_value:
#                     # Return the first entry that has 'food_level'
#                     return jsonify({"water_level": entry_value['water_level']}), 200
            
#             # If no entries have 'food_level'
#             return jsonify({"error": "No water level data found"}), 404
#         else:
#             return jsonify({"error": "No data found"}), 404
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# @app.route('/api/water_level', methods=['GET'])
# def get_water_level():
#     try:
#         with open('status.json', 'r') as file:
#             status = json.load(file)
#         return jsonify({"water_level": status.get("water_level", "Unknown")}), 200
#     except (FileNotFoundError, json.JSONDecodeError):
#         return jsonify({"error": "Status file not found or is empty"}), 404

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

# def require_api_key(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if 'api_key' in session and session['api_key'] == request.headers.get('Authorization'):
#             return f(*args, **kwargs)
#         return jsonify({"message": "Unauthorized"}), 401
#     return decorated_function

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
    data = request.json
    try:
        ref = firebase_db.child('food_water_levels')
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
    
@app.route('/api/live_feed', methods=['GET'])
def get_pic():
    try:
        ref = db.reference('users/cse123petfeeder')
        entries = ref.get()
        
        if entries:
            # Directly checking if 'food_level' is in the dictionary, as it seems there's only one entry
            if 'image_url' in entries:
                return jsonify({"image_url": entries['image_url']}), 200
            else:
                return jsonify({"error": "No image data found"}), 404
        else:
            return jsonify({"error": "No data found"}), 404
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
    
    return jsonify({"status": "Data successfully received"}), 20

@app.route('/api/upload', methods=['POST'])
def upload_content():
    # Assuming content is sent as plain text in the body
    content = request.data.decode('utf-8').strip()
    if not content:
        return jsonify({"error": "Empty content received"}), 400

    try:
        # Extract key and value from the content
        key, value = content.split(':', 1)
        key = key.strip().lower()  # e.g., 'food_level'
        value = value.strip().lower()  # e.g., 'low'

        # Update Firebase database
        ref = db.reference('users/cse123petfeeder')
        ref.update({key: value})

    except ValueError:
        return jsonify({"error": "Invalid content format, expected 'key: value'"}), 400

    print(f"Processed content: {content}")
    return jsonify({"status": "success", "message": f"Data updated in Firebase for {key} with value {value}"})

@app.route('/api/upload_picture', methods=['POST'])
def upload_pic():
   if 'file' not in request.files:
       return jsonify({"error": "No file part"}), 400
   uploaded_file = request.files['file']
   if uploaded_file.filename == '':
       return jsonify({"error": "No selected file"}), 400

   filename = uploaded_file.filename.lower()

   if filename.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.bmp', '.tiff')):
       file_path = os.path.join(UPLOAD_FOLDER_IMAGES, filename)
       try:
           with open(file_path, 'wb') as f:
               f.write(uploaded_file.read())
       except Exception as e:
           return jsonify({"error": f"Failed to save image: {str(e)}"}), 500


   else:
       return jsonify({"error": "Unsupported file type"}), 400


   print(f"Received file: {filename}, processed successfully.")
   return jsonify({"status": "success", "message": f"File {filename} received and processed successfully"})



# @app.route('/api/upload', methods=['POST'])
# @require_token
# def upload_file():
#     if 'file' not in request.files:
#         return jsonify({"error": "No file part"}), 400
#     uploaded_file = request.files['file']
#     if uploaded_file.filename == '':
#         return jsonify({"error": "No selected file"}), 400

#     filename = uploaded_file.filename.lower()
#     if filename.endswith('test.txt'):
#         try:
#             file_content = uploaded_file.read().decode('utf-8').strip()
#             if not file_content:
#                 return jsonify({"error": "No content found in the uploaded file"}), 400

#             # Assuming the content is like 'food_level: low'
#             key, value = file_content.split(':', 1)
#             key = key.strip().lower()  # e.g., 'food_level'
#             value = value.strip().lower()  # e.g., 'low'

#             ref = firebase_db.child(f'users/cse123petfeeder')

#             # Update the specific field
#             ref.update({key: value})

#         except UnicodeDecodeError:
#             return jsonify({"error": "Invalid text encoding"}), 400
#         except Exception as e:
#             app.logger.error('Failed to update Firebase: %s', str(e))
#             return jsonify({"error": str(e)}), 500

#     elif filename.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.bmp', '.tiff')):
#         file_path = os.path.join(UPLOAD_FOLDER_IMAGES, filename)
#         try:
#             with open(file_path, 'wb') as f:
#                 f.write(uploaded_file.read())
#         except Exception as e:
#             app.logger.error('Failed to save image: %s', str(e))
#             return jsonify({"error": str(e)}), 500

#     else:
#         return jsonify({"error": "Unsupported file type"}), 400

#     return jsonify({"status": "success", "message": f"File {filename} received and processed successfully"})

# @app.route('/api/upload', methods=['POST'])
# @require_token
# def upload_file():
#     if 'file' not in request.files:
#         return jsonify({"error": "No file part"}), 400
#     uploaded_file = request.files['file']
#     if uploaded_file.filename == '':
#         return jsonify({"error": "No selected file"}), 400

#     filename = uploaded_file.filename.lower()
#     if filename == 'data.json':
#         try:
#             file_content = json.loads(uploaded_file.read().decode('utf-8'))

#             # Reference to your Firebase database where you want to update data
#             ref = db.reference('users/cse123petfeeder')

#             # Iterate through each item in the JSON and update Firebase accordingly
#             for item in file_content:
#                 content_type = item['content'].split(' ')[0].lower()  # 'water' or 'food'
#                 level = item['content'].split(' ')[2].lower()  # 'high' or 'low'
#                 if content_type in ['water', 'food']:
#                     ref.update({
#                         f"{content_type}_level": level,
#                         f"{content_type}_timestamp": item['timestamp']
#                     })

#         except json.JSONDecodeError:
#             return jsonify({"error": "Invalid JSON file"}), 400
#         except Exception as e:
#             return jsonify({"error": str(e)}), 500

#     elif filename.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.bmp', '.tiff')):
#         file_path = os.path.join(UPLOAD_FOLDER_IMAGES, filename)
#         try:
#             with open(file_path, 'wb') as f:
#                 f.write(uploaded_file.read())
#         except Exception as e:
#             return jsonify({"error": f"Failed to save image: {str(e)}"}), 500

#     else:
#         return jsonify({"error": "Unsupported file type"}), 400

#     print(f"Received file: {filename}, processed successfully.")
#     return jsonify({"status": "success", "message": f"File {filename} received and processed successfully"})


# @app.route('/api/upload', methods=['POST'])
# @require_token
# def upload_file():
#     if 'file' not in request.files:
#         return jsonify({"error": "No file part"}), 400
#     uploaded_file = request.files['file']
#     if uploaded_file.filename == '':
#         return jsonify({"error": "No selected file"}), 400

#     filename = uploaded_file.filename.lower()
#     if filename == 'data.json':
#         # Process as JSON file
#         try:
#             file_content = json.loads(uploaded_file.read().decode('utf-8'))

#             # Reference to your Firebase database where you want to update data
#             ref = db.reference('users/cse123petfeeder')  # Update this path as needed

#             # Update data in Firebase
#             ref.update(file_content)

#             # Optionally, save the file locally
#             with open(DATA_JSON_FILE, 'w') as file:
#                 json.dump(file_content, file, indent=4)

#         except json.JSONDecodeError:
#             return jsonify({"error": "Invalid JSON file"}), 400
#         except Exception as e:
#             return jsonify({"error": str(e)}), 500

#     elif filename.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.bmp', '.tiff')):
#         file_path = os.path.join(UPLOAD_FOLDER_IMAGES, filename)
#         # Process as a binary file
#         try:
#             with open(file_path, 'wb') as f:
#                 f.write(uploaded_file.read())
#         except Exception as e:
#             return jsonify({"error": f"Failed to save image: {str(e)}"}), 500

#     else:
#         return jsonify({"error": "Unsupported file type"}), 400

#     print(f"Received file: {filename}, processed successfully.")
#     return jsonify({"status": "success", "message": f"File {filename} received and processed successfully"})


@app.route('/api/commands', methods=['GET', 'POST'])
def handle_commands():
    command_path = os.path.join(COMMANDS_FOLDER, COMMANDS_FILE)
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
            commands = []  # Create an empty list if file not found
            with open(command_path, "w") as file:
                json.dump(commands, file)  # Create the file
            return jsonify({"commands": commands}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)