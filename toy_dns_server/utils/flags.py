import argparse
import os
import platform

class FlagsConfig:
    default_config_path = None
    user_config_path = None

    def __init__(self, default_config_path, user_config_path):
        self.default_config_path = default_config_path
        self.user_config_path = user_config_path


class FlagsManager:
    DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "config.default.yml")
    DEFAULT_UNIX_CONFIG = "/etc/toy_dns_server/config.yml"
    DEFAULT_WINDOWS_CONFIG = os.path.join(os.environ.get("APPDATA", "C:\\ProgramData"), "toy_dns_server", "config.yml")

    def get_flags_config(self):
        flags_dict = self.__parse_flags()
        default_config_path = self.__get_default_user_config_path()

        flagsConfig = FlagsConfig(
            default_config_path=default_config_path,
            user_config_path=flags_dict["config"]
        )
        return flagsConfig

    def __parse_flags(self):
        parser = argparse.ArgumentParser(description="Toy DNS Server")

        parser.add_argument(
            "--config",
            type=str,
            default=self.__get_default_user_config_path(),
            help="Path to the user configuration file (default: platform-specific)"
        )

        flags_dict = vars(parser.parse_args())
        return flags_dict

    def __get_default_user_config_path(self):
        if platform.system() == "Windows":
            return self.DEFAULT_WINDOWS_CONFIG
        return self.DEFAULT_UNIX_CONFIG
