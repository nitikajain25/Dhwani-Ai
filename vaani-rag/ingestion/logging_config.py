import logging
import sys
from ingestion.config import LOGS_DIR

def setup_logging():
    # Define standard format
    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(log_format, date_format)

    # Console Handler (output to stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # File Handler (output to disk for debugging/tracing)
    file_path = LOGS_DIR / "pipeline.log"
    file_handler = logging.FileHandler(file_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    # Root Logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Ensure handlers are not added multiple times in environments like Jupyter
    if not root_logger.handlers:
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)

    # Create and return pipeline specific logger
    return logging.getLogger("pipeline")

# Initialize and export default logger
logger = setup_logging()
