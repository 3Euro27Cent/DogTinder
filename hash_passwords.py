from app import app, db, User
from werkzeug.security import generate_password_hash

usernames_to_hash = ['1', '2']  # nur diese User

with app.app_context():
    for username in usernames_to_hash:
        user = User.query.filter_by(username=username).first()
        if user:
            if not user.password.startswith('pbkdf2:sha256'):
                user.password = generate_password_hash(user.password)
                print(f"Passwort von {username} gehashed.")
            else:
                print(f"Passwort von {username} ist schon gehashed.")
        else:
            print(f"User {username} nicht gefunden.")
    db.session.commit()
    print("Fertig.")
