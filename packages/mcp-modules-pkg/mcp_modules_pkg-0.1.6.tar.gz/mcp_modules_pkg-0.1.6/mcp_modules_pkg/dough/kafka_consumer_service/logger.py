import logging


def setup_logger(consumer_name: str):
    """Set up logging configuration for the consumer.

    Args:
        consumer_name (str): Name of the consumer for logging.
    """
    logging.basicConfig(
        filename=f"/app/logs/{consumer_name}.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
