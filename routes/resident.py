from flask import Blueprint, request, jsonify, session
from db.db import (
    create_repair_request,
    get_connection,
    get_requests_for_resident,
    list_personnel,
    request_id_exists
)
from datetime import datetime
import random
import string

resident_bp = Blueprint("resident", __name__)


# ---------- helper ----------
def generate_request_id():
    while True:
        # Generate RQ + 6 digits
        rid = "RQ" + "".join(random.choices("0123456789", k=6))

        # Check DB uniqueness
        if not request_id_exists(rid):
            return rid


def login_required():
    if "user" not in session or session.get("role") != "resident":
        return False
    return True


# ---------- routes ----------

@resident_bp.route("/request", methods=["POST"])
def raise_request():
    if not login_required():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    issue = data.get("issue")

    if not issue:
        return jsonify({"error": "Issue description required"}), 400

    resident_id = session["user"]["Resident_ID"]
    request_id = generate_request_id()

    ok, msg = create_repair_request(request_id, resident_id, issue)

    if not ok:
        return jsonify({"error": msg}), 500

    return jsonify({
        "success": True,
        "request_id": request_id,
        "message": msg
    })


@resident_bp.route("/requests", methods=["GET"])
def my_requests():
    if not login_required():
        return jsonify({"error": "Unauthorized"}), 401

    resident_id = session["user"]["Resident_ID"]
    rows = get_requests_for_resident(resident_id)

    return jsonify(rows)


@resident_bp.route("/personnel", methods=["GET"])
def view_personnel():
    if not login_required():
        return jsonify({"error": "Unauthorized"}), 401

    return jsonify(list_personnel())
