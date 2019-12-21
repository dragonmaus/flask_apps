import requests

from ..common import status
from ..secret import authorization_key
from flask import Flask, json, jsonify, request

app = Flask(__name__)

@app.route('/push', methods=['POST'])
def push():
    if request.headers.get('X-Gitlab-Token') != authorization_key:
        return status(401)

    with open('gitlab.request.headers', 'w') as f:
        json.dump(dict(request.headers), f)
    with open('gitlab.request.payload', 'wb') as f:
        f.write(request.get_data())

    return status(200)
