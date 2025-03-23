import unittest
from unittest.mock import patch
from toy_dns_server.utils.flags import FlagsManager


class TestFlags(unittest.TestCase):

    @patch("sys.argv", ["flags.py"])
    @patch("platform.system", return_value="Linux")
    def test_default_config_path_unix(self, mock_platform):
        manager = FlagsManager()
        flags_config = manager.get_flags_config()
        self.assertEqual(flags_config.default_config_path, "/etc/toy_dns_server/config.yml")
        self.assertEqual(flags_config.user_config_path, "/etc/toy_dns_server/config.yml")

    @patch("sys.argv", ["flags.py"])
    @patch("platform.system", return_value="Windows")
    @patch.dict("os.environ", {"APPDATA": "C:\\Users\\Test\\AppData\\Roaming"})
    def test_default_config_path_windows(self, mock_platform):
        manager = FlagsManager()
        flags_config = manager.get_flags_config()
        expected_path =FlagsManager.DEFAULT_WINDOWS_CONFIG
        self.assertEqual(flags_config.default_config_path, expected_path)
        self.assertEqual(flags_config.user_config_path, expected_path)

    @patch("sys.argv", ["flags.py", "--config", "/tmp/custom.yml"])
    @patch("platform.system", return_value="Linux")
    def test_custom_config_path(self, mock_platform):
        manager = FlagsManager()
        flags_config = manager.get_flags_config()
        self.assertEqual(flags_config.user_config_path, "/tmp/custom.yml")
        self.assertEqual(flags_config.default_config_path, "/etc/toy_dns_server/config.yml")


if __name__ == "__main__":
    unittest.main()
