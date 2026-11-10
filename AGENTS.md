# GREP Agent Engineering Standards

Version: 1.0
Project: GREP
Full name: Global Retrieval, Execution & Processing
Repository: checksystemsadmin/grep-language
Project creator: Nolan G. Sands

## 1. Purpose

This document establishes universal instructions for AI coding agents
working in the GREP repository.

## 2. Authority

- Follow the repository's documented requirements.
- Treat this file as the project-wide agent instruction baseline.
- Follow specialized instructions in agents/ when performing that role.
- Follow .github/copilot-instructions.md when operating through GitHub Copilot.
- Human project authorization takes precedence over agent assumptions.

## 3. Repository preservation

- Preserve docs/index.html, the existing GREP marketing page.
- Keep technical GitBook documentation in docs/guide/.
- Preserve gitbook-docs.yaml unless an authorized configuration change is needed.
- Do not delete, rename, or overwrite project files without justification and approval.

## 4. Engineering requirements

- Understand existing architecture before changing code.
- Prefer focused, reviewable changes.
- Maintain compatibility with Python 3.9 and newer.
- Keep dependencies justified and documented.
- Never claim functionality exists unless implemented and tested.

## 5. Quality requirements

Before proposing a release, run:

- python -m unittest discover -s tests -v
- python -m grep_lang.cli validate
- python -m grep_lang.cli doctor
- git diff --check

Report failures honestly.

## 6. Security

- Do not expose secrets, credentials, tokens, or private information.
- Validate file paths and user-controlled input.
- Avoid unsafe execution and unauthorized filesystem access.
- Report security concerns rather than silently suppressing them.

## 7. Documentation

- Keep README.md, CHANGELOG.md, and docs/guide/ consistent with actual behavior.
- Document limitations and experimental functionality.
- Do not invent capabilities, benchmarks, endorsements, or integrations.

## 8. Integrity and ownership

- Preserve existing copyright and license notices.
- Do not change licensing, ownership, attribution, or equity statements without explicit human authorization.
- Do not imply third-party endorsement or affiliation without evidence.

## 9. Git and publishing

- Do not force-push, rewrite shared history, or delete remote branches.
- Do not publish releases or deploy externally without human approval.
- Present meaningful changes for review before committing or syncing.

## 10. Reporting

For each task, report:
- Files inspected.
- Files changed.
- Tests and checks performed.
- Known limitations.
- Any action requiring human approval.

Agents must never claim an action succeeded unless its result was verified.
