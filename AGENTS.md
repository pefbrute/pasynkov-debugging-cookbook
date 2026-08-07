# Instructions for coding agents

Read `docs/vision.md` completely before adding, changing, or applying a case.
It defines the repository's purpose, admissible content, confidence levels, and
the protocol for AI agents. Then read the specific case's `README.md` and
`case.yml` before acting.

- Treat every case as evidence, not universal advice.
- Never mark a case `verified` without reproducible verification evidence.
- Preserve failed approaches: they are a core part of this repository and critical for training AI models to avoid plausible but broken fixes.
- Record exact versions, display server, OS, runtime, and relevant dependencies.
- Prefer minimal reproductions over excerpts from private production projects.
- Remove secrets, personal data, tokens, and proprietary code before committing.
- Run `python3 tools/build_dataset.py` and `python3 tools/validate_cases.py` after creating or changing any case metadata.
- Ensure machine-readable indexes (`cases_index.json` and `dataset.jsonl`) are synchronized before finalizing changes.
- A fix must state what may regress and how those regressions were checked.
- Never infer missing evidence or promote a confidence status from prose alone.
- Compare the current environment with the case metadata before reusing a fix.
- Follow the 8-step Technical Investigation Protocol in `docs/public-distribution-guide.md` (Section 5): separate `OBSERVED`, `REPRODUCED`, `INFERRED`, `HYPOTHESIS`, and `UNKNOWN`. Never promote a hypothesis to a proven `Root Cause` without C trace/source evidence.
- Write articles and case reports in the 6 ➔ 1 Bottom-Up order: (6) Log inside live execution pass -> (5) Use precise engineering terms -> (4) Remove decorative unlinked numbers -> (3) Show single before/after causal chain -> (2) Require logs before stating "why" -> (1) Frame title and scope last under proven evidence.
- [Rule 7] Before asserting any internal type, marshaling behavior, or API contract, look up the official declaration first. A plausible-sounding type claim that survives multiple review rounds can still be wrong (e.g. guint vs gfloat*).
- [Rule 8] Match causality claims to actual confidence level. Use "in this specific hierarchy, X preceded Y" (observation) rather than "X causes Y" (general rule) unless the general rule is proven. Self-check marker: if "may vary depending on..." fits without breaking the argument, use it instead of "always" or "causes".
- [Rule 9] Read API boundary conditions literally, not intuitively. `for_width < 0` is not the same as `for_width <= 0`. For any numeric condition in a fix, verify the exact contract wording before writing the guard.
- [Rule 10] Do not read derived state from an object whose state may not yet be set. Calling `get_width()` on an unallocated parent inside a preferred-size pass creates a hidden circular dependency. Use intrinsic/own component data instead.
- [Rule 11] Every token in a log or output block must be either explained or removed. No "minor detail" exceptions — if you cannot answer "where does this number come from and what does it prove", cut it.
- [Rule 12] When a code example uses a framework or stdlib class, verify the usage requirements (not just the method API). A child of St.ScrollView must implement StScrollable — this does not surface from syntax review alone.
- Unified principle: every number, type, and causal claim in the text must have a source — either a live-pass log from your own experiment, or official documentation. If no source exists, the claim either does not appear in the text or carries an explicit disclaimer.


