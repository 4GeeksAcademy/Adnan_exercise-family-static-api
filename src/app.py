"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from utils import APIException, generate_sitemap
from datastructures import FamilyStructure

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

# Create the jackson family object
jackson_family = FamilyStructure("Jackson")


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


# Generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


# 1) GET /members -> must return a LIST
@app.route('/members', methods=['GET'])
def get_all_members():
    members = jackson_family.get_all_members()
    return jsonify(members), 200


# 2) GET /members/<id> -> must return ONLY these keys:
# [first_name, id, age, lucky_numbers]
@app.route('/members/<int:member_id>', methods=['GET'])
def get_one_member(member_id):
    member = jackson_family.get_member(member_id)
    if member is None:
        return jsonify({"error": "Member not found"}), 404

    cleaned_member = {
        "id": member["id"],
        "first_name": member["first_name"],
        "age": member["age"],
        "lucky_numbers": member["lucky_numbers"]
    }
    return jsonify(cleaned_member), 200


# 3) POST /members
@app.route('/members', methods=['POST'])
def create_member():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Malformed JSON"}), 400

    first_name = data.get("first_name")
    age = data.get("age")
    lucky_numbers = data.get("lucky_numbers")

    if not isinstance(first_name, str) or not first_name.strip():
        return jsonify({"error": "first_name is required"}), 400

    try:
        age = int(age)
    except (TypeError, ValueError):
        return jsonify({"error": "age must be an integer"}), 400

    if age <= 0:
        return jsonify({"error": "age must be > 0"}), 400

    if not isinstance(lucky_numbers, list):
        return jsonify({"error": "lucky_numbers must be a list"}), 400

    # ensure lucky_numbers are ints
    cleaned_lucky_numbers = []
    for n in lucky_numbers:
        try:
            cleaned_lucky_numbers.append(int(n))
        except (TypeError, ValueError):
            return jsonify({"error": "lucky_numbers must contain only integers"}), 400

    created = jackson_family.add_member({
        "first_name": first_name.strip(),
        "age": age,
        "lucky_numbers": cleaned_lucky_numbers
    })

    return jsonify(created), 200


# 4) DELETE /members/<id>
@app.route('/members/<int:member_id>', methods=['DELETE'])
def remove_member(member_id):
    deleted = jackson_family.delete_member(member_id)
    if not deleted:
        return jsonify({"error": "Member not found"}), 404
    return jsonify({"done": True}), 200


# This only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
