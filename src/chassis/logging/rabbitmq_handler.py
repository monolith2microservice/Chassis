from ..messaging import (
    RabbitMQConfig,
    RabbitMQPublisher
)
from datetime import (
    datetime,
    timezone,
)
from typing import (
    Dict, 
    Any, 
    Optional, 
    Set, 
)
import logging
import re

class RabbitMQHandler(logging.Handler):
    """Handler that publishes logs to RabbitMQ based on type."""
    
    def __init__(
        self, 
        rabbitmq_config: RabbitMQConfig, 
        exchange: str = "logs"
    ) -> None:
        super().__init__()
        self.rabbitmq_config = rabbitmq_config
        self.exchange = exchange
        self.type_pattern = re.compile(r'\[([A-Z]+):([^\]]+)\]')
    
    def emit(self, record: logging.LogRecord) -> None:
        try:
            # Parse log type and subtype from message
            match = self.type_pattern.search(record.getMessage())
            if not match:
                return
            
            log_type, subtype = match.groups()
            msg = record.getMessage()

            # Clean message (remove type tag and metadata)
            message = re.sub(r'\[.*?\]\s*-?\s*', '', msg)
            
            log_data: Dict[str, Any] = {
                "log_type": log_type,
                "subtype": subtype,
                "level": record.levelname,
                "message": message,
                "timestamp": str(datetime.now(timezone.utc)),
                "source": {
                    "filename": record.filename,
                    "lineno": record.lineno,
                    "funcName": record.funcName,
                    "pathname": record.pathname,
                    "logger": record.name
                }
            }
            
            routing_key = f"log.{log_type.lower()}"
            
            with RabbitMQPublisher(
                queue="",
                rabbitmq_config=self.rabbitmq_config,
                exchange=self.exchange,
                exchange_type="topic",
                routing_key=routing_key,
            ) as publisher:
                publisher.publish(log_data)
                
        except Exception:
            self.handleError(record)

class RabbitMQLoggerManager:  
    def __init__(
        self, 
        rabbitmq_config: RabbitMQConfig, 
        exchange: str = "logs"
    ) -> None:
        self.rabbitmq_config = rabbitmq_config
        self.exchange = exchange
        self._handler_added_to: Set[str] = set()
    
    def get_logger(self, name: str) -> logging.Logger:
        logger = logging.getLogger(name)
        
        if name not in self._handler_added_to:
            rabbitmq_handler = RabbitMQHandler(self.rabbitmq_config, self.exchange)
            rabbitmq_handler.setLevel(logging.INFO)
            logger.addHandler(rabbitmq_handler)
            self._handler_added_to.add(name)
        
        return logger


# Global instance - initialize once at startup
_manager: Optional[RabbitMQLoggerManager] = None


def setup_rabbitmq_logging(
    rabbitmq_config: RabbitMQConfig, 
    exchange: str = "logs",
    capture_dependencies: bool = False
) -> None:
    global _manager
    _manager = RabbitMQLoggerManager(rabbitmq_config, exchange)
    
    # Optionally add handler to root logger for dependencies with propagate=1
    if capture_dependencies:
        _manager.get_logger("")


def get_logger(name: str) -> logging.Logger:
    if _manager is None:
        raise RuntimeError(
            "RabbitMQ logging not configured. "
            "Call setup_rabbitmq_logging() first."
        )
    return _manager.get_logger(name)


# # Usage example with logging.ini
# if __name__ == '__main__':
#     import os
#     import logging.config
    
#     # Step 1: Load your existing logging.ini configuration
#     logging.config.fileConfig(
#         os.path.join(os.path.dirname(__file__), "logging.ini")
#     )
    
#     # Step 2: Setup RabbitMQ logging once
#     RABBITMQ_CONFIG = {
#         "host": "localhost",
#         "port": 5672,
#         "username": "guest",
#         "password": "guest"
#     }
    
#     setup_rabbitmq_logging(rabbitmq_config=RABBITMQ_CONFIG)
    
#     # Step 3: Use get_logger() everywhere in your code
#     payment_logger = get_logger('payment')
#     payment_logger.info("[EVENT:PIECE:CREATED] - Ordered piece created: order_id=123, piece_id=456")
    
#     chassis_logger = get_logger('chassis')
#     chassis_logger.info("[CMD:PAYMENT_RELEASE:SENT] - Sent release command: order_id=789, amount=100.50")
    
#     # Any new logger automatically gets the handler
#     new_logger = get_logger('some.new.module')
#     new_logger.info("[LOG:SAGA] - State: PROCESSING")