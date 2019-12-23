import os

from flask import Flask, escape, redirect, request, send_from_directory, url_for

app = Flask(__name__)

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
