import os
import yaml
from pydantic import ValidationError
from toy_dns_server.config.schema import ConfigSchema
from toy_dns_server.utils.flags import FlagsManager

from toy_dns_server.log.logger import Logger

from toy_dns_server.utils.deep_merge import deep_merge

class ConfigLoader:
    CONFIG_DIR = "config"
    DEFAULT_CONFIG_FILE = os.path.join(CONFIG_DIR, "config.default.yml")
    _logger: Logger
    __flags_manager = FlagsManager()

    def __init__(self):
        self._logger = Logger(self)

    def load_config(self):
        self._logger.debug("Getting flags config...")
        flags_config = self.__flags_manager.get_flags_config()
        user_config_file = flags_config.user_config_path

        self._logger.debug("Loading default configuration...")

        default_config = self._read_default_config()
        user_config = self._read_user_config(user_config_file)
        merged_config = deep_merge(default_config, user_config)
        parsed_config = self._parse_config(merged_config)

        return parsed_config

    def _read_user_config(self, user_config_path):
        user_config = {}
        if (user_config_path is None) or (user_config_path == ""):
            self._logger.warn("No user configuration file provided. Using default configuration.")
        elif not os.path.exists(user_config_path):
            self._logger.fatal(f"User configuration file `{user_config_path}` is missing.")
        else:
            self._logger.debug(f"User configuration file found at `{user_config_path}`.")
            with open(user_config_path, "r") as f:
                user_config = yaml.safe_load(f) or {}

        return user_config

    def _read_default_config(self):
        default_config = {}
        try:
            with open(self.DEFAULT_CONFIG_FILE, "r") as f:
                default_config = yaml.safe_load(f) or {}
        except FileNotFoundError:
            self._logger.fatal(f"Default configuration file `{self.DEFAULT_CONFIG_FILE}` is missing.")

        return default_config

    def _parse_config(self, merged_config: dict):
        config: ConfigSchema

        try:
            self._logger.debug("Validating configuration...")
            config = ConfigSchema(**merged_config)
            self._logger.info("Configuration validated successfully.")
        except ValidationError as e:
            self._logger.fatal(f"Configuration validation failed:\n{e}")

        return config
