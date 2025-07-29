
import configparser
import os
from cryptography.fernet import Fernet
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

ID_LEN = 250

PATH = os.path.join(os.path.dirname(__file__), 'db.cfg')

class DataBase:
    """Manages database configurations and connections.

    This class is responsible for reading the database configuration from a file,
    creating a Fernet instance for encryption/decryption, and initializing the database engine
    and session.
    """

    def get_config():
        """Reads database configuration from a file and returns it as a dictionary.

        Returns:
            dict: A dictionary containing database connection details and Fernet key
        """
        reader = configparser.RawConfigParser()
        reader.read(PATH)
        config = {
            # "host": reader.get("client", "host"),
            # "port": int(reader.get("client", "port")),
            # "user": reader.get("client", "user"),
            # "password": reader.get("client", "password"),
            # "key": reader.get("client", "fernetkey"),
        }
        return config

    @staticmethod
    def get_fernet():
        """Creates a Fernet instance using the key from the database configuration.

        Returns:
            Fernet: An instance of Fernet for encryption and decryption.
        """
        config = DataBase.get_config()
        fernet = Fernet(config["key"])
        return fernet

    # config = get_config()
    # DATABASE_URL = (
    #     f"postgresql://{config['user']}:{config['password']}@{config['host']}/airflow"
    # )
    # engine = create_engine(DATABASE_URL)
    # session_local = sessionmaker(autocommit=False, autoflush=True, bind=engine)

