import logging

import aiomysql
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.dialects.mysql import insert

from .base import DbApiBase

logger = logging.getLogger("airflow.task")


class Mysql(DbApiBase):
    """Handles MySQL database operations."""

    def __init__(self, mysql_conn_id: str, dbms="mariadb"):
        """Initializes the Mysql class with a connection ID.

        Args:
            mysql_conn_id (str): Connection ID for the MySQL database.
        """
        super().__init__()
        self.conn_id = mysql_conn_id
        self.dbms = dbms
        self.connection = self.get_connection(self.conn_id)

    def connect(self):
        """Establishes a connection to the MySQL database."""
        try:
            if self.dbms == "mariadb":
                url = f"mariadb+pymysql://{self.connection.login}:{self.connection._password}@{self.connection.host}:{self.connection.port}/{self.connection.schema}"
            elif self.dbms == "starrocks" or self.dbms == "mysql":
                url = (
                f"mysql+pymysql://{self.connection.login}:{self.connection._password}"
                f"@{self.connection.host}:{self.connection.port}/{self.connection.schema}"
                )
            self.engine = create_engine(f"{url}?charset=utf8mb4")
            self.conn = self.engine.raw_connection()
        except ConnectionError:
            print("Connection Error")
            raise

    async def connect_async(self):
        """Establishes an asynchronous connection to the MySQL database using aiomysql."""
        try:
            self.pool = await aiomysql.create_pool(
                host=self.connection.host,
                port=self.connection.port,
                user=self.connection.login,
                password=self.connection._password,
                db=self.connection.schema,
                charset="utf8mb4",
                autocommit=True,
            )
        except ConnectionError:
            print("Connection Error")
            raise

    async def async_query(self, sql: str) -> pd.DataFrame:
        """Executes an SQL query asynchronously and returns the results as a DataFrame.

        Args:
            sql (str): SQL query to be executed.

        Returns:
            pd.DataFrame: DataFrame containing the query results.
        """
        await self.connect_async()
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    await cur.execute(sql)
                    result = await cur.fetchall()
                    df = pd.DataFrame(result)
        except Exception as e:
            print(f"An error occurred while executing SQL query: {e}")
            raise
        return df

    def make_sql_insert_duplicatekey_update(self, tablename: str, cols: str, df: pd.DataFrame, chunksize: int) -> str:
        """Generates SQL queries for inserting data into MySQL with duplicate key update.

        Args:
            tablename (str): Name of the table where data will be inserted.
            cols (str): Comma-separated column names.
            df (pd.DataFrame): DataFrame containing the data to be inserted.
            chunksize (int): Number of rows per query.

        Yields:
            str: A SQL query for inserting data with handling duplicate keys.
        """
        df_size = len(df)
        dfs = []
        for i in range(df_size):
            if i * chunksize >= df_size:
                break
            dfs.append(df[i * chunksize : (i + 1) * chunksize])
        qry = ""
        for d in dfs:
            values, set_values = self.get_query_values_from_dataframe(d, cols)
            cols_str = "`" + cols.replace(",", "`,`") + "`"
            qry = f"""
        INSERT INTO {tablename}
            ({cols_str})
        VALUES
            {values}
        ON DUPLICATE KEY
            UPDATE {set_values}
            """
            yield qry

    def make_sql_insert_ignore(self, tablename, cols, df, chunksize):
        df_size = len(df)
        dfs = []
        for i in range(df_size):
            if i * chunksize >= df_size:
                break
            dfs.append(df[i * chunksize : (i + 1) * chunksize])
        for d in dfs:
            values, _ = self.get_query_values_from_dataframe(d, cols)
            cols_str = "`" + cols.replace(",", "`,`") + "`"
            qry = f"INSERT IGNORE INTO {tablename} ({cols_str}) VALUES {values}"
            yield qry

    def get_query_values_from_dataframe(self, df: pd.DataFrame, cols: str) -> (str, str):
        """Generates values and set values strings for SQL queries from a DataFrame.

        Args:
            df (pd.DataFrame): DataFrame containing the data.
            cols (str): Comma-separated column names.

        Returns:
            Tuple[str, str]: (Values string for the SQL query, Set values string for the SQL query's ON DUPLICATE KEY UPDATE clause.)
        """
        import numpy as np

        df = df.replace(np.nan, "NULL")
        clist = cols.split(",")
        rvalues = []
        for _, row in df.iterrows():
            values = []
            for c in clist:
                v = row[c]
                if isinstance(v, str) and v != "NULL":
                    row[c] = str(row[c]).replace('"', '\\"')
                    v = '"' + row[c] + '"'
                else:
                    v = str(v)
                values.append(v)
            rvalues.append("(" + ",".join(values) + ")")

        set_values = []
        for c in clist:
            set_values.append(f"`{c}`=values(`{c}`)")

        values = ",".join(rvalues)
        set_values = ",".join(set_values)

        return values, set_values

    def insert_duplicatekey_update(self, tablename: str, cols: str, df: pd.DataFrame, chunksize: int=1000):
        """Executes SQL queries for inserting data into MySQL with duplicate key update.

        Args:
            tablename (str): Name of the table where data will be inserted.
            cols (str): Comma-separated column names.
            df (pd.DataFrame): DataFrame containing the data to be inserted.
            chunksize (int): Number of rows per query.
        """
        self.connect()
        sql = self.make_sql_insert_duplicatekey_update(tablename, cols, df, chunksize)
        cursor = self.conn.cursor()
        for qry in sql:
            cursor.execute(qry)
        self.conn.commit()
        self.conn.close()

    def insert_ignore(self, tablename: str, cols: str, df: pd.DataFrame, chunksize: int=1000):
        """Executes SQL queries for inserting data into MySQL with ignore option.

        Args:
            tablename (str): Name of the table to insert data into.
            cols (str): Columns to insert data into.
            df (pd.DataFrame): DataFrame containing the data to be inserted.
            chunksize (int, optional): Number of rows to insert in each batch. Defaults to 1000.
        """
        self.connect()
        sql = self.make_sql_insert_ignore(tablename, cols, df, chunksize)
        cursor = self.conn.cursor()
        for qry in sql:
            cursor.execute(qry)
        self.conn.commit()
        self.conn.close()

    def execute(self, sql: str, params: tuple = None):
        """Executes a single SQL query synchronously.

        Args:
            sql (str): SQL query to be executed.
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


class MysqlAirflowHook(Mysql):
    """Extends the Mysql class to integrate with Airflow's MySQL hook for specific Airflow operations."""

    def __init__(self, mysql_conn_id: str):
        """Initializes the MysqlAirflowHook with a connection ID.

        Args:
            mysql_conn_id (str): Connection ID for the MySQL database.
        """
        super().__init__(mysql_conn_id)
        self.conn_id = mysql_conn_id

    def get_hook(self):
        """Retrieves an Airflow MySQL hook instance.

        Returns:
            MySqlHook: An instance of the Airflow MySqlHook class for database operations.
        """
        from airflow.providers.mysql.hooks.mysql import MySqlHook  # pylint: disable=import-outside-toplevel

        hook = MySqlHook(mysql_conn_id=self.conn_id)
        return hook

    def connect(self):
        """Overrides the connect method to establish a connection using Airflow's MySQL hook."""
        hook = self.get_hook()
        self.conn = hook.get_conn()

    def insert_duplicatekey_update(self, tablename: str, cols: str, df: pd.DataFrame, chunksize: int):
        """Overrides the insert_duplicatekey_update method to use Airflow's MySQL hook for database operations.

        Args:
            tablename (str): Name of the table where data will be inserted.
            cols (str): Comma-separated column names.
            df (pd.DataFrame): DataFrame containing the data to be inserted.
            chunksize (int): Number of rows per query.
        """
        sql = self.make_sql_insert_duplicatekey_update(tablename, cols, df, chunksize)
        hook = self.get_hook()
        hook.run(sql, autocommit=True)

    def load_df_to_mysql(self, data: pd.DataFrame, table: str, insert_method: str, chunksize: int = 5000):
        """Loads a DataFrame into a MySQL table using specified insert methods with Airflow's MySQL hook.

        Args:
            data (pd.DataFrame): DataFrame containing the data to be inserted.
            table (str): Name of the MySQL table to insert data into.
            insert_method (str): Method to use for inserting data ('insert_ignore' or 'on_duplicate_key_update').
            chunksize (int, optional): Number of rows per insert operation. Defaults to 5000.

        Raises:
            AirflowFailException: If an unsupported insert method is provided.
        """
        from airflow.exceptions import AirflowFailException  # pylint: disable=import-outside-toplevel

        methods = {
            "insert_ignore": self.to_sql_method_insert_ignore,
            "on_duplicate_key_update": self.to_sql_method_on_duplicate_key_update,
        }
        if not (method := methods.get(insert_method)):
            raise AirflowFailException(f"Wrong method {insert_method=}: {methods.keys()} 중에서 선택해야 합니다.")
        engine = self.get_hook().get_sqlalchemy_engine()
        data.to_sql(name=table, con=engine, if_exists="append", index=False, chunksize=chunksize, method=method)

    @staticmethod
    def to_sql_method_on_duplicate_key_update(table, conn, keys, data_iter):  # pylint: disable=unused-argument
        """Provides a method for on_duplicate_key_update that can be used with DataFrame.to_sql.

        This method is designed to be used as the `method` parameter in pandas DataFrame.to_sql to handle
        on duplicate key update operations.

        Args:
            table (sqlalchemy.Table): The table object where data will be inserted.
            conn (sqlalchemy.engine.base.Connection): Database connection.
            keys (List[str]): List of column names.
            data_iter (Iterable): An iterable that yields row data as tuples or dictionaries.
        """
        logger.info(f"LOGGER : {keys=}")
        logger.info(f"LOGGER : {data_iter=}")
        insert_stmt = insert(table.table).values(list(data_iter))
        on_duplicate_key_stmt = insert_stmt.on_duplicate_key_update(insert_stmt.inserted)
        ret = conn.execute(on_duplicate_key_stmt)
        logger.info(f"LOGGER : {ret=}")

    @staticmethod
    def to_sql_method_insert_ignore(table, conn, keys, data_iter):  # pylint: disable=unused-argument
        """Provides a method for insert_ignore that can be used with DataFrame.to_sql.

        This method is utilized as the `method` parameter in pandas DataFrame.to_sql for insert ignore operations.

        Args:
            table (sqlalchemy.Table): The table object where data will be inserted.
            conn (sqlalchemy.engine.base.Connection): Database connection.
            keys (List[str]): List of column names.
            data_iter (Iterable): An iterable that yields row data as tuples or dictionaries.
        """
        insert_stmt = insert(table.table).values(list(data_iter)).prefix_with("IGNORE")
        conn.execute(insert_stmt)
