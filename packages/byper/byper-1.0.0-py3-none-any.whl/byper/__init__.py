import importlib
import sys
from byper.constants import VERSION
from byper.core.commands import Commands
from byper.core.environment import Environment


def main():

    if len(sys.argv) > 1 and sys.argv[1].endswith(".py"):
        Environment.find_nested_venv()
        Commands.run_python_file(sys.argv[1])
        return

    parser = Commands.register_command()
    args = parser.parse_args()

    if args.command != "doctor":
        Environment.find_nested_venv()

    if args.command == "init":
        Commands.init(args.name)

    elif args.command == "add":
        for pkg in args.packages:
            Commands.add_package(pkg, args.no_cache)

    elif args.command == "tree":
        Commands.print_directory_tree()

    elif args.command == "run":
        Commands.run_script(args.script)

    elif args.version or args.command == "version":
        Logger = getattr(importlib.import_module(
            "byper.utils.logger"), "Logger"
        )

        Logger.log(VERSION, level="info")

    elif args.help or args.command == "help":
        Commands.print_help()

    elif args.command == "remove":
        for pkg in args.packages:
            Commands.remove_package(pkg)

    elif args.command == "login":
        Commands.login()

    elif args.command == "publish":
        Commands.publish()

    elif args.command == "doctor":
        Commands.doctor()

    else:
        if len(sys.argv) > 1:
            Commands.print_help()

        else:
            Commands.install()


if __name__ == "__main__":
    main()
