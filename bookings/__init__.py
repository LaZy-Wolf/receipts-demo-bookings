from datetime import datetime, timezone

from flask import Flask

from . import db
from .api import bp


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(
        DATABASE="bookings.sqlite3",
        CLOCK=lambda: datetime.now(timezone.utc),
    )
    app.config.update(config or {})
    db.init_app(app)
    app.register_blueprint(bp)
    return app
