# Public Distribution & Search Optimization Guide

This guide defines how cases investigated in the **Pasynkov Debugging Cookbook** should be published and syndicated across public platforms to maximize search engine indexability (Google, DuckDuckGo) and retrieval for AI agents (RAG, LLM pre-training corpora).

---

## 1. Core Principle: Search Fingerprints over Generic Titles

Knowledge is only useful if it can be retrieved when the failure reoccurs months or years later. A title such as *"Fix quick settings panel bug"* is impossible to find via search.

Every case title, headline, and article summary **must** include **Search Fingerprints**:
- **Exact Numeric Constants**: e.g., `4294967296`, `uint32(-1)`, exit code `137`.
- **Exact Error Messages & Log Tokens**: e.g., `Object DockAppIcon already disposed`, `status=4294967040`.
- **API & Type Names**: e.g., `St.BoxLayout`, `St.ScrollView`, `get_preferred_height`, `Clutter.Actor`.
- **Observable Mechanical Symptoms**: e.g., `collapses St.ScrollView to 1px`, `empty AppFavorites on startup`.

### Good vs. Bad Titles

| Bad Title | Search-Optimized Title (With Fingerprints) |
|---|---|
| Panel scroll view invisible bug | GNOME Shell St.BoxLayout returns invalid natural height 4294967296 and collapses St.ScrollView to 1px |
| Menu closes randomly | Context menu switches to adjacent items on hover due to shared PopupMenuManager |
| Extension preferences error | Extension preferences window fails to open or raises GDBus.Error.ServiceUnknown |

---

## 2. Multi-Platform Syndication Matrix

To ensure maximum reach without duplicate content penalties or fragmentation, follow this syndication matrix:

```
                  ┌───────────────────────────────────────────────┐
                  │    Canonical Home: Personal Site + GitHub     │
                  │ fedor-pasynkov.ru/blog/<case-slug>            │
                  │ github.com/.../cases/<stack>/<symptom-slug>/  │
                  └───────────────────────┬───────────────────────┘
                                          │
    ┌───────────────────┬─────────────────┼─────────────────┬───────────────────┐
    ▼                   ▼                 ▼                 ▼                   ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌───────────────────┐
│     Habr     │ │ DEV Community│ │Stack Overflow│ │GNOME Discourse│ │   Reddit / Social │
│  (RU Story)  │ │ (EN Article) │ │  (Q&A Pair)  │ │ (API Report) │ │ (Short Announcement)│
│  Narrative   │ │canonical_url │ │ Self-Answer  │ │ Minimal Repro│ │  With Log Snippet │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ └───────────────────┘
```

### Platform-Specific Protocols

#### 1. Canonical Origin (Personal Website & GitHub)
- **Role**: Authoritative single source of truth containing raw logs, `case.yml` metadata, minimal reproductions in `reproduction/`, broken/fixed code diffs, and verification scripts.
- **URL Structure**: `https://fedor-pasynkov.ru/blog/<case-slug>` and GitHub repo `cases/<stack>/<symptom-slug>/`.

#### 2. Habr (Russian Language Narrative)
- **Format**: Detailed engineering narrative.
- **Structure**:
  1. *Symptom*: What was observed (e.g. 1px height, missing icons).
  2. *False Hypotheses*: Failed approaches and why they broke adjacent functionality.
  3. *Diagnostic Path*: Traversing the Clutter actor tree and logging `get_preferred_height()`.
  4. *Root Cause Analysis*: Explaining `uint32(-1)` sentinel overflow in container allocation.
  5. *Fix & Regression Protection*: Minimal code change and verification procedure.

#### 3. DEV.to / Medium / Hashnode (English Articles)
- **Format**: Full technical breakdown in English.
- **Requirement**: Always set the `canonical_url` header to point directly to the personal site canonical post (`canonical_url: https://fedor-pasynkov.ru/blog/...`).

#### 4. Stack Overflow / Stack Overflow на русском (Targeted Q&A)
- **Format**: Concise Question with Self-Answer (encouraged by SO for documenting solutions).
- **Question**: State the exact error message, versions, minimal actor layout, and log output.
- **Answer**: Provide the root cause explanation, minimal code fix, and a reference link to the full canonical investigation.

#### 5. Upstream Community (GNOME Discourse / GitLab)
- **GNOME Discourse**: Post technical inquiries for GNOME/GJS developers to discuss underlying Clutter/St layout contracts.
- **GNOME GitLab**: Open an upstream issue only when a minimal reproduction reproduces on currently supported GNOME releases (last 2 stable releases or main).

#### 6. Social & Community Aggregators (Reddit `r/gnome`, Linux forums)
- **Format**: Short text post summarizing the problem and root cause with key diagnostic snippets. Avoid raw link spamming; provide self-contained value in the post body.

---

## 3. Case Structure Checklist for Public Publishing

When preparing a case for publication:

1. [ ] **Title**: Contains exact API symbols, error strings, and numeric constants.
2. [ ] **Symptoms**: Lists raw terminal logs or measurable geometry values.
3. [ ] **Minimal Reproduction**: Contains a standalone runnable project isolated from production code.
4. [ ] **Root Cause**: Pinpoints the exact mechanism (e.g., unsigned integer wrap, race condition).
5. [ ] **Failed Approaches**: Explains why obvious workarounds failed or caused side effects.
6. [ ] **Verification**: Provides automated commands (`verify.sh`) or reproducible manual steps.
7. [ ] **Canonical Link**: Cross-posted versions point to the primary source.
