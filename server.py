from flask import Flask, request, jsonify, render_template, redirect, session
import json
from functools import wraps
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore, db
import secrets

# Initialize Firebase Admin
cred = credentials.Certificate('/Users/kfout/cse123_test/cse123/cse123-bac2c-firebase-adminsdk-cj30n-c9082dc2a9.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://cse123-bac2c-default-rtdb.firebaseio.com/'
})

firebase_db = db.reference()

# Reference to your database
#ref = db.reference('server/saving-data/fireblog')
#db = firestore.client()
#users_ref = db.collection('users')
#users_ref.add({'username': 'johndoe', 'email': 'johndoe@example.com'})


app = Flask(__name__)
#CORS(app, resources={r"/api/*": {"origins": "https://cse123petfeeder.com"}})
app.secret_key = 'your_secret_key'  # Secret key for session management
CORS(app, resources={r"/*": {"origins": "*"}})  # This will allow all routes


@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')


# Main dashboard page
@app.route('/')
def home():
    if 'api_key' not in session:
        return redirect('/login')
    return render_template('index.html')

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
        if 'api_key' in session and session['api_key'] == request.headers.get('Authorization'):
            return f(*args, **kwargs)
        return jsonify({"message": "Unauthorized"}), 401
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Assume user validation returns True and assigns an API key
        if validate_user(username, password):
            session['api_key'] = 'your_users_api_key'  # Simulated API key
            return redirect('/')
        else:
            return render_template('login.html', error="Invalid credentials")
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

# Registration endpoint
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    api_key = generate_api_key()
    try:
        firebase_db.child('users').child(username).set({
            'password': password,
            'api_key': api_key
        })
        return jsonify(api_key=api_key), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
