import os
import yaml
from pydantic import ValidationError
from toy_dns_server.config.schema import ConfigSchema
from toy_dns_server.utils.flags import parse_flags
from toy_dns_server.logging.logger import logger, reconfigure_logger, flush_logs, catch_exceptions

CONFIG_DIR = "config"
DEFAULT_CONFIG_FILE = os.path.join(CONFIG_DIR, "config.default.yml")

@catch_exceptions
def load_config():
    """Loads and validates the configuration from YAML files."""
    flags = parse_flags()
    user_config_file = flags["config"]

    logger.info("Loading default configuration...")

    try:
        with open(DEFAULT_CONFIG_FILE, "r") as f:
            default_config = yaml.safe_load(f) or {}
    except FileNotFoundError:
        logger.error(f"Default configuration file `{DEFAULT_CONFIG_FILE}` is missing.")
        raise

    logger.info("Default configuration loaded successfully.")

    user_config = {}
    if os.path.exists(user_config_file):
        logger.info(f"Loading user configuration from `{user_config_file}`...")
        with open(user_config_file, "r") as f:
            user_config = yaml.safe_load(f) or {}

    merged_config = {**default_config, **user_config}

    try:
        config = ConfigSchema(**merged_config)
        logger.info("Configuration validated successfully.")
    except ValidationError as e:
        logger.error(f"Configuration validation failed:\n{e}")
        raise

    reconfigure_logger(config)
    logger.info("Logger reconfigured with user settings.")

    flush_logs(success=True)
    return config

CONFIG = load_config()
