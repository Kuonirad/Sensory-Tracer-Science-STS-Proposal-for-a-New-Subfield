#!/usr/bin/env python3
"""
Tests for the STS monitoring and analytics module.

These tests exercise the real public API of
``sensory_tracer_science.deployment.monitoring_analytics``:
the ``MonitoringMetric`` / ``AlertRule`` dataclasses and the
``MonitoringSystem`` (metric recording, alert evaluation, reporting,
health status and metric export).
"""

from datetime import datetime
from unittest.mock import patch

import pytest

from sensory_tracer_science.deployment.monitoring_analytics import (
    AlertRule,
    AlertSeverity,
    MetricType,
    MonitoringMetric,
    MonitoringSystem,
    run_monitoring_demo,
)


class TestEnums:
    def test_alert_severity_values(self):
        assert AlertSeverity.INFO.value == "info"
        assert AlertSeverity.WARNING.value == "warning"
        assert AlertSeverity.CRITICAL.value == "critical"
        assert AlertSeverity.EMERGENCY.value == "emergency"

    def test_metric_type_values(self):
        assert MetricType.COUNTER.value == "counter"
        assert MetricType.GAUGE.value == "gauge"
        assert MetricType.HISTOGRAM.value == "histogram"
        assert MetricType.SUMMARY.value == "summary"


class TestMonitoringMetric:
    def test_required_fields_and_post_init_defaults(self):
        metric = MonitoringMetric(
            name="cpu",
            metric_type=MetricType.GAUGE,
            description="CPU usage",
            unit="percent",
        )
        assert metric.name == "cpu"
        assert metric.metric_type is MetricType.GAUGE
        assert metric.value == 0.0
        # __post_init__ supplies an empty label dict and a timestamp
        assert metric.labels == {}
        assert isinstance(metric.timestamp, datetime)

    def test_custom_labels_preserved(self):
        labels = {"host": "server1"}
        metric = MonitoringMetric(
            name="io",
            metric_type=MetricType.COUNTER,
            description="IO",
            unit="bytes",
            labels=labels,
            value=12.0,
        )
        assert metric.labels == labels
        assert metric.value == 12.0


class TestAlertRule:
    def test_required_fields_and_defaults(self):
        rule = AlertRule(
            name="high_cpu",
            description="CPU too high",
            metric_name="sts_cpu_usage",
            condition="greater_than",
            threshold=80.0,
            severity=AlertSeverity.WARNING,
        )
        assert rule.duration == 300
        assert rule.enabled is True
        assert rule.notification_channels == []


class TestMonitoringSystem:
    def setup_method(self):
        with patch("builtins.print"):
            self.system = MonitoringSystem(environment="production")

    def test_initialization_populates_core_metrics_and_alerts(self):
        assert self.system.environment == "production"
        assert "sts_error_rate" in self.system.metrics_storage
        assert "sts_requests_total" in self.system.metrics_storage
        assert "high_error_rate" in self.system.alert_rules

    def test_record_metric_updates_value(self):
        with patch("builtins.print"):
            self.system.record_metric("sts_error_rate", 1.0)
        assert self.system.metrics_storage["sts_error_rate"].value == 1.0

    def test_record_unknown_metric_is_noop(self):
        with patch("builtins.print"):
            self.system.record_metric("does_not_exist", 5.0)
        assert "does_not_exist" not in self.system.metrics_storage

    def test_increment_counter(self):
        with patch("builtins.print"):
            start = self.system.metrics_storage["sts_requests_total"].value
            self.system.increment_counter("sts_requests_total", 3.0)
        assert self.system.metrics_storage["sts_requests_total"].value == start + 3.0

    def test_increment_counter_ignores_non_counter(self):
        with patch("builtins.print"):
            self.system.increment_counter("sts_error_rate", 5.0)
        # sts_error_rate is a GAUGE, so increment_counter must not change it
        assert self.system.metrics_storage["sts_error_rate"].value == 0.0

    def test_recording_threshold_breach_triggers_alert(self):
        with patch("builtins.print"):
            # high_error_rate fires when sts_error_rate > 5.0
            self.system.record_metric("sts_error_rate", 99.0)
        assert len(self.system.active_alerts) >= 1
        triggered = [
            a["rule_name"] for a in self.system.active_alerts.values()
        ]
        assert "high_error_rate" in triggered

    def test_generate_performance_report_structure(self):
        report = self.system.generate_performance_report(hours=12)
        assert report["time_range"]["duration_hours"] == 12
        assert "application_performance" in report
        assert "alerts_summary" in report

    def test_generate_compliance_report_structure(self):
        report = self.system.generate_compliance_report()
        assert report["compliance_status"] == "COMPLIANT"
        assert "regulatory_compliance" in report

    def test_system_health_status(self):
        with patch("builtins.print"):
            self.system.record_metric("sts_error_rate", 0.1)
        health = self.system.get_system_health_status()
        assert health["overall_status"] in (
            "HEALTHY",
            "WARNING",
            "DEGRADED",
            "CRITICAL",
        )
        assert 0.0 <= health["health_score"] <= 1.0

    def test_export_metrics_prometheus(self):
        output = self.system.export_metrics(format="prometheus")
        assert "# HELP" in output
        assert "# TYPE" in output

    def test_export_metrics_json(self):
        output = self.system.export_metrics(format="json")
        assert "sts_error_rate" in output

    def test_export_metrics_invalid_format(self):
        with pytest.raises(ValueError, match="Unsupported export format"):
            self.system.export_metrics(format="csv")


def test_run_monitoring_demo_is_callable():
    assert callable(run_monitoring_demo)
