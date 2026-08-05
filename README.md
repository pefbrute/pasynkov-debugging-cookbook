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
| GNOME Shell | [Popup menu switches on hover](cases/gnome-shell/popup-menu-hover-switch/) | Verified |
| GNOME Shell | [Fullscreen dock autohide on Alt+Tab](cases/gnome-shell/fullscreen-dock-autohide/) | Verified |
| GNOME Shell | [Maximized window struts reserved space](cases/gnome-shell/window-struts-reserved-space/) | Verified |
| GNOME Shell | [TopChrome input region click-through](cases/gnome-shell/topchrome-input-region-click-through/) | Verified |
| GNOME Shell | [Top panel opacity=0 invisible strip](cases/gnome-shell/top-panel-opacity-invisible-strip/) | Verified |
| GNOME Shell | [Stolen statusArea indicator alignment](cases/gnome-shell/stolen-tray-indicator-alignment/) | Verified |
| GNOME Shell | [Click-outside PopupMenu dismissal](cases/gnome-shell/click-outside-menu-dismissal/) | Verified |
| GNOME Shell | [Extension prefs DBus spawn & window focus](cases/gnome-shell/extension-prefs-dbus-spawn-focus/) | Verified |

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
