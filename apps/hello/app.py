import os.path
import re
from base64 import b64decode
from functools import wraps

from flask import Flask, escape, g, jsonify, redirect, request, send_from_directory, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

from common import secret, status

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = secret.key

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

def check_auth(request):
    auth = request.headers.get('Authorization')
    if not auth:
        return None
    auth = re.sub(r'^Basic ', '', auth)
    try:
        auth = b64decode(auth)
    except TypeError:
        pass
    name, password = auth.decode().split(':', 1)
    user = User.query.filter_by(name=name).first()
    if user and user.check_password(password):
        return user
    return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in session:
            user = User.query.filter_by(name=session['username']).first()
        else:
            user = check_auth(request)
        if not user:
            return status(401, headers={'WWW-Authenticate': 'Basic realm="Login Required"'})
        g.user = user
        session['username'] = user.name
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return redirect(url_for('hello'))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/hello')
def hello():
    name = request.args.get('name', 'world')
    return f'Hello, {escape(name)}!'

@app.route('/goodbye')
def goodbye():
    name = request.args.get('name', 'cruel world')
    return f'Goodbye, {escape(name)}!'

@app.route('/test')
@login_required
def test():
    return status(200, message=f'Hello, {g.user.name}!')
