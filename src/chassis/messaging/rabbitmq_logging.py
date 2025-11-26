import logging
import sys
from datetime import datetime
from typing import Optional

from chassis.messaging import RabbitMQPublisher, RabbitMQConfig


class RabbitMQHandler(logging.Handler):

    def __init__(
        self,
        service_name: str,
        rabbitmq_config: RabbitMQConfig,
        level: int = logging.INFO,
    ):
        super().__init__(level)
        self.service_name = service_name
        self.rabbitmq_config = rabbitmq_config

        # Exchange for logs
        self.exchange = "logs.exchange"
        self.exchange_type = "topic"

    def emit(self, record: logging.LogRecord) -> None:
        """
        Send a log record to RabbitMQ as a JSON message.
        """
        try:
            routing_key = f"{self.service_name}.{record.levelname.lower()}"
            queue = f"logs.{self.service_name}"

            # Optional contextual audit fields
            client_id = getattr(record, "client_id", None)
            order_id = getattr(record, "order_id", None)

            # Prepare the message dictionary
            message = {
                "timestamp": datetime.utcnow().isoformat(),
                "service": self.service_name,
                "level": record.levelname,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
            }

            if client_id is not None:
                message["client_id"] = client_id

            if order_id is not None:
                message["order_id"] = order_id

            # Publish message to RabbitMQ
            with RabbitMQPublisher(
                queue=queue,
                rabbitmq_config=self.rabbitmq_config,
                exchange=self.exchange,
                exchange_type=self.exchange_type,
                routing_key=routing_key,
            ) as publisher:
                publisher.publish(message)

        except Exception as e:
            print(f"RabbitMQHandler failed: {e}", file=sys.stderr)

    def log_message(self, *args):
        """Suppress default HTTP logging from frameworks like Uvicorn."""
        pass


def setup_rabbitmq_logging(
    service_name: str,
    rabbitmq_config: RabbitMQConfig,
    level: int = logging.INFO,
):
    """
    Attach RabbitMQ logging handler to the root logger.

    Must be called AFTER logging.config.fileConfig() or basicConfig().
    """
    handler = RabbitMQHandler(service_name, rabbitmq_config, level)
    logging.getLogger().addHandler(handler)
    logging.info(f" RabbitMQ logging configured for '{service_name}'")


def log_with_context(
    logger: logging.Logger,
    level: int,
    message: str,
    client_id: Optional[int] = None,
    order_id: Optional[int] = None,
):

    extra = {}
    if client_id is not None:
        extra["client_id"] = client_id
    if order_id is not None:
        extra["order_id"] = order_id

    logger.log(level, message, extra=extra)
