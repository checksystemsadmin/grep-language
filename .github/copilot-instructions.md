# GitHub Copilot Instructions — GREP

Follow the universal project requirements in the repository-root AGENTS.md.

## Project context

GREP means Global Retrieval, Execution & Processing.
It is an experimental search-native programming language.
The current project version is 0.1.0.

## Engineering rules

- Inspect existing code before proposing modifications.
- Preserve Python 3.9+ compatibility.
- Keep runtime changes focused and maintainable.
- Add or update unit tests for behavioral changes.
- Do not introduce dependencies without justification.
- Do not claim unimplemented features are available.

## Repository structure

- src/grep_lang/: language implementation.
- tests/: automated tests.
- examples/: GREP example programs.
- metadata/: project metadata.
- docs/index.html: existing marketing page; preserve it.
- docs/guide/: GitBook technical documentation.
- agents/: specialized agent specifications.

## Validation

Run the relevant checks:

python -m unittest discover -s tests -v
python -m grep_lang.cli validate
python -m grep_lang.cli doctor
git diff --check

Report actual results.

## Documentation

Keep documentation aligned with implemented behavior.
Update CHANGELOG.md when changes warrant an entry.
Do not invent performance claims, integrations, endorsements, or capabilities.

## Safety and authorization

Never expose secrets or credentials.
Never modify licensing, ownership, or attribution without explicit authorization.
Never force-push or publish releases without human approval.
Preserve existing marketing and documentation assets.

## Completion report

Summarize changed files, implementation details, tests, failures, and remaining work.
