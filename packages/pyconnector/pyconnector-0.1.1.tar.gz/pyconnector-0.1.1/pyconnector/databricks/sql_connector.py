
from databricks import sql
import os

class DatabricksSQLConnector:
    """
    Secure Databricks SQL Connector using the official Databricks SQL Connector for Python.
    """

    def __init__(self, server_hostname, http_path, access_token):
        self.server_hostname = server_hostname
        self.http_path = http_path
        self.access_token = access_token
        self.connection = None

    def __enter__(self):
        self.connection = sql.connect(
            server_hostname=self.server_hostname,
            http_path=self.http_path,
            access_token=self.access_token
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()
            self.connection = None

    def execute_query(self, query):
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    def insert_data(self, table, data):
        with self.connection.cursor() as cursor:
            values = ",".join([f"({', '.join(map(str, row))})" for row in data])
            cursor.execute(f"INSERT INTO {table} VALUES {values}")

    # Add more methods as needed (e.g., metadata, file management, etc.)
