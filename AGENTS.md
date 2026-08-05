# Instructions for coding agents

Read `docs/vision.md` completely before adding, changing, or applying a case.
It defines the repository's purpose, admissible content, confidence levels, and
the protocol for AI agents. Then read the specific case's `README.md` and
`case.yml` before acting.

- Treat every case as evidence, not universal advice.
- Never mark a case `verified` without reproducible verification evidence.
- Preserve failed approaches: they are a core part of this repository.
- Record exact versions, display server, OS, runtime, and relevant dependencies.
- Prefer minimal reproductions over excerpts from private production projects.
- Remove secrets, personal data, tokens, and proprietary code before committing.
- Run `python3 tools/validate_cases.py` after changing case metadata.
- A fix must state what may regress and how those regressions were checked.
- Never infer missing evidence or promote a confidence status from prose alone.
- Compare the current environment with the case metadata before reusing a fix.
