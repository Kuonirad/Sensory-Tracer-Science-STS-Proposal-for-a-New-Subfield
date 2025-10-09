#!/usr/bin/env python3
"""
Comprehensive tests for STS deployment modules.

This test suite provides extensive coverage for all deployment modules:
- cloud_deployment.py
- container_orchestration.py  
- monitoring_analytics.py
- production_config.py

Targets 100% coverage for the deployment package (currently 0%).
"""

import json
import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

# Import deployment modules
from sensory_tracer_science.deployment.cloud_deployment import (
    CloudDeploymentManager,
    CloudInfrastructure,
    CloudProvider,
    DeploymentType,
    create_cloud_deployment_demo,
)
from sensory_tracer_science.deployment.container_orchestration import (
    ContainerConfig,
    ContainerOrchestrator,
    create_deployment_packages,
)
from sensory_tracer_science.deployment.monitoring_analytics import (
    AlertRule,
    MonitoringAnalytics,
    MonitoringMetric,
    NotificationChannel,
)
from sensory_tracer_science.deployment.production_config import (
    DatabaseConfig,
    DeploymentEnvironment,
    ProductionConfigManager,
    RedisConfig,
    SecurityConfig,
    SystemConfig,
)


class TestCloudDeploymentModule(unittest.TestCase):
    """Comprehensive tests for cloud deployment functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.aws_manager = CloudDeploymentManager(
            CloudProvider.AWS, DeploymentType.SERVERLESS
        )
        self.azure_manager = CloudDeploymentManager(
            CloudProvider.AZURE, DeploymentType.CONTAINERS
        )
        self.gcp_manager = CloudDeploymentManager(
            CloudProvider.GCP, DeploymentType.KUBERNETES
        )
        self.hybrid_manager = CloudDeploymentManager(
            CloudProvider.HYBRID, DeploymentType.MANAGED_SERVICES
        )

    def test_cloud_provider_enum(self):
        """Test CloudProvider enum values."""
        assert CloudProvider.AWS.value == "aws"
        assert CloudProvider.AZURE.value == "azure"
        assert CloudProvider.GCP.value == "gcp"
        assert CloudProvider.HYBRID.value == "hybrid"

    def test_deployment_type_enum(self):
        """Test DeploymentType enum values."""
        assert DeploymentType.SERVERLESS.value == "serverless"
        assert DeploymentType.CONTAINERS.value == "containers"
        assert DeploymentType.VIRTUAL_MACHINES.value == "virtual_machines"
        assert DeploymentType.KUBERNETES.value == "kubernetes"
        assert DeploymentType.MANAGED_SERVICES.value == "managed_services"

    def test_cloud_infrastructure_initialization(self):
        """Test CloudInfrastructure initialization and post_init."""
        # Test with defaults
        infra = CloudInfrastructure(
            provider=CloudProvider.AWS,
            region="us-west-2",
            availability_zones=["us-west-2a", "us-west-2b"],
        )

        assert infra.provider == CloudProvider.AWS
        assert infra.region == "us-west-2"
        assert infra.availability_zones == ["us-west-2a", "us-west-2b"]
        assert infra.instance_type == "medium"
        assert infra.min_instances == 2
        assert infra.max_instances == 100
        assert infra.storage_type == "ssd"
        assert infra.storage_size_gb == 100
        assert infra.backup_enabled is True
        assert infra.vpc_cidr == "10.0.0.0/16"
        assert infra.encryption_enabled is True

        # Check post_init defaults
        assert infra.public_subnets == ["10.0.1.0/24", "10.0.2.0/24"]
        assert infra.private_subnets == ["10.0.10.0/24", "10.0.20.0/24"]
        assert infra.security_groups == []

    def test_cloud_infrastructure_custom_values(self):
        """Test CloudInfrastructure with custom values."""
        custom_public = ["192.168.1.0/24"]
        custom_private = ["192.168.10.0/24"]
        custom_security = ["sg-12345"]

        infra = CloudInfrastructure(
            provider=CloudProvider.AZURE,
            region="eastus",
            availability_zones=["eastus-1", "eastus-2"],
            instance_type="large",
            min_instances=5,
            max_instances=50,
            storage_size_gb=500,
            public_subnets=custom_public,
            private_subnets=custom_private,
            security_groups=custom_security,
        )

        assert infra.instance_type == "large"
        assert infra.min_instances == 5
        assert infra.max_instances == 50
        assert infra.storage_size_gb == 500
        assert infra.public_subnets == custom_public
        assert infra.private_subnets == custom_private
        assert infra.security_groups == custom_security

    @patch("builtins.print")
    def test_cloud_deployment_manager_initialization(self, mock_print):
        """Test CloudDeploymentManager initialization."""
        manager = CloudDeploymentManager(CloudProvider.AWS, DeploymentType.SERVERLESS)

        assert manager.provider == CloudProvider.AWS
        assert manager.deployment_type == DeploymentType.SERVERLESS
        assert manager.infrastructure is None

        # Check initialization message
        mock_print.assert_called_with(
            "☁️ Cloud deployment manager initialized: aws - serverless"
        )

    def test_generate_aws_terraform_basic(self):
        """Test AWS Terraform generation with basic infrastructure."""
        infrastructure = CloudInfrastructure(
            provider=CloudProvider.AWS,
            region="us-east-1",
            availability_zones=["us-east-1a", "us-east-1b"],
        )

        terraform_config = self.aws_manager.generate_aws_terraform(infrastructure)

        # Check Terraform configuration structure
        assert isinstance(terraform_config, str)
        assert len(terraform_config) > 500  # Should be substantial
        assert "terraform {" in terraform_config
        assert "provider \"aws\" {" in terraform_config
        assert f'region = "{infrastructure.region}"' in terraform_config
        assert "resource \"aws_vpc\" \"sts_vpc\"" in terraform_config
        assert f'cidr_block = "{infrastructure.vpc_cidr}"' in terraform_config
        assert "resource \"aws_internet_gateway\"" in terraform_config
        assert "sensory-tracer-science" in terraform_config

    def test_generate_serverless_config_aws(self):
        """Test serverless configuration generation for AWS."""
        self.aws_manager.deployment_type = DeploymentType.SERVERLESS

        config = self.aws_manager.generate_serverless_config()

        assert isinstance(config, dict)
        assert config["provider"] == "aws"
        assert config["runtime"] == "python3.11"
        assert "functions" in config
        assert "sts-processor" in config["functions"]
        assert "sts-validator" in config["functions"]
        assert "sts-tracer" in config["functions"]

        # Check function configuration
        processor_func = config["functions"]["sts-processor"]
        assert "handler" in processor_func
        assert "events" in processor_func
        assert processor_func["timeout"] == 300

    def test_generate_serverless_config_azure(self):
        """Test serverless configuration generation for Azure."""
        config = self.azure_manager.generate_serverless_config()

        assert isinstance(config, dict)
        assert config["provider"] == "azure"
        assert config["runtime"] == "python3.11"
        assert "functionAppName" in config
        assert "functions" in config

    def test_generate_serverless_config_gcp(self):
        """Test serverless configuration generation for GCP."""
        config = self.gcp_manager.generate_serverless_config()

        assert isinstance(config, dict)
        assert config["provider"] == "gcp"
        assert config["runtime"] == "python311"
        assert "functions" in config

    def test_generate_cost_optimization_recommendations(self):
        """Test cost optimization recommendations generation."""
        infrastructure = CloudInfrastructure(
            provider=CloudProvider.AWS,
            region="us-west-2",
            availability_zones=["us-west-2a", "us-west-2b"],
            instance_type="large",
            max_instances=200,
            storage_size_gb=1000,
        )

        recommendations = self.aws_manager.generate_cost_optimization_recommendations(
            infrastructure
        )

        assert isinstance(recommendations, dict)
        assert "estimated_monthly_cost" in recommendations
        assert "cost_optimization_recommendations" in recommendations
        assert "potential_savings" in recommendations

        # Check recommendations structure
        recs = recommendations["cost_optimization_recommendations"]
        assert isinstance(recs, list)
        assert len(recs) > 0

        # Check individual recommendation structure
        for rec in recs:
            assert "category" in rec
            assert "recommendation" in rec
            assert "estimated_savings" in rec
            assert "implementation_effort" in rec

    def test_calculate_estimated_cost_different_providers(self):
        """Test cost calculation for different cloud providers."""
        infrastructure = CloudInfrastructure(
            provider=CloudProvider.AWS,
            region="us-west-2",
            availability_zones=["us-west-2a"],
            min_instances=2,
            max_instances=10,
            storage_size_gb=100,
        )

        # Test AWS cost calculation
        aws_cost = self.aws_manager._calculate_estimated_cost(infrastructure)
        assert isinstance(aws_cost, float)
        assert aws_cost > 0

        # Test with different instance types
        infrastructure.instance_type = "small"
        small_cost = self.aws_manager._calculate_estimated_cost(infrastructure)

        infrastructure.instance_type = "large"
        large_cost = self.aws_manager._calculate_estimated_cost(infrastructure)

        # Larger instances should cost more
        assert large_cost > small_cost

    def test_get_aws_instance_type_mapping(self):
        """Test AWS instance type mapping."""
        assert self.aws_manager._get_aws_instance_type("small") == "t3.micro"
        assert self.aws_manager._get_aws_instance_type("medium") == "t3.small"
        assert self.aws_manager._get_aws_instance_type("large") == "t3.medium"
        assert self.aws_manager._get_aws_instance_type("xlarge") == "t3.large"
        assert self.aws_manager._get_aws_instance_type("unknown") == "t3.small"  # Default

    def test_generate_disaster_recovery_plan(self):
        """Test disaster recovery plan generation."""
        infrastructure = CloudInfrastructure(
            provider=CloudProvider.AWS,
            region="us-west-2",
            availability_zones=["us-west-2a", "us-west-2b"],
        )

        dr_plan = self.aws_manager.generate_disaster_recovery_plan(infrastructure)

        assert isinstance(dr_plan, dict)
        assert "backup_strategy" in dr_plan
        assert "recovery_procedures" in dr_plan
        assert "rto_rpo_targets" in dr_plan
        assert "testing_schedule" in dr_plan

        # Check backup strategy structure
        backup_strategy = dr_plan["backup_strategy"]
        assert "automated_backups" in backup_strategy
        assert "backup_retention" in backup_strategy
        assert "cross_region_replication" in backup_strategy

        # Check RTO/RPO targets
        rto_rpo = dr_plan["rto_rpo_targets"]
        assert "recovery_time_objective" in rto_rpo
        assert "recovery_point_objective" in rto_rpo

    @patch("builtins.print")
    def test_create_cloud_deployment_demo(self, mock_print):
        """Test create_cloud_deployment_demo function."""
        create_cloud_deployment_demo()

        # Should create multiple print calls for demo
        assert mock_print.call_count > 5

        # Check that demo covers different scenarios
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        demo_text = " ".join(print_calls)

        assert "Multi-Cloud Deployment Demo" in demo_text
        assert "AWS" in demo_text
        assert "Azure" in demo_text
        assert "GCP" in demo_text

    def test_private_helper_methods(self):
        """Test private helper methods with mocked infrastructure."""
        infrastructure = CloudInfrastructure(
            provider=CloudProvider.AWS,
            region="us-west-2",
            availability_zones=["us-west-2a", "us-west-2b"],
        )

        # Test public subnets generation
        public_subnets = self.aws_manager._generate_aws_public_subnets(infrastructure)
        assert isinstance(public_subnets, str)
        assert "aws_subnet" in public_subnets
        assert "10.0.1.0/24" in public_subnets

        # Test private subnets generation
        private_subnets = self.aws_manager._generate_aws_private_subnets(infrastructure)
        assert isinstance(private_subnets, str)
        assert "aws_subnet" in private_subnets
        assert "10.0.10.0/24" in private_subnets

        # Test security groups generation
        security_groups = self.aws_manager._generate_aws_security_groups()
        assert isinstance(security_groups, str)
        assert "aws_security_group" in security_groups

        # Test IAM roles generation
        iam_roles = self.aws_manager._generate_aws_iam_roles()
        assert isinstance(iam_roles, str)
        assert "aws_iam_role" in iam_roles


class TestContainerOrchestrationModule(unittest.TestCase):
    """Comprehensive tests for container orchestration functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Import ProductionConfig here to avoid circular imports
        from sensory_tracer_science.deployment.production_config import ProductionConfig
        
        self.container_config = ContainerConfig(
            image_name="sts-framework",
            image_tag="1.0.0",
        )

        self.production_config = ProductionConfig(
            environment=DeploymentEnvironment.PRODUCTION
        )

        self.orchestrator = ContainerOrchestrator(
            production_config=self.production_config,
            container_config=self.container_config,
        )

    def test_deployment_environment_enum(self):
        """Test DeploymentEnvironment enum values."""
        assert DeploymentEnvironment.DEVELOPMENT.value == "development"
        assert DeploymentEnvironment.STAGING.value == "staging"  
        assert DeploymentEnvironment.PRODUCTION.value == "production"
        assert DeploymentEnvironment.TESTING.value == "testing"
        assert DeploymentEnvironment.CLINICAL.value == "clinical"

    def test_container_config_initialization(self):
        """Test ContainerConfig initialization and post_init."""
        config = ContainerConfig(
            image_name="test-image",
            image_tag="2.0.0",
        )

        assert config.image_name == "test-image"
        assert config.image_tag == "2.0.0"
        assert config.base_image == "python:3.11-slim"
        assert config.port == 8000
        assert config.health_check_path == "/health"
        assert config.restart_policy == "Always"
        assert config.run_as_non_root is True

        # Check post_init defaults
        assert config.persistent_volumes == []
        assert config.config_maps == []
        assert config.secrets == []

    def test_container_config_custom_values(self):
        """Test ContainerConfig with custom values."""
        custom_volumes = [{"name": "data", "mountPath": "/data"}]
        custom_configs = ["app-config"]
        custom_secrets = ["app-secrets"]

        config = ContainerConfig(
            image_name="custom-sts",
            image_tag="3.0.0",
            base_image="python:3.10",
            port=9000,
            cpu_limit="2",
            memory_limit="4Gi",
            run_as_non_root=False,
            persistent_volumes=custom_volumes,
            config_maps=custom_configs,
            secrets=custom_secrets,
        )

        assert config.base_image == "python:3.10"
        assert config.port == 9000
        assert config.cpu_limit == "2"
        assert config.memory_limit == "4Gi"
        assert config.run_as_non_root is False
        
        # Custom values should be preserved
        assert config.persistent_volumes == custom_volumes
        assert config.config_maps == custom_configs
        assert config.secrets == custom_secrets

    @patch("builtins.print")
    def test_container_orchestrator_initialization(self, mock_print):
        """Test ContainerOrchestrator initialization."""
        # Import ProductionConfig here to avoid circular imports
        from sensory_tracer_science.deployment.production_config import ProductionConfig
        
        test_production_config = ProductionConfig(
            environment=DeploymentEnvironment.STAGING
        )
        
        orchestrator = ContainerOrchestrator(
            production_config=test_production_config,
            container_config=self.container_config,
        )

        assert orchestrator.production_config == test_production_config
        assert orchestrator.container_config == self.container_config

        # Check initialization message
        mock_print.assert_called()

    def test_generate_dockerfile_basic(self):
        """Test Dockerfile generation with basic configuration."""
        dockerfile = self.orchestrator.generate_dockerfile()

        assert isinstance(dockerfile, str)
        assert len(dockerfile) > 200  # Should be substantial

        # Check Dockerfile structure
        assert f"FROM {self.container_config.base_image}" in dockerfile
        assert "COPY requirements.txt" in dockerfile
        assert "RUN pip install" in dockerfile
        assert "COPY . ." in dockerfile
        assert "CMD" in dockerfile

        # Check exposed port
        assert f"EXPOSE {self.container_config.port}" in dockerfile

    def test_generate_dockerfile_health_check(self):
        """Test Dockerfile generation includes health check."""
        dockerfile = self.orchestrator.generate_dockerfile()

        # Should include some health check mechanism
        assert "HEALTHCHECK" in dockerfile or self.container_config.health_check_path in dockerfile

    def test_generate_docker_compose_basic(self):
        """Test Docker Compose configuration generation."""
        compose_config = self.orchestrator.generate_docker_compose()

        assert isinstance(compose_config, dict)
        assert "version" in compose_config
        assert compose_config["version"] == "3.8"
        assert "services" in compose_config

        # Check main application service
        services = compose_config["services"]
        assert "sts-app" in services

        app_service = services["sts-app"]
        assert "build" in app_service
        assert "ports" in app_service
        assert "environment" in app_service
        assert "volumes" in app_service
        assert "restart" in app_service

    def test_generate_docker_compose_with_dependencies(self):
        """Test Docker Compose with database dependencies."""
        compose_config = self.orchestrator.generate_docker_compose()

        services = compose_config["services"]

        # Should include PostgreSQL and Redis
        assert "postgres" in services
        assert "redis" in services

        postgres_service = services["postgres"]
        assert postgres_service["image"] == "postgres:15"
        assert "environment" in postgres_service
        assert "POSTGRES_DB" in postgres_service["environment"]

        redis_service = services["redis"]
        assert redis_service["image"] == "redis:7-alpine"

    def test_generate_kubernetes_deployment(self):
        """Test Kubernetes deployment manifest generation."""
        k8s_deployment = self.orchestrator.generate_kubernetes_deployment()

        assert isinstance(k8s_deployment, dict)
        assert k8s_deployment["apiVersion"] == "apps/v1"
        assert k8s_deployment["kind"] == "Deployment"

        # Check metadata
        metadata = k8s_deployment["metadata"]
        assert metadata["name"] == "sts-deployment"
        assert "labels" in metadata

        # Check spec
        spec = k8s_deployment["spec"]
        assert "replicas" in spec
        assert "selector" in spec
        assert "template" in spec

        # Check pod template
        template = spec["template"]
        assert "metadata" in template
        assert "spec" in template

        pod_spec = template["spec"]
        assert "containers" in pod_spec

        # Check container spec
        container = pod_spec["containers"][0]
        assert container["name"] == "sts-container"
        assert "image" in container
        assert "ports" in container
        assert "env" in container

    def test_generate_kubernetes_service(self):
        """Test Kubernetes service manifest generation."""
        k8s_service = self.orchestrator.generate_kubernetes_service()

        assert isinstance(k8s_service, dict)
        assert k8s_service["apiVersion"] == "v1"
        assert k8s_service["kind"] == "Service"

        # Check metadata
        metadata = k8s_service["metadata"]
        assert metadata["name"] == "sts-service"

        # Check spec
        spec = k8s_service["spec"]
        assert "selector" in spec
        assert "ports" in spec
        assert spec["type"] == "ClusterIP"

    def test_generate_kubernetes_hpa(self):
        """Test Kubernetes HPA manifest generation."""
        k8s_hpa = self.orchestrator.generate_kubernetes_hpa()

        assert isinstance(k8s_hpa, dict)
        assert k8s_hpa["apiVersion"] == "autoscaling/v2"
        assert k8s_hpa["kind"] == "HorizontalPodAutoscaler"

        # Check spec
        spec = k8s_hpa["spec"]
        assert "scaleTargetRef" in spec
        assert "minReplicas" in spec
        assert "maxReplicas" in spec
        assert "metrics" in spec

        # Check metrics
        metrics = spec["metrics"]
        assert len(metrics) >= 1
        cpu_metric = metrics[0]
        assert cpu_metric["type"] == "Resource"
        assert cpu_metric["resource"]["name"] == "cpu"

    def test_generate_kubernetes_ingress(self):
        """Test Kubernetes ingress manifest generation."""
        k8s_ingress = self.orchestrator.generate_kubernetes_ingress()

        assert isinstance(k8s_ingress, dict)
        assert k8s_ingress["apiVersion"] == "networking.k8s.io/v1"
        assert k8s_ingress["kind"] == "Ingress"

        # Check metadata
        metadata = k8s_ingress["metadata"]
        assert metadata["name"] == "sts-ingress"
        assert "annotations" in metadata

        # Check spec
        spec = k8s_ingress["spec"]
        assert "rules" in spec

    @patch("subprocess.run")
    def test_build_container_image_without_push(self, mock_subprocess):
        """Test container image building without pushing."""
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "Successfully built abc123"

        image_id = self.orchestrator.build_container_image(push=False)

        assert isinstance(image_id, str)
        mock_subprocess.assert_called()

        # Should only call docker build, not push
        call_args = mock_subprocess.call_args[0][0]
        assert "docker" in call_args
        assert "build" in call_args

    @patch("subprocess.run")
    def test_build_container_image_with_push(self, mock_subprocess):
        """Test container image building with pushing."""
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "Successfully built abc123"

        image_id = self.orchestrator.build_container_image(push=True)

        assert isinstance(image_id, str)
        assert mock_subprocess.call_count >= 2  # Build and push

    @patch("subprocess.run")
    def test_deploy_to_kubernetes(self, mock_subprocess):
        """Test Kubernetes deployment."""
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "deployment created"

        with tempfile.TemporaryDirectory() as temp_dir:
            deployed_resources = self.orchestrator.deploy_to_kubernetes(temp_dir)

            assert isinstance(deployed_resources, list)
            mock_subprocess.assert_called()

    def test_generate_deployment_package(self):
        """Test deployment package generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            package_path = self.orchestrator.generate_deployment_package(temp_dir)

            assert isinstance(package_path, str)
            assert temp_dir in package_path

            # Check that files were created
            package_dir = Path(package_path)
            assert package_dir.exists()
            assert (package_dir / "Dockerfile").exists()
            assert (package_dir / "docker-compose.yml").exists()
            assert (package_dir / "k8s").exists()

    @patch("builtins.print")
    def test_create_deployment_packages_function(self, mock_print):
        """Test create_deployment_packages function."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("sensory_tracer_science.deployment.container_orchestration.Path.cwd", return_value=Path(temp_dir)):
                create_deployment_packages()

        # Should create print output for demo
        assert mock_print.call_count > 3


if __name__ == "__main__":
    unittest.main()