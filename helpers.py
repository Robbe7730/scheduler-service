"""
helpers: Helpers module, based on
https://github.com/MikiDi/mu-python-template/blob/development/helpers.py
"""

import uuid

from flask import jsonify


def error(msg, status=400):
    """
    error: Returns a JSONAPI compliant error response with the given status code
    (400 by default).
    """
    response = jsonify({'message': msg})
    response.status_code = status
    return response

def generate_uuid():
    """
    generate_uuid: Generates a UUIDv4
    """
    return uuid.uuid4()
