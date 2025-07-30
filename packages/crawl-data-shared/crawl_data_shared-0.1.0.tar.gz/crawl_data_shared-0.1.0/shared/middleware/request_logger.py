from flask import request
import time

def log_request(app):
    @app.before_request
    def before():
        request.start_time = time.time()

    @app.after_request
    def after(response):
        if hasattr(request, 'start_time'):
            duration = round(time.time() - request.start_time, 4)
        else:
            duration = 0

        if response.status_code == 401:
            print(f"�� {request.method} {request.path} - {response.status_code} (AUTH_FAILED) - {duration}s")
        elif response.status_code >= 400:
            print(f"❌ {request.method} {request.path} - {response.status_code} (ERROR) - {duration}s")
        elif response.status_code >= 300:
            print(f"�� {request.method} {request.path} - {response.status_code} (REDIRECT) - {duration}s")
        else:
            print(f"✅ {request.method} {request.path} - {response.status_code} (SUCCESS) - {duration}s")
        
        return response