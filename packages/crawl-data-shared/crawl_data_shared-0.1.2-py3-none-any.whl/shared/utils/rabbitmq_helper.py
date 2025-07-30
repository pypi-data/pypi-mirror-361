import os
import json
import logging
import pika
import uuid
import time
from typing import Dict, Any, Optional, Callable
from functools import wraps
from shared.logger import setup_logger

logger = logging.getLogger(__name__)


class RabbitMQConnection:
    def __init__(self):
        self.connection = None
        self.channel = None
        self._connect()
    
    def _connect(self):
        try:
            # Get connection parameters from environment
            host = os.getenv('RABBITMQ_HOST', 'localhost')
            port = int(os.getenv('RABBITMQ_PORT', 5672))
            username = os.getenv('RABBITMQ_USER', 'guest')
            password = os.getenv('RABBITMQ_PASSWORD', 'guest')
            vhost = os.getenv('RABBITMQ_VHOST', '/')
            
            # Create connection parameters
            credentials = pika.PlainCredentials(username, password)
            parameters = pika.ConnectionParameters(
                host=host,
                port=port,
                virtual_host=vhost,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            
            # Establish connection
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            logger.info(f"Connected to RabbitMQ at {host}:{port}")
            
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    def ensure_connection(self):
        """Ensure connection is active, reconnect if necessary"""
        if not self.connection or self.connection.is_closed:
            logger.info("Reconnecting to RabbitMQ...")
            self._connect()
    
    def close(self):
        """Close the connection"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("RabbitMQ connection closed")


class RabbitMQPublisher:
    def __init__(self):
        self.rabbitmq = RabbitMQConnection()
    
    def publish_message(self, queue_name: str, message: Dict[str, Any], 
                       exchange: str = '', routing_key: str = None):
        try:
            self.rabbitmq.ensure_connection()
            
            # Declare queue
            self.rabbitmq.channel.queue_declare(queue=queue_name, durable=True)
            
            # Set routing key
            if routing_key is None:
                routing_key = queue_name
            
            # Publish message
            self.rabbitmq.channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )
            
            logger.info(f"Message published to queue '{queue_name}': {message}")
            
        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            raise
    
    def close(self):
        """Close the publisher connection"""
        self.rabbitmq.close()


class RabbitMQConsumer:
    def __init__(self):
        self.rabbitmq = RabbitMQConnection()
    
    def consume_messages(self, queue_name: str, callback: Callable, 
                        auto_ack: bool = False):
        try:
            self.rabbitmq.ensure_connection()
            
            # Declare queue
            self.rabbitmq.channel.queue_declare(queue=queue_name, durable=True)
            
            # Set QoS
            self.rabbitmq.channel.basic_qos(prefetch_count=1)
            
            # Define message handler
            def message_handler(ch, method, properties, body):
                try:
                    # Parse message
                    message = json.loads(body)
                    logger.info(f"Received message from queue '{queue_name}': {message}")
                    
                    # Call callback
                    callback(message)
                    
                    # Acknowledge message
                    if not auto_ack:
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                        
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    if not auto_ack:
                        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            
            # Start consuming
            self.rabbitmq.channel.basic_consume(
                queue=queue_name,
                on_message_callback=message_handler,
                auto_ack=auto_ack
            )
            
            logger.info(f"Started consuming from queue '{queue_name}'")
            
            # Start the consumer loop
            self.rabbitmq.channel.start_consuming()
            
        except Exception as e:
            logger.error(f"Failed to start consumer: {e}")
            raise
    
    def stop_consuming(self):
        """Stop consuming messages"""
        if self.rabbitmq.channel:
            self.rabbitmq.channel.stop_consuming()
    
    def close(self):
        """Close the consumer connection"""
        self.rabbitmq.close()


class RabbitMQRPC:
    def __init__(self):
        self.rabbitmq = RabbitMQConnection()
    
    def call(self, queue_name: str, message: Dict[str, Any], timeout: int = 5) -> Optional[Dict[str, Any]]:
        correlation_id = str(uuid.uuid4())
        response_queue = f"rpc_response_{correlation_id}"
        
        # Create temporary response queue
        self.rabbitmq.channel.queue_declare(
            queue=response_queue,
            durable=False,
            auto_delete=True
        )

        # Add correlation_id to message
        message['correlation_id'] = correlation_id
        message['timestamp'] = time.time()

        try:
            # Publish RPC request
            self.rabbitmq.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    reply_to=response_queue,
                    correlation_id=correlation_id,
                    content_type='application/json'
                )
            )

            logger.info(f"RPC request sent to '{queue_name}' with correlation_id: {correlation_id}")
            
            # Wait for response
            response = self._wait_for_response(response_queue, correlation_id, timeout)
            
            return response
            
        except Exception as e:
            logger.error(f"RPC call failed: {e}")
            return None
        finally:
            # Cleanup temporary queue
            self._cleanup_queue(response_queue)

    def _wait_for_response(self, response_queue: str, correlation_id: str, timeout: float) -> Optional[Dict[str, Any]]:
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Check for response
                method, properties, body = self.rabbitmq.channel.basic_get(
                    queue=response_queue,
                    auto_ack=True
                )
                
                if method:
                    response_data = json.loads(body)
                    
                    # Check if this is the response we're waiting for
                    if properties.correlation_id == correlation_id:
                        logger.info(f"RPC response received for correlation_id: {correlation_id}")
                        return response_data
                        
            except Exception as e:
                logger.error(f"Error waiting for RPC response: {e}")
                break
                
        logger.warning(f"RPC timeout for correlation_id: {correlation_id}")
        return None

    def _cleanup_queue(self, queue_name: str):
            try:
                self.rabbitmq.channel.queue_delete(queue=queue_name)
            except Exception as e:
                logger.error(f"Error cleaning up queue {queue_name}: {e}")
    
    def close(self):
        self.rabbitmq.close()


class RabbitMQRPCServer:
    def __init__(self, queue_name: str, handler: callable):
        self.rabbitmq = RabbitMQConnection()
        self.queue_name = queue_name
        self.handler = handler

    def start_server(self):
        try:
            # Declare request queue
            self.rabbitmq.channel.queue_declare(
                queue=self.queue_name,
                durable=True
            )
            
            # Set QoS
            self.rabbitmq.channel.basic_qos(prefetch_count=1)
            
            # Define message handler
            def message_handler(ch, method, properties, body):
                try:
                    # Parse request
                    request_data = json.loads(body)
                    correlation_id = properties.correlation_id
                    reply_to = properties.reply_to
                    
                    logger.info(f"RPC request received: {correlation_id}")
                    
                    # Process request
                    response = self.handler(request_data)
                    
                    # Send response
                    self.rabbitmq.channel.basic_publish(
                        exchange='',
                        routing_key=reply_to,
                        body=json.dumps(response),
                        properties=pika.BasicProperties(
                            correlation_id=correlation_id,
                            content_type='application/json'
                        )
                    )
                    
                    # Acknowledge request
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    
                    logger.info(f"RPC response sent for correlation_id: {correlation_id}")
                    
                except Exception as e:
                    logger.error(f"Error processing RPC request: {e}")
                    # Send error response
                    error_response = {
                        'success': False,
                        'message': 'Internal server error',
                        'status': 500
                    }
                    
                    self.rabbitmq.channel.basic_publish(
                        exchange='',
                        routing_key=properties.reply_to,
                        body=json.dumps(error_response),
                        properties=pika.BasicProperties(
                            correlation_id=properties.correlation_id,
                            content_type='application/json'
                        )
                    )
                    
                    ch.basic_ack(delivery_tag=method.delivery_tag)
            
            # Start consuming
            self.rabbitmq.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=message_handler
            )
            
            logger.info(f"RPC server started on queue: {self.queue_name}")
            
            # Start the server loop
            self.rabbitmq.channel.start_consuming()
        
        except Exception as e:
            logger.error(f"Failed to start RPC server: {e}")
            raise
    
    def stop_server(self):
        if self.rabbitmq.channel:
            self.rabbitmq.channel.stop_consuming()
    
    def close(self):
        self.rabbitmq.close()
        

def rabbitmq_connection_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (pika.exceptions.AMQPConnectionError, 
                pika.exceptions.StreamLostError) as e:
            logger.error(f"RabbitMQ connection error in {func.__name__}: {e}")
            raise
    return wrapper


# RPC helper functions
def rpc_call(queue_name: str, message: Dict[str, Any], timeout: float = 5.0) -> Optional[Dict[str, Any]]:
    rpc_client = RabbitMQRPC()
    try:
        return rpc_client.call(queue_name, message, timeout)
    finally:
        rpc_client.close()

def start_rpc_server(queue_name: str, handler: callable):
    rpc_server = RabbitMQRPCServer(queue_name, handler)
    try:
        rpc_server.start_server()
    finally:
        rpc_server.close()


# Example usage functions
def create_queue(queue_name: str, durable: bool = True):
    rabbitmq = RabbitMQConnection()
    try:
        rabbitmq.channel.queue_declare(queue=queue_name, durable=durable)
        logger.info(f"Queue '{queue_name}' created/verified")
    finally:
        rabbitmq.close()


def delete_queue(queue_name: str):
    rabbitmq = RabbitMQConnection()
    try:
        rabbitmq.channel.queue_delete(queue=queue_name)
        logger.info(f"Queue '{queue_name}' deleted")
    finally:
        rabbitmq.close()


def get_queue_info(queue_name: str) -> Optional[Dict[str, Any]]:
    rabbitmq = RabbitMQConnection()
    try:
        method = rabbitmq.channel.queue_declare(queue=queue_name, passive=True)
        return {
            'queue': method.method.queue,
            'message_count': method.method.message_count,
            'consumer_count': method.method.consumer_count
        }
    except pika.exceptions.ChannelClosedByBroker:
        logger.warning(f"Queue '{queue_name}' does not exist")
        return None
    finally:
        rabbitmq.close()