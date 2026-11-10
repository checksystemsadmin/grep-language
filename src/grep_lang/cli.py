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



def validate_metadata():
    if not METADATA_FILE.exists():
        raise SystemExit("ERROR: GREP metadata manifest not found.")

    try:
        data = json.loads(METADATA_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as error:
        raise SystemExit(f"ERROR: Cannot read metadata: {error}")

    errors = []

    if not isinstance(data, dict):
        raise SystemExit("ERROR: Metadata root must be a JSON object.")

    if data.get("schemaVersion") != "1.0":
        errors.append("Missing or invalid schemaVersion.")

    project = data.get("project")
    if not isinstance(project, dict):
        errors.append("Missing project object.")
        project = {}

    for field in ("name", "fullName", "version", "status", "creator", "license"):
        if not isinstance(project.get(field), str) or not project[field].strip():
            errors.append(f"Missing or invalid project.{field}.")

    version = project.get("version", "")
    if isinstance(version, str) and not __import__("re").fullmatch(
        r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", version
    ):
        errors.append("Project version must use semantic version format.")

    runtime = data.get("runtime")
    if not isinstance(runtime, dict):
        errors.append("Missing runtime object.")
        runtime = {}

    for field in ("implementation", "cli"):
        if not isinstance(runtime.get(field), str) or not runtime[field].strip():
            errors.append(f"Missing or invalid runtime.{field}.")

    capabilities = data.get("capabilities")
    if not isinstance(capabilities, list) or not capabilities:
        errors.append("Capabilities must be a non-empty list.")
    elif not all(isinstance(item, str) and item.strip() for item in capabilities):
        errors.append("Every capability must be a non-empty string.")

    if errors:
        print("GREP metadata: INVALID")
        for error in errors:
            print(f" - {error}")
        raise SystemExit(1)

    print("GREP metadata: VALID")
    print(f"Version: {project['version']}")
    print(f"Capabilities checked: {len(capabilities)}")


def main():
    parser = argparse.ArgumentParser(
        prog="greplang",
        description="GREP — Global Retrieval, Execution & Processing"
    )

    parser.add_argument(
        "file",
        nargs="?",
        help="GREP source file, metadata, or validate command"
    )

    args = parser.parse_args()

    if args.file == "metadata":
        show_metadata()
        return

    if args.file == "validate":
        validate_metadata()
        return

    if not args.file:
        parser.print_help()
        return

    source = Path(args.file).read_text(encoding="utf-8")

    for line in execute(source):
        print(line)


if __name__ == "__main__":
    main()
