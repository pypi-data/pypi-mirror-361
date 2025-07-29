
from __future__ import annotations

import logging

import pandas as pd

from dough.db_connector.mysql import Mysql

mysql = Mysql("idb_marketing_report")
FLAG_INFO = {
    "TITLE_MANAGED": "status IN ('MANAGED','SOFTLAUNCH')",
    "TITLE_ACTIVE": "status IN ('MANAGED','SOFTLAUNCH','AUTOMATION')",
    "TITLE_PUBLISH": "status IN ('MANAGED','SOFTLAUNCH','AUTOMATION','DROP')",
    "TITLE_ALL": "status IN ('MANAGED','SOFTLAUNCH','AUTOMATION','DROP','XLSOFT')",
    "STORE_MAJOR": "(appid LIKE '%%\\.ap\\.%%' OR appid LIKE '%%\\.go\\.%%')",
    "STORE_APPLE": "appid LIKE '%%\\.ap\\.%%'",
    "STORE_GOOGLE": "appid LIKE '%%\\.go\\.%%'",
    "STORE_AMAZON": "appid LIKE '%%\\.am\\.%%'",
    "STORE_WINDOWS": "appid LIKE '%%\\.ms\\.%%'",
    "GENRE_BLOCK": "genre = 'block'",
    "GENRE_BRICK": "genre = 'brick'",
    "GENRE_BUBBLE": "genre = 'bubble'",
    "GENRE_CASUAL": "genre = 'casual'",
    "GENRE_MATCH3": "genre = 'match3'",
    "GENRE_MERGE": "genre = 'merge'",
    "GENRE_SAMEMATCH": "genre = 'samematch'",
    "GENRE_SOLITAIRE": "genre = 'solitaire'",
    "GENRE_WORD": "genre = 'word'",
    "MANAGED": "status = 'MANAGED'",
}


def get_ua_info() -> pd.DataFrame:
    """Retrieve basic UA manager information including repository ID, status, and manager.

    Author: ksjung.

    Returns:
        pd.DataFrame: DataFrame containing columns ['repoid', 'status', 'manager'].
    """
    df = mysql.query("SELECT repoid, status, manager FROM ua_manager;")
    return df


def get_apps_by_status(status: str | list) -> list[str]:
    """Retrieve application repository IDs based on their status.

    Author: ksjung

    Args:
        status (str | list): Status or list of statuses to filter applications.

    Returns:
        list[str]: List of repository IDs corresponding to the specified statuses.
    """
    if isinstance(status, str):
        status = [status]

    status_str = ", ".join(f"'{s}'" for s in status)

    df = mysql.query(f"""
        SELECT repoid
        FROM ua_manager
        WHERE status in ({status_str});
    """)

    return df["repoid"].to_list()


def get_title_info(flags: list[str] | None = None, fields: list[str] | None = None) -> pd.DataFrame | list[str]:
    """Generate a query based on given flags and retrieve the title information.

    Author: yskim, ksjung

    Args:
        flags (list[str] | None): List of flags to apply to the query filter.
        fields (list[str] | None): Specific fields to retrieve; retrieves all if None.

    Returns:
        pd.DataFrame | list[str]: DataFrame with the results or a list of results if only one field is specified.
    """
    logger = logging.getLogger("airflow.task")
    logger.info(f"LOGGER : {flags=}")
    logger.info(f"LOGGER : {fields=}")
    hook = Mysql("idb_common")

    where_clause = "1=1"
    if flags:
        selected_flag = [FLAG_INFO.get(flag) for flag in flags if FLAG_INFO.get(flag)]
        where_clause = " AND ".join(selected_flag)

    select_clause = ",".join(fields) if fields else "*"

    sql = f"SELECT {select_clause} FROM common.view_apps_info WHERE {where_clause}"
    logger.info(f"LOGGER : {sql=}")
    df = hook.query(sql)
    df = df.drop_duplicates()
    df = df.reset_index(drop=True)

    if isinstance(fields, list) and len(fields) == 1:
        return df[fields[0]].to_list()

    return df


def get_appkeys_by_store(store_name: str) -> pd.DataFrame:
    """Generate a mapping table between app IDs and store-specific keys.

    Author: ksjung

    Args:
        store_name (str): Store identifier, e.g., 'apple', 'amazon', 'microsoft'.

    Returns:
        pd.DataFrame: DataFrame containing columns ['appid', 'storekey'] or the specific key for each store.
    """

    store_column_mapping = {"apple": "storekey", "amazon": "asin", "microsoft": "mskey"}
    column_name = store_column_mapping.get(store_name)

    if not column_name:
        raise ValueError(f"Unknown store name: {store_name}")

    sql = f"""
        select appid, {column_name}
        from common.apps_v3
        where {column_name} is not null
        and {column_name} <> ""
        """
    df = mysql.query(sql)

    return df


def retrieve_related_value(input_column: str, output_column: str, input_value: str) -> list[str]:
    """Convert values from one column to another based on an input value within apps_v3.

    Author: ksjung

    Args:
        input_column (str): The name of the input column from which to filter.
        output_column (str): The name of the output column to retrieve values.
        input_value (str): The value to match in the input column.

    Returns:
        list[str]: List of values from the output column that correspond to the input value.
    """
    sql = f"""
        SELECT {output_column}
        FROM common.view_apps_info
        WHERE {input_column} = '{input_value}'
        GROUP BY {output_column}
        ORDER BY {output_column}
    """
    df = mysql.query(sql)

    output_values = df[output_column].to_list()

    return output_values

