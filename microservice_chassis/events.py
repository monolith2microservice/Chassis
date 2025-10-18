import json, time, ssl, pika, logging
from pika.exchange_type import ExchangeType
from .config import settings

logger = logging.getLogger(__name__)

class EventPublisher:
    """Reusable RabbitMQ publisher for microservices."""

    def __init__(self, exchange: str = None):
        self.exchange = exchange or f"{settings.SERVICE_NAME}.events"
        self.connection = None
        self.channel = None

    def connect(self):
        """Connects to RabbitMQ (retrying several times)."""
        context = ssl.create_default_context()
        for _ in range(5):
            try:
                params = pika.URLParameters(settings.RABBITMQ_URL)
                params.ssl_options = pika.SSLOptions(context)
                self.connection = pika.BlockingConnection(params)
                self.channel = self.connection.channel()
                self.channel.exchange_declare(exchange=self.exchange, exchange_type=ExchangeType.topic)
                logger.info("Connected to RabbitMQ exchange: %s", self.exchange)
                return
            except pika.exceptions.AMQPConnectionError:
                logger.warning("RabbitMQ not ready, retrying...")
                time.sleep(2)
        raise RuntimeError("Could not connect to RabbitMQ")

    def publish(self, topic: str, payload: dict):
        """Publishes a JSON event to RabbitMQ."""
        if not self.channel:
            self.connect()
        body = json.dumps(payload)
        self.channel.basic_publish(exchange=self.exchange, routing_key=topic, body=body.encode("utf-8"))
        logger.info("Event published: %s -> %s", topic, payload)
