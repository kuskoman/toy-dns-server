from toy_dns_server.config.loader import ConfigLoader
from toy_dns_server.log.logger import Logger
from toy_dns_server.log.base_logger import base_logger

logger = Logger("main")
logger.info("Loading configuration...")
config_loader = ConfigLoader()
config = config_loader.load_config()
base_logger.reconfigure_logger(config.logging)
logger.info("Configuration loaded successfully.")
