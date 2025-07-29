# pylint: disable=import-outside-toplevel
from sqlalchemy import create_engine
from .base import DbApiBase

class ClickHouse(DbApiBase):
    """Represents a ClickHouse database connection handler.

    This class provides methods to initialize a connection to a ClickHouse database
    and to establish the connection using the provided connection ID.

    Attributes:
        conn_id (str): The connection ID for the ClickHouse database
    """

    def __init__(self, clickhouse_conn_id: str):
        """Initializes the ClickHouse class with a connection ID.
        
        Args:
            clickhouse_conn_id (str): Connection ID for the ClickHouse database.
        """
        super().__init__()
        self.conn_id = clickhouse_conn_id
        self.engine = None

    def connect(self):
        """Establishes a connection to the ClickHouse database using the stored connection ID.
        
        Attempts to connect to the ClickHouse database. If the connection is unsuccessful,
        a ConnectionError exception is caught and a message is printed.
        """
        conn = self.get_connection(self.conn_id)
        url = f"clickhouse+native://{conn.login}:{conn._password}@{conn.host}:{conn.port}/default"
        try:
            self.engine = create_engine(url)
            self.conn = self.engine.raw_connection()
        except Exception as e:
            print(f"Connection Error: {e}")
            self.engine = None


class ClickhouseAirflowHook(ClickHouse):
    """Provides methods for Airflow to interact with ClickHouse for database operations.

    Inherits from ClickHouse to leverage connection initialization and establishes
    additional functionalities specific to Airflow, including retrieving a ClickHouseHook
    for operations and inserting data frames into ClickHouse tables.

    Attributes:
        conn_id (str): The connection ID for the ClickHouse database.
    """

    def __init__(self, clickhouse_conn_id: str):
        """Initializes the ClickhouseAirflowHook with a ClickHouse connection ID.
        
        Args:
            clickhouse_conn_id (str): Connection ID for the ClickHouse database.
        """
        super().__init__(clickhouse_conn_id)

    def get_hook(self):
        """Retrieves a ClickHouseHook from the airflow_clickhouse_plugin.
        
        Returns:
            ClickHouseHook: An instance of ClickHouseHook from airflow_clickhouse_plugin.
        """
        from airflow_clickhouse_plugin.hooks.clickhouse import ClickHouseHook

        hook = ClickHouseHook(clickhouse_conn_id=self.conn_id)
        return hook

    def insert(self, df, table_name: str, chunksize: int = 1000) -> int:
        """Inserts a pandas DataFrame into a ClickHouse table.
        
        Args:
            df (DataFrame): The pandas DataFrame to insert into the ClickHouse table.
            table_name (str): The name of the ClickHouse table to insert data into.
            chunksize (int, optional): The size of chunks to split the DataFrame. Defaults to 1000.
        
        Returns:
            int: The number of rows affected by the insert operation.
        """
        import pandahouse as ph

        connection = self.get_connection(self.conn_id)
        pandahouse_connection = {
            "database": connection.schema,
            "host": connection.host,
            "user": connection.login,
            "password": connection._password,
        }
        affected_rows = ph.to_clickhouse(
            df,
            table_name,
            index=False,
            chunksize=chunksize,
            connection=pandahouse_connection,
        )
        return affected_rows

    def connect(self):
        """Establishes a connection to the ClickHouse database using an Airflow hook.
        
        Overrides the connect method in the parent class to use the ClickHouseHook from
        Airflow's airflow_clickhouse_plugin to establish the connection.
        """
        hook = self.get_hook()
        self.conn = hook.get_conn()

