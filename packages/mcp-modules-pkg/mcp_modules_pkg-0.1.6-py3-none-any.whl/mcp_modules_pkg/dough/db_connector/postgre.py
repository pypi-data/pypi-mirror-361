
import psycopg2

from .base import DbApiBase

class Postgres(DbApiBase):
    """Handles PostgreSQL database operations.

    Attributes:
        conn_id (str): Connection ID for the PostgreSQL database.
    """

    def __init__(self, postgres_conn_id: str):
        """Initializes the Postgres class with a connection ID.

        Args:
            postgres_conn_id (str): Connection ID for the PostgreSQL database
        """
        super().__init__()
        self.conn_id = postgres_conn_id

    def connect(self):
        """Establishes a connection to the PostgreSQL database.

        Uses the connection ID to obtain database connection details and attempts to establish a connection.
        If connection fails, prints an error message and exits the program.
        """
        conn = self.get_connection(self.conn_id)
        try:
            self.conn = psycopg2.connect(
                host=conn.host,
                port=conn.port,
                user=conn.login,
                password=conn._password,
                dbname=conn.schema,
            )
        except ConnectionError:
            print("Connection Error")
            exit()

    def execute(self, sql: str):
        """Executes a SQL command on the PostgreSQL database.

        First, attempts to connect to the database. Then, creates a cursor and executes the given SQL command.
        Commits the transaction and closes the connection afterwards.

        Args:
            sql (str): The SQL command to be executed.

        Returns:
            The result of the SQL command execution.
        """
        try:
            self.connect()
            cur = self.conn.cursor()
            ret = cur.execute(sql)
            self.conn.commit()
            self.conn.close()
            return ret
        except Exception as e:
            print(e)


class PostgresAirflowHook(Postgres):
    """Extends the Postgres class to integrate with Airflow's PostgreSQL hook.

    This class overrides the connect method to use Airflow's PostgresHook for establishing database connections.

    Attributes:
        conn_id (str): Connection ID for the PostgreSQL database.
    """

    def __init__(self, postgres_conn_id: str):
        """Initializes the PostgresAirflowHook class with a connection ID.

        Args:
            postgres_conn_id (str): Connection ID for the PostgreSQL database.
        """
        super().__init__(postgres_conn_id)
        self.conn_id = postgres_conn_id

    def get_hook(self):
        """Retrieves an Airflow PostgresHook instance using the connection ID.

        Returns:
            An instance of Airflow's PostgresHook.
        """
        from airflow.providers.postgres.hooks.postgres import PostgresHook

        hook = PostgresHook(postgres_conn_id=self.conn_id)
        return hook

    def connect(self):
        """Establishes a connection to the PostgreSQL database using Airflow's PostgresHook.

        Overrides the base class's connect method to use Airflow's PostgresHook for connecting to the database.
        """
        hook = self.get_hook()
        self.conn = hook.get_conn()

