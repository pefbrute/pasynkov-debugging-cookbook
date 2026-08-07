<!--
ARTICLE WRITING PROTOCOL
Before filling any section:
1. Fill evidence.yml for this case first
2. Run: python3 tools/fetch_api_docs.py <function_name> for any API you claim
3. Every number in a log block must appear in evidence.yml log_tokens
4. Every type claim must cite a source URL inline
5. Run: python3 tools/lint_article.py <this_file> before committing
-->

# [Title: write LAST, after proof is complete]

> **Tested Environment**:
> - **OS**: 
> - **Runtime**: 
> - **Session**: 

[One paragraph: what symptom you observed. ONLY what you observed — no explanation yet.]

---

## 1. Diagnostics: What the live pass shows

<!-- LOG INSTRUMENTATION: log from INSIDE vfunc override, not from external call -->

```javascript
// Instrumentation code
```

Live pass output:

```text
<!-- Every token here must be in evidence.yml log_tokens -->
<!-- Replace unexplained values with <observed anomalous value> -->
```

---

## 2. Analysis: Mechanism

<!--
For each claim below:
- If CONFIRMED by docs: add <!-- SOURCE: <url> --> after the paragraph
- If OBSERVED in this specific hierarchy: add <!-- OBSERVED: live-pass log -->
- If hypothesis: wrap in > blockquote and label HYPOTHESIS
-->

### Illustrative code example

<!--
If the code is NOT a literal reproduction of production code,
MUST add the ILLUSTRATIVE EXAMPLE comment inside the block.
-->

```javascript
// ILLUSTRATIVE EXAMPLE — demonstrates mechanism, not exact log values
```

### Anomalous value origin

<!--
If you cannot explain the exact origin from source: say so explicitly.
Do NOT speculate about types (guint, uint32) without checking the C declaration.
Use fetch_api_docs.py first.
-->

> **UNKNOWN**: The exact mechanism by which [X] becomes [Y] was not confirmed from source. <!-- SOURCE: or null -->

---

## 3. API Contract

<!--
For every API contract claim:
- Paste the exact quote from docs
- Add the source URL
Do NOT paraphrase: quote literally.
-->

> "[exact quote from docs]" <!-- SOURCE: <url> -->

---

## 4. Solutions

### Solution 1: Defensive Fix (Recommended)

<!--
Code must be safe: no get_parent().get_width() unless parent is confirmed allocated.
Every fallback must reference evidence.yml causal_claims confidence level.
-->

```javascript
// defensive fix
```

#### Log trace (Defensive Fix):

```text
<!-- Live-pass log, not illustrative -->
```

### Solution 2: Workaround

<!--
If the workaround was observed only in a specific hierarchy:
add: "In this specific actor hierarchy, ..."
Do NOT claim the workaround always works.
-->

```diff
```

#### Log trace (Workaround — this specific hierarchy):

```text
```

---

## 5. Failed Approaches

<!--
MUST include failed approaches — they prevent repeating mistakes.
One approach per section.
-->

### ❌ [Name]

```
```

**Why it failed**: [one sentence, OBSERVED behavior only]

---

## Conclusion

<!--
Write LAST. One paragraph.
Must match the title exactly.
No new claims — only summarize what was shown above.
-->
