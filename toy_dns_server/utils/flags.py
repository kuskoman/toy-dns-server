import argparse
import os

class FlagsConfig:
    default_config_path = None
    user_config_path = None

    def __init__(self, default_config_path, user_config_path):
        self.default_config_path = default_config_path
        self.user_config_path = user_config_path


class FlagsManager:
    DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "config.default.yml")

    def get_flags_config(self):
        flags_dict = self._parse_flags()

        flagsConfig = FlagsConfig(
            default_config_path=self.DEFAULT_CONFIG_PATH,
            user_config_path=flags_dict["config"]
        )
        return flagsConfig

    def _parse_flags(self):
        parser = argparse.ArgumentParser(description="Toy DNS Server")

        parser.add_argument(
            "--config",
            type=str,
            help="Path to the user configuration file (default: platform-specific)"
        )

        flags_dict = vars(parser.parse_args())
        return flags_dict
