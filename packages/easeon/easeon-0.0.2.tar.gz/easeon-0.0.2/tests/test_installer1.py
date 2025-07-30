import unittest
from unittest.mock import patch, mock_open
from easeon.core import PythonLibInstaller
from importlib.metadata import PackageNotFoundError


class TestPythonLibInstaller(unittest.TestCase):
    def setUp(self):
        self.installer = PythonLibInstaller()

    def test_get_list_from_txt(self):
        """Test loading packages from a .txt file."""
        mock_data = "requests==2.26.0\nflask==2.0.2"
        with patch("builtins.open", mock_open(read_data=mock_data)):
            self.installer.get_list_from_txt("dummy.txt")
        self.assertEqual(self.installer.package_list, ["requests==2.26.0", "flask==2.0.2"])

    def test_get_list_from_csv(self):
        """Test loading packages from a .csv file."""
        mock_data = "requests==2.26.0\nflask==2.0.2\n"
        with patch("builtins.open", mock_open(read_data=mock_data)):
            self.installer.get_list_from_csv("dummy.csv")
        self.assertEqual(self.installer.package_list, ["requests==2.26.0", "flask==2.0.2"])

    @patch("pipmanage.core.version", return_value="1.0.0")
    def test_is_package_already_installed_exact_match(self, mock_version):
        """Test exact version match returns installed=True and ver=None."""
        installed, ver = self.installer._is_package_already_installed("example-package==1.0.0")
        self.assertTrue(installed)
        self.assertIsNone(ver)

    @patch("pipmanage.core.version", return_value="1.2.3")
    def test_is_package_installed_but_version_differs(self, mock_version):
        """Test version mismatch returns current version."""
        installed, ver = self.installer._is_package_already_installed("example-package==1.0.0")
        self.assertTrue(installed)
        self.assertEqual(ver, "1.2.3")

    @patch("pipmanage.core.version", side_effect=PackageNotFoundError("Not installed"))
    def test_is_package_not_installed(self, mock_version):
        """Test when package is not installed at all."""
        installed, ver = self.installer._is_package_already_installed("nonexistent")
        self.assertFalse(installed)
        self.assertIsNone(ver)

    @patch("pipmanage.core.subprocess.run")
    def test_install_package_success(self, mock_run):
        """Test successful package installation."""
        mock_run.return_value.returncode = 0
        self.installer.get_list(["example-package==1.0.0"])
        self.installer.install()
        mock_run.assert_called()

    @patch("pipmanage.core.subprocess.run")
    def test_uninstall_package_success(self, mock_run):
        """Test successful package uninstallation."""
        mock_run.return_value.returncode = 0
        self.installer.get_list(["example-package==1.0.0"])
        self.installer.uninstall()
        mock_run.assert_called()

    @patch("pipmanage.core.subprocess.run")
    def test_run_pip_command_network_issue(self, mock_run):
        """Test pip command fails due to network issue."""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Temporary failure in name resolution"
        self.installer._run_pip_command(["install", "example-package"], "example-package")

    @patch("pipmanage.core.subprocess.run")
    def test_run_pip_command_no_matching_distribution(self, mock_run):
        """Test pip command fails due to invalid version."""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "ERROR: Could not find a version"
        self.installer._run_pip_command(["install", "unknownlib"], "unknownlib")

    @patch("pipmanage.core.subprocess.run")
    def test_run_pip_command_version_not_found(self, mock_run):
        """Test pip command fails due to missing package."""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "ERROR: No matching distribution found"
        self.installer._run_pip_command(["install", "badpackage==0.0.0"], "badpackage==0.0.0")

    def test_invalid_package_name(self):
        """Test invalid package names are skipped."""
        self.installer.get_list(["invalid$$package"])
        self.installer.install()

    @patch("pipmanage.core.subprocess.run")
    @patch("pipmanage.core.version", return_value="1.0.0")
    def test_update_package_skipped_if_up_to_date(self, mock_version, mock_run):
        """Test update is skipped if package is up-to-date."""
        mock_run.return_value.stdout = "[]"
        mock_run.return_value.returncode = 0
        self.installer.get_list(["example-package==1.0.0"])
        self.installer.update()
        mock_run.assert_any_call(
            [unittest.mock.ANY, "-m", "pip", "list", "--outdated", "--format=json"],
            capture_output=True, text=True
        )

    @patch("sys.argv", new=["script", "--install", "dummy.txt"])  # Does NOT pass an argument
    @patch("builtins.open", new_callable=mock_open, read_data="requests\n")
    @patch("pipmanage.core.subprocess.run")
    def test_run_cli_install_mode(self, mock_run, mock_open_file):
        """Test CLI install mode processes input file and installs package."""
        mock_run.return_value.returncode = 0
        PythonLibInstaller.run_cli()
        mock_run.assert_called()


if __name__ == "__main__":
    unittest.main()
