from pathlib import Path

def execute(source, root=None):
    root = Path(root or ".").resolve()
    variables = {}
    output = []

    for line in source.splitlines():
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        if line.startswith("print "):
            value = line[6:].strip()
            if value.startswith("$"):
                value = variables[value[1:]]
            else:
                value = value.strip('"').strip("'")
            output.append(value)

        elif line.startswith("let "):
            name, value = line[4:].split("=", 1)
            variables[name.strip()] = value.strip().strip('"').strip("'")

        elif line.startswith("find "):
            parts = line[5:].split(" in ", 1)
            needle = parts[0].strip('"').strip("'")
            filename = parts[1].strip('"').strip("'")
            target = (root / filename).resolve()

            if not target.is_relative_to(root):
                raise ValueError("Path outside project root")

            if not target.is_file():
                raise FileNotFoundError(filename)

            for number, text in enumerate(
                target.read_text(encoding="utf-8").splitlines(), 1
            ):
                if needle in text:
                    output.append(f"{filename}:{number}:{text}")

        else:
            raise ValueError(f"Unknown instruction: {line}")

    return output
