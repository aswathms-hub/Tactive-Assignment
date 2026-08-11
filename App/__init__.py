import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(config_override=None):
    """
    Application factory for Smart Leave Approval System.
    """
    app = Flask(__name__, instance_relative_config=True)

    default_db_path = os.path.join(app.instance_path, "leave_system.db")
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-key-smart-leave-2026"),
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            "DATABASE_URL", f"sqlite:///{default_db_path}"
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if config_override:
        app.config.update(config_override)

    # Ensure the instance folder exists for SQLite DB
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    db.init_app(app)

    with app.app_context():
        from . import models  # noqa: F401

        db.create_all()

    from .routes import bp

    app.register_blueprint(bp)

    return app
