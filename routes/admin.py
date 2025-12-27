from flask import Blueprint, request, jsonify, session, render_template
from db.db import (
    list_personnel,
    add_personnel,
    set_personnel_availability,
    get_all_requests,
    get_requests_for_block,
    assign_personnel_to_request,
    update_request_status,
    search_requests
)

admin_bp = Blueprint("admin", __name__)


# ---------- helper ----------
def admin_login_required():
    if "user" not in session or session.get("role") != "admin":
        return False
    return True


# ---------- routes ----------

@admin_bp.route("/requests", methods=["GET"])
def all_requests():
    if not admin_login_required():
        return jsonify({"error": "Unauthorized"}), 401

    admin_user = session.get("user") or {}
    block = admin_user.get("Block_name")
    # support server-side filtering via query params
    q = request.args.get('q')
    status = request.args.get('status')

    # if any filter provided, use search_requests which accepts block, q, status
    if q or status:
        return jsonify(search_requests(block_name=block, q=q, status=status))

    # no filters — return block-scoped or all
    if block:
        return jsonify(get_requests_for_block(block))
    return jsonify(get_all_requests())


@admin_bp.route("/personnel", methods=["GET"])
def personnel_list():
    if not admin_login_required():
        return jsonify({"error": "Unauthorized"}), 401

    return jsonify(list_personnel())


@admin_bp.route('/personnel/page', methods=['GET'])
def personnel_page():
    if not admin_login_required():
        return jsonify({"error": "Unauthorized"}), 401
    return render_template('personnel.html')


@admin_bp.route("/personnel", methods=["POST"])
def add_new_personnel():
    if not admin_login_required():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json

    required = ["personnel_id", "name", "email", "contact", "specialization"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    ok, msg = add_personnel(
        data["personnel_id"],
        data["name"],
        data["email"],
        data["contact"],
        data["specialization"]
    )

    if not ok:
        return jsonify({"error": msg}), 500

    return jsonify({"success": True, "message": msg})


@admin_bp.route("/personnel/availability", methods=["POST"])
def change_personnel_availability():
    if not admin_login_required():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json or {}
    personnel_id = data.get("personnel_id")
    available = data.get("available")

    if personnel_id is None or available is None:
        return jsonify({"error": "personnel_id and available required"}), 400

    # normalize boolean
    if isinstance(available, str):
        available = available.lower() in ("1", "true", "yes", "y")

    ok, msg = set_personnel_availability(personnel_id, bool(available))
    if not ok:
        return jsonify({"error": msg}), 500

    return jsonify({"success": True, "message": msg})


@admin_bp.route("/assign", methods=["POST"])
def assign_personnel():
    if not admin_login_required():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    request_id = data.get("request_id")
    personnel_id = data.get("personnel_id")

    if not request_id or not personnel_id:
        return jsonify({"error": "request_id and personnel_id required"}), 400

    ok, msg = assign_personnel_to_request(request_id, personnel_id)

    if not ok:
        return jsonify({"error": msg}), 500

    return jsonify({"success": True, "message": msg})


@admin_bp.route("/status", methods=["POST"])
def update_status():
    if not admin_login_required():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    request_id = data.get("request_id")
    status = data.get("status")
    completion_date = data.get("completion_date")

    if not request_id or not status:
        return jsonify({"error": "request_id and status required"}), 400

    ok, msg = update_request_status(request_id, status, completion_date)

    if not ok:
        return jsonify({"error": msg}), 500

    return jsonify({"success": True, "message": msg})
