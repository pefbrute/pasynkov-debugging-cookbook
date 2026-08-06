# Pasynkov Debugging Cookbook

An open database and training dataset of real-world software failures for developers and AI
assistants. Each case records the reproduction, environment, root cause, failed
approaches, fix, and verification evidence.

This is not a collection of quick tips. Every published case lets another
person or AI agent reproduce the failure, avoid disproven hypotheses, and validate the solution. Cases may
cover any language, platform, or stack as long as they contain concrete,
verifiable technical knowledge.

**Start with the [complete project vision](docs/vision.md).** It explains why
the repository exists, what belongs here, confidence levels, AI model training/retrieval formats, and the protocol
for AI agents.

## Machine-Readable Datasets for AI & Agents

To support AI model training (pre-training / fine-tuning) and real-time agentic retrieval (RAG / MCP), the repository automatically generates machine-readable indexes:

- `cases_index.json` — Compact JSON index of all cases for fast in-context lookup and search tools.
- `dataset.jsonl` — Formatted instruction-tuning dataset for fine-tuning LLMs on real debugging trajectories.

Run `python3 tools/build_dataset.py` to regenerate these dataset artifacts.

## Why this format helps

- `README.md` explains a case to humans;
- `case.yml` provides consistent fields for search, AI agents, and site generators;
- `reproduction/` contains a minimal reproducible example;
- `broken/` and `fixed/` make code comparison straightforward;
- `evidence/` stores sanitized logs, screenshots, and other evidence;
- `verify.sh` checks a fix automatically whenever possible.

## Case catalog

<!-- CASE_CATALOG_START -->
| Stack | Case | Status |
|---|---|---|
| GNOME Shell | [Custom PopupMenu stays open when clicking outside on desktop or workspace](cases/gnome-shell/click-outside-menu-dismissal/) | Verified |
| GNOME Shell | [Extension preferences window fails to open or doesn't raise to front on repeated click](cases/gnome-shell/extension-prefs-dbus-spawn-focus/) | Verified |
| GNOME Shell | [Dock extension fails to hide or stays visible over fullscreen games during Alt+Tab](cases/gnome-shell/fullscreen-dock-autohide/) | Verified |
| GNOME Shell | [Context menu switches to adjacent items on hover due to shared PopupMenuManager](cases/gnome-shell/popup-menu-hover-switch/) | Verified |
| GNOME Shell | [Stolen statusArea indicators distorted or misaligned in custom grid](cases/gnome-shell/stolen-tray-indicator-alignment/) | Verified |
| GNOME Shell | [Hiding top panel with opacity=0 leaves an invisible top dead zone](cases/gnome-shell/top-panel-opacity-invisible-strip/) | Verified |
| GNOME Shell | [Custom popup or window preview is visible but mouse clicks pass through to underlying windows](cases/gnome-shell/topchrome-input-region-click-through/) | Verified |
| GNOME Shell | [Maximized windows extend under custom GNOME Shell panel or dock](cases/gnome-shell/window-struts-reserved-space/) | Verified |
<!-- CASE_CATALOG_END -->

## Adding a case

1. Copy `templates/case/` to `cases/<stack>/<short-name>/`.
2. Complete `case.yml` and the case README without removing required sections.
3. Add a minimal reproduction and verification evidence.
4. Run `python3 tools/build_dataset.py` and `python3 tools/validate_cases.py`.
5. Open a pull request.

See the [vision](docs/vision.md), [contribution guide](CONTRIBUTING.md), and
[repository principles](docs/principles.md).

## For AI agents

Before fixing a similar issue, search `cases_index.json` or `case.yml` files by `stack`, `versions`,
`symptoms`, `root_cause`, and `failed_approaches`. Never transfer a solution to
a different version or environment without validating it again. A `draft` is a
hypothesis or incomplete investigation, not a ready-to-use recommendation. See
the [full AI protocol](docs/vision.md#how-ai-agents-should-use-the-database).

## License

This project uses a dual licensing model:
- **Documentation & Cases (Prose)**: Licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).
- **Source Code, Reproductions & Tooling**: Licensed under the [MIT License](LICENSE).

See [LICENSE](LICENSE) for full licensing terms.

