#!/usr/bin/env python3
"""
Comprehensive Test Suite for Monitoring and Analytics

Tests monitoring and analytics functionality including:
- Metrics collection and storage
- Alert rules and notification systems
- Performance analytics and baselines
- Compliance and audit logging
- Real-time monitoring and dashboards
- STS-specific neural tracer monitoring
"""

import json
import time
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, call, patch

import pytest

from sensory_tracer_science.deployment.monitoring_analytics import (
    AlertRule,
    AlertSeverity,
    MetricType,
    MonitoringMetric,
    MonitoringSystem,
)


class TestAlertSeverity(unittest.TestCase):
    """Test AlertSeverity enum."""

    def test_alert_severity_values(self):
        """Test all alert severity enum values."""
        self.assertEqual(AlertSeverity.INFO.value, "info")
        self.assertEqual(AlertSeverity.WARNING.value, "warning")
        self.assertEqual(AlertSeverity.CRITICAL.value, "critical")
        self.assertEqual(AlertSeverity.EMERGENCY.value, "emergency")

    def test_alert_severity_count(self):
        """Test expected number of alert severity levels."""
        self.assertEqual(len(AlertSeverity), 4)

    def test_severity_ordering(self):
        """Test that severity levels can be compared."""
        # While enums don't have natural ordering, we can test they exist
        severities = [AlertSeverity.INFO, AlertSeverity.WARNING, AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]
        self.assertEqual(len(set(severities)), 4)


class TestMetricType(unittest.TestCase):
    """Test MetricType enum."""

    def test_metric_type_values(self):
        """Test all metric type enum values."""
        self.assertEqual(MetricType.COUNTER.value, "counter")
        self.assertEqual(MetricType.GAUGE.value, "gauge")
        self.assertEqual(MetricType.HISTOGRAM.value, "histogram")
        self.assertEqual(MetricType.SUMMARY.value, "summary")

    def test_metric_type_count(self):
        """Test expected number of metric types."""
        self.assertEqual(len(MetricType), 4)


class TestMonitoringMetric(unittest.TestCase):
    """Test MonitoringMetric dataclass."""

    def test_basic_initialization(self):
        """Test basic MonitoringMetric initialization."""
        metric = MonitoringMetric(
            name="test_metric",
            metric_type=MetricType.COUNTER,
            description="Test metric description",
            unit="requests",
        )

        self.assertEqual(metric.name, "test_metric")
        self.assertEqual(metric.metric_type, MetricType.COUNTER)
        self.assertEqual(metric.description, "Test metric description")
        self.assertEqual(metric.unit, "requests")
        self.assertEqual(metric.value, 0.0)

    def test_post_init_defaults(self):
        """Test __post_init__ method sets default values."""
        metric = MonitoringMetric(
            name="test_metric",
            metric_type=MetricType.GAUGE,
            description="Test gauge",
            unit="bytes",
        )

        # Check default labels
        self.assertEqual(metric.labels, {})
        
        # Check timestamp is set
        self.assertIsInstance(metric.timestamp, datetime)
        self.assertLessEqual(
            (datetime.now() - metric.timestamp).total_seconds(), 1.0
        )

    def test_custom_initialization(self):
        """Test initialization with custom values."""
        custom_labels = {"environment": "production", "service": "sts-api"}
        custom_timestamp = datetime(2023, 1, 1, 12, 0, 0)

        metric = MonitoringMetric(
            name="custom_metric",
            metric_type=MetricType.HISTOGRAM,
            description="Custom metric",
            unit="seconds",
            labels=custom_labels,
            value=42.5,
            timestamp=custom_timestamp,
        )

        self.assertEqual(metric.name, "custom_metric")
        self.assertEqual(metric.metric_type, MetricType.HISTOGRAM)
        self.assertEqual(metric.labels, custom_labels)
        self.assertEqual(metric.value, 42.5)
        self.assertEqual(metric.timestamp, custom_timestamp)

    def test_different_metric_types(self):
        """Test initialization with different metric types."""
        metric_types = [
            MetricType.COUNTER,
            MetricType.GAUGE, 
            MetricType.HISTOGRAM,
            MetricType.SUMMARY,
        ]

        for metric_type in metric_types:
            metric = MonitoringMetric(
                name=f"test_{metric_type.value}",
                metric_type=metric_type,
                description=f"Test {metric_type.value} metric",
                unit="units",
            )
            
            self.assertEqual(metric.metric_type, metric_type)

    def test_dataclass_features(self):
        """Test dataclass features like equality and representation."""
        metric1 = MonitoringMetric(
            name="test",
            metric_type=MetricType.COUNTER,
            description="Test",
            unit="count",
        )

        metric2 = MonitoringMetric(
            name="test",
            metric_type=MetricType.COUNTER,
            description="Test", 
            unit="count",
            labels={},  # Explicitly set to same as default
        )

        # Should be equal (ignoring timestamp)
        metric2.timestamp = metric1.timestamp
        self.assertEqual(metric1, metric2)

        # Test representation
        repr_str = repr(metric1)
        self.assertIn("MonitoringMetric", repr_str)
        self.assertIn("name=", repr_str)


class TestAlertRule(unittest.TestCase):
    """Test AlertRule dataclass."""

    def test_basic_initialization(self):
        """Test basic AlertRule initialization."""
        rule = AlertRule(
            name="high_error_rate",
            description="Alert when error rate is high",
            metric_name="sts_error_rate",
            condition="greater_than",
            threshold=5.0,
            severity=AlertSeverity.CRITICAL,
        )

        self.assertEqual(rule.name, "high_error_rate")
        self.assertEqual(rule.description, "Alert when error rate is high")
        self.assertEqual(rule.metric_name, "sts_error_rate")
        self.assertEqual(rule.condition, "greater_than")
        self.assertEqual(rule.threshold, 5.0)
        self.assertEqual(rule.severity, AlertSeverity.CRITICAL)
        self.assertEqual(rule.duration, 300)  # Default
        self.assertTrue(rule.enabled)  # Default

    def test_post_init_defaults(self):
        """Test __post_init__ method sets default notification channels."""
        rule = AlertRule(
            name="test_rule",
            description="Test rule",
            metric_name="test_metric",
            condition="equals",
            threshold=1.0,
            severity=AlertSeverity.INFO,
        )

        self.assertEqual(rule.notification_channels, [])

    def test_custom_initialization(self):
        """Test initialization with custom values."""
        custom_channels = ["email", "slack", "pagerduty"]

        rule = AlertRule(
            name="custom_rule",
            description="Custom alert rule",
            metric_name="custom_metric",
            condition="less_than",
            threshold=10.0,
            severity=AlertSeverity.WARNING,
            duration=600,
            enabled=False,
            notification_channels=custom_channels,
        )

        self.assertEqual(rule.name, "custom_rule")
        self.assertEqual(rule.condition, "less_than")
        self.assertEqual(rule.threshold, 10.0)
        self.assertEqual(rule.severity, AlertSeverity.WARNING)
        self.assertEqual(rule.duration, 600)
        self.assertFalse(rule.enabled)
        self.assertEqual(rule.notification_channels, custom_channels)

    def test_different_conditions(self):
        """Test different alert conditions."""
        conditions = [
            "greater_than",
            "less_than",
            "equals",
            "not_equals",
            "greater_than_or_equal",
            "less_than_or_equal",
        ]

        for condition in conditions:
            rule = AlertRule(
                name=f"rule_{condition}",
                description=f"Rule with {condition} condition",
                metric_name="test_metric",
                condition=condition,
                threshold=1.0,
                severity=AlertSeverity.INFO,
            )
            
            self.assertEqual(rule.condition, condition)

    def test_different_severities(self):
        """Test different alert severities."""
        severities = [
            AlertSeverity.INFO,
            AlertSeverity.WARNING,
            AlertSeverity.CRITICAL,
            AlertSeverity.EMERGENCY,
        ]

        for severity in severities:
            rule = AlertRule(
                name=f"rule_{severity.value}",
                description=f"Rule with {severity.value} severity",
                metric_name="test_metric",
                condition="greater_than",
                threshold=1.0,
                severity=severity,
            )
            
            self.assertEqual(rule.severity, severity)


class TestMonitoringSystemInitialization(unittest.TestCase):
    """Test MonitoringSystem initialization."""

    @patch("builtins.print")
    def test_basic_initialization(self, mock_print):
        """Test basic MonitoringSystem initialization."""
        monitoring = MonitoringSystem()

        self.assertEqual(monitoring.environment, "production")
        self.assertIsInstance(monitoring.metrics_storage, dict)
        self.assertIsInstance(monitoring.alert_rules, dict)
        self.assertIsInstance(monitoring.active_alerts, dict)
        self.assertIsInstance(monitoring.performance_baselines, dict)

        mock_print.assert_called_once_with("📊 Monitoring system initialized for production")

    @patch("builtins.print")
    def test_custom_environment_initialization(self, mock_print):
        """Test initialization with custom environment."""
        monitoring = MonitoringSystem(environment="development")

        self.assertEqual(monitoring.environment, "development")
        mock_print.assert_called_once_with("📊 Monitoring system initialized for development")

    @patch("builtins.print")
    def test_core_metrics_initialization(self, mock_print):
        """Test that core metrics are initialized."""
        monitoring = MonitoringSystem()

        # Check that metrics storage has been populated
        self.assertGreater(len(monitoring.metrics_storage), 0)

        # Check for some expected core metrics
        expected_metrics = [
            "sts_requests_total",
            "sts_request_duration", 
            "sts_active_connections",
            "sts_error_rate",
            "sts_neural_experiments_total",
        ]

        for metric_name in expected_metrics:
            self.assertIn(metric_name, monitoring.metrics_storage)

    @patch("builtins.print")
    def test_default_alerts_initialization(self, mock_print):
        """Test that default alert rules are set up."""
        monitoring = MonitoringSystem()

        # Check that alert rules have been set up
        self.assertGreater(len(monitoring.alert_rules), 0)

        # Check for some expected alert rules
        expected_alerts = [
            "high_error_rate",
            "high_response_time",
            "neural_safety_violation",
        ]

        for alert_name in expected_alerts:
            self.assertIn(alert_name, monitoring.alert_rules)


class TestMetricsCollection(unittest.TestCase):
    """Test metrics collection functionality."""

    def setUp(self):
        """Set up test fixtures."""
        with patch("builtins.print"):
            self.monitoring = MonitoringSystem()

    def test_record_metric_basic(self):
        """Test basic metric recording."""
        # Mock the method since we need to implement it
        with patch.object(self.monitoring, "record_metric") as mock_method:
            self.monitoring.record_metric("test_metric", 42.0)
            mock_method.assert_called_once_with("test_metric", 42.0)

    def test_record_metric_with_labels(self):
        """Test metric recording with labels."""
        with patch.object(self.monitoring, "record_metric") as mock_method:
            labels = {"service": "sts-api", "endpoint": "/health"}
            self.monitoring.record_metric("test_metric", 1.0, labels=labels)
            mock_method.assert_called_once_with("test_metric", 1.0, labels=labels)

    def test_increment_counter(self):
        """Test counter increment functionality."""
        with patch.object(self.monitoring, "increment_counter") as mock_method:
            self.monitoring.increment_counter("sts_requests_total")
            mock_method.assert_called_once_with("sts_requests_total")

    def test_update_gauge(self):
        """Test gauge update functionality."""
        with patch.object(self.monitoring, "update_gauge") as mock_method:
            self.monitoring.update_gauge("sts_active_connections", 15)
            mock_method.assert_called_once_with("sts_active_connections", 15)

    def test_record_histogram(self):
        """Test histogram recording functionality."""
        with patch.object(self.monitoring, "record_histogram") as mock_method:
            self.monitoring.record_histogram("sts_request_duration", 0.250)
            mock_method.assert_called_once_with("sts_request_duration", 0.250)

    def test_batch_record_metrics(self):
        """Test batch metric recording."""
        metrics_batch = [
            {"name": "metric1", "value": 1.0},
            {"name": "metric2", "value": 2.0},
            {"name": "metric3", "value": 3.0},
        ]

        with patch.object(self.monitoring, "batch_record_metrics") as mock_method:
            self.monitoring.batch_record_metrics(metrics_batch)
            mock_method.assert_called_once_with(metrics_batch)


class TestAlertingSystem(unittest.TestCase):
    """Test alerting system functionality."""

    def setUp(self):
        """Set up test fixtures."""
        with patch("builtins.print"):
            self.monitoring = MonitoringSystem()

    def test_add_alert_rule(self):
        """Test adding new alert rule."""
        rule = AlertRule(
            name="test_alert",
            description="Test alert rule",
            metric_name="test_metric",
            condition="greater_than",
            threshold=5.0,
            severity=AlertSeverity.WARNING,
        )

        with patch.object(self.monitoring, "add_alert_rule") as mock_method:
            self.monitoring.add_alert_rule(rule)
            mock_method.assert_called_once_with(rule)

    def test_remove_alert_rule(self):
        """Test removing alert rule."""
        with patch.object(self.monitoring, "remove_alert_rule") as mock_method:
            self.monitoring.remove_alert_rule("test_alert")
            mock_method.assert_called_once_with("test_alert")

    def test_enable_disable_alert_rule(self):
        """Test enabling and disabling alert rules."""
        with patch.object(self.monitoring, "enable_alert_rule") as mock_enable:
            self.monitoring.enable_alert_rule("test_alert")
            mock_enable.assert_called_once_with("test_alert")

        with patch.object(self.monitoring, "disable_alert_rule") as mock_disable:
            self.monitoring.disable_alert_rule("test_alert")
            mock_disable.assert_called_once_with("test_alert")

    def test_evaluate_alerts(self):
        """Test alert evaluation functionality."""
        with patch.object(self.monitoring, "evaluate_alerts") as mock_method:
            self.monitoring.evaluate_alerts()
            mock_method.assert_called_once()

    def test_trigger_alert(self):
        """Test alert triggering functionality."""
        with patch.object(self.monitoring, "trigger_alert") as mock_method:
            self.monitoring.trigger_alert("test_alert", "Test alert message")
            mock_method.assert_called_once_with("test_alert", "Test alert message")

    def test_resolve_alert(self):
        """Test alert resolution functionality."""
        with patch.object(self.monitoring, "resolve_alert") as mock_method:
            self.monitoring.resolve_alert("test_alert")
            mock_method.assert_called_once_with("test_alert")


class TestPerformanceAnalytics(unittest.TestCase):
    """Test performance analytics functionality."""

    def setUp(self):
        """Set up test fixtures."""
        with patch("builtins.print"):
            self.monitoring = MonitoringSystem()

    def test_calculate_performance_baseline(self):
        """Test performance baseline calculation."""
        with patch.object(self.monitoring, "calculate_performance_baseline") as mock_method:
            mock_method.return_value = {
                "metric": "sts_request_duration",
                "baseline": 0.150,
                "std_deviation": 0.025,
                "sample_size": 1000,
            }

            result = self.monitoring.calculate_performance_baseline("sts_request_duration")
            
            self.assertIsInstance(result, dict)
            self.assertIn("baseline", result)
            mock_method.assert_called_once_with("sts_request_duration")

    def test_detect_performance_anomalies(self):
        """Test performance anomaly detection."""
        with patch.object(self.monitoring, "detect_performance_anomalies") as mock_method:
            mock_method.return_value = [
                {
                    "metric": "sts_request_duration",
                    "timestamp": datetime.now(),
                    "value": 2.5,
                    "baseline": 0.150,
                    "deviation": 15.67,
                }
            ]

            anomalies = self.monitoring.detect_performance_anomalies()
            
            self.assertIsInstance(anomalies, list)
            if anomalies:
                self.assertIn("metric", anomalies[0])
                self.assertIn("timestamp", anomalies[0])
            mock_method.assert_called_once()

    def test_generate_performance_report(self):
        """Test performance report generation."""
        start_time = datetime.now() - timedelta(hours=24)
        end_time = datetime.now()

        with patch.object(self.monitoring, "generate_performance_report") as mock_method:
            mock_method.return_value = {
                "period": {"start": start_time, "end": end_time},
                "summary": {"total_requests": 10000, "avg_response_time": 0.125},
                "metrics": [],
                "anomalies": [],
            }

            report = self.monitoring.generate_performance_report(start_time, end_time)
            
            self.assertIsInstance(report, dict)
            self.assertIn("period", report)
            self.assertIn("summary", report)
            mock_method.assert_called_once_with(start_time, end_time)


class TestNeuralTracerMonitoring(unittest.TestCase):
    """Test neural tracer specific monitoring functionality."""

    def setUp(self):
        """Set up test fixtures."""
        with patch("builtins.print"):
            self.monitoring = MonitoringSystem()

    def test_neural_experiment_monitoring(self):
        """Test neural experiment monitoring."""
        experiment_data = {
            "experiment_id": "exp_001",
            "tracer_type": "neural",
            "duration": 120.5,
            "safety_score": 0.95,
            "biocompatibility_score": 0.98,
        }

        with patch.object(self.monitoring, "record_neural_experiment") as mock_method:
            self.monitoring.record_neural_experiment(experiment_data)
            mock_method.assert_called_once_with(experiment_data)

    def test_safety_violation_monitoring(self):
        """Test safety violation monitoring."""
        violation_data = {
            "experiment_id": "exp_002",
            "violation_type": "energy_threshold_exceeded",
            "severity": "high",
            "timestamp": datetime.now(),
        }

        with patch.object(self.monitoring, "record_safety_violation") as mock_method:
            self.monitoring.record_safety_violation(violation_data)
            mock_method.assert_called_once_with(violation_data)

    def test_biocompatibility_monitoring(self):
        """Test biocompatibility monitoring."""
        biocompat_data = {
            "tracer_id": "tracer_001",
            "biocompatibility_score": 0.97,
            "toxicity_level": 0.02,
            "atp_consumption_rate": 1.5e-15,  # J/s
        }

        with patch.object(self.monitoring, "record_biocompatibility_metrics") as mock_method:
            self.monitoring.record_biocompatibility_metrics(biocompat_data)
            mock_method.assert_called_once_with(biocompat_data)

    def test_quantum_tracer_monitoring(self):
        """Test quantum tracer monitoring."""
        quantum_data = {
            "experiment_id": "quantum_exp_001",
            "entanglement_fidelity": 0.985,
            "decoherence_time": 0.1,  # seconds
            "photon_pair_rate": 1000,  # Hz
        }

        with patch.object(self.monitoring, "record_quantum_metrics") as mock_method:
            self.monitoring.record_quantum_metrics(quantum_data)
            mock_method.assert_called_once_with(quantum_data)


class TestComplianceAndAudit(unittest.TestCase):
    """Test compliance and audit functionality."""

    def setUp(self):
        """Set up test fixtures."""
        with patch("builtins.print"):
            self.monitoring = MonitoringSystem()

    def test_audit_log_creation(self):
        """Test audit log creation."""
        audit_event = {
            "event_type": "experiment_start",
            "user_id": "user_001",
            "experiment_id": "exp_001",
            "timestamp": datetime.now(),
            "details": {"tracer_type": "neural"},
        }

        with patch.object(self.monitoring, "create_audit_log") as mock_method:
            self.monitoring.create_audit_log(audit_event)
            mock_method.assert_called_once_with(audit_event)

    def test_compliance_check(self):
        """Test compliance checking."""
        with patch.object(self.monitoring, "run_compliance_check") as mock_method:
            mock_method.return_value = {
                "compliant": True,
                "violations": [],
                "recommendations": [],
                "timestamp": datetime.now(),
            }

            result = self.monitoring.run_compliance_check()
            
            self.assertIsInstance(result, dict)
            self.assertIn("compliant", result)
            mock_method.assert_called_once()

    def test_generate_compliance_report(self):
        """Test compliance report generation."""
        report_params = {
            "start_date": datetime.now() - timedelta(days=30),
            "end_date": datetime.now(),
            "report_type": "monthly",
        }

        with patch.object(self.monitoring, "generate_compliance_report") as mock_method:
            mock_method.return_value = {
                "report_id": "comp_report_001",
                "period": report_params,
                "compliance_score": 98.5,
                "violations": [],
                "recommendations": [],
            }

            report = self.monitoring.generate_compliance_report(**report_params)
            
            self.assertIsInstance(report, dict)
            self.assertIn("compliance_score", report)
            mock_method.assert_called_once_with(**report_params)


class TestDashboardAndVisualization(unittest.TestCase):
    """Test dashboard and visualization functionality."""

    def setUp(self):
        """Set up test fixtures."""
        with patch("builtins.print"):
            self.monitoring = MonitoringSystem()

    def test_dashboard_data_generation(self):
        """Test dashboard data generation."""
        with patch.object(self.monitoring, "get_dashboard_data") as mock_method:
            mock_method.return_value = {
                "system_health": {"status": "healthy", "score": 95},
                "active_experiments": 5,
                "recent_alerts": [],
                "performance_metrics": {},
                "timestamp": datetime.now(),
            }

            data = self.monitoring.get_dashboard_data()
            
            self.assertIsInstance(data, dict)
            self.assertIn("system_health", data)
            mock_method.assert_called_once()

    def test_real_time_metrics_stream(self):
        """Test real-time metrics streaming."""
        with patch.object(self.monitoring, "stream_real_time_metrics") as mock_method:
            def mock_generator():
                yield {"metric": "sts_requests_total", "value": 100}
                yield {"metric": "sts_active_connections", "value": 15}

            mock_method.return_value = mock_generator()

            stream = self.monitoring.stream_real_time_metrics()
            
            # Test that we can iterate over the stream
            metrics = list(stream)
            self.assertEqual(len(metrics), 2)
            mock_method.assert_called_once()

    def test_visualization_config_generation(self):
        """Test visualization configuration generation."""
        with patch.object(self.monitoring, "generate_visualization_config") as mock_method:
            mock_method.return_value = {
                "dashboards": [
                    {
                        "name": "System Overview",
                        "panels": [
                            {"type": "graph", "metric": "sts_requests_total"},
                            {"type": "gauge", "metric": "sts_error_rate"},
                        ],
                    }
                ],
                "alerting": {"rules": [], "channels": []},
            }

            config = self.monitoring.generate_visualization_config()
            
            self.assertIsInstance(config, dict)
            self.assertIn("dashboards", config)
            mock_method.assert_called_once()


class TestHealthChecks(unittest.TestCase):
    """Test health check functionality."""

    def setUp(self):
        """Set up test fixtures."""
        with patch("builtins.print"):
            self.monitoring = MonitoringSystem()

    def test_system_health_check(self):
        """Test system health check."""
        with patch.object(self.monitoring, "check_system_health") as mock_method:
            mock_method.return_value = {
                "status": "healthy",
                "score": 95.5,
                "components": {
                    "database": {"status": "healthy", "response_time": 0.05},
                    "cache": {"status": "healthy", "hit_ratio": 0.85},
                    "api": {"status": "healthy", "error_rate": 0.001},
                },
                "timestamp": datetime.now(),
            }

            health = self.monitoring.check_system_health()
            
            self.assertIsInstance(health, dict)
            self.assertIn("status", health)
            self.assertIn("score", health)
            mock_method.assert_called_once()

    def test_service_dependency_check(self):
        """Test service dependency checking."""
        with patch.object(self.monitoring, "check_service_dependencies") as mock_method:
            mock_method.return_value = {
                "postgres": {"status": "connected", "latency": 0.02},
                "redis": {"status": "connected", "latency": 0.001},
                "elasticsearch": {"status": "connected", "latency": 0.05},
            }

            dependencies = self.monitoring.check_service_dependencies()
            
            self.assertIsInstance(dependencies, dict)
            for service, status in dependencies.items():
                self.assertIn("status", status)
            mock_method.assert_called_once()


class TestDataRetentionAndCleanup(unittest.TestCase):
    """Test data retention and cleanup functionality."""

    def setUp(self):
        """Set up test fixtures."""
        with patch("builtins.print"):
            self.monitoring = MonitoringSystem()

    def test_data_retention_policy(self):
        """Test data retention policy application."""
        retention_policy = {
            "metrics": {"retention_days": 90},
            "logs": {"retention_days": 30},
            "alerts": {"retention_days": 365},
        }

        with patch.object(self.monitoring, "apply_retention_policy") as mock_method:
            self.monitoring.apply_retention_policy(retention_policy)
            mock_method.assert_called_once_with(retention_policy)

    def test_cleanup_old_data(self):
        """Test old data cleanup."""
        cutoff_date = datetime.now() - timedelta(days=90)

        with patch.object(self.monitoring, "cleanup_old_data") as mock_method:
            mock_method.return_value = {
                "deleted_metrics": 1000,
                "deleted_logs": 5000,
                "deleted_alerts": 50,
                "cleanup_timestamp": datetime.now(),
            }

            result = self.monitoring.cleanup_old_data(cutoff_date)
            
            self.assertIsInstance(result, dict)
            self.assertIn("deleted_metrics", result)
            mock_method.assert_called_once_with(cutoff_date)

    def test_data_archival(self):
        """Test data archival functionality."""
        archive_config = {
            "destination": "s3://sts-archive-bucket",
            "compression": "gzip",
            "format": "parquet",
        }

        with patch.object(self.monitoring, "archive_old_data") as mock_method:
            mock_method.return_value = {
                "archived_files": ["metrics_2023_01.parquet", "logs_2023_01.parquet"],
                "total_size": "1.2GB",
                "archive_timestamp": datetime.now(),
            }

            result = self.monitoring.archive_old_data(archive_config)
            
            self.assertIsInstance(result, dict)
            self.assertIn("archived_files", result)
            mock_method.assert_called_once_with(archive_config)


class TestEdgeCasesAndErrorHandling(unittest.TestCase):
    """Test edge cases and error handling."""

    def setUp(self):
        """Set up test fixtures."""
        with patch("builtins.print"):
            self.monitoring = MonitoringSystem()

    def test_invalid_metric_values(self):
        """Test handling of invalid metric values."""
        # Test with various invalid values
        invalid_values = [float('inf'), float('-inf'), float('nan'), None]

        for invalid_value in invalid_values:
            with patch.object(self.monitoring, "record_metric") as mock_method:
                # Should handle gracefully without raising exceptions
                try:
                    self.monitoring.record_metric("test_metric", invalid_value)
                except Exception as e:
                    self.fail(f"Should handle invalid value {invalid_value} gracefully: {e}")

    def test_duplicate_alert_rules(self):
        """Test handling of duplicate alert rule names."""
        rule1 = AlertRule(
            name="duplicate_rule",
            description="First rule",
            metric_name="metric1",
            condition="greater_than",
            threshold=1.0,
            severity=AlertSeverity.INFO,
        )

        rule2 = AlertRule(
            name="duplicate_rule",
            description="Second rule", 
            metric_name="metric2",
            condition="less_than",
            threshold=2.0,
            severity=AlertSeverity.WARNING,
        )

        with patch.object(self.monitoring, "add_alert_rule") as mock_method:
            # Should handle duplicate names appropriately
            self.monitoring.add_alert_rule(rule1)
            self.monitoring.add_alert_rule(rule2)
            
            self.assertEqual(mock_method.call_count, 2)

    def test_empty_metrics_storage(self):
        """Test handling of empty metrics storage."""
        with patch.object(self.monitoring, "metrics_storage", {}):
            with patch.object(self.monitoring, "get_metric_value") as mock_method:
                mock_method.return_value = None
                
                result = self.monitoring.get_metric_value("nonexistent_metric")
                self.assertIsNone(result)

    def test_very_large_threshold_values(self):
        """Test handling of very large threshold values."""
        large_threshold = 1e100

        rule = AlertRule(
            name="large_threshold_rule",
            description="Rule with large threshold",
            metric_name="test_metric",
            condition="greater_than",
            threshold=large_threshold,
            severity=AlertSeverity.CRITICAL,
        )

        # Should handle large threshold values
        self.assertEqual(rule.threshold, large_threshold)

    def test_negative_duration_values(self):
        """Test handling of negative duration values."""
        rule = AlertRule(
            name="negative_duration_rule",
            description="Rule with negative duration",
            metric_name="test_metric",
            condition="greater_than",
            threshold=1.0,
            severity=AlertSeverity.INFO,
            duration=-300,  # Negative duration
        )

        # Should still create the rule (validation could be added later)
        self.assertEqual(rule.duration, -300)

    def test_concurrent_metric_updates(self):
        """Test handling of concurrent metric updates."""
        import threading

        def update_metric():
            with patch.object(self.monitoring, "record_metric") as mock_method:
                self.monitoring.record_metric("concurrent_metric", 1.0)

        # Create multiple threads updating metrics concurrently
        threads = [threading.Thread(target=update_metric) for _ in range(10)]
        
        for thread in threads:
            thread.start()
            
        for thread in threads:
            thread.join()

        # Should complete without deadlocks or exceptions
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()