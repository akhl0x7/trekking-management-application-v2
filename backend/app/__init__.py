import os
from pathlib import Path

from flask import Flask

from .config import Config
from .extensions import db
from .models import User, UserRole, UserStatus
from .api.auth import bp as auth_bp
from .api.public import bp as public_bp
from .api.admin import bp as admin_bp
from .api.staff import bp as staff_bp
from .api.trekker import bp as trekker_bp
from .tasks import init_tasks


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    Path(app.instance_path, "exports").mkdir(parents=True, exist_ok=True)
    Path(app.instance_path, "reports").mkdir(parents=True, exist_ok=True)
    db.init_app(app)
    init_tasks(app)

    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(public_bp, url_prefix="/api/v1")
    app.register_blueprint(admin_bp, url_prefix="/api/v1/admin")
    app.register_blueprint(staff_bp, url_prefix="/api/v1/staff")
    app.register_blueprint(trekker_bp, url_prefix="/api/v1/trekker")

    @app.errorhandler(PermissionError)
    def permission_error(error):
        from flask import jsonify
        return jsonify({"data": None, "error": {"code": "FORBIDDEN", "message": str(error)}}), 403

    @app.cli.command("init-db")
    def init_db_command():
        with app.app_context():
            db.create_all()
        print("Database initialized.")

    @app.cli.command("seed")
    def seed_command():
        from .seed import seed
        seed(app)
        print("Seed data created.")

    return app
