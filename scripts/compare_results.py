"""Compare expected measure results against actual CQL engine results.

Reads two CSVs of ``measure_name,guid,population,count`` rows and writes:

  * ``output_results.csv`` -- one PASS/FAIL/MISSING row per population cell
  * ``discrepancy_report.md`` -- per-measure Missing Results, Missing
    Populations, and Mismatched Test Cases

Run it with no arguments from the repository root; see ``scripts/readme.md``.

Two behaviours are worth knowing about, because both exist to stop the report
inventing discrepancies that are not there:

  * **Population names are canonicalised** (``scripts/comparison/populations.py``)
    before comparison. The expected CSV takes population names from the fixture
    MeasureReport's ``code.coding[0].display`` while the engine emits its own
    spelling, so CMS986's "Measure Population Observation" and "Measure
    Observation" are the same cell under different names. Without
    canonicalisation those rows could never match and every one read as a
    failure.
  * **CQFM measure-observation populations are excluded from scoring.** Three
    ratio measures (CMS1017, CMS871, CMS986) wire a `measure-observation` to a
    parameterized CQL function invoked once per member and then aggregated.
    This harness cannot perform that computation, so those cells are reported
    separately instead of scored. See `defect-tracking/known-issues.md`, I-62.
"""
import csv
import glob
import os
import re
import sys
from collections import namedtuple
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, FrozenSet, List, NamedTuple, Set, Tuple, TypedDict

_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_SCRIPTS_DIR, "comparison"))
from populations import (
    CANONICAL_POPULATIONS,
    DEFAULT_MEASURE_RESOURCE_DIR,
    canonical_cell,
    is_scored,
    load_cqfm_aggregation_exclusions,
    split_population,
)


measure_id_pattern = r"(?:CMS|CMSFHIR)(?P<measure_id>\d+)"

MeasureDifference = namedtuple('MeasureDifference', ['measure', 'total_test_cases', 'test_cases_with_differences', 'result_deltas'])
ResultKey = namedtuple('ResultKey', ['measure_name', 'patient_guid', 'group'])
ResultDelta = namedtuple('ResultDelta', ['patient_guid', 'group', 'population', 'expected', 'actual'])
Comparison = namedtuple('Comparison', ['expected', 'actual'])
TestCaseGroupId = namedtuple('TestCaseId', ['patient_guid', 'group'])

# Canonical scored populations live in scripts/comparison/populations.py, which
# also holds the alias table reconciling the different spellings the expected and
# actual extractors emit. Kept as a module-level name for backwards compatibility
# with callers/tests that referenced it; membership tests should go through
# populations.is_scored(), which applies aliases first.
ValidMeasurePopulationTypes = sorted(CANONICAL_POPULATIONS)

class MissingPopulation(NamedTuple):
    result_key: ResultKey
    population: List[str]

class Discrepancies(NamedTuple):
    missing_results: List[ResultKey]
    missing_populations: List[MissingPopulation]
    population_differences: Dict[str, List[str]]
    measures_with_discrepancies: Set[str]

@dataclass
class MeasureDiscrepancy:
    all_test_cases: List[str] = field(default_factory=list)
    missing_results: List[ResultKey] = field(default_factory=list)
    missing_populations: List[MissingPopulation] = field(default_factory=list)
    mismatched_test_cases: Dict[TestCaseGroupId, Dict[str, Comparison]] = field(default_factory=dict)

class UnscoredCell(NamedTuple):
    measure_name: str
    patient_guid: str
    population: str
    reason: str = "unrecognized-population"
    value: str = ""


class Results(NamedTuple):
    rows: Dict[str, str]
    groups: Dict[ResultKey, Dict[str, str]]
    unscored: List[UnscoredCell] = []


def capture_results(file: str, cqfm_exclusions: Dict[str, FrozenSet[str]] = None) -> Results:
    """Read a results CSV into row- and group-keyed dicts.

    Population names are canonicalised on the way in (see
    ``scripts/comparison/populations.py``) so that keys from the expected and
    actual extractors line up even where they spell the same population
    differently -- e.g. CMS986's "Measure Population Observation" in expected
    vs "Measure Observation" in both engines' actuals. Canonicalising here, at
    the single read point, keeps every downstream key consistent.

    Cells whose population is not a scored population are collected in
    ``unscored`` instead of being silently dropped, so the report can say what
    it did not measure.

    ``cqfm_exclusions`` (``populations.load_cqfm_aggregation_exclusions()``)
    are cells that require per-member CQFM aggregation this harness cannot
    perform (see defect-tracking/known-issues.md, I-62) -- these are also routed to
    ``unscored`` (with ``reason="cqfm-aggregation-excluded"``) rather than
    ``rows``/``results``. Passing the *same* exclusion set into every
    ``capture_results`` call for a run (expected, actual, qicore-actual) is
    what keeps the exclusion symmetric: since the cell never enters
    ``rows``/``results`` on any side, ``capture_discrepancies_by_measure``
    never sees it as missing and the scoring functions never see it as FAIL.
    """
    cqfm_exclusions = cqfm_exclusions or {}
    rows = {}
    results = {}
    unscored: List[UnscoredCell] = []
    with open(file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['measure_name'].lower().startswith("test"):
                continue

            group, population = split_population(row["population"])
            cell = f"{group}:{population}"

            if cell in cqfm_exclusions.get(row["measure_name"], ()):
                unscored.append(UnscoredCell(
                    row["measure_name"], row["guid"], row["population"],
                    reason="cqfm-aggregation-excluded", value=row["count"]))
                continue

            key = (row["measure_name"], row["guid"], cell)
            rows[key] = row["count"]

            if population not in CANONICAL_POPULATIONS:
                unscored.append(UnscoredCell(
                    row["measure_name"], row["guid"], row["population"],
                    reason="unrecognized-population", value=row["count"]))
                continue

            result_key = ResultKey(row["measure_name"], row["guid"], group)
            result = results.setdefault(result_key, {})
            result[population] = row["count"]
    return Results(rows, results, unscored)


# ---------------------------------------------------------------------------
# Cross-engine diffs: this project's engine output vs the QI-Core engine output.
# The QI-Core project's `actual_results.csv` is copied in as the source of truth
# for QI-Core measures; comparing it against this project's own `actual_results`
# surfaces every population where the two engines disagree.
# ---------------------------------------------------------------------------

def render_cqfm_exclusions_section(
        cqfm_exclusions: Dict[str, FrozenSet[str]],
        unscored_cells: List[UnscoredCell]) -> List[str]:
    """`## Populations Excluded from Automated Scoring (CQFM Aggregation)`.

    Shown whenever any measure has CQFM-aggregation populations. Without this,
    those cells would either read as a misleading FAIL or be silently scored as
    0 -- both of which invent a discrepancy that does not exist.
    """
    if not cqfm_exclusions:
        return []
    out = ["## Populations Excluded from Automated Scoring (CQFM Aggregation)\n", "\n"]
    out.append(
        "_These populations require invoking a parameterized CQL "
        "`measure-observation` function once per member of a "
        "`cqfm-criteriaReference` population and then applying "
        "`cqfm-aggregateMethod` (Sum/Count/Average) -- a computation this "
        "harness's CQL-execution path cannot perform (no scriptable/batch "
        "CQL runner; see `defect-tracking/known-issues.md`, I-62). They are "
        "intentionally excluded from pass/fail scoring rather than reported "
        "as FAIL or silently read as 0. Every other population on these "
        "measures (Initial Population, Denominator, Numerator, exclusions, "
        "etc.) is unaffected and scored normally. Use the `mcp-cql-debug` "
        "per-member probe method documented in I-62 to manually verify any "
        "of the expected values below._\n")
    out.append("\n")
    out.append("| Measure | Excluded Populations |\n")
    out.append("| --- | --- |\n")
    for measure in sort_measure_names(list(cqfm_exclusions)):
        cells = ", ".join(sorted(cqfm_exclusions[measure]))
        out.append(f"| {measure} | {cells} |\n")
    out.append("\n")

    cqfm_cells = [c for c in unscored_cells
                  if getattr(c, "reason", None) == "cqfm-aggregation-excluded"]
    if cqfm_cells:
        out.append(
            f"_{len(cqfm_cells)} cells excluded across {len(cqfm_exclusions)} "
            "measures._\n")
        out.append("\n")
    return out

def row_outcome(expected_result: str, actual_result: str) -> Tuple[str, str]:
    """Return (result, actual_display) for a single expected/actual comparison."""
    if actual_result is None or str(expected_result) != str(actual_result):
        return ("FAIL", actual_result if actual_result is not None else "MISSING")
    return ("PASS", actual_result)


def test_case_outcomes(expected_rows: Dict, actual_rows: Dict) -> Dict[Tuple[str, str], str]:
    """Map (measure_name, patient_guid) -> 'PASS' or 'FAIL'.

    A test case passes iff every expected valid population cell for that case
    matches the actual value; it fails once if any expected cell is wrong or
    missing. Counting distinct test cases avoids inflating the counts when a
    single root cause (e.g. a denominator bug) derails several populations of
    the same case.
    """
    outcomes: Dict[Tuple[str, str], str] = {}
    for key, expected_result in expected_rows.items():
        # key fields: [ 'measure_name', 'patient_guid', 'group:population' ]
        if not is_scored(key[2].split(':', 1)[1]):
            continue
        actual_result = actual_rows.get(key)
        result, _ = row_outcome(expected_result, actual_result)
        case_key = (key[0], key[1])
        if result == "PASS":
            outcomes.setdefault(case_key, "PASS")
        else:
            outcomes[case_key] = "FAIL"
    return outcomes


def generate_output(file: str, expected_rows: Dict, actual_rows: Dict) -> Tuple[int, int]:
    """Write one row per expected population cell to ``file``.

    The CSV keeps per-population detail; the returned (pass, fail) counts are
    at test-case granularity (a case counts once even if several of its
    population cells mismatch — they usually share a root cause).
    """
    header = ["result", "measure_name", "guid", "population", "expected_result", "actual_result"]
    output = []

    for key, expected_result in expected_rows.items():
        # key fields: [ 'measure_name', 'patient_guid', 'group:population' ]
        # Unscored populations are excluded here and reported in the discrepancy
        # report's "Cells excluded from scoring" section (Results.unscored), so
        # the omission is visible rather than silent.
        if not is_scored(key[2].split(':', 1)[1]):
            continue

        actual_result = actual_rows.get(key)
        result, actual_display = row_outcome(expected_result, actual_result)
        output.append([result, key[0], key[1], key[2], expected_result, actual_display])

    with open(file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(output)

    return scores(expected_rows, actual_rows)


def scores(expected_rows: Dict[str, str], actual_rows: Dict[str, str]) -> Tuple[int, int]:
    """Compute (pass, fail) counting distinct test cases (not population cells)."""
    outcomes = test_case_outcomes(expected_rows, actual_rows)
    pass_count = sum(1 for o in outcomes.values() if o == "PASS")
    fail_count = sum(1 for o in outcomes.values() if o == "FAIL")
    return (pass_count, fail_count)


def create_markdown_table(headers: List[str], data: List[str], custom_separator_row: str=None) -> List[str]:
    table_rows = []

    # header row
    table_rows.append(f'| {" | ".join(headers)} |\n')

    # separator row
    table_rows.append(custom_separator_row if custom_separator_row else f'| {" | ".join(["---"] * len(headers))} |\n')

    # data rows
    for row_data in data:
        table_rows.append("| " + " | ".join(map(str, row_data)) + " |\n")
    table_rows.append('\n\n')
    return table_rows


def sort_measure_names(measure_names: List[str]) -> List[str]:
    measures_with_numbers_in_name = []
    for measure_name in measure_names:
        match = re.match(measure_id_pattern, measure_name)
        if match:
            measures_with_numbers_in_name.append(f'{match.group("measure_id")}---{measure_name}')
    sorted_measures_with_numbers_in_name = [m.split('---')[1] for m in sorted(measures_with_numbers_in_name, key=lambda x: int(x.split('---')[0]))]
    return sorted_measures_with_numbers_in_name + \
        [m for m in sorted([m for m in measure_names if m not in sorted_measures_with_numbers_in_name])]

def sort_populations(populations: List[str]) -> List[str]:
    order = {
        'initial population': 1,
        'denominator': 2,
        'denominator exclusion': 3,
        'denominator exception': 4,
        'numerator': 5,
        'numerator exclusion': 6}
    return sorted(populations, key=lambda x: order[x.lower()] if x.lower() in order else 99)

def sort_by_test_case(patient_guid: str, group: str) -> Tuple[str, str]:
    """Alphabetical sort key for a test case, ordered by patient GUID then group."""
    return (patient_guid.casefold(), group)

def sort_result_keys(result_keys: List[ResultKey]) -> List[ResultKey]:
    """Sort Missing Results alphabetically by test case."""
    return sorted(result_keys, key=lambda r: sort_by_test_case(r.patient_guid, r.group))

def sort_missing_populations(missing_populations: List[MissingPopulation]) -> List[MissingPopulation]:
    """Sort Missing Populations alphabetically by test case."""
    return sorted(missing_populations,
                  key=lambda mp: sort_by_test_case(mp.result_key.patient_guid, mp.result_key.group))

def sort_mismatched_test_cases(mismatched_test_cases: Dict[TestCaseGroupId, Dict[str, Comparison]]) -> List[Tuple[TestCaseGroupId, Dict[str, Comparison]]]:
    """Sort Mismatched Test Cases alphabetically by test case."""
    return sorted(mismatched_test_cases.items(),
                  key=lambda kv: sort_by_test_case(kv[0].patient_guid, kv[0].group))

def cql_file_link(measure_name: str, custom_id: str = None) -> str:
    return f'[ {custom_id} ](../../input/cql/{measure_name}.cql)' if custom_id else f'[ {measure_name} ](../../input/cql/{measure_name}.cql)'

def measure_report_file_link(measure_name: str, patient_guid: str) -> str:
    # path relative to root directory, this is the expected location for running the script
    measure_dir = f'./input/tests/measure/{measure_name}/{patient_guid}/'
    measure_report_file = glob.glob(f'{measure_dir}/MeasureReport*.json')
    if measure_report_file:
        # path relative to this script, need to add parent directories
        return f'[ {patient_guid} ](../../{measure_report_file[0]})'
    else:
        return patient_guid

def test_results_file_link(measure_name: str, custom_id: str = None) -> str:
    return f'[ {custom_id} ](../../input/tests/results/{measure_name}.txt)' if custom_id else f'[ {measure_name} ](../../input/tests/results/{measure_name}.txt)'


def capture_discrepancies_by_measure(expected_results: Dict[ResultKey, Dict[str, str]], actual_results: Dict[ResultKey, Dict[str, str]]) -> Dict[str, MeasureDiscrepancy]:
    def has_discrepancy(discrepancy: MeasureDiscrepancy) -> bool:
        return discrepancy.missing_populations or \
           discrepancy.missing_results or \
           discrepancy.mismatched_test_cases

    discrepancies = {}
    for expected_results_key, expected_populations in expected_results.items():
        measure_discrepancy = discrepancies.setdefault(expected_results_key.measure_name, MeasureDiscrepancy())
        measure_discrepancy.all_test_cases.append(expected_results_key.patient_guid)
        if expected_results_key not in actual_results:
            measure_discrepancy.missing_results.append(expected_results_key)
        else:
            actual_populations = actual_results[expected_results_key]
            # confirm all expected populations exist
            population_delta = list(set(expected_populations.keys()) - set(actual_populations.keys()))
            if population_delta:
                measure_discrepancy.missing_populations.append(MissingPopulation(expected_results_key, population_delta))
            else:
                mismatched_populations = { population: Comparison(expected_populations[population], actual_populations[population])
                     for population in expected_populations.keys() & actual_populations.keys() if expected_populations[population] != actual_populations[population]}
                if mismatched_populations:
                    measure_discrepancy.mismatched_test_cases[TestCaseGroupId(expected_results_key.patient_guid, expected_results_key.group)] = mismatched_populations
    return {measure: discrepancies[measure] for measure in sort_measure_names([k for k,v in discrepancies.items() if has_discrepancy(v)])}


def generate_comparison_report(file: str,
                               expected_results: Dict[ResultKey, Dict[str, str]],
                               actual_results: Dict[ResultKey, Dict[str, str]],
                               pass_count: int,
                               fail_count: int,
                               unscored_cells: List[UnscoredCell] = None,
                               cqfm_exclusions: Dict[str, FrozenSet[str]] = None):
    discrepancies = capture_discrepancies_by_measure(expected_results, actual_results)
    total_cases = pass_count + fail_count

    with open(file, "w", newline="") as f:
        f.write('# Discrepancy Report\n')
        f.writelines(create_markdown_table(
            ['Details', 'Value'],
            [
                ['Generated', datetime.now()],
                ['Total Measures', len(set([k.measure_name for k in expected_results.keys()]))],
                ['Total Test Cases', total_cases],
                ['Measures with Discrepancies', len(discrepancies)],
                ['Pass Count', f'{pass_count} ({pass_count / total_cases * 100:.2f}%)' if total_cases else '0'],
                ['Fail Count', f'{fail_count} ({fail_count / total_cases * 100:.2f}%)' if total_cases else '0'],
            ]
        ))
        f.writelines(create_markdown_table(
            ['Discrepancy Summary', 'Measure Count', 'Test Case Count'],
            [
                [
                    'Missing Results',
                    len(set([m for m, d in discrepancies.items() if d.missing_results])),
                    sum([len(d.missing_results) for d in discrepancies.values()])
                ],
                [
                    'Missing Populations',
                    len(set([m for m, d in discrepancies.items() if d.missing_populations])),
                    sum([len(d.missing_populations) for d in discrepancies.values()])
                ],
                [
                    'Mismatched Test Cases',
                    len(set([m for m, d in discrepancies.items() if d.mismatched_test_cases])),
                    sum([len(d.mismatched_test_cases.keys()) for d in discrepancies.values()])
                ]
            ],
            '|---|:---:|:---:|\n'))
        f.write('\n')
        f.write('_Note: Measures can have multiple discrepancies, so the Measures with '
                'Discrepancies count may not match the summary counts._\n')
        f.write('\n')

        f.writelines(render_cqfm_exclusions_section(cqfm_exclusions or {},
                                                    unscored_cells or []))

        non_discrepancy_measures = [
            m for m in sort_measure_names(list(set([k.measure_name for k in expected_results.keys()])))
            if m not in discrepancies]
        if non_discrepancy_measures:
            f.write(f'## Measures with No Discrepancies ({len(non_discrepancy_measures)})\n')
            for measure in non_discrepancy_measures:
                f.write(f'- {measure} {cql_file_link(measure, "[cql]")} '
                        f'{test_results_file_link(measure, "[test results]")}\n')
            f.write('\n')

        if discrepancies:
            f.write(f'## Measures with Discrepancies ({len(discrepancies)})\n')
            f.writelines(create_markdown_table(
                ['Measure', 'Total Test Cases', 'Missing Results', 'Missing Populations', 'Mismatched Test Cases'],
                [
                    [
                        f'[{measure}](#{measure.lower()})',
                        len(discrepancy.all_test_cases),
                        len(discrepancy.missing_results),
                        len(discrepancy.missing_populations),
                        f'{len(discrepancy.mismatched_test_cases)/len(discrepancy.all_test_cases)*100:.2f}%   '
                        f'({len(discrepancy.mismatched_test_cases)})'
                    ] for measure, discrepancy in discrepancies.items()
                ],
                '|---|:---:|:---:|:---:|:---:|\n'))
            f.write('\n')

            for measure, discrepancy in discrepancies.items():
                f.write(f'#### {measure}\n')
                f.write(f'{cql_file_link(measure, "[cql]")} '
                        f'{test_results_file_link(measure, "[test results]")}\n\n')

                if discrepancy.missing_results:
                    f.write(f'Missing Results ({len(discrepancy.missing_results)} of '
                            f'{len(discrepancy.all_test_cases)} test cases)\n')
                    f.writelines(create_markdown_table(
                        ['Test Case', 'Group'],
                        [[
                            measure_report_file_link(m.measure_name, m.patient_guid),
                            m.group
                        ] for m in sort_result_keys(list(discrepancy.missing_results))]))

                if discrepancy.missing_populations:
                    f.write(f'Missing Populations ({len(discrepancy.missing_populations)} of '
                            f'{len(discrepancy.all_test_cases)} test cases)\n')
                    f.writelines(create_markdown_table(
                        ['Test Case', 'Group', 'Population'],
                        [[
                            measure_report_file_link(missing_id.measure_name, missing_id.patient_guid),
                            missing_id.group,
                            ','.join(populations)
                        ] for (missing_id, populations) in sort_missing_populations(
                            list(discrepancy.missing_populations))]))

                if discrepancy.mismatched_test_cases:
                    f.write(f'Mismatched Test Cases ({len(discrepancy.mismatched_test_cases)} of '
                            f'{len(discrepancy.all_test_cases)})\n')
                    f.writelines(create_markdown_table(
                        ['Test Case', 'Group', 'Population', 'Expected', 'Actual'],
                        [[
                            measure_report_file_link(measure, test_group_id.patient_guid),
                            test_group_id.group,
                            '<br>'.join([p for p in sort_populations(populations.keys())]),
                            '<br>'.join([populations[p].expected for p in sort_populations(populations.keys())]),
                            '<br>'.join([populations[p].actual for p in sort_populations(populations.keys())])
                        ] for test_group_id, populations in sort_mismatched_test_cases(
                            discrepancy.mismatched_test_cases)],
                        '|---|---|---|:---:|:---:|\n'))
                    f.write('\n')

        f.write('\n_Known issues are tracked by hand in '
                '`defect-tracking/known-issues.md`; open judgment calls are in '
                '`defect-tracking/CONNECTATHON-BREADCRUMBS.md`._\n')


def main(expected_file: str, actual_file: str, output_file: str,
         comparison_report: str, measure_resource_dir: str = None):
    # Exclusions are computed once and applied symmetrically to expected and
    # actual, so a cell is either scored on both sides or neither.
    cqfm_exclusions = load_cqfm_aggregation_exclusions(
        measure_resource_dir or DEFAULT_MEASURE_RESOURCE_DIR)

    expected_results = capture_results(expected_file, cqfm_exclusions)
    actual_results = capture_results(actual_file, cqfm_exclusions)

    pass_count, fail_count = generate_output(output_file, expected_results.rows,
                                             actual_results.rows)
    total = pass_count + fail_count
    pass_pct = (pass_count / total * 100) if total else 0.0
    print(f"PASS (test cases): {pass_count} ({pass_pct:.2f})%")
    print(f"FAIL (test cases): {fail_count} ({(100 - pass_pct):.2f})%")

    unscored = list(expected_results.unscored) + list(actual_results.unscored)
    generate_comparison_report(comparison_report, expected_results.groups,
                               actual_results.groups, pass_count, fail_count,
                               unscored_cells=unscored,
                               cqfm_exclusions=cqfm_exclusions)


if __name__ == '__main__':
    expected_file = "./scripts/comparison/expected_results.csv"
    actual_file = "./scripts/comparison/actual_results.csv"
    output_file = "./scripts/comparison/output_results.csv"
    comparison_report = "./scripts/comparison/discrepancy_report.md"
    measure_resource_dir = None

    args = sys.argv[1:]
    if "--measure-resource-dir" in args:
        idx = args.index("--measure-resource-dir")
        if idx + 1 < len(args):
            measure_resource_dir = args[idx + 1]
        args = args[:idx] + args[idx + 2:]
    if args:
        # positional: expected actual output report
        expected_file = args[0]
        if len(args) > 1:
            actual_file = args[1]
        if len(args) > 2:
            output_file = args[2]
        if len(args) > 3:
            comparison_report = args[3]

    main(expected_file, actual_file, output_file, comparison_report,
         measure_resource_dir=measure_resource_dir)
