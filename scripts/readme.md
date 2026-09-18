# Test Case Comparison Process

This repository provides a workflow for comparing expected and actual results for measure test cases. The process generates a comparison file at `./scripts/comparison/output_results.csv` that summarizes PASS/FAIL for each population result, plus a human-readable `./scripts/comparison/discrepancy_report.md`.

## Workflow Steps

1. **Run the CQL plugin**  
   Execute the CQL plugin to generate actual test results for each measure. This will create files in the `./input/tests/results` directory.

2. **Run the scripts in order:**
   - **Step 1:** `extract_population_expected.py`  
     Parses expected results from MeasureReport files and Measure resources.  
     _Only rerun when MeasureReport expected results change._
   - **Step 2:** `extract_population_actual.py`  
     Parses actual results from the output of the CQL plugin in `./input/tests/results/`.  
     _Rerun whenever these result files change._
   - **Step 3:** `compare_results.py`  
     Compares expected and actual results, producing `./scripts/comparison/output_results.csv` and `./scripts/comparison/discrepancy_report.md`.  
     _Rerun whenever either expected or actual results change._

_NOTES_

- Execute scripts from the project's root directory
  - `python ./scripts/<SCRIPT NAME>`
- Scripts developed/tested using `python 3.12`
- No dependencies beyond the standard library

## Script Descriptions

### `extract_population_expected.py`

- Reads MeasureReport JSON files and corresponding Measure resources.
- Extracts population codes and criteria expressions as display names.
- Outputs a CSV of expected results to `./scripts/comparison/expected_results.csv`.

### `extract_population_actual.py`

- Reads actual result files from `./input/tests/results`, which the CQL plugin writes in two
  forms: per-measure `TestCaseResult-*.json` files, and `{MeasureName}.txt` engine traces.
- **Prefers the JSON whenever it is present**, falling back to traces only when there is no JSON.
  The JSON is the complete format — one file per test case, with every population plus an
  `errors` array. The traces are for humans and the plugin writes them inconsistently: on
  extension 0.9.8 / engine 5.3.0, only 48 of 73 traces contained population lines; the other 25
  were header-only stubs (tool versions and a list of test-case paths, nothing else).
- Override with `--json-results` / `-jr` or `--text-results` / `-txt`, e.g. for an archived
  capture containing only traces.
- Parses population results for each test case, handling boolean and list values. Test cases
  whose JSON carries a non-empty `errors` array are skipped.
- Prints the format it chose, the row count, and a **warning listing any measure that produced
  zero population rows**. Take that warning seriously: a measure contributing nothing appears
  downstream as "Missing Results", which reads identically to the CQL failing to translate.
  Reading stub traces instead of the JSON once turned a healthy 96.29% run into an apparent
  49.12%, with 35 measures reported missing.
- Outputs a CSV of actual results to `./scripts/comparison/actual_results.csv`.

### `compare_results.py`

- Compares expected and actual results by measure name, guid, and population.
- Outputs `./scripts/comparison/output_results.csv` with PASS/FAIL/MISSING for each population cell, and `./scripts/comparison/discrepancy_report.md` grouping the differences per measure.
- Prints the number and percentage of passing and failing test cases to the terminal.

### `comparison/populations.py`

Support module for the above. It does two things that exist to stop the report inventing differences that are not really there, so it's worth knowing about before you interpret a result:

- **Canonicalises population names.** The expected CSV takes names from the fixture MeasureReport's `code.coding[0].display`, while the engine emits its own spelling. CMS986's "Measure Population Observation" and "Measure Observation" are the same cell under two names; without canonicalisation those rows could never match and every one would read as a failure.
- **Excludes CQFM measure-observation populations from scoring.** CMS1017, CMS871 and CMS986 wire a `measure-observation` to a parameterized CQL function that is meant to be invoked once per member of another population and then aggregated (`cqfm-criteriaReference` + `cqfm-aggregateMethod`). This workflow has no way to perform that computation, so those cells are listed in their own report section instead of being scored — see `defect-tracking/known-issues.md`, I-62. Every other population on those three measures is scored normally.

### `validate_test_fixtures.py`

Sanity-checks the per-measure test case fixtures under `input/tests/measure/` for
internal-reference consistency — the kind of data-authoring bug that produces a silent zero
population instead of an error, and so is easy to misdiagnose as a CQL or engine defect (see
I-07 below).

- **Patient-reference mismatches.** Each test case is scoped to one patient (`context Patient`);
  a resource whose `subject` / `patient` / `beneficiary` / `Task.for` (etc.) points at a
  *different* or non-existent patient is invisible to the measure logic. Auto-discovers every
  such field across a folder's resources and classifies each mismatch.
- **Missing required fields.** Some resource types (`Task.for`, `Encounter.subject`,
  `MedicationAdministration.subject`, `Observation.subject`) need that reference present at all
  for `context Patient` retrieval to work — not just correct. A resource missing it entirely is
  flagged as `MISSING-REQUIRED-FIELD`.
- **This is exactly what was needed to fix CMS816** (I-07, see `defect-tracking/change-log.md`):
  17 of its 28 fixture Encounter resources had no `subject` at all, so the engine silently
  dropped them from every retrieve no matter how correctly their type/status/period were
  authored — 12 cases failed visibly, 5 more carried the same defect without a visible symptom.
  `python3 scripts/validate_test_fixtures.py --measure CMS816FHIRHHHypo --fix-required-fields
  --apply` found and fixed all 19 affected files.

```sh
python3 scripts/validate_test_fixtures.py                                    # report only
python3 scripts/validate_test_fixtures.py --measure CMS104                   # one measure
python3 scripts/validate_test_fixtures.py --json                             # machine output
python3 scripts/validate_test_fixtures.py --fix --apply                      # rewrite CORE fields
python3 scripts/validate_test_fixtures.py --fix-required-fields --apply      # inject missing for/subject
```

No `--apply` run ever commits anything — review with `git diff` first. See the script's own
docstring for the full field taxonomy and the `--fix-profile-ns` migration mode.

## Reproducing Results Without Running CQL

To quickly reproduce the comparison results without running the CQL plugin:

- Extract `./scripts/results-connectathon-2025-09-13.zip` to `./input/tests/results`.
- This will populate the results directory with a captured run, allowing you to run the scripts and regenerate the comparison outputs.

```sh
unzip scripts/results-connectathon-2025-09-13.zip -d input/tests/results
python3 scripts/extract_population_expected.py
python3 scripts/extract_population_actual.py
python3 scripts/compare_results.py
```

## Unit Tests

- Unit tests are provided for the modules with logic worth pinning
  - run them from the root directory: `python3 -m pytest`
  - or individually, e.g. `python3 -m pytest scripts/tests/test_populations.py`
  - or `python3 -m pytest scripts/tests/test_validate_test_fixtures.py`
