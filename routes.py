# # routes.py
# from flask import Blueprint, request, jsonify
# import qrng, os

# api = Blueprint("api", __name__)

# SECRET_API_KEY = os.getenv("SECRET_API_KEY", None)

# def check_api_key():
#     """Check if request has valid API key in header."""
#     key = request.headers.get("x-api-key")
#     return SECRET_API_KEY and key == SECRET_API_KEY

# @api.route("/random-bits", methods=["GET"])
# def random_bits():
#     if not check_api_key():
#         return jsonify({"status": "error", "message": "Invalid or missing API key"}), 401
#     length = int(request.args.get("length", 8))
#     bits = qrng.get_random_bits(length)
#     return jsonify({"status": "success", "bits": bits})

# @api.route("/random-int", methods=["GET"])
# def random_int():
#     if not check_api_key():
#         return jsonify({"status": "error", "message": "Invalid or missing API key"}), 401
#     min_val = int(request.args.get("min", 0))
#     max_val = int(request.args.get("max", 100))
#     value = qrng.get_random_int(min_val, max_val)
#     return jsonify({"status": "success", "random_int": value, "range": [min_val, max_val]})

# @api.route("/random-float", methods=["GET"])
# def random_float():
#     if not check_api_key():
#         return jsonify({"status": "error", "message": "Invalid or missing API key"}), 401
#     min_val = float(request.args.get("min", 0.0))
#     max_val = float(request.args.get("max", 1.0))
#     value = qrng.get_random_float(min_val, max_val)
#     return jsonify({"status": "success", "random_float": value, "range": [min_val, max_val]})


# # http://127.0.0.1:5000/api/random-float?min=0&max=5.
# # http://127.0.0.1:5000/api/random-bits?length=8"
# # http://127.0.0.1:5000/api/random-int?min=1&max=10



# routes.py
from flask import Blueprint, request, jsonify
import qrng, os
from qiskit import QuantumCircuit, Aer, execute
import numpy as np
import string
import secrets
import hmac
import hashlib
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import io
import base64

app = Flask(__name__)
api = Blueprint("api", __name__)

SECRET_API_KEY = os.getenv("SECRET_API_KEY","12345-ABCDE" )

# In-memory stores (in production, use Redis or database)
captcha_store = {}
otp_store = {}

def check_api_key():
    """Check if request has valid API key in header."""
    key = request.headers.get("x-api-key")
    return SECRET_API_KEY and key == SECRET_API_KEY

def quantum_random_bit() -> int:
    """Generate a single random bit using quantum computer."""
    # Create a quantum circuit with 1 qubit and 1 classical bit
    qc = QuantumCircuit(1, 1)
    qc.h(0)  # Apply Hadamard gate to create superposition
    qc.measure(0, 0)  # Measure the qubit
    
    # Execute the circuit on a quantum simulator
    simulator = Aer.get_backend('qasm_simulator')
    result = execute(qc, simulator, shots=1).result()
    counts = result.get_counts()
    return int(list(counts.keys())[0])

def quantum_random_int(min_val: int, max_val: int) -> int:
    """Generate a random integer within specified range using quantum randomness."""
    range_size = max_val - min_val + 1
    bits_needed = range_size.bit_length()
    
    while True:
        # Generate enough random bits
        random_bits = ''.join(str(quantum_random_bit()) for _ in range(bits_needed))
        random_num = int(random_bits, 2)
        
        # Check if within range
        if random_num < range_size:
            return min_val + random_num

def quantum_random_float(min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Generate a random float using quantum randomness."""
    # Generate enough random bits for good precision
    bits = 32
    random_bits = ''.join(str(quantum_random_bit()) for _ in range(bits))
    random_int = int(random_bits, 2)
    
    # Convert to float in [0.0, 1.0)
    random_float = random_int / (2 ** bits)
    
    # Scale to desired range
    return min_val + random_float * (max_val - min_val)

def quantum_random_string(length: int) -> str:
    """Generate a random string of specified length using quantum randomness."""
    chars = string.ascii_letters + string.digits
    return ''.join(chars[quantum_random_int(0, len(chars)-1)] for _ in range(length))

def generate_secure_password(length: int = 12, 
                           use_uppercase: bool = True,
                           use_lowercase: bool = True,
                           use_digits: bool = True,
                           use_special: bool = True) -> str:
    """Generate a cryptographically secure password using quantum randomness."""
    if length < 8:
        raise ValueError("Password length must be at least 8 characters")
    
    char_pool = ""
    if use_uppercase:
        char_pool += string.ascii_uppercase
    if use_lowercase:
        char_pool += string.ascii_lowercase
    if use_digits:
        char_pool += string.digits
    if use_special:
        char_pool += "!@#$%^&*"
    
    if not char_pool:
        raise ValueError("At least one character type must be selected")
    
    while True:
        password = ''.join(char_pool[quantum_random_int(0, len(char_pool)-1)] 
                          for _ in range(length))
        if (use_uppercase and any(c.isupper() for c in password) and
            use_lowercase and any(c.islower() for c in password) and
            use_digits and any(c.isdigit() for c in password) and
            use_special and any(c in "!@#$%^&*" for c in password)):
            return password

def generate_captcha(length: int = 6, width: int = 200, height: int = 80) -> tuple:
    """Generate a secure CAPTCHA with quantum randomness."""
    # Generate random CAPTCHA text using quantum randomness
    captcha_text = quantum_random_string(length)
    
    # Generate salt and create hash
    salt = secrets.token_hex(8)
    captcha_hash = hmac.new(
        salt.encode(),
        captcha_text.lower().encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Create image
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Try to use a font, fall back to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    # Draw text with random position and rotation using quantum randomness
    x = 10
    for char in captcha_text:
        y = int(quantum_random_float(0.1, 0.7) * (height - 40))
        angle = int(quantum_random_float(-0.5, 0.5) * 60)  # -30 to 30 degrees
        draw.text((x, y), char, font=font, fill='black')
        x += int(quantum_random_float(0.6, 0.8) * 50) + 30  # 30 to 80 pixels
    
    # Add noise lines using quantum randomness
    for _ in range(5):
        x1 = int(quantum_random_float(0, 1) * width)
        y1 = int(quantum_random_float(0, 1) * height)
        x2 = int(quantum_random_float(0, 1) * width)
        y2 = int(quantum_random_float(0, 1) * height)
        draw.line([(x1, y1), (x2, y2)], fill='gray')
    
    # Convert to base64
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    image_b64 = base64.b64encode(buffer.getvalue()).decode()
    
    # Generate verification token using quantum randomness
    verification_token = quantum_random_string(16)
    
    return image_b64, verification_token, captcha_hash, salt

def generate_otp(length: int = 6) -> tuple:
    """Generate a secure 6-digit OTP using quantum randomness."""
    if length < 4 or length > 8:
        raise ValueError("OTP length must be between 4 and 8 digits")
    
    # Generate OTP using quantum randomness
    otp = ''.join(str(quantum_random_int(0, 9)) for _ in range(length))
    
    # Generate salt and create hash
    salt = secrets.token_hex(8)
    otp_hash = hmac.new(
        salt.encode(),
        otp.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Set expiration (5 minutes from now)
    expires_at = datetime.utcnow() + timedelta(minutes=5)
    
    return otp, otp_hash, salt, expires_at

# API Routes
@api.route("/random-bits", methods=["GET"])
def random_bits():
    if not check_api_key():
        return jsonify({"status": "error", "message": "Invalid or missing API key"}), 401
    length = int(request.args.get("length", 8))
    bits = [quantum_random_bit() for _ in range(length)]
    return jsonify({"status": "success", "bits": bits})

@api.route("/random-int", methods=["GET"])
def random_int():
    if not check_api_key():
        return jsonify({"status": "error", "message": "Invalid or missing API key"}), 401
    min_val = int(request.args.get("min", 0))
    max_val = int(request.args.get("max", 100))
    value = quantum_random_int(min_val, max_val)
    return jsonify({"status": "success", "random_int": value, "range": [min_val, max_val]})

@api.route("/random-float", methods=["GET"])
def random_float():
    if not check_api_key():
        return jsonify({"status": "error", "message": "Invalid or missing API key"}), 401
    min_val = float(request.args.get("min", 0.0))
    max_val = float(request.args.get("max", 1.0))
    value = quantum_random_float(min_val, max_val)
    return jsonify({"status": "success", "random_float": value, "range": [min_val, max_val]})

@api.route("/generate-password", methods=["POST"])
def generate_password():
    if not check_api_key():
        return jsonify({"status": "error", "message": "Invalid or missing API key"}), 401
    
    try:
        data = request.get_json()
        length = data.get('length', 12)
        password = generate_secure_password(length)
        return jsonify({
            "status": "success",
            "password": password
        })
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@api.route("/generate-captcha", methods=["POST"])
def generate_captcha_route():
    if not check_api_key():
        return jsonify({"status": "error", "message": "Invalid or missing API key"}), 401
    
    try:
        data = request.get_json()
        length = data.get('length', 6)
        width = data.get('width', 200)
        height = data.get('height', 80)
        
        image_b64, token, captcha_hash, salt = generate_captcha(length, width, height)
        
        # Store verification data
        captcha_store[token] = {
            'hash': captcha_hash,
            'salt': salt,
            'expires_at': datetime.utcnow() + timedelta(minutes=5)
        }
        
        return jsonify({
            "status": "success",
            "image": image_b64,
            "token": token
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@api.route("/verify-captcha", methods=["POST"])
def verify_captcha_route():
    if not check_api_key():
        return jsonify({"status": "error", "message": "Invalid or missing API key"}), 401
    
    try:
        data = request.get_json()
        token = data.get('token')
        user_input = data.get('input')
        
        if not token or not user_input:
            return jsonify({"status": "error", "message": "Missing token or input"}), 400
        
        stored_data = captcha_store.get(token)
        if not stored_data:
            return jsonify({"status": "error", "message": "Invalid or expired token"}), 400
        
        if datetime.utcnow() > stored_data['expires_at']:
            del captcha_store[token]
            return jsonify({"status": "error", "message": "Token expired"}), 400
        
        input_hash = hmac.new(
            stored_data['salt'].encode(),
            user_input.lower().encode(),
            hashlib.sha256
        ).hexdigest()
        
        if hmac.compare_digest(input_hash, stored_data['hash']):
            del captcha_store[token]
            return jsonify({"status": "success", "message": "CAPTCHA verified"})
        else:
            return jsonify({"status": "error", "message": "Invalid CAPTCHA"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@api.route("/generate-otp", methods=["POST"])
def generate_otp_route():
    if not check_api_key():
        return jsonify({"status": "error", "message": "Invalid or missing API key"}), 401
    
    try:
        otp, otp_hash, salt, expires_at = generate_otp()
        
        # Store OTP data
        otp_store[otp] = {
            'hash': otp_hash,
            'salt': salt,
            'expires_at': expires_at
        }
        
        return jsonify({
            "status": "success",
            "otp": otp,
            "expires_at": expires_at.isoformat()
        })
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@api.route("/verify-otp", methods=["POST"])
def verify_otp_route():
    if not check_api_key():
        return jsonify({"status": "error", "message": "Invalid or missing API key"}), 401
    
    try:
        data = request.get_json()
        otp = data.get('otp')
        user_input = data.get('input')
        
        if not otp or not user_input:
            return jsonify({"status": "error", "message": "Missing OTP or input"}), 400
        
        stored_data = otp_store.get(otp)
        if not stored_data:
            return jsonify({"status": "error", "message": "Invalid or expired OTP"}), 400
        
        if datetime.utcnow() > stored_data['expires_at']:
            del otp_store[otp]
            return jsonify({"status": "error", "message": "OTP expired"}), 400
        
        input_hash = hmac.new(
            stored_data['salt'].encode(),
            user_input.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if hmac.compare_digest(input_hash, stored_data['hash']):
            del otp_store[otp]
            return jsonify({"status": "success", "message": "OTP verified"})
        else:
            return jsonify({"status": "error", "message": "Invalid OTP"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
