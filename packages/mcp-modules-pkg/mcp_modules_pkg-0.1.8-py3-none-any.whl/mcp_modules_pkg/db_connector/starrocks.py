
import os
import jaydebeapi

from .base import DbApiBase

class Starrocks(DbApiBase):
    """Handles Starrocks database operations.

    Attributes:
        conn_id (str): Connection ID for the Starrocks database.
        connection: The database connection object.
        conn: The active database connection.

    Author:
        tskim.
    """

    def __init__(self, starrocks_conn_id: str):
        """Initializes the Starrocks class with a connection ID.

        Args:
            starrocks_conn_id (str): Connection ID for the Starrocks database.
        """
        super().__init__()
        self.conn_id = starrocks_conn_id
        self.connection = self.get_connection(self.conn_id)

    def connect(self):
        """Establishes a connection to the Starrocks database.

        Raises:
            ConnectionError: If the connection to the database fails.
        """
        try:
            module_path = os.path.dirname(os.path.abspath(__file__))
            conn = jaydebeapi.connect(
                "com.mysql.cj.jdbc.Driver",
                f"jdbc:mysql:loadbalance://{self.connection.host}",
                [f"{self.connection.login}", f"{self.connection._password}"],
                f"{module_path}/mysql-connector-j-9.0.0.jar"
            )
            self.conn = conn
            print("Successfully connected to Starrocks")
        except ConnectionError:
            print("Connection Error.")
            raise

