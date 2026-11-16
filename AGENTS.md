# AGENTS.md

For CQL, FHIR, and eCQM debugging tasks (executing CQL libraries, inspecting ELM, stepping through
defines, comparing persisted test runs), use the cql-mcp server tools. Pass
`configPath` = `input/tests/config.json` to `cql_test_run_suite` so the Measurement Period
parameter is applied.

## Test-case reporting

`scripts/readme.md` documents the whole flow: extract expected results from the fixture
MeasureReports, extract actual results from the CQL engine output, compare the two. Three scripts,
no build step, no code generation.

```sh
python3 scripts/extract_population_expected.py
python3 scripts/extract_population_actual.py
python3 scripts/compare_results.py
python3 -m pytest
```

## Known issues

- `defect-tracking/known-issues.md` — every issue found so far, with its root-cause class and
  status. The **Open issues** table, `scripts/comparison/known_issues.csv`, and
  `scripts/comparison/implementation_issues.csv` are generated from the project's issue catalog;
  don't edit them by hand. The rest of `known-issues.md` is hand-maintained.
- `defect-tracking/change-log.md` — what content has already been changed and why. Check it before
  "fixing" something, so you don't undo a deliberate decision. Add an entry for any CQL, FHIR
  resource/fixture, or valueset change you apply.

Issue ids appear in CQL comments next to the affected logic. Use the full block —
issue id, one-line summary, upstream ticket, affected test cases — e.g.

```cql
// [I-28] base FHIR.Condition retrieve (defect-tracking/known-issues.md)
// Upstream ticket: https://github.com/cqframework/clinical_quality_language/issues/1872
// Affected test cases: all 45 CMS117 cases (library-wide translate failure)
```

`Upstream ticket:` is required; use `(pending)` when no ticket is filed yet. When code
was replaced, keep the original commented out immediately above the replacement under
an `// original` line, with every line of that block starting `//` in the same column.

Deeper per-issue analysis (reproduction steps, engine/translator root causes, ELM traces) lives in
a separate internal tooling repo, keyed by the same `I-XX` ids.
