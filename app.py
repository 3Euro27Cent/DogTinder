from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from PIL import Image
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import base64
import os
import re

app = Flask(__name__)
app.secret_key = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['UPLOAD_FOLDER'] = 'static/images'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    display_name = db.Column(db.String(120))
    description = db.Column(db.Text)
    email = db.Column(db.String(120))
    dogs = db.relationship('Dog', backref='owner', lazy='select')

class Dog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    beschreibung = db.Column(db.Text, nullable=False)
    bild = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    besitzer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rasse = db.Column(db.String(80))
    alter = db.Column(db.Integer)
    groesse = db.Column(db.Float)   # Größe in cm
    gewicht = db.Column(db.Float)   # Gewicht in kg
    geimpft_gechipt = db.Column(db.String(20))
    vertraeglich_katzen = db.Column(db.Boolean, default=False)
    vertraeglich_hunde = db.Column(db.Boolean, default=False)
    vertraeglich_kinder = db.Column(db.Boolean, default=False)
    besonderheiten = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.beschreibung,
            'bild': self.bild,
            'besitzer_id': self.besitzer_id,
            'owner_display_name': self.owner.display_name,
            'owner_username': self.owner.username
        }

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])

# Temporär, wird nicht genutzt, da DB
users = {}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('profile'))
        else:
            flash('Invalid username or password')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        display_name = request.form['display_name']
        email = request.form['email']

        if User.query.filter_by(username=username).first():
            flash("Benutzername existiert bereits.")
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

        new_user = User(
            username=username,
            email=email,
            display_name=display_name,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registrierung erfolgreich! Bitte logge dich ein.")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Du wurdest erfolgreich abgemeldet.")
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    user = User.query.get(session['user_id'])

    vermittler = {
        'display_name': user.display_name,
        'description': user.description,
        'email': user.email,
        'comments': [],  # Optional, falls noch implementiert
    }
    hunde = user.dogs

    return render_template('profile.html', vermittler=vermittler, hunde=hunde)

@app.route('/profil_bearbeiten', methods=['GET', 'POST'])
@login_required
def profil_bearbeiten():
    vermittler = User.query.get(session['user_id'])
    if not vermittler:
        flash("Benutzer nicht gefunden.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        display_name = request.form.get('display_name', '').strip()
        email = request.form.get('email', '').strip()
        description = request.form.get('description', '').strip()

        vermittler.display_name = display_name
        vermittler.email = email
        vermittler.description = description

        db.session.commit()

        flash('Profil erfolgreich aktualisiert!')
        return redirect(url_for('profile'))

    return render_template('profil_bearbeiten.html', vermittler=vermittler)

@app.route('/hunde_entfernen', methods=['GET', 'POST'])
@login_required
def hunde_entfernen():
    back_url = url_for('profile')
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        hund_id = request.form.get('hund_id')
        if not hund_id:
            flash("Keine Hund-ID übergeben.")
            return redirect(url_for('hunde_entfernen'))

        hund = Dog.query.get(hund_id)
        if not hund:
            flash("Hund nicht gefunden.")
            return redirect(url_for('hunde_entfernen'))

        if hund.besitzer_id != user.id:
            flash("Du darfst diesen Hund nicht löschen.")
            return redirect(url_for('hunde_entfernen'))

        # Bild löschen
        try:
            bildpfad = os.path.join(app.config['UPLOAD_FOLDER'], hund.bild)
            if os.path.exists(bildpfad):
                os.remove(bildpfad)
        except Exception as e:
            flash("Fehler beim Löschen des Bildes.")
            print("Fehler beim Löschen der Bilddatei:", e)

        db.session.delete(hund)
        db.session.commit()
        flash(f"Hund {hund.name} wurde gelöscht.")
        return redirect(url_for('hunde_entfernen'))

    vermittler = {
        'display_name': user.display_name,
        'description': user.description,
        'email': user.email,
        'comments': [],
    }
    hunde = user.dogs
    return render_template('hunde_entfernen.html',
                           vermittler=vermittler,
                           hunde=hunde,
                           show_back=True,
                           back_url=back_url)

@app.route('/hund_hinzufuegen', methods=['POST', 'GET'])
@login_required
def hund_hinzufuegen():
    if request.method == 'POST':
        name = request.form.get('name')
        beschreibung = request.form.get('beschreibung')
        image_file = request.files.get('bild')  # <--- Datei statt base64
        rasse = request.form.get('rasse')
        alter = request.form.get('alter', type=int)
        groesse = request.form.get('groesse', type=float)
        gewicht = request.form.get('gewicht', type=float)
        geimpft_gechipt = request.form.get('geimpft_gechipt', '0')
        geimpft_gechipt = 'ja' if geimpft_gechipt == '1' else 'nein'
        vertraeglich_hunde = bool(int(request.form.get('vertraeglich_hunde', '0')))
        vertraeglich_katzen = bool(int(request.form.get('vertraeglich_katzen', '0')))
        vertraeglich_kinder = bool(int(request.form.get('vertraeglich_kinder', '0')))
        besonderheiten_list = request.form.getlist('besonderheiten')
        besonderheiten = ', '.join(besonderheiten_list) if besonderheiten_list else ''
        if not image_file:
            flash("Bitte Bild hinzufügen.")
            return redirect(url_for('hund_hinzufuegen'))
        if not name:
            flash("Bitte Name hinzufügen.")
            return redirect(url_for('hund_hinzufuegen'))
        if not beschreibung:
            flash("Bitte Beschreibung hinzufügen.")
            return redirect(url_for('hund_hinzufuegen'))

        if not image_file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            flash("Ungültiges Bildformat. Erlaubt sind JPG und PNG.")
            return redirect(url_for('hund_hinzufuegen'))

        vermittler_id = session.get('user_id')
        if not vermittler_id:
            flash("Nicht authentifiziert.")
            return redirect(url_for('login'))

        try:
            safe_name = re.sub(r'[^a-zA-Z0-9_-]', '', name.replace(" ", "_"))

            new_dog = Dog(
                name=name,
                beschreibung=beschreibung,
                bild="temp.jpg",  # Platzhalter
                besitzer_id=vermittler_id,
                rasse=rasse,
                alter=alter,
                groesse=groesse,
                gewicht=gewicht,
                geimpft_gechipt=geimpft_gechipt,
                vertraeglich_hunde=vertraeglich_hunde,
                vertraeglich_katzen=vertraeglich_katzen,
                vertraeglich_kinder=vertraeglich_kinder,
                besonderheiten=besonderheiten
            )

            db.session.add(new_dog)
            db.session.flush()  # Erstellt die ID

            filename = f"{safe_name}_{vermittler_id}_{new_dog.id}.jpg"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))

            image_file.save(filepath)  # Speichert Bild auf Server

            new_dog.bild = filename
            db.session.commit()

            flash("Hund erfolgreich hinzugefügt!")
            return redirect(url_for('profile'))

        except Exception as e:
            flash("Fehler beim Verarbeiten des Hundes oder Bildes.")
            print("Fehler:", e)
            return redirect(url_for('hund_hinzufuegen'))

    # GET-Anfrage
    user = User.query.get(session['user_id'])
    vermittler_info = {
        "display_name": user.display_name,
        "description": user.description,
        "email": user.email,
    }
    back_url = url_for('profile')

    return render_template("hund_hinzufuegen.html", 
                           vermittler=vermittler_info, 
                           vermittler_username=user.username,
                           show_back=True,
                           back_url=back_url)

@app.route('/')
@login_required
def home():
    # 1. Hunde aus DB
    hunde_query = Dog.query.order_by(Dog.created_at.desc()).all()
    hunde = [hund.to_dict() for hund in hunde_query]

    if not hunde:
        return "Keine Hunde vorhanden", 404

    # 2. Aktuellen Hund bestimmen
    current_dog = request.args.get('current_dog', hunde[0]['name'])
    current_index = next((i for i, h in enumerate(hunde) if h['name'] == current_dog), 0)

    # 3. Vermittler-Daten (alle User)
    vermittler_query = User.query.all()
    vermittler = {str(user.id): user for user in vermittler_query}

    return render_template(
        "index.html",
        hunde=hunde,
        current_dog=current_dog,
        current_index=current_index,
        vermittler=vermittler,
        show_back=False
    )


@app.route('/filter', methods=['GET', 'POST'])
def filter_view():
    if request.method == 'POST':
        session['filter'] = {
            "rasse": request.form.get('rasse'),
            "alter_max": request.form.get('alter_max'),
            "groesse": request.form.get('groesse'),
            "aktivitaetslevel": request.form.get('aktivitaetslevel'),
            "geimpft": request.form.get('geimpft') == 'on',
            "kastriert": request.form.get('kastriert') == 'on',
            "kinderfreundlich": request.form.get('kinderfreundlich') == 'on',
            "hundevertraeglich": request.form.get('hundevertraeglich') == 'on',
            "geschlecht": request.form.get('geschlecht'),
            "vermittler": request.form.get('vermittler'),
        }
        return redirect(url_for('home'))

    alle_rassen = (
        db.session.query(Dog.rasse)
        .filter(Dog.rasse.isnot(None))
        .distinct()
        .order_by(Dog.rasse)
        .all()
    )
    alle_rassen = [r[0] for r in alle_rassen]

    vermittler_query = User.query.all()
    
    return render_template(
        'filter.html',
        alle_rassen=alle_rassen,
        vermittler=vermittler_query
    )

@app.route('/meinehunde/<int:hund_id>')
@login_required
def benutzer_hund_details(hund_id):
    userhunde = User.query.get(session['user_id']).dogs
    hund = Dog.query.filter_by(id=hund_id, besitzer_id=session['user_id']).first()


    if not hund:
        return "<h1>Hund nicht gefunden!</h1>", 404

    vermittler_id = hund.besitzer_id
    vermittler_username = hund.owner.username
    vermittler_info = User.query.filter_by(username=vermittler_username).first()

    if not vermittler_info:
        # Optional: Fehlerseite oder Default
        return f"<h1>Vermittler '{vermittler_username}' nicht gefunden!</h1>", 404
    back_url = f"/profile"

    return render_template("details.html", 
                         hund=hund, 
                         vermittler=vermittler_info, 
                         vermittler_username=vermittler_username,
                         show_back=True,
                         back_url=back_url)
@app.route('/hund/<int:hund_id>')
def hund_details(hund_id):
    hund = Dog.query.get(hund_id)
    if not hund:
        return "<h1>Hund nicht gefunden!</h1>", 404

    vermittler_info = User.query.get(hund.besitzer_id)
    if not vermittler_info:
        return f"<h1>Vermittler mit ID {hund.besitzer_id} nicht gefunden!</h1>", 404

    back_url = "/"

    return render_template("details.html",
                           hund=hund,
                           vermittler=vermittler_info,
                           vermittler_username=vermittler_info.username,
                           show_back=True,
                           back_url=back_url)

@app.route('/vermittler/<username>')
@login_required
def vermittler_profil(username):
    current_user = User.query.get(session['user_id'])

    if username == current_user.username:
        return redirect(url_for('profile'))

    info = User.query.filter_by(username=username).first()
    if not info:
        return "<h1>Vermittler nicht gefunden!</h1>", 404
    vermittler_hunde = Dog.query.filter_by(besitzer_id=info.id).all()

    back_url = request.headers.get('Referer', '/')

    return render_template(
        "vermittler.html",
        vermittler=info,
        username=username,
        hunde=vermittler_hunde,
        show_back=True,
        back_url=back_url
    )


@app.route('/chats')
@login_required
def chats():
    user_id = session['user_id']
    
    # Alle User, mit denen aktuell Nachrichten ausgetauscht wurden
    sent = db.session.query(Message.receiver_id).filter_by(sender_id=user_id)
    received = db.session.query(Message.sender_id).filter_by(receiver_id=user_id)
    
    partner_ids = set([row[0] for row in sent.union(received).all()])
    
    partners = User.query.filter(User.id.in_(partner_ids)).all()
    
    return render_template('chats.html', partners=partners)


@app.route('/chat/<int:partner_id>', methods=['GET', 'POST'])
@login_required
def chat(partner_id):
    user_id = session['user_id']
    
    # Nachrichten zwischen aktuell eingeloggtem User und Partner laden
    messages = Message.query.filter(
        ((Message.sender_id == user_id) & (Message.receiver_id == partner_id)) |
        ((Message.sender_id == partner_id) & (Message.receiver_id == user_id))
    ).order_by(Message.timestamp).all()
    
    if request.method == 'POST':
        content = request.form.get('message')
        if content:
            msg = Message(sender_id=user_id, receiver_id=partner_id, content=content)
            db.session.add(msg)
            db.session.commit()
            return redirect(url_for('chat', partner_id=partner_id))
    
    partner = User.query.get(partner_id)
    if not partner:
        flash('Chat-Partner nicht gefunden')
        return redirect(url_for('profile'))
    
    return render_template('chat.html', messages=messages, partner=partner)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)

