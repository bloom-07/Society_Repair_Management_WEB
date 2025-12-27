from flask import Blueprint, render_template, session, redirect, url_for

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/")
def home():
    return render_template("home.html")


@pages_bp.route("/login/resident")
def resident_login():
    return render_template("resident_login.html")


@pages_bp.route("/login/admin")
def admin_login():
    return render_template("admin_login.html")


@pages_bp.route("/resident")
def resident_dashboard():
    if "user" not in session or session.get("role") != "resident":
        return redirect(url_for("pages.home"))
    return render_template("resident_dashboard.html", user=session["user"])


@pages_bp.route("/admin")
def admin_dashboard():
    if "user" not in session or session.get("role") != "admin":
        return redirect(url_for("pages.home"))
    return render_template("admin_dashboard.html", user=session["user"])


@pages_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("pages.home"))

@pages_bp.route("/register/resident")
def resident_register():
    return render_template("resident_register.html")