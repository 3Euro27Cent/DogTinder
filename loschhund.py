from app import app, db, Dog  # Annahme: dein Flask-App-Paket heißt app.py
with app.app_context():
    # Hund mit ID 1 laden
    hund = db.session.get(Dog, 6)

    if hund:
        db.session.delete(hund)
        db.session.commit()
        print("Hund gelöscht.")
    else:
        print("Hund nicht gefunden.")
