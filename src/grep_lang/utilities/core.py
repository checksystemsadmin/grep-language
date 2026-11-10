"""GREP Utility Standard — initial working utility implementations."""

import csv
import difflib
import hashlib
import json
import math
import re
import sqlite3
import unicodedata
from collections import defaultdict
from pathlib import Path
import ast
import os
import stat
import subprocess
import time
import zipfile
from collections import Counter


def safe_path(path, root="."):
    base = Path(root).resolve()
    target = (base / path).resolve()
    if not target.is_relative_to(base):
        raise ValueError("Path outside project root")
    return target


def file_walker(path=".", pattern="*", root="."):
    base = safe_path(path, root)
    return [str(p.relative_to(base)) for p in sorted(base.rglob(pattern)) if p.is_file()]


def file_hasher(path, algorithm="sha256", root="."):
    target = safe_path(path, root)
    digest = hashlib.new(algorithm)
    with target.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return {"algorithm": algorithm, "digest": digest.hexdigest()}


def file_type_detect(path, root="."):
    target = safe_path(path, root)
    with target.open("rb") as stream:
        header = stream.read(16)
    signatures = {
        b"\x89PNG\r\n\x1a\n": "image/png",
        b"\xff\xd8\xff": "image/jpeg",
        b"PK\x03\x04": "application/zip",
        b"%PDF": "application/pdf",
        b"\x1f\x8b": "application/gzip",
    }
    mime = next((v for k, v in signatures.items() if header.startswith(k)), None)
    if mime is None:
        mime = {
            ".json": "application/json", ".csv": "text/csv",
            ".txt": "text/plain", ".md": "text/markdown",
            ".py": "text/x-python", ".grep": "text/x-grep",
        }.get(target.suffix.lower(), "application/octet-stream")
    return {"mime": mime, "size": target.stat().st_size}


def csv_streamer(path, limit=1000, root="."):
    target = safe_path(path, root)
    rows = []
    with target.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        columns = reader.fieldnames or []
        for row in reader:
            if len(rows) >= limit:
                break
            rows.append(row)
    return {"columns": columns, "rows": rows, "returned": len(rows)}


def json_lines_reader(path, limit=1000, root="."):
    target = safe_path(path, root)
    records = []
    with target.open(encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            if len(records) >= limit:
                break
            if line.strip():
                records.append({"line": number, "value": json.loads(line)})
    return records


def json_validator(path, root="."):
    try:
        with safe_path(path, root).open(encoding="utf-8") as stream:
            json.load(stream)
        return {"valid": True, "error": None}
    except (ValueError, OSError) as error:
        return {"valid": False, "error": str(error)}


def regex_search(path, pattern, root="."):
    target = safe_path(path, root)
    regex = re.compile(pattern)
    matches = []
    with target.open(encoding="utf-8", errors="replace") as stream:
        for number, line in enumerate(stream, 1):
            if regex.search(line):
                matches.append({"line": number, "text": line.rstrip("\n")})
    return matches


def fuzzy_match(query, choices, limit=10):
    return difflib.get_close_matches(query, choices, n=limit, cutoff=0.0)


def text_normalizer(text):
    text = unicodedata.normalize("NFKC", text).casefold()
    return " ".join(re.findall(r"\w+", text, flags=re.UNICODE))


def inverted_index(documents):
    index = defaultdict(list)
    for doc_id, content in enumerate(documents):
        for term in set(text_normalizer(content).split()):
            index[term].append(doc_id)
    return dict(index)


def bm25_ranker(query, documents, k1=1.5, b=0.75):
    terms = text_normalizer(query).split()
    docs = [text_normalizer(doc).split() for doc in documents]
    if not docs:
        return []
    average = sum(map(len, docs)) / len(docs) or 1
    results = []
    for doc_id, words in enumerate(docs):
        score = 0.0
        for term in terms:
            frequency = words.count(term)
            if not frequency:
                continue
            document_frequency = sum(term in doc for doc in docs)
            idf = math.log(1 + (len(docs) - document_frequency + 0.5)
                           / (document_frequency + 0.5))
            denominator = frequency + k1 * (
                1 - b + b * len(words) / average
            )
            score += idf * frequency * (k1 + 1) / denominator
        results.append({"document": doc_id, "score": score})
    return sorted(results, key=lambda item: item["score"], reverse=True)


def text_chunker(text, chunk_size=1000, overlap=100):
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Require chunk_size > overlap >= 0")
    step = chunk_size - overlap
    return [text[i:i + chunk_size] for i in range(0, len(text), step)]


def env_parser(path, root="."):
    target = safe_path(path, root)
    values = {}
    for line in target.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip("'\"")
    return values


def gradle_log_analyzer(path, root="."):
    lines = safe_path(path, root).read_text(errors="replace").splitlines()
    counts = {"error": 0, "warning": 0, "failure": 0}
    examples = []
    for number, line in enumerate(lines, 1):
        lower = line.lower()
        for level in counts:
            if level in lower:
                counts[level] += 1
                if len(examples) < 50:
                    examples.append({"line": number, "level": level, "text": line})
                break
    return {"counts": counts, "examples": examples}


def gradle_project_scanner(path=".", root="."):
    target = safe_path(path, root)
    names = (
        "settings.gradle", "settings.gradle.kts",
        "build.gradle", "build.gradle.kts", "gradlew",
    )
    found = [name for name in names if (target / name).is_file()]
    return {"is_gradle_project": bool(found), "files": found}


def dependency_inventory(path="pyproject.toml", root="."):
    target = safe_path(path, root)
    text = target.read_text(encoding="utf-8")
    match = re.search(r"(?ms)^\s*dependencies\s*=\s*\[(.*?)^\s*\]", text)
    dependencies = re.findall(r"""['"]([^'"]+)['"]""", match.group(1)) if match else []
    return {"source": target.name, "dependencies": dependencies}


def markdown_link_checker(path, root="."):
    target = safe_path(path, root)
    content = target.read_text(encoding="utf-8")
    links = re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", content)
    results = []
    for link in links:
        clean = link.split("#", 1)[0].strip()
        if not clean or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", clean):
            continue
        resolved = (target.parent / clean).resolve()
        results.append({"link": link, "exists": resolved.is_file()})
    return results


def secret_pattern_scanner(path, root="."):
    target = safe_path(path, root)
    patterns = {
        "private_key": r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
        "aws_access_key": r"\bAKIA[0-9A-Z]{16}\b",
        "generic_token": (
            r"(?i)\b(?:api[_-]?key|secret|token)\s*[:=]\s*"
            r"['\"]?[A-Za-z0-9_./+=-]{16,}"
        ),
    }
    findings = []
    for number, line in enumerate(target.read_text(errors="replace").splitlines(), 1):
        for name, pattern in patterns.items():
            if re.search(pattern, line):
                findings.append({"line": number, "type": name})
    return findings


def sqlite_reader(path, query="SELECT name FROM sqlite_master WHERE type='table'",
                  root="."):
    target = safe_path(path, root)
    if not re.match(r"^\s*(SELECT|PRAGMA)\b", query, re.I):
        raise ValueError("Only SELECT and PRAGMA queries are permitted")
    with sqlite3.connect(target.as_uri() + "?mode=ro", uri=True) as connection:
        cursor = connection.execute(query)
        return {
            "columns": [item[0] for item in cursor.description or []],
            "rows": cursor.fetchmany(1000),
        }


def build_report(root="."):
    base = Path(root).resolve()
    excluded = {".git", "__pycache__", ".venv"}
    files = [
        p for p in base.rglob("*")
        if p.is_file() and not any(part in excluded for part in p.parts)
    ]
    extensions = defaultdict(int)
    for item in files:
        extensions[item.suffix.lower() or "[no extension]"] += 1
    return {
        "root": str(base),
        "file_count": len(files),
        "extension_counts": dict(sorted(extensions.items())),
        "has_readme": (base / "README.md").is_file(),
        "has_tests": (base / "tests").is_dir(),
    }


# ---------------------------------------------------------------------------
# GREP Utility Standard — Batch 2: Filesystem and source intelligence
# Utilities 21–40
# ---------------------------------------------------------------------------

def _utility_files(path=".", root="."):
    base = safe_path(path, root)
    if base.is_file():
        return [base]
    if not base.is_dir():
        raise NotADirectoryError(str(base))
    excluded = {".git", ".venv", "__pycache__", "node_modules"}
    return [
        item for item in sorted(base.rglob("*"))
        if item.is_file()
        and not any(part in excluded for part in item.relative_to(base).parts)
    ]


def directory_size(path=".", root="."):
    base = safe_path(path, root)
    files = _utility_files(path, root)
    return {
        "path": str(base),
        "file_count": len(files),
        "total_bytes": sum(item.stat().st_size for item in files),
    }


def duplicate_finder(path=".", root="."):
    base = safe_path(path, root)
    groups = {}
    for item in _utility_files(path, root):
        digest = hashlib.sha256()
        with item.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        groups.setdefault(digest.hexdigest(), []).append(
            str(item.relative_to(base))
        )
    return [
        {"sha256": digest, "files": names}
        for digest, names in groups.items() if len(names) > 1
    ]


def large_file_finder(path=".", min_bytes=10_000_000, limit=100, root="."):
    if min_bytes < 0 or limit < 1:
        raise ValueError("min_bytes must be nonnegative and limit must be positive")
    files = _utility_files(path, root)
    found = [
        {"path": str(p.relative_to(safe_path(root, "."))),
         "size_bytes": p.stat().st_size}
        for p in files if p.stat().st_size >= min_bytes
    ]
    return sorted(found, key=lambda item: item["size_bytes"], reverse=True)[:limit]


def empty_file_finder(path=".", root="."):
    return [
        str(item.relative_to(safe_path(root, ".")))
        for item in _utility_files(path, root)
        if item.stat().st_size == 0
    ]


def file_age_analyzer(path=".", older_than_days=30, root="."):
    if older_than_days < 0:
        raise ValueError("older_than_days must be nonnegative")
    now = time.time()
    results = []
    for item in _utility_files(path, root):
        age = max(0.0, (now - item.stat().st_mtime) / 86400)
        results.append({
            "path": str(item.relative_to(safe_path(root, "."))),
            "age_days": round(age, 2),
            "older_than_threshold": age >= older_than_days,
        })
    return sorted(results, key=lambda item: item["age_days"], reverse=True)


def permission_auditor(path=".", root="."):
    results = []
    for item in _utility_files(path, root):
        mode = item.stat().st_mode
        results.append({
            "path": str(item.relative_to(safe_path(root, "."))),
            "mode": stat.filemode(mode),
            "world_writable": bool(mode & stat.S_IWOTH),
            "executable": bool(mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)),
        })
    return results


def symlink_inspector(path=".", root="."):
    base = safe_path(path, root)
    candidates = [base] if base.is_symlink() else base.rglob("*")
    results = []
    for item in candidates:
        if item.is_symlink():
            target = os.readlink(item)
            resolved = (item.parent / target).resolve()
            results.append({
                "path": str(item.relative_to(safe_path(root, "."))),
                "target": target,
                "exists": resolved.exists(),
                "within_root": resolved.is_relative_to(Path(root).resolve()),
            })
    return results


def archive_inspector(path, root="."):
    target = safe_path(path, root)
    if not zipfile.is_zipfile(target):
        raise ValueError("Unsupported or invalid ZIP archive")
    with zipfile.ZipFile(target) as archive:
        entries = archive.infolist()
        return {
            "archive": target.name,
            "entry_count": len(entries),
            "total_uncompressed_bytes": sum(x.file_size for x in entries),
            "entries": [
                {"name": x.filename, "size": x.file_size,
                 "compressed_size": x.compress_size,
                 "is_directory": x.is_dir()}
                for x in entries[:1000]
            ],
        }


def encoding_detector(path, root="."):
    target = safe_path(path, root)
    data = target.read_bytes()
    if b"\x00" in data:
        return {"encoding": "binary", "valid_text": False}
    for encoding in ("utf-8-sig", "utf-16", "utf-8"):
        try:
            data.decode(encoding)
            return {"encoding": encoding, "valid_text": True}
        except UnicodeDecodeError:
            pass
    return {"encoding": "latin-1", "valid_text": True}


def line_counter(path, root="."):
    target = safe_path(path, root)
    counts = {"lines": 0, "blank_lines": 0, "nonblank_lines": 0}
    with target.open("r", encoding="utf-8", errors="replace") as stream:
        for line in stream:
            counts["lines"] += 1
            if line.strip():
                counts["nonblank_lines"] += 1
            else:
                counts["blank_lines"] += 1
    return {"path": str(target), **counts}


def extension_report(path=".", root="."):
    counts = Counter()
    for item in _utility_files(path, root):
        counts[item.suffix.lower() or "[no extension]"] += 1
    return {"total_extensions": len(counts), "counts": dict(sorted(counts.items()))}


def git_change_analyzer(path=".", root="."):
    target = safe_path(path, root)
    cwd = target if target.is_dir() else target.parent
    try:
        output = subprocess.check_output(
            ["git", "-C", str(cwd), "status", "--short"],
            text=True, stderr=subprocess.PIPE, timeout=10
        )
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as error:
        raise RuntimeError("Unable to inspect Git working tree: " + str(error)) from error
    lines = output.splitlines()
    return {
        "changed_count": len(lines),
        "changes": [{"status": line[:2], "path": line[3:]} for line in lines],
    }


def git_blame_reader(path, line=None, root="."):
    target = safe_path(path, root)
    relative = str(target.relative_to(Path(root).resolve()))
    command = ["git", "-C", str(Path(root).resolve()),
               "blame", "--line-porcelain"]
    if line is not None:
        if line < 1:
            raise ValueError("line must be a positive integer")
        command.extend(["-L", str(line) + "," + str(line)])
    command.extend(["--", relative])
    try:
        output = subprocess.check_output(
            command, text=True, stderr=subprocess.PIPE, timeout=15
        )
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as error:
        raise RuntimeError("Unable to read Git blame: " + str(error)) from error
    records = []
    current = {}
    for item in output.splitlines():
        if item.startswith("\t"):
            current["text"] = item[1:]
            records.append(current)
            current = {}
        elif item.startswith("author "):
            current["author"] = item[7:]
        elif item.startswith("summary "):
            current["summary"] = item[8:]
        elif re.match(r"^[0-9a-f]{40} ", item):
            parts = item.split()
            current["commit"] = parts[0]
            current["line"] = int(parts[2])
    return records


def source_file_classifier(path, root="."):
    target = safe_path(path, root)
    groups = {
        ".py": "python", ".pyi": "python", ".grep": "grep",
        ".js": "javascript", ".mjs": "javascript", ".cjs": "javascript",
        ".ts": "typescript", ".tsx": "typescript", ".jsx": "javascript",
        ".rs": "rust", ".go": "go", ".java": "java",
        ".c": "c", ".h": "c-header", ".cpp": "cpp", ".hpp": "cpp-header",
        ".html": "html", ".css": "css", ".sql": "sql",
        ".sh": "shell", ".bash": "shell", ".toml": "toml",
        ".yaml": "yaml", ".yml": "yaml", ".json": "json",
        ".md": "markdown",
    }
    return {
        "path": str(target),
        "extension": target.suffix.lower(),
        "language": groups.get(target.suffix.lower(), "unknown"),
    }


def code_symbol_extractor(path, root="."):
    target = safe_path(path, root)
    if target.suffix.lower() == ".py":
        tree = ast.parse(target.read_text(encoding="utf-8"))
        symbols = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                symbols.append({
                    "name": node.name,
                    "kind": "class" if isinstance(node, ast.ClassDef) else "function",
                    "line": node.lineno,
                })
        return sorted(symbols, key=lambda item: item["line"])
    text = target.read_text(encoding="utf-8", errors="replace")
    pattern = re.compile(
        r"(?m)^\s*(?:export\s+)?(?:async\s+)?"
        r"(?:function|class|def|fn|struct|interface|type)\s+([A-Za-z_$][\w$]*)"
    )
    return [{"name": match.group(1), "kind": "declaration",
             "line": text.count("\n", 0, match.start()) + 1}
            for match in pattern.finditer(text)]


def import_graph(path=".", root="."):
    base = safe_path(path, root)
    files = [base] if base.is_file() else list(base.rglob("*.py"))
    graph = {}
    for item in files:
        if item.suffix != ".py":
            continue
        try:
            tree = ast.parse(item.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            graph[str(item.relative_to(safe_path(root, ".")))] = {"error": "parse_error"}
            continue
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module)
        graph[str(item.relative_to(safe_path(root, ".")))] = sorted(imports)
    return graph


def dead_file_detector(path=".", root="."):
    files = _utility_files(path, root)
    text_files = []
    for item in files:
        if item.suffix.lower() in {".py", ".grep", ".md", ".toml", ".json",
                                  ".yaml", ".yml", ".txt", ".js", ".ts"}:
            try:
                text_files.append((item, item.read_text(encoding="utf-8")))
            except (UnicodeDecodeError, OSError):
                pass
    results = []
    for candidate in files:
        name = candidate.name
        references = []
        for other, content in text_files:
            if other == candidate:
                continue
            if name in content:
                references.append(str(other.relative_to(safe_path(root, "."))))
        if not references:
            results.append({
                "path": str(candidate.relative_to(safe_path(root, "."))),
                "status": "possibly_unreferenced",
                "warning": "Heuristic only; dynamic references may be missed",
            })
    return results


def project_tree(path=".", max_entries=500, root="."):
    if max_entries < 1:
        raise ValueError("max_entries must be positive")
    base = safe_path(path, root)
    excluded = {".git", ".venv", "__pycache__", "node_modules"}
    entries = []
    for item in sorted(base.rglob("*")):
        if any(part in excluded for part in item.relative_to(base).parts):
            continue
        entries.append({
            "path": str(item.relative_to(base)),
            "type": "directory" if item.is_dir() else "file",
        })
        if len(entries) >= max_entries:
            break
    return {"root": str(base), "entries": entries, "truncated": len(entries) >= max_entries}


def file_diff_engine(path_a, path_b, root="."):
    left = safe_path(path_a, root).read_text(encoding="utf-8", errors="replace").splitlines()
    right = safe_path(path_b, root).read_text(encoding="utf-8", errors="replace").splitlines()
    return list(difflib.unified_diff(
        left, right, fromfile=str(path_a), tofile=str(path_b), lineterm=""
    ))


def file_snapshot(path, root="."):
    target = safe_path(path, root)
    info = target.stat()
    digest = hashlib.sha256()
    with target.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return {
        "path": str(target.relative_to(Path(root).resolve())),
        "size_bytes": info.st_size,
        "modified_time": info.st_mtime,
        "mode": stat.filemode(info.st_mode),
        "sha256": digest.hexdigest(),
    }


IMPLEMENTATIONS = {
    "file_walker": file_walker,
    "file_hasher": file_hasher,
    "file_type_detect": file_type_detect,
    "csv_streamer": csv_streamer,
    "json_lines_reader": json_lines_reader,
    "json_validator": json_validator,
    "regex_search": regex_search,
    "fuzzy_match": fuzzy_match,
    "text_normalizer": text_normalizer,
    "inverted_index": inverted_index,
    "bm25_ranker": bm25_ranker,
    "text_chunker": text_chunker,
    "env_parser": env_parser,
    "gradle_log_analyzer": gradle_log_analyzer,
    "gradle_project_scanner": gradle_project_scanner,
    "dependency_inventory": dependency_inventory,
    "markdown_link_checker": markdown_link_checker,
    "secret_pattern_scanner": secret_pattern_scanner,
    "sqlite_reader": sqlite_reader,
    "build_report": build_report,

    "directory_size": directory_size,
    "duplicate_finder": duplicate_finder,
    "large_file_finder": large_file_finder,
    "empty_file_finder": empty_file_finder,
    "file_age_analyzer": file_age_analyzer,
    "permission_auditor": permission_auditor,
    "symlink_inspector": symlink_inspector,
    "archive_inspector": archive_inspector,
    "encoding_detector": encoding_detector,
    "line_counter": line_counter,
    "extension_report": extension_report,
    "git_change_analyzer": git_change_analyzer,
    "git_blame_reader": git_blame_reader,
    "source_file_classifier": source_file_classifier,
    "code_symbol_extractor": code_symbol_extractor,
    "import_graph": import_graph,
    "dead_file_detector": dead_file_detector,
    "project_tree": project_tree,
    "file_diff_engine": file_diff_engine,
    "file_snapshot": file_snapshot,

}


def run_utility(name, arguments=None, root="."):
    if name not in IMPLEMENTATIONS:
        raise KeyError("Unknown or unimplemented utility: " + name)
    import inspect
    arguments = dict(arguments or {})
    if "root" in inspect.signature(IMPLEMENTATIONS[name]).parameters:
        arguments.setdefault("root", root)
    return IMPLEMENTATIONS[name](**arguments)
