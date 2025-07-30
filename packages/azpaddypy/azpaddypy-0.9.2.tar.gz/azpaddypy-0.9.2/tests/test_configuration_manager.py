"""
Pytest tests for the Configuration Manager tool.

Tests cover configuration loading, access tracking, reporting,
health checks, and error handling scenarios.
"""

import pytest
import os
import json
import tempfile
import pathlib
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from azpaddypy.tools.configuration_manager import (
    ConfigurationManager,
    create_configuration_manager,
    ConfigSource,
    ConfigEntry
)
from azpaddypy.mgmt.logging import AzureLogger
from azpaddypy.builder.configuration import EnvironmentConfiguration


class TestConfigEntry:
    """Test the ConfigEntry dataclass."""

    def test_config_entry_creation(self):
        """Test ConfigEntry creation with defaults."""
        entry = ConfigEntry(
            key="test_key",
            value="test_value",
            source=ConfigSource.ENVIRONMENT,
            source_detail="Environment Variable"
        )
        
        assert entry.key == "test_key"
        assert entry.value == "test_value"
        assert entry.source == ConfigSource.ENVIRONMENT
        assert entry.source_detail == "Environment Variable"
        assert entry.access_count == 0
        assert isinstance(entry.loaded_at, float)
        assert isinstance(entry.last_accessed, float)

    def test_mark_accessed(self):
        """Test access tracking functionality."""
        entry = ConfigEntry(
            key="test_key",
            value="test_value",
            source=ConfigSource.ENVIRONMENT,
            source_detail="Environment Variable"
        )
        
        initial_access_time = entry.last_accessed
        initial_count = entry.access_count
        
        time.sleep(0.1)  # Small delay to ensure time difference
        entry.mark_accessed()
        
        assert entry.access_count == initial_count + 1
        assert entry.last_accessed > initial_access_time

    def test_human_readable_timestamps(self):
        """Test human readable timestamp formatting."""
        entry = ConfigEntry(
            key="test_key",
            value="test_value", 
            source=ConfigSource.ENVIRONMENT,
            source_detail="Environment Variable"
        )
        
        # Test loaded time format
        loaded_str = entry.get_human_readable_loaded_at()
        assert isinstance(loaded_str, str)
        assert len(loaded_str) == 19  # YYYY-MM-DD HH:MM:SS format
        
        # Test last access time format
        access_str = entry.get_human_readable_last_access()
        assert isinstance(access_str, str)
        assert len(access_str) == 19  # YYYY-MM-DD HH:MM:SS format


class TestConfigurationManager:
    """Test the ConfigurationManager class."""

    @pytest.fixture
    def temp_config_dir(self):
        """Create a temporary directory with test config files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = pathlib.Path(temp_dir) / "configs"
            config_dir.mkdir()
            
            # Create test JSON files
            database_config = {
                "database": {
                    "host": "localhost",
                    "port": 5432,
                    "name": "testdb"
                },
                "cache": {
                    "enabled": True,
                    "ttl": 3600
                }
            }
            
            features_config = {
                "features": {
                    "new_ui": {"enabled": True},
                    "beta_mode": {"enabled": False}
                }
            }
            
            # Write config files
            with open(config_dir / "database.json", "w") as f:
                json.dump(database_config, f)
                
            with open(config_dir / "features.json", "w") as f:
                json.dump(features_config, f)
            
            # Create invalid JSON file
            with open(config_dir / "invalid.json", "w") as f:
                f.write("{ invalid json }")
            
            yield str(config_dir)

    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger for testing."""
        logger = Mock(spec=AzureLogger)
        logger.create_span = MagicMock()
        logger.create_span.return_value.__enter__ = Mock()
        logger.create_span.return_value.__exit__ = Mock()
        return logger

    @pytest.fixture
    def mock_environment_config(self):
        """Create a mock EnvironmentConfiguration for testing."""
        return EnvironmentConfiguration(
            running_in_docker=False,
            local_settings={},
            local_env_manager=Mock(),
            service_name="test_service",
            service_version="1.0.0",
            reflection_kind="test",
            logger_enable_console=True,
            logger_connection_string=None,
            logger_instrumentation_options={},
            logger_log_level="INFO",
            identity_enable_token_cache=True,
            identity_allow_unencrypted_storage=True,
            identity_custom_credential_options=None,
            identity_connection_string=None,
        )

    @pytest.fixture
    def config_manager(self, temp_config_dir, mock_logger, mock_environment_config):
        """Create a ConfigurationManager for testing."""
        with patch.dict(os.environ, {"TEST_VAR": "test_value", "APP_CONFIG": "app_value"}):
            return ConfigurationManager(
                environment_configuration=mock_environment_config,
                configs_dir=temp_config_dir,
                auto_reload=False,
                include_env_vars=True,
                env_var_prefix="TEST_",
                logger=mock_logger
            )

    def test_initialization(self, config_manager, mock_logger):
        """Test ConfigurationManager initialization."""
        assert config_manager.service_name == "test_service"
        assert config_manager.service_version == "1.0.0"
        assert config_manager.logger == mock_logger
        assert config_manager.auto_reload is False
        assert config_manager.include_env_vars is True
        assert config_manager.env_var_prefix == "TEST_"
        assert len(config_manager._config_entries) > 0

    def test_environment_variable_loading(self, temp_config_dir, mock_logger, mock_environment_config):
        """Test loading environment variables with prefix filtering."""
        with patch.dict(os.environ, {"TEST_VAR1": "value1", "TEST_VAR2": "value2", "OTHER_VAR": "other"}):
            manager = ConfigurationManager(
                environment_configuration=mock_environment_config,
                configs_dir=temp_config_dir,
                env_var_prefix="TEST_",
                logger=mock_logger
            )
            
            # Should load TEST_ prefixed vars
            assert manager.get_config("TEST_VAR1") == "value1"
            assert manager.get_config("TEST_VAR2") == "value2"
            
            # Should not load non-prefixed vars
            assert manager.get_config("OTHER_VAR") is None

    def test_json_config_loading(self, config_manager):
        """Test loading JSON configuration files."""
        # Test flattened JSON access
        assert config_manager.get_config("database.host") == "localhost"
        assert config_manager.get_config("database.port") == 5432
        assert config_manager.get_config("cache.enabled") is True
        assert config_manager.get_config("features.new_ui.enabled") is True
        assert config_manager.get_config("features.beta_mode.enabled") is False

    def test_get_config_with_defaults(self, config_manager):
        """Test getting configuration with default values."""
        # Existing key
        assert config_manager.get_config("database.host", "default") == "localhost"
        
        # Non-existing key with default
        assert config_manager.get_config("nonexistent.key", "default_value") == "default_value"
        
        # Non-existing key without default
        assert config_manager.get_config("nonexistent.key") is None

    def test_access_tracking(self, config_manager):
        """Test configuration access tracking."""
        key = "database.host"
        
        # Get initial access count
        entry = config_manager._config_entries[key]
        initial_count = entry.access_count
        initial_time = entry.last_accessed
        
        time.sleep(0.1)  # Small delay
        
        # Access the configuration
        value = config_manager.get_config(key)
        
        # Verify access tracking
        assert value == "localhost"
        assert entry.access_count == initial_count + 1
        assert entry.last_accessed > initial_time

    def test_has_config(self, config_manager):
        """Test configuration existence checking."""
        assert config_manager.has_config("database.host") is True
        assert config_manager.has_config("nonexistent.key") is False

    def test_get_all_configs(self, config_manager):
        """Test getting all configurations."""
        all_configs = config_manager.get_all_configs()
        
        assert isinstance(all_configs, dict)
        assert "database.host" in all_configs
        assert "features.new_ui.enabled" in all_configs
        assert all_configs["database.host"] == "localhost"

    def test_repr_method(self, config_manager):
        """Test __repr__ method for verbose output."""
        repr_output = repr(config_manager)
        
        assert "Configuration Manager Report" in repr_output
        assert "test_service v1.0.0" in repr_output
        assert "Total Entries:" in repr_output
        assert "database.host" in repr_output
        assert "Last Access:" in repr_output
        assert "Access Count:" in repr_output
        
        # Test sensitive value hiding
        config_manager._config_entries["secret_password"] = ConfigEntry(
            key="secret_password",
            value="sensitive_value",
            source=ConfigSource.ENVIRONMENT,
            source_detail="Environment Variable"
        )
        
        repr_output = repr(config_manager)
        assert "[HIDDEN]" in repr_output

    def test_get_filtered_report(self, config_manager):
        """Test filtered configuration reporting."""
        # Test with prefix filter
        report = config_manager.get_filtered_report(filter_prefix="database", show_values=True)
        
        assert "Filtered Configuration Report" in report
        assert "database.host" in report
        assert "localhost" in report
        assert "features.new_ui" not in report
        
        # Test with value hiding
        report = config_manager.get_filtered_report(filter_prefix="database", show_values=False)
        assert "[HIDDEN]" in report

    def test_get_access_stats(self, config_manager):
        """Test access statistics generation."""
        # Access some configurations
        config_manager.get_config("database.host")
        config_manager.get_config("database.port")
        config_manager.get_config("database.host")  # Access twice
        
        stats = config_manager.get_access_stats()
        
        assert isinstance(stats, dict)
        assert "total_entries" in stats
        assert "accessed_entries" in stats
        assert "unaccessed_entries" in stats
        assert "total_accesses" in stats
        assert "most_accessed_key" in stats
        assert "most_accessed_count" in stats
        assert "sources" in stats
        
        assert stats["total_accesses"] >= 3
        assert stats["accessed_entries"] >= 2
        assert stats["most_accessed_key"] == "database.host"
        assert stats["most_accessed_count"] == 2

    def test_health_check(self, config_manager):
        """Test health check functionality."""
        health = config_manager.health_check()
        
        assert isinstance(health, dict)
        assert health["status"] == "healthy"
        assert "timestamp" in health
        assert "service" in health
        assert "checks" in health
        
        # Verify service info
        assert health["service"]["name"] == "test_service"
        assert health["service"]["version"] == "1.0.0"
        
        # Verify checks
        checks = health["checks"]
        assert "configs_directory" in checks
        assert "configuration_loading" in checks
        assert "file_accessibility" in checks

    def test_reload_configs(self, config_manager, temp_config_dir):
        """Test manual configuration reloading."""
        # Verify initial state - new config shouldn't exist
        assert config_manager.get_config("new_section.value") is None
        
        # Add new config file
        new_config = {"new_section": {"value": "test"}}
        with open(pathlib.Path(temp_config_dir) / "new_config.json", "w") as f:
            json.dump(new_config, f)
        
        # Reload
        result = config_manager.reload_configs()
        
        assert result is True
        # Verify the new config was loaded
        assert config_manager.get_config("new_section.value") == "test"

    def test_auto_reload(self, temp_config_dir, mock_logger, mock_environment_config):
        """Test automatic configuration reloading."""
        manager = ConfigurationManager(
            environment_configuration=mock_environment_config,
            configs_dir=temp_config_dir,
            auto_reload=True,
            logger=mock_logger
        )
        
        # Modify a config file
        config_file = pathlib.Path(temp_config_dir) / "database.json"
        time.sleep(0.1)  # Ensure file timestamp difference
        
        new_config = {"database": {"host": "updated_host"}}
        with open(config_file, "w") as f:
            json.dump(new_config, f)
        
        # Access config to trigger reload check
        value = manager.get_config("database.host")
        assert value == "updated_host"

    def test_missing_configs_directory(self, mock_logger, mock_environment_config):
        """Test behavior when configs directory doesn't exist."""
        manager = ConfigurationManager(
            environment_configuration=mock_environment_config,
            configs_dir="/nonexistent/path",
            include_env_vars=False,
            logger=mock_logger
        )
        
        # Should handle gracefully
        assert len(manager._config_entries) == 0
        assert manager.get_config("any.key") is None

    def test_invalid_json_handling(self, temp_config_dir, mock_logger, mock_environment_config):
        """Test handling of invalid JSON files."""
        manager = ConfigurationManager(
            environment_configuration=mock_environment_config,
            configs_dir=temp_config_dir,
            include_env_vars=False,
            logger=mock_logger
        )
        
        # Should load valid configs despite invalid ones
        assert manager.get_config("database.host") == "localhost"
        
        # Should log errors for invalid files
        mock_logger.error.assert_called()

    def test_no_environment_variables(self, temp_config_dir, mock_logger, mock_environment_config):
        """Test configuration manager without environment variables."""
        manager = ConfigurationManager(
            environment_configuration=mock_environment_config,
            configs_dir=temp_config_dir,
            include_env_vars=False,
            logger=mock_logger
        )
        
        # Should only have config file entries
        all_configs = manager.get_all_configs()
        env_vars = [k for k in all_configs.keys() if not "." in k]
        
        # Should have minimal environment variables (if any)
        assert len(env_vars) == 0

    def test_json_flattening(self, config_manager):
        """Test nested JSON flattening with dot notation."""
        # Test deeply nested structure
        nested_config = {
            "level1": {
                "level2": {
                    "level3": {
                        "value": "deep_value"
                    }
                }
            }
        }
        
        flattened = config_manager._flatten_json(nested_config, "test")
        expected_key = "test.level1.level2.level3.value"
        
        assert expected_key in flattened
        assert flattened[expected_key] == "deep_value"


class TestConfigurationManagerFactory:
    """Test the create_configuration_manager factory function."""

    def test_factory_function(self):
        """Test configuration manager creation via factory function."""
        # Create mock environment config for factory test
        mock_env_config = EnvironmentConfiguration(
            running_in_docker=False,
            local_settings={},
            local_env_manager=Mock(),
            service_name="test_factory",
            service_version="2.0.0",
            reflection_kind="test",
            logger_enable_console=True,
            logger_connection_string=None,
            logger_instrumentation_options={},
            logger_log_level="INFO",
            identity_enable_token_cache=True,
            identity_allow_unencrypted_storage=True,
            identity_custom_credential_options=None,
            identity_connection_string=None,
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = create_configuration_manager(
                environment_configuration=mock_env_config,
                configs_dir=temp_dir,
                auto_reload=True,
                include_env_vars=False,
                env_var_prefix="FACTORY_"
            )
            
            assert isinstance(manager, ConfigurationManager)
            assert manager.service_name == "test_factory"
            assert manager.service_version == "2.0.0"
            assert manager.auto_reload is True
            assert manager.include_env_vars is False
            assert manager.env_var_prefix == "FACTORY_"

    def test_factory_with_custom_logger(self):
        """Test factory function with custom logger."""
        mock_logger = Mock(spec=AzureLogger)
        mock_logger.create_span = MagicMock()
        mock_logger.create_span.return_value.__enter__ = Mock()
        mock_logger.create_span.return_value.__exit__ = Mock()
        
        # Create mock environment config
        mock_env_config = EnvironmentConfiguration(
            running_in_docker=False,
            local_settings={},
            local_env_manager=Mock(),
            service_name="test_service",
            service_version="1.0.0",
            reflection_kind="test",
            logger_enable_console=True,
            logger_connection_string=None,
            logger_instrumentation_options={},
            logger_log_level="INFO",
            identity_enable_token_cache=True,
            identity_allow_unencrypted_storage=True,
            identity_custom_credential_options=None,
            identity_connection_string=None,
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = create_configuration_manager(
                environment_configuration=mock_env_config,
                configs_dir=temp_dir,
                logger=mock_logger
            )
            
            assert manager.logger == mock_logger


class TestConfigurationManagerIntegration:
    """Integration tests for ConfigurationManager."""

    def test_realistic_scenario(self):
        """Test a realistic configuration management scenario."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = pathlib.Path(temp_dir) / "configs"
            config_dir.mkdir()
            
            # Create realistic config files
            app_config = {
                "app": {
                    "name": "MyApp",
                    "version": "1.0.0",
                    "debug": False
                },
                "database": {
                    "host": "prod-db.example.com",
                    "port": 5432,
                    "ssl": True
                },
                "features": {
                    "analytics": {"enabled": True},
                    "beta_ui": {"enabled": False}
                }
            }
            
            limits_config = {
                "limits": {
                    "max_requests_per_minute": 1000,
                    "max_upload_size_mb": 100,
                    "session_timeout_minutes": 30
                }
            }
            
            with open(config_dir / "app.json", "w") as f:
                json.dump(app_config, f)
            with open(config_dir / "limits.json", "w") as f:
                json.dump(limits_config, f)
            
            # Set environment variables
            env_vars = {
                "APP_ENV": "production",
                "APP_DEBUG": "false",
                "DATABASE_PASSWORD": "secret123"
            }
            
            with patch.dict(os.environ, env_vars):
                # Create mock environment config for integration test
                integration_env_config = EnvironmentConfiguration(
                    running_in_docker=False,
                    local_settings={},
                    local_env_manager=Mock(),
                    service_name="integration_test",
                    service_version="1.0.0",
                    reflection_kind="test",
                    logger_enable_console=True,
                    logger_connection_string=None,
                    logger_instrumentation_options={},
                    logger_log_level="INFO",
                    identity_enable_token_cache=True,
                    identity_allow_unencrypted_storage=True,
                    identity_custom_credential_options=None,
                    identity_connection_string=None,
                )
                
                manager = create_configuration_manager(
                    environment_configuration=integration_env_config,
                    configs_dir=str(config_dir),
                    auto_reload=True,
                    include_env_vars=True,
                    env_var_prefix="APP_"
                )
                
                # Test various configuration access patterns
                assert manager.get_config("app.name") == "MyApp"
                assert manager.get_config("database.host") == "prod-db.example.com"
                assert manager.get_config("features.analytics.enabled") is True
                assert manager.get_config("limits.max_requests_per_minute") == 1000
                assert manager.get_config("APP_ENV") == "production"
                
                # Test defaults
                assert manager.get_config("nonexistent.key", "default") == "default"
                
                # Test health check
                health = manager.health_check()
                assert health["status"] == "healthy"
                
                # Test repr output
                repr_output = repr(manager)
                assert "integration_test" in repr_output
                assert "app.name" in repr_output
                
                # Test access statistics
                stats = manager.get_access_stats()
                assert stats["total_accesses"] >= 5
                
                # Test filtered reporting
                app_report = manager.get_filtered_report(filter_prefix="app")
                assert "app.name" in app_report
                assert "database.host" not in app_report 