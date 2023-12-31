import logging.config
import yaml


# Load YAML configuration from file
with open('logging_config.yaml', 'rt') as f:
    config = yaml.safe_load(f.read())

# Configure logging
logging.config.dictConfig(config)

logger = logging.getLogger(__name__)


def main_test_func():
    logger.debug("debug message")
    logger.info("info message")
    logger.warning("warn message")
    logger.error("error message")
    logger.critical("critical message")
    
    
if __name__ == '__main__':
    main_test_func()
