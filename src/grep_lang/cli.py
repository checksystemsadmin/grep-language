import argparse
from pathlib import Path
from .runtime import execute

def main():
    parser = argparse.ArgumentParser(
        prog="grep",
        description="GREP — Global Retrieval, Execution & Processing"
    )
    parser.add_argument("file", help="GREP source file")
    args = parser.parse_args()

    source = Path(args.file).read_text(encoding="utf-8")
    for line in execute(source):
        print(line)

if __name__ == "__main__":
    main()
