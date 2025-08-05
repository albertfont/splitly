from event_expenses.extensions import db
from datetime import datetime

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    validated = db.Column(db.Boolean, default=False)
    archived = db.Column(db.Boolean, default=False)
    token = db.Column(db.String(32), unique=True, nullable=True)
    validation_token = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    participants = db.relationship('Participant', backref='event', lazy=True)
    expenses = db.relationship('Expense', backref='event', lazy=True)

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    num_people = db.Column(db.Integer, nullable=False, default=1)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(256), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payer_id = db.Column(db.Integer, db.ForeignKey('participant.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    split_between = db.Column(db.String(512), nullable=False)
    receipt_image = db.Column(db.String(200), nullable=True)

