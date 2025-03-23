import unittest
import os
import tempfile
import sys
from io import StringIO
from toy_dns_server.logging.logger import logger, flush_logs, reconfigure_logger
from toy_dns_server.config.schema import LoggingConfig

class TestLogger(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp_log_dir = tempfile.TemporaryDirectory()

        cls.stdout_log = os.path.join(cls.temp_log_dir.name, "stdout_test.log")
        cls.stderr_log = os.path.join(cls.temp_log_dir.name, "stderr_test.log")

        mock_config = LoggingConfig(
            level="info",
            stdout_log_file=cls.stdout_log,
            stderr_log_file=cls.stderr_log
        )
        reconfigure_logger(mock_config)

    @classmethod
    def tearDownClass(cls):
        cls.temp_log_dir.cleanup()

    def test_info_logging(self):
        logger.info("Test INFO message")
        flush_logs(success=True)

        with open(self.stdout_log, "r") as f:
            logs = f.read()

        self.assertIn("Test INFO message", logs)
        self.assertIn("[INFO]", logs)

    def test_warning_logging(self):
        logger.warning("Test WARNING message")
        flush_logs(success=True)

        with open(self.stderr_log, "r") as f:
            logs = f.read()

        self.assertIn("Test WARNING message", logs)
        self.assertIn("[WARNING]", logs)

    def test_error_logging(self):
        logger.error("Test ERROR message")
        flush_logs(success=True)

        with open(self.stderr_log, "r") as f:
            logs = f.read()

        self.assertIn("Test ERROR message", logs)
        self.assertIn("[ERROR]", logs)

    def test_debug_logs_on_failure(self):
        # Temporarily set log level to debug for this test
        mock_config = LoggingConfig(
            level="debug",
            stdout_log_file=self.stdout_log,
            stderr_log_file=self.stderr_log
        )
        reconfigure_logger(mock_config)

        stderr_backup = sys.stderr
        sys.stderr = StringIO()

        logger.debug("Test DEBUG message")
        flush_logs(success=False)

        logs = sys.stderr.getvalue()
        sys.stderr = stderr_backup

        self.assertIn("Test DEBUG message", logs)
        self.assertIn("[DEBUG]", logs)

        # Restore original log level
        mock_config = LoggingConfig(
            level="info",
            stdout_log_file=self.stdout_log,
            stderr_log_file=self.stderr_log
        )
        reconfigure_logger(mock_config)

if __name__ == "__main__":
    unittest.main()
