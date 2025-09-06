# routes.py
from flask import Blueprint, request, jsonify
import qrng, os

api = Blueprint("api", __name__)

SECRET_API_KEY = os.getenv("SECRET_API_KEY", None)

def check_api_key():
    """Check if request has valid API key in header."""
    key = request.headers.get("x-api-key")
    return SECRET_API_KEY and key == SECRET_API_KEY

@api.route("/random-bits", methods=["GET"])
def random_bits():
    if not check_api_key():
        return jsonify({"status": "error", "message": "Invalid or missing API key"}), 401
    length = int(request.args.get("length", 8))
    bits = qrng.get_random_bits(length)
    return jsonify({"status": "success", "bits": bits})

@api.route("/random-int", methods=["GET"])
def random_int():
    if not check_api_key():
        return jsonify({"status": "error", "message": "Invalid or missing API key"}), 401
    min_val = int(request.args.get("min", 0))
    max_val = int(request.args.get("max", 100))
    value = qrng.get_random_int(min_val, max_val)
    return jsonify({"status": "success", "random_int": value, "range": [min_val, max_val]})

@api.route("/random-float", methods=["GET"])
def random_float():
    if not check_api_key():
        return jsonify({"status": "error", "message": "Invalid or missing API key"}), 401
    min_val = float(request.args.get("min", 0.0))
    max_val = float(request.args.get("max", 1.0))
    value = qrng.get_random_float(min_val, max_val)
    return jsonify({"status": "success", "random_float": value, "range": [min_val, max_val]})


# http://127.0.0.1:5000/api/random-float?min=0&max=5.
# http://127.0.0.1:5000/api/random-bits?length=8"
# http://127.0.0.1:5000/api/random-int?min=1&max=10
