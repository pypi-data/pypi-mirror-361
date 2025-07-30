import os
import platform
import subprocess
import csv
import importlib.metadata
import json
import re
import sys
import venv

def set_utf8_terminal_encoding():
    system = platform.system()

    if system == "Windows":
        try:
            subprocess.run("chcp 65001", shell=True, check=True)
            print("✅ Windows terminal set to UTF-8 (chcp 65001).")
        except subprocess.CalledProcessError:
            print("❌ Failed to set Windows code page to UTF-8.")
    
    elif system in ["Linux", "Darwin"]:
        try:
            # Set environment variables
            os.environ["LC_ALL"] = "en_US.UTF-8"
            os.environ["LANG"] = "en_US.UTF-8"

            # Reconfigure Python output streams if supported
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8")
                sys.stderr.reconfigure(encoding="utf-8")
                print("✅ sys.stdout/stderr reconfigured to UTF-8.")
            
            print("✅ Environment variables LANG and LC_ALL set to UTF-8.")
            print("🌐 Terminal UTF-8 test: ✓ ✓ ✓")
        except Exception as e:
            print(f"❌ Failed to enforce UTF-8 on {system}: {e}")
    
    else:
        print(f"⚠️ Unsupported platform: {system}")

class PythonLibInstaller:
    def __init__(self, auto_create_venv=False):
        set_utf8_terminal_encoding()
        self.package_list = []
        self.os_name = os.name
        self.platform_name = platform.system()
        self.default_path = os.path.abspath(__file__)
        self._check_virtualenv(auto_create_venv)

    def _check_virtualenv(self, auto_create=False):
        if sys.prefix == sys.base_prefix:
            print("⚠️ Not using a virtual environment.")
            if auto_create:
                print("🛠 Creating virtual environment in `.venv`...")
                venv.create('.venv', with_pip=True)
                print("✅ Virtual environment created. Please activate it before proceeding.")
            else:
                print("💡 Tip: Use a virtual environment to avoid conflicts.")

    def _is_valid_package_name(self, name):
        return re.match(r'^[a-zA-Z0-9\-_]+(==\d+(\.\d+){0,2})?$', name) is not None

    def get_list_from_txt(self, _file_location):
        try:
            with open(_file_location, 'r') as f:
                self.package_list = [
                    pkg.strip() for pkg in f.readlines()
                    if pkg.strip() and not pkg.strip().startswith('#')
                ]
        except FileNotFoundError:
            print("❌ The file doesn't exist.")

    def get_list_from_csv(self, _file_location):
        try:
            with open(_file_location, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and not row[0].strip().startswith('#'):
                        self.package_list.append(row[0].strip())
        except FileNotFoundError:
            print("❌ The file doesn't exist.")

    def get_list(self, packages):
        if not packages:
            print("⚠️ The packages aren't present in the given list.")
        else:
            self.package_list.extend(packages)

    def _is_package_already_installed(self, package_string):
        if '==' in package_string:
            pkg_name, target_version = package_string.split('==')
        else:
            pkg_name = package_string
            target_version = None

        try:
            installed_version = importlib.metadata.version(pkg_name)
            if target_version:
                if installed_version == target_version:
                    return True, None
                else:
                    return True, installed_version
            else:
                return True, None
        except importlib.metadata.PackageNotFoundError:
            return False, None

    def _run_pip_command(self, args, package, uninstall=False):
        result = subprocess.run([sys.executable, '-m', 'pip'] + args,
                                capture_output=True, text=True)

        stderr = result.stderr.strip()
        if result.returncode != 0:
            if "Could not find a version" in stderr:
                print(f"❌ ERROR: No such version ➤ {package}")
            elif "No matching distribution found" in stderr:
                print(f"❌ ERROR: Platform mismatch ➤ {package}")
            elif "Temporary failure in name resolution" in stderr or "ConnectionError" in stderr:
                print("🌐 Network error: Please check your internet connection.")
            elif "Permission denied" in stderr.lower():
                print("🔐 Permission error: Try running as administrator or with sudo.")
            elif uninstall and "not installed" in stderr.lower():
                print(f"⚠️ {package} is not installed, skipping.")
            else:
                print(f"⚠️ Failed to {'uninstall' if uninstall else 'install'}: {package}")
                print(stderr)
            return False
        else:
            print(f"✅ Successfully {'uninstalled' if uninstall else 'installed'}: {package}")
            return True

    def _write_temp_package_list(self):
        temp_file = os.path.join(os.path.dirname(__file__), "_temp_packages.txt")
        with open(temp_file, "w") as f:
            for pkg in self.package_list:
                f.write(pkg + "\n")
        return temp_file

    def _launch_terminal_cli(self, action_flag, file_path=None):
        if file_path is None:
            file_path = "requirements.txt"

        script_path = os.path.abspath(__file__)
        system = platform.system()

        if system == "Windows":
            command = f'cmd /c start "" cmd /k python "{script_path}" {action_flag} "{file_path}"'
            subprocess.run(command, shell=True)

        elif system == "Linux":
            subprocess.Popen([
                "x-terminal-emulator", "-e",
                f'python3 "{script_path}" {action_flag} "{file_path}"'
            ])

        elif system == "Darwin":  # macOS
            subprocess.Popen([
                "osascript", "-e",
                f'tell application "Terminal" to do script "python3 \\"{script_path}\\" {action_flag} \\"{file_path}\\""'
            ])
        else:
            print("❌ Unsupported OS for terminal CLI launching.")

    def install(self):
        print("📦 Launching terminal for install...")
        file_path = self._write_temp_package_list() if self.package_list else "requirements.txt"
        self._launch_terminal_cli("--install", file_path)

    def uninstall(self):
        print("🧹 Launching terminal for uninstall...")
        file_path = self._write_temp_package_list() if self.package_list else "requirements.txt"
        self._launch_terminal_cli("--uninstall", file_path)

    def update(self):
        print("🔄 Launching terminal for update...")
        file_path = self._write_temp_package_list() if self.package_list else "requirements.txt"
        self._launch_terminal_cli("--update", file_path)

    @staticmethod
    def run_cli():
        import argparse

        parser = argparse.ArgumentParser(description="📦 Python Library Installer CLI Tool")

        parser.add_argument(
            "--install", metavar="FILE", help="Install packages from .txt or .csv file"
        )
        parser.add_argument(
            "--uninstall", metavar="FILE", help="Uninstall packages from .txt or .csv file"
        )
        parser.add_argument(
            "--update", metavar="FILE", help="Update packages from .txt or .csv file"
        )
        parser.add_argument(
            "--venv", action="store_true", help="Auto-create virtual environment if not found"
        )

        args = parser.parse_args()
        manager = PythonLibInstaller(auto_create_venv=args.venv)

        def load_file(file):
            if file.endswith('.txt'):
                manager.get_list_from_txt(file)
            elif file.endswith('.csv'):
                manager.get_list_from_csv(file)
            else:
                print(f"❌ Unsupported file format: {file}")
                return False
            return True

        if args.install:
            if load_file(args.install):
                manager._real_install()

        if args.uninstall:
            if load_file(args.uninstall):
                manager._real_uninstall()

        if args.update:
            if load_file(args.update):
                manager._real_update()

    def _real_install(self):
        if not self.package_list:
            print("❗ No packages to install.")
            return

        success_count, fail_count = 0, 0
        for package in self.package_list:
            print(f"\n📦 Installing: {package}")
            if not self._is_valid_package_name(package):
                print(f"❌ Invalid package: {package}")
                fail_count += 1
                continue

            already_installed, version_info = self._is_package_already_installed(package)
            if already_installed and version_info is None:
                print(f"✅ Already installed: {package}")
                success_count += 1
                continue

            if already_installed:
                print(f"🔄 Reinstalling due to version mismatch: {version_info} → {package}")

            if self._run_pip_command(['install', package], package):
                success_count += 1
            else:
                fail_count += 1

        print("\n📋 Install Summary:")
        print(f"✅ Installed: {success_count}")
        print(f"❌ Failed: {fail_count}")

    def _real_uninstall(self):
        if not self.package_list:
            print("❗ No packages to uninstall.")
            return

        success_count, fail_count = 0, 0
        for package in self.package_list:
            print(f"\n🗑️ Uninstalling: {package}")
            if self._run_pip_command(['uninstall', '-y', package], package, uninstall=True):
                success_count += 1
            else:
                fail_count += 1

        print("\n📋 Uninstall Summary:")
        print(f"✅ Uninstalled: {success_count}")
        print(f"❌ Failed: {fail_count}")

    def _real_update(self):
        if not self.package_list:
            print("❗ No packages to update.")
            return

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"],
                capture_output=True, text=True
            )
            outdated = json.loads(result.stdout)
            outdated_map = {pkg['name'].lower(): pkg['latest_version'] for pkg in outdated}
        except Exception as e:
            print("❌ Could not retrieve outdated packages:", str(e))
            return

        success_count, fail_count = 0, 0
        for package in self.package_list:
            pkg_name = package.split('==')[0].lower()
            if pkg_name in outdated_map:
                print(f"\n🔄 Updating: {pkg_name} → {outdated_map[pkg_name]}")
                if self._run_pip_command(['install', '--upgrade', pkg_name], pkg_name):
                    success_count += 1
                else:
                    fail_count += 1
            else:
                print(f"✅ {pkg_name} is already up to date.")
                success_count += 1

        print("\n📋 Update Summary:")
        print(f"✅ Updated: {success_count}")
        print(f"❌ Failed: {fail_count}")

# 🧠 Enables CLI execution when terminal launches this script
if __name__ == "__main__":
    if len(sys.argv) > 1:
        PythonLibInstaller.run_cli()
