from flask import request, g
from shared.response import *
from shared.utils.rabbitmq_helper import *
import time

class AuthMiddleware:
    def __init__(self, app=None, auto_auth=False, public_endpoints=None):
        self.app = app
        self.auto_auth = auto_auth
        self.public_endpoints = public_endpoints or []
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    def before_request(self):
        # Skip auth check for public endpoints
        if request.path in self.public_endpoints:
            return
        
        # Skip if auto_auth is disabled
        if not self.auto_auth:
            return
        
        # Check auth header
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return make_response(
                success = False, 
                message = 'Authorization header required', 
                status = 401
            )
        
        token = auth.split(' ')[1]
        result = verify_token_rpc(token)

        if not result['success']:
            return make_response(
                success = False, 
                message = result['message'], 
                status = 401
            )

        # Set user info
        request.user = result['data']
        g.user = result['data']
    
    def after_request(self, response):
        # Add auth info to response headers if needed
        if hasattr(request, 'user') and request.user:
            response.headers['X-User-ID'] = str(request.user.get('id', ''))
            response.headers['X-User-Role'] = str(request.user.get('role', ''))
        
        return response


def create_auth_middleware(auto_auth=False, public_endpoints=None):
    return AuthMiddleware(
        auto_auth = auto_auth,
        public_endpoints = public_endpoints or []
    )


def verify_token_rpc(token: str) -> dict:
    try:
        # Prepare request message
        request_message = {
            'token': token,
            'action': 'verify_token'
        }

        # Publish verification request
        response = rpc_call(
            queue_name='iam_requests',
            message=request_message,
            timeout=3.0
        )

        if response:
            return make_response_dict(success = True, data = response, message = 'Token hợp lệ', status = 200)
        else:
            return make_response_dict(success = False, message = 'Authentication service error', status = 401)
            
    except Exception as e:
        return make_response_dict(success = False, message = f'Authentication service error: {str(e)}', status = 401)