from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    # Serve the HTML file for the homepage
    with open('index.html', 'r') as file:
        return file.read()

@app.route('/api/receive_data', methods=['POST'])
def receive_data():
    data = request.json  # Get JSON data sent by the hardware
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Assuming data contains keys 'food_level' and 'water_level'
    with open('status.json', 'w') as file:
        json.dump(data, file)

    return jsonify({"status": "Data successfully received"}), 200

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
