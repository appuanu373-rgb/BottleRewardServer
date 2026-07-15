from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, db
import json

app = Flask(__name__)

# -----------------------------
# Firebase Initialization
# -----------------------------
cred = credentials.Certificate("firebase_key.json")

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://smartbottlereward-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

# -----------------------------
# Home Page
# -----------------------------
@app.route('/')
def home():
    return "Bottle Reward Server Running!"

# -----------------------------
# Reward API
# -----------------------------
@app.route('/reward', methods=['POST'])
def reward():

    # Read JSON or Plain Text
    data = request.get_json(silent=True)

    if data is None:
        try:
            data = json.loads(request.get_data(as_text=True))
        except:
            return jsonify({
                "success": False,
                "message": "Invalid data format"
            }), 400

    email = data.get("email")
    qr = data.get("qr")

    if not email:
        return jsonify({
            "success": False,
            "message": "Email missing"
        })

    if not qr:
        return jsonify({
            "success": False,
            "message": "QR missing"
        })

    print("--------------------------------")
    print("User :", email)
    print("QR   :", qr)
    print("--------------------------------")

    # -----------------------------
    # Check if QR already used
    # -----------------------------
    qr_ref = db.reference("UsedQR/" + qr)

    if qr_ref.get():
        return jsonify({
            "success": False,
            "message": "QR Code Already Used!"
        })

    # -----------------------------
    # Get User
    # -----------------------------
    user_ref = db.reference("Users/" + email.replace(".", "_"))

    user = user_ref.get()

    if user is None:
        user = {
            "points": 0
        }

    # -----------------------------
    # Add 10 Points
    # -----------------------------
    points = user.get("points", 0)
    points = points + 10

    # -----------------------------
    # Save Points
    # -----------------------------
    user_ref.update({
        "points": points
    })

    # -----------------------------
    # Save Used QR
    # -----------------------------
    qr_ref.set({
        "email": email
    })

    print("New Points :", points)

    # -----------------------------
    # Return Response
    # -----------------------------
    return jsonify({
        "success": True,
        "message": "Reward Added Successfully",
        "points": points
    })


# -----------------------------
# Run Server
# -----------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)