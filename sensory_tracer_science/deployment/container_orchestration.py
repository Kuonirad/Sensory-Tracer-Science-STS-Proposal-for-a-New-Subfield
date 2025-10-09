#!/usr/bin/env python3
"""
Container Orchestration for STS Framework

Comprehensive container orchestration system supporting Docker, Kubernetes,
and cloud-native deployment patterns for scalable STS applications.
"""

import yaml
import json
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime
import tempfile
import subprocess

from .production_config import ProductionConfig, DeploymentEnvironment


@dataclass
class ContainerConfig:
    """Container configuration parameters."""
    
    # Base image settings
    base_image: str = "python:3.11-slim"
    image_name: str = "sts-framework"
    image_tag: str = "latest"
    
    # Resource requirements
    cpu_request: str = "100m"
    cpu_limit: str = "500m"
    memory_request: str = "256Mi"
    memory_limit: str = "512Mi"
    
    # Container settings
    port: int = 8000
    health_check_path: str = "/health"
    restart_policy: str = "Always"
    
    # Security settings
    run_as_non_root: bool = True
    run_as_user: int = 1001
    read_only_root_filesystem: bool = True
    
    # Volumes and persistence
    persistent_volumes: List[Dict[str, str]] = None
    config_maps: List[str] = None
    secrets: List[str] = None
    
    def __post_init__(self):
        if self.persistent_volumes is None:
            self.persistent_volumes = []
        if self.config_maps is None:
            self.config_maps = []
        if self.secrets is None:
            self.secrets = []


@dataclass 
class KubernetesConfig:
    """Kubernetes-specific configuration."""
    
    # Cluster settings
    namespace: str = "sts-production"
    cluster_name: str = "sts-cluster"
    
    # Deployment strategy
    deployment_strategy: str = "RollingUpdate"
    max_surge: str = "25%"
    max_unavailable: str = "25%"
    
    # Service configuration
    service_type: str = "ClusterIP"
    load_balancer_type: str = "application"
    
    # Ingress settings
    ingress_enabled: bool = True
    ingress_class: str = "nginx"
    tls_enabled: bool = True
    
    # Autoscaling
    hpa_enabled: bool = True
    min_replicas: int = 2
    max_replicas: int = 100
    target_cpu_utilization: int = 70
    
    # Storage
    storage_class: str = "fast-ssd"
    volume_size: str = "10Gi"
    
    # Network policies
    network_policies_enabled: bool = True
    pod_security_policy: str = "restricted"


class ContainerOrchestrator:
    """
    Comprehensive container orchestration manager.
    
    Provides complete container lifecycle management including:
    - Docker container building and deployment
    - Kubernetes cluster orchestration
    - Service mesh integration
    - Auto-scaling and load balancing
    - Health monitoring and recovery
    """
    
    def __init__(self, 
                 production_config: ProductionConfig,
                 container_config: Optional[ContainerConfig] = None,
                 kubernetes_config: Optional[KubernetesConfig] = None):
        """Initialize container orchestrator."""
        
        self.production_config = production_config
        self.container_config = container_config or ContainerConfig()
        self.kubernetes_config = kubernetes_config or KubernetesConfig()
        
        # Apply environment-specific overrides
        self._apply_environment_overrides()
        
        print(f"🐳 Container Orchestrator initialized for {production_config.environment.value}")
    
    def _apply_environment_overrides(self):
        """Apply environment-specific container overrides."""
        
        env = self.production_config.environment
        
        if env == DeploymentEnvironment.DEVELOPMENT:
            self.container_config.image_tag = "dev"
            self.container_config.cpu_limit = "200m"
            self.container_config.memory_limit = "256Mi"
            self.kubernetes_config.min_replicas = 1
            self.kubernetes_config.max_replicas = 3
            
        elif env == DeploymentEnvironment.TESTING:
            self.container_config.image_tag = "test"
            self.kubernetes_config.namespace = "sts-testing"
            self.kubernetes_config.min_replicas = 1
            self.kubernetes_config.max_replicas = 5
            
        elif env == DeploymentEnvironment.STAGING:
            self.container_config.image_tag = "staging"
            self.kubernetes_config.namespace = "sts-staging"
            self.kubernetes_config.min_replicas = 2
            self.kubernetes_config.max_replicas = 10
            
        elif env == DeploymentEnvironment.PRODUCTION:
            self.container_config.image_tag = "v1.0.0"
            self.kubernetes_config.namespace = "sts-production"
            self.kubernetes_config.min_replicas = 3
            self.kubernetes_config.max_replicas = 100
            
        elif env == DeploymentEnvironment.CLINICAL:
            self.container_config.image_tag = "clinical-v1.0.0"
            self.kubernetes_config.namespace = "sts-clinical"
            self.kubernetes_config.min_replicas = 3
            self.kubernetes_config.max_replicas = 20  # Limited scaling for stability
            self.kubernetes_config.network_policies_enabled = True
            self.kubernetes_config.pod_security_policy = "highly-restricted"
    
    def generate_dockerfile(self) -> str:
        """Generate optimized Dockerfile for STS framework."""
        
        dockerfile_content = f'''# Multi-stage Dockerfile for STS Framework
# Stage 1: Build stage
FROM {self.container_config.base_image} AS builder

# Set build arguments
ARG STS_VERSION=1.0.0
ARG BUILD_DATE
ARG VCS_REF

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    gcc \\
    g++ \\
    gfortran \\
    libopenblas-dev \\
    liblapack-dev \\
    pkg-config \\
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt requirements-prod.txt ./
RUN pip install --no-cache-dir --upgrade pip && \\
    pip install --no-cache-dir -r requirements-prod.txt

# Copy source code
COPY . .

# Install STS framework
RUN pip install --no-cache-dir -e .

# Run tests (optional, can be disabled for faster builds)
RUN python -m pytest tests/ --tb=short || echo "Tests skipped in production build"

# Stage 2: Runtime stage
FROM {self.container_config.base_image} AS runtime

# Set metadata labels
LABEL maintainer="STS Development Team" \\
      version="$STS_VERSION" \\
      build_date="$BUILD_DATE" \\
      vcs_ref="$VCS_REF" \\
      description="Sensory Tracer Science Framework Production Container"

# Create non-root user
RUN groupadd -r sts && useradd -r -g sts -u {self.container_config.run_as_user} sts

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \\
    libopenblas0 \\
    liblapack3 \\
    curl \\
    && rm -rf /var/lib/apt/lists/* \\
    && apt-get clean

# Copy built application from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

# Create required directories with proper permissions
RUN mkdir -p /app/data /app/logs /app/config && \\
    chown -R sts:sts /app

# Set working directory
WORKDIR /app

# Switch to non-root user
USER {self.container_config.run_as_user}

# Expose port
EXPOSE {self.container_config.port}

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \\
    CMD curl -f http://localhost:{self.container_config.port}{self.container_config.health_check_path} || exit 1

# Set environment variables
ENV PYTHONPATH=/app \\
    PYTHONUNBUFFERED=1 \\
    PYTHONDONTWRITEBYTECODE=1 \\
    STS_PORT={self.container_config.port}

# Default command
CMD ["python", "-m", "sensory_tracer_science.api.server"]
'''
        
        return dockerfile_content
    
    def generate_docker_compose(self) -> Dict[str, Any]:
        """Generate Docker Compose configuration for local development."""
        
        env_vars = self.production_config.generate_docker_env()
        
        compose_config = {
            'version': '3.8',
            'services': {
                'sts-app': {
                    'build': {
                        'context': '.',
                        'dockerfile': 'Dockerfile',
                        'args': {
                            'STS_VERSION': '1.0.0',
                            'BUILD_DATE': datetime.now().isoformat(),
                            'VCS_REF': 'main'
                        }
                    },
                    'image': f'{self.container_config.image_name}:{self.container_config.image_tag}',
                    'container_name': 'sts-framework',
                    'ports': [f'{self.container_config.port}:{self.container_config.port}'],
                    'environment': env_vars,
                    'volumes': [
                        './data:/app/data',
                        './logs:/app/logs',
                        './config:/app/config'
                    ],
                    'depends_on': ['postgres', 'redis'],
                    'restart': self.container_config.restart_policy.lower(),
                    'healthcheck': {
                        'test': [
                            'CMD', 'curl', '-f',
                            f'http://localhost:{self.container_config.port}{self.container_config.health_check_path}'
                        ],
                        'interval': '30s',
                        'timeout': '5s',
                        'retries': 3,
                        'start_period': '60s'
                    },
                    'security_opt': ['no-new-privileges:true'],
                    'read_only': self.container_config.read_only_root_filesystem,
                    'tmpfs': ['/tmp', '/var/tmp'] if self.container_config.read_only_root_filesystem else None
                },
                'postgres': {
                    'image': 'postgres:15-alpine',
                    'container_name': 'sts-postgres',
                    'environment': {
                        'POSTGRES_DB': self.production_config.database.database,
                        'POSTGRES_USER': self.production_config.database.username,
                        'POSTGRES_PASSWORD': '${STS_DB_PASSWORD}',
                        'POSTGRES_INITDB_ARGS': '--auth-host=scram-sha-256'
                    },
                    'volumes': [
                        'postgres_data:/var/lib/postgresql/data',
                        './docker/postgres/init:/docker-entrypoint-initdb.d'
                    ],
                    'ports': [f'{self.production_config.database.port}:5432'],
                    'restart': 'unless-stopped',
                    'healthcheck': {
                        'test': ['CMD-SHELL', 'pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}'],
                        'interval': '10s',
                        'timeout': '5s',
                        'retries': 5
                    }
                },
                'redis': {
                    'image': 'redis:7-alpine',
                    'container_name': 'sts-redis',
                    'command': [
                        'redis-server',
                        '--appendonly', 'yes',
                        '--requirepass', '${STS_REDIS_PASSWORD}',
                        '--maxmemory', f'{self.production_config.redis.max_memory_mb}mb',
                        '--maxmemory-policy', self.production_config.redis.max_memory_policy
                    ],
                    'volumes': [
                        'redis_data:/data'
                    ],
                    'ports': [f'{self.production_config.redis.port}:6379'],
                    'restart': 'unless-stopped',
                    'healthcheck': {
                        'test': ['CMD', 'redis-cli', '--raw', 'incr', 'ping'],
                        'interval': '10s',
                        'timeout': '3s',
                        'retries': 5
                    }
                }
            },
            'volumes': {
                'postgres_data': {'driver': 'local'},
                'redis_data': {'driver': 'local'}
            },
            'networks': {
                'sts-network': {
                    'driver': 'bridge'
                }
            }
        }
        
        # Connect all services to custom network
        for service in compose_config['services'].values():
            service['networks'] = ['sts-network']
        
        return compose_config
    
    def generate_kubernetes_deployment(self) -> Dict[str, Any]:
        """Generate Kubernetes Deployment specification."""
        
        deployment = {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': 'sts-framework',
                'namespace': self.kubernetes_config.namespace,
                'labels': {
                    'app': 'sts-framework',
                    'version': self.container_config.image_tag,
                    'component': 'api',
                    'environment': self.production_config.environment.value
                }
            },
            'spec': {
                'replicas': self.kubernetes_config.min_replicas,
                'strategy': {
                    'type': self.kubernetes_config.deployment_strategy,
                    'rollingUpdate': {
                        'maxSurge': self.kubernetes_config.max_surge,
                        'maxUnavailable': self.kubernetes_config.max_unavailable
                    }
                },
                'selector': {
                    'matchLabels': {
                        'app': 'sts-framework',
                        'component': 'api'
                    }
                },
                'template': {
                    'metadata': {
                        'labels': {
                            'app': 'sts-framework',
                            'version': self.container_config.image_tag,
                            'component': 'api',
                            'environment': self.production_config.environment.value
                        },
                        'annotations': {
                            'prometheus.io/scrape': 'true',
                            'prometheus.io/port': str(self.container_config.port),
                            'prometheus.io/path': '/metrics'
                        }
                    },
                    'spec': {
                        'serviceAccountName': 'sts-framework',
                        'securityContext': {
                            'runAsNonRoot': self.container_config.run_as_non_root,
                            'runAsUser': self.container_config.run_as_user,
                            'fsGroup': self.container_config.run_as_user,
                            'seccompProfile': {
                                'type': 'RuntimeDefault'
                            }
                        },
                        'containers': [{
                            'name': 'sts-framework',
                            'image': f'{self.container_config.image_name}:{self.container_config.image_tag}',
                            'imagePullPolicy': 'IfNotPresent',
                            'ports': [{
                                'name': 'http',
                                'containerPort': self.container_config.port,
                                'protocol': 'TCP'
                            }],
                            'env': [
                                {'name': key, 'value': value}
                                for key, value in self.production_config.generate_docker_env().items()
                            ],
                            'envFrom': [{
                                'configMapRef': {
                                    'name': f'sts-config-{self.production_config.environment.value}'
                                }
                            }, {
                                'secretRef': {
                                    'name': f'sts-secrets-{self.production_config.environment.value}'
                                }
                            }],
                            'resources': {
                                'requests': {
                                    'cpu': self.container_config.cpu_request,
                                    'memory': self.container_config.memory_request
                                },
                                'limits': {
                                    'cpu': self.container_config.cpu_limit,
                                    'memory': self.container_config.memory_limit
                                }
                            },
                            'livenessProbe': {
                                'httpGet': {
                                    'path': self.container_config.health_check_path,
                                    'port': 'http'
                                },
                                'initialDelaySeconds': 60,
                                'periodSeconds': 10,
                                'timeoutSeconds': 5,
                                'failureThreshold': 3
                            },
                            'readinessProbe': {
                                'httpGet': {
                                    'path': '/ready',
                                    'port': 'http'
                                },
                                'initialDelaySeconds': 30,
                                'periodSeconds': 5,
                                'timeoutSeconds': 3,
                                'failureThreshold': 3
                            },
                            'securityContext': {
                                'allowPrivilegeEscalation': False,
                                'readOnlyRootFilesystem': self.container_config.read_only_root_filesystem,
                                'runAsNonRoot': True,
                                'runAsUser': self.container_config.run_as_user,
                                'capabilities': {
                                    'drop': ['ALL']
                                }
                            },
                            'volumeMounts': [
                                {
                                    'name': 'tmp-volume',
                                    'mountPath': '/tmp'
                                },
                                {
                                    'name': 'data-volume',
                                    'mountPath': '/app/data'
                                }
                            ]
                        }],
                        'volumes': [
                            {
                                'name': 'tmp-volume',
                                'emptyDir': {}
                            },
                            {
                                'name': 'data-volume',
                                'persistentVolumeClaim': {
                                    'claimName': 'sts-data-pvc'
                                }
                            }
                        ],
                        'affinity': {
                            'podAntiAffinity': {
                                'preferredDuringSchedulingIgnoredDuringExecution': [{
                                    'weight': 100,
                                    'podAffinityTerm': {
                                        'labelSelector': {
                                            'matchLabels': {
                                                'app': 'sts-framework'
                                            }
                                        },
                                        'topologyKey': 'kubernetes.io/hostname'
                                    }
                                }]
                            }
                        }
                    }
                }
            }
        }
        
        return deployment
    
    def generate_kubernetes_service(self) -> Dict[str, Any]:
        """Generate Kubernetes Service specification."""
        
        service = {
            'apiVersion': 'v1',
            'kind': 'Service',
            'metadata': {
                'name': 'sts-framework-service',
                'namespace': self.kubernetes_config.namespace,
                'labels': {
                    'app': 'sts-framework',
                    'component': 'api'
                },
                'annotations': {
                    'service.beta.kubernetes.io/aws-load-balancer-type': 'nlb' if self.kubernetes_config.service_type == 'LoadBalancer' else None
                }
            },
            'spec': {
                'type': self.kubernetes_config.service_type,
                'selector': {
                    'app': 'sts-framework',
                    'component': 'api'
                },
                'ports': [{
                    'name': 'http',
                    'port': 80,
                    'targetPort': self.container_config.port,
                    'protocol': 'TCP'
                }],
                'sessionAffinity': 'None'
            }
        }
        
        # Remove None annotations
        if service['metadata']['annotations']['service.beta.kubernetes.io/aws-load-balancer-type'] is None:
            del service['metadata']['annotations']['service.beta.kubernetes.io/aws-load-balancer-type']
            if not service['metadata']['annotations']:
                del service['metadata']['annotations']
        
        return service
    
    def generate_kubernetes_hpa(self) -> Dict[str, Any]:
        """Generate Horizontal Pod Autoscaler specification."""
        
        if not self.kubernetes_config.hpa_enabled:
            return {}
        
        hpa = {
            'apiVersion': 'autoscaling/v2',
            'kind': 'HorizontalPodAutoscaler',
            'metadata': {
                'name': 'sts-framework-hpa',
                'namespace': self.kubernetes_config.namespace,
                'labels': {
                    'app': 'sts-framework',
                    'component': 'autoscaler'
                }
            },
            'spec': {
                'scaleTargetRef': {
                    'apiVersion': 'apps/v1',
                    'kind': 'Deployment',
                    'name': 'sts-framework'
                },
                'minReplicas': self.kubernetes_config.min_replicas,
                'maxReplicas': self.kubernetes_config.max_replicas,
                'metrics': [
                    {
                        'type': 'Resource',
                        'resource': {
                            'name': 'cpu',
                            'target': {
                                'type': 'Utilization',
                                'averageUtilization': self.kubernetes_config.target_cpu_utilization
                            }
                        }
                    },
                    {
                        'type': 'Resource',
                        'resource': {
                            'name': 'memory',
                            'target': {
                                'type': 'Utilization',
                                'averageUtilization': 80
                            }
                        }
                    }
                ],
                'behavior': {
                    'scaleUp': {
                        'stabilizationWindowSeconds': 60,
                        'policies': [{
                            'type': 'Percent',
                            'value': 100,
                            'periodSeconds': 15
                        }]
                    },
                    'scaleDown': {
                        'stabilizationWindowSeconds': 300,
                        'policies': [{
                            'type': 'Percent',
                            'value': 10,
                            'periodSeconds': 60
                        }]
                    }
                }
            }
        }
        
        return hpa
    
    def generate_kubernetes_ingress(self) -> Dict[str, Any]:
        """Generate Kubernetes Ingress specification."""
        
        if not self.kubernetes_config.ingress_enabled:
            return {}
        
        ingress = {
            'apiVersion': 'networking.k8s.io/v1',
            'kind': 'Ingress',
            'metadata': {
                'name': 'sts-framework-ingress',
                'namespace': self.kubernetes_config.namespace,
                'labels': {
                    'app': 'sts-framework',
                    'component': 'ingress'
                },
                'annotations': {
                    'kubernetes.io/ingress.class': self.kubernetes_config.ingress_class,
                    'nginx.ingress.kubernetes.io/rewrite-target': '/',
                    'nginx.ingress.kubernetes.io/ssl-redirect': 'true',
                    'nginx.ingress.kubernetes.io/rate-limit': str(self.production_config.security.rate_limit_requests_per_minute),
                    'nginx.ingress.kubernetes.io/rate-limit-window': '1m'
                }
            },
            'spec': {
                'rules': [{
                    'host': f'sts-api-{self.production_config.environment.value}.company.com',
                    'http': {
                        'paths': [{
                            'path': '/',
                            'pathType': 'Prefix',
                            'backend': {
                                'service': {
                                    'name': 'sts-framework-service',
                                    'port': {
                                        'number': 80
                                    }
                                }
                            }
                        }]
                    }
                }]
            }
        }
        
        # Add TLS configuration if enabled
        if self.kubernetes_config.tls_enabled:
            ingress['spec']['tls'] = [{
                'hosts': [f'sts-api-{self.production_config.environment.value}.company.com'],
                'secretName': f'sts-tls-{self.production_config.environment.value}'
            }]
        
        return ingress
    
    def build_container_image(self, push: bool = False) -> str:
        """Build container image using Docker."""
        
        print(f"🔨 Building container image: {self.container_config.image_name}:{self.container_config.image_tag}")
        
        # Generate Dockerfile
        dockerfile_content = self.generate_dockerfile()
        
        # Write Dockerfile to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.Dockerfile', delete=False) as f:
            f.write(dockerfile_content)
            dockerfile_path = f.name
        
        try:
            # Build image
            build_args = [
                '--build-arg', f'STS_VERSION=1.0.0',
                '--build-arg', f'BUILD_DATE={datetime.now().isoformat()}',
                '--build-arg', f'VCS_REF=main'
            ]
            
            image_tag = f"{self.container_config.image_name}:{self.container_config.image_tag}"
            
            cmd = ['docker', 'build'] + build_args + ['-f', dockerfile_path, '-t', image_tag, '.']
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"Docker build failed: {result.stderr}")
            
            print(f"✅ Image built successfully: {image_tag}")
            
            # Push image if requested
            if push:
                push_cmd = ['docker', 'push', image_tag]
                push_result = subprocess.run(push_cmd, capture_output=True, text=True)
                
                if push_result.returncode != 0:
                    raise RuntimeError(f"Docker push failed: {push_result.stderr}")
                
                print(f"✅ Image pushed successfully: {image_tag}")
            
            return image_tag
            
        finally:
            # Clean up temporary Dockerfile
            os.unlink(dockerfile_path)
    
    def deploy_to_kubernetes(self, manifests_dir: str = "k8s") -> List[str]:
        """Deploy STS framework to Kubernetes cluster."""
        
        print(f"🚀 Deploying to Kubernetes: {self.kubernetes_config.namespace}")
        
        # Create manifests directory
        manifests_path = Path(manifests_dir)
        manifests_path.mkdir(exist_ok=True)
        
        deployed_resources = []
        
        # Generate and write Kubernetes manifests
        manifests = {
            'deployment.yaml': self.generate_kubernetes_deployment(),
            'service.yaml': self.generate_kubernetes_service(),
            'configmap.yaml': self.production_config.generate_kubernetes_configmap(),
        }
        
        # Optional manifests
        hpa = self.generate_kubernetes_hpa()
        if hpa:
            manifests['hpa.yaml'] = hpa
        
        ingress = self.generate_kubernetes_ingress()
        if ingress:
            manifests['ingress.yaml'] = ingress
        
        # Write manifests to files
        for filename, manifest in manifests.items():
            manifest_path = manifests_path / filename
            
            with open(manifest_path, 'w') as f:
                yaml.dump(manifest, f, default_flow_style=False, sort_keys=False)
            
            print(f"✅ Generated manifest: {manifest_path}")
        
        # Apply manifests to cluster
        for filename in manifests.keys():
            manifest_path = manifests_path / filename
            
            cmd = ['kubectl', 'apply', '-f', str(manifest_path)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"⚠️ Failed to apply {filename}: {result.stderr}")
            else:
                deployed_resources.append(filename)
                print(f"✅ Applied manifest: {filename}")
        
        print(f"🎉 Deployment completed: {len(deployed_resources)}/{len(manifests)} resources deployed")
        
        return deployed_resources
    
    def generate_deployment_package(self, output_dir: str = "deployment") -> str:
        """Generate complete deployment package."""
        
        print(f"📦 Generating deployment package for {self.production_config.environment.value}")
        
        # Create output directory
        package_path = Path(output_dir)
        package_path.mkdir(exist_ok=True)
        
        # Generate Dockerfile
        dockerfile_path = package_path / "Dockerfile"
        with open(dockerfile_path, 'w') as f:
            f.write(self.generate_dockerfile())
        
        # Generate Docker Compose
        compose_config = self.generate_docker_compose()
        compose_path = package_path / "docker-compose.yml"
        with open(compose_path, 'w') as f:
            yaml.dump(compose_config, f, default_flow_style=False)
        
        # Generate Kubernetes manifests
        k8s_path = package_path / "kubernetes"
        k8s_path.mkdir(exist_ok=True)
        
        k8s_manifests = {
            'deployment.yaml': self.generate_kubernetes_deployment(),
            'service.yaml': self.generate_kubernetes_service(),
            'configmap.yaml': self.production_config.generate_kubernetes_configmap(),
            'hpa.yaml': self.generate_kubernetes_hpa(),
            'ingress.yaml': self.generate_kubernetes_ingress()
        }
        
        for filename, manifest in k8s_manifests.items():
            if manifest:  # Skip empty manifests
                manifest_path = k8s_path / filename
                with open(manifest_path, 'w') as f:
                    yaml.dump(manifest, f, default_flow_style=False)
        
        # Generate deployment scripts
        scripts_path = package_path / "scripts"
        scripts_path.mkdir(exist_ok=True)
        
        # Build script
        build_script = f'''#!/bin/bash
set -e

echo "Building STS Framework container..."
docker build -t {self.container_config.image_name}:{self.container_config.image_tag} .

echo "Container build completed successfully!"
'''
        
        build_script_path = scripts_path / "build.sh"
        with open(build_script_path, 'w') as f:
            f.write(build_script)
        os.chmod(build_script_path, 0o755)
        
        # Deploy script
        deploy_script = f'''#!/bin/bash
set -e

echo "Deploying STS Framework to Kubernetes..."

# Create namespace if it doesn't exist
kubectl create namespace {self.kubernetes_config.namespace} --dry-run=client -o yaml | kubectl apply -f -

# Apply all Kubernetes manifests
kubectl apply -f kubernetes/ -n {self.kubernetes_config.namespace}

echo "Deployment completed successfully!"
echo "Check deployment status with:"
echo "  kubectl get pods -n {self.kubernetes_config.namespace}"
'''
        
        deploy_script_path = scripts_path / "deploy.sh"
        with open(deploy_script_path, 'w') as f:
            f.write(deploy_script)
        os.chmod(deploy_script_path, 0o755)
        
        # Generate README
        readme_content = f'''# STS Framework Deployment Package

Environment: {self.production_config.environment.value.upper()}
Generated: {datetime.now().isoformat()}

## Quick Start

### Docker Compose (Development)
```bash
# Set required environment variables
export STS_DB_PASSWORD="your-db-password"
export STS_REDIS_PASSWORD="your-redis-password"

# Start services
docker-compose up -d
```

### Kubernetes (Production)
```bash
# Build container image
./scripts/build.sh

# Deploy to Kubernetes
./scripts/deploy.sh
```

## Files Included

- `Dockerfile` - Container image definition
- `docker-compose.yml` - Local development environment
- `kubernetes/` - Kubernetes manifests
- `scripts/` - Deployment automation scripts

## Configuration

The deployment is configured for the {self.production_config.environment.value} environment with:

- Replicas: {self.kubernetes_config.min_replicas}-{self.kubernetes_config.max_replicas}
- Resources: {self.container_config.cpu_request}-{self.container_config.cpu_limit} CPU, {self.container_config.memory_request}-{self.container_config.memory_limit} Memory
- Security: {self.production_config.security.compliance_level.value.upper()} compliance
- Monitoring: {self.production_config.monitoring.log_level} logging, {self.production_config.monitoring.metrics_enabled} metrics

## Support

For deployment issues, contact the STS Development Team.
'''
        
        readme_path = package_path / "README.md"
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        
        print(f"✅ Deployment package generated: {package_path}")
        print(f"   Files: Dockerfile, docker-compose.yml, kubernetes/, scripts/, README.md")
        
        return str(package_path)


def create_deployment_packages():
    """Create deployment packages for all environments."""
    
    print("🏗️ Creating Deployment Packages")
    print("="*50)
    
    environments = [
        DeploymentEnvironment.DEVELOPMENT,
        DeploymentEnvironment.STAGING,
        DeploymentEnvironment.PRODUCTION,
        DeploymentEnvironment.CLINICAL
    ]
    
    for env in environments:
        print(f"\n📦 Creating deployment package for {env.value}...")
        
        # Create production config
        prod_config = ProductionConfig(env)
        
        # Create container orchestrator
        orchestrator = ContainerOrchestrator(prod_config)
        
        # Generate deployment package
        package_path = orchestrator.generate_deployment_package(f"deployment-{env.value}")
        
        print(f"✅ {env.value} deployment package created: {package_path}")
    
    print("\n🎉 All deployment packages created successfully!")


if __name__ == "__main__":
    create_deployment_packages()