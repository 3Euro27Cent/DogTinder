from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# SQLite-Datenbank (du kannst hier auch eine andere DB-URL verwenden)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Vermeidet unnötige Warnungen

db = SQLAlchemy(app)

# Beispiel einer Datenbank-Tabelle
class Hund(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    alter = db.Column(db.Integer, nullable=False)
    rasse = db.Column(db.String(100), nullable=False)
    beschreibung = db.Column(db.Text, nullable=True)

# Datenbanktabellen erstellen (mit Context)
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("✅ Datenbank und Tabellen wurden erstellt!")
