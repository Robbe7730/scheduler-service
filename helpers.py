"""
helpers: Helpers module, based on
https://github.com/MikiDi/mu-python-template/blob/development/helpers.py
"""

import uuid

from flask import jsonify, Response

def error(msg, status=400) -> Response:
    """
    error: Returns a JSON:API compliant error response with the given status
    code (400 by default).

    :returns: A JSON:API compliant Flask Response
    """
    response = jsonify({'message': msg})
    response.status_code = status
    return response

def generate_uuid() -> uuid.UUID:
    """
    generate_uuid: Generates a UUIDv4

    :returns: A UUID v4
    """
    return uuid.uuid4()
