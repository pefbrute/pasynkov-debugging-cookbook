# Pasynkov Debugging Cookbook

An open database of real-world software failures for developers and AI
assistants. Each case records the reproduction, environment, root cause, failed
approaches, fix, and verification evidence.

This is not a collection of quick tips. Every published case should let another
person or AI agent reproduce the failure and validate the solution. Cases may
cover any language, platform, or stack as long as they contain concrete,
verifiable technical knowledge.

**Start with the [complete project vision](docs/vision.md).** It explains why
the repository exists, what belongs here, confidence levels, and the protocol
for AI agents.

## Why this format helps

- `README.md` explains a case to humans;
- `case.yml` provides consistent fields for search and a future website;
- `reproduction/` contains a minimal reproducible example;
- `broken/` and `fixed/` make code comparison straightforward;
- `evidence/` stores sanitized logs, screenshots, and other evidence;
- `verify.sh` checks a fix automatically whenever possible.

## Case catalog

| Stack | Case | Status |
|---|---|---|
| GNOME Shell | [Popup menu switches on hover](cases/gnome-shell/popup-menu-hover-switch/) | Draft; reproduction required |

## Adding a case

1. Copy `templates/case/` to `cases/<stack>/<short-name>/`.
2. Complete `case.yml` and the case README without removing required sections.
3. Add a minimal reproduction and verification evidence.
4. Run `python3 tools/validate_cases.py`.
5. Open a pull request.

See the [vision](docs/vision.md), [contribution guide](CONTRIBUTING.md), and
[repository principles](docs/principles.md).

## For AI agents

Before fixing a similar issue, search `case.yml` files by `stack`, `versions`,
`symptoms`, `root_cause`, and `failed_approaches`. Never transfer a solution to
a different version or environment without validating it again. A `draft` is a
hypothesis or incomplete investigation, not a ready-to-use recommendation. See
the [full AI protocol](docs/vision.md#how-ai-agents-should-use-the-database).

## License

The materials and examples are not licensed yet. Choose appropriate licenses
for prose and code before public release.
