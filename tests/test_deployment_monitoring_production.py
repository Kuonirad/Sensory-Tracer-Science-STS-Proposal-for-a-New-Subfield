#!/usr/bin/env python3
"""
Tests for the STS production configuration module (and its interaction
with the monitoring system).

These tests exercise the real public API of
``sensory_tracer_science.deployment.production_config``: the component
config dataclasses and the ``ProductionConfig`` manager with its
environment-specific overrides, connection URLs, security settings and
deployment artifact generation.
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from sensory_tracer_science.deployment.monitoring_analytics import MonitoringSystem
from sensory_tracer_science.deployment.production_config import (
    DatabaseConfig,
    DeploymentEnvironment,
    ProductionConfig,
    RedisConfig,
    SecurityConfig,
    SecurityLevel,
    SystemConfig,
)


def make_config(environment=DeploymentEnvironment.PRODUCTION):
    with patch("builtins.print"):
        return ProductionConfig(environment=environment)


class TestComponentConfigDefaults:
    def test_database_defaults(self):
        db = DatabaseConfig()
        assert db.host == "localhost"
        assert db.port == 5432
        assert db.database == "sts_production"
        assert db.ssl_enabled is True

    def test_redis_defaults_and_post_init(self):
        redis = RedisConfig()
        assert redis.port == 6379
        # cluster_nodes defaults to an empty list via __post_init__
        assert redis.cluster_nodes == []

    def test_security_defaults(self):
        sec = SecurityConfig()
        assert sec.authentication_method == "jwt"
        assert sec.compliance_level is SecurityLevel.HIPAA
        # list fields populated by __post_init__
        assert isinstance(sec.cors_allowed_origins, list)
        assert isinstance(sec.allowed_ip_ranges, list)


class TestSecurityLevelEnum:
    def test_values(self):
        assert SecurityLevel.BASIC.value == "basic"
        assert SecurityLevel.HIPAA.value == "hipaa"
        assert SecurityLevel.FDA_CFR21.value == "fda_cfr21"


class TestProductionConfigEnvironmentOverrides:
    def test_development_overrides(self):
        config = make_config(DeploymentEnvironment.DEVELOPMENT)
        assert config.database.host == "localhost"
        assert config.database.backup_enabled is False
        assert config.security.compliance_level is SecurityLevel.BASIC
        assert config.monitoring.log_level == "DEBUG"

    def test_production_overrides(self):
        config = make_config(DeploymentEnvironment.PRODUCTION)
        assert config.database.host == "prod-db.internal"
        assert config.database.backup_enabled is True
        assert config.security.compliance_level is SecurityLevel.HIPAA
        assert config.scaling.max_replicas == 100

    def test_clinical_overrides(self):
        config = make_config(DeploymentEnvironment.CLINICAL)
        assert config.database.host == "clinical-db.internal"
        assert config.security.compliance_level is SecurityLevel.FDA_CFR21
        assert config.security.multi_factor_auth_required is True


class TestProductionConfigConnectionStrings:
    def test_database_url_requires_password(self):
        config = make_config()
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop(config.database.password_env_var, None)
            with pytest.raises(ValueError, match="Database password not found"):
                config.get_database_url()

    def test_database_url_with_password(self):
        config = make_config()
        with patch.dict(os.environ, {config.database.password_env_var: "secret"}):
            url = config.get_database_url()
        assert url.startswith("postgresql://")
        assert "secret" in url
        assert str(config.database.port) in url

    def test_redis_url(self):
        config = make_config()
        url = config.get_redis_url()
        assert url.startswith("redis://")
        assert str(config.redis.port) in url

    def test_security_settings_requires_jwt_secret(self):
        config = make_config()
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop(config.security.jwt_secret_env_var, None)
            with pytest.raises(ValueError, match="JWT secret not found"):
                config.get_security_settings()

    def test_security_settings_with_secret(self):
        config = make_config()
        with patch.dict(os.environ, {config.security.jwt_secret_env_var: "jwt-token"}):
            settings = config.get_security_settings()
        assert settings["jwt_secret"] == "jwt-token"
        assert settings["compliance_level"] == config.security.compliance_level.value


class TestProductionConfigArtifacts:
    def test_export_config_json(self):
        config = make_config()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "config.json"
            with patch("builtins.print"):
                config.export_config(str(out))
            data = json.loads(out.read_text())
        assert data["environment"] == "production"
        assert "database" in data and "security" in data

    def test_export_config_yaml(self):
        config = make_config()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "config.yaml"
            with patch("builtins.print"):
                config.export_config(str(out))
            data = yaml.safe_load(out.read_text())
        assert data["environment"] == "production"

    def test_generate_docker_env(self):
        config = make_config()
        env = config.generate_docker_env()
        assert isinstance(env, dict)
        assert env.get("STS_ENVIRONMENT") == "production"

    def test_generate_kubernetes_configmap(self):
        config = make_config()
        configmap = config.generate_kubernetes_configmap()
        assert configmap["kind"] == "ConfigMap"

    def test_generate_deployment_summary(self):
        config = make_config()
        summary = config.generate_deployment_summary()
        assert isinstance(summary, str)
        assert "production" in summary.lower()


class TestSystemConfigDataclass:
    def test_system_config_instantiable(self):
        system = SystemConfig()
        assert system is not None


class TestMonitoringProductionIntegration:
    def test_monitoring_system_runs_in_production_environment(self):
        config = make_config(DeploymentEnvironment.PRODUCTION)
        with patch("builtins.print"):
            monitoring = MonitoringSystem(environment=config.environment.value)
            monitoring.record_metric("sts_error_rate", 0.5)
        health = monitoring.get_system_health_status()
        assert health["environment"] == "production"
