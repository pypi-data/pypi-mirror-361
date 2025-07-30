import jwt
from datetime import datetime, timedelta
from shared.config.settings import *

def create_token(data: dict, exp_minutes=30):
    payload = {
        'exp': datetime.utcnow() + timedelta(minutes=exp_minutes),
        'type': 'access',
        **data
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def create_refresh_token(data: dict, expires_in_days=7):
    payload = {
        'exp': datetime.utcnow() + timedelta(days=expires_in_days),
        'type': 'refresh',
        **data
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str):
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
