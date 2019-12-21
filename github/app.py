import hmac
import requests
import uritemplate

from ..common import status
from ..secret import authorization_key, github_token
from flask import Flask, request
from subprocess import PIPE, run
from tempfile import SpooledTemporaryFile, TemporaryDirectory

app = Flask(__name__)

@app.route('/push', methods=['POST'])
def push():
    signature = hmac.new(authorization_key.encode(), msg=request.get_data(), digestmod='sha1').hexdigest()
    if request.headers.get('X-Hub-Signature') != f'sha1={signature}':
        return status(401)

    data = request.get_json()
    if not data:
        return status(400)

    if not (data['created'] and data['ref'].startswith('refs/tags/')):
        return status(200)

    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': 'token {github_token}',
    }

    uri = uritemplate.expand(data['repository']['git_refs_url']) + '/' + data['ref'].split('/', 1)[1]
    r = requests.get(uri, headers=headers)
    if r.status_code != 200:
        return status(500, message=f'error fetching "{uri}"')

    try:
        uri = r.json()['object']['url']
    except ValueError:
        return status(500, message='error parsing JSON')

    r = requests.get(uri, headers=headers)
    if r.status_code != 200:
        return status(500, message=f'error fetching "{uri}"')

    try:
        tag = r.json()
    except ValueError:
        return status(500, message='error parsing JSON')

    message = tag['message'].strip()
    tag = tag['tag']

    uri = uritemplate.expand(data['repository']['releases_url'])
    payload = {
        'tag_name': tag,
        'target_commitish': data['repository']['default_branch'],
        'name': f'Fantasque Magisk {tag}',
        'body': message,
        'draft': False,
        'prerelease': False,
    }
    r = requests.post(uri, json=payload, headers=headers)
    if r.status_code == 422 and r.json()['errors'][0]['code'] == 'already_exists':
        uri += f'/tags/{tag}'
        r = requests.get(uri, headers=headers)

    if r.status_code not in [200, 201]:
        return status(500, message=f'error fetching "{uri}"')

    try:
        release = r.json()
    except ValueError:
        return status(500, message='error parsing JSON')

    with SpooledTemporaryFile() as f:
        with TemporaryDirectory() as d:
            p = run(['git', 'clone', data['repository']['clone_url'], d])
            if p.returncode != 0:
                return status(500, message='error cloning repository')

            p = run(['git', '-C', d, 'archive', '--format=zip', tag], stdout=PIPE)
            if p.returncode != 0:
                return status(500, message='error creating archive')

            b = p.stdout

    headers.update({
        'Content-Length': str(len(b)),
        'Content-Type': 'application/zip',
    })
    uri = uritemplate.expand(release['upload_url'], name='fantasque-magisk.zip')
    r = requests.post(uri, data=b, headers=headers)

    if r.status_code != 201:
        return status(500, message='error uploading archive')

    return status(200, message='release created')
