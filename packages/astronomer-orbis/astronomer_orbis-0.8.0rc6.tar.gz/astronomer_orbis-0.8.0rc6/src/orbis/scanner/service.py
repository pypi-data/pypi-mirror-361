from orbis.scanner.k8s_client import K8sClient
from orbis.scanner.models import JobStatus, ScannerConfig, ScannerResult
from orbis.scanner.yaml_generator import YamlGenerator
from orbis.utils.logger import get_early_logger


class ScannerService:
    """Main service for scanner operations."""

    def __init__(self, config: ScannerConfig):
        self.config = config
        self.logger = get_early_logger()
        self.k8s_client = K8sClient(config.kubeconfig_path)
        self.yaml_generator = YamlGenerator()

    def generate_yaml(self, output_file: str | None = None) -> ScannerResult:
        """Generate YAML bundle for manual application."""
        if not self.config.image:
            return ScannerResult(success=False, error_message="Docker image is required for YAML generation")

        self.logger.info(f"Generating YAML for namespace: {self.config.namespace}")

        try:
            yaml_content = self.yaml_generator.generate_support_bundle(self.config)

            if output_file:
                if self.yaml_generator.write_to_file(yaml_content, output_file):
                    self.logger.info(f"YAML saved to: {output_file}")
                    return ScannerResult(success=True, output_file=output_file)
                else:
                    return ScannerResult(success=False, error_message=f"Failed to write YAML to {output_file}")
            else:
                # Print to console
                print(yaml_content)
                print("\n" + "=" * 80)
                print("NEXT STEPS:")
                print("1. Save the above YAML to a file (e.g., scanner-bundle.yaml)")
                print("2. Share with your infrastructure team")
                print("3. They should apply it: kubectl apply -f scanner-bundle.yaml")
                print(f"4. After completion, retrieve data: orbis scanner retrieve -a {self.config.namespace}")
                return ScannerResult(success=True)

        except Exception as e:
            self.logger.error(f"Failed to generate YAML: {e}")
            return ScannerResult(success=False, error_message=str(e))

    def create_and_execute(self) -> ScannerResult:
        """Execute scanner directly and retrieve results."""
        if not self.config.image:
            return ScannerResult(success=False, error_message="Docker image is required for scanner execution")

        self.logger.info("Starting direct execution mode")

        try:
            # Apply Kubernetes resources
            self.k8s_client.create_service_account(self.config)
            self.k8s_client.create_cluster_role_binding(self.config)
            job_name = self.k8s_client.create_job(self.config)

            # Monitor job progress
            job_completed = self.k8s_client.wait_for_job_completion(job_name, self.config.namespace)

            if not job_completed:
                return ScannerResult(success=False, error_message="Job failed to complete successfully")

            # Retrieve data
            result = self.retrieve_data(self.config.namespace)

            # Cleanup if requested
            if self.config.cleanup:
                self.cleanup_resources(self.config.namespace)

            return result

        except Exception as e:
            self.logger.error(f"Execution failed: {e}")
            return ScannerResult(success=False, error_message=str(e))

    def retrieve_data(self, namespace: str, pod_name: str | None = None) -> ScannerResult:
        """Retrieve data from scanner pod."""
        try:
            if not pod_name:
                pod_name = self.k8s_client.find_scanner_pod(namespace)
                if not pod_name:
                    return ScannerResult(success=False, error_message=f"No scanner pod found in namespace {namespace}")

            self.logger.info(f"Retrieving data from pod: {pod_name}")

            # Copy file from pod
            success = self.k8s_client.copy_file_from_pod(pod_name, namespace, self.config.remote_tar_path, self.config.local_tar_path)

            if not success:
                return ScannerResult(success=False, error_message="Failed to copy support bundle from pod")

            # Verify checksum
            if self.k8s_client.verify_file_checksum(pod_name, namespace, self.config.remote_tar_path, self.config.local_tar_path):
                self.logger.info("Support bundle retrieved and verified successfully")
                return ScannerResult(success=True, output_file=self.config.local_tar_path)
            else:
                return ScannerResult(success=False, error_message="File checksum verification failed")

        except Exception as e:
            self.logger.error(f"Failed to retrieve data: {e}")
            return ScannerResult(success=False, error_message=str(e))

    def check_status(self, namespace: str) -> JobStatus:
        """Check status of scanner job and pod."""
        try:
            # Find job by component label
            jobs = self.k8s_client.batch_v1.list_namespaced_job(namespace=namespace, label_selector="component=scanner")

            if not jobs.items:
                return JobStatus(name="N/A", namespace=namespace, pod_status="No scanner job found")

            job_name = jobs.items[0].metadata.name
            return self.k8s_client.get_job_status(job_name, namespace)

        except Exception as e:
            self.logger.error(f"Failed to check status: {e}")
            return JobStatus(name="N/A", namespace=namespace, pod_status=f"Error: {str(e)}")

    def cleanup_resources(self, namespace: str) -> ScannerResult:
        """Clean up scanner resources."""
        try:
            self.logger.info(f"Cleaning up resources in namespace: {namespace}")
            self.k8s_client.cleanup_scanner_resources(namespace)
            return ScannerResult(success=True)

        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            return ScannerResult(success=False, error_message=str(e))
