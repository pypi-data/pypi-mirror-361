from functools import wraps
from flask import request
import requests
from shared.response import make_response
from shared.middleware.auth_middleware import verify_token_rpc

def auth_required_with_role(required_role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Check role
            user_role = request.user.get('role')
            if user_role != required_role:
                return make_response(
                    success=False, 
                    message='Insufficient permissions', 
                    status=403
                )
            
            return f(*args, **kwargs)
        return wrapper
    return decorator
