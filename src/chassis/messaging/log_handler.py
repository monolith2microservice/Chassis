from datetime import datetime
from typing import Callable, Type, Any
import logging

from .types import MessageType
from .listener import register_queue_handler

logger = logging.getLogger(__name__)


def create_log_handler(
    *,
    session_factory: Callable[[], Any],
    log_model: Type[Any],
    exchange_name: str = "logs.exchange",
    queue_name: str = "logs.aggregator",
    routing_key: str = "*.#",
):


    @register_queue_handler(
        queue=queue_name,
        exchange=exchange_name,
        exchange_type="topic",
        routing_key=routing_key,
    )
    def _log_handler(message: MessageType) -> None:
        """Stores incoming log messages using the provided ORM model."""
        try:
            timestamp = message.get("timestamp")
            service = message.get("service")
            level = message.get("level")
            text = message.get("message")

            # Required fields check
            if not all([timestamp, service, level, text]):
                logger.error("Missing required fields in log message")
                return

            # Normalize fields
            try:
                timestamp_dt = datetime.fromisoformat(str(timestamp))
            except ValueError:
                logger.error(f"Invalid timestamp format: {timestamp}")
                return

            module = message.get("module")
            function = message.get("function")
            line = message.get("line")
            client_id = message.get("client_id")
            order_id = message.get("order_id")

            # Open database session
            session = session_factory()
            try:
                log_entry = log_model(
                    timestamp=timestamp_dt,
                    service=str(service),
                    level=str(level).upper(),
                    message=str(text),
                    module=str(module) if module else None,
                    function=str(function) if function else None,
                    line=int(line) if line is not None else None,
                    client_id=int(client_id) if client_id is not None else None,
                    order_id=int(order_id) if order_id is not None else None,
                )

                session.add(log_entry)
                session.commit()

                # Local logging for debug
                logger.debug(
                    f"Log stored: {service}.{level} - "
                    f"{text[:50]}{'...' if len(text) > 50 else ''}"
                )
            finally:
                session.close()

        except Exception as e:
            logger.exception(f"Failed to store log: {e}")

    return _log_handler
