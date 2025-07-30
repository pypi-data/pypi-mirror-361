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

"""Teradata Arguments Manager for handling Teradata source connections."""

import os

from typing import Optional

import typer

from snowflake.snowflake_data_validation.configuration.model.configuration_model import (
    ConfigurationModel,
)
from snowflake.snowflake_data_validation.connector.connector_base import (
    ConnectorBase,
)
from snowflake.snowflake_data_validation.snowflake.connector.connector_snowflake import (
    ConnectorSnowflake,
)
from snowflake.snowflake_data_validation.teradata.connector.connector_teradata import (
    ConnectorTeradata,
)
from snowflake.snowflake_data_validation.utils.arguments_manager_base import (
    ArgumentsManagerBase,
)
from snowflake.snowflake_data_validation.utils.console_output_handler import (
    ConsoleOutputHandler,
)
from snowflake.snowflake_data_validation.utils.constants import (
    CREDENTIALS_CONNECTION_MODE,
    DEFAULT_CONNECTION_MODE,
    NAME_CONNECTION_MODE,
    ExecutionMode,
    Platform,
)


class TeradataArgumentsManager(ArgumentsManagerBase):

    """Arguments manager for Teradata source to Snowflake target validations."""

    def __init__(self):
        """Initialize the Teradata arguments manager."""
        super().__init__(Platform.TERADATA, Platform.SNOWFLAKE)

    @property
    def is_snowflake_to_snowflake(self) -> bool:
        """Check if this is a Snowflake-to-Snowflake validation scenario.

        Returns:
            bool: False since this handles Teradata-to-Snowflake

        """
        return False

    def create_validation_environment_from_config(
        self,
        config_model: ConfigurationModel,
        data_validation_config_file: str,
        execution_mode: ExecutionMode,
        output_handler: Optional[ConsoleOutputHandler] = None,
    ):
        """Create validation environment from configuration file.

        Args:
            config_model: Configuration model loaded from YAML
            data_validation_config_file: Path to config file
            execution_mode: Execution mode for validation
            output_handler: Optional output handler

        Returns:
            Validation environment ready for execution

        """
        # Set up source and target connectors based on configuration
        source_connector = self._setup_source_from_config(config_model)
        target_connector = self._setup_target_from_config(config_model)

        # Set up validation environment using base class method
        return self.setup_validation_environment(
            source_connector=source_connector,
            target_connector=target_connector,
            data_validation_config_file=data_validation_config_file,
            output_directory_path=config_model.output_directory_path,
            output_handler=output_handler or ConsoleOutputHandler(),
        )

    def _setup_source_from_config(
        self, config_model: ConfigurationModel
    ) -> ConnectorBase:
        """Set up Teradata source connection from configuration model."""
        if not config_model.source_connection:
            raise typer.BadParameter(
                message="No source connection configured in YAML file. "
                "Please add a source_connection section to your configuration file."
            )

        source_conn = config_model.source_connection

        mode = getattr(source_conn, "mode", CREDENTIALS_CONNECTION_MODE)
        if mode == CREDENTIALS_CONNECTION_MODE:
            # Extract credentials from the source connection
            source_credentials = {
                "host": source_conn.host,
                "username": source_conn.username,
                "password": source_conn.password,
                "database": source_conn.database,
            }
            return self.setup_source_connection(
                source_conn_mode=CREDENTIALS_CONNECTION_MODE,
                teradata_credential_object=source_credentials,
            )
        else:
            raise typer.BadParameter(
                message=f"Unsupported source connection mode for Teradata: {mode}. "
                "Only 'credentials' mode is supported."
            )

    def _setup_target_from_config(
        self, config_model: ConfigurationModel
    ) -> ConnectorBase:
        """Set up target connection from configuration model."""
        if not config_model.target_connection:
            raise typer.BadParameter(
                message="No target connection configured in YAML file. "
                "Please add a target_connection section to your configuration file."
            )

        target_conn = config_model.target_connection
        target_platform = config_model.target_platform or "Snowflake"

        if target_platform.lower() == "snowflake":
            return self._setup_snowflake_target_from_config(target_conn)
        else:
            raise typer.BadParameter(
                message=f"Unsupported target platform: {target_platform}. "
                "Teradata only supports Snowflake as target."
            )

    def _setup_snowflake_target_from_config(self, target_conn) -> ConnectorBase:
        """Set up Snowflake target connection from configuration."""
        mode = getattr(target_conn, "mode", NAME_CONNECTION_MODE)
        if mode == NAME_CONNECTION_MODE:
            return self.setup_target_connection(
                snowflake_conn_mode=NAME_CONNECTION_MODE,
                snowflake_connection_name=getattr(target_conn, "name", None),
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

    def setup_source_connection(
        self,
        source_conn_mode: str = CREDENTIALS_CONNECTION_MODE,
        teradata_credential_object: Optional[dict[str, str]] = None,
        # Direct connection parameters for IPC mode
        source_host: Optional[str] = None,
        source_username: Optional[str] = None,
        source_password: Optional[str] = None,
        source_database: Optional[str] = None,
        **kwargs,
    ) -> ConnectorBase:
        """Set up Teradata source connection based on connection mode.

        Args:
            source_conn_mode: Connection mode (only credentials mode is supported for Teradata at this time)
            teradata_credential_object: Credentials dictionary
            source_host: Direct host parameter (for IPC)
            source_username: Direct username parameter (for IPC)
            source_password: Direct password parameter (for IPC)
            source_database: Direct database parameter (for IPC)
            **kwargs: Additional parameters

        Returns:
            ConnectorBase: Configured Teradata connector

        """
        # Handle IPC mode with direct parameters
        if (
            source_host
            and source_username
            and source_password
        ):
            teradata_credential_object = {
                "host": source_host,
                "username": source_username,
                "password": source_password,
                "database": source_database or "DBC",
            }
            source_conn_mode = CREDENTIALS_CONNECTION_MODE

        return self._setup_teradata_connection(
            source_conn_mode, teradata_credential_object
        )

    def setup_target_connection(
        self,
        snowflake_conn_mode: str = DEFAULT_CONNECTION_MODE,
        snowflake_connection_name: Optional[str] = None,
        snow_credential_object: Optional[dict[str, str]] = None,
        **kwargs,
    ) -> ConnectorBase:
        """Set up Snowflake target connection for Teradata migrations.

        Args:
            snowflake_conn_mode: Connection mode for Snowflake
            snowflake_connection_name: Connection name
            snow_credential_object: Snowflake credentials dictionary
            **kwargs: Additional parameters

        Returns:
            ConnectorBase: Configured Snowflake connector

        """
        return self._setup_snowflake_connection(
            snowflake_conn_mode, snowflake_connection_name, snow_credential_object
        )

    def get_source_templates_path(self) -> str:
        """Get Teradata templates path.

        TODO: Implement actual Teradata-specific templates in future PR.
        For now, using placeholder templates to avoid file not found errors.
        """
        current_dir = os.path.dirname(__file__)
        return os.path.join(current_dir, "extractor", "templates")

    def get_target_templates_path(self) -> str:
        """Get Snowflake target templates path."""
        current_dir = os.path.dirname(__file__)
        return os.path.join(current_dir, "..", "snowflake", "extractor", "templates")

    def _setup_teradata_connection(
        self,
        source_conn_mode: str,
        teradata_credential_object: Optional[dict[str, str]] = None,
    ) -> ConnectorTeradata:
        """Set up Teradata connector based on connection mode."""
        try:
            connector_teradata = ConnectorTeradata()

            if (
                source_conn_mode == DEFAULT_CONNECTION_MODE
                and not teradata_credential_object
            ):
                raise typer.BadParameter(
                    message="Source connection object cannot be empty."
                )

            if not teradata_credential_object:
                raise typer.BadParameter(
                    message="Teradata connection credentials are required."
                )

            # Validate required connection parameters
            required_params = ["host", "username", "password"]
            missing_params = [
                param
                for param in required_params
                if not teradata_credential_object.get(param)
            ]
            if missing_params:
                raise typer.BadParameter(
                    message=f"Missing required Teradata connection parameters: {', '.join(missing_params)}"
                )

            try:
                connector_teradata.connect(
                    host=teradata_credential_object["host"],
                    user=teradata_credential_object["username"],
                    password=teradata_credential_object["password"],
                    database=teradata_credential_object.get("database", "DBC")
                )
            except ConnectionError as e:
                raise ConnectionError(
                    f"Failed to establish Teradata connection: {e}"
                ) from e
            except ImportError as e:
                raise ImportError(f"Teradata dependencies not available: {e}") from e
            except ValueError as e:
                raise typer.BadParameter(
                    f"Invalid Teradata connection parameters: {e}"
                ) from e

            return connector_teradata

        except (typer.BadParameter, ConnectionError, ImportError):
            raise  # Re-raise these as-is
        except Exception as e:
            raise RuntimeError(
                f"Unexpected error setting up Teradata connection: {e}"
            ) from e

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
