import os
from typing import Dict, Any

# RabbitMQ Connection Settings
RABBITMQ_CONFIG = {
    'host': os.getenv('RABBITMQ_HOST', 'localhost'),
    'port': int(os.getenv('RABBITMQ_PORT', 5672)),
    'username': os.getenv('RABBITMQ_USER', 'guest'),
    'password': os.getenv('RABBITMQ_PASSWORD', 'guest'),
    'vhost': os.getenv('RABBITMQ_VHOST', '/'),
    'heartbeat': 600,
    'blocked_connection_timeout': 300
}

# Consumer Settings
CONSUMER_SETTINGS = {
    'prefetch_count': 1,
    'auto_ack': False,
    'exclusive': False,
    'arguments': {}
}

# Publisher Settings
PUBLISHER_SETTINGS = {
    'mandatory': False,
    'immediate': False,
    'delivery_mode': 2,
    'content_type': 'application/json'
}