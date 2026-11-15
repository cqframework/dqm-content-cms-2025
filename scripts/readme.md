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
- Outputs `./scripts/comparison/output_results.csv` with PASS/FAIL/IMPLEMENTATION for each population cell (a missing actual value shows as `MISSING` in the `actual_result` column), and `./scripts/comparison/discrepancy_report.md` grouping the differences per measure.
- Prints the number and percentage of passing, implementation-issue and failing test cases to the terminal.

#### Implementation issues (optional)

Some test cases can't match their fixture MeasureReport because the measure steward's test data or expectation misuses FHIR or CQL semantics, not because of the CQL or the engine. These are class `implementation` in `defect-tracking/known-issues.md`; I-67 is an example (a start-only `abatementPeriod` used to mean a resolution date). An issue that explains the failure is as good as a match, so these cases count as resolved. They are listed in:

- `scripts/comparison/implementation_issues.csv`, with columns `issue_id,measure_name,guid,group,note`. Leave `group` blank to cover every group of the test case. Quote any `note` that contains a comma. The script stops with an error on a missing required column or an unquoted comma.
- **If the file is absent or empty, nothing changes.**

How a listed case is scored:

| Where | Effect |
|---|---|
| `output_results.csv` | A mismatching cell in a covered group has `result` `IMPLEMENTATION` instead of `FAIL`. Matching cells stay `PASS` |
| Test-case verdict | `IMPLEMENTATION` when every mismatching cell is covered. One mismatch in a group the issue doesn't cover keeps the case `FAIL` |
| Header `Details` table | `Implementation Issue Count` sits between `Pass Count` and `Fail Count`, and `Resolved (Pass + Implementation)` gives the combined rate. The three counts add up to `Total Test Cases`. Neither row appears when no case is resolved this way |
| Per-measure tables | Covered groups stay listed under "Measures with Discrepancies", with `I-XX (implementation)` in the `Issue` column and the note in the measure's `Issues` list. They don't count toward `Unattributed` |

A listed case that passes needs no explanation and is scored `PASS` as usual.

#### Known issues with a ticket (optional)

Other failing test cases are explained by an issue in `defect-tracking/known-issues.md`. Only an `engine` or `translator` issue can carry a GitHub ticket — those are the two classes whose root cause lives in the upstream `clinical_quality_language`/`clinical-reasoning` projects. Such a case counts as resolved only once its issue has a ticket. A defect in our own content, fixture, or harness can never be ticketed upstream, so it never resolves this way. They are listed in:

- `scripts/comparison/known_issues.csv`, with columns `issue_id,class,status,ticket,measure_name,guid,group,note`.
- `class` is one of the classes in `known-issues.md`, except `implementation`, which belongs in `implementation_issues.csv`.
- `status` is the issue's `defect_status` from the catalog: `suspected`, `confirmed` or `workaround-applied`. It decides how a case is scored when it *matches* its fixture; see "Workarounds" below.
- `ticket` is the GitHub issue or pull request URL, e.g. `https://github.com/cqframework/clinical_quality_language/issues/1855`. Leave it blank until one is filed. Any other value, such as `TBD`, stops the script with an error.
- Every row of one issue must carry the same `class`, `status` and `ticket`.
- `group` and quoting work as in `implementation_issues.csv`. **If the file is absent or empty, nothing changes.**

#### Open tickets (optional)

`scripts/comparison/open_tickets.csv`, with columns `ticket,summary,issues`, lists every upstream ticket an open known issue cites: the GitHub or HL7 JIRA URL, a one-line summary, and the citing issue ids separated by spaces. The report lists them in an `Open Tickets` section after the `Measures with Discrepancies` table, whether or not the tickets' cases fail today. It doesn't affect scoring. **If the file is absent or empty, the section is left out.**

These files, and the Open issues table in `defect-tracking/known-issues.md`, are generated from the project's issue catalog, so a hand edit is overwritten on the next update.

How a listed case is scored:

| Ticket | `output_results.csv` | Test-case verdict | Report |
|---|---|---|---|
| Recorded | Mismatching covered cells are `KNOWN_ISSUE` | `KNOWN_ISSUE`, counted as resolved | `Known Issue Count (ticketed)` row; a bare `I-XX` in the per-measure `Issue` column; the ticket number links from the `Ticketed` column |
| Blank, `engine`/`translator` | Cells stay `FAIL` | `FAIL` | `— known issue, needs ticket` row under `Fail Count`; a bare `I-XX` in the `Issue` column and `pending` in `Ticketed`; counted as `Unattributed` |
| Blank, any other class | Cells stay `FAIL` | `FAIL` | `— known issue, no ticket expected` row under `Fail Count`; a bare `I-XX` in the `Issue` column and `N/A` in `Ticketed`; counted as `Unattributed` |

An upstream ticket tracks a defect in `clinical_quality_language` / `clinical-reasoning`, so it is meaningful only for the `engine` and `translator` classes. For any other class the `Ticketed` column reads `N/A` rather than `pending`: no ticket is owed, and `pending` would suggest one is.

Every failing test case, whatever its issue state, is listed under `## Measures with Discrepancies`. Under its tables, each measure has an `Issues` list giving each cited issue's class, ticket, and note (an unticketed known issue's bullet reads e.g. `- **I-65** (\`content\`)`, dropping the `**needs ticket**` belt-and-braces that the per-row `Ticketed` column carries instead). A test case that no implementation issue or ticketed known issue resolves is counted under `Unattributed Discrepancies` in the `Discrepancy Summary` table and in the `Unattributed` column of the per-measure summary; these are the `FAIL` verdicts. A measure is listed under "Measures with No Discrepancies" only when every test case matches its fixture. An implementation issue takes precedence over a known issue on the same cells.

A ticketed known issue and a workaround are not mutually exclusive, and a case can be both: I-78's CMS145 cases are covered by a ticketed issue *and* match only because the measure's CQL works around it. `cell_outcome` can give such a case only one verdict, since it reaches `KNOWN_ISSUE` from a mismatching cell and `WORKAROUND` from a matching one, so neither count on its own reports that coverage. The header `Details` table therefore also carries a cross-cutting `Known issues with an upstream ticket` row, counting the cases that either explained verdict covers. It is deliberately not one of the five that add up to `Total Test Cases`, and `Resolved` still excludes the workaround half of it: the defect behind those cases is open, and reverting the workaround turns them into failures again.

A `Ticketed` column sits to the right of the `Issue` column on every per-measure table (Missing Results, Missing Populations, Mismatched Test Cases, Workarounds). `N/A` means no ticket is owed: the issue is `implementation` (the steward's own data), or a known issue outside `engine`/`translator` (our own content, fixture, or harness). `pending` means an `engine` or `translator` issue that is still waiting on a ticket, and a link to the issue/PR (`[1868](https://github.com/.../issues/1868)`) means it is recorded. The cell is blank when no issue covers the row, matching the `Issue` cell beside it.

#### Workarounds (`status` `workaround-applied`, optional)

Some issues are worked around in the measure's own CQL -- a cast that removes an overload ambiguity, a `System.Quantity` construction, and so on (I-78 and I-24 are examples). The case then *matches* its fixture, but the defect is open and the workaround is meant to be reverted once the root cause is fixed. Scoring it `PASS` would erase the defect from the report, which is the opposite of the report's purpose, so it is scored `WORKAROUND` instead: counted as neither a pass nor a failure, and listed under the measure as its own discrepancy.

| Where | Effect |
|---|---|
| `output_results.csv` | Matching cells under a `workaround-applied` issue have `result` `WORKAROUND` instead of `PASS` |
| Test-case verdict | `WORKAROUND` when the case matches and carries such an issue. The case leaves `Pass Count` |
| Header `Details` table | `Workaround Count` sits between `Pass Count` and `Fail Count`, with a `— covered by a ticketed known issue` sub-row when any of them has one. The five counts add up to `Total Test Cases`; the row is absent when no case is a workaround |
| `Discrepancy Summary` | A `Workarounds` row, and a `Workarounds` column in the per-measure summary |
| Per-measure tables | A `Workarounds` table with the issue, e.g. `I-78 (workaround applied)`, and the issue's note. The measure stays under "Measures with Discrepancies" even when nothing else in it differs |

An issue-carried workaround that is *not* holding the case up -- reverted, or never applied -- leaves the cell failing, and the failure takes the ordinary path above; its `Issue` column then reads `I-XX (workaround reverted)` rather than `ticketed`/`needs ticket`. A row whose `status` is anything else is never a workaround, so an ordinary catalog row whose case happens to pass stays a stale attribution instead of being relabelled.

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
- **Resource IDs.** MADiE evaluates test cases with the JS CQL engine, which treats every resource
  in the bundle as the patient's, so it used to accept test bundles in which several entries
  shared one `resourceType/id`. Splitting such a bundle into `<resourceType>-<id>.json` files keeps only the
  last entry, so the other resources disappear without any error (I-76: CMS819 lost the
  qualifying opioid/antagonist pair this way). On the fixture tree the duplicate is already gone,
  so the script looks for what it leaves behind: a file whose name disagrees with its
  `resourceType`/`id` (`ID-FILENAME-MISMATCH`, `ID-DUPLICATE`), and a fixture MeasureReport whose
  `evaluatedResource` repeats a reference (`EVALUATED-REF-REPEATED`, a warning) or names a
  resource with no file (`EVALUATED-REF-DANGLING`). `--check-references` also reports relative
  references between resources that resolve to no file in the folder, split into
  `REF-UNRESOLVED-CLINICAL` (types measure logic dereferences, e.g. `Location`) and
  `REF-UNRESOLVED-ACTOR` (Practitioner, Organization, Coverage, …). `--bundle` checks a source
  export *before* it is split: duplicate ids, plus the patient-reference, required-field and
  unresolved-reference checks on every entry. It exits 1 if two entries share an id but differ in
  content, or on any finding that isn't a warning. `--restore-from-bundle BUNDLE --case
  MEASURE/GUID` drafts the resources a split lost (new ids, dates shifted to the fixture's years,
  the fixture's profile) plus the rewritten MeasureReport, under `out/restore/`. It never edits
  `input/tests/`; copy approved drafts in by hand.

```sh
python3 scripts/validate_test_fixtures.py                                    # report only
python3 scripts/validate_test_fixtures.py --measure CMS104                   # one measure
python3 scripts/validate_test_fixtures.py --json                             # machine output
python3 scripts/validate_test_fixtures.py --fix --apply                      # rewrite CORE fields
python3 scripts/validate_test_fixtures.py --fix-required-fields --apply      # inject missing for/subject
python3 scripts/validate_test_fixtures.py --check-references                 # + unresolved intra-folder refs
python3 scripts/validate_test_fixtures.py --bundle path/to/madie-export.json # lint a source bundle
python3 scripts/validate_test_fixtures.py --restore-from-bundle path/to/madie-export.json --case CMS819FHIRHHORAE/<guid>  # draft lost resources
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
  - `test_compare_results_report.py` covers the per-case verdict rule, CQFM
    exclusions, the report's table shapes and headings, and argument parsing;
    `test_compare_results_implementation.py` and
    `test_compare_results_known_issues.py` cover the two issue files.
