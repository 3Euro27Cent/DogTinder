from app import app, User

with app.app_context():
    for u in User.query.all():
        print(u.username, u.password)
        