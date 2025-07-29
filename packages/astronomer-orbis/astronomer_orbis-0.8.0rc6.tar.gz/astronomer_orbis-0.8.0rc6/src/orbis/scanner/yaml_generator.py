from datetime import datetime
from pathlib import Path

from jinja2 import Template

from orbis.scanner.models import ScannerConfig
from orbis.utils.logger import get_early_logger


class YamlGenerator:
    """Generate YAML manifests for scanner operations."""

    def __init__(self):
        self.logger = get_early_logger()

    def generate_service_account_yaml(self, config: ScannerConfig) -> str:
        """Generate service account and role binding YAML."""
        template_content = """
apiVersion: v1
kind: ServiceAccount
metadata:
  labels:
    app: support-bundle
    component: scanner
  name: {{ sa_name }}
  namespace: {{ namespace }}
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: read-support-bundle
  labels:
    app: support-bundle
    component: scanner
rules:
  - apiGroups: [""]
    resources:
      - namespaces
      - pods
      - pods/log
      - pods/status
      - pods/ephemeralcontainers
      - configmaps
      - secrets
      - services
      - persistentvolumes
      - persistentvolumeclaims
      - endpoints
      - events
      - resourcequotas
      - limitranges
      - replicationcontrollers
      - nodes
    verbs: ["get", "list", "watch"]
  - apiGroups: ["apps"]
    resources:
      - deployments
      - daemonsets
      - statefulsets
      - replicasets
    verbs: ["get", "list", "watch"]
  - apiGroups: ["batch"]
    resources:
      - jobs
      - cronjobs
    verbs: ["get", "list", "watch"]
  - apiGroups: ["networking.k8s.io"]
    resources:
      - ingresses
      - networkpolicies
    verbs: ["get", "list", "watch"]
  - apiGroups: ["apiextensions.k8s.io"]
    resources:
      - customresourcedefinitions
    verbs: ["get", "list", "watch"]
  - apiGroups: ["operators.coreos.com"]
    resources: ["*"]
    verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  labels:
    app: support-bundle
    component: scanner
  name: {{ role_binding_name }}
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
  - kind: ServiceAccount
    name: {{ sa_name }}
    namespace: {{ namespace }}
"""

        template = Template(template_content)
        return template.render(sa_name=config.service_account_name, role_binding_name=config.role_binding_name, namespace=config.namespace).strip()

    def generate_job_yaml(self, config: ScannerConfig) -> str:
        """Generate scanner job YAML."""
        scanner_args = config.build_scanner_command_args()
        scanner_command = f"scanner.py {' '.join(scanner_args)} && cp /data/*.tar.gz /results/"

        template_content = """
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ job_name }}
  namespace: {{ namespace }}
  labels:
    app: support-bundle
    component: scanner
spec:
  backoffLimit: 0
  template:
    metadata:
      labels:
        app: support-bundle
        component: scanner
    spec:
      serviceAccountName: {{ sa_name }}
      initContainers:
      - name: scanner-init
        image: {{ image }}
        command: ["/bin/bash", "-c"]
        args:
                  - |
          {{ scanner_command }}
        volumeMounts:
        - name: results-file
          mountPath: /results
        resources:
          limits:
            memory: "{{ memory }}"
            cpu: "{{ cpu }}"
          requests:
            memory: "200Mi"
            cpu: "200m"
      containers:
      - name: main
        image: {{ image }}
        command: ["/bin/bash", "-c"]
        args:
          - |
            echo "Data collection complete. Sleeping for {{ sleep_duration }}"
            sleep {{ sleep_duration }}
        volumeMounts:
        - name: results-file
          mountPath: /results
        resources:
          limits:
            memory: "200Mi"
            cpu: "200m"
          requests:
            memory: "100Mi"
            cpu: "100m"
      restartPolicy: Never
      volumes:
      - name: results-file
        emptyDir: {}
"""

        template = Template(template_content)
        return template.render(
            job_name=config.job_name,
            namespace=config.namespace,
            sa_name=config.service_account_name,
            image=config.image,
            scanner_command=scanner_command,
            memory=config.memory,
            cpu=config.cpu,
            sleep_duration=config.sleep_duration,
        ).strip()

    def generate_support_bundle(self, config: ScannerConfig) -> str:
        """Generate complete support bundle YAML with instructions."""
        sa_yaml = self.generate_service_account_yaml(config)
        job_yaml = self.generate_job_yaml(config)

        instructions = f"""# =============================================================================
# ASTRONOMER Scanner - Support Bundle Generation
# =============================================================================
#
# Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
# Namespace: {config.namespace}
# Customer: {config.customer_name or "N/A"}
# Cluster: {config.cluster_name or "N/A"}
#
# Instructions for the infrastructure team:
# 1. Save this YAML to a file (e.g., scanner-bundle.yaml)
# 2. Apply using: kubectl apply -f scanner-bundle.yaml
# 3. Monitor the job: kubectl logs -f job/{config.job_name} -n {config.namespace}
# 4. After completion, retrieve data: orbis scanner retrieve -a {config.namespace}
# 5. Clean up resources: orbis scanner clean -a {config.namespace}
#
# ⚠️  SECURITY NOTE:
# This creates a ServiceAccount with cluster-admin access for diagnostic collection.
# The access is scoped to the scanner job only and should be cleaned up after use.
#
# =============================================================================

{sa_yaml}
---
{job_yaml}

# =============================================================================
# Post-deployment Instructions:
#
# To check job status:
#   kubectl get job {config.job_name} -n {config.namespace}
#   kubectl get pods -l component=scanner -n {config.namespace}
#
# To view logs:
#   kubectl logs -f job/{config.job_name} -n {config.namespace} -c scanner-init
#
# To retrieve data (once job completes):
#   orbis scanner retrieve -a {config.namespace}
#
# To clean up:
#   kubectl delete -f scanner-bundle.yaml
#   or
#   orbis scanner clean -a {config.namespace}
# ============================================================================="""

        return instructions

    def write_to_file(self, content: str, output_file: str) -> bool:
        """Write YAML content to file."""
        try:
            output_path = Path(output_file)
            output_path.write_text(content)
            self.logger.info(f"YAML saved to: {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to write YAML to {output_file}: {e}")
            return False
