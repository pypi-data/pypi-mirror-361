from datetime import datetime

def now_iso():
    return datetime.utcnow().isoformat() + 'Z'

def format_time(dt: datetime):
    return dt.strftime('%Y-%m-%d %H:%M:%S')
