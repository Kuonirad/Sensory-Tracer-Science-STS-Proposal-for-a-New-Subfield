#!/usr/bin/env python3
"""
Integration Test Suite for Deployment Modules

Direct integration tests that import and execute deployment code to ensure
actual coverage of the deployment modules.
"""

import unittest
from datetime import datetime, timedelta

from sensory_tracer_science.deployment.cloud_deployment import (
    CloudDeploymentManager,
    CloudInfrastructure,
    CloudProvider,
    DeploymentType,
    create_cloud_deployment_demo,
)
from sensory_tracer_science.deployment.monitoring_analytics import (
    AlertRule,
    AlertSeverity,
    MetricType,
    MonitoringMetric,
    MonitoringSystem,
)
from sensory_tracer_science.deployment.production_config import (
    DatabaseConfig,
    DeploymentEnvironment,
    ProductionConfig,
    RedisConfig,
    SecurityConfig,
    SecurityLevel,
)
from sensory_tracer_science.deployment.container_orchestration import (
    ContainerConfig,
    ContainerOrchestrator,
    KubernetesConfig,
)


class TestCloudDeploymentIntegration(unittest.TestCase):
    """Integration tests for cloud deployment module."""

    def test_cloud_provider_enum_usage(self):
        """Test actual usage of CloudProvider enum."""
        # This will execute actual enum code
        aws = CloudProvider.AWS
        azure = CloudProvider.AZURE
        gcp = CloudProvider.GCP
        hybrid = CloudProvider.HYBRID
        
        self.assertEqual(aws.value, "aws")
        self.assertEqual(azure.value, "azure")
        self.assertEqual(gcp.value, "gcp")
        self.assertEqual(hybrid.value, "hybrid")

    def test_deployment_type_enum_usage(self):
        """Test actual usage of DeploymentType enum."""
        # This will execute actual enum code
        serverless = DeploymentType.SERVERLESS
        containers = DeploymentType.CONTAINERS
        vms = DeploymentType.VIRTUAL_MACHINES
        k8s = DeploymentType.KUBERNETES
        managed = DeploymentType.MANAGED_SERVICES
        
        self.assertEqual(serverless.value, "serverless")
        self.assertEqual(containers.value, "containers")
        self.assertEqual(vms.value, "virtual_machines")
        self.assertEqual(k8s.value, "kubernetes")
        self.assertEqual(managed.value, "managed_services")

    def test_cloud_infrastructure_creation(self):
        """Test actual CloudInfrastructure creation and methods."""
        # This will execute actual dataclass code
        infra = CloudInfrastructure(
            provider=CloudProvider.AWS,
            region="us-east-1",
            availability_zones=["us-east-1a", "us-east-1b"],
            instance_type="large",
            min_instances=3,
            max_instances=50,
            storage_size_gb=200,
        )
        
        # Test dataclass functionality
        self.assertEqual(infra.provider, CloudProvider.AWS)
        self.assertEqual(infra.region, "us-east-1")
        self.assertEqual(infra.instance_type, "large")
        self.assertEqual(infra.min_instances, 3)
        self.assertEqual(infra.max_instances, 50)
        self.assertEqual(infra.storage_size_gb, 200)

        # Test __post_init__ execution
        self.assertEqual(infra.public_subnets, ["10.0.1.0/24", "10.0.2.0/24"])
        self.assertEqual(infra.private_subnets, ["10.0.10.0/24", "10.0.20.0/24"])
        self.assertEqual(infra.security_groups, [])

    def test_cloud_deployment_manager_creation(self):
        """Test actual CloudDeploymentManager creation."""
        # This will execute actual class code including __init__
        manager = CloudDeploymentManager(CloudProvider.AWS, DeploymentType.KUBERNETES)
        
        self.assertEqual(manager.provider, CloudProvider.AWS)
        self.assertEqual(manager.deployment_type, DeploymentType.KUBERNETES)
        self.assertIsNone(manager.infrastructure)

    def test_aws_terraform_generation(self):
        """Test actual Terraform generation methods."""
        manager = CloudDeploymentManager(CloudProvider.AWS, DeploymentType.KUBERNETES)
        
        infra = CloudInfrastructure(
            provider=CloudProvider.AWS,
            region="us-east-1",
            availability_zones=["us-east-1a", "us-east-1b"],
        )
        
        # Test actual method execution
        terraform_config = manager.generate_aws_terraform(infra)
        
        self.assertIsInstance(terraform_config, str)
        self.assertIn("terraform {", terraform_config)
        self.assertIn("provider \"aws\"", terraform_config)

    def test_cost_optimization_methods(self):
        """Test actual cost optimization methods."""
        manager = CloudDeploymentManager(CloudProvider.AWS, DeploymentType.KUBERNETES)
        
        infra = CloudInfrastructure(
            provider=CloudProvider.AWS,
            region="us-east-1",
            availability_zones=["us-east-1a"],
            max_instances=75,  # Trigger recommendation
        )
        
        # Test actual method execution
        recommendations = manager.generate_cost_optimization_recommendations(infra)
        
        self.assertIsInstance(recommendations, dict)
        self.assertIn("estimated_monthly_cost", recommendations)
        self.assertIn("recommendations", recommendations)

    def test_disaster_recovery_methods(self):
        """Test actual disaster recovery methods."""
        manager = CloudDeploymentManager(CloudProvider.AWS, DeploymentType.KUBERNETES)
        
        infra = CloudInfrastructure(
            provider=CloudProvider.AWS,
            region="us-east-1",
            availability_zones=["us-east-1a"],
        )
        
        # Test actual method execution
        dr_plan = manager.generate_disaster_recovery_plan(infra)
        
        self.assertIsInstance(dr_plan, dict)
        self.assertIn("recovery_objectives", dr_plan)
        self.assertIn("failover_procedures", dr_plan)

    def test_serverless_config_generation(self):
        """Test actual serverless configuration generation."""
        # Test AWS serverless
        aws_manager = CloudDeploymentManager(CloudProvider.AWS, DeploymentType.SERVERLESS)
        aws_config = aws_manager.generate_serverless_config()
        
        self.assertIsInstance(aws_config, dict)
        self.assertEqual(aws_config["service"], "sts-serverless")
        
        # Test Azure serverless
        azure_manager = CloudDeploymentManager(CloudProvider.AZURE, DeploymentType.SERVERLESS)
        azure_config = azure_manager.generate_serverless_config()
        
        self.assertIsInstance(azure_config, dict)
        self.assertEqual(azure_config["service"], "sts-azure-functions")
        
        # Test GCP serverless
        gcp_manager = CloudDeploymentManager(CloudProvider.GCP, DeploymentType.SERVERLESS)
        gcp_config = gcp_manager.generate_serverless_config()
        
        self.assertIsInstance(gcp_config, dict)
        self.assertEqual(gcp_config["service"], "sts-cloud-functions")

    def test_demo_function_execution(self):
        """Test actual demo function execution."""
        # This will execute the entire demo function with all its methods
        demo_result = create_cloud_deployment_demo()
        
        self.assertIsInstance(demo_result, dict)
        self.assertIn("aws_manager", demo_result)
        self.assertIn("infrastructure", demo_result)
        self.assertIn("terraform_config", demo_result)
        self.assertIn("cost_recommendations", demo_result)
        self.assertIn("dr_plan", demo_result)
        self.assertIn("serverless_config", demo_result)


class TestMonitoringAnalyticsIntegration(unittest.TestCase):
    """Integration tests for monitoring analytics module."""

    def test_alert_severity_enum_usage(self):
        """Test actual usage of AlertSeverity enum."""
        info = AlertSeverity.INFO
        warning = AlertSeverity.WARNING
        critical = AlertSeverity.CRITICAL
        emergency = AlertSeverity.EMERGENCY
        
        self.assertEqual(info.value, "info")
        self.assertEqual(warning.value, "warning")
        self.assertEqual(critical.value, "critical")
        self.assertEqual(emergency.value, "emergency")

    def test_metric_type_enum_usage(self):
        """Test actual usage of MetricType enum."""
        counter = MetricType.COUNTER
        gauge = MetricType.GAUGE
        histogram = MetricType.HISTOGRAM
        summary = MetricType.SUMMARY
        
        self.assertEqual(counter.value, "counter")
        self.assertEqual(gauge.value, "gauge")
        self.assertEqual(histogram.value, "histogram")
        self.assertEqual(summary.value, "summary")

    def test_monitoring_metric_creation(self):
        """Test actual MonitoringMetric creation and methods."""
        metric = MonitoringMetric(
            name="test_requests_total",
            metric_type=MetricType.COUNTER,
            description="Total test requests",
            unit="requests",
            labels={"service": "test", "endpoint": "/api"},
            value=42.0,
        )
        
        self.assertEqual(metric.name, "test_requests_total")
        self.assertEqual(metric.metric_type, MetricType.COUNTER)
        self.assertEqual(metric.description, "Total test requests")
        self.assertEqual(metric.unit, "requests")
        self.assertEqual(metric.labels["service"], "test")
        self.assertEqual(metric.value, 42.0)
        
        # Test __post_init__ execution
        self.assertIsInstance(metric.timestamp, datetime)

    def test_alert_rule_creation(self):
        """Test actual AlertRule creation and methods."""
        rule = AlertRule(
            name="high_error_rate",
            description="Alert when error rate exceeds threshold",
            metric_name="error_rate",
            condition="greater_than",
            threshold=5.0,
            severity=AlertSeverity.CRITICAL,
            duration=300,
            notification_channels=["email", "slack"],
        )
        
        self.assertEqual(rule.name, "high_error_rate")
        self.assertEqual(rule.metric_name, "error_rate")
        self.assertEqual(rule.condition, "greater_than")
        self.assertEqual(rule.threshold, 5.0)
        self.assertEqual(rule.severity, AlertSeverity.CRITICAL)
        self.assertEqual(rule.duration, 300)
        self.assertEqual(rule.notification_channels, ["email", "slack"])

    def test_monitoring_system_initialization(self):
        """Test actual MonitoringSystem initialization and methods."""
        monitoring = MonitoringSystem(environment="testing")
        
        self.assertEqual(monitoring.environment, "testing")
        self.assertIsInstance(monitoring.metrics_storage, dict)
        self.assertIsInstance(monitoring.alert_rules, dict)
        self.assertIsInstance(monitoring.active_alerts, dict)
        self.assertIsInstance(monitoring.performance_baselines, dict)
        
        # Verify core metrics were initialized
        self.assertGreater(len(monitoring.metrics_storage), 0)
        
        # Verify default alerts were set up
        self.assertGreater(len(monitoring.alert_rules), 0)


class TestProductionConfigIntegration(unittest.TestCase):
    """Integration tests for production config module."""

    def test_deployment_environment_enum_usage(self):
        """Test actual usage of DeploymentEnvironment enum."""
        dev = DeploymentEnvironment.DEVELOPMENT
        test = DeploymentEnvironment.TESTING
        staging = DeploymentEnvironment.STAGING
        prod = DeploymentEnvironment.PRODUCTION
        clinical = DeploymentEnvironment.CLINICAL
        
        self.assertEqual(dev.value, "development")
        self.assertEqual(test.value, "testing")
        self.assertEqual(staging.value, "staging")
        self.assertEqual(prod.value, "production")
        self.assertEqual(clinical.value, "clinical")

    def test_security_level_enum_usage(self):
        """Test actual usage of SecurityLevel enum."""
        basic = SecurityLevel.BASIC
        hipaa = SecurityLevel.HIPAA
        fda = SecurityLevel.FDA_CFR21
        iso = SecurityLevel.ISO27001
        sox = SecurityLevel.SOX
        
        self.assertEqual(basic.value, "basic")
        self.assertEqual(hipaa.value, "hipaa")
        self.assertEqual(fda.value, "fda_cfr21")
        self.assertEqual(iso.value, "iso27001")
        self.assertEqual(sox.value, "sox")

    def test_database_config_creation(self):
        """Test actual DatabaseConfig creation and methods."""
        db_config = DatabaseConfig(
            host="db.example.com",
            port=5433,
            database="sts_test",
            username="test_user",
            password_env_var="TEST_DB_PASSWORD",
            min_connections=10,
            max_connections=200,
            backup_enabled=True,
            ssl_enabled=True,
            audit_logging=True,
        )
        
        self.assertEqual(db_config.host, "db.example.com")
        self.assertEqual(db_config.port, 5433)
        self.assertEqual(db_config.database, "sts_test")
        self.assertEqual(db_config.username, "test_user")
        self.assertEqual(db_config.password_env_var, "TEST_DB_PASSWORD")
        self.assertEqual(db_config.min_connections, 10)
        self.assertEqual(db_config.max_connections, 200)
        self.assertTrue(db_config.backup_enabled)
        self.assertTrue(db_config.ssl_enabled)
        self.assertTrue(db_config.audit_logging)

    def test_redis_config_creation(self):
        """Test actual RedisConfig creation and methods."""
        redis_config = RedisConfig(
            host="redis.example.com",
            port=6380,
            database=1,
            max_connections=100,
            max_memory_mb=2048,
            persistence_enabled=True,
            cluster_enabled=True,
            cluster_nodes=["redis1:6379", "redis2:6379"],
        )
        
        self.assertEqual(redis_config.host, "redis.example.com")
        self.assertEqual(redis_config.port, 6380)
        self.assertEqual(redis_config.database, 1)
        self.assertEqual(redis_config.max_connections, 100)
        self.assertEqual(redis_config.max_memory_mb, 2048)
        self.assertTrue(redis_config.persistence_enabled)
        self.assertTrue(redis_config.cluster_enabled)
        self.assertEqual(redis_config.cluster_nodes, ["redis1:6379", "redis2:6379"])

    def test_security_config_creation(self):
        """Test actual SecurityConfig creation and methods."""
        security_config = SecurityConfig(
            authentication_method="oauth2",
            jwt_expiration_hours=12,
            multi_factor_auth_required=True,
            rbac_enabled=True,
            encryption_algorithm="AES-256-GCM",
            key_rotation_days=90,
            rate_limiting_enabled=True,
            rate_limit_requests_per_minute=2000,
            audit_log_enabled=True,
            compliance_level=SecurityLevel.HIPAA,
            cors_allowed_origins=["https://app1.com", "https://app2.com"],
            ip_whitelist_enabled=True,
            allowed_ip_ranges=["10.0.0.0/8"],
        )
        
        self.assertEqual(security_config.authentication_method, "oauth2")
        self.assertEqual(security_config.jwt_expiration_hours, 12)
        self.assertTrue(security_config.multi_factor_auth_required)
        self.assertTrue(security_config.rbac_enabled)
        self.assertEqual(security_config.encryption_algorithm, "AES-256-GCM")
        self.assertEqual(security_config.key_rotation_days, 90)
        self.assertTrue(security_config.rate_limiting_enabled)
        self.assertEqual(security_config.rate_limit_requests_per_minute, 2000)
        self.assertTrue(security_config.audit_log_enabled)
        self.assertEqual(security_config.compliance_level, SecurityLevel.HIPAA)
        self.assertEqual(security_config.cors_allowed_origins, ["https://app1.com", "https://app2.com"])
        self.assertTrue(security_config.ip_whitelist_enabled)
        self.assertEqual(security_config.allowed_ip_ranges, ["10.0.0.0/8"])

        # Test __post_init__ execution for default values when None
        default_config = SecurityConfig()
        self.assertEqual(default_config.cors_allowed_origins, ["https://sts-dashboard.company.com"])
        self.assertEqual(default_config.allowed_ip_ranges, [])


class TestContainerOrchestrationIntegration(unittest.TestCase):
    """Integration tests for container orchestration module."""

    def test_container_config_creation(self):
        """Test actual ContainerConfig creation and methods."""
        from sensory_tracer_science.deployment.container_orchestration import ContainerConfig
        
        config = ContainerConfig(
            base_image="python:3.11-slim",
            image_name="sts-test",
            image_tag="v1.0.0",
            cpu_request="200m",
            cpu_limit="1000m",
            memory_request="512Mi",
            memory_limit="1Gi",
            port=9000,
            health_check_path="/api/health",
            restart_policy="OnFailure",
            run_as_non_root=True,
            run_as_user=2000,
            read_only_root_filesystem=True,
        )
        
        self.assertEqual(config.base_image, "python:3.11-slim")
        self.assertEqual(config.image_name, "sts-test")
        self.assertEqual(config.image_tag, "v1.0.0")
        self.assertEqual(config.cpu_request, "200m")
        self.assertEqual(config.cpu_limit, "1000m")
        self.assertEqual(config.memory_request, "512Mi")
        self.assertEqual(config.memory_limit, "1Gi")
        self.assertEqual(config.port, 9000)
        self.assertEqual(config.health_check_path, "/api/health")
        self.assertEqual(config.restart_policy, "OnFailure")
        self.assertTrue(config.run_as_non_root)
        self.assertEqual(config.run_as_user, 2000)
        self.assertTrue(config.read_only_root_filesystem)
        
        # Test __post_init__ execution
        self.assertEqual(config.persistent_volumes, [])
        self.assertEqual(config.config_maps, [])
        self.assertEqual(config.secrets, [])

    def test_kubernetes_config_creation(self):
        """Test actual KubernetesConfig creation and methods."""
        from sensory_tracer_science.deployment.container_orchestration import KubernetesConfig
        
        k8s_config = KubernetesConfig(
            namespace="sts-test",
            cluster_name="test-cluster",
            deployment_strategy="RollingUpdate",
            max_surge="50%",
            max_unavailable="10%",
            service_type="LoadBalancer",
            ingress_enabled=True,
            hpa_enabled=True,
            min_replicas=1,
            max_replicas=50,
            target_cpu_utilization=80,
            storage_class="standard",
            volume_size="20Gi",
        )
        
        self.assertEqual(k8s_config.namespace, "sts-test")
        self.assertEqual(k8s_config.cluster_name, "test-cluster")
        self.assertEqual(k8s_config.deployment_strategy, "RollingUpdate")
        self.assertEqual(k8s_config.max_surge, "50%")
        self.assertEqual(k8s_config.max_unavailable, "10%")
        self.assertEqual(k8s_config.service_type, "LoadBalancer")
        self.assertTrue(k8s_config.ingress_enabled)
        self.assertTrue(k8s_config.hpa_enabled)
        self.assertEqual(k8s_config.min_replicas, 1)
        self.assertEqual(k8s_config.max_replicas, 50)
        self.assertEqual(k8s_config.target_cpu_utilization, 80)
        self.assertEqual(k8s_config.storage_class, "standard")
        self.assertEqual(k8s_config.volume_size, "20Gi")

    def test_container_orchestrator_initialization(self):
        """Test actual ContainerOrchestrator initialization with all environments."""
        from sensory_tracer_science.deployment.container_orchestration import ContainerOrchestrator
        
        # Test all environment types to execute environment override code
        environments = [
            DeploymentEnvironment.DEVELOPMENT,
            DeploymentEnvironment.TESTING,
            DeploymentEnvironment.STAGING,
            DeploymentEnvironment.PRODUCTION,
            DeploymentEnvironment.CLINICAL,
        ]
        
        for env in environments:
            prod_config = ProductionConfig(environment=env)
            orchestrator = ContainerOrchestrator(prod_config)
            
            self.assertEqual(orchestrator.production_config.environment, env)
            self.assertIsInstance(orchestrator.container_config, ContainerConfig)
            self.assertIsInstance(orchestrator.kubernetes_config, KubernetesConfig)
            
            # Verify environment-specific overrides were applied
            if env == DeploymentEnvironment.DEVELOPMENT:
                self.assertEqual(orchestrator.container_config.image_tag, "dev")
                self.assertEqual(orchestrator.kubernetes_config.min_replicas, 1)
                self.assertEqual(orchestrator.kubernetes_config.max_replicas, 3)
            elif env == DeploymentEnvironment.PRODUCTION:
                self.assertEqual(orchestrator.container_config.image_tag, "v1.0.0")
                self.assertEqual(orchestrator.kubernetes_config.min_replicas, 3)
                self.assertEqual(orchestrator.kubernetes_config.max_replicas, 100)
            elif env == DeploymentEnvironment.CLINICAL:
                self.assertEqual(orchestrator.container_config.image_tag, "clinical-v1.0.0")
                self.assertEqual(orchestrator.kubernetes_config.pod_security_policy, "highly-restricted")

    def test_dockerfile_generation(self):
        """Test actual Dockerfile generation method."""
        from sensory_tracer_science.deployment.container_orchestration import ContainerOrchestrator
        
        prod_config = ProductionConfig(environment=DeploymentEnvironment.PRODUCTION)
        orchestrator = ContainerOrchestrator(prod_config)
        
        # Execute actual Dockerfile generation
        dockerfile = orchestrator.generate_dockerfile()
        
        self.assertIsInstance(dockerfile, str)
        self.assertGreater(len(dockerfile), 1000)
        self.assertIn("FROM python:3.11-slim AS builder", dockerfile)
        self.assertIn("FROM python:3.11-slim AS runtime", dockerfile)
        self.assertIn("USER 1001", dockerfile)
        self.assertIn("EXPOSE 8000", dockerfile)
        self.assertIn("HEALTHCHECK", dockerfile)

    def test_docker_compose_generation(self):
        """Test actual Docker Compose generation method."""
        from sensory_tracer_science.deployment.container_orchestration import ContainerOrchestrator
        
        prod_config = ProductionConfig(environment=DeploymentEnvironment.DEVELOPMENT)
        orchestrator = ContainerOrchestrator(prod_config)
        
        # Execute actual Docker Compose generation
        compose_config = orchestrator.generate_docker_compose()
        
        self.assertIsInstance(compose_config, dict)
        self.assertEqual(compose_config["version"], "3.8")
        self.assertIn("services", compose_config)
        self.assertIn("sts-app", compose_config["services"])
        
        app_service = compose_config["services"]["sts-app"]
        self.assertIn("build", app_service)
        self.assertIn("image", app_service)
        self.assertIn("container_name", app_service)
        self.assertEqual(app_service["container_name"], "sts-framework")


if __name__ == "__main__":
    unittest.main()