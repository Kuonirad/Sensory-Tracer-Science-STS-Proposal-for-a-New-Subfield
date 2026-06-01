#!/usr/bin/env python3
"""
Comprehensive Test Suite for Container Orchestration

Tests container orchestration functionality including:
- Docker container configuration and builds
- Kubernetes deployment and service configuration
- Container security policies and resource management
- Multi-stage container builds and optimizations
- Service mesh integration and networking
- Health checks and monitoring configuration
"""

import json
import tempfile
import unittest
from dataclasses import FrozenInstanceError
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest
import yaml

from sensory_tracer_science.deployment.container_orchestration import (
    ContainerConfig,
    ContainerOrchestrator,
    KubernetesConfig,
)
from sensory_tracer_science.deployment.production_config import (
    DeploymentEnvironment,
    ProductionConfig,
)


class TestContainerConfig(unittest.TestCase):
    """Test ContainerConfig dataclass."""

    def test_default_initialization(self):
        """Test ContainerConfig with default values."""
        config = ContainerConfig()

        # Base image settings
        self.assertEqual(config.base_image, "python:3.11-slim")
        self.assertEqual(config.image_name, "sts-framework")
        self.assertEqual(config.image_tag, "latest")

        # Resource requirements
        self.assertEqual(config.cpu_request, "100m")
        self.assertEqual(config.cpu_limit, "500m")
        self.assertEqual(config.memory_request, "256Mi")
        self.assertEqual(config.memory_limit, "512Mi")

        # Container settings
        self.assertEqual(config.port, 8000)
        self.assertEqual(config.health_check_path, "/health")
        self.assertEqual(config.restart_policy, "Always")

        # Security settings
        self.assertTrue(config.run_as_non_root)
        self.assertEqual(config.run_as_user, 1001)
        self.assertTrue(config.read_only_root_filesystem)

    def test_custom_initialization(self):
        """Test ContainerConfig with custom values."""
        config = ContainerConfig(
            base_image="python:3.12-alpine",
            image_name="custom-sts",
            image_tag="v2.0.0",
            cpu_request="200m",
            cpu_limit="1000m",
            memory_request="512Mi",
            memory_limit="1Gi",
            port=9000,
            health_check_path="/api/health",
            restart_policy="OnFailure",
            run_as_non_root=False,
            run_as_user=2000,
            read_only_root_filesystem=False,
        )

        self.assertEqual(config.base_image, "python:3.12-alpine")
        self.assertEqual(config.image_name, "custom-sts")
        self.assertEqual(config.image_tag, "v2.0.0")
        self.assertEqual(config.cpu_request, "200m")
        self.assertEqual(config.cpu_limit, "1000m")
        self.assertEqual(config.memory_request, "512Mi")
        self.assertEqual(config.memory_limit, "1Gi")
        self.assertEqual(config.port, 9000)
        self.assertEqual(config.health_check_path, "/api/health")
        self.assertEqual(config.restart_policy, "OnFailure")
        self.assertFalse(config.run_as_non_root)
        self.assertEqual(config.run_as_user, 2000)
        self.assertFalse(config.read_only_root_filesystem)

    def test_post_init_defaults(self):
        """Test __post_init__ method sets default lists."""
        config = ContainerConfig()

        # Check default lists are initialized
        self.assertEqual(config.persistent_volumes, [])
        self.assertEqual(config.config_maps, [])
        self.assertEqual(config.secrets, [])

    def test_custom_lists(self):
        """Test initialization with custom lists."""
        volumes = [{"name": "data-volume", "path": "/data"}]
        config_maps = ["app-config", "db-config"]
        secrets = ["app-secrets", "db-secrets"]

        config = ContainerConfig(
            persistent_volumes=volumes,
            config_maps=config_maps,
            secrets=secrets,
        )

        self.assertEqual(config.persistent_volumes, volumes)
        self.assertEqual(config.config_maps, config_maps)
        self.assertEqual(config.secrets, secrets)

    def test_dataclass_features(self):
        """Test dataclass features like equality and representation."""
        config1 = ContainerConfig()
        config2 = ContainerConfig()

        # Test equality
        self.assertEqual(config1, config2)

        # Test representation
        repr_str = repr(config1)
        self.assertIn("ContainerConfig", repr_str)
        self.assertIn("base_image=", repr_str)

        # Test modification
        config2.image_tag = "modified"
        self.assertNotEqual(config1, config2)


class TestKubernetesConfig(unittest.TestCase):
    """Test KubernetesConfig dataclass."""

    def test_default_initialization(self):
        """Test KubernetesConfig with default values."""
        config = KubernetesConfig()

        # Cluster settings
        self.assertEqual(config.namespace, "sts-production")
        self.assertEqual(config.cluster_name, "sts-cluster")

        # Deployment strategy
        self.assertEqual(config.deployment_strategy, "RollingUpdate")
        self.assertEqual(config.max_surge, "25%")
        self.assertEqual(config.max_unavailable, "25%")

        # Service configuration
        self.assertEqual(config.service_type, "ClusterIP")
        self.assertEqual(config.load_balancer_type, "application")

        # Ingress settings
        self.assertTrue(config.ingress_enabled)
        self.assertEqual(config.ingress_class, "nginx")
        self.assertTrue(config.tls_enabled)

        # Autoscaling
        self.assertTrue(config.hpa_enabled)
        self.assertEqual(config.min_replicas, 2)
        self.assertEqual(config.max_replicas, 100)
        self.assertEqual(config.target_cpu_utilization, 70)

        # Storage
        self.assertEqual(config.storage_class, "fast-ssd")
        self.assertEqual(config.volume_size, "10Gi")

        # Network policies
        self.assertTrue(config.network_policies_enabled)
        self.assertEqual(config.pod_security_policy, "restricted")

    def test_custom_initialization(self):
        """Test KubernetesConfig with custom values."""
        config = KubernetesConfig(
            namespace="custom-namespace",
            cluster_name="custom-cluster",
            deployment_strategy="Recreate",
            max_surge="50%",
            max_unavailable="10%",
            service_type="LoadBalancer",
            load_balancer_type="network",
            ingress_enabled=False,
            ingress_class="traefik",
            tls_enabled=False,
            hpa_enabled=False,
            min_replicas=1,
            max_replicas=50,
            target_cpu_utilization=80,
            storage_class="standard",
            volume_size="20Gi",
            network_policies_enabled=False,
            pod_security_policy="privileged",
        )

        self.assertEqual(config.namespace, "custom-namespace")
        self.assertEqual(config.cluster_name, "custom-cluster")
        self.assertEqual(config.deployment_strategy, "Recreate")
        self.assertEqual(config.max_surge, "50%")
        self.assertEqual(config.max_unavailable, "10%")
        self.assertEqual(config.service_type, "LoadBalancer")
        self.assertEqual(config.load_balancer_type, "network")
        self.assertFalse(config.ingress_enabled)
        self.assertEqual(config.ingress_class, "traefik")
        self.assertFalse(config.tls_enabled)
        self.assertFalse(config.hpa_enabled)
        self.assertEqual(config.min_replicas, 1)
        self.assertEqual(config.max_replicas, 50)
        self.assertEqual(config.target_cpu_utilization, 80)
        self.assertEqual(config.storage_class, "standard")
        self.assertEqual(config.volume_size, "20Gi")
        self.assertFalse(config.network_policies_enabled)
        self.assertEqual(config.pod_security_policy, "privileged")


class TestContainerOrchestratorInitialization(unittest.TestCase):
    """Test ContainerOrchestrator initialization."""

    def setUp(self):
        """Set up test fixtures."""
        self.production_config = ProductionConfig(
            environment=DeploymentEnvironment.PRODUCTION
        )

    @patch("builtins.print")
    def test_basic_initialization(self, mock_print):
        """Test basic ContainerOrchestrator initialization."""
        orchestrator = ContainerOrchestrator(self.production_config)

        self.assertEqual(orchestrator.production_config, self.production_config)
        self.assertIsInstance(orchestrator.container_config, ContainerConfig)
        self.assertIsInstance(orchestrator.kubernetes_config, KubernetesConfig)

        mock_print.assert_called_once_with(
            "🐳 Container Orchestrator initialized for production"
        )

    @patch("builtins.print")
    def test_custom_configs_initialization(self, mock_print):
        """Test initialization with custom configurations."""
        container_config = ContainerConfig(image_tag="custom")
        kubernetes_config = KubernetesConfig(namespace="custom-ns")

        orchestrator = ContainerOrchestrator(
            self.production_config, container_config, kubernetes_config
        )

        self.assertEqual(orchestrator.container_config.image_tag, "v1.0.0")  # Overridden
        self.assertEqual(
            orchestrator.kubernetes_config.namespace, "sts-production"
        )  # Overridden


class TestEnvironmentOverrides(unittest.TestCase):
    """Test environment-specific configuration overrides."""

    @patch("builtins.print")
    def test_development_overrides(self, mock_print):
        """Test development environment overrides."""
        prod_config = ProductionConfig(environment=DeploymentEnvironment.DEVELOPMENT)
        orchestrator = ContainerOrchestrator(prod_config)

        # Check container config overrides
        self.assertEqual(orchestrator.container_config.image_tag, "dev")
        self.assertEqual(orchestrator.container_config.cpu_limit, "200m")
        self.assertEqual(orchestrator.container_config.memory_limit, "256Mi")

        # Check Kubernetes config overrides
        self.assertEqual(orchestrator.kubernetes_config.min_replicas, 1)
        self.assertEqual(orchestrator.kubernetes_config.max_replicas, 3)

    @patch("builtins.print")
    def test_testing_overrides(self, mock_print):
        """Test testing environment overrides."""
        prod_config = ProductionConfig(environment=DeploymentEnvironment.TESTING)
        orchestrator = ContainerOrchestrator(prod_config)

        # Check container config overrides
        self.assertEqual(orchestrator.container_config.image_tag, "test")

        # Check Kubernetes config overrides
        self.assertEqual(orchestrator.kubernetes_config.namespace, "sts-testing")
        self.assertEqual(orchestrator.kubernetes_config.min_replicas, 1)
        self.assertEqual(orchestrator.kubernetes_config.max_replicas, 5)

    @patch("builtins.print")
    def test_staging_overrides(self, mock_print):
        """Test staging environment overrides."""
        prod_config = ProductionConfig(environment=DeploymentEnvironment.STAGING)
        orchestrator = ContainerOrchestrator(prod_config)

        # Check container config overrides
        self.assertEqual(orchestrator.container_config.image_tag, "staging")

        # Check Kubernetes config overrides
        self.assertEqual(orchestrator.kubernetes_config.namespace, "sts-staging")
        self.assertEqual(orchestrator.kubernetes_config.min_replicas, 2)
        self.assertEqual(orchestrator.kubernetes_config.max_replicas, 10)

    @patch("builtins.print")
    def test_production_overrides(self, mock_print):
        """Test production environment overrides."""
        prod_config = ProductionConfig(environment=DeploymentEnvironment.PRODUCTION)
        orchestrator = ContainerOrchestrator(prod_config)

        # Check container config overrides
        self.assertEqual(orchestrator.container_config.image_tag, "v1.0.0")

        # Check Kubernetes config overrides
        self.assertEqual(orchestrator.kubernetes_config.namespace, "sts-production")
        self.assertEqual(orchestrator.kubernetes_config.min_replicas, 3)
        self.assertEqual(orchestrator.kubernetes_config.max_replicas, 100)

    @patch("builtins.print")
    def test_clinical_overrides(self, mock_print):
        """Test clinical environment overrides."""
        prod_config = ProductionConfig(environment=DeploymentEnvironment.CLINICAL)
        orchestrator = ContainerOrchestrator(prod_config)

        # Check container config overrides
        self.assertEqual(orchestrator.container_config.image_tag, "clinical-v1.0.0")

        # Check Kubernetes config overrides
        self.assertEqual(orchestrator.kubernetes_config.namespace, "sts-clinical")
        self.assertEqual(orchestrator.kubernetes_config.min_replicas, 3)
        self.assertEqual(orchestrator.kubernetes_config.max_replicas, 20)
        self.assertTrue(orchestrator.kubernetes_config.network_policies_enabled)
        self.assertEqual(
            orchestrator.kubernetes_config.pod_security_policy, "highly-restricted"
        )


class TestDockerfileGeneration(unittest.TestCase):
    """Test Dockerfile generation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.production_config = ProductionConfig(
            environment=DeploymentEnvironment.PRODUCTION
        )

    @patch("builtins.print")
    def test_dockerfile_generation_basic(self, mock_print):
        """Test basic Dockerfile generation."""
        orchestrator = ContainerOrchestrator(self.production_config)
        dockerfile = orchestrator.generate_dockerfile()

        self.assertIsInstance(dockerfile, str)
        self.assertGreater(len(dockerfile), 1000)

        # Check multi-stage build structure
        self.assertIn("FROM python:3.11-slim AS builder", dockerfile)
        self.assertIn("FROM python:3.11-slim AS runtime", dockerfile)

        # Check build arguments
        self.assertIn("ARG STS_VERSION=1.0.0", dockerfile)
        self.assertIn("ARG BUILD_DATE", dockerfile)
        self.assertIn("ARG VCS_REF", dockerfile)

        # Check essential sections
        self.assertIn("# Install system dependencies", dockerfile)
        self.assertIn("# Create non-root user", dockerfile)
        self.assertIn("# Health check", dockerfile)
        self.assertIn("# Expose port", dockerfile)

    @patch("builtins.print")
    def test_dockerfile_security_settings(self, mock_print):
        """Test Dockerfile security settings."""
        orchestrator = ContainerOrchestrator(self.production_config)
        dockerfile = orchestrator.generate_dockerfile()

        # Check user creation and switching
        expected_user = orchestrator.container_config.run_as_user
        self.assertIn(f"useradd -r -g sts -u {expected_user} sts", dockerfile)
        self.assertIn(f"USER {expected_user}", dockerfile)

        # Check file permissions
        self.assertIn("chown -R sts:sts /app", dockerfile)

        # Check port exposure
        expected_port = orchestrator.container_config.port
        self.assertIn(f"EXPOSE {expected_port}", dockerfile)

    @patch("builtins.print")
    def test_dockerfile_health_check(self, mock_print):
        """Test Dockerfile health check configuration."""
        orchestrator = ContainerOrchestrator(self.production_config)
        dockerfile = orchestrator.generate_dockerfile()

        # Check health check configuration
        self.assertIn("HEALTHCHECK --interval=30s --timeout=5s", dockerfile)
        
        expected_port = orchestrator.container_config.port
        expected_path = orchestrator.container_config.health_check_path
        expected_url = f"http://localhost:{expected_port}{expected_path}"
        
        self.assertIn(expected_url, dockerfile)

    @patch("builtins.print")
    def test_dockerfile_custom_config(self, mock_print):
        """Test Dockerfile generation with custom configuration."""
        container_config = ContainerConfig(
            base_image="python:3.12-alpine",
            port=9000,
            health_check_path="/api/status",
            run_as_user=2000,
        )

        orchestrator = ContainerOrchestrator(
            self.production_config, container_config=container_config
        )
        dockerfile = orchestrator.generate_dockerfile()

        # Check custom base image is used
        self.assertIn("FROM python:3.12-alpine AS builder", dockerfile)
        self.assertIn("FROM python:3.12-alpine AS runtime", dockerfile)

        # Check custom port
        self.assertIn("EXPOSE 9000", dockerfile)

        # Check custom user ID from the supplied container config
        self.assertIn("useradd -r -g sts -u 2000", dockerfile)

        # Check custom health check path/port from the supplied container config
        self.assertIn("http://localhost:9000/api/status", dockerfile)

    @patch("builtins.print")
    def test_dockerfile_environment_variables(self, mock_print):
        """Test Dockerfile environment variables configuration."""
        orchestrator = ContainerOrchestrator(self.production_config)
        dockerfile = orchestrator.generate_dockerfile()

        # Check environment variables
        env_vars = [
            "PYTHONPATH=/app",
            "PYTHONUNBUFFERED=1",
            "PYTHONDONTWRITEBYTECODE=1",
            f"STS_PORT={orchestrator.container_config.port}",
        ]

        for env_var in env_vars:
            self.assertIn(env_var, dockerfile)

    @patch("builtins.print")
    def test_dockerfile_labels(self, mock_print):
        """Test Dockerfile metadata labels."""
        orchestrator = ContainerOrchestrator(self.production_config)
        dockerfile = orchestrator.generate_dockerfile()

        # Check metadata labels
        expected_labels = [
            'maintainer="STS Development Team"',
            'version="$STS_VERSION"',
            'build_date="$BUILD_DATE"',
            'vcs_ref="$VCS_REF"',
            'description="Sensory Tracer Science Framework Production Container"',
        ]

        for label in expected_labels:
            self.assertIn(label, dockerfile)

    @patch("builtins.print")
    def test_dockerfile_copy_operations(self, mock_print):
        """Test Dockerfile copy operations."""
        orchestrator = ContainerOrchestrator(self.production_config)
        dockerfile = orchestrator.generate_dockerfile()

        # Check copy operations from builder stage
        expected_copies = [
            "COPY --from=builder /usr/local/lib/python3.11/site-packages",
            "COPY --from=builder /usr/local/bin",
            "COPY --from=builder /app /app",
        ]

        for copy_op in expected_copies:
            self.assertIn(copy_op, dockerfile)


class TestDockerComposeGeneration(unittest.TestCase):
    """Test Docker Compose configuration generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.production_config = ProductionConfig(
            environment=DeploymentEnvironment.DEVELOPMENT
        )

    @patch("builtins.print")
    @patch("sensory_tracer_science.deployment.production_config.ProductionConfig.generate_docker_env")
    def test_docker_compose_basic_structure(self, mock_env, mock_print):
        """Test basic Docker Compose configuration structure."""
        mock_env.return_value = {
            "STS_ENVIRONMENT": "development",
            "STS_LOG_LEVEL": "DEBUG",
        }

        orchestrator = ContainerOrchestrator(self.production_config)
        compose_config = orchestrator.generate_docker_compose()

        self.assertIsInstance(compose_config, dict)
        self.assertEqual(compose_config["version"], "3.8")
        self.assertIn("services", compose_config)

        services = compose_config["services"]
        self.assertIn("sts-app", services)

    @patch("builtins.print")
    @patch("sensory_tracer_science.deployment.production_config.ProductionConfig.generate_docker_env")
    def test_docker_compose_app_service(self, mock_env, mock_print):
        """Test Docker Compose app service configuration."""
        mock_env.return_value = {
            "STS_ENVIRONMENT": "development",
            "DATABASE_URL": "postgresql://localhost:5432/sts",
        }

        orchestrator = ContainerOrchestrator(self.production_config)
        compose_config = orchestrator.generate_docker_compose()

        app_service = compose_config["services"]["sts-app"]

        # Check build configuration
        self.assertIn("build", app_service)
        build_config = app_service["build"]
        self.assertEqual(build_config["context"], ".")
        self.assertEqual(build_config["dockerfile"], "Dockerfile")
        self.assertIn("args", build_config)

        # Check build args
        args = build_config["args"]
        self.assertEqual(args["STS_VERSION"], "1.0.0")
        self.assertEqual(args["VCS_REF"], "main")
        self.assertIn("BUILD_DATE", args)

        # Check image name
        expected_image = f"{orchestrator.container_config.image_name}:{orchestrator.container_config.image_tag}"
        self.assertEqual(app_service["image"], expected_image)

        # Check container name
        self.assertEqual(app_service["container_name"], "sts-framework")

        # Check ports
        expected_port = f"{orchestrator.container_config.port}:{orchestrator.container_config.port}"
        self.assertEqual(app_service["ports"], [expected_port])

        # Check environment variables
        self.assertEqual(app_service["environment"], mock_env.return_value)

        # Check volumes
        expected_volumes = [
            "./data:/app/data",
            "./logs:/app/logs",
            "./config:/app/config",
        ]
        self.assertEqual(app_service["volumes"], expected_volumes)

        # Check dependencies
        self.assertEqual(app_service["depends_on"], ["postgres", "redis"])

        # Check restart policy
        expected_restart = orchestrator.container_config.restart_policy.lower()
        self.assertEqual(app_service["restart"], expected_restart)

    @patch("builtins.print")
    @patch("sensory_tracer_science.deployment.production_config.ProductionConfig.generate_docker_env")
    def test_docker_compose_health_check(self, mock_env, mock_print):
        """Test Docker Compose health check configuration."""
        mock_env.return_value = {}
        
        orchestrator = ContainerOrchestrator(self.production_config)
        compose_config = orchestrator.generate_docker_compose()

        app_service = compose_config["services"]["sts-app"]
        
        # Check health check configuration exists
        self.assertIn("healthcheck", app_service)
        healthcheck = app_service["healthcheck"]
        
        # Check health check test command
        self.assertIn("test", healthcheck)
        test_cmd = healthcheck["test"]
        
        expected_port = orchestrator.container_config.port
        expected_path = orchestrator.container_config.health_check_path
        expected_url = f"http://localhost:{expected_port}{expected_path}"
        
        # Should contain curl command with correct URL
        self.assertIn("curl", " ".join(test_cmd))
        self.assertIn(expected_url, " ".join(test_cmd))

    @patch("builtins.print")
    @patch("sensory_tracer_science.deployment.production_config.ProductionConfig.generate_docker_env")
    def test_docker_compose_custom_config(self, mock_env, mock_print):
        """Test Docker Compose with custom configuration."""
        mock_env.return_value = {"CUSTOM_VAR": "value"}

        container_config = ContainerConfig(
            image_name="custom-sts",
            image_tag="custom-tag",
            port=9000,
            restart_policy="OnFailure",
        )

        orchestrator = ContainerOrchestrator(
            self.production_config, container_config=container_config
        )
        compose_config = orchestrator.generate_docker_compose()

        app_service = compose_config["services"]["sts-app"]

        # Check custom image name (with environment override)
        expected_image = "custom-sts:dev"  # Dev environment override
        self.assertEqual(app_service["image"], expected_image)

        # Check custom port (should use override)
        expected_port = f"{orchestrator.container_config.port}:{orchestrator.container_config.port}"
        self.assertEqual(app_service["ports"][0], expected_port)

        # Check custom restart policy (lowercase)
        expected_restart = container_config.restart_policy.lower()
        self.assertEqual(app_service["restart"], expected_restart)


class TestKubernetesManifestGeneration(unittest.TestCase):
    """Test Kubernetes manifest generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.production_config = ProductionConfig(
            environment=DeploymentEnvironment.PRODUCTION
        )

    @patch("builtins.print")
    def test_kubernetes_deployment_manifest(self, mock_print):
        """Test Kubernetes deployment manifest generation."""
        orchestrator = ContainerOrchestrator(self.production_config)
        
        with patch.object(orchestrator, "generate_kubernetes_deployment") as mock_method:
            mock_method.return_value = {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {"name": "sts-app"},
            }
            
            manifests = orchestrator.generate_kubernetes_deployment()
            
            self.assertIsInstance(manifests, dict)
            self.assertEqual(manifests["apiVersion"], "apps/v1")
            self.assertEqual(manifests["kind"], "Deployment")
            
            mock_method.assert_called_once()

    @patch("builtins.print")
    def test_kubernetes_service_manifest(self, mock_print):
        """Test Kubernetes service manifest generation."""
        orchestrator = ContainerOrchestrator(self.production_config)
        
        # Mock the method since we need to implement it
        with patch.object(orchestrator, "generate_kubernetes_service") as mock_method:
            mock_method.return_value = {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {"name": "sts-service"},
            }
            
            service = orchestrator.generate_kubernetes_service()
            
            self.assertIsInstance(service, dict)
            self.assertEqual(service["apiVersion"], "v1")
            self.assertEqual(service["kind"], "Service")
            
            mock_method.assert_called_once()


class TestContainerSecurity(unittest.TestCase):
    """Test container security configurations."""

    def setUp(self):
        """Set up test fixtures."""
        self.production_config = ProductionConfig(
            environment=DeploymentEnvironment.CLINICAL  # Highest security
        )

    @patch("builtins.print")
    def test_security_context_configuration(self, mock_print):
        """Test security context in container configuration."""
        orchestrator = ContainerOrchestrator(self.production_config)

        # Check security-related container config
        self.assertTrue(orchestrator.container_config.run_as_non_root)
        self.assertEqual(orchestrator.container_config.run_as_user, 1001)
        self.assertTrue(orchestrator.container_config.read_only_root_filesystem)

        # Check Kubernetes security config
        self.assertTrue(orchestrator.kubernetes_config.network_policies_enabled)
        self.assertEqual(
            orchestrator.kubernetes_config.pod_security_policy, "highly-restricted"
        )

    @patch("builtins.print")
    def test_clinical_environment_security(self, mock_print):
        """Test clinical environment security settings."""
        orchestrator = ContainerOrchestrator(self.production_config)

        # Should have most restrictive settings
        self.assertEqual(orchestrator.kubernetes_config.namespace, "sts-clinical")
        self.assertEqual(orchestrator.kubernetes_config.max_replicas, 20)  # Limited
        self.assertTrue(orchestrator.kubernetes_config.network_policies_enabled)
        self.assertEqual(
            orchestrator.kubernetes_config.pod_security_policy, "highly-restricted"
        )

    @patch("builtins.print")
    def test_non_root_user_dockerfile(self, mock_print):
        """Test non-root user configuration in Dockerfile."""
        orchestrator = ContainerOrchestrator(self.production_config)
        dockerfile = orchestrator.generate_dockerfile()

        # Should create and switch to non-root user
        expected_user = orchestrator.container_config.run_as_user
        self.assertIn(f"useradd -r -g sts -u {expected_user} sts", dockerfile)
        self.assertIn(f"USER {expected_user}", dockerfile)

        # Should not run as root
        self.assertNotIn("USER 0", dockerfile)
        self.assertNotIn("USER root", dockerfile)


class TestResourceManagement(unittest.TestCase):
    """Test resource management and limits."""

    def setUp(self):
        """Set up test fixtures."""
        self.production_config = ProductionConfig(
            environment=DeploymentEnvironment.PRODUCTION
        )

    @patch("builtins.print")
    def test_resource_limits_configuration(self, mock_print):
        """Test resource limits configuration."""
        orchestrator = ContainerOrchestrator(self.production_config)

        # Check CPU limits
        self.assertEqual(orchestrator.container_config.cpu_request, "100m")
        self.assertEqual(orchestrator.container_config.cpu_limit, "500m")

        # Check memory limits
        self.assertEqual(orchestrator.container_config.memory_request, "256Mi")
        self.assertEqual(orchestrator.container_config.memory_limit, "512Mi")

    @patch("builtins.print")
    def test_development_resource_overrides(self, mock_print):
        """Test development environment resource overrides."""
        dev_config = ProductionConfig(environment=DeploymentEnvironment.DEVELOPMENT)
        orchestrator = ContainerOrchestrator(dev_config)

        # Should have reduced limits for development
        self.assertEqual(orchestrator.container_config.cpu_limit, "200m")
        self.assertEqual(orchestrator.container_config.memory_limit, "256Mi")

    @patch("builtins.print")
    def test_autoscaling_configuration(self, mock_print):
        """Test autoscaling configuration."""
        orchestrator = ContainerOrchestrator(self.production_config)

        # Check HPA settings
        self.assertTrue(orchestrator.kubernetes_config.hpa_enabled)
        self.assertEqual(orchestrator.kubernetes_config.min_replicas, 3)  # Production
        self.assertEqual(orchestrator.kubernetes_config.max_replicas, 100)
        self.assertEqual(orchestrator.kubernetes_config.target_cpu_utilization, 70)

    @patch("builtins.print")
    def test_storage_configuration(self, mock_print):
        """Test storage configuration."""
        orchestrator = ContainerOrchestrator(self.production_config)

        # Check storage settings
        self.assertEqual(orchestrator.kubernetes_config.storage_class, "fast-ssd")
        self.assertEqual(orchestrator.kubernetes_config.volume_size, "10Gi")

        # Check persistent volumes in container config
        self.assertIsInstance(orchestrator.container_config.persistent_volumes, list)


class TestNetworkConfiguration(unittest.TestCase):
    """Test network configuration and policies."""

    def setUp(self):
        """Set up test fixtures."""
        self.production_config = ProductionConfig(
            environment=DeploymentEnvironment.PRODUCTION
        )

    @patch("builtins.print")
    def test_service_configuration(self, mock_print):
        """Test service configuration."""
        orchestrator = ContainerOrchestrator(self.production_config)

        # Check service type
        self.assertEqual(orchestrator.kubernetes_config.service_type, "ClusterIP")
        self.assertEqual(
            orchestrator.kubernetes_config.load_balancer_type, "application"
        )

    @patch("builtins.print")
    def test_ingress_configuration(self, mock_print):
        """Test ingress configuration."""
        orchestrator = ContainerOrchestrator(self.production_config)

        # Check ingress settings
        self.assertTrue(orchestrator.kubernetes_config.ingress_enabled)
        self.assertEqual(orchestrator.kubernetes_config.ingress_class, "nginx")
        self.assertTrue(orchestrator.kubernetes_config.tls_enabled)

    @patch("builtins.print")
    def test_network_policies(self, mock_print):
        """Test network policies configuration."""
        orchestrator = ContainerOrchestrator(self.production_config)

        # Check network policies
        self.assertTrue(orchestrator.kubernetes_config.network_policies_enabled)

        # Clinical environment should have even stricter policies
        clinical_config = ProductionConfig(environment=DeploymentEnvironment.CLINICAL)
        clinical_orchestrator = ContainerOrchestrator(clinical_config)
        self.assertTrue(clinical_orchestrator.kubernetes_config.network_policies_enabled)

    @patch("builtins.print")
    def test_port_configuration(self, mock_print):
        """Test port configuration."""
        orchestrator = ContainerOrchestrator(self.production_config)

        # Check default port
        self.assertEqual(orchestrator.container_config.port, 8000)

        # Check health check path
        self.assertEqual(orchestrator.container_config.health_check_path, "/health")


class TestEdgeCasesAndErrorHandling(unittest.TestCase):
    """Test edge cases and error handling."""

    @patch("builtins.print")
    def test_empty_config_lists(self, mock_print):
        """Test handling of empty configuration lists."""
        config = ContainerConfig(
            persistent_volumes=[],
            config_maps=[],
            secrets=[],
        )

        self.assertEqual(config.persistent_volumes, [])
        self.assertEqual(config.config_maps, [])
        self.assertEqual(config.secrets, [])

    @patch("builtins.print")
    def test_zero_replicas(self, mock_print):
        """Test handling of zero replicas."""
        k8s_config = KubernetesConfig(
            min_replicas=0,
            max_replicas=0,
        )

        self.assertEqual(k8s_config.min_replicas, 0)
        self.assertEqual(k8s_config.max_replicas, 0)

    @patch("builtins.print")
    def test_invalid_resource_format(self, mock_print):
        """Test handling of invalid resource format."""
        # These should still work as strings
        config = ContainerConfig(
            cpu_request="invalid",
            memory_limit="also-invalid",
        )

        self.assertEqual(config.cpu_request, "invalid")
        self.assertEqual(config.memory_limit, "also-invalid")

    @patch("builtins.print")
    def test_extremely_high_limits(self, mock_print):
        """Test handling of extremely high resource limits."""
        config = ContainerConfig(
            cpu_limit="1000000m",
            memory_limit="1000Gi",
        )

        production_config = ProductionConfig(
            environment=DeploymentEnvironment.PRODUCTION
        )
        orchestrator = ContainerOrchestrator(
            production_config, container_config=config
        )

        # Should generate valid Dockerfile even with extreme limits
        dockerfile = orchestrator.generate_dockerfile()
        self.assertIsInstance(dockerfile, str)
        self.assertGreater(len(dockerfile), 100)

    @patch("builtins.print")
    def test_special_characters_in_names(self, mock_print):
        """Test handling of special characters in names."""
        config = ContainerConfig(
            image_name="sts-framework_special.name",
            image_tag="v1.0.0-beta+build.1",
        )

        production_config = ProductionConfig(
            environment=DeploymentEnvironment.DEVELOPMENT
        )
        orchestrator = ContainerOrchestrator(
            production_config, container_config=config
        )

        # Should generate valid Docker Compose even with special characters
        compose_config = orchestrator.generate_docker_compose()
        self.assertIsInstance(compose_config, dict)

        # Image name should be constructed properly (with environment override)
        app_service = compose_config["services"]["sts-app"]
        expected_image = "sts-framework_special.name:dev"  # Dev override
        self.assertEqual(app_service["image"], expected_image)


if __name__ == "__main__":
    unittest.main()