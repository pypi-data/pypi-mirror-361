import unittest
from unittest.mock import patch
from easeon.core import PythonLibInstaller  # ✅ Adjusted import


class TestPythonLibInstaller(unittest.TestCase):

    def setUp(self):
        self.installer = PythonLibInstaller(verbose=False)
        self.test_package = "example-package==1.0.0"
        self.installer.package_list = [self.test_package]

    @patch("pipmanage.core.subprocess.run")  # ✅ Corrected patch path
    def test_install_package_success(self, mock_run):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Successfully installed example-package"
        with self.assertLogs(level='INFO') as log:
            self.installer.install()
        self.assertTrue(any("installing" in msg.lower() for msg in log.output))
        self.assertTrue(any("installed" in msg.lower() for msg in log.output))

    @patch("pipmanage.core.subprocess.run")
    def test_uninstall_package_success(self, mock_run):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Successfully uninstalled example-package"
        with self.assertLogs(level='INFO') as log:
            self.installer.uninstall()
        self.assertTrue(any("uninstalling" in msg.lower() for msg in log.output))
        self.assertTrue(any("uninstalled" in msg.lower() for msg in log.output))

    @patch("pipmanage.core.subprocess.run")
    def test_update_package_skipped_if_up_to_date(self, mock_run):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "[]"
        with self.assertLogs(level='INFO') as log:
            self.installer.update()
        self.assertTrue(any("already up to date" in msg.lower() for msg in log.output))

    def test_invalid_package_name(self):
        self.installer.package_list = ["invalid$$package"]
        with self.assertLogs(level='WARNING') as log:
            self.installer.install()
        self.assertTrue(any("invalid package name" in msg.lower() for msg in log.output))

    def test_empty_package_list_warning(self):
        self.installer.package_list = []
        with self.assertLogs(level='WARNING') as log:
            self.installer.install()
        self.assertTrue(any("empty package list" in msg.lower() for msg in log.output))


if __name__ == "__main__":
    unittest.main()
