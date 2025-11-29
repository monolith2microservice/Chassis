import logging
import sys
import socket
from datetime import datetime
from typing import Optional

from chassis.messaging import RabbitMQPublisher, RabbitMQConfig


class RabbitMQHandler(logging.Handler):
    """
    Logging handler that forwards logs to RabbitMQ into logs.exchange (topic).
    """

    def __init__(
        self,
        service_name: str,
        rabbitmq_config: RabbitMQConfig,
        level: int = logging.INFO,
    ):
        super().__init__(level)
        self.service_name = service_name
        self.rabbitmq_config = rabbitmq_config

        # Exchange configuration for logs
        self.exchange = "logs.exchange"
        self.exchange_type = "topic"

        # Useful metadata
        self.host = socket.gethostname()

    def emit(self, record: logging.LogRecord) -> None:
        """
        Send a log record to RabbitMQ as a JSON message.
        """
        try:
            # Python logging levels → routing_key format
            routing_key = f"{self.service_name}.{record.levelname.lower()}"

            # Optional contextual audit fields
            client_id = getattr(record, "client_id", None)
            order_id = getattr(record, "order_id", None)

            # Build log message for log_aggregation
            message = {
                "timestamp": datetime.utcnow().isoformat(),
                "service": self.service_name,
                "level": record.levelname,
                "message": record.getMessage(),
                "routing_key": routing_key,
                "host": self.host,

                # Automatic capture
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
            }

            if client_id is not None:
                message["client_id"] = client_id

            if order_id is not None:
                message["order_id"] = order_id

            # Publish the log using topic exchange
            with RabbitMQPublisher(
                queue="",  
                rabbitmq_config=self.rabbitmq_config,
                exchange=self.exchange,
                exchange_type=self.exchange_type,
                routing_key=routing_key,
            ) as publisher:
                publisher.publish(message)

        except Exception as e:
            print(f"[RabbitMQHandler ERROR] {e}", file=sys.stderr)

    def log_message(self, *args):
        """
        Suppress default HTTP logs from frameworks like Uvicorn.
        """
        pass


def setup_rabbitmq_logging(
    service_name: str,
    rabbitmq_config: RabbitMQConfig,
    level: int = logging.INFO,
):

    handler = RabbitMQHandler(service_name, rabbitmq_config, level)
    root_logger = logging.getLogger()

    root_logger.setLevel(level) 
    root_logger.addHandler(handler)

    logging.info(
        f" RabbitMQ logging configured for service '{service_name}' "
        f"(level={logging.getLevelName(level)})"
    )


def log_with_context(
    logger: logging.Logger,
    level: int,
    message: str,
    client_id: Optional[int] = None,
    order_id: Optional[int] = None,
):
    """
    Helper to include contextual fields (client_id, order_id).
    """
    extra = {}
    if client_id is not None:
        extra["client_id"] = client_id
    if order_id is not None:
        extra["order_id"] = order_id

    logger.log(level, message, extra=extra)
