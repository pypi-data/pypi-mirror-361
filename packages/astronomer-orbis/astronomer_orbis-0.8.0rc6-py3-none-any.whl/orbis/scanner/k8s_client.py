import hashlib
import os
import time
from pathlib import Path
from typing import cast

from kubernetes import client, config
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream

from orbis.scanner.models import JobStatus, ScannerConfig
from orbis.utils.logger import get_early_logger


class K8sClient:
    """Kubernetes operations for scanner using Python client."""

    def __init__(self, kubeconfig_path: str | None = None):
        self.logger = get_early_logger()
        self._load_config(kubeconfig_path)

        # Initialize API clients
        self.core_v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.batch_v1 = client.BatchV1Api()
        self.rbac_v1 = client.RbacAuthorizationV1Api()

    def _load_config(self, kubeconfig_path: str | None = None):
        """Load Kubernetes configuration with priority order."""
        try:
            if kubeconfig_path:
                # 1. Explicit path provided
                config.load_kube_config(config_file=kubeconfig_path)
                self.logger.info(f"Loaded config from: {kubeconfig_path}")
            elif os.getenv("KUBECONFIG"):
                # 2. KUBECONFIG environment variable
                config.load_kube_config(config_file=os.getenv("KUBECONFIG"))
                self.logger.info(f"Loaded config from KUBECONFIG: {os.getenv('KUBECONFIG')}")
            elif Path.home().joinpath(".kube/config").exists():
                # 3. Default location
                config.load_kube_config()
                self.logger.info("Loaded config from ~/.kube/config")
            else:
                # 4. In-cluster config (for pods)
                config.load_incluster_config()
                self.logger.info("Loaded in-cluster config")
        except Exception as e:
            raise RuntimeError(f"Failed to load Kubernetes config: {e}")

    def create_service_account(self, config: ScannerConfig) -> bool:
        """Create service account using Python client."""
        try:
            sa_body = client.V1ServiceAccount(metadata=client.V1ObjectMeta(name=config.service_account_name, namespace=config.namespace, labels={"app": "support-bundle", "component": "scanner"}))

            self.core_v1.create_namespaced_service_account(namespace=config.namespace, body=sa_body)
            self.logger.info(f"Created ServiceAccount: {config.service_account_name}")
            return True

        except ApiException as e:
            if e.status == 409:  # Already exists
                self.logger.info(f"ServiceAccount {config.service_account_name} already exists")
                return True
            else:
                self.logger.error(f"Failed to create ServiceAccount: {e}")
                raise

    def create_cluster_role_binding(self, config: ScannerConfig) -> bool:
        """Create cluster role binding."""
        try:
            crb_body = client.V1ClusterRoleBinding(
                metadata=client.V1ObjectMeta(name=config.role_binding_name, labels={"app": "support-bundle", "component": "scanner"}),
                role_ref=client.V1RoleRef(
                    api_group="rbac.authorization.k8s.io",
                    kind="ClusterRole",
                    name="cluster-admin",  # Note: Should be restricted in production
                ),
                subjects=[client.RbacV1Subject(kind="ServiceAccount", name=config.service_account_name, namespace=config.namespace)],
            )

            self.rbac_v1.create_cluster_role_binding(body=crb_body)
            self.logger.info(f"Created ClusterRoleBinding: {config.role_binding_name}")
            return True

        except ApiException as e:
            if e.status == 409:
                self.logger.info(f"ClusterRoleBinding {config.role_binding_name} already exists")
                return True
            else:
                self.logger.error(f"Failed to create ClusterRoleBinding: {e}")
                raise

    def create_job(self, config: ScannerConfig) -> str:
        """Create scanner job with proper resource definitions."""
        scanner_args = config.build_scanner_command_args()
        scanner_command = f"scanner.py {' '.join(scanner_args)} && cp /data/*.tar.gz /results/"

        job_body = client.V1Job(
            metadata=client.V1ObjectMeta(name=config.job_name, namespace=config.namespace, labels={"app": "support-bundle", "component": "scanner"}),
            spec=client.V1JobSpec(
                backoff_limit=0,
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(labels={"app": "support-bundle", "component": "scanner"}),
                    spec=client.V1PodSpec(
                        service_account_name=config.service_account_name,
                        restart_policy="Never",
                        init_containers=[
                            client.V1Container(
                                name="scanner-init",
                                image=config.image,
                                command=["/bin/bash", "-c"],
                                args=[scanner_command],
                                volume_mounts=[client.V1VolumeMount(name="results-file", mount_path="/results")],
                                resources=client.V1ResourceRequirements(limits={"memory": config.memory, "cpu": config.cpu}, requests={"memory": "200Mi", "cpu": "200m"}),
                            )
                        ],
                        containers=[
                            client.V1Container(
                                name="main",
                                image=config.image,
                                command=["/bin/bash", "-c"],
                                args=[f"echo 'Data collection complete. Sleeping for {config.sleep_duration}' && sleep {config.sleep_duration}"],
                                volume_mounts=[client.V1VolumeMount(name="results-file", mount_path="/results")],
                                resources=client.V1ResourceRequirements(limits={"memory": "200Mi", "cpu": "200m"}, requests={"memory": "100Mi", "cpu": "100m"}),
                            )
                        ],
                        volumes=[client.V1Volume(name="results-file", empty_dir=client.V1EmptyDirVolumeSource())],
                    ),
                ),
            ),
        )

        try:
            job = cast(client.V1Job, self.batch_v1.create_namespaced_job(namespace=config.namespace, body=job_body))
            if job.metadata and job.metadata.name:
                self.logger.info(f"Created job: {job.metadata.name}")
                return job.metadata.name
            else:
                raise RuntimeError("Job created but metadata is missing")

        except ApiException as e:
            self.logger.error(f"Failed to create job: {e}")
            raise

    def get_job_status(self, job_name: str, namespace: str) -> JobStatus:
        """Get comprehensive job status with rich information."""
        try:
            job = cast(client.V1Job, self.batch_v1.read_namespaced_job_status(name=job_name, namespace=namespace))

            if not job.metadata or not job.status:
                raise RuntimeError("Job metadata or status is missing")

            status = JobStatus(
                name=job.metadata.name or "",
                namespace=job.metadata.namespace or "",
                creation_time=job.metadata.creation_timestamp,
                start_time=job.status.start_time,
                completion_time=job.status.completion_time,
                active=job.status.active or 0,
                succeeded=job.status.succeeded or 0,
                failed=job.status.failed or 0,
            )

            if job.status.conditions:
                for condition in job.status.conditions:
                    status.conditions.append({
                        "type": condition.type,
                        "status": condition.status,
                        "reason": condition.reason,
                        "message": condition.message,
                        "last_transition_time": condition.last_transition_time,
                    })

                    if condition.type == "Complete" and condition.status == "True":
                        status.ready = True

            # Get pod information
            pod_name = self.find_scanner_pod(namespace)
            if pod_name:
                status.pod_name = pod_name
                pod = cast(client.V1Pod, self.core_v1.read_namespaced_pod(name=pod_name, namespace=namespace))
                if pod.status:
                    status.pod_status = pod.status.phase

            return status

        except ApiException as e:
            self.logger.error(f"Failed to get job status: {e}")
            raise

    def find_scanner_pod(self, namespace: str) -> str | None:
        """Find scanner pod by label selector."""
        try:
            pods = cast(client.V1PodList, self.core_v1.list_namespaced_pod(namespace=namespace, label_selector="component=scanner"))
            if pods.items:
                return pods.items[0].metadata.name
            return None
        except ApiException as e:
            self.logger.error(f"Failed to find scanner pod: {e}")
            return None

    def wait_for_job_completion(self, job_name: str, namespace: str, timeout: int = 3600) -> bool:
        """Wait for job completion with progress monitoring."""
        start_time = time.time()
        last_status = None

        while time.time() - start_time < timeout:
            try:
                status = self.get_job_status(job_name, namespace)

                # Log status changes
                current_status_str = f"Active={status.active}, Succeeded={status.succeeded}, Failed={status.failed}"
                if current_status_str != last_status:
                    self.logger.info(f"Job {job_name}: {current_status_str}")
                    last_status = current_status_str

                if status.succeeded and status.succeeded > 0:
                    self.logger.info("Job completed successfully")
                    return True
                elif status.failed and status.failed > 0:
                    self.logger.error("Job failed")
                    self._log_failed_job_details(job_name, namespace)
                    return False

                time.sleep(10)

            except ApiException as e:
                self.logger.warning(f"Error checking job status: {e}")
                time.sleep(5)

        raise TimeoutError(f"Job {job_name} did not complete within {timeout} seconds")

    def _log_failed_job_details(self, job_name: str, namespace: str):
        """Log details about failed job for debugging."""
        try:
            pod_name = self.find_scanner_pod(namespace)
            if pod_name:
                self.logger.error(f"Job '{job_name}' failed. Check pod logs: kubectl logs {pod_name} -n {namespace} -c scanner-init")
            else:
                self.logger.error(f"Job '{job_name}' failed but could not find associated pod")
        except Exception as e:
            self.logger.error(f"Could not get failed job details for '{job_name}': {e}")

    def copy_file_from_pod(self, pod_name: str, namespace: str, remote_path: str, local_path: str) -> bool:
        """Copy file from pod using Kubernetes exec API."""
        try:
            # Create tar command to stream file
            exec_command = ["tar", "cf", "-", "-C", os.path.dirname(remote_path), os.path.basename(remote_path)]

            # Execute command and get tar stream
            resp = stream(self.core_v1.connect_get_namespaced_pod_exec, pod_name, namespace, command=exec_command, stderr=True, stdin=False, stdout=True, tty=False, _preload_content=False)

            # Extract tar stream to local file
            with open(local_path, "wb") as local_file:
                while resp.is_open():
                    resp.update(timeout=1)
                    if resp.peek_stdout():
                        local_file.write(resp.read_stdout())
                    if resp.peek_stderr():
                        self.logger.warning(f"stderr: {resp.read_stderr()}")

            resp.close()

            # Verify file was copied
            if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
                self.logger.info(f"File copied successfully: {local_path}")
                return True
            else:
                self.logger.error("File copy verification failed")
                return False

        except Exception as e:
            self.logger.error(f"Failed to copy file: {e}")
            return False

    def verify_file_checksum(self, pod_name: str, namespace: str, remote_path: str, local_path: str) -> bool:
        """Verify file integrity using checksums."""
        try:
            # Get remote checksum
            exec_command = ["sha256sum", remote_path]
            resp = stream(self.core_v1.connect_get_namespaced_pod_exec, pod_name, namespace, command=exec_command, stderr=True, stdin=False, stdout=True, tty=False)
            remote_checksum = resp.split()[0]

            # Calculate local checksum
            with open(local_path, "rb") as f:
                local_checksum = hashlib.sha256(f.read()).hexdigest()

            if remote_checksum == local_checksum:
                self.logger.info("File checksum verification passed")
                return True
            else:
                self.logger.error("File checksum verification failed")
                return False

        except Exception as e:
            self.logger.error(f"Checksum verification failed: {e}")
            return False

    def cleanup_scanner_resources(self, namespace: str) -> None:
        """Clean up scanner resources."""
        self.logger.info(f"Cleaning up scanner resources in namespace: {namespace}")

        try:
            # Delete jobs
            jobs = self.batch_v1.list_namespaced_job(namespace=namespace, label_selector="component=scanner")
            for job in jobs.items:
                self.batch_v1.delete_namespaced_job(name=job.metadata.name, namespace=namespace)
                self.logger.info(f"Deleted job: {job.metadata.name}")

            # Delete pods
            pods = self.core_v1.list_namespaced_pod(namespace=namespace, label_selector="component=scanner")
            for pod in pods.items:
                self.core_v1.delete_namespaced_pod(name=pod.metadata.name, namespace=namespace)
                self.logger.info(f"Deleted pod: {pod.metadata.name}")

            # Delete service account
            config = ScannerConfig(namespace=namespace)
            try:
                self.core_v1.delete_namespaced_service_account(name=config.service_account_name, namespace=namespace)
                self.logger.info("Deleted service account")
            except ApiException as e:
                if e.status != 404:
                    self.logger.warning(f"Failed to delete service account: {e}")

            # Delete cluster role binding
            try:
                self.rbac_v1.delete_cluster_role_binding(name=config.role_binding_name)
                self.logger.info("Deleted cluster role binding")
            except ApiException as e:
                if e.status != 404:
                    self.logger.warning(f"Failed to delete cluster role binding: {e}")

        except ApiException as e:
            self.logger.error(f"Error during cleanup: {e}")
            raise
