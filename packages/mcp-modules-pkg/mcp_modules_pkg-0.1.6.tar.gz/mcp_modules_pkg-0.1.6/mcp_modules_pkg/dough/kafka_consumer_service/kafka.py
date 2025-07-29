import functools
import logging
import time
from datetime import datetime, timedelta

from confluent_kafka import Consumer, KafkaError, KafkaException, Producer
from dough.db_connector.mysql import Mysql
from dough.kafka_consumer_service.logger import setup_logger


class KafkaDatabase:
    """Singleton class to handle MySQL database operations for Kafka.

    Author: 
        tskim.
    """

    _instance = None

    def __new__(cls):
        """Create a new instance of KafkaDatabase if it does not exist."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.db = Mysql("idb_kafkaops")
        return cls._instance

    def get_bootstrap_servers(self) -> str:
        """Get the bootstrap servers for Kafka.

        Returns:
            str: The bootstrap servers for Kafka.
        """
        if not hasattr(self, "_bootstrap_servers"):
            sql = "SELECT * FROM view_kafka_ui WHERE cluster_name='bi'"
            self._bootstrap_servers = self.db.query(sql)["bootstrap_servers"].iloc[0]
        return self._bootstrap_servers


class KafkaBase:
    """Base class for Kafka operations.

    Attributes:
        db (KafkaDatabase): Instance of KafkaDatabase for database operations.
    
    Author: 
        tskim.
    """

    def __init__(self, logger_name: str = None):
        """Initialize the KafkaBase class.

        Args:
            logger_name (str): Name of the logger to set up.
        """
        if logger_name is not None:
            setup_logger(logger_name)
        self.db = KafkaDatabase()

    def get_bootstrap_servers(self) -> str:
        """Get the bootstrap servers for Kafka.

        Returns:
            str: The bootstrap servers for Kafka.
        """
        return self.db.get_bootstrap_servers()


class RoesettaProducer(KafkaBase):
    """Producer class for sending messages to Kafka.

    Author: 
        tskim.
    """

    _instance = None  # Singleton applied

    def __new__(cls):
        """Create a new instance of RoesettaProducer if it does not exist."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        """Initialize the RoesettaProducer class.

        Args:
            **kwargs: Additional keyword arguments for Producer configuration.
        """
        super().__init__()
        if not hasattr(self, "producer"):
            default_config = {"bootstrap.servers": self.get_bootstrap_servers()}
            producer_config = {**default_config, **kwargs}
            self.producer = Producer(producer_config)

    def __call__(self, func):
        """Decorator to handle Kafka message processing.

        Args:
            func: The function to be decorated.

        Returns:
            function: The wrapper function for Kafka message processing.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(self.producer, *args, **kwargs)
            except Exception as e:
                logging.error(f"Error in {func.__name__}: {e}")
                raise

        return wrapper


class RosettaConsumer(KafkaBase):
    """Consumer class for receiving messages from Kafka.

    Author: 
        tskim.
    """

    def __init__(self, topic: str, group_id: str, delayed_seconds: int, **kwargs):
        """Initialize the RosettaConsumer class.

        Args:
            topic (str): The Kafka topic to consume messages from.
            group_id (str): The consumer group ID.
            delayed_seconds (int): The delay threshold in seconds for processing messages.
            **kwargs: Additional keyword arguments for Consumer configuration.
        """
        super().__init__(topic)
        # Set Consumer
        default_config = {
            "bootstrap.servers": self.get_bootstrap_servers(),
            "group.id": group_id,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
        consumer_config = {**default_config, **kwargs}
        self.consumer = Consumer(consumer_config)

        self.delayed_seconds = delayed_seconds
        self.topic = topic
        logging.info(f"Consumer created for topic: {self.topic}")

    def is_delay_elapsed(self, msg):
        """Check if the message delay has elapsed.

        Args:
            msg: The Kafka message to check.

        Returns:
            bool: True if the delay has elapsed, False otherwise.
        """
        msg_timestamp = datetime.fromtimestamp(msg.timestamp()[1] / 1000)
        current_time = datetime.now()
        return (current_time - msg_timestamp) >= timedelta(seconds=self.delayed_seconds)

    def __call__(self, func):
        """Decorator to handle Kafka message processing.

        Args:
            func: The function to be decorated.

        Returns:
            function: The wrapper function for Kafka message processing.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):  # Remove `self`
            self.consumer.subscribe([self.topic])
            self.consumer.poll(0)   # → assignment 강제
            self.consumer.commit()
            pending_messages = []

            try:
                while True:
                    msg = self.consumer.poll(timeout=1.0)
                    if msg is None and not pending_messages:
                        time.sleep(0.1)
                        continue  # If there are no messages and no pending messages, move to the next poll()

                    # Process delayed messages
                    for delayed_msg in pending_messages[:]:
                        if self.is_delay_elapsed(delayed_msg):
                            try:
                                func(delayed_msg, *args, **kwargs)
                                self.consumer.commit(delayed_msg)
                                pending_messages.remove(delayed_msg)  # Remove if successful
                            except Exception as e:
                                logging.error(f"Failed to process delayed message: {e}")

                    if msg is None:
                        continue  # If there are no new messages, go back to poll()

                    if msg.error():
                        if msg.error().code() == KafkaError._PARTITION_EOF:
                            logging.info(
                                f"Reached end of partition: {msg.topic()} [{msg.partition()}] at offset {msg.offset()}"
                            )
                            continue
                        else:
                            raise KafkaException(msg.error())

                    if self.is_delay_elapsed(msg):
                        try:
                            func(msg, *args, **kwargs)
                            self.consumer.commit(msg)  # Commit if processing is successful
                        except Exception as e:
                            logging.error(f"Failed to process message: {e}")
                    else:
                        logging.info("Delaying message...")
                        pending_messages.append(msg)

            except KeyboardInterrupt:
                logging.info("Consumer stopped by user.")
            except KafkaException as e:
                logging.error(f"Kafka Exception occurred: {e}")
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
            finally:
                self.consumer.commit()
                self.consumer.close()

        return wrapper
