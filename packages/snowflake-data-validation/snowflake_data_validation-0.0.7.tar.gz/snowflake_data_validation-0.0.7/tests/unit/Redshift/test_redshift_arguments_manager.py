import os
import pytest
from unittest.mock import MagicMock, patch, Mock
from pydantic import ValidationError
import typer

from snowflake.snowflake_data_validation.redshift.redshift_arguments_manager import RedshiftArgumentsManager
from snowflake.snowflake_data_validation.redshift.model.redshift_credentials_connection import RedshiftCredentialsConnection
from snowflake.snowflake_data_validation.configuration.model.configuration_model import ConfigurationModel
from snowflake.snowflake_data_validation.utils.constants import (
    CREDENTIALS_CONNECTION_MODE,
    DEFAULT_CONNECTION_MODE,
    NAME_CONNECTION_MODE,
    ExecutionMode,
    Platform,
    MISSING_SOURCE_CONNECTION_ERROR,
    MISSING_TARGET_CONNECTION_ERROR
)

class TestRedshiftArgumentsManager:

    def setup_method(self):
        self.manager = RedshiftArgumentsManager()

    def test_init(self):
        assert self.manager.source_platform == Platform.REDSHIFT
        assert self.manager.target_platform == Platform.SNOWFLAKE

    def test_is_snowflake_to_snowflake_property(self):
        assert self.manager.is_snowflake_to_snowflake is False

    @patch('snowflake.snowflake_data_validation.redshift.redshift_arguments_manager.NullConnector')
    @patch.object(RedshiftArgumentsManager, 'setup_validation_environment')
    def test_create_validation_environment_from_config_async_mode(self, mock_setup_env, mock_null_connector):
        mock_config = MagicMock()
        mock_config.output_directory_path = "/tmp/output"
        mock_null_instance = MagicMock()
        mock_null_connector.return_value = mock_null_instance
        
        result = self.manager.create_validation_environment_from_config(
            config_model=mock_config,
            data_validation_config_file="test_config.yaml",
            execution_mode=ExecutionMode.ASYNC_VALIDATION
        )
        
        mock_setup_env.assert_called_once()
        assert mock_null_connector.call_count == 2  # source and target

    @patch.object(RedshiftArgumentsManager, '_setup_source_from_config')
    @patch.object(RedshiftArgumentsManager, '_setup_target_from_config')
    @patch.object(RedshiftArgumentsManager, 'setup_validation_environment')
    def test_create_validation_environment_from_config_sync_mode(self, mock_setup_env, mock_setup_target, mock_setup_source):
        mock_config = MagicMock()
        mock_config.output_directory_path = "/tmp/output"
        mock_source_connector = MagicMock()
        mock_target_connector = MagicMock()
        mock_setup_source.return_value = mock_source_connector
        mock_setup_target.return_value = mock_target_connector
        
        result = self.manager.create_validation_environment_from_config(
            config_model=mock_config,
            data_validation_config_file="test_config.yaml",
            execution_mode=ExecutionMode.SYNC_VALIDATION
        )
        
        mock_setup_source.assert_called_once_with(mock_config)
        mock_setup_target.assert_called_once_with(mock_config)
        mock_setup_env.assert_called_once()

    @patch('snowflake.snowflake_data_validation.redshift.redshift_arguments_manager.ConnectorRedshift')
    def test_setup_source_connection_success(self, mock_connector_class):
        mock_connector = MagicMock()
        mock_connector_class.return_value = mock_connector
        
        redshift_creds = RedshiftCredentialsConnection(
            host="localhost",
            port=5439,
            username="user",
            password="pass",
            database="db"
        )
        
        result = self.manager.setup_source_connection(redshift_creds)
        
        assert result == mock_connector
        mock_connector.connect.assert_called_once()

    @patch('snowflake.snowflake_data_validation.redshift.redshift_arguments_manager.ConnectorRedshift')
    def test_setup_source_connection_connection_error(self, mock_connector_class):
        mock_connector = MagicMock()
        mock_connector.connect.side_effect = ConnectionError("Connection failed")
        mock_connector_class.return_value = mock_connector
        
        redshift_creds = RedshiftCredentialsConnection(
            host="localhost",
            port=5439,
            username="user",
            password="pass",
            database="db"
        )
        
        with pytest.raises(ConnectionError, match="Failed to establish Redshift connection"):
            self.manager.setup_source_connection(redshift_creds)

    @patch('snowflake.snowflake_data_validation.redshift.redshift_arguments_manager.ConnectorRedshift')
    def test_setup_source_connection_validation_error(self, mock_connector_class):
        mock_connector = MagicMock()
        mock_connector.connect.side_effect = ValidationError.from_exception_data("ValidationError", [])
        mock_connector_class.return_value = mock_connector
        
        redshift_creds = RedshiftCredentialsConnection(
            host="localhost",
            port=5439,
            username="user",
            password="pass",
            database="db"
        )
        
        with pytest.raises(typer.BadParameter, match="Invalid Redshift connection parameters"):
            self.manager.setup_source_connection(redshift_creds)

    @patch('snowflake.snowflake_data_validation.redshift.redshift_arguments_manager.ConnectorRedshift')
    def test_setup_source_connection_import_error(self, mock_connector_class):
        mock_connector_class.side_effect = ImportError("Import failed")
        
        redshift_creds = RedshiftCredentialsConnection(
            host="localhost",
            port=5439,
            username="user",
            password="pass",
            database="db"
        )
        
        with pytest.raises(ImportError, match="Redshift dependencies not available"):
            self.manager.setup_source_connection(redshift_creds)

    @patch('snowflake.snowflake_data_validation.redshift.redshift_arguments_manager.ConnectorRedshift')
    def test_setup_source_connection_generic_error(self, mock_connector_class):
        mock_connector = MagicMock()
        mock_connector.connect.side_effect = Exception("Generic error")
        mock_connector_class.return_value = mock_connector
        
        redshift_creds = RedshiftCredentialsConnection(
            host="localhost",
            port=5439,
            username="user",
            password="pass",
            database="db"
        )
        
        with pytest.raises(Exception, match="Unexpected error while setting up Redshift connection"):
            self.manager.setup_source_connection(redshift_creds)

    def test_get_source_templates_path(self):
        result = self.manager.get_source_templates_path()
        expected_path = os.path.join(os.path.dirname(__file__), "..", "..", "src", "snowflake", "snowflake_data_validation", "redshift", "extractor", "templates")
        assert "extractor" in result
        assert "templates" in result

    @patch.object(RedshiftArgumentsManager, '_setup_snowflake_connection')
    def test_setup_target_connection_default_mode(self, mock_setup_snowflake):
        mock_connector = MagicMock()
        mock_setup_snowflake.return_value = mock_connector
        
        result = self.manager.setup_target_connection()
        
        assert result == mock_connector
        mock_setup_snowflake.assert_called_once_with(DEFAULT_CONNECTION_MODE, None, None)

    @patch.object(RedshiftArgumentsManager, '_setup_snowflake_connection')
    def test_setup_target_connection_with_credentials(self, mock_setup_snowflake):
        """Test target connection setup with credentials."""
        mock_connector = MagicMock()
        mock_setup_snowflake.return_value = mock_connector
        
        snow_creds = {"account": "test_account", "username": "test_user"}
        
        result = self.manager.setup_target_connection(
            snowflake_conn_mode=NAME_CONNECTION_MODE,
            snowflake_connection_name="test_conn",
            snow_credential_object=snow_creds
        )
        
        assert result == mock_connector
        mock_setup_snowflake.assert_called_once_with(NAME_CONNECTION_MODE, "test_conn", snow_creds)

    def test_get_target_templates_path(self):
        result = self.manager.get_target_templates_path()
        assert "snowflake" in result
        assert "extractor" in result
        assert "templates" in result

    @patch.object(RedshiftArgumentsManager, 'setup_source_connection')
    def test_setup_source_from_config_credentials_mode(self, mock_setup_source):
        mock_config = MagicMock()
        mock_config.target_connection = MagicMock()
        mock_config.source_connection = MagicMock()
        mock_config.source_connection.mode = CREDENTIALS_CONNECTION_MODE
        mock_config.source_connection.host = "localhost"
        mock_config.source_connection.port = 5439
        mock_config.source_connection.username = "user"
        mock_config.source_connection.password = "pass"
        mock_config.source_connection.database = "db"
        
        mock_connector = MagicMock()
        mock_setup_source.return_value = mock_connector
        
        result = self.manager._setup_source_from_config(mock_config)
        
        assert result == mock_connector
        mock_setup_source.assert_called_once()

    def test_setup_source_from_config_missing_target_connection(self):
        mock_config = MagicMock()
        mock_config.target_connection = None
        
        with pytest.raises(typer.BadParameter, match=MISSING_SOURCE_CONNECTION_ERROR):
            self.manager._setup_source_from_config(mock_config)

    def test_setup_source_from_config_unsupported_mode(self):
        mock_config = MagicMock()
        mock_config.target_connection = MagicMock()
        mock_config.source_connection = MagicMock()
        mock_config.source_connection.mode = "unsupported_mode"
        
        with pytest.raises(typer.BadParameter, match="Unsupported source connection mode"):
            self.manager._setup_source_from_config(mock_config)

    @patch('snowflake.snowflake_data_validation.redshift.redshift_arguments_manager.ConnectorSnowflake')
    def test_setup_snowflake_connection_name_mode_success(self, mock_connector_class):
        mock_connector = MagicMock()
        mock_connector_class.return_value = mock_connector
        
        result = self.manager._setup_snowflake_connection(
            snowflake_conn_mode=NAME_CONNECTION_MODE,
            snowflake_connection_name="test_conn"
        )
        
        assert result == mock_connector
        mock_connector.connect.assert_called_once()

    @patch('snowflake.snowflake_data_validation.redshift.redshift_arguments_manager.ConnectorSnowflake')
    def test_setup_snowflake_connection_name_mode_missing_name(self, mock_connector_class):
        """Test Snowflake connection setup with name mode but missing name."""
        with pytest.raises(typer.BadParameter, match="you must provide the Snowflake connection name"):
            self.manager._setup_snowflake_connection(
                snowflake_conn_mode=NAME_CONNECTION_MODE,
                snowflake_connection_name=None
            )

    @patch('snowflake.snowflake_data_validation.redshift.redshift_arguments_manager.ConnectorSnowflake')
    def test_setup_snowflake_connection_with_credentials(self, mock_connector_class):
        """Test Snowflake connection setup with credentials."""
        mock_connector = MagicMock()
        mock_connector_class.return_value = mock_connector
        
        snow_creds = {
            "account": "test_account",
            "username": "test_user",
            "password": "test_pass",
            "database": "test_db",
            "schema": "test_schema",
            "warehouse": "test_wh",
            "role": "test_role"
        }
        
        result = self.manager._setup_snowflake_connection(
            snowflake_conn_mode=DEFAULT_CONNECTION_MODE,
            snow_credential_object=snow_creds
        )
        
        assert result == mock_connector
        mock_connector.connect.assert_called_once()

    @patch('snowflake.snowflake_data_validation.redshift.redshift_arguments_manager.ConnectorSnowflake')
    def test_setup_snowflake_connection_error(self, mock_connector_class):
        """Test Snowflake connection setup with error."""
        mock_connector = MagicMock()
        mock_connector.connect.side_effect = Exception("Connection failed")
        mock_connector_class.return_value = mock_connector
        
        with pytest.raises(RuntimeError, match="Failed to set up Snowflake connection"):
            self.manager._setup_snowflake_connection(
                snowflake_conn_mode=DEFAULT_CONNECTION_MODE
            )

    @patch.object(RedshiftArgumentsManager, 'setup_target_connection')
    def test_setup_target_from_config_name_mode(self, mock_setup_target):
        """Test setup target from config with name mode."""
        mock_config = MagicMock()
        mock_config.target_connection = MagicMock()
        mock_config.target_connection.mode = NAME_CONNECTION_MODE
        mock_config.target_connection.name = "test_conn"
        
        mock_connector = MagicMock()
        mock_setup_target.return_value = mock_connector
        
        result = self.manager._setup_target_from_config(mock_config)
        
        assert result == mock_connector
        mock_setup_target.assert_called_once_with(
            snowflake_conn_mode=NAME_CONNECTION_MODE,
            snowflake_connection_name="test_conn"
        )

    @patch.object(RedshiftArgumentsManager, 'setup_target_connection')
    def test_setup_target_from_config_default_mode(self, mock_setup_target):
        """Test setup target from config with default mode."""
        mock_config = MagicMock()
        mock_config.target_connection = MagicMock()
        mock_config.target_connection.mode = DEFAULT_CONNECTION_MODE
        
        mock_connector = MagicMock()
        mock_setup_target.return_value = mock_connector
        
        result = self.manager._setup_target_from_config(mock_config)
        
        assert result == mock_connector
        mock_setup_target.assert_called_once_with(
            snowflake_conn_mode=DEFAULT_CONNECTION_MODE
        )

    def test_setup_target_from_config_missing_target_connection(self):
        """Test setup target from config with missing target connection."""
        mock_config = MagicMock()
        mock_config.target_connection = None
        
        with pytest.raises(typer.BadParameter, match=MISSING_TARGET_CONNECTION_ERROR):
            self.manager._setup_target_from_config(mock_config)

    def test_setup_target_from_config_unsupported_mode(self):
        """Test setup target from config with unsupported mode."""
        mock_config = MagicMock()
        mock_config.target_connection = MagicMock()
        mock_config.target_connection.mode = "unsupported_mode"
        
        with pytest.raises(typer.BadParameter, match="Unsupported target connection mode"):
            self.manager._setup_target_from_config(mock_config)


# =============================================================================
# PYTEST FIXTURES
# =============================================================================

@pytest.fixture
def mock_redshift_credentials():
    """Mock Redshift credentials for testing."""
    return RedshiftCredentialsConnection(
        host="localhost",
        port=5439,
        username="testuser",
        password="testpass",
        database="testdb"
    )


@pytest.fixture
def mock_config_model():
    """Mock configuration model for testing."""
    mock_config = MagicMock(spec=ConfigurationModel)
    mock_config.output_directory_path = "/tmp/output"
    mock_config.source_connection = MagicMock()
    mock_config.target_connection = MagicMock()
    return mock_config


@pytest.fixture
def mock_snowflake_credentials():
    """Mock Snowflake credentials for testing."""
    return {
        "account": "test_account",
        "username": "test_user",
        "password": "test_pass",
        "database": "test_db",
        "schema": "test_schema",
        "warehouse": "test_wh",
        "role": "test_role"
    } 