from event_expenses import create_app
from event_expenses.extensions import db

app = create_app()

with app.app_context():
    db.create_all()
    print("Base de dades inicialitzada correctament.")
