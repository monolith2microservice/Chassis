from .listener import RabbitMQListener
from .types import (
    _HandlerFunc,
    MessageType,
    RabbitMQConfig,
)
from typing import (
    Any,
    Callable,
    Dict,
    LiteralString,
)
import asyncio
import logging

# Global Variables ############################################################
logger = logging.getLogger(__name__)
_QUEUE_HANDLERS: Dict[str, _HandlerFunc] = {}

# Functions ###################################################################
def register_queue_handler(
    queue: LiteralString
) -> Callable[[_HandlerFunc], _HandlerFunc]:
    """Decorator to register sync or async event handlers"""
    def decorator(func: _HandlerFunc) -> _HandlerFunc:
        _QUEUE_HANDLERS[queue] = func
        handler_type = "async" if asyncio.iscoroutinefunction(func) else "sync"
        logger.info(f"Registered {handler_type} handler for queue: {queue}")
        return func
    return decorator

def _process_message(message: MessageType, queue: str):
    """Process incoming RabbitMQ messages."""
    try:
        handler = _QUEUE_HANDLERS[queue]
        if asyncio.iscoroutinefunction(handler):
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(handler(message))
            except RuntimeError:
                asyncio.run(handler(message))
        else:
            handler(message)
    except Exception as e:
        logger.error(f"Error processing event: {e}", exc_info=True)
        raise

def start_rabbitmq_listener(
    queue: str,
    config: RabbitMQConfig,
) -> None:
    """Start RabbitMQ listener in a separate thread."""
    try:
        with RabbitMQListener(
            logger=logger,
            rabbitmq_config=config,
        ) as listener:
            logger.info(
                f"RabbitMQ listener connected to queue: {queue}"
            )
            listener.consume(_process_message)
    except KeyboardInterrupt:
        logger.info("RabbitMQ listener stopped by keyboard interrupt")
    except Exception as e:
        logger.error(f"RabbitMQ listener error: {e}", exc_info=True)