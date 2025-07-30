"""
pipmanage - Python Package Management Utility

This module provides the PythonLibInstaller class to install, uninstall,
and update pip packages programmatically. It supports packages from .txt,
.csv, or Python lists, and ensures UTF-8 support and virtualenv handling.

Author: Kiran Soorya R.S
License: MIT
"""

import os
import sys
import platform
import subprocess
import csv
import json
import re
import venv
import tempfile
import logging
from typing import List, Optional, Tuple
from importlib.metadata import version, PackageNotFoundError  # ✅ Updated

# Configure logging globally
logging.basicConfig(
    filename='pipmanage.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)


def set_utf8_terminal_encoding() -> None:
    system = platform.system()
    if system == "Windows":
        subprocess.run("chcp 65001", shell=True)
    elif system in ["Linux", "Darwin"]:
        os.environ["LC_ALL"] = "en_US.UTF-8"
        os.environ["LANG"] = "en_US.UTF-8"
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")


class PythonLibInstaller:
    def __init__(self, auto_create_venv: bool = False, verbose: bool = False) -> None:
        set_utf8_terminal_encoding()
        self.package_list: List[str] = []
        self.os_name: str = os.name
        self.platform_name: str = platform.system()
        self.verbose = verbose
        self._check_virtualenv(auto_create_venv)

    def _check_virtualenv(self, auto_create: bool = False) -> None:
        if sys.prefix == sys.base_prefix:
            print("⚠️ Not using a virtual environment.")
            logger.warning("Not using a virtual environment.")
            if auto_create:
                print("🛠 Creating `.venv`...")
                logger.info("Creating virtual environment `.venv`")
                venv.create(".venv", with_pip=True)
                print("✅ Virtual environment created. Activate it before proceeding.")
                logger.info("Virtual environment `.venv` created.")
            else:
                print("💡 Tip: Run with `--venv` to auto-create one.")

    def _is_valid_package_name(self, name: str) -> bool:
        return re.match(r'^[a-zA-Z0-9\-_]+(==\d+(\.\d+){0,2})?$', name) is not None

    def get_list_from_txt(self, path: str) -> None:
        try:
            with open(path, 'r', encoding="utf-8") as f:
                self.package_list = [
                    line.strip() for line in f.readlines()
                    if line.strip() and not line.strip().startswith('#')
                ]
            logger.info(f"Loaded packages from text file: {path}")
        except FileNotFoundError:
            print("❌ File not found:", path)
            logger.error(f"Text file not found: {path}")

    def get_list_from_csv(self, path: str) -> None:
        try:
            with open(path, 'r', encoding="utf-8") as f:
                reader = csv.reader(f)
                self.package_list = [
                    row[0].strip() for row in reader
                    if row and not row[0].strip().startswith('#')
                ]
            logger.info(f"Loaded packages from CSV file: {path}")
        except FileNotFoundError:
            print("❌ File not found:", path)
            logger.error(f"CSV file not found: {path}")

    def get_list(self, packages: List[str]) -> None:
        if not packages:
            print("⚠️ Package list is empty.")
            logger.warning("Provided package list is empty.")
        else:
            self.package_list.extend(packages)
            logger.info(f"Added packages: {packages}")

    def _is_package_already_installed(self, pkg_str: str) -> Tuple[bool, Optional[str]]:
        if '==' in pkg_str:
            name, required_ver = pkg_str.split('==')
        else:
            name, required_ver = pkg_str, None
        try:
            current_ver = version(name)
            if required_ver and current_ver != required_ver:
                return True, current_ver
            return True, None
        except (PackageNotFoundError, ModuleNotFoundError):  # ✅ Combined handling
            return False, None

    def _run_pip_command(self, args: List[str], pkg: str, uninstall=False) -> bool:
        result = subprocess.run([sys.executable, "-m", "pip"] + args, capture_output=True, text=True)
        if result.returncode != 0:
            stderr = result.stderr.lower()
            logger.error(f"pip error with {pkg}: {stderr}")
            if "could not find a version" in stderr:
                print(f"❌ Version not found ➤ {pkg}")
            elif "no matching distribution" in stderr:
                print(f"❌ No match ➤ {pkg}")
            elif "temporary failure" in stderr or "connectionerror" in stderr:
                print("🌐 Network issue. Check your internet.")
            elif "permission denied" in stderr:
                print("🔐 Permission denied. Try as admin.")
            elif uninstall and "not installed" in stderr:
                print(f"⚠️ Not installed ➤ {pkg}")
            else:
                print(f"⚠️ pip error with {pkg}:\n{result.stderr}")
            return False
        if self.verbose:
            print(result.stdout.strip())
        print(f"✅ {'Uninstalled' if uninstall else 'Installed'}: {pkg}")
        logger.info(f"{'Uninstalled' if uninstall else 'Installed'}: {pkg}")
        return True

    def _write_temp_package_list(self) -> str:
        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix=".txt", encoding="utf-8") as f:
            f.write("\n".join(self.package_list))
            return f.name

    def install(self) -> None:
        self._real_install()

    def uninstall(self) -> None:
        self._real_uninstall()

    def update(self) -> None:
        self._real_update()

    @staticmethod
    def run_cli() -> None:
        import argparse

        parser = argparse.ArgumentParser(description="📦 pipmanage - Python package manager utility")
        parser.add_argument("--install", metavar="FILE", help="Install from .txt or .csv file")
        parser.add_argument("--uninstall", metavar="FILE", help="Uninstall from .txt or .csv file")
        parser.add_argument("--update", metavar="FILE", help="Update packages listed in file")
        parser.add_argument("--venv", action="store_true", help="Create virtualenv if not active")
        parser.add_argument("--verbose", action="store_true", help="Show pip output details")
        args = parser.parse_args()

        logger.info("Running in CLI mode with arguments: %s", sys.argv[1:])

        manager = PythonLibInstaller(auto_create_venv=args.venv, verbose=args.verbose)

        def load_file(file: str) -> bool:
            if file.endswith(".txt"):
                manager.get_list_from_txt(file)
            elif file.endswith(".csv"):
                manager.get_list_from_csv(file)
            else:
                print(f"❌ Unsupported file: {file}")
                logger.error(f"Unsupported file type: {file}")
                return False
            return True

        if args.install and load_file(args.install):
            manager.install()
        if args.uninstall and load_file(args.uninstall):
            manager.uninstall()
        if args.update and load_file(args.update):
            manager.update()

    def _real_install(self) -> None:
        if not self.package_list:
            print("❗ No packages to install.")
            logger.warning("Install called with empty package list.")
            return
        for pkg in self.package_list:
            print(f"\n📦 Installing: {pkg}")
            logger.info(f"Installing: {pkg}")
            if not self._is_valid_package_name(pkg):
                print(f"❌ Invalid name: {pkg}")
                logger.warning(f"Invalid package name: {pkg}")
                continue
            installed, ver = self._is_package_already_installed(pkg)
            if installed and not ver:
                print(f"✅ Already installed: {pkg}")
                logger.info(f"Already installed: {pkg}")
                continue
            if installed:
                print(f"🔄 Version mismatch: {ver} → {pkg}")
                logger.warning(f"Version mismatch: {ver} → {pkg}")
            self._run_pip_command(['install', pkg], pkg)

    def _real_uninstall(self) -> None:
        if not self.package_list:
            print("❗ No packages to uninstall.")
            logger.warning("Uninstall called with empty package list.")
            return
        for pkg in self.package_list:
            print(f"\n🗑️ Uninstalling: {pkg}")
            logger.info(f"Uninstalling: {pkg}")
            self._run_pip_command(['uninstall', '-y', pkg], pkg, uninstall=True)

    def _real_update(self) -> None:
        if not self.package_list:
            print("❗ No packages to update.")
            logger.warning("Update called with empty package list.")
            return
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"],
                capture_output=True, text=True
            )
            outdated = json.loads(result.stdout)
            outdated_map = {pkg['name'].lower(): pkg['latest_version'] for pkg in outdated}
        except Exception as e:
            print("❌ Could not check outdated packages:", e)
            logger.error(f"Failed to retrieve outdated packages: {e}")
            return
        for pkg in self.package_list:
            name = pkg.split('==')[0].lower()
            if name in outdated_map:
                print(f"\n🔄 Updating: {name} → {outdated_map[name]}")
                logger.info(f"Updating: {name} → {outdated_map[name]}")
                self._run_pip_command(['install', '--upgrade', name], name)
            else:
                print(f"✅ {name} is up to date.")
                logger.info(f"{name} is already up to date.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        PythonLibInstaller.run_cli()
