import importlib
import os
from pathlib import Path
import subprocess
import sys
from byper.constants import ENVIRONMENT_DIRECTORY

Logger = getattr(importlib.import_module("byper.utils.logger"), "Logger")


class Environment:
    @staticmethod
    def find_nested_venv():
        other_envs = []
        for root, dirs, files in os.walk(os.getcwd()):
            rel_root = os.path.relpath(root, os.getcwd())

            # Skip Packages/ itself
            if rel_root == "Packages" or rel_root.startswith("Packages" + os.sep):
                continue

            is_env = (
                "pyvenv.cfg" in files or
                "site-packages" in dirs or
                "bin" in dirs or
                "Scripts" in dirs
            )

            if is_env:
                other_envs.append(rel_root)

        if other_envs:
            Logger.log("↪ Found additional virtual environment-like folders:", indent=1, level="warn")
            for path in other_envs:
                Logger.log(f"- {path}", indent=2, level="warn")
                
        return other_envs

    @staticmethod
    def get_python_version():
        return f"{sys.version_info.major}.{sys.version_info.minor}"

    @staticmethod
    def get_install_dir():
        return f"Packages/lib/python{Environment.get_python_version()}/site-packages"

    @staticmethod
    def get_env_python():
        return os.path.join(ENVIRONMENT_DIRECTORY, "bin", "python")

    @staticmethod
    def ensure_dirs(workspace: str = "./"):
        if not os.path.exists(workspace + ENVIRONMENT_DIRECTORY):
            subprocess.check_call([
                sys.executable, "-m", "venv", workspace + ENVIRONMENT_DIRECTORY
            ])

    @staticmethod
    def get_library_root():
        return Path(__file__).resolve().parent.parent

    @staticmethod
    def get_cache_dir():
        cache_dir = Environment.get_library_root() / ".cache/packages"
        cache_dir.mkdir(parents=True, exist_ok=True)

        return cache_dir
