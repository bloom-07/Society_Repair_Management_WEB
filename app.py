from flask import Flask, jsonify
from config import SECRET_KEY, DEBUG
from db.__init__ import initialize_database

from routes.pages import pages_bp
from routes.auth import auth_bp
from routes.resident import resident_bp
from routes.admin import admin_bp


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["DEBUG"] = DEBUG

    # register blueprints
    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(resident_bp, url_prefix="/resident")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"})

    return app


if __name__ == "__main__":
    initialize_database()
    app = create_app()
    app.run()
