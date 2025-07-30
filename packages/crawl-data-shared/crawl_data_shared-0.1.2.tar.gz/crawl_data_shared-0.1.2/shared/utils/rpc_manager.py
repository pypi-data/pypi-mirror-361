import threading
import os
from shared.utils.rabbitmq_helper import *
from shared.logger import setup_logger

logger = setup_logger(__name__)

class RPCManager:
    def __init__(self, app=None):
        self.rpc_servers = {}
        self.rpc_threads = {}
        self.handlers = {}
        self.app = app
    
    
    def init_app(self, app):
        self.app = app
    
    
    def add_rpc_server(self, name: str, queue_name: str, handler: callable):
        try:
            # Store handler
            self.handlers[name] = handler

            # Create RPC server
            rpc_server = RabbitMQRPCServer(queue_name, handler)
            
            # Start in background thread
            def start_server():
                try:
                    print(f"🚀 Starting {name} RPC Server...")
                    rpc_server.start_server()
                except Exception as e:
                    print(f"❌ Failed to start {name} RPC server: {e}")
            
            thread = threading.Thread(target=start_server, daemon=True)
            thread.start()
            
            # Store references
            self.rpc_servers[name] = rpc_server
            self.rpc_threads[name] = thread
            
            # Wait a bit to see if server starts successfully
            import time
            time.sleep(1)
            
            if thread.is_alive():
                print(f"✅ {name} RPC server started successfully!")
            else:
                print(f"❌ {name} RPC server failed to start")
                
        except Exception as e:
            print(f"❌ Failed to add RPC server {name}: {e}")
    

    def add_rpc_server_with_app(self, name: str, queue_name: str, handler: callable):

        if not self.app:
            raise ValueError("Flask app not set. Call set_app() first.")
        
        def handler_with_context(request_data: dict) -> dict:
            with self.app.app_context():
                return handler(request_data)
        
        self.add_rpc_server(name, queue_name, handler_with_context)


    def stop_rpc_server(self, name: str):
        if name in self.rpc_servers:
            print(f"🛑 Stopping {name} RPC server...")
            self.rpc_servers[name].stop_server()
            self.rpc_servers[name].close()
            print(f"✅ {name} RPC server stopped")
    

    def stop_all(self):
        for name in list(self.rpc_servers.keys()):
            self.stop_rpc_server(name)
    

    def get_status(self):
        status = {}
        for name, thread in self.rpc_threads.items():
            status[name] = {
                'alive': thread.is_alive(),
                'queue': self.rpc_servers[name].queue_name if name in self.rpc_servers else None
            }
        return status


    def restart_rpc_server(self, name: str):
        if name in self.rpc_servers:
            print(f"🔄 Restarting {name} RPC server...")
            self.stop_rpc_server(name)
            time.sleep(1)
            self.add_rpc_server(name, self.rpc_servers[name].queue_name, self.handlers[name])

# Global RPC manager instance
rpc_manager = RPCManager()