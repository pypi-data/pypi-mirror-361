from abc import ABC, abstractmethod

import pandas as pd

from .connection import Connection


class DbApiBase(ABC):
    """Abstract base class for database API operations.

    This class provides template methods for connecting to a database,
    getting a database connection, and executing a query to return data as a pandas DataFrame.

    Attributes:
        conn (Connection): The database connection object. Initialized as None and should be
        set by the `connect` method of subclasses
    """

    conn = None

    @abstractmethod
    def connect(self):
        """Abstract method to establish a database connection.

        This method must be implemented by subclasses to establish the database connection
        and assign it to the `conn` attribute.
        """
        ...

    def get_connection(self, conn_id: str) -> "Connection":
        """Gets the database connection information based on a connection ID.

        This method retrieves and returns the database connection information associated with
        the specified connection ID.

        Args:
            conn_id (str): The connection ID used to retrieve the database connection.

        Returns:
            Connection: The database connection associated with the specified connection ID.
        """
        return Connection.get_connection(conn_id=conn_id)

    def query(self, sql: str, params: tuple = None) -> pd.DataFrame:
        """Executes a SQL query and returns the results as a pandas DataFrame.

        This method connects to the database, executes the specified SQL query, and returns
        the results as a pandas DataFrame. The database connection is closed after
        retrieving the data.

        Args:
            sql (str): The SQL query to be executed.
            params (tuple, optional): Parameters for the SQL query. Defaults to None.

        Returns:
            pd.DataFrame: The results of the query as a pandas DataFrame.

        Raises:
            pd.io.sql.DatabaseError: If there is an error executing the query.
            pd.errors.DatabaseError: If there is a database error while executing the query.
        """
        df: pd.DataFrame = pd.DataFrame()

        self.connect()
        try:
            if params:  # ✅ params가 존재하면 바인딩된 SQL 실행
                df = pd.read_sql(sql, self.conn, params=params)
            else:  # ✅ params가 없으면 기존 방식 실행
                df = pd.read_sql(sql, self.conn)
        except (pd.io.sql.DatabaseError, pd.errors.DatabaseError):
            raise
        finally:
            self.conn.close()
        return df

    def execute_parameterized(self, sql: str, params: tuple) -> any:
        """Executes a parameterized SQL query synchronously.

        Args:
            sql (str): SQL query string with placeholders.
            params (tuple): Tuple of parameters to replace the placeholders in the SQL query.

        Returns:
            any: The result of the query execution.
        """
        try:
            self.connect()
            cur = self.conn.cursor()
            ret = cur.execute(sql, params)
            self.conn.commit()
            self.conn.close()
            return ret
        except Exception as e:
            print(e)
            raise
