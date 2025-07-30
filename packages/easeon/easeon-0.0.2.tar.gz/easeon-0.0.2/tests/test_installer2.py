import pytest
from unittest.mock import patch, mock_open, ANY
from easeon.core import PythonLibInstaller
from importlib.metadata import PackageNotFoundError


@pytest.fixture
def installer():
    return PythonLibInstaller()


def test_get_list_from_txt(installer):
    mock_data = "requests==2.26.0\nflask==2.0.2"
    with patch("builtins.open", mock_open(read_data=mock_data)):
        installer.get_list_from_txt("dummy.txt")
        assert installer.package_list == ["requests==2.26.0", "flask==2.0.2"]


def test_get_list_from_csv(installer):
    mock_data = "requests==2.26.0\nflask==2.0.2\n"
    with patch("builtins.open", mock_open(read_data=mock_data)):
        installer.get_list_from_csv("dummy.csv")
        assert installer.package_list == ["requests==2.26.0", "flask==2.0.2"]


@patch("pipmanage.core.version", return_value="1.0.0")
def test_is_package_already_installed_exact_match(mock_version, installer):
    installed, ver = installer._is_package_already_installed("example-package==1.0.0")
    assert installed is True
    assert ver is None


@patch("pipmanage.core.version", return_value="1.2.3")
def test_is_package_installed_but_version_differs(mock_version, installer):
    installed, ver = installer._is_package_already_installed("example-package==1.0.0")
    assert installed is True
    assert ver == "1.2.3"


@patch("pipmanage.core.version", side_effect=PackageNotFoundError("Not installed"))
def test_is_package_not_installed(mock_version, installer):
    installed, ver = installer._is_package_already_installed("nonexistent")
    assert not installed
    assert ver is None


@patch("pipmanage.core.subprocess.run")
def test_install_package_success(mock_run, installer):
    mock_run.return_value.returncode = 0
    installer.get_list(["example-package==1.0.0"])
    installer.install()
    mock_run.assert_called()


@patch("pipmanage.core.subprocess.run")
def test_uninstall_package_success(mock_run, installer):
    mock_run.return_value.returncode = 0
    installer.get_list(["example-package==1.0.0"])
    installer.uninstall()
    mock_run.assert_called()


@patch("pipmanage.core.subprocess.run")
def test_run_pip_command_network_issue(mock_run, installer):
    mock_run.return_value.returncode = 1
    mock_run.return_value.stderr = "Temporary failure in name resolution"
    result = installer._run_pip_command(["install", "example-package"], "example-package")
    assert result is False


@patch("pipmanage.core.subprocess.run")
def test_run_pip_command_no_matching_distribution(mock_run, installer):
    mock_run.return_value.returncode = 1
    mock_run.return_value.stderr = "ERROR: Could not find a version"
    result = installer._run_pip_command(["install", "unknownlib"], "unknownlib")
    assert result is False


@patch("pipmanage.core.subprocess.run")
def test_run_pip_command_version_not_found(mock_run, installer):
    mock_run.return_value.returncode = 1
    mock_run.return_value.stderr = "ERROR: No matching distribution found"
    result = installer._run_pip_command(["install", "badpackage==0.0.0"], "badpackage==0.0.0")
    assert result is False


def test_invalid_package_name(installer):
    installer.get_list(["invalid$$package"])
    installer.install()
    assert "invalid$$package" in installer.package_list


@patch("pipmanage.core.subprocess.run")
@patch("pipmanage.core.version", return_value="1.0.0")
def test_update_package_skipped_if_up_to_date(mock_version, mock_run, installer):
    mock_run.return_value.stdout = "[]"
    mock_run.return_value.returncode = 0
    installer.get_list(["example-package==1.0.0"])
    installer.update()
    mock_run.assert_any_call(
        [ANY, "-m", "pip", "list", "--outdated", "--format=json"],
        capture_output=True, text=True
    )


@patch("sys.argv", new=["script", "--install", "dummy.txt"])
@patch("builtins.open", new_callable=mock_open, read_data="requests\n")
@patch("pipmanage.core.subprocess.run")
def test_run_cli_install_mode(mock_subprocess_run, mock_file_open):
    mock_subprocess_run.return_value.returncode = 0
    PythonLibInstaller.run_cli()
    mock_subprocess_run.assert_called()
