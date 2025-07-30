import argparse
import os
import importlib
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import webbrowser
from colorama import Fore, Style
import pkg_resources
from byper.constants import REQUIREMENTS_FILE, ENVIRONMENT_DIRECTORY
from configparser import ConfigParser

Environment = getattr(importlib.import_module("byper.core.environment"), "Environment")
Manifest = getattr(importlib.import_module("byper.core.manifest"), "Manifest")
Logger = getattr(importlib.import_module("byper.utils.logger"), "Logger")
Installation = getattr(importlib.import_module("byper.core.installation"), "Installation")


class Commands:
    @staticmethod
    def doctor():
        Logger.log("🧠 Running environment diagnostics...")

        # Python version
        py_version = sys.version.split()[0]
        Logger.log(f"↪ Python version: {py_version}", indent=1, level="command")

        # Check for main 'Packages/' env
        packages_exists = os.path.isdir("Packages")

        # Check if environment is installed
        packages_exists = os.path.isdir("Packages")
        if packages_exists:
            Logger.log(f"↪ Python environment found at: {os.getcwd()}", indent=1, level="command")
        else:
            Logger.log("↪ Packages/ environment folder does not exist", indent=1, level="warn")

        # Internet access
        try:
            socket.create_connection(("pypi.org", 443), timeout=3)
            Logger.log("↪ Internet connectivity, successfully", indent=1, level="command")
        except Exception:
            Logger.log("↪ Internet connectivity, failed", indent=1, level="warn")

        # Warn about nested virtual environments (outside of Packages/)
        Environment.find_nested_venv()

        # Check for mismatched or broken packages
        broken_packages = []
        installed_packages = {dist.project_name: dist.version for dist in pkg_resources.working_set}

        for name, version in installed_packages.items():
            try:
                dist = pkg_resources.get_distribution(name)
                if dist.version != version:
                    broken_packages.append((name, version, dist.version))
            except Exception:
                broken_packages.append((name, version, "not installed"))

        if broken_packages:
            Logger.log("↪ Issues detected with installed packages:", indent=2, level="warn")
            for name, expected, actual in broken_packages:
                Logger.log(f"- {name}: expected {expected}, got {actual}", indent=3, level="warn")

        # Optional: print Python executable path
        Logger.log(f"↪ Python executable: {Environment.get_env_python()}", indent=1, level="command")

    @staticmethod
    def register_command():
        parser = argparse.ArgumentParser(add_help=False)
        subparsers = parser.add_subparsers(dest="command")

        parser.add_argument('-h', '--help', action='store_true', help='Show help')

        subparsers.add_parser("tree", help="Print directory tree")
        subparsers.add_parser("login", help="PyPI login")
        subparsers.add_parser("publish", help="Publish package to PyPI")
        subparsers.add_parser("doctor", help="Run dependencies diagnostics")

        parser.add_argument(
            "-v", "--version",
            help="Print byper version",
            action="store_true"
        )

        init_parser = subparsers.add_parser("init", help="Initialize byper project")
        init_parser.add_argument("name", nargs="?", default=None)

        add_parser = subparsers.add_parser("add", help="Add package to dependencies")
        add_parser.add_argument("packages", nargs="+")
        add_parser.add_argument(
            "--no-cache",
            action="store_true",
            help="Don't use cached packages",
        )

        run_parser = subparsers.add_parser("run", help="Run script")
        run_parser.add_argument("script")

        remove_parser = subparsers.add_parser("remove", help="Remove package from dependencies")
        remove_parser.add_argument("packages", nargs="+")

        return parser

    @staticmethod
    def print_help():
        Logger.log("List of byper commands and options:", level="info")
        Logger.log("Commands:", level="info")

        Logger.log("byper init                    Initialize byper project", indent=2, level="command")
        Logger.log("byper add <package-name>      Add package to dependencies", indent=2, level="command")
        Logger.log("byper tree                    Print directory tree", indent=2, level="command")
        Logger.log("byper run <script>            Run script", indent=2, level="command")
        Logger.log("byper remove <package-name>   Remove package from dependencies", indent=2, level="command")
        Logger.log("byper install                 Install dependencies", indent=2, level="command")
        Logger.log("byper                         Run byper by itself to install dependencies from Requirements", indent=2, level="command")

        Logger.log("\n")
        Logger.log("Options:", level="info")
        Logger.log("-h, --help                    Print help(byper -h, byper --help)", indent=2, level="command")
        Logger.log("--no-cache                    Install packages without use cached packages(byper add <package-name> --no-cache)", indent=2, level="command")

        exit()

    @staticmethod
    def print_directory_tree(start_path=".", prefix="", excluded_dirs={"Packages"}):
        try:
            entries = sorted(os.listdir(start_path))
        except OSError as e:
            print(f"{Fore.RED}Error accessing {start_path}: {e}")
            return

        files = []
        dirs = []

        for entry in entries:
            full_path = os.path.join(start_path, entry)
            if os.path.isdir(full_path):
                dirs.append(entry)
            else:
                files.append(entry)

        for index, directory in enumerate(dirs):
            is_last = index == len(dirs) - 1 and not files
            connector = "└── " if is_last else "├── "

            if directory in excluded_dirs:
                print(
                    f"{prefix}{connector}{Fore.LIGHTBLACK_EX}{directory}/*{Style.RESET_ALL}"
                )
            else:
                print(f"{prefix}{connector}{Fore.CYAN}{directory}/{Style.RESET_ALL}")
                new_prefix = f"{prefix}    " if is_last else f"{prefix}│   "
                Commands.print_directory_tree(
                    os.path.join(start_path, directory), new_prefix, excluded_dirs
                )

        for index, file in enumerate(files):
            is_last = index == len(files) - 1
            connector = "└── " if is_last else "├── "
            print(f"{prefix}{connector}{Fore.GREEN}{file}{Style.RESET_ALL}")

    @staticmethod
    def remove_package(package: str):
        try:
            Installation.uninstall(package)

        except ValueError as e:
            print(f"❌ {package} failed to remove: {e}")
            return

    @staticmethod
    def add_package(package, no_cache):
        try:
            Installation.reinstall_from_requirements()
            Installation.install(package, no_cache)

        except Exception as e:
            Logger.log(f"🗑️ {package} installation failed: {e}")

    @staticmethod
    def install():
        try:
            Installation.reinstall_from_requirements(True)

        except Exception as e:
            print(f"❌ {e}")

    @staticmethod
    def reinstall():
        Installation.reinstall_from_requirements()

    @staticmethod
    def init(name: str = None):
        if name:
            os.makedirs(name, exist_ok=True)
            os.chdir(name)

        if not os.path.exists(REQUIREMENTS_FILE):
            project_name = name or os.path.basename(os.getcwd())
            name = (
                input(f"Project name (default = {project_name}): ").strip()
                or project_name
            )

            entry = input("Entry point (default = main.py): ").strip() or "main.py"

            Manifest.save_manifest(
                {
                    "name": project_name,
                    "dependencies": {},
                    "scripts": {"start": f"python {entry}"},
                },
                True,
            )

            Environment.ensure_dirs()
            with open(entry, "w") as f:
                f.write("print('Hello, world!')")

            print(f"Initialized {REQUIREMENTS_FILE} environment in {os.getcwd()}")
        else:
            Logger.log(f"{REQUIREMENTS_FILE} manifest already exists in {os.getcwd()}")

            if not os.path.exists(ENVIRONMENT_DIRECTORY):
                Logger.log(f"📂 Creating missing {ENVIRONMENT_DIRECTORY} environment", indent=1, level="command")
                Logger.log(f"✅ {ENVIRONMENT_DIRECTORY} environment created", indent=1, level="success")
                Environment.ensure_dirs()

    @staticmethod
    def run_script(_script: str):
        script = Manifest.load_script_from_manifest(_script)
        if not script:
            print(f"Script '{_script}' not found in manifest.")
            return

        # Build environment for subprocess
        env_path = os.environ.copy()
        venv_bin = os.path.dirname(Environment.get_env_python())
        env_path["PATH"] = f"{venv_bin}:{env_path.get('PATH', '')}"
        env_path["VIRTUAL_ENV"] = os.path.abspath(os.path.dirname(venv_bin))

        subprocess.run(script, shell=True, env=env_path)

    @staticmethod
    def run_python_file(file_path: str):
        # Ensure it's a .py file
        if not file_path.endswith(".py"):
            Logger.log("❌ Only Python files (.py) can be executed.", level="debug")
            return

        # Get the path to the virtual environment's Python interpreter
        env_python = Environment.get_env_python()

        if not os.path.exists(env_python):
            Logger.log(f"❌ No byper environment found at {os.getcwd()}", level="debug")
            return

        # Build environment variables
        env_path = os.environ.copy()
        venv_bin = os.path.dirname(env_python)
        env_path["PATH"] = f"{venv_bin}{os.pathsep}{env_path.get('PATH', '')}"
        env_path["VIRTUAL_ENV"] = os.path.abspath(os.path.dirname(venv_bin))

        # Run the file using the virtual environment's Python
        try:
            subprocess.run([env_python, file_path], env=env_path, check=True)
        except subprocess.CalledProcessError as e:
            Logger.log(f"❌ Script exited with error: {e.returncode}")

    @staticmethod
    def login():
        Logger.log("🔐 PyPI Login Setup", newline=True, level="install")
        Logger.log(f"To upload packages to PyPI, you need an API token.")

        Logger.log(f"You can generate one here:")
        Logger.log(
            "→ https://pypi.org/manage/account/#api-tokens",
            indent=1,
            newline=True,
            level="command",
        )

        Logger.log("Opening link in your browser...", level="command")
        webbrowser.open("https://pypi.org/manage/account/#api-tokens")

        prompt = f"{Fore.BLUE}Enter your PyPI API token (starts with 'pypi-'): {Style.RESET_ALL}"
        token = input(prompt).strip()

        if not token.startswith("pypi-"):
            Logger.log(
                "⚠️ Warning: This doesn't look like a valid PyPI API token", level="warn"
            )
            return

        # Save token to ~/.pypirc
        pypirc_path = os.path.expanduser("~/.pypirc")
        config = ConfigParser()

        if os.path.exists(pypirc_path):
            config.read(pypirc_path)

        config["distutils"] = {"index-servers": "pypi"}
        config["pypi"] = {"username": "__token__", "password": token}

        with open(pypirc_path, "w") as f:
            config.write(f)

        Logger.log(
            f"\n✅ Login successful. Your PyPI token has been saved to {pypirc_path}.",
            level="success",
            newline=True,
        )

    @staticmethod
    def publish(dist_dir="dist"):
        project_root = Path.cwd()
        dist_path = project_root / dist_dir
        pypirc = Path.home() / ".pypirc"

        Logger.log("🚀 Preparing to upload your package to PyPI...\n")

        if not pypirc.exists():
            Logger.log(
                "❌ PyPI credentials not found. Please run the login command first."
            )
            return

        if (
            not (project_root / "setup.py").exists()
            and not (project_root / "pyproject.toml").exists()
        ):
            Logger.log("❌ No setup.py or pyproject.toml found. Cannot proceed.")
            return

        # Clean previous dist
        if dist_path.exists():
            shutil.rmtree(dist_path)

        Logger.log("📦 Building distribution using global Python...")

        try:
            subprocess.run(["python", "-m", "build"], check=True)
        except subprocess.CalledProcessError:
            Logger.log(
                "❌ Build failed. Make sure `build` is installed globally (e.g. pip install build)",
                level="error",
            )
            return

        Logger.log("📤 Uploading via twine using global Python...")

        try:
            subprocess.run(
                ["python", "-m", "twine", "upload", f"{dist_path}/*"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            Logger.log("✅ Successfully uploaded to PyPI!", level="success")

        except subprocess.CalledProcessError as e:
            Logger.log("❌ Upload failed.", level="error")
            if e.stdout:
                Logger.log(e.stdout.decode(), level="error")
