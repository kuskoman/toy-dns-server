import os
from posixpath import abspath
import yaml
from pydantic import ValidationError
from toy_dns_server.config.schema import ConfigSchema
from toy_dns_server.utils.flags import FlagsManager

from toy_dns_server.log.logger import Logger

from toy_dns_server.utils.deep_merge import deep_merge

class ConfigLoader:
    _logger: Logger
    _flags_manager = FlagsManager()
    _default_config_file: str

    def __init__(self, root_location: str):
        self._logger = Logger(self)
        default_config_file = os.path.join(root_location, "..", "config", "config.default.yml")
        self._default_config_file = abspath(default_config_file)


    def load_config(self):
        self._logger.debug("Getting flags config...")
        flags_config = self._flags_manager.get_flags_config()
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
            user_config = self._read_yaml(user_config_path)

        return user_config

    def _read_default_config(self):
        default_config = {}
        file_path = self._default_config_file
        self._logger.debug(f"Reading default configuration file at `{file_path}`...")
        try:
            self._read_yaml(file_path)
        except FileNotFoundError:
            self._logger.fatal(f"Default configuration file `{file_path}` is missing.")

        if len(default_config.keys()) == 0:
            self._logger.error("Default configuration file is empty. Using an empty configuration instead.")

        return default_config

    def _read_yaml(self, file_path):
        with open(file_path, "r") as f:
            return yaml.safe_load(f) or {}

    def _parse_config(self, merged_config: dict):
        config: ConfigSchema

        try:
            self._logger.debug("Validating configuration...")
            config = ConfigSchema(**merged_config)
            self._logger.info("Configuration validated successfully.")
        except ValidationError as e:
            self._logger.fatal(f"Configuration validation failed:\n{e}")

        return config
