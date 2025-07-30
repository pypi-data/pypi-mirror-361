# Copyright 2025 Snowflake Inc.
# SPDX-License-Identifier: Apache-2.0
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import types

from typing import TYPE_CHECKING, Any, Optional

from snowflake.snowflake_data_validation.connector.connector_base import (
    ConnectorBase as BaseConnector,
)
from snowflake.snowflake_data_validation.utils.constants import (
    CONNECTION_NOT_ESTABLISHED,
    FAILED_TO_EXECUTE_QUERY,
    FAILED_TO_EXECUTE_STATEMENT,
)
from snowflake.snowflake_data_validation.utils.helper import Helper
from snowflake.snowflake_data_validation.utils.logging_utils import log
from snowflake.snowflake_data_validation.utils.telemetry import (
    report_telemetry,
)


if TYPE_CHECKING:
    import redshift_connector

LOGGER = logging.getLogger(__name__)

@Helper.import_dependencies("redshift")
def import_redshift():
    """Import the redshift_connector module for Redshift connector."""
    import redshift_connector

    return redshift_connector

class ConnectorRedshift(BaseConnector):

    """Connector for Redshift database using the pyodbc connector."""

    def __init__(self) -> None:
        """Initialize the Redshift connector."""
        super().__init__()
        self.redshift_connector: types.ModuleType = import_redshift()
        self.connection: Optional[redshift_connector.Connection] = None

    @log
    def close(self) -> None:
        if self.connection is not None:
            try:
                LOGGER.debug("Closing Redshift connection")
                self.connection.close()
                LOGGER.debug("Redshift connection closed successfully")
            except self.redshift_connector.Error as e:
                LOGGER.error("Failed to close Redshift connection: %s", str(e))
                raise
        else:
            LOGGER.warning("No Redshift connection to close")

    @log
    @report_telemetry(params_list=["host", "port", "database", "user"])
    def connect(self, host: str, database: str, user: str, password: str, port: Optional[int] = None) -> None:
        """Establish a connection to a Redshift database using the redshift_connector.

        Args:
            host (str): The hostname or IP address of the Redshift server.
            user (str): The username for authentication.
            password (str): The password for authentication.
            database (str): The name of the database to connect to.
            port (str, optional): The port number for the Redshift server. Defaults to 5439.

        """
        LOGGER.info("Attempting to connect to Redshift at %s:%d", host, port or 5439)

        if not all([host, database, user, password]):
            error_msg = "All connection parameters (host, database, user, password) are required"
            LOGGER.error(error_msg)
            raise ValueError(error_msg)
        try:
            self.connection = self.redshift_connector.connect(
                host=host,
                database=database,
                user=user,
                password=password,
                port=port
            )

            self._verify_connection()
            LOGGER.info("Successfully connected to Redshift")
        except self.redshift_connector.Error as e:
            LOGGER.error("Failed to connect to Redshift: %s", str(e))
            self.connection = None
            raise ConnectionError(f"Failed to connect to Redshift: {e}") from e

    @log
    def execute_query(self, query) -> tuple[list[str], tuple[tuple[Any, ...]]]:
        if self.connection is None:
            error_msg = (
                "Database connection is not established. Please call connect() first."
            )
            LOGGER.error(error_msg)
            raise Exception(error_msg)
        try:
            LOGGER.debug(
                "Executing Redshift query: %s",
                query[:100] + "..." if len(query) > 100 else query,
            )
            cursor = self.connection.cursor()
            with cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
                return column_names, results
        except Exception as e:
            LOGGER.error("Failed to execute Redshift query: %s", str(e))
            raise Exception(FAILED_TO_EXECUTE_QUERY.format(query=query)) from e

    @log
    def execute_query_no_return(self, query: str) -> None:
        if self.connection is None:
            raise Exception(CONNECTION_NOT_ESTABLISHED)

        try:
            LOGGER.debug("Executing Redshift query: %s", query)
            with self.connection.cursor() as cursor:
                cursor.execute(query)
            LOGGER.debug("Query executed successfully, returned 0 rows")
        except self.redshift_connector.Error as e:
            raise Exception(FAILED_TO_EXECUTE_QUERY.format(query=query)) from e

    @log
    def execute_statement(self, statement) -> None:
        if self.connection is None:
            raise Exception(CONNECTION_NOT_ESTABLISHED)

        try:
            LOGGER.debug("Executing Redshift statement: %s", statement)
            with self.connection.cursor() as cursor:
                cursor.execute(statement)
                self.connection.commit()
            LOGGER.debug("Statement executed successfully")
        except self.redshift_connector.Error as e:
            raise Exception(
                FAILED_TO_EXECUTE_STATEMENT.format(statement=statement)
            ) from e

    @log
    def _verify_connection(self) -> None:
        """Verify the connection by executing a simple test query.

        Raises:
            ConnectionError: If connection verification fails

        """
        try:
            LOGGER.debug("Verifying Redshift connection")
            if self.connection is not None:
                # Execute a simple query to verify connection
                cursor = self.connection.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result is not None and len(result) > 0:
                    LOGGER.debug("Redshift connection verified successfully")
                else:
                    raise ConnectionError("Connection verification failed")
            else:
                raise ConnectionError("Connection is None")
        except Exception as e:
            LOGGER.error("Failed to verify Redshift connection: %s", str(e))
            self.connection = None
            raise ConnectionError(f"Failed to verify Redshift connection: {e}") from e
