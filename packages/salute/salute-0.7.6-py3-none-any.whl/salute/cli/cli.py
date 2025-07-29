import argparse
from pathlib import Path
import tomllib
from salute.cli.actions import InitScenarioAction


def get_version() -> str:
    try:
        with Path("project.toml").open("rb") as f:
            toml_dict = tomllib.load(f)
            return toml_dict.get("project", {}).get("version", "0.0.0")
    except (FileNotFoundError, tomllib.TOMLDecodeError):
        return "0.0.0"


def command():
    parser = argparse.ArgumentParser(
        description="Salute CLI tool for managing your application"
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {get_version()}",
        help="Show program's version number and exit",
    )
    parser.add_argument(
        "-i",
        "--init",
        action=InitScenarioAction,
        help="Execute init scenario to prepare your application",
        nargs=0,
    )

    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        return
