import hashlib
import random
import string
import time
import os
from collections import OrderedDict
from typing import List

import pandas as pd
from impala.dbapi import connect

from dough.db_connector.base import DbApiBase

class Impala(DbApiBase):
    """Handles Impala database operations, extending the DbApiBase class for Impala-specific functionality."""

    def __init__(self, conn_id: str):
        """Initializes the Impala class with a connection ID.

        Args:
            conn_id (str): Connection ID for the Impala database.
        """
        super().__init__()
        self.conn_id = conn_id

    def connect(self) -> None:
        """Attempts to establish a connection to the Impala database using the provided connection ID."""
        connection = self.get_connection(self.conn_id)
        try:
            self.conn = connect(host=connection.host, port=connection.port)
        except ConnectionError:
            print("Connection Error")
            exit()
            
class ImpalaDataLoader(Impala):
    """Manages data loading operations into Impala, including handling temporary tables and partition management."""

    def __init__(self, database: str, table: str, **kwargs) -> None:
        """Initializes the ImpalaDataLoader with database and table information.

        Args:
            database (str): The name of the database.
            table (str): The name of the table.
            **kwargs: Additional keyword arguments that are passed to the parent constructor.
        """
        super().__init__(**kwargs)
        import pyarrow as pa
        import pyarrow.parquet as pq
        from airflow.providers.apache.hdfs.hooks.webhdfs import WebHDFSHook

        self.hook = WebHDFSHook("hdfs")
        self.database = database
        self.table = table
        self.set_partitions()
        self.set_columns()
        self.pa = pa
        self.pq = pq

    def set_partitions(self) -> None:
        """Sets the partitions of the table by querying the Impala database."""
        sql = f"""
SHOW PARTITIONS `{self.database}`.`{self.table}`
"""
        df = self.query(sql)
        self.partitions = df.columns[:-8].to_list()  # Excludes the last 8 columns from the partition list.

    def set_columns(self) -> None:
        """Sets the columns of the table by querying the Impala database."""
        sql = f"""
DESCRIBE `{self.database}`.`{self.table}`
"""
        df = self.query(sql)
        self.columns = dict(zip(df.name, df.type))

    def set_tmp_table_name(self) -> None:
        """Generates a unique temporary table name based on the DAG ID, current timestamp, and a random string."""
        from airflow.operators.python import get_current_context
        context = get_current_context()
        dag_id = context["dag"].dag_id
        timestamp = "".join(
            [
                i
                for i in context["execution_date"]
                .in_timezone("Asia/Seoul")
                .to_datetime_string()
                if i.isalnum()
            ]
        )
        letters = string.ascii_lowercase
        random_str = "".join(random.choice(letters) for _ in range(6))
        self.TMP_TABLE_NAME = f"{dag_id}_{timestamp}_{random_str}"

    def load_to_hdfs(self, df: pd.DataFrame) -> None:
        """Loads a DataFrame to HDFS as a CSV file.

        Args:
            df (pd.DataFrame): The DataFrame to load.
        """
        hook = self.hook
        local_filepath = (
            "/tmp/" + hashlib.md5(f"{self.TMP_TABLE_NAME}".encode()).hexdigest()
        )
        df.to_csv(local_filepath, index=False, header=False)
        hdfs_filepath = (
            f"/user/hive/warehouse/airflow_etl.db/{self.TMP_TABLE_NAME}/data.csv"
        )
        hook.load_file(local_filepath, hdfs_filepath)

    def load_to_hdfs2(self, df: pd.DataFrame) -> None:
        """Loads a DataFrame to HDFS as a compressed Parquet file.

        Args:
            df (pd.DataFrame): The DataFrame to load.
        """
        hook = self.hook
        local_filepath = (
            "/tmp/" + hashlib.md5(f"{self.TMP_TABLE_NAME}".encode()).hexdigest()
        )
        df.to_parquet(local_filepath, engine="pyarrow", compression="gzip", index=False)
        hdfs_filepath = (
            f"/user/hive/warehouse/airflow_etl.db/{self.TMP_TABLE_NAME}/data.gz.parquet"
        )
        hook.load_file(local_filepath, hdfs_filepath)

    def load_user_segment_to_hdfs_parquet(self, df: pd.DataFrame, db, table_name, segemnt_name, logdate) -> None:
        """Loads a DataFrame to HDFS as a compressed Parquet file.

        Args:
            df (pd.DataFrame): The DataFrame to load.
            db (str): Target database.
            table (str): Target table.
            partition_name (str): The name of the partition.
            partition (str): The partition value.
        """
        hook = self.hook
        local_filepath = f"{os.environ['AIRFLOW_TMP']}/{logdate}_{table_name}_{segemnt_name}.parquet"
        table = self.pa.Table.from_pandas(df, preserve_index=False)
        self.pq.write_table(table, local_filepath, version='1.0', compression='gzip')
        hdfs_filepath = f"/user/hive/warehouse/{db}.db/{table_name}/segment={segemnt_name}/logdate={logdate}/data.parquet"
        hook.load_file(local_filepath, hdfs_filepath)
        os.remove(local_filepath)

    def create_tmp_table(self) -> None:
        """Creates a temporary table in Impala with CSV format based on the schema of the target table."""
        columns_clause = ",".join([f"`{k}` {v}" for k, v in self.columns.items()])
        sql = f"""
    CREATE TABLE IF NOT EXISTS `airflow_etl`.`{self.TMP_TABLE_NAME}`
        ({columns_clause})
    ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
    LOCATION '/user/hive/warehouse/airflow_etl.db/{self.TMP_TABLE_NAME}';
    """
        self.execute(sql)

    def create_tmp_table2(self) -> None:
        """Creates a temporary table in Impala with Parquet format based on the schema of the target table."""
        columns_clause = ",".join([f"`{k}` {v}" for k, v in self.columns.items()])
        sql = f"""
    CREATE TABLE IF NOT EXISTS `airflow_etl`.`{self.TMP_TABLE_NAME}`
        ({columns_clause})
    STORED AS PARQUET
    LOCATION '/user/hive/warehouse/airflow_etl.db/{self.TMP_TABLE_NAME}';
    """
        self.execute(sql)

    def drop_tmp_table(self, tmp_table_name: str) -> None:
        """Drops the specified temporary table from Impala.

        Args:
            tmp_table_name (str): The name of the temporary table to drop.
        """
        sql = f"""
DROP TABLE `airflow_etl`.`{tmp_table_name}`
"""
        self.execute(sql)

    def drop_partitions_by_data(self, tmp_table_name: str) -> None:
        """Drops partitions from the target table based on the data in the temporary table.

        Args:
            tmp_table_name (str): The name of the temporary table containing partition data.
        """
        distinct_clause = ",".join(self.partitions)
        sql = f"""
SELECT DISTINCT {distinct_clause}
FROM `airflow_etl`.`{tmp_table_name}`
"""
        df = self.query(sql)
        for idx, row in df.iterrows():
            partition_spec = []
            for key, value in row.to_dict(into=OrderedDict).items():
                if isinstance(value, int):
                    partition_spec.append(f"{key}={value}")
                else:
                    partition_spec.append(f"{key}='{value}'")
            partition_spec_str = ",".join(partition_spec)
            sql = f"ALTER TABLE `{self.database}`.`{self.table}` DROP IF EXISTS PARTITION ({partition_spec_str}) PURGE;"
            self.execute(sql)

    def etl_to_table(self, tmp_table_name: str) -> None:
        """Executes the ETL process: loading data from the temporary table to the target table.

        Args:
            tmp_table_name (str): The name of the temporary table.
        """
        str_partition = ",".join(self.partitions)
        partition_clause = f"PARTITION ({str_partition})"
        sql = f"""
INSERT INTO TABLE `{self.database}`.`{self.table}`
{partition_clause}
SELECT *
FROM `airflow_etl`.`{tmp_table_name}`
"""
        self.execute(sql)

    def validate_df(self, df: pd.DataFrame, columns: dict) -> pd.DataFrame:
        """Validates and transforms a DataFrame to match the target table schema.

        Args:
            df (pd.DataFrame): The DataFrame to validate and transform.
            columns (dict): A dictionary mapping column names to their data types.

        Returns:
            pd.DataFrame: The validated and transformed DataFrame.
        """
        df = df.astype(columns)
        df = df[columns.keys()]
        return df

class ImpalaHelper(ImpalaDataLoader):
    """Provides helper methods for common Impala data loading tasks."""

    def __init__(self, **kwargs):
        """Initializes the ImpalaHelper with optional database and table information.

        Args:
            **kwargs: Keyword arguments containing optional database and table information.
        """
        if "database" in kwargs and "table" in kwargs:
            self.init_data_loader(kwargs.get("database"), kwargs.get("table"))

    def init_data_loader(self, database: str, table: str) -> None:
        """Initializes the data loader with the specified database and table.

        Args:
            database (str): The name of the database.
            table (str): The name of the table.
        """
        super().__init__(database, table)

    def df_to_hdfs(self, df: pd.DataFrame) -> None:
        """Validates, sets a temporary table name, loads the DataFrame to HDFS, and creates a temporary table.

        Args:
            df (pd.DataFrame): The DataFrame to process.
        """
        df = self.validate_df(df, self.columns)
        self.set_tmp_table_name()
        self.load_to_hdfs(df)
        self.create_tmp_table()

    def load_dart4_to_hdfs(self, repoid: str, logdate: str, file: str) -> None:
        """Loads a specified file to HDFS in the dart4_etl directory.

        Args:
            repoid (str): The repository ID.
            logdate (str): The log date.
            file (str): The file to load.
        """
        hook = self.hook
        local_filepath = "/dart4/" + file
        hdfs_filepath = (
            f"/user/hive/warehouse/dart4_etl.db/{repoid}/logdate={logdate}/{file}"
        )
        hook.load_file(local_filepath, hdfs_filepath)

    def df_to_hdfs2(self, df: pd.DataFrame) -> None:
        """Validates, sets a temporary table name, loads the DataFrame to HDFS as a Parquet file, and creates a Parquet-formatted temporary table.

        Args:
            df (pd.DataFrame): The DataFrame to process.
        """
        df = self.validate_df(df, self.columns)
        self.set_tmp_table_name()
        self.load_to_hdfs2(df)
        self.create_tmp_table2()

    def tmp_to_real_table(self, tmp_table_name: str) -> None:
        """Manages the entire process of loading data from a temporary table to the real table and cleaning up.

        Args:
            tmp_table_name (str): The name of the temporary table.
        """
        time.sleep(5)  # Wait for any pending operations to complete
        self.drop_partitions_by_data(tmp_table_name)
        self.etl_to_table(tmp_table_name)
        self.drop_tmp_table(tmp_table_name)

    def get_tmp_table_name(self) -> str:
        """Returns the name of the current temporary table.

        Returns:
            str: The name of the temporary table.
        """
        return self.TMP_TABLE_NAME

    @classmethod
    def get_repoid_list(cls) -> List[str]:
        """Fetches a list of repository IDs (repoid) from the dart4 database.

        Returns:
            List[str]: A list of repository IDs.
        """
        conn = connect(host=cls.HOST, port=cls.PORT)
        cursor = conn.cursor()
        cursor.execute("USE dart4;")
        cursor.execute("SHOW TABLES;")
        tables = []
        for table in cursor.fetchall():
            tables.append(table[0])
        return tables
