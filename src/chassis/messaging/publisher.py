from .client import RabbitMQBaseClient
from .types import (
    RabbitMQConfig,
    MessageType
)
from pika import BasicProperties
from typing import Optional
import json

class RabbitMQPublisher(RabbitMQBaseClient):
    """RabbitMQ publisher with TLS support"""
    def __init__(
        self,
        rabbitmq_config: RabbitMQConfig
    ) -> None:
        super().__init__(rabbitmq_config)

    def publish(
        self,
        message: MessageType,
        exchange: Optional[str] = None,
        persistent: bool = True,
    ) -> None:
        """
        Publish a message to RabbitMQ.
        
        Args:
            routing_key: Routing key (queue name for default exchange)
            message: Message to publish (will be JSON serialized if dict/list)
            exchange: Exchange name (uses instance default if None)
            persistent: Whether message should survive broker restart
        """
        if self._channel is None:
            raise RuntimeError("Not connected. Make sure it is connected.")
        
        # Serialize message
        body = json.dumps(message)
        
        # Message properties
        properties = BasicProperties(
            content_type=super()._CONTENT_TYPE,
            delivery_mode=2 if persistent else 1,
        )

        # Publish message
        self._channel.basic_publish(
            exchange=exchange if exchange is not None else "",
            routing_key=self._queue,
            body=body,
            properties=properties,
        )