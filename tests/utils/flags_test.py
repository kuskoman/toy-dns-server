import unittest
from unittest.mock import patch
from toy_dns_server.utils.flags import parse_flags, get_default_config_path

class TestFlags(unittest.TestCase):

    @patch("sys.argv", ["flags.py"])
    def test_default_config_path(self):
        """Test default config path based on OS"""
        expected_path = get_default_config_path()
        self.assertEqual(parse_flags()["config"], expected_path)

    @patch("sys.argv", ["flags.py", "--config", "/tmp/test.yml"])
    def test_custom_config(self):
        """Test custom config file flag"""
        self.assertEqual(parse_flags()["config"], "/tmp/test.yml")

if __name__ == "__main__":
    unittest.main()
