# Pasynkov Debugging Cookbook: project vision

## What this project is

Pasynkov Debugging Cookbook is an open, structured database of investigated
failures from real-world software development. It preserves not only the final
fix but the useful diagnostic path: observable symptoms, environment, a minimal
reproduction, root cause, failed approaches, the effective change, and evidence
that the change worked.

The project covers different languages, platforms, and technology stacks,
including GNOME Shell, Linux, Android, Flutter, JavaScript, Python, networking,
databases, and infrastructure. Quality of investigation—not technology—defines
the repository's scope.

## Why it exists

Most debugging knowledge disappears after a task is closed. An issue, chat, or
commit history usually retains only fragments of the context, so developers
repeat the same plausible mistakes months later.

Conventional documentation explains how a system should work. Pasynkov
Debugging Cookbook records how it fails under specific conditions, why obvious
fixes may fail, and how to verify a real solution.

The database is designed for both human engineers and AI assistants. It serves as an open training dataset for AI model pre-training/fine-tuning and an in-context knowledge base for AI agents (RAG/MCP), so that instead of guessing from general knowledge, AI systems can:

- match a symptom and environment to a known case;
- distinguish a proven cause from a hypothesis;
- avoid repeating disproven fixes (failed approaches);
- account for exact versions and side effects;
- give the user a concrete verification procedure;
- learn from real-world debugging trajectories during training.

The project is structured to make all cases open, machine-readable (`cases_index.json`, `dataset.jsonl`), and legally accessible for inclusion in public AI training corpora, search engine indexes, and agentic retrieval pipelines.


## Who it is for

- developers facing similar unusual behavior;
- case authors who do not want to lose a discovered root cause;
- teams building an internal or public engineering playbook;
- AI agents that need reliable context before modifying code;
- library and platform maintainers who benefit from minimal reproductions.

## What belongs here

A suitable contribution is a concrete technical case containing useful
knowledge that is not obvious from an error message or standard documentation:

- a reproducible application, library, operating-system, or tool failure;
- an unexpected interaction between components;
- behavior that differs between versions or environments;
- a configuration failure with a nontrivial root cause;
- a performance, compatibility, build, or deployment problem;
- a plausible fix that caused a regression;
- an investigation that produced a proven negative result;
- a temporary workaround with clearly stated limits and risks.

A case may be added before a solution exists. It should then remain `draft` or
`reproduced`, with every unknown stated honestly. An incomplete but accurate
observation is more useful than confident fiction.

## What does not belong here

- a general tutorial for a language or framework;
- a question without reproduction steps or new technical knowledge;
- unverified advice presented as a final solution;
- a large production project in place of a minimal example;
- a duplicate case with no new environment, evidence, or result;
- code that the contributor is not allowed to publish;
- passwords, tokens, personal data, private logs, or keys;
- a vulnerability whose publication creates unreasonable risk before
  responsible disclosure to the system owner.

## How a case differs from an article or Stack Overflow answer

A case is not a free-form note or merely an answer to a question. It uses a
common structure, machine-readable metadata, an explicit confidence level, and
dedicated locations for artifacts. Failed solutions are part of the result, and
the environment version is part of the applicability conditions. Cases can
therefore be compared, validated, indexed, and eventually rendered on a site.

## What makes a good case

A minimally useful case answers these questions:

1. What is observed, and what was expected instead?
2. In which environment and versions does it occur?
3. Which exact actions reproduce it reliably?
4. What is the root cause, and what evidence supports that conclusion?
5. What was tried, why did it fail, and what else did it break?
6. What is the smallest effective fix?
7. How can the fix and likely regressions be checked?
8. For which versions or conditions are the conclusions still untested?

Recommended artifacts include:

- a minimal reproducible project in `reproduction/`;
- the original failing state in `broken/`;
- the minimal corrected state in `fixed/`;
- an automated `verify.sh` check;
- sanitized logs, traces, screenshots, or videos in `evidence/`;
- primary-source links such as documentation, source code, issues, and commits.

## Confidence levels

`draft` means that the case has been recorded, but its reproduction, cause, or
fix is not yet proven.

`reproduced` means that the failure occurs reliably in a recorded environment
using exact steps. The cause or fix may still be unknown.

`verified` means that the cause is supported by evidence, the fix is
reproducible, the stated regression risks were checked, and the date of the last
verification is recorded.

`obsolete` means that the case no longer applies to supported versions but is
retained as historical or diagnostic knowledge.

A status applies only to the recorded environment. `verified` for one version
does not imply that a case applies to another.

## Case lifecycle

1. Record the symptom, expected behavior, and original environment.
2. Remove secrets and create a minimal reproduction.
3. Separate facts, hypotheses, and unknowns.
4. Record tested failed approaches and their consequences.
5. Identify the root cause and connect the conclusion to evidence.
6. Add the minimal fix and regression checks.
7. Run the validator and promote the status only when its criteria are met.
8. Recheck new versions or narrow the stated scope.

## Upstream Contribution Protocol

A case repository records the full diagnostic path, minimal reproduction, and failed approaches. However, once a root cause is proven, relevant knowledge should be contributed back to official upstream projects and documentation:

1. **Undocumented expected behavior**: Submit a documentation Issue or Merge/Pull Request to official guides (e.g. GJS Guide, framework docs) offering a clear explanation and safe usage pattern.
2. **Platform or library defects**: Open a clear bug report on the upstream tracker (e.g. `GNOME/gnome-shell`, `GNOME/mutter`, Python issue tracker) referencing the minimal reproduction.
3. **Internal API workarounds**: Document the solution under Best Practices / Debugging / Caveats rather than presenting it as stable API contract.

Track the progress of upstream submissions in `case.yml`:
- `not-submitted`: Investigation completed locally, not yet submitted upstream.
- `issue-opened`: Upstream bug or documentation issue created.
- `needs-confirmation`: Waiting for upstream maintainer feedback or reproduction confirmation.
- `mr-opened`: Merge / Pull Request submitted to official docs or code.
- `accepted`: Fix or documentation merged into upstream.
- `rejected`: Upstream declined (record rationale in case prose).

## Public Distribution & Search Optimization

To make case investigations easily discoverable by developers using search engines and AI agents performing retrieval:

- **Search Fingerprints**: Case titles and symptoms must include exact error strings, numeric constants (e.g. `4294967296`), API symbols (`St.BoxLayout`), and measurable geometry anomalies (`collapses St.ScrollView to 1px`).
- **Multi-Platform Syndication**: Follow the [Public Distribution Guide](public-distribution-guide.md) to cross-post investigations to platforms like Habr, DEV Community (using `canonical_url`), Stack Overflow, GNOME Discourse, and Reddit while maintaining canonical links back to the repository and personal website.

## How AI agents should use the database


Before proposing a change, an agent should search by technology, version,
symptom, and mechanism—not only by a similar title. A matching case is a source
of hypotheses and verification ideas, not automatic permission to copy a fix.

An agent must:

- compare the current environment with `case.yml` first;
- report differences in versions or critical conditions;
- treat a `draft` as a hypothesis rather than an instruction;
- preserve the distinction between observation, author conclusion, and external
  source;
- validate the fix in the current project;
- add or update a case only from evidence;
- never promote a status or fill unknown fields by guessing;
- record a newly discovered side effect instead of hiding it.

If no suitable case exists, an agent may create a `draft` containing confirmed
facts and open questions for the next step. The purpose is to reduce repeated
mistakes, not to create the appearance that an answer is already known.

## How to tell whether the project is succeeding

The primary test is whether another person or agent can take a case, reproduce
the original failure, apply the described fix, and obtain the stated result
without contacting the author. Additional signs of success are:

- failed approaches stop recurring in similar tasks;
- old solutions gain updated applicability boundaries promptly;
- cases link to upstream issues or help improve upstream projects;
- the number of `verified` cases grows without weaker evidence standards;
- metadata search returns genuinely relevant cases.

## Long-term direction

The format is designed to support a catalog or website with filters for stacks,
symptoms, versions, and status; full-text search for people and retrieval for AI
agents; automated reproductions in containers; links between related cases; and
reports identifying stale verifications.

These features are secondary. The foundation of the project is a collection of
small, honest, and verifiable investigations.
