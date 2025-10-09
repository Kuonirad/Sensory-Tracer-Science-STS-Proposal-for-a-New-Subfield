#!/usr/bin/env python3
"""
Comprehensive tests for STS monitoring and production configuration modules.

This test suite provides extensive coverage for:
- monitoring_analytics.py
- production_config.py

Part of achieving 100% coverage for deployment package (currently 0%).
"""

import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

# Import monitoring and production config modules
from sensory_tracer_science.deployment.monitoring_analytics import (
    AlertRule,
    MonitoringAnalytics,
    MonitoringMetric,
    NotificationChannel,
)
from sensory_tracer_science.deployment.production_config import (
    DatabaseConfig,
    ProductionConfigManager,
    RedisConfig,
    SecurityConfig,
    SystemConfig,
)


class TestMonitoringAnalyticsModule(unittest.TestCase):
    """Comprehensive tests for monitoring and analytics functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.monitoring = MonitoringAnalytics(environment="production")

        # Create test metrics and alerts
        self.test_metric = MonitoringMetric(
            name="test_cpu_usage",
            value=75.5,
            timestamp=datetime.now(),
            tags={"host": "server1", "service": "sts-api"},
        )

        self.test_alert_rule = AlertRule(
            name="high_cpu_alert",
            metric_name="cpu_usage",
            condition="greater_than",
            threshold=80.0,
            duration_seconds=300,
            notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK],
        )

    def test_notification_channel_enum(self):
        """Test NotificationChannel enum values."""
        assert NotificationChannel.EMAIL.value == "email"
        assert NotificationChannel.SLACK.value == "slack"
        assert NotificationChannel.PAGERDUTY.value == "pagerduty"
        assert NotificationChannel.SMS.value == "sms"

    def test_monitoring_metric_initialization(self):
        """Test MonitoringMetric initialization and post_init."""
        metric = MonitoringMetric(
            name="memory_usage",
            value=1024.0,
            timestamp=datetime.now(),
        )

        assert metric.name == "memory_usage"
        assert metric.value == 1024.0
        assert isinstance(metric.timestamp, datetime)
        assert metric.unit == "percent"  # Default
        assert metric.tags == {}  # Default

        # Test with custom values
        custom_tags = {"region": "us-west-2", "env": "prod"}
        custom_metric = MonitoringMetric(
            name="network_io",
            value=512.5,
            timestamp=datetime.now(),
            unit="bytes/sec",
            tags=custom_tags,
        )

        assert custom_metric.unit == "bytes/sec"
        assert custom_metric.tags == custom_tags

    def test_monitoring_metric_post_init(self):
        """Test MonitoringMetric post_init validation."""
        # Test with missing required fields
        with pytest.raises((ValueError, TypeError)):
            MonitoringMetric(name="", value=10.0, timestamp=datetime.now())

        # Test with negative values (should be allowed)
        negative_metric = MonitoringMetric(
            name="temp_change", value=-5.0, timestamp=datetime.now()
        )
        assert negative_metric.value == -5.0

    def test_alert_rule_initialization(self):
        """Test AlertRule initialization and post_init."""
        alert = AlertRule(
            name="disk_space_alert",
            metric_name="disk_usage",
            condition="greater_than",
            threshold=90.0,
            duration_seconds=600,
        )

        assert alert.name == "disk_space_alert"
        assert alert.metric_name == "disk_usage"
        assert alert.condition == "greater_than"
        assert alert.threshold == 90.0
        assert alert.duration_seconds == 600
        assert alert.notification_channels == [NotificationChannel.EMAIL]  # Default
        assert alert.enabled is True
        assert alert.alert_count == 0

    def test_alert_rule_post_init_validation(self):
        """Test AlertRule post_init validation."""
        # Test valid conditions
        valid_conditions = ["greater_than", "less_than", "equals", "not_equals"]
        for condition in valid_conditions:
            alert = AlertRule(
                name="test_alert",
                metric_name="test_metric",
                condition=condition,
                threshold=50.0,
                duration_seconds=300,
            )
            assert alert.condition == condition

        # Test invalid condition
        with pytest.raises(ValueError):
            AlertRule(
                name="bad_alert",
                metric_name="test_metric",
                condition="invalid_condition",
                threshold=50.0,
                duration_seconds=300,
            )

        # Test negative duration
        with pytest.raises(ValueError):
            AlertRule(
                name="bad_duration",
                metric_name="test_metric",
                condition="greater_than",
                threshold=50.0,
                duration_seconds=-100,
            )

    @patch("builtins.print")
    def test_monitoring_analytics_initialization(self, mock_print):
        """Test MonitoringAnalytics initialization."""
        monitoring = MonitoringAnalytics(environment="staging")

        assert monitoring.environment == "staging"
        assert isinstance(monitoring.metrics_history, list)
        assert isinstance(monitoring.active_alerts, list)
        assert monitoring.start_time is not None

        # Should initialize core metrics and alerts
        assert len(monitoring.metrics_history) > 0
        assert len(monitoring.active_alerts) > 0

    def test_record_metric_basic(self):
        """Test basic metric recording."""
        initial_count = len(self.monitoring.metrics_history)

        self.monitoring.record_metric(
            name="api_response_time",
            value=150.5,
            unit="ms",
            tags={"endpoint": "/api/tracers", "method": "GET"},
        )

        assert len(self.monitoring.metrics_history) == initial_count + 1

        # Check the recorded metric
        recorded_metric = self.monitoring.metrics_history[-1]
        assert recorded_metric.name == "api_response_time"
        assert recorded_metric.value == 150.5
        assert recorded_metric.unit == "ms"
        assert recorded_metric.tags["endpoint"] == "/api/tracers"

    def test_increment_counter_basic(self):
        """Test counter increment functionality."""
        counter_name = "api_requests_total"

        # Increment counter multiple times
        self.monitoring.increment_counter(counter_name)
        self.monitoring.increment_counter(counter_name)
        self.monitoring.increment_counter(counter_name, increment=3)

        # Find the counter metrics
        counter_metrics = [
            m for m in self.monitoring.metrics_history if m.name == counter_name
        ]

        assert len(counter_metrics) >= 3
        # Values should be cumulative
        values = [m.value for m in counter_metrics]
        assert 1.0 in values  # First increment
        assert 2.0 in values  # Second increment
        assert 5.0 in values  # Third increment (+3)

    def test_increment_counter_with_tags(self):
        """Test counter increment with tags."""
        counter_name = "http_requests"
        tags = {"status_code": "200", "method": "POST"}

        self.monitoring.increment_counter(counter_name, tags=tags, increment=2)

        # Find the specific counter
        counter_metrics = [
            m
            for m in self.monitoring.metrics_history
            if m.name == counter_name and m.tags == tags
        ]

        assert len(counter_metrics) >= 1
        assert counter_metrics[-1].value == 2.0
        assert counter_metrics[-1].tags == tags

    @patch("sensory_tracer_science.deployment.monitoring_analytics.MonitoringAnalytics._send_alert_notifications")
    def test_check_alert_conditions_triggered(self, mock_send_notifications):
        """Test alert condition checking when threshold is exceeded."""
        # Create a metric that exceeds the alert threshold
        high_cpu_metric = MonitoringMetric(
            name="cpu_usage",
            value=85.0,  # Exceeds 80.0 threshold
            timestamp=datetime.now(),
            tags={"host": "server1"},
        )

        # Add alert rule to monitoring
        self.monitoring.active_alerts.append(self.test_alert_rule)

        # Check alert conditions
        self.monitoring._check_alert_conditions(high_cpu_metric)

        # Alert should be triggered
        mock_send_notifications.assert_called()

    def test_check_alert_conditions_not_triggered(self):
        """Test alert condition checking when threshold is not exceeded."""
        # Create a metric below the threshold
        normal_cpu_metric = MonitoringMetric(
            name="cpu_usage",
            value=75.0,  # Below 80.0 threshold
            timestamp=datetime.now(),
            tags={"host": "server1"},
        )

        # Add alert rule to monitoring
        self.monitoring.active_alerts.append(self.test_alert_rule)

        # Should not trigger any alerts (no exceptions should be raised)
        self.monitoring._check_alert_conditions(normal_cpu_metric)

    @patch("sensory_tracer_science.deployment.monitoring_analytics.MonitoringAnalytics._send_email_notification")
    @patch("sensory_tracer_science.deployment.monitoring_analytics.MonitoringAnalytics._send_slack_notification")
    def test_trigger_alert(self, mock_slack, mock_email):
        """Test alert triggering with notifications."""
        trigger_metric = MonitoringMetric(
            name="cpu_usage",
            value=95.0,
            timestamp=datetime.now(),
            tags={"host": "critical-server"},
        )

        self.monitoring._trigger_alert(self.test_alert_rule, trigger_metric)

        # Should increment alert count
        assert self.test_alert_rule.alert_count > 0

    def test_generate_performance_report_basic(self):
        """Test performance report generation."""
        # Add some test metrics
        self.monitoring.record_metric("cpu_usage", 78.5)
        self.monitoring.record_metric("memory_usage", 65.2)
        self.monitoring.record_metric("response_time", 250.0, unit="ms")

        report = self.monitoring.generate_performance_report(hours=24)

        assert isinstance(report, dict)
        assert "report_period" in report
        assert "system_metrics" in report
        assert "performance_summary" in report
        assert "recommendations" in report

        # Check system metrics
        system_metrics = report["system_metrics"]
        assert "avg_cpu_usage" in system_metrics
        assert "avg_memory_usage" in system_metrics
        assert "avg_response_time" in system_metrics

        # Check performance summary
        performance_summary = report["performance_summary"]
        assert "total_metrics_collected" in performance_summary
        assert "active_alerts" in performance_summary

    def test_generate_compliance_report(self):
        """Test compliance report generation."""
        report = self.monitoring.generate_compliance_report()

        assert isinstance(report, dict)
        assert "compliance_status" in report
        assert "security_metrics" in report
        assert "availability_metrics" in report
        assert "data_protection" in report

        # Check compliance status
        compliance_status = report["compliance_status"]
        assert "overall_score" in compliance_status
        assert isinstance(compliance_status["overall_score"], (int, float))
        assert 0 <= compliance_status["overall_score"] <= 100

    def test_get_system_health_status(self):
        """Test system health status generation."""
        # Add some metrics to calculate health
        self.monitoring.record_metric("cpu_usage", 45.0)
        self.monitoring.record_metric("memory_usage", 60.0)
        self.monitoring.record_metric("disk_usage", 70.0)

        health_status = self.monitoring.get_system_health_status()

        assert isinstance(health_status, dict)
        assert "overall_health" in health_status
        assert "component_health" in health_status
        assert "alerts_summary" in health_status
        assert "uptime_seconds" in health_status

        # Check overall health
        overall_health = health_status["overall_health"]
        assert overall_health in ["healthy", "warning", "critical"]

        # Check component health
        component_health = health_status["component_health"]
        assert isinstance(component_health, dict)

    def test_export_metrics_prometheus_format(self):
        """Test Prometheus format export."""
        # Add some metrics
        self.monitoring.record_metric("http_requests_total", 150.0, tags={"method": "GET"})
        self.monitoring.record_metric("cpu_usage_percent", 78.5)

        prometheus_export = self.monitoring.export_metrics(format="prometheus")

        assert isinstance(prometheus_export, str)
        assert "# HELP" in prometheus_export
        assert "# TYPE" in prometheus_export
        assert "http_requests_total" in prometheus_export
        assert "cpu_usage_percent" in prometheus_export

    def test_export_metrics_json_format(self):
        """Test JSON format export."""
        # Add some metrics
        self.monitoring.record_metric("memory_usage", 1024.0, unit="MB")

        json_export = self.monitoring.export_metrics(format="json")

        assert isinstance(json_export, str)

        # Should be valid JSON
        parsed_json = json.loads(json_export)
        assert isinstance(parsed_json, dict)
        assert "metrics" in parsed_json
        assert "export_timestamp" in parsed_json

    def test_send_notification_methods(self):
        """Test notification sending methods (mocked)."""
        alert_data = {
            "alert_name": "test_alert",
            "metric_value": 95.0,
            "threshold": 80.0,
            "timestamp": datetime.now().isoformat(),
        }

        # Test individual notification methods
        self.monitoring._send_email_notification(alert_data)
        self.monitoring._send_slack_notification(alert_data)
        self.monitoring._send_pagerduty_notification(alert_data)
        self.monitoring._send_sms_notification(alert_data)

        # These are placeholder methods, so they should execute without error


class TestProductionConfigModule(unittest.TestCase):
    """Comprehensive tests for production configuration management."""

    def setUp(self):
        """Set up test fixtures."""
        self.system_config = SystemConfig(
            app_name="sts-framework",
            debug=False,
            log_level="INFO",
        )

        self.database_config = DatabaseConfig(
            host="localhost",
            port=5432,
            name="sts_production",
            username="sts_user",
            password="secure_password",
        )

        self.redis_config = RedisConfig(
            host="localhost",
            port=6379,
            database=0,
        )

        self.security_config = SecurityConfig(
            secret_key="super_secret_key_123",
            allowed_hosts=["localhost", "sts.example.com"],
            cors_origins=["https://frontend.example.com"],
        )

        self.config_manager = ProductionConfigManager(
            environment="production",
            system_config=self.system_config,
            database_config=self.database_config,
            redis_config=self.redis_config,
            security_config=self.security_config,
        )

    def test_system_config_initialization(self):
        """Test SystemConfig initialization and post_init."""
        config = SystemConfig(
            app_name="test-app",
            debug=True,
            log_level="DEBUG",
        )

        assert config.app_name == "test-app"
        assert config.debug is True
        assert config.log_level == "DEBUG"
        assert config.port == 8080  # Default
        assert config.workers == 4  # Default

        # Test post_init
        assert config.app_version is not None
        assert config.build_timestamp is not None

    def test_system_config_post_init_validation(self):
        """Test SystemConfig post_init validation."""
        # Test invalid log level
        with pytest.raises(ValueError):
            SystemConfig(
                app_name="test-app",
                debug=False,
                log_level="INVALID_LEVEL",
            )

        # Test invalid port ranges
        with pytest.raises(ValueError):
            SystemConfig(
                app_name="test-app",
                debug=False,
                log_level="INFO",
                port=70000,  # Above valid range
            )

        with pytest.raises(ValueError):
            SystemConfig(
                app_name="test-app",
                debug=False,
                log_level="INFO",
                port=500,  # Below valid range
            )

    def test_database_config_initialization(self):
        """Test DatabaseConfig initialization and post_init."""
        config = DatabaseConfig(
            host="db.example.com",
            port=3306,
            name="mysql_db",
            username="admin",
            password="admin_pass",
            engine="mysql",
        )

        assert config.host == "db.example.com"
        assert config.port == 3306
        assert config.name == "mysql_db"
        assert config.username == "admin"
        assert config.password == "admin_pass"
        assert config.engine == "mysql"

        # Check post_init defaults
        assert config.max_connections >= 10
        assert config.ssl_enabled is True

    def test_database_config_post_init_validation(self):
        """Test DatabaseConfig post_init validation."""
        # Test invalid engine
        with pytest.raises(ValueError):
            DatabaseConfig(
                host="localhost",
                port=5432,
                name="test_db",
                username="user",
                password="pass",
                engine="invalid_engine",
            )

        # Test invalid port
        with pytest.raises(ValueError):
            DatabaseConfig(
                host="localhost",
                port=100000,  # Invalid port
                name="test_db",
                username="user",
                password="pass",
            )

    def test_redis_config_initialization(self):
        """Test RedisConfig initialization and post_init."""
        config = RedisConfig(
            host="redis.example.com",
            port=6380,
            database=5,
            password="redis_pass",
        )

        assert config.host == "redis.example.com"
        assert config.port == 6380
        assert config.database == 5
        assert config.password == "redis_pass"
        assert config.ssl_enabled is False  # Default

        # Check post_init
        assert config.max_connections > 0

    def test_redis_config_post_init_validation(self):
        """Test RedisConfig post_init validation."""
        # Test invalid database number
        with pytest.raises(ValueError):
            RedisConfig(
                host="localhost",
                port=6379,
                database=20,  # Above valid range (0-15)
            )

        with pytest.raises(ValueError):
            RedisConfig(
                host="localhost",
                port=6379,
                database=-1,  # Below valid range
            )

    def test_security_config_initialization(self):
        """Test SecurityConfig initialization and post_init."""
        config = SecurityConfig(
            secret_key="my_secret_key",
            allowed_hosts=["example.com", "api.example.com"],
            cors_origins=["https://app.example.com"],
            jwt_algorithm="HS512",
        )

        assert config.secret_key == "my_secret_key"
        assert config.allowed_hosts == ["example.com", "api.example.com"]
        assert config.cors_origins == ["https://app.example.com"]
        assert config.jwt_algorithm == "HS512"

        # Check post_init defaults
        assert config.session_timeout > 0
        assert config.max_login_attempts > 0

    def test_security_config_post_init_validation(self):
        """Test SecurityConfig post_init validation."""
        # Test short secret key
        with pytest.raises(ValueError):
            SecurityConfig(
                secret_key="short",  # Less than 32 characters
                allowed_hosts=["localhost"],
            )

        # Test invalid JWT algorithm
        with pytest.raises(ValueError):
            SecurityConfig(
                secret_key="a" * 32,
                allowed_hosts=["localhost"],
                jwt_algorithm="INVALID_ALGO",
            )

    @patch("builtins.print")
    def test_production_config_manager_initialization(self, mock_print):
        """Test ProductionConfigManager initialization."""
        manager = ProductionConfigManager(
            environment="staging",
            system_config=self.system_config,
            database_config=self.database_config,
        )

        assert manager.environment == "staging"
        assert manager.system_config == self.system_config
        assert manager.database_config == self.database_config

    def test_get_database_url(self):
        """Test database URL generation."""
        db_url = self.config_manager.get_database_url()

        assert isinstance(db_url, str)
        assert "postgresql://" in db_url
        assert "sts_user" in db_url
        assert "localhost" in db_url
        assert "5432" in db_url
        assert "sts_production" in db_url

        # Password should not be in plain text (masked)
        assert "secure_password" not in db_url or "***" in db_url

    def test_get_redis_url(self):
        """Test Redis URL generation."""
        redis_url = self.config_manager.get_redis_url()

        assert isinstance(redis_url, str)
        assert "redis://" in redis_url
        assert "localhost" in redis_url
        assert "6379" in redis_url

    def test_get_security_settings(self):
        """Test security settings retrieval."""
        security_settings = self.config_manager.get_security_settings()

        assert isinstance(security_settings, dict)
        assert "jwt_algorithm" in security_settings
        assert "session_timeout" in security_settings
        assert "cors_origins" in security_settings
        assert "allowed_hosts" in security_settings

        # Secret key should be masked
        assert "secret_key" in security_settings
        assert security_settings["secret_key"] == "***"

    def test_export_config(self):
        """Test configuration export to file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            self.config_manager.export_config(temp_path)

            # Check that file was created and contains valid JSON
            with open(temp_path, "r") as f:
                config_data = json.load(f)

            assert isinstance(config_data, dict)
            assert "environment" in config_data
            assert "system_config" in config_data
            assert "database_config" in config_data

        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_generate_docker_env(self):
        """Test Docker environment variables generation."""
        docker_env = self.config_manager.generate_docker_env()

        assert isinstance(docker_env, dict)

        # Check expected environment variables
        assert "APP_NAME" in docker_env
        assert "DATABASE_URL" in docker_env
        assert "REDIS_URL" in docker_env
        assert "LOG_LEVEL" in docker_env
        assert "ENVIRONMENT" in docker_env

        # Check values
        assert docker_env["APP_NAME"] == self.system_config.app_name
        assert docker_env["LOG_LEVEL"] == self.system_config.log_level
        assert docker_env["ENVIRONMENT"] == "production"

    def test_generate_kubernetes_configmap(self):
        """Test Kubernetes ConfigMap generation."""
        configmap = self.config_manager.generate_kubernetes_configmap()

        assert isinstance(configmap, dict)
        assert configmap["apiVersion"] == "v1"
        assert configmap["kind"] == "ConfigMap"

        # Check metadata
        metadata = configmap["metadata"]
        assert metadata["name"] == "sts-config"

        # Check data
        data = configmap["data"]
        assert "app.properties" in data
        assert isinstance(data["app.properties"], str)

    @patch.dict("os.environ", {"STS_DEBUG": "true", "STS_LOG_LEVEL": "DEBUG"})
    def test_apply_environment_overrides(self):
        """Test environment variable overrides."""
        manager = ProductionConfigManager(
            environment="development",
            system_config=SystemConfig(
                app_name="test-app", debug=False, log_level="INFO"
            ),
        )

        # Environment overrides should be applied
        assert manager.system_config.debug is True
        assert manager.system_config.log_level == "DEBUG"

    def test_load_custom_configurations(self):
        """Test loading custom configurations from file."""
        custom_config = {
            "system_config": {"workers": 8, "port": 9000},
            "database_config": {"max_connections": 50},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as temp_file:
            json.dump(custom_config, temp_file)
            temp_path = temp_file.name

        try:
            manager = ProductionConfigManager(
                environment="production",
                system_config=self.system_config,
                database_config=self.database_config,
                config_file=temp_path,
            )

            # Custom configurations should be applied
            assert manager.system_config.workers == 8
            assert manager.system_config.port == 9000
            assert manager.database_config.max_connections == 50

        finally:
            Path(temp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()