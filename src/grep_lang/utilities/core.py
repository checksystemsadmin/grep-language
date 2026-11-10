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
}


def run_utility(name, arguments=None, root="."):
    if name not in IMPLEMENTATIONS:
        raise KeyError("Unknown or unimplemented utility: " + name)
    import inspect
    arguments = dict(arguments or {})
    if "root" in inspect.signature(IMPLEMENTATIONS[name]).parameters:
        arguments.setdefault("root", root)
    return IMPLEMENTATIONS[name](**arguments)
