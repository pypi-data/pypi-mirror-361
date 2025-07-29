
import pymongo

from .base import DbApiBase

class MongoDB(DbApiBase):
    """Handles MongoDB database operations.

    Utilizes the given connection ID to establish and manage connections to a MongoDB database.
    This class provides a method to connect to the database and retrieve the current connection instance.

    Attributes:
        conn_id (str): Connection ID for the MongoDB database
    """

    def __init__(self, mongo_conn_id: str):
        """Initializes the MongoDB class with a connection ID.

        Sets up the MongoDB class instance with the specified connection ID and attempts to establish 
        a connection to the MongoDB database using this ID.

        Args:
            mongo_conn_id (str): Connection ID for the MongoDB database.
        """
        super().__init__()
        self.conn_id = mongo_conn_id
        self.connect()

    def connect(self):
        """Establishes a connection to the MongoDB database.

        Utilizes the connection ID provided during class initialization to connect to the MongoDB database.
        This method attempts to create a MongoClient instance with the connection parameters. On failure,
        it prints an error message and exits the application.

        Raises:
            ConnectionError: If connection to the MongoDB database fails.
        """
        conn = self.get_connection(self.conn_id)
        try:
            self.conn = pymongo.MongoClient(
                host=conn.host,
                port=conn.port,
                username=conn.login,
                password=conn._password,
            )
        except ConnectionError:
            print("Connection Error")
            exit()

    def get_conn(self) -> pymongo.MongoClient:
        """Retrieves the current MongoDB connection.

        Returns the MongoClient instance representing the current connection to the MongoDB database.

        Returns:
            pymongo.MongoClient: The current MongoDB connection.
        """
        return self.conn


class MongoDBAirflowHook(MongoDB):
    """Extends MongoDB to specifically support Airflow's hook system.

    This subclass of the MongoDB class is tailored to integrate with Apache Airflow, leveraging Airflow's hook system
    for MongoDB interactions. It provides an additional method to retrieve an Airflow MongoHook instance for database operations.

    Attributes:
        conn_id (str): Connection ID for the MongoDB database.
    """

    def __init__(self, mongo_conn_id: str):
        """Initializes the MongoDBAirflowHook class with a connection ID.

        Sets up the MongoDBAirflowHook instance with the specified connection ID, intended for use within Apache Airflow.

        Args:
            mongo_conn_id (str): Connection ID for the MongoDB database.
        """
        super().__init__(mongo_conn_id)
        self.conn_id = mongo_conn_id

    def get_hook(self):
        """Retrieves an instance of Airflow's MongoDB hook.

        Creates and returns an instance of the MongoHook class from Airflow's provider package, which can be used
        for MongoDB operations within Airflow's ecosystem.

        Returns:
            MongoHook: An instance of Airflow's MongoHook class for MongoDB operations.
        """
        from airflow.providers.mongo.hooks.mongo import MongoHook

        hook = MongoHook(conn_id=self.conn_id)
        return hook

    def connect(self):
        """Overrides the connect method to use Airflow's MongoHook for connection.

        Instead of establishing a direct connection to MongoDB, this method utilizes Airflow's MongoHook to connect,
        aligning with Airflow's standardized mechanisms for database interactions.

        """
        hook = self.get_hook()
        self.conn = hook.get_conn()

