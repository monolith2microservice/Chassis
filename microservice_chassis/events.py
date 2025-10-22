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
        """Connects to RabbitMQ (retrying several times) using client cert auth."""
        cafile = "/etc/rabbitmq/ssl/ca_cert.pem"
        client_cert = "/etc/rabbitmq/ssl/client_cert.pem"
        client_key = "/etc/rabbitmq/ssl/client_key.pem"

        # Create SSL context that presents a client cert and verifies server with CA
        context = ssl.create_default_context(cafile=cafile)
        # load client's cert + key so RabbitMQ (which requires client cert) accepts us
        context.load_cert_chain(certfile=client_cert, keyfile=client_key)

        for _ in range(5):
            try:
                params = pika.URLParameters(settings.RABBITMQ_URL)  # should be amqps://...
                params.ssl_options = pika.SSLOptions(context)
                self.connection = pika.BlockingConnection(params)
                self.channel = self.connection.channel()

                # Exchange durable
                self.channel.exchange_declare(
                    exchange=self.exchange,
                    exchange_type=ExchangeType.topic,
                    durable=True
                )

                logger.info("Connected to RabbitMQ exchange: %s", self.exchange)
                return
            except pika.exceptions.AMQPConnectionError as e:
                logger.warning("RabbitMQ not ready, retrying... (%s)", e)
                time.sleep(2)

        raise RuntimeError("Could not connect to RabbitMQ")


    def publish(self, topic: str, payload: dict):
        if not self.channel:
            self.connect()
        body = json.dumps(payload)
        properties = pika.BasicProperties(delivery_mode=2, content_type="application/json")
        self.channel.basic_publish(
            exchange=self.exchange,
            routing_key=topic,
            body=body.encode("utf-8"),
            properties=properties
        )
        logger.info("Event published: %s -> %s", topic, payload)
    
    def close(self):
        """Cierra la conexión con RabbitMQ si está abierta."""
        try:
            if self.channel and self.channel.is_open:
                self.channel.close()
            if self.connection and self.connection.is_open:
                self.connection.close()
            logger.info("RabbitMQ connection closed cleanly.")
        except Exception as e:
            logger.warning("Error closing RabbitMQ connection: %s", e)


    

class EventSubscriber:
    """Reusable RabbitMQ subscriber with durable queue."""

    def __init__(self, exchange: str = None, queue_name: str = None):
        self.exchange = exchange or f"{settings.SERVICE_NAME}.events"
        self.queue_name = queue_name or f"{settings.SERVICE_NAME}.queue"
        self.connection = None
        self.channel = None

    def connect(self):
        """Connects and declares durable exchange/queue using client cert auth."""
        cafile = "/etc/rabbitmq/ssl/ca_cert.pem"
        client_cert = "/etc/rabbitmq/ssl/client_cert.pem"
        client_key = "/etc/rabbitmq/ssl/client_key.pem"

        context = ssl.create_default_context(cafile=cafile)
        context.load_cert_chain(certfile=client_cert, keyfile=client_key)

        for _ in range(5):
            try:
                params = pika.URLParameters(settings.RABBITMQ_URL)
                params.ssl_options = pika.SSLOptions(context)
                self.connection = pika.BlockingConnection(params)
                self.channel = self.connection.channel()

                # Exchange y cola durables
                self.channel.exchange_declare(
                    exchange=self.exchange,
                    exchange_type=ExchangeType.topic,
                    durable=True
                )
                self.channel.queue_declare(queue=self.queue_name, durable=True)
                logger.info("Connected to RabbitMQ exchange: %s", self.exchange)
                return
            except pika.exceptions.AMQPConnectionError as e:
                logger.warning("RabbitMQ not ready, retrying... (%s)", e)
                time.sleep(2)

        raise RuntimeError("Could not connect to RabbitMQ")


    async def listen(self, routing_key: str):
        """Async generator that yields incoming messages."""
        import asyncio

        if not self.channel:
            self.connect()

        self.channel.queue_bind(exchange=self.exchange, queue=self.queue_name, routing_key=routing_key)
        logger.info("Subscribed to topic: %s", routing_key)

        loop = asyncio.get_event_loop()
        queue = asyncio.Queue()

        def callback(ch, method, properties, body):
            try:
                msg = json.loads(body.decode("utf-8"))
                loop.call_soon_threadsafe(queue.put_nowait, msg)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.error("Error processing message: %s", e)
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        self.channel.basic_consume(queue=self.queue_name, on_message_callback=callback, auto_ack=False)

        def run_consumer():
            try:
                self.channel.start_consuming()
            except Exception as e:
                logger.error("Consumer stopped: %s", e)

        import threading
        threading.Thread(target=run_consumer, daemon=True).start()

        while True:
            message = await queue.get()
            yield message
