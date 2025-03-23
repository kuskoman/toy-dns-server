import os
import yaml
from pydantic import ValidationError
from toy_dns_server.config.schema import ConfigSchema
from toy_dns_server.log.logger import Logger
from toy_dns_server.utils.flags import FlagsManager



class ConfigLoader:
    CONFIG_DIR = "config"
    DEFAULT_CONFIG_FILE = os.path.join(CONFIG_DIR, "config.default.yml")
    __logger: Logger
    __flags_manager = FlagsManager()

    def __init__(self):
        self.__logger = Logger(self)

    def load_config(self):
        self.__logger.debug("Getting flags config...")
        flags_config = self.__flags_manager.get_flags_config()
        user_config_file = flags_config.user_config_path

        self.__logger.debug("Loading default configuration...")

        default_config, user_config = self.__read_configs(user_config_file)
        merged_config = {**default_config, **user_config}
        parsed_config = self.__parse_config(merged_config)

        return parsed_config

    def __read_configs(self, user_config_path):
        default_config = None
        try:
            with open(self.DEFAULT_CONFIG_FILE, "r") as f:
                default_config = yaml.safe_load(f) or {}
        except FileNotFoundError:
            self.__logger.error(f"Default configuration file `{self.DEFAULT_CONFIG_FILE}` is missing.")
            raise RuntimeError("Default configuration file is missing.")

        user_config = {}
        if (user_config_path is None) or (user_config_path == ""):
            self.__logger.warn("No user configuration file provided. Using default configuration.")
        elif not os.path.exists(user_config_path):
            self.__logger.error(f"User configuration file `{user_config_path}` is missing.")
            raise RuntimeError("User configuration file is missing.")
        else:
            self.__logger.debug(f"User configuration file found at `{user_config_path}`.")
            with open(user_config_path, "r") as f:
                user_config = yaml.safe_load(f) or {}

        return default_config, user_config

    def __parse_config(self, merged_config: dict):
        config: ConfigSchema

        try:
            self.__logger.debug("Validating configuration...")
            config = ConfigSchema(**merged_config)
            self.__logger.info("Configuration validated successfully.")
        except ValidationError as e:
            self.__logger.error(f"Configuration validation failed:\n{e}")
            raise

        return config
