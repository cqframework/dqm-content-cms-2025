# AGENTS.md

For CQL, FHIR, and eCQM debugging tasks (executing CQL libraries, inspecting ELM, stepping through
defines, comparing persisted test runs), use the cql-debug MCP tools.

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
  status. Maintained **by hand**; nothing generates it and no script reads it, so edit it freely.
- `defect-tracking/CONNECTATHON-BREADCRUMBS.md` — issues with a confirmed root cause and a
  verified candidate fix that was deliberately left unapplied, because choosing the fix is a
  modelling decision. Start here if you want something concrete to work on.
- `defect-tracking/change-log.md` — what content has already been changed and why. Check it before
  "fixing" something, so you don't undo a deliberate decision. Add an entry for any CQL, FHIR
  resource/fixture, or valueset change you apply.

Issue ids appear in CQL comments next to the affected logic, e.g.
`// [I-28] base FHIR.Condition retrieve (defect-tracking/known-issues.md)`.

Deeper per-issue analysis (reproduction steps, engine/translator root causes, ELM traces) lives in
a separate internal tooling repo, keyed by the same `I-XX` ids.
