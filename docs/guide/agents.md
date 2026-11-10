# GREP Agent Engineering Framework

Version: 1.0

## Overview

The GREP Agent Engineering Framework establishes consistent instructions,
responsibilities, and quality requirements for AI coding agents working
with the GREP repository.

Its purpose is to improve engineering consistency, documentation quality,
software testing, security awareness, and project integrity.

## Governance Structure

The framework consists of six documents.

| Document | Responsibility |
|---|---|
| `AGENTS.md` | Universal project instructions |
| `.github/copilot-instructions.md` | GitHub Copilot guidance |
| `agents/engineering.md` | Engineering and runtime development |
| `agents/qa.md` | Testing and quality assurance |
| `agents/integrity.md` | Security, attribution, and licensing |
| `docs/guide/agents.md` | Public architecture documentation |

## Agent Responsibilities

### Engineering Agent

Responsible for maintaining the runtime, command-line interface,
language implementation, examples, and engineering quality.

### QA Agent

Responsible for automated testing, metadata validation,
system diagnostics, and regression reporting.

### Integrity Agent

Responsible for reviewing security concerns, preserving
attribution and licensing, and identifying unsupported claims.

## Governance Principles

All agents must:

- Follow the universal instructions in `AGENTS.md`.
- Respect their actual tool permissions.
- Preserve existing project assets.
- Keep documentation consistent with implementation.
- Report test results honestly.
- Avoid exposing secrets or credentials.
- Obtain human approval for consequential changes.

## Human Oversight

The framework provides instructions and role definitions.
It does not automatically deploy autonomous agents or grant
additional repository permissions.

Humans retain authority over licensing, ownership, releases,
publishing, and other consequential project decisions.

## Quality Assurance

The standard validation commands are:

- `python -m unittest discover -s tests -v`
- `python -m grep_lang.cli validate`
- `python -m grep_lang.cli doctor`
- `git diff --check`

Agents must report actual results and outstanding limitations.

## Project Status

GREP is an experimental search-native programming language.
The agent framework is an initial governance specification,
not a certification of security or software completeness.

## Maintainer

Nolan G. Sands
