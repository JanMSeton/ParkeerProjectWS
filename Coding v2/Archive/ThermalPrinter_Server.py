# OLD CODE!  
from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
from escpos.printer import Usb

# Initialize the thermal printer
p = Usb(0x28e9, 0x0289, 0, 0, 0x81, 3, width=384)

# Create Flask app
app = Flask(__name__)
CORS(app, origins=["http://localhost:5501"])  # Enable CORS for the entire app

# Endpoint to receive answers from P5.js and print them
@app.route('/submit', methods=['POST'])
def submit_answers():
    if request.method == 'OPTIONS':
        # Handle the preflight request
        return '', 200  # No content, just a 200 status
    
    data = request.json  # Get JSON data sent from P5.js
    print(f"Received data: {data}")  # Print received data for debugging

    if not data:
        return jsonify({"status": "failure", "message": "No data received"}), 400

    # Format and print the answers
    p.set(align='center', flip=True, invert=True)
    p.text("Bon van Betekenis\n")
    
    for question, answer in data.items():
        p.text(f"{question}: {answer}\n")

    p.cut()  # Cut the paper
    return jsonify({"status": "success", "message": "Printed successfully!"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Start the Flask server


