import os
from byper.constants import REQUIREMENTS_FILE
from ruamel.yaml import YAML


class Manifest:
    @staticmethod
    def save_manifest(data: dict, new_line: bool = False):
        out_data = {
            "name": data.get("name", os.path.basename(os.getcwd())),
            "dependencies": data.get("dependencies", {}),
            "scripts": data.get("scripts", {})
        }

        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml.width = 4096

        with open(REQUIREMENTS_FILE, "w") as f:
            yaml.dump({"name": out_data["name"]}, f)
            if out_data["scripts"]:
                f.write("\n")
                yaml.dump({"scripts": out_data["scripts"]}, f)
            if new_line:
                f.write("\n")
            if out_data["dependencies"]:
                yaml.dump({"dependencies": out_data["dependencies"]}, f)

    @staticmethod
    def load_requirements_manifest():
        if not os.path.exists(REQUIREMENTS_FILE):
            return {"name": "", "dependencies": {}, "scripts": {}}

        yaml = YAML()
        with open(REQUIREMENTS_FILE, "r") as f:
            data = yaml.load(f) or {}

        return {
            "name": data.get("name", ""),
            "dependencies": data.get("dependencies", {}),
            "scripts": data.get("scripts", {})
        }

    @staticmethod
    def load_script_from_manifest(_script: str):
        if not os.path.exists(REQUIREMENTS_FILE):
            return {}

        yaml = YAML()
        with open(REQUIREMENTS_FILE, "r") as f:
            data = yaml.load(f) or {}

        scripts: dict = data.get("scripts", {})
        return scripts.get(_script)
