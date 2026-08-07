# Contributing a high-quality case

A case is ready for review when a reader can answer four questions:

1. How can the failure be observed precisely?
2. Why does it happen?
3. Why did the obvious solutions fail?
4. What proves that the fix works without breaking adjacent behavior?

## Confidence levels

- `draft` — the observation is recorded, but the cause or fix is unproven.
- `reproduced` — stable reproduction steps and a minimal example exist.
- `verified` — the fix, applicable versions, and regression checks are recorded.
- `obsolete` — the case no longer applies but remains useful historically.

Do not promote a case after a single successful manual attempt. When automated
verification is impossible, document multiple manual checks and attach
sanitized logs, screenshots, or video.

## Naming & Search Fingerprints

Use `cases/<stack>/<symptom-in-kebab-case>/`. One directory represents one
observable failure. Connect related failures with links instead of mixing them
into one narrative.

Ensure case titles and `symptoms` include exact **Search Fingerprints**:
- Specific error strings and log output (e.g. `status=4294967040`).
- Exact numeric constants and sentinels (e.g. `4294967296`, `uint32(-1)`).
- API symbols, types, and UI elements (e.g. `St.BoxLayout`, `St.ScrollView`, `get_preferred_height`).

For publishing cases across public sites (Habr, DEV.to, Stack Overflow, etc.), refer to the [Public Distribution Guide](docs/public-distribution-guide.md).
