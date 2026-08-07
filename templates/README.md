# Templates

Templates for creating new cases. Use these to enforce accuracy from the first draft.

## Workflow

1. Copy `evidence.yml` into the new case directory
2. Fill ALL claims with source_url before writing any prose
3. Run `python3 tools/fetch_api_docs.py <function>` for every API type claim
4. Copy `case_article.md` and fill sections in order
5. Run `python3 tools/lint_article.py cases/<id>/` before committing
6. Only then write the final article from the template

## Why this order matters

Every iteration in article writing that required correction traced back to
one of these violations:
- Type/marshaling claim made before checking the C declaration (Rule 7)
- Causal claim stronger than the evidence supports (Rule 8)
- API boundary condition read intuitively, not literally (Rule 9)
- Derived state read from an unallocated object (Rule 10)
- Log token present in output block but never explained (Rule 11)
- Framework usage requirements assumed from syntax, not docs (Rule 12)

The template and evidence.yml enforce Rules 7-12 structurally.
