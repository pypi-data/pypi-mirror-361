from typing import Dict, List

import mysql.connector

from schemachange.common.schema import MySQLConnectorArgsSchema
from schemachange.common.utils import get_connect_kwargs
from schemachange.session.base import BaseSession


class MySQLSession(BaseSession):
    def _connect(self):
        self.database = self.connections_info.get("database")
        self.user = self.connections_info.get("user")
        self._connection = mysql.connector.connect(
            **get_connect_kwargs(
                connections_info=self.connections_info,
                supported_args_schema=MySQLConnectorArgsSchema,
            )
        )
        self._cursor = self._connection.cursor()

    def fetch_change_history_metadata(self) -> List[Dict]:
        query = f"""\
            SELECT
                CREATE_TIME,
                UPDATE_TIME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE UPPER(TABLE_SCHEMA) = '{self.change_history_table.database_name}'
                AND UPPER(TABLE_NAME) = '{self.change_history_table.table_name}'
        """
        data = self.execute_query(query=query)

        return data

    def reset_session(self):
        if self.database:
            self.execute_query(query=f"USE {self.database}")

    def create_change_history_schema(self, dry_run: bool) -> None:
        schemachange_database = self.change_history_table.database_name

        # Check if database exists yet
        database_data = self.execute_query(
            query=f"SELECT * FROM INFORMATION_SCHEMA.SCHEMATA WHERE UPPER(SCHEMA_NAME) = UPPER('{schemachange_database}')"
        )
        if not database_data:
            raise Exception(
                f"Database '{schemachange_database}' of change history table does not exist. "
                "It should be created beforehand"
            )
