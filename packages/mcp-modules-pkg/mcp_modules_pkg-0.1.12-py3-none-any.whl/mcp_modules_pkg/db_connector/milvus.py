
from .base import DbApiBase
from pymilvus import connections, Collection


class MilvusConnectionInfo(DbApiBase):
    """Handles Milvus database connection information and operations.

    Attributes:
        conn_id (str): Connection ID for the Milvus database.
        conn (Connection): Connection object for the Milvus database
    """

    def __init__(self, conn_id: str) -> 'Connection':
        """Initializes the MilvusConnectionInfo class with a connection ID and establishes the connection.

        Args:
            conn_id (str): Connection ID for the Milvus database.
        """
        super().__init__()
        self.conn_id = conn_id
        self.conn = self.get_connection(conn_id=conn_id)

    def connect(self):
        """Establishes a connection to the Milvus database. Implementation not provided."""
        ...

    def drop_table(self, table_name: str) -> None:
        """Drop a table from the Milvus database.

        Args:
            table_name (str): mangobot_ai
        """
        connections.connect(host=self.conn.host, port=self.conn.port)
        collection = Collection(table_name)
        collection.drop()