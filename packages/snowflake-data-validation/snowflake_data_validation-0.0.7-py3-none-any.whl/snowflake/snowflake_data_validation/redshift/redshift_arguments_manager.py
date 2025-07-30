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

import os

from typing import Optional

import typer

from pydantic import ValidationError

from snowflake.snowflake_data_validation.configuration.model.configuration_model import ConfigurationModel
from snowflake.snowflake_data_validation.connector.connector_base import (
    ConnectorBase as BaseConnector,
)
from snowflake.snowflake_data_validation.connector.connector_base import (
    NullConnector,
)
from snowflake.snowflake_data_validation.redshift.connector.connector_redshift import ConnectorRedshift
from snowflake.snowflake_data_validation.redshift.model.redshift_credentials_connection import (
    RedshiftCredentialsConnection,
)
from snowflake.snowflake_data_validation.snowflake.connector.connector_snowflake import ConnectorSnowflake
from snowflake.snowflake_data_validation.utils.arguments_manager_base import ArgumentsManagerBase
from snowflake.snowflake_data_validation.utils.console_output_handler import ConsoleOutputHandler
from snowflake.snowflake_data_validation.utils.constants import (
    CREDENTIALS_CONNECTION_MODE,
    DEFAULT_CONNECTION_MODE,
    MISSING_SOURCE_CONNECTION_ERROR,
    MISSING_TARGET_CONNECTION_ERROR,
    NAME_CONNECTION_MODE,
    ExecutionMode,
    Platform,
)


class RedshiftArgumentsManager(ArgumentsManagerBase):

    """Class to manage Redshift arguments for data validation.

    This class is a placeholder and can be extended with specific methods
    for handling Redshift arguments as needed.
    """

    def __init__(self):
        super().__init__(source_platform=Platform.REDSHIFT, target_platform=Platform.SNOWFLAKE)

    @property
    def is_snowflake_to_snowflake(self) -> bool:
        return False

    def create_validation_environment_from_config(
        self,
        config_model: ConfigurationModel,
        data_validation_config_file: str,
        execution_mode: ExecutionMode,
        output_handler: Optional[ConsoleOutputHandler] = None,
    ):
        if execution_mode == ExecutionMode.ASYNC_VALIDATION:
            source_connector = NullConnector()
            target_connector = NullConnector()
        else:
            source_connector = self._setup_source_from_config(config_model)
            target_connector = self._setup_target_from_config(config_model)

        return self.setup_validation_environment(
            source_connector=source_connector,
            target_connector=target_connector,
            data_validation_config_file=data_validation_config_file,
            output_directory_path=config_model.output_directory_path,
            output_handler=output_handler or ConsoleOutputHandler(),
        )

    def setup_source_connection(
        self,
        redshift_credentials: RedshiftCredentialsConnection
    ) -> BaseConnector:
        try:
            redshift_connector = ConnectorRedshift()
            # Note: The linter may show parameter errors due to the @log decorator
            # affecting parameter detection, but the parameters are correct
            redshift_connector.connect(
                host=redshift_credentials.host,
                port=int(redshift_credentials.port),
                user=redshift_credentials.username,
                password=redshift_credentials.password,
                database=redshift_credentials.database,
            )

        except ConnectionError as e:
            raise ConnectionError(
                f"Failed to establish Redshift connection: {e}"
            ) from e
        except ValidationError as e:
            raise typer.BadParameter(
                f"Invalid Redshift connection parameters: {e}"
            ) from e
        except ImportError as e:
            raise ImportError(
                f"Redshift dependencies not available: {e}"
            ) from e
        except Exception as e:
            raise Exception(
                f"Unexpected error while setting up Redshift connection: {e}"
            ) from e
        return redshift_connector

    def get_source_templates_path(self) -> str:
        """Get Teradata templates path.

        TODO: Implement actual Teradata-specific templates in future PR.
        For now, using placeholder templates to avoid file not found errors.
        """
        current_dir = os.path.dirname(__file__)
        return os.path.join(current_dir, "extractor", "templates")

    def setup_target_connection(
        self,
        snowflake_conn_mode: str = DEFAULT_CONNECTION_MODE,
        snowflake_connection_name: Optional[str] = None,
        snow_credential_object: Optional[dict[str, str]] = None,
        **kwargs,
    ) -> BaseConnector:
        """Set up Snowflake target connection for Teradata migrations.

        Args:
            snowflake_conn_mode: Connection mode for Snowflake
            snowflake_connection_name: Connection name
            snow_credential_object: Snowflake credentials dictionary
            **kwargs: Additional parameters

        Returns:
            BaseConnector: Configured Snowflake connector

        """
        return self._setup_snowflake_connection(
            snowflake_conn_mode, snowflake_connection_name, snow_credential_object
        )

    def get_target_templates_path(self) -> str:
        """Get Snowflake target templates path."""
        current_dir = os.path.dirname(__file__)
        return os.path.join(current_dir, "..", "snowflake", "extractor", "templates")

    def _setup_source_from_config(
        self,
        config_model: ConfigurationModel
    ) -> BaseConnector:
        """Set up source connector from configuration model."""
        if not config_model.target_connection:
            raise typer.BadParameter(
                MISSING_SOURCE_CONNECTION_ERROR
            )

        source_connection = config_model.source_connection
        mode = getattr(source_connection, "mode", CREDENTIALS_CONNECTION_MODE)
        if mode == CREDENTIALS_CONNECTION_MODE:
            redshift_credentials = RedshiftCredentialsConnection(
                host=source_connection.host,
                port=source_connection.port,
                username=source_connection.username,
                password=source_connection.password,
                database=source_connection.database,
            )

            return self.setup_source_connection(redshift_credentials)

        else:
            raise typer.BadParameter(
                f"Unsupported source connection mode for Redshift: {mode}. "
                f"Only '{CREDENTIALS_CONNECTION_MODE}' is supported."
            )

    def _setup_snowflake_connection(
        self,
        snowflake_conn_mode: str,
        snowflake_connection_name: Optional[str] = None,
        snow_credential_object: Optional[dict[str, str]] = None,
    ) -> ConnectorSnowflake:
        """Set up internal Snowflake connection."""
        if (
            snowflake_conn_mode == NAME_CONNECTION_MODE
            and not snowflake_connection_name
        ):
            raise typer.BadParameter(
                message="If using 'name' connection mode, you must provide the Snowflake connection name"
            )

        try:
            snowflake_connector = ConnectorSnowflake()
            connection_params: dict[str, str] = {
                "mode": snowflake_conn_mode,
                "connection_name": snowflake_connection_name,
            }

            if snow_credential_object:
                connection_params.update(
                    {
                        "account": snow_credential_object.get("account"),
                        "username": snow_credential_object.get("username"),
                        "role": snow_credential_object.get("role"),
                        "database": snow_credential_object.get("database"),
                        "schema": snow_credential_object.get("schema"),
                        "warehouse": snow_credential_object.get("warehouse"),
                        "password": snow_credential_object.get("password"),
                    }
                )

            snowflake_connector.connect(**connection_params)
            return snowflake_connector
        except Exception as e:
            raise RuntimeError(f"Failed to set up Snowflake connection: {e}") from e


    def _setup_target_from_config(
        self,
        config_model: ConfigurationModel,
    ) -> BaseConnector:
        if not config_model.target_connection:
            raise typer.BadParameter(
                MISSING_TARGET_CONNECTION_ERROR
            )
        target_connection = config_model.target_connection
        mode = getattr(target_connection, "mode", NAME_CONNECTION_MODE)
        if mode == NAME_CONNECTION_MODE:
            return self.setup_target_connection(
                snowflake_conn_mode=NAME_CONNECTION_MODE,
                snowflake_connection_name=getattr(target_connection, "name", None),
            )
        elif mode == DEFAULT_CONNECTION_MODE:
            return self.setup_target_connection(
                snowflake_conn_mode=DEFAULT_CONNECTION_MODE,
            )
        else:
            raise typer.BadParameter(
                message=f"Unsupported target connection mode for Snowflake: {mode}. "
                "Supported modes are 'name' and 'default'. Use IPC commands for credentials mode."
            )
