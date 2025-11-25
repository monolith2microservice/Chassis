import requests
import socket
import logging
import atexit
import os
from typing import Optional

class ConsulClient:
    def __init__(
        self, 
        logger: logging.Logger, 
        consul_host: Optional[str] = None, 
        consul_port: int = 8500
    ) -> None:
        self._logger = logger
        self._consul_host = consul_host or os.getenv('CONSUL_HOST', 'consul')
        self._consul_port = consul_port
        self._service_id: Optional[str] = None

    def register_service(self, service_name: str, port: int, health_path: str = "/health") -> None:
        try:
            if not health_path.startswith("/"):
                health_path = "/" + health_path
            
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            
            self._service_id = f"{service_name}-{hostname}"

            payload = {
                "ID": self._service_id,
                "Name": service_name,
                "Address": ip_address,
                "Port": port,
                "Check": {
                    "HTTP": f"http://{ip_address}:{port}{health_path}",
                    "Interval": "10s",
                    "DeregisterCriticalServiceAfter": "1m"
                }
            }

            url = f"http://{self._consul_host}:{self._consul_port}/v1/agent/service/register"
            res = requests.put(url, json=payload, timeout=2)
            
            if res.status_code == 200:
                self._logger.info(f"Service '{service_name}' registered successfully as '{self._service_id}'")
                atexit.register(self.deregister_service)
            else:
                self._logger.error(f"Failed to register: {res.text}")

        except Exception as e:
            self._logger.error(f"Connection failed: {e}")

    def deregister_service(self) -> None:
        if not self._service_id:
            return

        try:
            url = f"http://{self._consul_host}:{self._consul_port}/v1/agent/service/deregister/{self._service_id}"
            requests.put(url, timeout=2)
            self._logger.info(f"Service '{self._service_id}' deregistered.")
        except Exception as e:
            self._logger.warning(f"Error during deregistration: {e}")