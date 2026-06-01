#!/usr/bin/env python3
"""
Comprehensive Test Suite for Cloud Deployment Manager

Tests all cloud deployment functionality including:
- Multi-cloud provider support (AWS, Azure, GCP, Hybrid)
- Deployment types (Serverless, Containers, VMs, Kubernetes, Managed Services)
- Infrastructure as Code generation
- Cost optimization recommendations
- Disaster recovery planning
- Security configurations
- Serverless configurations
"""

import json
import re
import unittest
from dataclasses import FrozenInstanceError
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from sensory_tracer_science.deployment.cloud_deployment import (
    CloudDeploymentManager,
    CloudInfrastructure,
    CloudProvider,
    DeploymentType,
    create_cloud_deployment_demo,
)


def _collapse_ws(text: str) -> str:
    """Collapse runs of spaces/tabs to a single space (HCL output is
    column-aligned, so assertions on ``key = value`` must be
    whitespace-insensitive)."""
    return re.sub(r"[ \t]+", " ", text)


class TestCloudProvider(unittest.TestCase):
    """Test CloudProvider enum."""

    def test_cloud_provider_values(self):
        """Test all cloud provider enum values."""
        self.assertEqual(CloudProvider.AWS.value, "aws")
        self.assertEqual(CloudProvider.AZURE.value, "azure")
        self.assertEqual(CloudProvider.GCP.value, "gcp")
        self.assertEqual(CloudProvider.HYBRID.value, "hybrid")

    def test_cloud_provider_count(self):
        """Test expected number of cloud providers."""
        self.assertEqual(len(CloudProvider), 4)


class TestDeploymentType(unittest.TestCase):
    """Test DeploymentType enum."""

    def test_deployment_type_values(self):
        """Test all deployment type enum values."""
        self.assertEqual(DeploymentType.SERVERLESS.value, "serverless")
        self.assertEqual(DeploymentType.CONTAINERS.value, "containers")
        self.assertEqual(DeploymentType.VIRTUAL_MACHINES.value, "virtual_machines")
        self.assertEqual(DeploymentType.KUBERNETES.value, "kubernetes")
        self.assertEqual(DeploymentType.MANAGED_SERVICES.value, "managed_services")

    def test_deployment_type_count(self):
        """Test expected number of deployment types."""
        self.assertEqual(len(DeploymentType), 5)


class TestCloudInfrastructure(unittest.TestCase):
    """Test CloudInfrastructure dataclass."""

    def setUp(self):
        """Set up test fixtures."""
        self.provider = CloudProvider.AWS
        self.region = "us-east-1"
        self.availability_zones = ["us-east-1a", "us-east-1b"]

    def test_basic_initialization(self):
        """Test basic CloudInfrastructure initialization."""
        infra = CloudInfrastructure(
            provider=self.provider,
            region=self.region,
            availability_zones=self.availability_zones,
        )

        self.assertEqual(infra.provider, self.provider)
        self.assertEqual(infra.region, self.region)
        self.assertEqual(infra.availability_zones, self.availability_zones)
        self.assertEqual(infra.instance_type, "medium")
        self.assertEqual(infra.min_instances, 2)
        self.assertEqual(infra.max_instances, 100)

    def test_default_values(self):
        """Test default values for optional parameters."""
        infra = CloudInfrastructure(
            provider=self.provider,
            region=self.region,
            availability_zones=self.availability_zones,
        )

        # Compute defaults
        self.assertEqual(infra.instance_type, "medium")
        self.assertEqual(infra.min_instances, 2)
        self.assertEqual(infra.max_instances, 100)

        # Storage defaults
        self.assertEqual(infra.storage_type, "ssd")
        self.assertEqual(infra.storage_size_gb, 100)
        self.assertTrue(infra.backup_enabled)

        # Network defaults
        self.assertEqual(infra.vpc_cidr, "10.0.0.0/16")

        # Security defaults
        self.assertTrue(infra.encryption_enabled)

    def test_post_init_default_subnets(self):
        """Test __post_init__ method sets default subnets."""
        infra = CloudInfrastructure(
            provider=self.provider,
            region=self.region,
            availability_zones=self.availability_zones,
        )

        # Check default public subnets
        expected_public = ["10.0.1.0/24", "10.0.2.0/24"]
        self.assertEqual(infra.public_subnets, expected_public)

        # Check default private subnets
        expected_private = ["10.0.10.0/24", "10.0.20.0/24"]
        self.assertEqual(infra.private_subnets, expected_private)

        # Check default security groups
        self.assertEqual(infra.security_groups, [])

    def test_custom_subnets(self):
        """Test initialization with custom subnets."""
        custom_public = ["192.168.1.0/24", "192.168.2.0/24"]
        custom_private = ["192.168.10.0/24", "192.168.20.0/24"]
        custom_security_groups = ["sg-12345", "sg-67890"]

        infra = CloudInfrastructure(
            provider=self.provider,
            region=self.region,
            availability_zones=self.availability_zones,
            public_subnets=custom_public,
            private_subnets=custom_private,
            security_groups=custom_security_groups,
        )

        self.assertEqual(infra.public_subnets, custom_public)
        self.assertEqual(infra.private_subnets, custom_private)
        self.assertEqual(infra.security_groups, custom_security_groups)

    def test_custom_configuration(self):
        """Test initialization with custom configuration parameters."""
        infra = CloudInfrastructure(
            provider=CloudProvider.GCP,
            region="us-central1",
            availability_zones=["us-central1-a", "us-central1-b"],
            instance_type="xlarge",
            min_instances=5,
            max_instances=200,
            storage_type="nvme",
            storage_size_gb=500,
            backup_enabled=False,
            vpc_cidr="172.16.0.0/16",
            encryption_enabled=False,
        )

        self.assertEqual(infra.provider, CloudProvider.GCP)
        self.assertEqual(infra.instance_type, "xlarge")
        self.assertEqual(infra.min_instances, 5)
        self.assertEqual(infra.max_instances, 200)
        self.assertEqual(infra.storage_type, "nvme")
        self.assertEqual(infra.storage_size_gb, 500)
        self.assertFalse(infra.backup_enabled)
        self.assertEqual(infra.vpc_cidr, "172.16.0.0/16")
        self.assertFalse(infra.encryption_enabled)

    def test_dataclass_immutability_features(self):
        """Test dataclass features like equality and representation."""
        infra1 = CloudInfrastructure(
            provider=self.provider,
            region=self.region,
            availability_zones=self.availability_zones,
        )

        infra2 = CloudInfrastructure(
            provider=self.provider,
            region=self.region,
            availability_zones=self.availability_zones,
        )

        # Test equality
        self.assertEqual(infra1, infra2)

        # Test representation
        repr_str = repr(infra1)
        self.assertIn("CloudInfrastructure", repr_str)
        self.assertIn("provider=", repr_str)
        self.assertIn("region=", repr_str)


class TestCloudDeploymentManager(unittest.TestCase):
    """Test CloudDeploymentManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.provider = CloudProvider.AWS
        self.deployment_type = DeploymentType.KUBERNETES

    def test_initialization(self):
        """Test CloudDeploymentManager initialization."""
        manager = CloudDeploymentManager(self.provider, self.deployment_type)

        self.assertEqual(manager.provider, self.provider)
        self.assertEqual(manager.deployment_type, self.deployment_type)
        self.assertIsNone(manager.infrastructure)

    @patch("builtins.print")
    def test_initialization_with_print(self, mock_print):
        """Test initialization prints correct message."""
        manager = CloudDeploymentManager(self.provider, self.deployment_type)

        mock_print.assert_called_once_with(
            f"☁️ Cloud deployment manager initialized: {self.provider.value} - {self.deployment_type.value}"
        )

    def test_different_provider_combinations(self):
        """Test different provider and deployment type combinations."""
        combinations = [
            (CloudProvider.AWS, DeploymentType.SERVERLESS),
            (CloudProvider.AZURE, DeploymentType.CONTAINERS),
            (CloudProvider.GCP, DeploymentType.VIRTUAL_MACHINES),
            (CloudProvider.HYBRID, DeploymentType.MANAGED_SERVICES),
        ]

        for provider, deployment_type in combinations:
            with patch("builtins.print"):
                manager = CloudDeploymentManager(provider, deployment_type)
                self.assertEqual(manager.provider, provider)
                self.assertEqual(manager.deployment_type, deployment_type)


class TestAWSTerraformGeneration(unittest.TestCase):
    """Test AWS Terraform configuration generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = CloudDeploymentManager(
            CloudProvider.AWS, DeploymentType.KUBERNETES
        )
        self.infrastructure = CloudInfrastructure(
            provider=CloudProvider.AWS,
            region="us-east-1",
            availability_zones=["us-east-1a", "us-east-1b"],
            instance_type="large",
            min_instances=3,
            max_instances=50,
            storage_size_gb=200,
        )

    @patch("builtins.print")
    def test_generate_aws_terraform_basic(self, mock_print):
        """Test basic AWS Terraform configuration generation."""
        terraform_config = self.manager.generate_aws_terraform(self.infrastructure)

        # Check that configuration is generated
        self.assertIsInstance(terraform_config, str)
        self.assertGreater(len(terraform_config), 1000)

        # Check for essential Terraform blocks
        self.assertIn("terraform {", terraform_config)
        self.assertIn("provider \"aws\"", terraform_config)
        self.assertIn("resource \"aws_vpc\"", terraform_config)
        self.assertIn("resource \"aws_eks_cluster\"", terraform_config)
        self.assertIn("resource \"aws_db_instance\"", terraform_config)

    @patch("builtins.print")
    def test_terraform_config_content(self, mock_print):
        """Test specific content in Terraform configuration."""
        terraform_config = _collapse_ws(
            self.manager.generate_aws_terraform(self.infrastructure)
        )

        # Check region configuration
        self.assertIn(f'region = "{self.infrastructure.region}"', terraform_config)

        # Check VPC CIDR
        self.assertIn(f'cidr_block = "{self.infrastructure.vpc_cidr}"', terraform_config)

        # Check instance scaling configuration
        self.assertIn(f"desired_size = {self.infrastructure.min_instances}", terraform_config)
        self.assertIn(f"max_size = {self.infrastructure.max_instances}", terraform_config)

        # Check storage configuration
        self.assertIn(f"allocated_storage = {self.infrastructure.storage_size_gb}", terraform_config)

        # Check encryption settings
        encryption_value = str(self.infrastructure.encryption_enabled).lower()
        self.assertIn(f"storage_encrypted = {encryption_value}", terraform_config)

    @patch("builtins.print")
    def test_aws_instance_type_mapping(self, mock_print):
        """Test AWS instance type mapping."""
        # Test different instance type mappings
        test_cases = [
            ("small", "t3.medium"),
            ("medium", "t3.large"),
            ("large", "c5.xlarge"),
            ("xlarge", "c5.2xlarge"),
            ("unknown", "t3.large"),  # Default fallback
        ]

        for input_size, expected_type in test_cases:
            actual_type = self.manager._get_aws_instance_type(input_size)
            self.assertEqual(actual_type, expected_type)

    @patch("builtins.print")
    def test_aws_public_subnets_generation(self, mock_print):
        """Test AWS public subnets generation."""
        subnets_config = self.manager._generate_aws_public_subnets(self.infrastructure)

        self.assertIsInstance(subnets_config, str)
        self.assertGreater(len(subnets_config), 100)
        subnets_config = _collapse_ws(subnets_config)

        # Check for subnet resources
        self.assertIn('resource "aws_subnet" "sts_public_subnet_0"', subnets_config)
        self.assertIn('resource "aws_subnet" "sts_public_subnet_1"', subnets_config)

        # Check for route table associations
        self.assertIn('resource "aws_route_table_association"', subnets_config)

        # Check subnet CIDRs
        for subnet_cidr in self.infrastructure.public_subnets:
            self.assertIn(f'cidr_block = "{subnet_cidr}"', subnets_config)

        # Check availability zones
        for az in self.infrastructure.availability_zones:
            self.assertIn(f'availability_zone = "{az}"', subnets_config)

    @patch("builtins.print")
    def test_aws_private_subnets_generation(self, mock_print):
        """Test AWS private subnets generation."""
        subnets_config = self.manager._generate_aws_private_subnets(self.infrastructure)

        self.assertIsInstance(subnets_config, str)
        self.assertGreater(len(subnets_config), 100)
        subnets_config = _collapse_ws(subnets_config)

        # Check for subnet resources
        self.assertIn('resource "aws_subnet" "sts_private_subnet_0"', subnets_config)
        self.assertIn('resource "aws_subnet" "sts_private_subnet_1"', subnets_config)

        # Check for Kubernetes tags
        self.assertIn('"kubernetes.io/role/internal-elb" = "1"', subnets_config)

        # Check subnet CIDRs
        for subnet_cidr in self.infrastructure.private_subnets:
            self.assertIn(f'cidr_block = "{subnet_cidr}"', subnets_config)

    @patch("builtins.print")
    def test_aws_security_groups_generation(self, mock_print):
        """Test AWS security groups generation."""
        security_groups_config = self.manager._generate_aws_security_groups()

        self.assertIsInstance(security_groups_config, str)
        self.assertGreater(len(security_groups_config), 500)
        security_groups_config = _collapse_ws(security_groups_config)

        # Check for security group resources
        expected_security_groups = [
            "sts_cluster_sg",
            "sts_db_sg",
            "sts_redis_sg", 
            "sts_app_sg",
        ]

        for sg_name in expected_security_groups:
            self.assertIn(f'resource "aws_security_group" "{sg_name}"', security_groups_config)

        # Check for ingress/egress rules
        self.assertIn("ingress {", security_groups_config)
        self.assertIn("egress {", security_groups_config)

        # Check for specific ports
        self.assertIn("from_port = 443", security_groups_config)  # HTTPS
        self.assertIn("from_port = 5432", security_groups_config)  # PostgreSQL
        self.assertIn("from_port = 6379", security_groups_config)  # Redis
        self.assertIn("from_port = 8000", security_groups_config)  # Application

    @patch("builtins.print")
    def test_aws_iam_roles_generation(self, mock_print):
        """Test AWS IAM roles generation."""
        iam_roles_config = self.manager._generate_aws_iam_roles()

        self.assertIsInstance(iam_roles_config, str)
        self.assertGreater(len(iam_roles_config), 1000)

        # Check for IAM role resources
        expected_roles = [
            "sts_cluster_role",
            "sts_node_role",
        ]

        for role_name in expected_roles:
            self.assertIn(f'resource "aws_iam_role" "{role_name}"', iam_roles_config)

        # Check for policy attachments
        self.assertIn('resource "aws_iam_role_policy_attachment"', iam_roles_config)

        # Check for AWS managed policies
        self.assertIn("AmazonEKSClusterPolicy", iam_roles_config)
        self.assertIn("AmazonEKSWorkerNodePolicy", iam_roles_config)
        self.assertIn("AmazonEKS_CNI_Policy", iam_roles_config)

        # Check for assume role policies
        self.assertIn("assume_role_policy", iam_roles_config)
        self.assertIn("eks.amazonaws.com", iam_roles_config)
        self.assertIn("ec2.amazonaws.com", iam_roles_config)


class TestServerlessConfiguration(unittest.TestCase):
    """Test serverless configuration generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.aws_manager = CloudDeploymentManager(
            CloudProvider.AWS, DeploymentType.SERVERLESS
        )
        self.azure_manager = CloudDeploymentManager(
            CloudProvider.AZURE, DeploymentType.SERVERLESS
        )
        self.gcp_manager = CloudDeploymentManager(
            CloudProvider.GCP, DeploymentType.SERVERLESS
        )

    @patch("builtins.print")
    def test_aws_serverless_config(self, mock_print):
        """Test AWS serverless configuration generation."""
        config = self.aws_manager.generate_serverless_config()

        self.assertIsInstance(config, dict)
        self.assertEqual(config["service"], "sts-serverless")
        self.assertEqual(config["frameworkVersion"], "3")

        # Check provider configuration
        provider_config = config["provider"]
        self.assertEqual(provider_config["name"], "aws")
        self.assertEqual(provider_config["runtime"], "python3.11")
        self.assertEqual(provider_config["region"], "us-east-1")
        self.assertEqual(provider_config["stage"], "production")

        # Check environment variables
        env = provider_config["environment"]
        self.assertEqual(env["STS_ENVIRONMENT"], "production")
        self.assertEqual(env["STS_LOG_LEVEL"], "INFO")

        # Check IAM role statements
        iam_statements = provider_config["iamRoleStatements"]
        self.assertGreater(len(iam_statements), 0)

        # Check function definitions
        functions = config["functions"]
        expected_functions = [
            "neural_tracer_api",
            "quantum_tracer_api",
            "brillouin_tracer_api",
            "monitoring_collector",
        ]

        for func_name in expected_functions:
            self.assertIn(func_name, functions)
            func_config = functions[func_name]
            self.assertIn("handler", func_config)
            self.assertIn("timeout", func_config)
            self.assertIn("memorySize", func_config)

    @patch("builtins.print")
    def test_aws_serverless_function_configurations(self, mock_print):
        """Test specific AWS serverless function configurations."""
        config = self.aws_manager.generate_serverless_config()
        functions = config["functions"]

        # Test neural tracer function
        neural_func = functions["neural_tracer_api"]
        self.assertEqual(neural_func["handler"], "sensory_tracer_science.serverless.neural_handler.handler")
        self.assertEqual(neural_func["timeout"], 30)
        self.assertEqual(neural_func["memorySize"], 512)
        self.assertEqual(neural_func["environment"]["TRACER_TYPE"], "neural")

        # Check HTTP events
        events = neural_func["events"]
        self.assertEqual(len(events), 1)
        http_event = events[0]["http"]
        self.assertEqual(http_event["path"], "/api/neural/{proxy+}")
        self.assertEqual(http_event["method"], "ANY")
        self.assertTrue(http_event["cors"])

        # Test quantum tracer function
        quantum_func = functions["quantum_tracer_api"]
        self.assertEqual(quantum_func["memorySize"], 1024)
        self.assertEqual(quantum_func["environment"]["TRACER_TYPE"], "quantum")

        # Test brillouin tracer function
        brillouin_func = functions["brillouin_tracer_api"]
        self.assertEqual(brillouin_func["timeout"], 60)
        self.assertEqual(brillouin_func["memorySize"], 256)

        # Test monitoring collector function
        monitoring_func = functions["monitoring_collector"]
        self.assertEqual(monitoring_func["events"][0]["schedule"], "rate(1 minute)")
        self.assertEqual(monitoring_func["environment"]["MONITORING_ENABLED"], "true")

    @patch("builtins.print")
    def test_azure_serverless_config(self, mock_print):
        """Test Azure serverless configuration generation."""
        config = self.azure_manager.generate_serverless_config()

        self.assertIsInstance(config, dict)
        self.assertEqual(config["service"], "sts-azure-functions")
        self.assertEqual(config["provider"], "azure")
        self.assertEqual(config["runtime"], "python3.11")

        # Check functions
        functions = config["functions"]
        self.assertIn("neural_tracer", functions)

        neural_func = functions["neural_tracer"]
        bindings = neural_func["bindings"]
        self.assertEqual(len(bindings), 1)

        binding = bindings[0]
        self.assertEqual(binding["authLevel"], "function")
        self.assertEqual(binding["type"], "httpTrigger")
        self.assertEqual(binding["direction"], "in")
        self.assertEqual(binding["name"], "req")
        self.assertIn("get", binding["methods"])
        self.assertIn("post", binding["methods"])

    @patch("builtins.print")
    def test_gcp_serverless_config(self, mock_print):
        """Test GCP serverless configuration generation."""
        config = self.gcp_manager.generate_serverless_config()

        self.assertIsInstance(config, dict)
        self.assertEqual(config["service"], "sts-cloud-functions")
        self.assertEqual(config["provider"], "gcp")
        self.assertEqual(config["runtime"], "python311")

        # Check functions
        functions = config["functions"]
        self.assertIn("neural_tracer", functions)

        neural_func = functions["neural_tracer"]
        self.assertIn("trigger", neural_func)
        self.assertIn("httpsTrigger", neural_func["trigger"])
        self.assertEqual(neural_func["entryPoint"], "neural_tracer_handler")
        self.assertEqual(neural_func["runtime"], "python311")
        self.assertEqual(neural_func["availableMemoryMb"], 512)
        self.assertEqual(neural_func["timeout"], "60s")

    @patch("builtins.print")
    def test_unsupported_provider_serverless(self, mock_print):
        """Test unsupported provider for serverless configuration."""
        hybrid_manager = CloudDeploymentManager(
            CloudProvider.HYBRID, DeploymentType.SERVERLESS
        )

        with self.assertRaises(ValueError) as context:
            hybrid_manager.generate_serverless_config()

        self.assertIn("Serverless not supported for hybrid", str(context.exception))


class TestCostOptimization(unittest.TestCase):
    """Test cost optimization functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = CloudDeploymentManager(
            CloudProvider.AWS, DeploymentType.KUBERNETES
        )
        self.infrastructure = CloudInfrastructure(
            provider=CloudProvider.AWS,
            region="us-east-1",
            availability_zones=["us-east-1a", "us-east-1b"],
            min_instances=10,
            max_instances=100,
            storage_size_gb=1000,
        )

    @patch("builtins.print")
    def test_cost_optimization_recommendations_structure(self, mock_print):
        """Test cost optimization recommendations structure."""
        recommendations = self.manager.generate_cost_optimization_recommendations(
            self.infrastructure
        )

        # Check basic structure
        self.assertIsInstance(recommendations, dict)
        required_keys = [
            "timestamp",
            "provider",
            "estimated_monthly_cost",
            "optimization_opportunities",
            "cost_breakdown",
            "recommendations",
        ]

        for key in required_keys:
            self.assertIn(key, recommendations)

        # Check timestamp format
        timestamp = recommendations["timestamp"]
        datetime.fromisoformat(timestamp)  # Should not raise exception

        # Check provider
        self.assertEqual(recommendations["provider"], "aws")

        # Check cost breakdown structure
        cost_breakdown = recommendations["cost_breakdown"]
        expected_categories = ["compute", "storage", "networking", "managed_services"]
        for category in expected_categories:
            self.assertIn(category, cost_breakdown)
            self.assertIsInstance(cost_breakdown[category], (int, float))

        # Check recommendations list
        recommendations_list = recommendations["recommendations"]
        self.assertIsInstance(recommendations_list, list)

    @patch("builtins.print")
    def test_cost_optimization_high_instances(self, mock_print):
        """Test cost optimization for high instance count."""
        high_instance_infra = CloudInfrastructure(
            provider=CloudProvider.AWS,
            region="us-east-1",
            availability_zones=["us-east-1a", "us-east-1b"],
            max_instances=75,  # Triggers spot instance recommendation
        )

        recommendations = self.manager.generate_cost_optimization_recommendations(
            high_instance_infra
        )

        recommendations_list = recommendations["recommendations"]
        
        # Should contain spot instance recommendation
        spot_recommendations = [
            rec for rec in recommendations_list
            if "spot instances" in rec["description"]
        ]
        self.assertGreater(len(spot_recommendations), 0)

        spot_rec = spot_recommendations[0]
        self.assertEqual(spot_rec["category"], "compute")
        self.assertEqual(spot_rec["priority"], "high")
        self.assertIn("60-70%", spot_rec["potential_savings"])

    @patch("builtins.print")
    def test_cost_optimization_large_storage(self, mock_print):
        """Test cost optimization for large storage."""
        large_storage_infra = CloudInfrastructure(
            provider=CloudProvider.AWS,
            region="us-east-1",
            availability_zones=["us-east-1a", "us-east-1b"],
            storage_size_gb=750,  # Triggers intelligent tiering recommendation
        )

        recommendations = self.manager.generate_cost_optimization_recommendations(
            large_storage_infra
        )

        recommendations_list = recommendations["recommendations"]
        
        # Should contain storage tiering recommendation
        storage_recommendations = [
            rec for rec in recommendations_list
            if "intelligent tiering" in rec["description"]
        ]
        self.assertGreater(len(storage_recommendations), 0)

        storage_rec = storage_recommendations[0]
        self.assertEqual(storage_rec["category"], "storage")
        self.assertEqual(storage_rec["priority"], "medium")
        self.assertIn("40-50%", storage_rec["potential_savings"])

    @patch("builtins.print")
    def test_cost_optimization_aws_reserved_instances(self, mock_print):
        """Test AWS-specific reserved instance recommendations."""
        recommendations = self.manager.generate_cost_optimization_recommendations(
            self.infrastructure
        )

        recommendations_list = recommendations["recommendations"]
        
        # AWS should always include reserved instance recommendation
        ri_recommendations = [
            rec for rec in recommendations_list
            if "Reserved Instances" in rec["description"]
        ]
        self.assertGreater(len(ri_recommendations), 0)

        ri_rec = ri_recommendations[0]
        self.assertEqual(ri_rec["category"], "compute")
        self.assertEqual(ri_rec["priority"], "high")
        self.assertIn("30-50%", ri_rec["potential_savings"])

    @patch("builtins.print")
    def test_calculate_estimated_cost_aws(self, mock_print):
        """Test estimated cost calculation for AWS."""
        cost = self.manager._calculate_estimated_cost(self.infrastructure)

        self.assertIsInstance(cost, float)
        self.assertGreater(cost, 0)

        # Cost should include compute, storage, DB, and LB costs
        expected_minimum = (
            50.0 * self.infrastructure.min_instances +  # Compute
            0.10 * self.infrastructure.storage_size_gb +  # Storage
            100.0 +  # Managed DB
            25.0  # Load balancer
        )
        
        self.assertGreaterEqual(cost, expected_minimum - 1.0)  # Allow small rounding differences

    @patch("builtins.print")
    def test_calculate_estimated_cost_different_providers(self, mock_print):
        """Test estimated cost calculation for different providers."""
        providers_and_managers = [
            (CloudProvider.AWS, self.manager),
            (CloudProvider.AZURE, CloudDeploymentManager(CloudProvider.AZURE, DeploymentType.KUBERNETES)),
            (CloudProvider.GCP, CloudDeploymentManager(CloudProvider.GCP, DeploymentType.KUBERNETES)),
        ]

        costs = {}
        for provider, manager in providers_and_managers:
            infra = CloudInfrastructure(
                provider=provider,
                region="test-region",
                availability_zones=["zone-a", "zone-b"],
                min_instances=5,
                storage_size_gb=200,
            )
            
            cost = manager._calculate_estimated_cost(infra)
            costs[provider] = cost
            
            self.assertIsInstance(cost, float)
            self.assertGreater(cost, 0)

        # GCP should be cheapest, AWS most expensive (based on the pricing model)
        self.assertGreater(costs[CloudProvider.AWS], costs[CloudProvider.GCP])

    @patch("builtins.print")
    def test_calculate_estimated_cost_backup_influence(self, mock_print):
        """Test backup settings influence on cost calculation."""
        infra_with_backup = CloudInfrastructure(
            provider=CloudProvider.AWS,
            region="us-east-1",
            availability_zones=["us-east-1a"],
            backup_enabled=True,
        )

        infra_without_backup = CloudInfrastructure(
            provider=CloudProvider.AWS,
            region="us-east-1",
            availability_zones=["us-east-1a"],
            backup_enabled=False,
        )

        cost_with_backup = self.manager._calculate_estimated_cost(infra_with_backup)
        cost_without_backup = self.manager._calculate_estimated_cost(infra_without_backup)

        # With backup should be more expensive
        self.assertGreater(cost_with_backup, cost_without_backup)

    @patch("builtins.print")
    def test_calculate_estimated_cost_unsupported_provider(self, mock_print):
        """Test cost calculation for unsupported provider."""
        hybrid_manager = CloudDeploymentManager(
            CloudProvider.HYBRID, DeploymentType.KUBERNETES
        )
        
        infra = CloudInfrastructure(
            provider=CloudProvider.HYBRID,
            region="hybrid-region",
            availability_zones=["zone-a"],
        )

        cost = hybrid_manager._calculate_estimated_cost(infra)
        self.assertEqual(cost, 0.0)


class TestDisasterRecovery(unittest.TestCase):
    """Test disaster recovery planning functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = CloudDeploymentManager(
            CloudProvider.AWS, DeploymentType.KUBERNETES
        )
        self.infrastructure = CloudInfrastructure(
            provider=CloudProvider.AWS,
            region="us-east-1",
            availability_zones=["us-east-1a", "us-east-1b"],
        )

    @patch("builtins.print")
    def test_disaster_recovery_plan_structure(self, mock_print):
        """Test disaster recovery plan structure."""
        dr_plan = self.manager.generate_disaster_recovery_plan(self.infrastructure)

        # Check basic structure
        self.assertIsInstance(dr_plan, dict)
        required_keys = [
            "recovery_objectives",
            "backup_strategy",
            "failover_procedures",
            "testing_schedule",
        ]

        for key in required_keys:
            self.assertIn(key, dr_plan)

    @patch("builtins.print")
    def test_recovery_objectives(self, mock_print):
        """Test recovery objectives configuration."""
        dr_plan = self.manager.generate_disaster_recovery_plan(self.infrastructure)
        
        objectives = dr_plan["recovery_objectives"]
        self.assertIn("rto", objectives)
        self.assertIn("rpo", objectives)
        
        # Check that values are reasonable
        rto = objectives["rto"]
        rpo = objectives["rpo"]
        
        self.assertIsInstance(rto, int)
        self.assertIsInstance(rpo, int)
        self.assertGreater(rto, 0)
        self.assertGreater(rpo, 0)
        self.assertEqual(rto, 60)  # 60 minutes RTO
        self.assertEqual(rpo, 15)  # 15 minutes RPO

    @patch("builtins.print")
    def test_backup_strategy(self, mock_print):
        """Test backup strategy configuration."""
        dr_plan = self.manager.generate_disaster_recovery_plan(self.infrastructure)
        
        backup_strategy = dr_plan["backup_strategy"]
        self.assertIn("database_backups", backup_strategy)
        self.assertIn("application_backups", backup_strategy)

        # Check database backup configuration
        db_backups = backup_strategy["database_backups"]
        self.assertEqual(db_backups["frequency"], "continuous")
        self.assertEqual(db_backups["retention"], "30 days")
        self.assertTrue(db_backups["cross_region"])

        # Check application backup configuration
        app_backups = backup_strategy["application_backups"]
        self.assertEqual(app_backups["frequency"], "daily")
        self.assertEqual(app_backups["retention"], "7 days")
        self.assertTrue(app_backups["cross_region"])

    @patch("builtins.print")
    def test_failover_procedures(self, mock_print):
        """Test failover procedures configuration."""
        dr_plan = self.manager.generate_disaster_recovery_plan(self.infrastructure)
        
        procedures = dr_plan["failover_procedures"]
        self.assertIsInstance(procedures, list)
        self.assertEqual(len(procedures), 4)

        # Check procedure steps
        expected_steps = [
            "Detect service outage",
            "Activate standby region", 
            "Redirect traffic to DR site",
            "Validate service functionality",
        ]

        for i, expected_desc in enumerate(expected_steps):
            procedure = procedures[i]
            self.assertEqual(procedure["step"], i + 1)
            self.assertEqual(procedure["description"], expected_desc)
            self.assertIn("automated", procedure)
            self.assertIn("timeout", procedure)
            self.assertIsInstance(procedure["timeout"], int)
            self.assertGreater(procedure["timeout"], 0)

        # Check automation settings
        self.assertTrue(procedures[0]["automated"])  # Detection
        self.assertTrue(procedures[1]["automated"])  # Activation
        self.assertTrue(procedures[2]["automated"])  # Traffic redirect
        self.assertFalse(procedures[3]["automated"])  # Manual validation

    @patch("builtins.print")
    def test_testing_schedule(self, mock_print):
        """Test disaster recovery testing schedule."""
        dr_plan = self.manager.generate_disaster_recovery_plan(self.infrastructure)
        
        testing = dr_plan["testing_schedule"]
        self.assertEqual(testing["frequency"], "quarterly")
        self.assertIn("next_test_date", testing)
        self.assertIn("test_types", testing)

        # Check test types
        test_types = testing["test_types"]
        expected_types = ["failover", "data_recovery", "network_switching"]
        self.assertEqual(test_types, expected_types)

        # Check date format
        next_test_date = testing["next_test_date"]
        self.assertIsInstance(next_test_date, str)
        # Should be in YYYY-MM-DD format
        self.assertRegex(next_test_date, r"^\d{4}-\d{2}-\d{2}$")


class TestCloudDeploymentDemo(unittest.TestCase):
    """Test cloud deployment demo functionality."""

    @patch("builtins.print")
    def test_create_cloud_deployment_demo(self, mock_print):
        """Test the demo function runs without errors."""
        demo_result = create_cloud_deployment_demo()

        # Check return value structure
        self.assertIsInstance(demo_result, dict)
        expected_keys = [
            "aws_manager",
            "infrastructure",
            "terraform_config",
            "cost_recommendations",
            "dr_plan",
            "serverless_config",
        ]

        for key in expected_keys:
            self.assertIn(key, demo_result)

        # Check types of returned objects
        self.assertIsInstance(demo_result["aws_manager"], CloudDeploymentManager)
        self.assertIsInstance(demo_result["infrastructure"], CloudInfrastructure)
        self.assertIsInstance(demo_result["terraform_config"], str)
        self.assertIsInstance(demo_result["cost_recommendations"], dict)
        self.assertIsInstance(demo_result["dr_plan"], dict)
        self.assertIsInstance(demo_result["serverless_config"], dict)

        # Check that print was called multiple times (demo output)
        self.assertGreater(mock_print.call_count, 5)

    @patch("builtins.print")
    def test_demo_infrastructure_configuration(self, mock_print):
        """Test demo infrastructure configuration."""
        demo_result = create_cloud_deployment_demo()
        
        infrastructure = demo_result["infrastructure"]
        self.assertEqual(infrastructure.provider, CloudProvider.AWS)
        self.assertEqual(infrastructure.region, "us-east-1")
        self.assertEqual(infrastructure.instance_type, "medium")
        self.assertEqual(infrastructure.min_instances, 3)
        self.assertEqual(infrastructure.max_instances, 50)
        self.assertEqual(infrastructure.storage_size_gb, 200)

    @patch("builtins.print")
    def test_demo_managers_configuration(self, mock_print):
        """Test demo managers configuration."""
        demo_result = create_cloud_deployment_demo()
        
        aws_manager = demo_result["aws_manager"]
        self.assertEqual(aws_manager.provider, CloudProvider.AWS)
        self.assertEqual(aws_manager.deployment_type, DeploymentType.KUBERNETES)

    @patch("builtins.print")
    def test_demo_output_content(self, mock_print):
        """Test demo generates valid content."""
        demo_result = create_cloud_deployment_demo()

        # Check Terraform config
        terraform_config = demo_result["terraform_config"]
        self.assertGreater(len(terraform_config), 1000)
        self.assertIn("terraform {", terraform_config)

        # Check cost recommendations
        cost_recommendations = demo_result["cost_recommendations"]
        self.assertIn("estimated_monthly_cost", cost_recommendations)
        self.assertIsInstance(cost_recommendations["estimated_monthly_cost"], float)

        # Check DR plan
        dr_plan = demo_result["dr_plan"]
        self.assertIn("recovery_objectives", dr_plan)
        self.assertIn("rto", dr_plan["recovery_objectives"])

        # Check serverless config
        serverless_config = demo_result["serverless_config"]
        self.assertIn("functions", serverless_config)
        self.assertGreater(len(serverless_config["functions"]), 0)


class TestEdgeCasesAndErrorHandling(unittest.TestCase):
    """Test edge cases and error handling."""

    def test_empty_availability_zones(self):
        """Test handling of empty availability zones."""
        with self.assertRaises(TypeError):
            # This should fail at the dataclass level since availability_zones is required
            CloudInfrastructure(
                provider=CloudProvider.AWS,
                region="us-east-1",
            )

    def test_zero_instances(self):
        """Test handling of zero instances."""
        infra = CloudInfrastructure(
            provider=CloudProvider.AWS,
            region="us-east-1",
            availability_zones=["us-east-1a"],
            min_instances=0,
            max_instances=0,
        )
        
        # Should still work, just with zero instances
        self.assertEqual(infra.min_instances, 0)
        self.assertEqual(infra.max_instances, 0)

    @patch("builtins.print")
    def test_negative_storage_size(self, mock_print):
        """Test handling of negative storage size."""
        infra = CloudInfrastructure(
            provider=CloudProvider.AWS,
            region="us-east-1",
            availability_zones=["us-east-1a"],
            storage_size_gb=-100,
        )

        manager = CloudDeploymentManager(CloudProvider.AWS, DeploymentType.KUBERNETES)
        cost = manager._calculate_estimated_cost(infra)
        
        # Cost calculation should handle negative values gracefully
        self.assertIsInstance(cost, float)

    @patch("builtins.print")
    def test_very_large_infrastructure(self, mock_print):
        """Test handling of very large infrastructure configurations."""
        infra = CloudInfrastructure(
            provider=CloudProvider.AWS,
            region="us-east-1",
            availability_zones=["us-east-1a", "us-east-1b"],
            min_instances=1000,
            max_instances=10000,
            storage_size_gb=100000,
        )

        manager = CloudDeploymentManager(CloudProvider.AWS, DeploymentType.KUBERNETES)
        
        # Should handle large configurations without errors
        terraform_config = manager.generate_aws_terraform(infra)
        self.assertIsInstance(terraform_config, str)
        self.assertGreater(len(terraform_config), 1000)

        cost = manager._calculate_estimated_cost(infra)
        self.assertIsInstance(cost, float)
        self.assertGreater(cost, 10000)  # Should be expensive

        cost_recommendations = manager.generate_cost_optimization_recommendations(infra)
        self.assertIsInstance(cost_recommendations, dict)


if __name__ == "__main__":
    unittest.main()