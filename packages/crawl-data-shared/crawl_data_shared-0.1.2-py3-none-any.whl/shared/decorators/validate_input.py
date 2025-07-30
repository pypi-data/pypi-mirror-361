from functools import wraps
from flask import request
from shared.response import make_response

def validate_input(schema):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            json_data = request.get_json()
            try:
                validated_data = schema().load(json_data)
                request.validated_data = validated_data
            except Exception as e:
                return make_response(False, None, str(e), 400)
            return f(*args, **kwargs)
        return wrapper
    return decorator