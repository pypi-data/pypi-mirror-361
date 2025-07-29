import os
import sys
from datetime import datetime
from importlib import resources
from typing import Any

import yaml
from dotenv import find_dotenv, load_dotenv
from pendulum.datetime import DateTime

from orbis.utils.logger import get_early_logger

load_dotenv(find_dotenv(), override=True)

SOFTWARE_QUERIES_FILE_PATH = str(resources.files("orbis.config").joinpath("prometheus_queries.yaml"))
HOUSTON_QUERIES_FILE_PATH = str(resources.files("orbis.config").joinpath("houston_queries.yaml"))
CSV_TEMPLATE_PATH = str(resources.files("orbis.config").joinpath("csv_template.csv"))
ASTRO_SOFTWARE_API_TOKEN = os.environ.get("ASTRO_SOFTWARE_API_TOKEN")
KE_QUERIES = "ke"
CELERY_QUERIES = "celery"
SCHEDULER_QUERIES = "scheduler"
COLORS = ["lightgreen", "yellow", "red", "blue", "orange", "purple", "pink", "brown", "cyan", "magenta"]
DECIMAL_PRECISION = 2

COMPRESSED_FILE_PREFIX = "gather-info"
COMPRESSED_FILE = f"{COMPRESSED_FILE_PREFIX}-{datetime.now().strftime('%d-%m-%y')}.tar.gz"
LOCAL_TAR_PATH = f"./{COMPRESSED_FILE}"
REMOTE_TAR_PATH = f"/results/{COMPRESSED_FILE}"
CPU = "1"
MEMORY = "1Gi"
SLEEP_DURATION = "1d"
IMAGE = "docker.io/sudarshanuc/astronomer-gather-info:v1.2"
SA_NAME = "temp-gather-info-support-bundle"
ROLE_BINDING_NAME = "gather-info-admin-access-binding"
CLEANUP = True
MAX_RETRIES = 3
RETRY_DELAY = 5
SA_AND_ROLE_BINDING_YAML_PATH = str(resources.files("orbis.config").joinpath("sa_and_role_binding.yaml"))
SCANNER_JOB_YAML_PATH = str(resources.files("orbis.config").joinpath("gather_info_job.yaml"))

logger = get_early_logger()


def validate_input_args(base_domain: str, start_date: DateTime, end_date: DateTime) -> None:
    """Validate input arguments."""
    if not base_domain:
        logger.error("Base Domain/Organization ID is required")
        sys.exit(2)
    if start_date > end_date:
        logger.error("Start Date cannot be greater than End Date")
        sys.exit(2)


def parse_yaml(file_name: str) -> Any:
    """Parse YAML file."""
    with open(file_name, encoding="utf-8") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.error("Error while parsing YAML file: %s", exc)
            sys.exit(2)
