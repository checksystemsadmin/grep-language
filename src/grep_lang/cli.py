import argparse
import json
from pathlib import Path

from .runtime import execute

ROOT = Path(__file__).resolve().parents[2]
METADATA_FILE = ROOT / "metadata" / "grep.json"


def show_metadata():
    if not METADATA_FILE.exists():
        raise SystemExit("GREP metadata manifest not found.")

    data = json.loads(METADATA_FILE.read_text(encoding="utf-8"))

    project = data["project"]
    runtime = data["runtime"]

    print(f"{project['name']} — {project['fullName']}")
    print(f"Version:      {project['version']}")
    print(f"Creator:      {project['creator']}")
    print(f"License:      {project['license']}")
    print(f"Status:       {project['status']}")
    print(f"Runtime:      {runtime['implementation']}")
    print("Capabilities: " + ", ".join(data["capabilities"]))


def main():
    parser = argparse.ArgumentParser(
        prog="greplang",
        description="GREP — Global Retrieval, Execution & Processing"
    )

    parser.add_argument(
        "file",
        nargs="?",
        help="GREP source file or metadata command"
    )

    args = parser.parse_args()

    if args.file == "metadata":
        show_metadata()
        return

    if not args.file:
        parser.print_help()
        return

    source = Path(args.file).read_text(encoding="utf-8")

    for line in execute(source):
        print(line)


if __name__ == "__main__":
    main()
