"""CSV template management and basic row operations."""

import csv
import logging
import os
from typing import Any

logger = logging.getLogger("root")


def get_csv_template_headers() -> list[str]:
    """Get the headers from the CSV template file."""
    template_path = os.path.join(os.path.dirname(__file__), "..", "..", "config", "csv_template.csv")
    try:
        with open(template_path) as f:
            reader = csv.reader(f)
            return next(reader)  # Get the header row
    except Exception as e:
        logger.error(f"Failed to read CSV template: {e}")
        raise


def get_empty_row() -> dict[str, Any]:
    """Get an empty row with just the headers."""
    return dict.fromkeys(get_csv_template_headers(), "")
