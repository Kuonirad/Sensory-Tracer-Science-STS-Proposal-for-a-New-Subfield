#!/usr/bin/env python3
"""
Production Configuration Management for STS Framework

Comprehensive production configuration system with environment management,
security controls, performance optimization, and deployment automation.
"""

import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class DeploymentEnvironment(Enum):
    """Deployment environment types."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    CLINICAL = "clinical"  # Special environment for clinical trials


class SecurityLevel(Enum):
    """Security compliance levels."""

    BASIC = "basic"
    HIPAA = "hipaa"  # Healthcare compliance
    FDA_CFR21 = "fda_cfr21"  # FDA 21 CFR Part 11
    ISO27001 = "iso27001"  # International security standard
    SOX = "sox"  # Sarbanes-Oxley compliance


@dataclass
class DatabaseConfig:
    """Database configuration parameters."""

    # Connection parameters
    host: str = "localhost"
    port: int = 5432
    database: str = "sts_production"
    username: str = "sts_user"
    password_env_var: str = "STS_DB_PASSWORD"

    # Connection pool settings
    min_connections: int = 5
    max_connections: int = 100
    connection_timeout: int = 30

    # Performance settings
    statement_timeout: int = 300  # seconds
    lock_timeout: int = 30  # seconds
    idle_in_transaction_timeout: int = 60

    # Backup and recovery
    backup_enabled: bool = True
    backup_schedule: str = "0 2 * * *"  # Daily at 2 AM
    backup_retention_days: int = 30
    point_in_time_recovery: bool = True

    # Security settings
    ssl_enabled: bool = True
    ssl_cert_path: str = "/etc/ssl/certs/postgresql.crt"
    encryption_at_rest: bool = True
    audit_logging: bool = True


@dataclass
class RedisConfig:
    """Redis cache configuration."""

    # Connection parameters
    host: str = "localhost"
    port: int = 6379
    password_env_var: str = "STS_REDIS_PASSWORD"
    database: int = 0

    # Performance settings
    max_connections: int = 50
    socket_timeout: int = 5
    socket_connect_timeout: int = 5

    # Memory management
    max_memory_mb: int = 1024
    max_memory_policy: str = "allkeys-lru"

    # Persistence
    persistence_enabled: bool = True
    save_schedule: str = "900 1 300 10 60 10000"  # Redis save points

    # Clustering
    cluster_enabled: bool = False
    cluster_nodes: List[str] = None

    def __post_init__(self):
        if self.cluster_nodes is None:
            self.cluster_nodes = []


@dataclass
class SecurityConfig:
    """Security configuration parameters."""

    # Authentication
    authentication_method: str = "jwt"
    jwt_secret_env_var: str = "STS_JWT_SECRET"
    jwt_expiration_hours: int = 24
    multi_factor_auth_required: bool = True

    # Authorization
    rbac_enabled: bool = True
    role_definitions_file: str = "config/roles.yaml"
    permission_cache_ttl: int = 300  # seconds

    # Encryption
    encryption_algorithm: str = "AES-256-GCM"
    key_rotation_days: int = 90
    key_management_service: str = "aws_kms"

    # API Security
    rate_limiting_enabled: bool = True
    rate_limit_requests_per_minute: int = 1000
    cors_allowed_origins: List[str] = None
    csrf_protection: bool = True

    # Audit and Compliance
    audit_log_enabled: bool = True
    audit_log_retention_days: int = 365
    compliance_level: SecurityLevel = SecurityLevel.HIPAA

    # Network Security
    ip_whitelist_enabled: bool = False
    allowed_ip_ranges: List[str] = None
    vpc_endpoint_enabled: bool = True

    def __post_init__(self):
        if self.cors_allowed_origins is None:
            self.cors_allowed_origins = ["https://sts-dashboard.company.com"]
        if self.allowed_ip_ranges is None:
            self.allowed_ip_ranges = []


@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration."""

    # Metrics collection
    metrics_enabled: bool = True
    metrics_retention_days: int = 90
    metrics_aggregation_interval: int = 60  # seconds

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    log_retention_days: int = 30
    structured_logging: bool = True

    # Tracing
    distributed_tracing_enabled: bool = True
    trace_sampling_rate: float = 0.1  # 10% sampling
    jaeger_endpoint: str = "http://jaeger-collector:14268"

    # Alerting
    alerting_enabled: bool = True
    alert_channels: List[str] = None

    # Health checks
    health_check_interval: int = 30  # seconds
    health_check_timeout: int = 5  # seconds

    # Performance monitoring
    apm_enabled: bool = True
    profiling_enabled: bool = False  # Only in non-prod

    def __post_init__(self):
        if self.alert_channels is None:
            self.alert_channels = ["email", "slack", "pagerduty"]


@dataclass
class ScalingConfig:
    """Auto-scaling configuration parameters."""

    # Horizontal scaling
    min_replicas: int = 2
    max_replicas: int = 100
    target_cpu_utilization: int = 70  # percentage
    target_memory_utilization: int = 80  # percentage

    # Scaling behavior
    scale_up_period: int = 60  # seconds
    scale_down_period: int = 300  # seconds
    scale_up_increment: int = 2
    scale_down_increment: int = 1

    # Load balancing
    load_balancer_type: str = "application"
    health_check_path: str = "/health"
    health_check_interval: int = 30

    # Resource limits
    cpu_request: str = "100m"
    cpu_limit: str = "500m"
    memory_request: str = "256Mi"
    memory_limit: str = "512Mi"

    # Autoscaling strategies
    predictive_scaling_enabled: bool = True
    scheduled_scaling_enabled: bool = True
    custom_metrics_scaling: bool = True


@dataclass
class BackupConfig:
    """Backup and disaster recovery configuration."""

    # Backup strategy
    backup_enabled: bool = True
    backup_schedule: str = "0 1 * * *"  # Daily at 1 AM
    backup_retention_days: int = 90

    # Backup types
    full_backup_schedule: str = "0 1 * * 0"  # Weekly full backup
    incremental_backup_schedule: str = "0 1 * * 1-6"  # Daily incremental

    # Backup storage
    backup_storage_type: str = "s3"
    backup_encryption_enabled: bool = True
    backup_compression: bool = True

    # Disaster recovery
    disaster_recovery_enabled: bool = True
    rto_minutes: int = 60  # Recovery Time Objective
    rpo_minutes: int = 15  # Recovery Point Objective

    # Multi-region replication
    cross_region_backup: bool = True
    backup_regions: List[str] = None

    def __post_init__(self):
        if self.backup_regions is None:
            self.backup_regions = ["us-east-1", "us-west-2"]


@dataclass
class SystemConfig:
    """System-wide configuration parameters."""

    # Application settings
    app_name: str = "sts-framework"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8080
    workers: int = 4

    # Runtime metadata
    build_timestamp: Optional[str] = None
    environment: Optional[str] = None

    def __post_init__(self):
        if self.build_timestamp is None:
            self.build_timestamp = datetime.now().isoformat()


class ProductionConfig:
    """
    Comprehensive production configuration manager for STS deployment.

    Manages all aspects of production configuration including:
    - Environment-specific settings
    - Security and compliance configurations
    - Performance and scaling parameters
    - Monitoring and alerting setup
    - Backup and disaster recovery
    """

    def __init__(
        self, environment: DeploymentEnvironment, config_path: Optional[str] = None
    ):
        """Initialize production configuration."""

        self.environment = environment
        self.config_path = Path(config_path) if config_path else Path("config")

        # Initialize configuration components
        self.database = DatabaseConfig()
        self.redis = RedisConfig()
        self.security = SecurityConfig()
        self.monitoring = MonitoringConfig()
        self.scaling = ScalingConfig()
        self.backup = BackupConfig()

        # Environment-specific overrides
        self._apply_environment_overrides()

        # Load custom configurations if available
        self._load_custom_configurations()

        # Validate configuration
        self._validate_configuration()

        print(f"🔧 Production config initialized for {environment.value}")

    def _apply_environment_overrides(self):
        """Apply environment-specific configuration overrides."""

        if self.environment == DeploymentEnvironment.DEVELOPMENT:
            # Development environment settings
            self.database.host = "localhost"
            self.database.backup_enabled = False
            self.security.multi_factor_auth_required = False
            self.security.compliance_level = SecurityLevel.BASIC
            self.monitoring.log_level = "DEBUG"
            self.scaling.min_replicas = 1
            self.scaling.max_replicas = 3

        elif self.environment == DeploymentEnvironment.TESTING:
            # Testing environment settings
            self.database.host = "test-db.internal"
            self.database.backup_enabled = False
            self.security.compliance_level = SecurityLevel.BASIC
            self.monitoring.metrics_retention_days = 7
            self.scaling.min_replicas = 1
            self.scaling.max_replicas = 5

        elif self.environment == DeploymentEnvironment.STAGING:
            # Staging environment (production-like)
            self.database.host = "staging-db.internal"
            self.database.backup_enabled = True
            self.database.backup_retention_days = 7
            self.security.compliance_level = SecurityLevel.ISO27001
            self.scaling.min_replicas = 2
            self.scaling.max_replicas = 10

        elif self.environment == DeploymentEnvironment.PRODUCTION:
            # Production environment settings
            self.database.host = "prod-db.internal"
            self.database.backup_enabled = True
            self.database.backup_retention_days = 90
            self.security.compliance_level = SecurityLevel.HIPAA
            self.security.audit_log_retention_days = 2555  # 7 years
            self.monitoring.metrics_retention_days = 365
            self.scaling.min_replicas = 3
            self.scaling.max_replicas = 100

        elif self.environment == DeploymentEnvironment.CLINICAL:
            # Clinical trial environment (highest security)
            self.database.host = "clinical-db.internal"
            self.database.backup_enabled = True
            self.database.backup_retention_days = 2555  # 7 years
            self.security.compliance_level = SecurityLevel.FDA_CFR21
            self.security.audit_log_retention_days = 2555
            self.security.multi_factor_auth_required = True
            self.monitoring.metrics_retention_days = 2555
            self.scaling.min_replicas = 3
            self.scaling.max_replicas = 20  # Limited scaling for stability

    def _load_custom_configurations(self):
        """Load custom configurations from files."""

        config_file = self.config_path / f"{self.environment.value}.yaml"

        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    custom_config = yaml.safe_load(f)

                # Apply custom configurations
                if "database" in custom_config:
                    self._update_dataclass(self.database, custom_config["database"])

                if "security" in custom_config:
                    self._update_dataclass(self.security, custom_config["security"])

                if "monitoring" in custom_config:
                    self._update_dataclass(self.monitoring, custom_config["monitoring"])

                if "scaling" in custom_config:
                    self._update_dataclass(self.scaling, custom_config["scaling"])

                print(f"✅ Loaded custom config from {config_file}")

            except Exception as e:
                print(f"⚠️ Failed to load custom config: {e}")

    def _update_dataclass(self, dataclass_instance: Any, updates: Dict[str, Any]):
        """Update dataclass instance with dictionary values."""

        for key, value in updates.items():
            if hasattr(dataclass_instance, key):
                setattr(dataclass_instance, key, value)

    def _validate_configuration(self):
        """Validate configuration for consistency and completeness."""

        validation_errors = []

        # Database validation
        if self.database.max_connections <= self.database.min_connections:
            validation_errors.append(
                "Database max_connections must be > min_connections"
            )

        # Security validation
        if self.security.jwt_expiration_hours <= 0:
            validation_errors.append("JWT expiration must be positive")

        # Scaling validation
        if self.scaling.max_replicas <= self.scaling.min_replicas:
            validation_errors.append("Max replicas must be > min replicas")

        # Environment-specific validation
        if self.environment == DeploymentEnvironment.PRODUCTION:
            if not self.database.backup_enabled:
                validation_errors.append("Backup must be enabled in production")

            if not self.security.audit_log_enabled:
                validation_errors.append("Audit logging must be enabled in production")

        if validation_errors:
            raise ValueError(f"Configuration validation failed: {validation_errors}")

        print("✅ Configuration validation passed")

    def get_database_url(self) -> str:
        """Generate database connection URL."""

        password = os.getenv(self.database.password_env_var)
        if not password:
            raise ValueError(
                f"Database password not found in {self.database.password_env_var}"
            )

        return (
            f"postgresql://{self.database.username}:{password}@"
            f"{self.database.host}:{self.database.port}/{self.database.database}"
        )

    def get_redis_url(self) -> str:
        """Generate Redis connection URL."""

        password = os.getenv(self.redis.password_env_var, "")
        password_part = f":{password}@" if password else ""

        return f"redis://{password_part}{self.redis.host}:{self.redis.port}/{self.redis.database}"

    def get_security_settings(self) -> Dict[str, Any]:
        """Get security settings dictionary."""

        jwt_secret = os.getenv(self.security.jwt_secret_env_var)
        if not jwt_secret:
            raise ValueError(
                f"JWT secret not found in {self.security.jwt_secret_env_var}"
            )

        return {
            "jwt_secret": jwt_secret,
            "jwt_expiration": self.security.jwt_expiration_hours * 3600,
            "mfa_required": self.security.multi_factor_auth_required,
            "rbac_enabled": self.security.rbac_enabled,
            "compliance_level": self.security.compliance_level.value,
            "rate_limit_rpm": self.security.rate_limit_requests_per_minute,
            "cors_origins": self.security.cors_allowed_origins,
        }

    def export_config(self, output_path: str):
        """Export configuration to file."""

        config_dict = {
            "environment": self.environment.value,
            "database": asdict(self.database),
            "redis": asdict(self.redis),
            "security": asdict(self.security),
            "monitoring": asdict(self.monitoring),
            "scaling": asdict(self.scaling),
            "backup": asdict(self.backup),
            "export_timestamp": datetime.now().isoformat(),
        }

        # Convert enums to strings
        config_dict["security"][
            "compliance_level"
        ] = self.security.compliance_level.value

        output_file = Path(output_path)

        if output_file.suffix.lower() == ".yaml":
            with open(output_file, "w") as f:
                yaml.dump(config_dict, f, default_flow_style=False, sort_keys=True)
        else:
            with open(output_file, "w") as f:
                json.dump(config_dict, f, indent=2, sort_keys=True)

        print(f"✅ Configuration exported to {output_file}")

    def generate_docker_env(self) -> Dict[str, str]:
        """Generate environment variables for Docker containers."""

        env_vars = {
            # Application settings
            "STS_ENVIRONMENT": self.environment.value,
            "STS_LOG_LEVEL": self.monitoring.log_level,
            "STS_DEBUG": str(self.environment == DeploymentEnvironment.DEVELOPMENT),
            # Database settings
            "STS_DB_HOST": self.database.host,
            "STS_DB_PORT": str(self.database.port),
            "STS_DB_NAME": self.database.database,
            "STS_DB_USER": self.database.username,
            "STS_DB_MIN_CONN": str(self.database.min_connections),
            "STS_DB_MAX_CONN": str(self.database.max_connections),
            # Redis settings
            "STS_REDIS_HOST": self.redis.host,
            "STS_REDIS_PORT": str(self.redis.port),
            "STS_REDIS_DB": str(self.redis.database),
            "STS_REDIS_MAX_CONN": str(self.redis.max_connections),
            # Security settings
            "STS_AUTH_METHOD": self.security.authentication_method,
            "STS_JWT_EXPIRATION": str(self.security.jwt_expiration_hours * 3600),
            "STS_MFA_REQUIRED": str(self.security.multi_factor_auth_required),
            "STS_RBAC_ENABLED": str(self.security.rbac_enabled),
            "STS_COMPLIANCE_LEVEL": self.security.compliance_level.value,
            # Monitoring settings
            "STS_METRICS_ENABLED": str(self.monitoring.metrics_enabled),
            "STS_TRACING_ENABLED": str(self.monitoring.distributed_tracing_enabled),
            "STS_JAEGER_ENDPOINT": self.monitoring.jaeger_endpoint,
            # Scaling settings
            "STS_MIN_REPLICAS": str(self.scaling.min_replicas),
            "STS_MAX_REPLICAS": str(self.scaling.max_replicas),
            "STS_CPU_REQUEST": self.scaling.cpu_request,
            "STS_CPU_LIMIT": self.scaling.cpu_limit,
            "STS_MEMORY_REQUEST": self.scaling.memory_request,
            "STS_MEMORY_LIMIT": self.scaling.memory_limit,
        }

        return env_vars

    def generate_kubernetes_configmap(self) -> Dict[str, Any]:
        """Generate Kubernetes ConfigMap specification."""

        configmap = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": f"sts-config-{self.environment.value}",
                "labels": {
                    "app": "sensory-tracer-science",
                    "environment": self.environment.value,
                    "component": "configuration",
                },
            },
            "data": self.generate_docker_env(),
        }

        return configmap

    def generate_deployment_summary(self) -> str:
        """Generate deployment configuration summary."""

        summary = f"""
SENSORY TRACER SCIENCE (STS) - DEPLOYMENT CONFIGURATION
======================================================

ENVIRONMENT: {self.environment.value.upper()}
Configuration Generated: {datetime.now().isoformat()}

DATABASE CONFIGURATION:
----------------------
Host: {self.database.host}:{self.database.port}
Database: {self.database.database}
Connection Pool: {self.database.min_connections}-{self.database.max_connections}
Backup Enabled: {self.database.backup_enabled}
SSL Enabled: {self.database.ssl_enabled}

SECURITY CONFIGURATION:
----------------------
Compliance Level: {self.security.compliance_level.value.upper()}
Multi-Factor Auth: {self.security.multi_factor_auth_required}
RBAC Enabled: {self.security.rbac_enabled}
Audit Logging: {self.security.audit_log_enabled}
Rate Limiting: {self.security.rate_limit_requests_per_minute} req/min

SCALING CONFIGURATION:
---------------------
Replicas: {self.scaling.min_replicas}-{self.scaling.max_replicas}
CPU Target: {self.scaling.target_cpu_utilization}%
Memory Target: {self.scaling.target_memory_utilization}%
Resource Limits: {self.scaling.cpu_limit} CPU, {self.scaling.memory_limit} Memory

MONITORING CONFIGURATION:
------------------------
Metrics Enabled: {self.monitoring.metrics_enabled}
Log Level: {self.monitoring.log_level}
Distributed Tracing: {self.monitoring.distributed_tracing_enabled}
Alert Channels: {', '.join(self.monitoring.alert_channels)}

BACKUP CONFIGURATION:
--------------------
Backup Enabled: {self.backup.backup_enabled}
Retention: {self.backup.backup_retention_days} days
Cross-Region: {self.backup.cross_region_backup}
RTO: {self.backup.rto_minutes} minutes
RPO: {self.backup.rpo_minutes} minutes

STATUS: READY FOR DEPLOYMENT
============================
"""

        return summary


def create_production_configs():
    """Create production configurations for all environments."""

    print("🏗️ Creating Production Configurations")
    print("=" * 50)

    environments = [
        DeploymentEnvironment.DEVELOPMENT,
        DeploymentEnvironment.TESTING,
        DeploymentEnvironment.STAGING,
        DeploymentEnvironment.PRODUCTION,
        DeploymentEnvironment.CLINICAL,
    ]

    for env in environments:
        print(f"\n📝 Configuring {env.value} environment...")

        config = ProductionConfig(env)

        # Export configuration
        config.export_config(f"config/sts-{env.value}.yaml")

        # Generate Kubernetes ConfigMap
        configmap = config.generate_kubernetes_configmap()
        with open(f"config/sts-configmap-{env.value}.yaml", "w") as f:
            yaml.dump(configmap, f, default_flow_style=False)

        print(f"✅ {env.value} configuration created")

    print("\n🎉 All production configurations created successfully!")


if __name__ == "__main__":
    create_production_configs()
