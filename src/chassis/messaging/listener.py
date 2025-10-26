from .client import RabbitMQBaseClient
from .types import (
    MessageType,
    RabbitMQConfig,
)
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import (
    Basic,
    BasicProperties,
)
from typing import (
    Callable,
    Optional,
)
import json
import logging
import sys

class RabbitMQListener(RabbitMQBaseClient):
    """RabbitMQ listener with TLS support"""
    def __init__(
        self,
        logger: logging.Logger,
        queue: str,
        rabbitmq_config: RabbitMQConfig,
        exchange: Optional[str] = None,
        exchange_type: str = "direct",
        routing_key: Optional[str] = None,
    ) -> None:
        super().__init__(
            queue=queue, 
            rabbitmq_config=rabbitmq_config,
            exchange=exchange,
            exchange_type=exchange_type,
            routing_key=routing_key,
        )
        self._logger = logger

    def _parse_json(
        self, 
        body: bytes, 
        content_type: str
    ) -> MessageType:
        assert content_type == RabbitMQBaseClient._CONTENT_TYPE, "Only valid content should be processed."
        decoded_str = body.decode()
        return json.loads(decoded_str)

    def consume(
        self,
        callback: Callable[[MessageType, str], None],
        auto_ack: bool = False,
    ) -> None:
        """
        Start consuming messages.
        
        Args:
            callback: Function called for each message. 
                     Signature: callback(message, delivery, properties)
            auto_ack: Whether to automatically acknowledge messages
        """
        def _on_message(
            ch: BlockingChannel,
            method: Basic.Deliver,
            properties: BasicProperties,
            body: bytes
        ) -> None:
            try:
                assert properties.content_type is not None, "Content type must be set."
                message = self._parse_json(
                    body=body,
                    content_type=properties.content_type,
                )
                callback(message, self._queue)

                # Manual acknowledgment if not auto_ack
                if not auto_ack:
                    ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                self._logger.error(f"Failed to process message: {e}", exc_info=True)
                
                if not auto_ack:
                    ch.basic_nack(
                        delivery_tag=method.delivery_tag,
                        requeue=False
                    )                
            

        if self._channel is None:
            raise RuntimeError("Not connected. Make sure it is connected.")
        
        # Start consuming
        self._channel.basic_consume(
            queue=self._queue,
            on_message_callback=_on_message,
            auto_ack=auto_ack,
        )

        self._logger.info(f"Started consuming from queue: {self._queue}")
        try:
            self._channel.start_consuming()
        except KeyboardInterrupt:
            self._logger.info("Interrupted by user")
            self._channel.stop_consuming()

#### EXAMPLES
# # Custom topic exchange (automatic binding)
# listener = RabbitMQListener(
#     logger=logger,
#     queue="logs_queue",
#     rabbitmq_config=config,
#     exchange="logs",
#     exchange_type="topic",
#     routing_key="app.*.error"  # Topic pattern
# )
