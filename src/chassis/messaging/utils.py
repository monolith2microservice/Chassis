from .listener import RabbitMQListener
from .types import (
    _HandlerFunc,
    MessageType,
    RabbitMQConfig,
)
from typing import (
    Callable,
    Dict,
    Optional,
    Tuple,
)
import asyncio
import logging

# Global Variables ############################################################
logger = logging.getLogger(__name__)
_QUEUE_HANDLERS: Dict[str, Tuple[_HandlerFunc, Optional[Dict[str, str]]]] = {}

# Functions ###################################################################
def register_queue_handler(
    queue: str,
    exchange: Optional[str] = None,
    exchange_type: str = "direct",
    routing_key: Optional[str] = None,
) -> Callable[[_HandlerFunc], _HandlerFunc]:
    def decorator(func: _HandlerFunc) -> _HandlerFunc:
        exchange_config = None
        if exchange is not None:
            exchange_config = {
                "exchange": exchange,
                "exchange_type": exchange_type,
                "routing_key": routing_key if routing_key is not None else queue,
            }
        
        _QUEUE_HANDLERS[queue] = (func, exchange_config)
        handler_type = "async" if asyncio.iscoroutinefunction(func) else "sync"
        exchange_info = f" (exchange: {exchange}, type: {exchange_type})" if exchange else " (default exchange)"
        logger.info(f"Registered {handler_type} handler for queue: {queue}{exchange_info}")
        return func
    return decorator

def _process_message(message: MessageType, queue: str):
    """Process incoming RabbitMQ messages."""
    try:
        handler, _ = _QUEUE_HANDLERS[queue]
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
    one_use: bool = False,
) -> None:
    """
    Start RabbitMQ listener in a separate thread.
    Uses exchange configuration from the registered handler decorator.
    """
    try:
        # Get the exchange configuration for this queue
        if queue not in _QUEUE_HANDLERS:
            raise ValueError(f"No handler registered for queue: {queue}")
        
        _, exchange_config = _QUEUE_HANDLERS[queue]

        # Delete if queue is one use
        if one_use:
            del _QUEUE_HANDLERS[queue]
        
        # Create listener with appropriate exchange configuration
        listener_kwargs = {
            "logger": logger,
            "queue": queue,
            "rabbitmq_config": config,
        }
        
        if exchange_config:
            listener_kwargs.update(exchange_config)
        
        with RabbitMQListener(**listener_kwargs) as listener:
            logger.info(
                f"RabbitMQ listener connected to queue: {queue}"
            )
            listener.consume(
                callback=_process_message, 
                one_use=one_use
            )
    except KeyboardInterrupt:
        logger.info("RabbitMQ listener stopped by keyboard interrupt")
    except Exception as e:
        print(f"Exc: {e}")
        logger.error(f"RabbitMQ listener error: {e}", exc_info=True)