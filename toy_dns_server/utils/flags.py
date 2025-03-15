import argparse
import os
import platform

DEFAULT_UNIX_CONFIG = "/etc/toy_dns_server/config.yml"
DEFAULT_WINDOWS_CONFIG = os.path.join(os.environ.get("APPDATA", "C:\\ProgramData"), "toy_dns_server", "config.yml")

def get_default_config_path():
    """Returns the default configuration path based on OS."""
    if platform.system() == "Windows":
        return DEFAULT_WINDOWS_CONFIG
    return DEFAULT_UNIX_CONFIG

def parse_flags():
    """Parses command-line flags and returns them as a dictionary."""
    parser = argparse.ArgumentParser(description="Toy DNS Server")

    parser.add_argument(
        "--config",
        type=str,
        default=get_default_config_path(),
        help="Path to the user configuration file (default: platform-specific)"
    )

    flags_dict = vars(parser.parse_args())
    return flags_dict
