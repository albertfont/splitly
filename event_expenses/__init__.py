from flask import Flask
from config import Config
from event_expenses.extensions import db, mail

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    mail.init_app(app)

    with app.app_context():
        from event_expenses import models, routes
        db.create_all()

    return app
