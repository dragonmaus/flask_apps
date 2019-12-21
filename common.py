__all__ = ['status']

from flask import jsonify, make_response

codemap = {
    200: 'ok',
    400: 'bad_request',
    401: 'unauthorized',
    500: 'internal_error',
}

def kebab2normal(s):
    return ' '.join(x.capitalize() for x in s.split('-'))

def status(code, **kwargs):
    payload = {'status': codemap[code]}
    payload.update(**kwargs)
    return make_response((jsonify(payload), code))
