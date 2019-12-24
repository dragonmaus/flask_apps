from functools import wraps

import requests
from flask import Flask, json, jsonify, request

from common import secret, status

app = Flask(__name__)

def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.headers.get('X-Gitlab-Token').encode() != secret.api_key:
            return status(401)
        return f(*args, **kwargs)
    return decorated_function

@app.route('/push', methods=['POST'])
@api_key_required
def push():
    with open('gitlab.request.headers', 'w') as f:
        json.dump(dict(request.headers), f)
    with open('gitlab.request.payload', 'wb') as f:
        f.write(request.get_data())

    return status(200)
