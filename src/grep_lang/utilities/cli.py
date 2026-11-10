"""GREP utility command-line interface."""
import argparse
import json

from . import IMPLEMENTATIONS, run_utility


def main(argv=None):
    parser = argparse.ArgumentParser(prog="greplang utils")
    commands = parser.add_subparsers(dest="command", required=True)

    listing = commands.add_parser("list", help="List implemented utilities")
    listing.add_argument("--implemented", action="store_true")

    runner = commands.add_parser("run", help="Execute a utility")
    runner.add_argument("name")
    runner.add_argument("--args", default="{}")

    args = parser.parse_args(argv)

    if args.command == "list":
        for name in sorted(IMPLEMENTATIONS):
            print(name)
        print("Implemented:", len(IMPLEMENTATIONS))
        return 0

    try:
        parameters = json.loads(args.args)
        if not isinstance(parameters, dict):
            raise ValueError("--args must be a JSON object")
        result = run_utility(args.name, parameters)
        print(json.dumps(result, indent=2, default=str))
        return 0
    except Exception as error:
        parser.exit(1, "GREP utility error: " + str(error) + "\n")
