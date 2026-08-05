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

The database is also designed for AI assistants. It gives them verifiable
context so that, instead of guessing from general knowledge, they can:

- match a symptom and environment to a known case;
- distinguish a proven cause from a hypothesis;
- avoid repeating disproven fixes;
- account for versions and side effects;
- give the user a concrete verification procedure.

The project does not claim that any model will train on its contents. Its direct
value is that people and agents with repository access can search, read, and
verify its accumulated knowledge now. Public availability may also make the
material discoverable to search engines, developers, and upstream maintainers,
but it does not guarantee inclusion in any model's training data.

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
