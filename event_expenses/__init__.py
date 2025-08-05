from flask import Flask
from config import Config
from event_expenses.extensions import db, mail
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    mail.init_app(app)

    with app.app_context():
        from event_expenses import models, routes
        db.create_all()

    return app
