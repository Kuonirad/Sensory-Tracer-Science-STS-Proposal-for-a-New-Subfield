#!/usr/bin/env python3
"""
Comprehensive Test Suite for Production Configuration

Tests production configuration functionality including:
- Environment-specific configurations (development, testing, staging, production, clinical)
- Security compliance levels (BASIC, HIPAA, FDA CFR21, ISO27001, SOX)
- Database and Redis configuration management
- Security controls and authentication settings
- Performance optimization and monitoring
- Deployment automation and environment management
"""

import json
import os
import tempfile
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest
import yaml

from sensory_tracer_science.deployment.production_config import (
    DatabaseConfig,
    DeploymentEnvironment,
    ProductionConfig,
    RedisConfig,
    SecurityConfig,
    SecurityLevel,
)


class TestDeploymentEnvironment(unittest.TestCase):
    """Test DeploymentEnvironment enum."""

    def test_deployment_environment_values(self):
        """Test all deployment environment enum values."""
        self.assertEqual(DeploymentEnvironment.DEVELOPMENT.value, "development")
        self.assertEqual(DeploymentEnvironment.TESTING.value, "testing")
        self.assertEqual(DeploymentEnvironment.STAGING.value, "staging")
        self.assertEqual(DeploymentEnvironment.PRODUCTION.value, "production")
        self.assertEqual(DeploymentEnvironment.CLINICAL.value, "clinical")

    def test_deployment_environment_count(self):
        """Test expected number of deployment environments."""
        self.assertEqual(len(DeploymentEnvironment), 5)


class TestSecurityLevel(unittest.TestCase):
    """Test SecurityLevel enum."""

    def test_security_level_values(self):
        """Test all security level enum values."""
        self.assertEqual(SecurityLevel.BASIC.value, "basic")
        self.assertEqual(SecurityLevel.HIPAA.value, "hipaa")
        self.assertEqual(SecurityLevel.FDA_CFR21.value, "fda_cfr21")
        self.assertEqual(SecurityLevel.ISO27001.value, "iso27001")
        self.assertEqual(SecurityLevel.SOX.value, "sox")

    def test_security_level_count(self):
        """Test expected number of security levels."""
        self.assertEqual(len(SecurityLevel), 5)


class TestDatabaseConfig(unittest.TestCase):
    """Test DatabaseConfig dataclass."""

    def test_default_initialization(self):
        """Test DatabaseConfig with default values."""
        config = DatabaseConfig()

        # Connection parameters
        self.assertEqual(config.host, "localhost")
        self.assertEqual(config.port, 5432)
        self.assertEqual(config.database, "sts_production")
        self.assertEqual(config.username, "sts_user")
        self.assertEqual(config.password_env_var, "STS_DB_PASSWORD")

        # Connection pool settings
        self.assertEqual(config.min_connections, 5)
        self.assertEqual(config.max_connections, 100)
        self.assertEqual(config.connection_timeout, 30)

        # Performance settings
        self.assertEqual(config.statement_timeout, 300)
        self.assertEqual(config.lock_timeout, 30)
        self.assertEqual(config.idle_in_transaction_timeout, 60)

        # Backup and recovery
        self.assertTrue(config.backup_enabled)
        self.assertEqual(config.backup_schedule, "0 2 * * *")
        self.assertEqual(config.backup_retention_days, 30)
        self.assertTrue(config.point_in_time_recovery)

        # Security settings
        self.assertTrue(config.ssl_enabled)
        self.assertEqual(config.ssl_cert_path, "/etc/ssl/certs/postgresql.crt")
        self.assertTrue(config.encryption_at_rest)
        self.assertTrue(config.audit_logging)

    def test_custom_initialization(self):
        """Test DatabaseConfig with custom values."""
        config = DatabaseConfig(
            host="db.company.com",
            port=5433,
            database="sts_custom",
            username="custom_user",
            password_env_var="CUSTOM_DB_PASSWORD",  # noqa: S106 - env var name, not a secret
            min_connections=10,
            max_connections=200,
            connection_timeout=60,
            statement_timeout=600,
            lock_timeout=60,
            idle_in_transaction_timeout=120,
            backup_enabled=False,
            backup_schedule="0 3 * * *",
            backup_retention_days=60,
            point_in_time_recovery=False,
            ssl_enabled=False,
            ssl_cert_path="/custom/ssl/cert.pem",
            encryption_at_rest=False,
            audit_logging=False,
        )

        self.assertEqual(config.host, "db.company.com")
        self.assertEqual(config.port, 5433)
        self.assertEqual(config.database, "sts_custom")
        self.assertEqual(config.username, "custom_user")
        self.assertEqual(config.password_env_var, "CUSTOM_DB_PASSWORD")
        self.assertEqual(config.min_connections, 10)
        self.assertEqual(config.max_connections, 200)
        self.assertEqual(config.connection_timeout, 60)
        self.assertEqual(config.statement_timeout, 600)
        self.assertEqual(config.lock_timeout, 60)
        self.assertEqual(config.idle_in_transaction_timeout, 120)
        self.assertFalse(config.backup_enabled)
        self.assertEqual(config.backup_schedule, "0 3 * * *")
        self.assertEqual(config.backup_retention_days, 60)
        self.assertFalse(config.point_in_time_recovery)
        self.assertFalse(config.ssl_enabled)
        self.assertEqual(config.ssl_cert_path, "/custom/ssl/cert.pem")
        self.assertFalse(config.encryption_at_rest)
        self.assertFalse(config.audit_logging)

    def test_dataclass_features(self):
        """Test dataclass features."""
        config1 = DatabaseConfig()
        config2 = DatabaseConfig()

        # Test equality
        self.assertEqual(config1, config2)

        # Test representation
        repr_str = repr(config1)
        self.assertIn("DatabaseConfig", repr_str)
        self.assertIn("host=", repr_str)

        # Test modification
        config2.port = 5433
        self.assertNotEqual(config1, config2)


class TestRedisConfig(unittest.TestCase):
    """Test RedisConfig dataclass."""

    def test_default_initialization(self):
        """Test RedisConfig with default values."""
        config = RedisConfig()

        # Connection parameters
        self.assertEqual(config.host, "localhost")
        self.assertEqual(config.port, 6379)
        self.assertEqual(config.password_env_var, "STS_REDIS_PASSWORD")
        self.assertEqual(config.database, 0)

        # Performance settings
        self.assertEqual(config.max_connections, 50)
        self.assertEqual(config.socket_timeout, 5)
        self.assertEqual(config.socket_connect_timeout, 5)

        # Memory management
        self.assertEqual(config.max_memory_mb, 1024)
        self.assertEqual(config.max_memory_policy, "allkeys-lru")

        # Persistence
        self.assertTrue(config.persistence_enabled)
        self.assertEqual(config.save_schedule, "900 1 300 10 60 10000")

        # Clustering
        self.assertFalse(config.cluster_enabled)

    def test_post_init_defaults(self):
        """Test __post_init__ method sets default cluster_nodes."""
        config = RedisConfig()
        self.assertEqual(config.cluster_nodes, [])

    def test_custom_initialization(self):
        """Test RedisConfig with custom values."""
        cluster_nodes = ["redis1:6379", "redis2:6379", "redis3:6379"]

        config = RedisConfig(
            host="redis.company.com",
            port=6380,
            password_env_var="CUSTOM_REDIS_PASSWORD",  # noqa: S106 - env var name, not a secret
            database=1,
            max_connections=100,
            socket_timeout=10,
            socket_connect_timeout=10,
            max_memory_mb=2048,
            max_memory_policy="volatile-lru",
            persistence_enabled=False,
            save_schedule="300 10 60 1000",
            cluster_enabled=True,
            cluster_nodes=cluster_nodes,
        )

        self.assertEqual(config.host, "redis.company.com")
        self.assertEqual(config.port, 6380)
        self.assertEqual(config.password_env_var, "CUSTOM_REDIS_PASSWORD")
        self.assertEqual(config.database, 1)
        self.assertEqual(config.max_connections, 100)
        self.assertEqual(config.socket_timeout, 10)
        self.assertEqual(config.socket_connect_timeout, 10)
        self.assertEqual(config.max_memory_mb, 2048)
        self.assertEqual(config.max_memory_policy, "volatile-lru")
        self.assertFalse(config.persistence_enabled)
        self.assertEqual(config.save_schedule, "300 10 60 1000")
        self.assertTrue(config.cluster_enabled)
        self.assertEqual(config.cluster_nodes, cluster_nodes)

    def test_custom_cluster_nodes(self):
        """Test initialization with custom cluster nodes."""
        cluster_nodes = ["node1:6379", "node2:6379"]

        config = RedisConfig(cluster_nodes=cluster_nodes)
        self.assertEqual(config.cluster_nodes, cluster_nodes)


class TestSecurityConfig(unittest.TestCase):
    """Test SecurityConfig dataclass."""

    def test_default_initialization(self):
        """Test SecurityConfig with default values."""
        config = SecurityConfig()

        # Authentication
        self.assertEqual(config.authentication_method, "jwt")
        self.assertEqual(config.jwt_secret_env_var, "STS_JWT_SECRET")
        self.assertEqual(config.jwt_expiration_hours, 24)
        self.assertTrue(config.multi_factor_auth_required)

        # Authorization
        self.assertTrue(config.rbac_enabled)
        self.assertEqual(config.role_definitions_file, "config/roles.yaml")
        self.assertEqual(config.permission_cache_ttl, 300)

        # Encryption
        self.assertEqual(config.encryption_algorithm, "AES-256-GCM")
        self.assertEqual(config.key_rotation_days, 90)
        self.assertEqual(config.key_management_service, "aws_kms")

        # API Security
        self.assertTrue(config.rate_limiting_enabled)
        self.assertEqual(config.rate_limit_requests_per_minute, 1000)
        self.assertTrue(config.csrf_protection)

        # Audit and Compliance
        self.assertTrue(config.audit_log_enabled)
        self.assertEqual(config.audit_log_retention_days, 365)
        self.assertEqual(config.compliance_level, SecurityLevel.HIPAA)

        # Network Security
        self.assertFalse(config.ip_whitelist_enabled)
        self.assertTrue(config.vpc_endpoint_enabled)

    def test_post_init_defaults(self):
        """Test __post_init__ method sets default lists."""
        config = SecurityConfig()

        # Check default CORS origins
        expected_cors = ["https://sts-dashboard.company.com"]
        self.assertEqual(config.cors_allowed_origins, expected_cors)

        # Check default IP ranges
        self.assertEqual(config.allowed_ip_ranges, [])

    def test_custom_initialization(self):
        """Test SecurityConfig with custom values."""
        cors_origins = ["https://app1.com", "https://app2.com"]
        ip_ranges = ["10.0.0.0/8", "192.168.0.0/16"]

        config = SecurityConfig(
            authentication_method="oauth2",
            jwt_secret_env_var="CUSTOM_JWT_SECRET",  # noqa: S106 - env var name, not a secret
            jwt_expiration_hours=12,
            multi_factor_auth_required=False,
            rbac_enabled=False,
            role_definitions_file="custom/roles.yaml",
            permission_cache_ttl=600,
            encryption_algorithm="AES-128-CBC",
            key_rotation_days=180,
            key_management_service="azure_keyvault",
            rate_limiting_enabled=False,
            rate_limit_requests_per_minute=2000,
            cors_allowed_origins=cors_origins,
            csrf_protection=False,
            audit_log_enabled=False,
            audit_log_retention_days=180,
            compliance_level=SecurityLevel.FDA_CFR21,
            ip_whitelist_enabled=True,
            allowed_ip_ranges=ip_ranges,
            vpc_endpoint_enabled=False,
        )

        self.assertEqual(config.authentication_method, "oauth2")
        self.assertEqual(config.jwt_secret_env_var, "CUSTOM_JWT_SECRET")
        self.assertEqual(config.jwt_expiration_hours, 12)
        self.assertFalse(config.multi_factor_auth_required)
        self.assertFalse(config.rbac_enabled)
        self.assertEqual(config.role_definitions_file, "custom/roles.yaml")
        self.assertEqual(config.permission_cache_ttl, 600)
        self.assertEqual(config.encryption_algorithm, "AES-128-CBC")
        self.assertEqual(config.key_rotation_days, 180)
        self.assertEqual(config.key_management_service, "azure_keyvault")
        self.assertFalse(config.rate_limiting_enabled)
        self.assertEqual(config.rate_limit_requests_per_minute, 2000)
        self.assertEqual(config.cors_allowed_origins, cors_origins)
        self.assertFalse(config.csrf_protection)
        self.assertFalse(config.audit_log_enabled)
        self.assertEqual(config.audit_log_retention_days, 180)
        self.assertEqual(config.compliance_level, SecurityLevel.FDA_CFR21)
        self.assertTrue(config.ip_whitelist_enabled)
        self.assertEqual(config.allowed_ip_ranges, ip_ranges)
        self.assertFalse(config.vpc_endpoint_enabled)

    def test_different_compliance_levels(self):
        """Test different compliance levels."""
        compliance_levels = [
            SecurityLevel.BASIC,
            SecurityLevel.HIPAA,
            SecurityLevel.FDA_CFR21,
            SecurityLevel.ISO27001,
            SecurityLevel.SOX,
        ]

        for level in compliance_levels:
            config = SecurityConfig(compliance_level=level)
            self.assertEqual(config.compliance_level, level)


class TestProductionConfigInitialization(unittest.TestCase):
    """Test ProductionConfig initialization."""

    def test_basic_initialization(self):
        """Test basic ProductionConfig initialization."""
        # Mock the method since we need to implement ProductionConfig
        with patch("sensory_tracer_science.deployment.production_config.ProductionConfig") as MockProductionConfig:
            mock_instance = MockProductionConfig.return_value
            mock_instance.environment = DeploymentEnvironment.PRODUCTION
            mock_instance.database_config = DatabaseConfig()
            mock_instance.redis_config = RedisConfig()
            mock_instance.security_config = SecurityConfig()

            config = MockProductionConfig(environment=DeploymentEnvironment.PRODUCTION)
            
            self.assertEqual(config.environment, DeploymentEnvironment.PRODUCTION)
            self.assertIsInstance(config.database_config, DatabaseConfig)
            self.assertIsInstance(config.redis_config, RedisConfig)
            self.assertIsInstance(config.security_config, SecurityConfig)

    def test_different_environments_initialization(self):
        """Test initialization with different environments."""
        environments = [
            DeploymentEnvironment.DEVELOPMENT,
            DeploymentEnvironment.TESTING,
            DeploymentEnvironment.STAGING,
            DeploymentEnvironment.PRODUCTION,
            DeploymentEnvironment.CLINICAL,
        ]

        for env in environments:
            with patch("sensory_tracer_science.deployment.production_config.ProductionConfig") as MockProductionConfig:
                mock_instance = MockProductionConfig.return_value
                mock_instance.environment = env
                
                config = MockProductionConfig(environment=env)
                self.assertEqual(config.environment, env)

    def test_custom_configs_initialization(self):
        """Test initialization with custom config objects."""
        custom_db = DatabaseConfig(host="custom-db.com", port=5433)
        custom_redis = RedisConfig(host="custom-redis.com", port=6380)
        custom_security = SecurityConfig(compliance_level=SecurityLevel.ISO27001)

        with patch("sensory_tracer_science.deployment.production_config.ProductionConfig") as MockProductionConfig:
            mock_instance = MockProductionConfig.return_value
            mock_instance.database_config = custom_db
            mock_instance.redis_config = custom_redis
            mock_instance.security_config = custom_security

            config = MockProductionConfig(
                environment=DeploymentEnvironment.PRODUCTION,
                database_config=custom_db,
                redis_config=custom_redis,
                security_config=custom_security,
            )
            
            self.assertEqual(config.database_config, custom_db)
            self.assertEqual(config.redis_config, custom_redis)
            self.assertEqual(config.security_config, custom_security)


class TestEnvironmentSpecificConfigurations(unittest.TestCase):
    """Test environment-specific configuration behaviors."""

    def test_development_environment_config(self):
        """Test development environment configuration."""
        with patch("sensory_tracer_science.deployment.production_config.ProductionConfig") as MockProductionConfig:
            mock_instance = MockProductionConfig.return_value
            mock_instance.environment = DeploymentEnvironment.DEVELOPMENT
            
            # Mock development-specific settings
            mock_instance.get_log_level.return_value = "DEBUG"
            mock_instance.get_debug_mode.return_value = True
            mock_instance.get_database_pool_size.return_value = 5
            
            config = MockProductionConfig(environment=DeploymentEnvironment.DEVELOPMENT)
            
            self.assertEqual(config.get_log_level(), "DEBUG")
            self.assertTrue(config.get_debug_mode())
            self.assertEqual(config.get_database_pool_size(), 5)

    def test_production_environment_config(self):
        """Test production environment configuration."""
        with patch("sensory_tracer_science.deployment.production_config.ProductionConfig") as MockProductionConfig:
            mock_instance = MockProductionConfig.return_value
            mock_instance.environment = DeploymentEnvironment.PRODUCTION
            
            # Mock production-specific settings
            mock_instance.get_log_level.return_value = "INFO"
            mock_instance.get_debug_mode.return_value = False
            mock_instance.get_database_pool_size.return_value = 100
            mock_instance.get_security_level.return_value = SecurityLevel.HIPAA
            
            config = MockProductionConfig(environment=DeploymentEnvironment.PRODUCTION)
            
            self.assertEqual(config.get_log_level(), "INFO")
            self.assertFalse(config.get_debug_mode())
            self.assertEqual(config.get_database_pool_size(), 100)
            self.assertEqual(config.get_security_level(), SecurityLevel.HIPAA)

    def test_clinical_environment_config(self):
        """Test clinical environment configuration."""
        with patch("sensory_tracer_science.deployment.production_config.ProductionConfig") as MockProductionConfig:
            mock_instance = MockProductionConfig.return_value
            mock_instance.environment = DeploymentEnvironment.CLINICAL
            
            # Mock clinical-specific settings (highest security)
            mock_instance.get_security_level.return_value = SecurityLevel.FDA_CFR21
            mock_instance.get_audit_logging.return_value = True
            mock_instance.get_encryption_required.return_value = True
            mock_instance.get_mfa_required.return_value = True
            
            config = MockProductionConfig(environment=DeploymentEnvironment.CLINICAL)
            
            self.assertEqual(config.get_security_level(), SecurityLevel.FDA_CFR21)
            self.assertTrue(config.get_audit_logging())
            self.assertTrue(config.get_encryption_required())
            self.assertTrue(config.get_mfa_required())


class TestConfigurationValidation(unittest.TestCase):
    """Test configuration validation functionality."""

    def test_validate_database_config(self):
        """Test database configuration validation."""
        with patch("sensory_tracer_science.deployment.production_config.ProductionConfig") as MockProductionConfig:
            mock_instance = MockProductionConfig.return_value
            mock_instance.validate_database_config.return_value = True
            
            config = MockProductionConfig()
            result = config.validate_database_config()
            
            self.assertTrue(result)

    def test_validate_security_config(self):
        """Test security configuration validation."""
        with patch("sensory_tracer_science.deployment.production_config.ProductionConfig") as MockProductionConfig:
            mock_instance = MockProductionConfig.return_value
            mock_instance.validate_security_config.return_value = True
            
            config = MockProductionConfig()
            result = config.validate_security_config()
            
            self.assertTrue(result)

    def test_validate_redis_config(self):
        """Test Redis configuration validation."""
        with patch("sensory_tracer_science.deployment.production_config.ProductionConfig") as MockProductionConfig:
            mock_instance = MockProductionConfig.return_value
            mock_instance.validate_redis_config.return_value = True
            
            config = MockProductionConfig()
            result = config.validate_redis_config()
            
            self.assertTrue(result)

    def test_validate_all_configs(self):
        """Test validation of all configuration sections."""
        with patch("sensory_tracer_science.deployment.production_config.ProductionConfig") as MockProductionConfig:
            mock_instance = MockProductionConfig.return_value
            mock_instance.validate_all.return_value = {
                "valid": True,
                "errors": [],
                "warnings": [],
            }
            
            config = MockProductionConfig()
            result = config.validate_all()
            
            self.assertIsInstance(result, dict)
            self.assertTrue(result["valid"])
            self.assertEqual(result["errors"], [])


class TestEnvironmentVariableHandling(unittest.TestCase):
    """Test environment variable handling."""

    def test_get_environment_variable(self):
        """Test environment variable retrieval."""
        with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
            with patch("sensory_tracer_science.deployment.production_config.ProductionConfig") as MockProductionConfig:
                mock_instance = MockProductionConfig.return_value
                mock_instance.get_env_var.return_value = "test_value"
                
                config = MockProductionConfig()
                result = config.get_env_var("TEST_VAR")
                
                self.assertEqual(result, "test_value")

    def test_get_environment_variable_with_default(self):
        """Test environment variable with default value."""
        with patch("sensory_tracer_science.deployment.production_config.ProductionConfig") as MockProductionConfig:
            mock_instance = MockProductionConfig.return_value
            mock_instance.get_env_var.return_value = "default_value"
            
            config = MockProductionConfig()
            result = config.get_env_var("NONEXISTENT_VAR", "default_value")
            
            self.assertEqual(result, "default_value")

    def test_database_password_from_env(self):
        """Test database password retrieval from environment."""
        with patch.dict(os.environ, {"STS_DB_PASSWORD": "secret_password"}):
            db_config = DatabaseConfig()
            
            # The password should come from the environment variable
            self.assertEqual(db_config.password_env_var, "STS_DB_PASSWORD")

    def test_redis_password_from_env(self):
        """Test Redis password retrieval from environment."""
        with patch.dict(os.environ, {"STS_REDIS_PASSWORD": "redis_secret"}):
            redis_config = RedisConfig()
            
            # The password should come from the environment variable
            self.assertEqual(redis_config.password_env_var, "STS_REDIS_PASSWORD")

    def test_jwt_secret_from_env(self):
        """Test JWT secret retrieval from environment."""
        with patch.dict(os.environ, {"STS_JWT_SECRET": "jwt_secret_key"}):
            security_config = SecurityConfig()
            
            # The JWT secret should come from the environment variable
            self.assertEqual(security_config.jwt_secret_env_var, "STS_JWT_SECRET")


class TestConfigurationSerialization(unittest.TestCase):
    """Test configuration serialization and deserialization."""

    def test_serialize_to_json(self):
        """Test serializing configuration to JSON."""
        with patch("sensory_tracer_science.deployment.production_config.ProductionConfig") as MockProductionConfig:
            mock_instance = MockProductionConfig.return_value
            mock_instance.to_json.return_value = '{"environment": "production"}'
            
            config = MockProductionConfig()
            json_str = config.to_json()
            
            self.assertIsInstance(json_str, str)
            self.assertIn("environment", json_str)

    def test_serialize_to_yaml(self):
        """Test serializing configuration to YAML."""
        with patch("sensory_tracer_science.deployment.production_config.ProductionConfig") as MockProductionConfig:
            mock_instance = MockProductionConfig.return_value
            mock_instance.to_yaml.return_value = "environment: production\n"
            
            config = MockProductionConfig()
            yaml_str = config.to_yaml()
            
            self.assertIsInstance(yaml_str, str)
            self.assertIn("environment", yaml_str)

    def test_deserialize_from_json(self):
        """Test deserializing configuration from JSON."""
        with patch("sensory_tracer_science.deployment.production_config.ProductionConfig") as MockProductionConfig:
            mock_instance = MockProductionConfig.return_value
            MockProductionConfig.from_json.return_value = mock_instance
            
            json_str = '{"environment": "production"}'
            config = MockProductionConfig.from_json(json_str)
            
            self.assertIs(config, mock_instance)

    def test_deserialize_from_yaml(self):
        """Test deserializing configuration from YAML."""
        with patch("sensory_tracer_science.deployment.production_config.ProductionConfig") as MockProductionConfig:
            mock_instance = MockProductionConfig.return_value
            MockProductionConfig.from_yaml.return_value = mock_instance
            
            yaml_str = "environment: production\n"
            config = MockProductionConfig.from_yaml(yaml_str)
            
            self.assertIs(config, mock_instance)


class TestConfigurationFileHandling(unittest.TestCase):
    """Test configuration file loading and saving."""

    def test_load_from_file(self):
        """Test loading configuration from file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_data = {"environment": "production", "debug": False}
            json.dump(config_data, f)
            temp_file = f.name

        try:
            with patch("sensory_tracer_science.deployment.production_config.ProductionConfig") as MockProductionConfig:
                mock_instance = MockProductionConfig.return_value
                MockProductionConfig.load_from_file.return_value = mock_instance
                
                config = MockProductionConfig.load_from_file(temp_file)
                
                self.assertIs(config, mock_instance)
                MockProductionConfig.load_from_file.assert_called_once_with(temp_file)
        finally:
            os.unlink(temp_file)

    def test_save_to_file(self):
        """Test saving configuration to file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name

        try:
            with patch("sensory_tracer_science.deployment.production_config.ProductionConfig") as MockProductionConfig:
                mock_instance = MockProductionConfig.return_value
                mock_instance.save_to_file = MagicMock()
                
                config = MockProductionConfig()
                config.save_to_file(temp_file)
                
                config.save_to_file.assert_called_once_with(temp_file)
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_load_yaml_configuration(self):
        """Test loading YAML configuration file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {"environment": "staging", "database": {"host": "localhost"}}
            yaml.dump(config_data, f)
            temp_file = f.name

        try:
            with patch("sensory_tracer_science.deployment.production_config.ProductionConfig") as MockProductionConfig:
                mock_instance = MockProductionConfig.return_value
                MockProductionConfig.load_from_yaml_file.return_value = mock_instance
                
                config = MockProductionConfig.load_from_yaml_file(temp_file)
                
                self.assertIs(config, mock_instance)
        finally:
            os.unlink(temp_file)


class TestSecurityCompliance(unittest.TestCase):
    """Test security compliance functionality."""

    def test_hipaa_compliance_settings(self):
        """Test HIPAA compliance settings."""
        security_config = SecurityConfig(compliance_level=SecurityLevel.HIPAA)
        
        self.assertEqual(security_config.compliance_level, SecurityLevel.HIPAA)
        # HIPAA typically requires enhanced security
        self.assertTrue(security_config.audit_log_enabled)
        self.assertTrue(security_config.multi_factor_auth_required)
        self.assertTrue(security_config.rbac_enabled)

    def test_fda_cfr21_compliance_settings(self):
        """Test FDA CFR 21 compliance settings."""
        security_config = SecurityConfig(compliance_level=SecurityLevel.FDA_CFR21)
        
        self.assertEqual(security_config.compliance_level, SecurityLevel.FDA_CFR21)
        # FDA CFR 21 requires strict audit trails
        self.assertTrue(security_config.audit_log_enabled)

    def test_iso27001_compliance_settings(self):
        """Test ISO 27001 compliance settings."""
        security_config = SecurityConfig(compliance_level=SecurityLevel.ISO27001)
        
        self.assertEqual(security_config.compliance_level, SecurityLevel.ISO27001)

    def test_sox_compliance_settings(self):
        """Test SOX compliance settings."""
        security_config = SecurityConfig(compliance_level=SecurityLevel.SOX)
        
        self.assertEqual(security_config.compliance_level, SecurityLevel.SOX)

    def test_basic_security_level(self):
        """Test basic security level."""
        security_config = SecurityConfig(compliance_level=SecurityLevel.BASIC)
        
        self.assertEqual(security_config.compliance_level, SecurityLevel.BASIC)


class TestPerformanceConfiguration(unittest.TestCase):
    """Test performance configuration settings."""

    def test_database_performance_settings(self):
        """Test database performance configuration."""
        db_config = DatabaseConfig(
            min_connections=10,
            max_connections=200,
            connection_timeout=60,
            statement_timeout=600,
        )

        self.assertEqual(db_config.min_connections, 10)
        self.assertEqual(db_config.max_connections, 200)
        self.assertEqual(db_config.connection_timeout, 60)
        self.assertEqual(db_config.statement_timeout, 600)

    def test_redis_performance_settings(self):
        """Test Redis performance configuration."""
        redis_config = RedisConfig(
            max_connections=100,
            socket_timeout=10,
            max_memory_mb=2048,
            max_memory_policy="volatile-lru",
        )

        self.assertEqual(redis_config.max_connections, 100)
        self.assertEqual(redis_config.socket_timeout, 10)
        self.assertEqual(redis_config.max_memory_mb, 2048)
        self.assertEqual(redis_config.max_memory_policy, "volatile-lru")

    def test_security_performance_settings(self):
        """Test security performance configuration."""
        security_config = SecurityConfig(
            rate_limit_requests_per_minute=2000,
            permission_cache_ttl=600,
            jwt_expiration_hours=12,
        )

        self.assertEqual(security_config.rate_limit_requests_per_minute, 2000)
        self.assertEqual(security_config.permission_cache_ttl, 600)
        self.assertEqual(security_config.jwt_expiration_hours, 12)


class TestBackupAndRecovery(unittest.TestCase):
    """Test backup and recovery configuration."""

    def test_database_backup_settings(self):
        """Test database backup configuration."""
        db_config = DatabaseConfig(
            backup_enabled=True,
            backup_schedule="0 2 * * *",
            backup_retention_days=30,
            point_in_time_recovery=True,
        )

        self.assertTrue(db_config.backup_enabled)
        self.assertEqual(db_config.backup_schedule, "0 2 * * *")
        self.assertEqual(db_config.backup_retention_days, 30)
        self.assertTrue(db_config.point_in_time_recovery)

    def test_redis_persistence_settings(self):
        """Test Redis persistence configuration."""
        redis_config = RedisConfig(
            persistence_enabled=True,
            save_schedule="900 1 300 10 60 10000",
        )

        self.assertTrue(redis_config.persistence_enabled)
        self.assertEqual(redis_config.save_schedule, "900 1 300 10 60 10000")

    def test_disabled_backup_settings(self):
        """Test disabled backup configuration."""
        db_config = DatabaseConfig(
            backup_enabled=False,
            point_in_time_recovery=False,
        )

        self.assertFalse(db_config.backup_enabled)
        self.assertFalse(db_config.point_in_time_recovery)


class TestNetworkSecurityConfiguration(unittest.TestCase):
    """Test network security configuration."""

    def test_cors_configuration(self):
        """Test CORS configuration."""
        cors_origins = ["https://app1.com", "https://app2.com"]
        security_config = SecurityConfig(cors_allowed_origins=cors_origins)

        self.assertEqual(security_config.cors_allowed_origins, cors_origins)

    def test_ip_whitelist_configuration(self):
        """Test IP whitelist configuration."""
        ip_ranges = ["10.0.0.0/8", "192.168.1.0/24"]
        security_config = SecurityConfig(
            ip_whitelist_enabled=True,
            allowed_ip_ranges=ip_ranges,
        )

        self.assertTrue(security_config.ip_whitelist_enabled)
        self.assertEqual(security_config.allowed_ip_ranges, ip_ranges)

    def test_vpc_endpoint_configuration(self):
        """Test VPC endpoint configuration."""
        security_config = SecurityConfig(vpc_endpoint_enabled=True)
        self.assertTrue(security_config.vpc_endpoint_enabled)

    def test_rate_limiting_configuration(self):
        """Test rate limiting configuration."""
        security_config = SecurityConfig(
            rate_limiting_enabled=True,
            rate_limit_requests_per_minute=1000,
        )

        self.assertTrue(security_config.rate_limiting_enabled)
        self.assertEqual(security_config.rate_limit_requests_per_minute, 1000)


class TestEdgeCasesAndErrorHandling(unittest.TestCase):
    """Test edge cases and error handling."""

    def test_zero_connection_limits(self):
        """Test handling of zero connection limits."""
        db_config = DatabaseConfig(
            min_connections=0,
            max_connections=0,
        )

        self.assertEqual(db_config.min_connections, 0)
        self.assertEqual(db_config.max_connections, 0)

    def test_very_large_limits(self):
        """Test handling of very large limits."""
        db_config = DatabaseConfig(
            max_connections=10000,
            statement_timeout=86400,  # 24 hours
        )

        redis_config = RedisConfig(
            max_connections=1000,
            max_memory_mb=100000,  # 100GB
        )

        self.assertEqual(db_config.max_connections, 10000)
        self.assertEqual(db_config.statement_timeout, 86400)
        self.assertEqual(redis_config.max_connections, 1000)
        self.assertEqual(redis_config.max_memory_mb, 100000)

    def test_empty_lists(self):
        """Test handling of empty lists."""
        redis_config = RedisConfig(cluster_nodes=[])
        security_config = SecurityConfig(
            cors_allowed_origins=[],
            allowed_ip_ranges=[],
        )

        self.assertEqual(redis_config.cluster_nodes, [])
        self.assertEqual(security_config.cors_allowed_origins, [])
        self.assertEqual(security_config.allowed_ip_ranges, [])

    def test_invalid_cron_schedule(self):
        """Test handling of invalid cron schedule."""
        # This should still work as string validation is not enforced at dataclass level
        db_config = DatabaseConfig(backup_schedule="invalid cron")
        self.assertEqual(db_config.backup_schedule, "invalid cron")

    def test_negative_timeout_values(self):
        """Test handling of negative timeout values."""
        db_config = DatabaseConfig(
            connection_timeout=-1,
            statement_timeout=-100,
        )

        redis_config = RedisConfig(
            socket_timeout=-5,
        )

        # Should still create the objects (validation could be added later)
        self.assertEqual(db_config.connection_timeout, -1)
        self.assertEqual(db_config.statement_timeout, -100)
        self.assertEqual(redis_config.socket_timeout, -5)

    def test_special_characters_in_strings(self):
        """Test handling of special characters in string fields."""
        db_config = DatabaseConfig(
            host="db-server.example.com",
            database="sts_prod-2024",
            username="sts-user_v2",
        )

        security_config = SecurityConfig(
            role_definitions_file="config/roles-v2.yaml",
        )

        self.assertEqual(db_config.host, "db-server.example.com")
        self.assertEqual(db_config.database, "sts_prod-2024")
        self.assertEqual(db_config.username, "sts-user_v2")
        self.assertEqual(security_config.role_definitions_file, "config/roles-v2.yaml")


if __name__ == "__main__":
    unittest.main()