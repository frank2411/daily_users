import base64
import binascii

from flask import request, g
from flask_restful import abort

from functools import wraps

from daily_users_api.models import User


def check_basicauth_header(fn):
    """Decorator that checks if authorization header is present and validates it's format"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('authorization', None)

        if not auth_header:
            abort(403, message="Missing Authorization Header")

        auth_header = auth_header.split(" ")

        error_msg = "Bad {} header. Expected value '{} <BASIC_AUTH>'".format(
            'Authorization',
            'Basic'
        )

        if len(auth_header) != 2:
            abort(403, message=error_msg)

        if auth_header[0] != 'Basic':
            abort(403, message=error_msg)

        # Validate if token is correct base64 format
        try:
            base64.b64decode(auth_header[1])
        except binascii.Error:
            abort(403, message="No base64 format")

        return fn(*args, **kwargs)

    return wrapper


# Modify this decorator accordingly to your auth flow
def authenticate_user(fn):
    """Decorator that check token against the DB and then set the current user for the application"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('authorization', None)
        auth_header = auth_header.split(" ")
        token = auth_header[1]
        User.set_current_user(token)
        return fn(*args, **kwargs)

    return wrapper


# Modify this decorator accordingly to your auth flow
def partial_authenticate_user(fn):
    """Decorator that check token against the DB and then set the current user for the application"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('authorization', None)
        auth_header = auth_header.split(" ")
        token = auth_header[1]
        User.set_current_user(token, is_active_check=False)
        return fn(*args, **kwargs)

    return wrapper


# def redirect_if_not_admin(fn):
#     @wraps(fn)
#     def wrapper(*args, **kwargs):
#         if g.current_user.role.value == "user":
#             abort(403, message="Access forbidden")
#         return fn(*args, **kwargs)

#     return wrapper


# def redirect_if_not_superadmin(fn):
#     @wraps(fn)
#     def wrapper(*args, **kwargs):
#         if g.current_user.role.value != "superadmin":
#             abort(403, message="Access forbidden")
#         return fn(*args, **kwargs)

#     return wrapper
