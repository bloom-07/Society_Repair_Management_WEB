from flask import Blueprint, request, jsonify, session
from db.db import register_resident, verify_resident_login, verify_admin_login

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    user_id = data.get("id")
    password = data.get("password")
    role = data.get("role")

    if role == "resident":
        user = verify_resident_login(user_id, password)
    elif role == "admin":
        user = verify_admin_login(user_id, password)
    else:
        return jsonify({"error": "Invalid role"}), 400

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    session["user"] = user
    session["role"] = role

    return jsonify({"success": True, "user": user})

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json

    ok, msg = register_resident(
        data["resident_id"],
        data["name"],
        data["email"],
        data["contact"],
        data["block"],
        data["flat_no"],
        data["password"]
    )

    if not ok:
        return jsonify({"error": msg}), 400

    return jsonify({"success": True})

@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})