import os

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from .config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    new_app = Flask(__name__)
    new_app.config.from_object(Config)

    db.init_app(new_app)
    migrate.init_app(new_app, db)

    from .routes import frontend_bp
    new_app.register_blueprint(frontend_bp)

    return new_app


def main():
    port = int(os.environ.get("ISITDOWN_PORT", 5000))
    app = create_app()
    app.run(host='0.0.0.0', port=port)


if __name__ == "__main__":
    main()
