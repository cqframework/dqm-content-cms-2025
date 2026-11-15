"""Compare expected measure results against actual CQL engine results.

Reads two CSVs of ``measure_name,guid,population,count`` rows and writes:

  * ``output_results.csv`` -- one PASS/FAIL/MISSING row per population cell
  * ``discrepancy_report.md`` -- per-measure Missing Results, Missing
    Populations, and Mismatched Test Cases

Run it with no arguments from the repository root; see ``scripts/readme.md``.

Five behaviours are worth knowing about, because each exists to stop the report
inventing discrepancies that are not there -- and one exists to stop it hiding
one that is real:

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
  * **Implementation issues resolve a failing test case.** Some test cases
    can't match their fixture MeasureReport because the measure steward's test
    data or expectation misuses FHIR or CQL semantics (class `implementation` in
    `defect-tracking/known-issues.md`; e.g. I-67). They are listed in
    ``scripts/comparison/implementation_issues.csv``. A failing cell covered by
    one scores ``IMPLEMENTATION`` instead of ``FAIL``, and a test case whose
    every failing cell is covered counts as resolved, the same as a pass. Those
    cases stay in the per-measure discrepancy tables, labelled with the issue.
  * **A ticketed known issue resolves a failing test case.** A case whose
    failure is explained by a catalogued engine, translator, content, ... issue
    is listed in ``scripts/comparison/known_issues.csv`` with the issue's
    upstream ticket (a GitHub issue/PR or an HL7 JIRA issue). Once the ticket is recorded, a covered failing cell scores
    ``KNOWN_ISSUE`` and the case counts as resolved. Without a ticket the case
    still fails, and the report labels it as awaiting one -- or, for a class no
    upstream ticket could track (our own content, fixture, or harness), labels
    the cell ``N/A`` while it stays a failure. Every mismatch, of
    either kind or of none, is listed under `## Measures with Discrepancies`
    with an `Issue` column and the issue's note. The ones no issue resolves are
    counted as Unattributed Discrepancies.
  * **A workaround keeps a passing case in the report.** Some issues are listed
    in ``known_issues.csv`` with ``defect_status`` ``workaround-applied``: the
    measure's CQL already casts, retrieves or restructures around the defect, so
    the test case *matches* its fixture. Scoring it ``PASS`` would erase the
    open defect from the report, so a matching cell whose issue carries that
    status scores ``WORKAROUND`` instead -- neither a pass nor a failure. The
    measure stays under `## Measures with Discrepancies` with a `Workarounds`
    table, and the workaround is expected to be reverted when the root cause is
    fixed (at which point the case fails again and takes the normal FAIL path).
  * **An I-28 workaround note names the affected measures.** Measures whose CQL
    carries the ``[I-28]`` comment marker use a base ``FHIR.Condition`` retrieve
    in place of a sibling-profile Condition union -- the preferred pattern while
    the I-28 translator defect is open, and the only form that resolves today.
    The note lists those measures (never their test cases), says the change is a
    workaround rather than a fix, and points at the upstream ticket; the
    workaround is to be reverted once that ticket closes.
"""
import csv
import glob
import os
import re
import sys
from collections import namedtuple
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, FrozenSet, List, NamedTuple, Optional, Sequence, Set, Tuple, TypedDict

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

# Optional third input: test cases that can't match their fixture because of
# the measure steward's test data, not the engine. See the module docstring.
# Absent is fine -- no case is treated as an implementation issue.
DEFAULT_IMPLEMENTATION_ISSUES_FILE = "./scripts/comparison/implementation_issues.csv"

# The per-cell and per-test-case verdict for a failure covered by an
# implementation issue. Counts as resolved, not as a failure.
IMPLEMENTATION = "IMPLEMENTATION"

# Optional fourth input: failing test cases tied to a catalogued engine,
# translator, content, ... issue (`defect-tracking/known-issues.md`). A case
# resolves only once its issue has an upstream ticket (GitHub issue/PR or HL7
# JIRA). Absent is fine.
DEFAULT_KNOWN_ISSUES_FILE = "./scripts/comparison/known_issues.csv"

# The per-cell and per-test-case verdict for a failure covered by a known issue
# that has a ticket. Counts as resolved. Without a ticket the cell stays FAIL.
KNOWN_ISSUE = "KNOWN_ISSUE"

# The per-cell and per-test-case verdict for a *matching* cell whose issue says a
# workaround is applied. Counts as neither a pass nor a failure: the case matches
# its fixture, but only because the measure's CQL works around an open defect,
# and the workaround is scheduled to be reverted.
WORKAROUND = "WORKAROUND"

# The `KnownIssue.status` value that marks a workaround. `known_issues.csv` is
# generated from the dossier's `defect_status`, so this is the only spelling that
# can appear.
WORKAROUND_STATUS = "workaround-applied"

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
    # Cases that match their fixture only because a workaround is applied. Not a
    # mismatch, but an open defect the report must not lose sight of.
    workarounds: List[ResultKey] = field(default_factory=list)

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
    vs "Measure Observation" in the engine's actuals. Canonicalising here, at
    the single read point, keeps every downstream key consistent.

    Cells whose population is not a scored population are collected in
    ``unscored`` instead of being silently dropped, so the report can say what
    it did not measure.

    ``cqfm_exclusions`` (``populations.load_cqfm_aggregation_exclusions()``)
    are cells that require per-member CQFM aggregation this harness cannot
    perform (see defect-tracking/known-issues.md, I-62) -- these are also routed to
    ``unscored`` (with ``reason="cqfm-aggregation-excluded"``) rather than
    ``rows``/``results``. Passing the *same* exclusion set into both
    ``capture_results`` calls for a run (expected and actual) is what keeps
    the exclusion symmetric: since the cell never enters
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


def side_status(expected_pops: Dict[str, str],
                side_pops: Optional[Dict[str, str]]) -> str:
    """The engine's verdict on one test case: PASS, FAIL, or MISSING.

    ``expected_pops`` and ``side_pops`` are the per-population count maps for
    one (measure, guid, group), as produced by ``capture_results(...).groups``.

    * ``MISSING`` -- the engine produced no result for this test case at all, so
      there is nothing to compare. Not the same as PASS: it is the absence of
      evidence, and is reported separately from a confirmed FAIL.
    * ``PASS`` -- every expected population equals the engine's value.
    * ``FAIL`` -- otherwise. A population this engine lacks counts as a mismatch,
      because a measure that emits no row for a scored population has not
      reproduced the expectation any more than a wrong value has.

    Comparison is string-equality on the raw counts, matching ``row_outcome`` so
    that the per-case and per-cell verdicts are decided by the same rule.
    """
    if side_pops is None:
        return "MISSING"
    for population, expected in expected_pops.items():
        side_value = side_pops.get(population)
        if side_value is None or str(expected) != str(side_value):
            return "FAIL"
    return "PASS"


class ImplementationIssue(NamedTuple):
    """One row of ``implementation_issues.csv``.

    ``group`` is optional: blank means the issue applies to every group of the
    test case, which is the usual case because a malformed resource belongs to
    the patient, not to a group.
    """
    issue_id: str
    measure_name: str
    guid: str
    group: str
    note: str


IMPLEMENTATION_ISSUE_COLUMNS = ("issue_id", "measure_name", "guid", "group", "note")


def load_implementation_issues(file: Optional[str]) -> List[ImplementationIssue]:
    """Read ``implementation_issues.csv``; an absent file means no issues.

    Columns: ``issue_id,measure_name,guid,group,note``. Values are stripped and
    blank rows are skipped. A file missing a required column, or a row with
    more fields than columns (an unquoted comma), raises ValueError rather than
    silently matching nothing.
    """
    if not file or not os.path.exists(file):
        return []
    issues: List[ImplementationIssue] = []
    with open(file, newline="") as f:
        reader = csv.DictReader(f)
        header = [h.strip() for h in (reader.fieldnames or [])]
        missing = [c for c in ("issue_id", "measure_name", "guid") if c not in header]
        if missing:
            raise ValueError(
                f"{file}: missing column(s) {', '.join(missing)}; expected "
                f"{','.join(IMPLEMENTATION_ISSUE_COLUMNS)}")
        for raw in reader:
            if None in raw:
                # csv.DictReader files surplus fields under the None key.
                raise ValueError(
                    f"{file}, line {reader.line_num}: more fields than columns; "
                    "quote any value that contains a comma")
            row = {(k or "").strip(): (v or "").strip() for k, v in raw.items()}
            if not any(row.values()):
                continue
            issues.append(ImplementationIssue(
                row["issue_id"], row["measure_name"], row["guid"],
                row.get("group", ""), row.get("note", "")))
    return issues


def implementation_issue_for(key: ResultKey, issues: Sequence):
    """The issue covering this (measure, guid, group), if any.

    Works on any rows with ``measure_name``, ``guid`` and ``group``, so it
    serves ``KnownIssue`` lists as well as ``ImplementationIssue`` ones.
    """
    for issue in issues:
        if (issue.measure_name == key.measure_name
                and issue.guid == key.patient_guid
                and issue.group in ("", key.group)):
            return issue
    return None


def cell_result_key(row_key: Tuple[str, str, str]) -> ResultKey:
    """The ResultKey of a ``Results.rows`` key ``(measure, guid, "group:population")``."""
    return ResultKey(row_key[0], row_key[1], row_key[2].split(':', 1)[0])


def failing_implementation_keys(expected_results: Dict[ResultKey, Dict[str, str]],
                                actual_results: Dict[ResultKey, Dict[str, str]],
                                issues: Sequence[ImplementationIssue]) -> Set[ResultKey]:
    """Failing (test case, group)s covered by an implementation issue.

    Decided by ``side_status``. A covered group that passes isn't included: it needs no
    explanation.
    """
    if not issues:
        return set()
    return {key for key, expected_pops in expected_results.items()
            if side_status(expected_pops, actual_results.get(key)) != "PASS"
            and implementation_issue_for(key, issues) is not None}


class KnownIssue(NamedTuple):
    """One row of ``known_issues.csv``: a test case tied to a catalogued issue.

    ``ticket`` is the upstream ticket URL tracking the fix -- a GitHub issue (or
    pull request), or an HL7 JIRA issue such as
    ``https://jira.hl7.org/browse/FHIR-59691``. A
    known issue resolves a failing case only once it has one; until then the
    case stays FAIL and is reported as awaiting a ticket. ``group`` is optional,
    as in ``ImplementationIssue``.

    ``status`` is the dossier's ``defect_status`` -- one of ``suspected``,
    ``confirmed`` or ``workaround-applied``, because the file is generated from
    the open-issue catalog. A ``workaround-applied`` issue means the measure's
    CQL already works around the defect, so the case is *expected to pass*: a
    matching cell scores ``WORKAROUND`` rather than ``PASS``, and the measure
    stays in the discrepancy report while the defect is open. Optional in the
    file; a row without it is an ordinary failing-case catalog row, which keeps
    older hand-written fixtures loading.
    """
    issue_id: str
    issue_class: str
    status: str
    ticket: str
    measure_name: str
    guid: str
    group: str
    note: str

    @property
    def ticketed(self) -> bool:
        return bool(self.ticket)

    @property
    def workaround_applied(self) -> bool:
        return self.status == WORKAROUND_STATUS


KNOWN_ISSUE_COLUMNS = ("issue_id", "class", "status", "ticket", "measure_name", "guid",
                       "group", "note")

# Root-cause classes from `defect-tracking/known-issues.md`, less `implementation`,
# which has its own file because it resolves a case without a ticket.
KNOWN_ISSUE_CLASSES = ("engine", "translator", "content", "migration", "fixture",
                       "vendored", "harness")

# The subset of `KNOWN_ISSUE_CLASSES` whose root cause lives in an upstream project
# (`clinical_quality_language` / `clinical-reasoning`), so an upstream ticket is the
# right tracking artifact and its absence is worth saying out loud as ``pending``.
# Every other class is our own content, fixture, or harness -- nothing an upstream
# ticket tracks, so those rows read ``N/A`` rather than implying a ticket is owed.
TICKETABLE_CLASSES = ("engine", "translator")

GITHUB_TICKET_PATTERN = re.compile(r"^https://github\.com/[^/\s]+/[^/\s]+/(?:issues|pull)/\d+$")
# HL7 JIRA, e.g. https://jira.hl7.org/browse/FHIR-59691 -- the tracker the
# upstream projects outside GitHub (FHIRCommon, the published IGs) use.
JIRA_TICKET_PATTERN = re.compile(r"^https://jira\.hl7\.org/browse/[A-Z][A-Z0-9]+-\d+$")


def is_ticket_url(value: str) -> bool:
    """True for a recognized upstream ticket URL: a GitHub issue/PR or HL7 JIRA."""
    return bool(GITHUB_TICKET_PATTERN.match(value) or JIRA_TICKET_PATTERN.match(value))


def load_known_issues(file: Optional[str]) -> List[KnownIssue]:
    """Read ``known_issues.csv``; an absent file means no known issues.

    Columns: ``issue_id,class,status,ticket,measure_name,guid,group,note``
    (``status`` optional and empty when absent). Raises ValueError on a missing
    column, an unquoted comma, a class outside ``KNOWN_ISSUE_CLASSES``, a
    ``ticket`` that isn't a GitHub issue/PR or HL7 JIRA URL (so a placeholder like ``TBD``
    can't resolve a case), or rows of one issue that disagree on class, status
    or ticket (those belong to the issue, not the case).

    ``status`` is not validated: it is generated from the catalog, whose open
    statuses are the only values that can appear, and rejecting an unfamiliar
    one here would stop the harness rather than report anything useful.
    """
    if not file or not os.path.exists(file):
        return []
    issues: List[KnownIssue] = []
    seen: Dict[str, Tuple[str, str]] = {}
    with open(file, newline="") as f:
        reader = csv.DictReader(f)
        header = [h.strip() for h in (reader.fieldnames or [])]
        missing = [c for c in ("issue_id", "class", "ticket", "measure_name", "guid")
                   if c not in header]
        if missing:
            raise ValueError(
                f"{file}: missing column(s) {', '.join(missing)}; expected "
                f"{','.join(KNOWN_ISSUE_COLUMNS)}")
        for raw in reader:
            if None in raw:
                raise ValueError(
                    f"{file}, line {reader.line_num}: more fields than columns; "
                    "quote any value that contains a comma")
            row = {(k or "").strip(): (v or "").strip() for k, v in raw.items()}
            if not any(row.values()):
                continue
            where = f"{file}, line {reader.line_num}"
            if row["class"] not in KNOWN_ISSUE_CLASSES:
                hint = (" (list implementation issues in implementation_issues.csv)"
                        if row["class"] == "implementation" else "")
                raise ValueError(f"{where}: class {row['class']!r} is not one of "
                                 f"{', '.join(KNOWN_ISSUE_CLASSES)}{hint}")
            if row["ticket"] and not is_ticket_url(row["ticket"]):
                raise ValueError(f"{where}: ticket {row['ticket']!r} is neither a GitHub "
                                 "issue or pull request URL nor an HL7 JIRA URL; leave it "
                                 "blank until one exists")
            identity = (row["class"], row.get("status", ""), row["ticket"])
            if seen.setdefault(row["issue_id"], identity) != identity:
                raise ValueError(f"{where}: {row['issue_id']} rows disagree on class, "
                                 "status or ticket; every row of an issue must carry the "
                                 "same values")
            issues.append(KnownIssue(
                row["issue_id"], row["class"], row.get("status", ""), row["ticket"],
                row["measure_name"], row["guid"], row.get("group", ""), row.get("note", "")))
    return issues


def failing_known_issue_keys(expected_results: Dict[ResultKey, Dict[str, str]],
                             actual_results: Dict[ResultKey, Dict[str, str]],
                             known_issues: Sequence[KnownIssue],
                             implementation_issues: Sequence[ImplementationIssue] = (),
                             ticketed: bool = True) -> Set[ResultKey]:
    """Failing (test case, group)s covered by a known issue with (or without) a ticket.

    A group an implementation issue already covers is left out: that
    explanation takes precedence, so no group is counted twice.
    """
    if not known_issues:
        return set()
    keys = set()
    for key, expected_pops in expected_results.items():
        if side_status(expected_pops, actual_results.get(key)) == "PASS":
            continue
        if implementation_issue_for(key, implementation_issues) is not None:
            continue
        issue = implementation_issue_for(key, known_issues)
        if issue is not None and issue.ticketed == ticketed:
            keys.add(key)
    return keys


def workaround_keys(expected_results: Dict[ResultKey, Dict[str, str]],
                    actual_results: Dict[ResultKey, Dict[str, str]],
                    known_issues: Sequence[KnownIssue]) -> Set[ResultKey]:
    """Matching (test case, group)s whose issue says a workaround is applied.

    Only a group that currently matches counts. An issue-carried workaround that
    has been reverted -- or that never worked -- leaves the cell failing, and
    that failure is reported through the ordinary FAIL path instead, so the
    report can never claim a workaround is holding up a case it is not.

    A row without a ``status`` is never a workaround, so an ordinary catalog row
    whose case happens to pass stays a stale attribution rather than being
    relabelled here.
    """
    if not known_issues:
        return set()
    keys = set()
    for key, expected_pops in expected_results.items():
        if side_status(expected_pops, actual_results.get(key)) != "PASS":
            continue
        issue = implementation_issue_for(key, known_issues)
        if issue is not None and issue.workaround_applied:
            keys.add(key)
    return keys


I28_MARKER = '[I-28]'
I28_TICKET = 'https://github.com/cqframework/clinical_quality_language/issues/1872'


def measures_with_cql_marker(marker: str,
                             cql_dir: str = './input/cql',
                             tests_dir: str = './input/tests/measure') -> List[str]:
    """Measures whose CQL carries ``marker`` and that have a test-case suite.

    The CQL comment convention (``// [I-XX] ...``, see the repository's
    ``AGENTS.md``) makes the measures' own CQL the source of truth for which
    ones carry a workaround -- no separate list to drift. Helper libraries
    without a test-case suite (e.g. ``defectHelper.cql``) are excluded, and an
    absent ``cql_dir`` (a run outside the content repository) yields nothing.
    """
    if not os.path.isdir(cql_dir):
        return []
    measures = []
    for entry in sorted(os.listdir(cql_dir)):
        if not entry.endswith('.cql'):
            continue
        stem = entry[:-len('.cql')]
        if not os.path.isdir(os.path.join(tests_dir, stem)):
            continue
        with open(os.path.join(cql_dir, entry), encoding='utf-8') as fh:
            if marker in fh.read():
                measures.append(stem)
    return measures


def render_i28_workaround_note_section(measures: Sequence[str]) -> List[str]:
    """``## I-28 Workaround Note``: the base-``Condition`` retrieve, and why.

    I-28 is a translator defect: a sibling-profile Condition union types as
    ``Choice<ConditionProblemsHealthConcerns, ConditionEncounterDiagnosis>`` and
    the translator will not widen it to base ``FHIR.Condition``, so the whole
    library fails to translate. Every affected measure therefore retrieves
    ``[FHIR.Condition: ...]`` directly. That change is semantics-preserving and
    is the preferred pattern *while the defect is open* -- but it is a
    workaround, not a fix, and the original union code is what should be
    restored once the upstream ticket closes. Without this note the measures
    read as unqualified passes, hiding both the workaround and the open defect.
    Test cases are deliberately not listed: the workaround is library-wide, so
    every case of every listed measure runs it. The grid matches
    `## Measures with No Discrepancies` -- column-major, with the measure name
    as the CQL link label -- so the two lists read the same way.
    """
    if not measures:
        return []
    out = ["## I-28 Workaround Note\n", "\n"]
    out.append(
        f"_{len(measures)} measures include the I-28 workaround: the original "
        "sibling-profile "
        "`[ConditionProblemsHealthConcerns: ...] union [ConditionEncounterDiagnosis: ...]` "
        "retrieves were replaced with a single base `[FHIR.Condition: ...]` "
        "retrieve. The base-`Condition` retrieve is the preferred CQL pattern "
        "for this content while I-28 is open -- it selects the same Conditions "
        "the union expresses, so the change is semantics-preserving, and it is "
        "the only form the translator resolves "
        "today. It is a workaround, not a fix: the original union code is "
        "valid CQL, and I-28 is the translator defect that blocks it "
        "(`Choice<...>` arguments are not widened to base `Condition`, for "
        "either a shared-library `prevalenceInterval` overload or an ancestor "
        "overload). The union defect is tracked by "
        f"[cqframework/clinical_quality_language#1872]({I28_TICKET}); once that "
        "ticket closes, these measures' workarounds could be reverted to the "
        "original union code, but using just Condition is the preferred pattern."
        "Individual test cases are not listed because the workaround is "
        "library-wide: every test case of every measure below runs it._\n")
    out.append("\n")
    sorted_measures = sort_measure_names(list(measures))
    column_count = NO_DISCREPANCY_TABLE_COLUMNS
    rows_needed = -(-len(sorted_measures) // column_count)
    columns = [sorted_measures[row * rows_needed:(row + 1) * rows_needed]
               for row in range(column_count)]
    out.extend(create_markdown_table(
        [''] * column_count,
        [[cql_file_link(column[row]) if row < len(column) else ''
          for column in columns]
         for row in range(rows_needed)]))
    return out


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
        "etc.) is unaffected and scored normally. Use the cql-mcp `cql_execute` "
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


def cell_outcome(key: Tuple[str, str, str], expected_result: str, actual_result: str,
                 implementation_issues: Sequence[ImplementationIssue] = (),
                 known_issues: Sequence[KnownIssue] = ()) -> Tuple[str, str]:
    """``row_outcome``, with a covered FAIL scored IMPLEMENTATION or KNOWN_ISSUE.

    An implementation issue wins over a known issue. A known issue without a
    ticket leaves the cell FAIL.

    A *matching* cell whose issue carries ``workaround-applied`` scores
    ``WORKAROUND``: it passes, but only because the measure's CQL works around an
    open defect, so calling it a pass would hide the defect.
    """
    result, actual_display = row_outcome(expected_result, actual_result)
    result_key = cell_result_key(key)
    if result == "FAIL":
        if implementation_issue_for(result_key, implementation_issues):
            result = IMPLEMENTATION
        else:
            issue = implementation_issue_for(result_key, known_issues)
            if issue is not None and issue.ticketed:
                result = KNOWN_ISSUE
    elif result == "PASS":
        issue = implementation_issue_for(result_key, known_issues)
        if issue is not None and issue.workaround_applied:
            result = WORKAROUND
    return result, actual_display


def test_case_outcomes(expected_rows: Dict, actual_rows: Dict,
                       implementation_issues: Sequence[ImplementationIssue] = (),
                       known_issues: Sequence[KnownIssue] = ()) -> Dict[Tuple[str, str], str]:
    """Map (measure_name, patient_guid) -> a verdict for the case.

    One of ``PASS``, ``WORKAROUND``, ``IMPLEMENTATION``, ``KNOWN_ISSUE`` or
    ``FAIL``.

    A test case passes iff every expected valid population cell for that case
    matches the actual value; it fails once if any expected cell is wrong or
    missing. Counting distinct test cases avoids inflating the counts when a
    single root cause (e.g. a denominator bug) derails several populations of
    the same case.

    A case is IMPLEMENTATION when it has a mismatching cell and every
    mismatching cell is covered by an implementation issue. One uncovered
    mismatch, e.g. in a group the issue doesn't name, makes it FAIL. KNOWN_ISSUE
    is the same, for cells covered by a ticketed known issue; a case with both
    kinds of cell is KNOWN_ISSUE. WORKAROUND is a case that matches but carries a
    workaround-applied issue, and it outranks PASS so that a single workaround
    cell marks the whole case. Every verdict but FAIL counts as accounted for;
    only PASS counts as a pass and only FAIL as a failure.
    """
    rank = {"PASS": 0, WORKAROUND: 1, IMPLEMENTATION: 2, KNOWN_ISSUE: 3, "FAIL": 4}
    outcomes: Dict[Tuple[str, str], str] = {}
    for key, expected_result in expected_rows.items():
        # key fields: [ 'measure_name', 'patient_guid', 'group:population' ]
        if not is_scored(key[2].split(':', 1)[1]):
            continue
        result, _ = cell_outcome(key, expected_result, actual_rows.get(key),
                                 implementation_issues, known_issues)
        case_key = (key[0], key[1])
        if rank[result] >= rank[outcomes.get(case_key, "PASS")]:
            outcomes[case_key] = result
    return outcomes


def generate_output(file: str, expected_rows: Dict, actual_rows: Dict,
                    implementation_issues: Sequence[ImplementationIssue] = (),
                    known_issues: Sequence[KnownIssue] = ()) -> Tuple[int, int]:
    """Write one row per expected population cell to ``file``.

    The CSV keeps per-population detail; the returned (pass, fail) counts are
    at test-case granularity (a case counts once even if several of its
    population cells mismatch — they usually share a root cause). A mismatching
    cell covered by an implementation issue is written as IMPLEMENTATION, one
    covered by a ticketed known issue as KNOWN_ISSUE, and a matching cell under
    a workaround-applied issue as WORKAROUND; such cases are in neither count;
    see ``implementation_case_count``/``known_issue_case_count``/
    ``workaround_case_count``.
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

        result, actual_display = cell_outcome(key, expected_result, actual_rows.get(key),
                                              implementation_issues, known_issues)
        output.append([result, key[0], key[1], key[2], expected_result, actual_display])

    with open(file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(output)

    return scores(expected_rows, actual_rows, implementation_issues, known_issues)


def scores(expected_rows: Dict[str, str], actual_rows: Dict[str, str],
           implementation_issues: Sequence[ImplementationIssue] = (),
           known_issues: Sequence[KnownIssue] = ()) -> Tuple[int, int]:
    """Compute (pass, fail) counting distinct test cases (not population cells).

    IMPLEMENTATION, KNOWN_ISSUE and WORKAROUND cases are in neither count; see
    ``implementation_case_count``, ``known_issue_case_count`` and
    ``workaround_case_count``.
    """
    outcomes = test_case_outcomes(expected_rows, actual_rows, implementation_issues,
                                  known_issues)
    pass_count = sum(1 for o in outcomes.values() if o == "PASS")
    fail_count = sum(1 for o in outcomes.values() if o == "FAIL")
    return (pass_count, fail_count)


def implementation_case_count(expected_rows: Dict[str, str], actual_rows: Dict[str, str],
                              implementation_issues: Sequence[ImplementationIssue],
                              known_issues: Sequence[KnownIssue] = ()) -> int:
    """Test cases resolved by an implementation issue rather than by a match."""
    outcomes = test_case_outcomes(expected_rows, actual_rows, implementation_issues,
                                  known_issues)
    return sum(1 for o in outcomes.values() if o == IMPLEMENTATION)


def known_issue_case_count(expected_rows: Dict[str, str], actual_rows: Dict[str, str],
                           implementation_issues: Sequence[ImplementationIssue],
                           known_issues: Sequence[KnownIssue]) -> int:
    """Test cases resolved by a ticketed known issue rather than by a match."""
    outcomes = test_case_outcomes(expected_rows, actual_rows, implementation_issues,
                                  known_issues)
    return sum(1 for o in outcomes.values() if o == KNOWN_ISSUE)


def workaround_case_count(expected_rows: Dict[str, str], actual_rows: Dict[str, str],
                          implementation_issues: Sequence[ImplementationIssue],
                          known_issues: Sequence[KnownIssue]) -> int:
    """Test cases that match only because a workaround is applied.

    Counted separately from both the passes and the failures: the case agrees
    with its fixture, but the issue that explains why the CQL needs a workaround
    is still open, and the workaround is meant to be removed once it is fixed.
    """
    outcomes = test_case_outcomes(expected_rows, actual_rows, implementation_issues,
                                  known_issues)
    return sum(1 for o in outcomes.values() if o == WORKAROUND)


def ticketed_known_issue_cases(expected_rows: Dict[str, str],
                               known_issues: Sequence[KnownIssue]) -> Set[Tuple[str, str]]:
    """``(measure, guid)`` pairs with a scored cell covered by a ticketed issue.

    Coverage is a property of the attribution rows and the expected keys, so the
    actual values are not consulted: a case counts whether it currently matches
    its fixture or not. That is the point. ``cell_outcome`` reaches
    ``KNOWN_ISSUE`` only from a mismatching cell and ``WORKAROUND`` only from a
    matching one, so a case that a ticketed issue covers *and* a workaround props
    up (I-78's CMS145 cases) can carry only one of the two verdicts, and neither
    verdict alone reports the ticketed coverage.
    """
    cases = set()
    for key in expected_rows:
        issue = implementation_issue_for(cell_result_key(key), known_issues)
        if issue is not None and issue.ticketed:
            cases.add((key[0], key[1]))
    return cases


def ticketed_known_issue_coverage_count(expected_rows: Dict[str, str],
                                        actual_rows: Dict[str, str],
                                        implementation_issues: Sequence[ImplementationIssue],
                                        known_issues: Sequence[KnownIssue]) -> int:
    """Test cases explained by a ticketed known issue, matching or failing.

    Spans the ``KNOWN_ISSUE`` and ``WORKAROUND`` verdicts, which partition with
    each other, so it reports the ticketed coverage that either one alone drops.
    Only those two explained verdicts are counted: a stale attribution row on a
    case that genuinely passes would otherwise inflate the total.
    """
    outcomes = test_case_outcomes(expected_rows, actual_rows, implementation_issues,
                                  known_issues)
    covered = ticketed_known_issue_cases(expected_rows, known_issues)
    return sum(1 for case_key, verdict in outcomes.items()
               if case_key in covered and verdict in (KNOWN_ISSUE, WORKAROUND))


def ticketed_workaround_case_count(expected_rows: Dict[str, str],
                                   actual_rows: Dict[str, str],
                                   implementation_issues: Sequence[ImplementationIssue],
                                   known_issues: Sequence[KnownIssue]) -> int:
    """The ``WORKAROUND`` subset of ``ticketed_known_issue_coverage_count``."""
    outcomes = test_case_outcomes(expected_rows, actual_rows, implementation_issues,
                                  known_issues)
    covered = ticketed_known_issue_cases(expected_rows, known_issues)
    return sum(1 for case_key, verdict in outcomes.items()
               if case_key in covered and verdict == WORKAROUND)


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


NO_DISCREPANCY_TABLE_COLUMNS = 3


def render_no_discrepancy_section(non_discrepancy_measures: List[str],
                                  total_measures: int) -> List[str]:
    """`## Measures with No Discrepancies`: the clean measures, several per row.

    As a bullet list this was the tallest thing in the report: 52 measures, one
    ~200-character line each, because the measure name appears once as text and
    again inside the link path. A 3-column grid cuts that by two thirds.

    Column-major, not row-major: alphabetical order runs *down* each column, so
    the list stays scannable like a phone book and the short final column stays
    the tail of the alphabet rather than an interleaved jump. Only the last
    column is padded.

    The measure name doubles as the CQL link label here (rather than the short
    `[cql]` used in the per-measure sections below, where the `####` heading has
    already named the measure). In a grid a bare `[cql]` identifies nothing.
    There is no `test` link: the engine's `{Measure}.txt` traces it pointed at
    were replaced by per-measure `TestCaseResult-*.json` directories, so every
    such link was a dead 404.
    """
    if not non_discrepancy_measures:
        return []

    def cell(measure: str) -> str:
        return cql_file_link(measure)

    column_count = NO_DISCREPANCY_TABLE_COLUMNS
    rows_needed = -(-len(non_discrepancy_measures) // column_count)
    columns = [non_discrepancy_measures[row * rows_needed:(row + 1) * rows_needed]
               for row in range(column_count)]

    lines = [f'## Measures with No Discrepancies '
             f'({len(non_discrepancy_measures)} of {total_measures})\n',
             '\n']
    lines.extend(create_markdown_table(
        [''] * column_count,
        [[cell(column[row]) if row < len(column) else ''
          for column in columns]
         for row in range(rows_needed)]))
    return lines


def capture_discrepancies_by_measure(expected_results: Dict[ResultKey, Dict[str, str]],
                                     actual_results: Dict[ResultKey, Dict[str, str]],
                                     resolved_keys: Set[ResultKey] = frozenset(),
                                     workaround_keys: Set[ResultKey] = frozenset()) -> Dict[str, MeasureDiscrepancy]:
    """Per-measure discrepancies, for measures that have any.

    ``resolved_keys`` still count toward ``all_test_cases`` but are not
    discrepancies. The report passes none, so a resolved failure stays listed,
    labelled with its issue.

    ``workaround_keys`` are matching groups whose issue says a workaround is
    applied. They are not mismatches either, but they are discrepancies in the
    sense that matters here -- an open defect the case would expose if the
    workaround were removed -- so a measure whose only qualifier is a workaround
    still appears under `## Measures with Discrepancies`.
    """
    def has_discrepancy(discrepancy: MeasureDiscrepancy) -> bool:
        return discrepancy.missing_populations or \
           discrepancy.missing_results or \
           discrepancy.mismatched_test_cases or \
           discrepancy.workarounds

    discrepancies = {}
    for expected_results_key, expected_populations in expected_results.items():
        measure_discrepancy = discrepancies.setdefault(expected_results_key.measure_name, MeasureDiscrepancy())
        measure_discrepancy.all_test_cases.append(expected_results_key.patient_guid)
        if expected_results_key in workaround_keys:
            measure_discrepancy.workarounds.append(expected_results_key)
            continue
        if expected_results_key in resolved_keys:
            continue
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


def ticket_link(ticket: str) -> str:
    """`[owner/repo#123](url)` for a GitHub ticket URL, `[FHIR-59691](url)` for
    a JIRA one; blank stays blank."""
    if not ticket:
        return ''
    if JIRA_TICKET_PATTERN.match(ticket):
        return f'[{ticket_number(ticket)}]({ticket})'
    owner, repo, _, number = ticket.split('/')[3:7]
    return f'[{owner}/{repo}#{number}]({ticket})'


def ticket_number(ticket: str) -> str:
    """`123` from a GitHub issue or pull request URL, `FHIR-59691` from an HL7
    JIRA URL; blank stays blank.

    The trailing path segment is the issue (or PR) number / the JIRA key, e.g.
    ``https://github.com/org/repo/issues/123`` or
    ``https://jira.hl7.org/browse/FHIR-59691``. ``load_known_issues`` rejects a
    ``ticket`` that is neither shape, so the shape is not in doubt here.
    """
    return ticket.rstrip('/').rsplit('/', 1)[-1] if ticket else ''


def sort_issue_ids(issue_ids) -> List[str]:
    """`I-9` before `I-26`: numeric order, not string order."""
    def key(issue_id: str):
        match = re.search(r'\d+', issue_id)
        return (int(match.group()) if match else float('inf'), issue_id)
    return sorted(issue_ids, key=key)


def covering_issue(key: ResultKey,
                   implementation_issues: Sequence[ImplementationIssue],
                   known_issues: Sequence[KnownIssue]):
    """(issue, status) for a failing group, or (None, None) when no issue covers it.

    ``status`` is ``implementation``, ``ticketed``, ``needs ticket`` or
    ``workaround reverted``; the first two resolve the group. An implementation
    issue takes precedence over a known issue, as in ``cell_outcome``.

    Only failing groups reach this function, so an issue with a
    ``workaround-applied`` status here means the workaround is *not* holding the
    group up -- it was reverted, or never worked. That is the more useful thing
    to say than whether the issue has a ticket yet.
    """
    issue = implementation_issue_for(key, implementation_issues)
    if issue is not None:
        return issue, "implementation"
    issue = implementation_issue_for(key, known_issues)
    if issue is not None:
        if issue.workaround_applied:
            return issue, "workaround reverted"
        return issue, "ticketed" if issue.ticketed else "needs ticket"
    return None, None


def render_measure_issue_notes(keys: Sequence[ResultKey],
                               implementation_issues: Sequence[ImplementationIssue],
                               known_issues: Sequence[KnownIssue]) -> List[str]:
    """The `Issues` list under a measure's tables: one bullet per issue it cites.

    Each bullet gives the issue's class, its status (implementation, the ticket,
    or **workaround applied**) and its note. Notes are written per test case, so
    an issue whose cases in this measure carry different notes gets one
    sub-bullet per note, naming the test cases (by GUID prefix) it applies to.

    ``keys`` may include matching workaround groups as well as failing ones, so
    an issue which only holds a passing case up is still listed here. The
    bullet's status is a property of the *issue*, not of any one key, so
    deriving it from ``covering_issue`` would mangle the bullet whenever a
    workaround-applied issue's first key processed is a matching group
    (``covering_issue`` reads every workaround-applied group as "reverted").
    The issue's own properties (``workaround_applied``, ``ticketed``, the
    ``implementation_issue_for`` lookup) are used instead. The bullet also
    drops ``(needs ticket)``: the per-row `Ticketed` column already says
    ``pending`` (or ``N/A``, for a class no ticket is owed), and the bullet's
    job here is the issue, not its row.
    """
    by_issue: Dict[str, Tuple[object, str, Dict[str, List[str]]]] = {}
    for key in sort_result_keys(list(keys)):
        impl = implementation_issue_for(key, implementation_issues)
        if impl is not None:
            issue = impl
            status = 'implementation'
        else:
            kn = implementation_issue_for(key, known_issues)
            if kn is None:
                continue
            issue = kn
            if kn.workaround_applied:
                status = 'workaround applied'
            elif kn.ticketed:
                status = 'ticketed'
            else:
                status = 'needs ticket'
        if issue.issue_id not in by_issue:
            by_issue[issue.issue_id] = (issue, status, {})
        _, _, notes = by_issue[issue.issue_id]
        guids = notes.setdefault(issue.note, [])
        if key.patient_guid not in guids:
            guids.append(key.patient_guid)
    if not by_issue:
        return []

    lines = ['Issues\n', '\n']
    for issue_id in sort_issue_ids(by_issue):
        issue, status, notes = by_issue[issue_id]
        if status == "implementation":
            detail = '`implementation`'
        elif status == "workaround applied":
            detail = f'`{issue.issue_class}`, **workaround applied**'
        elif status == "ticketed":
            detail = f'`{issue.issue_class}`, {ticket_link(issue.ticket)}'
        else:  # "needs ticket"
            detail = f'`{issue.issue_class}`'
        bullet = f'- **{issue_id}** ({detail})'
        if len(notes) == 1:
            note = next(iter(notes))
            lines.append(f'{bullet}: {note}\n' if note else f'{bullet}\n')
        else:
            lines.append(f'{bullet}\n')
            for note, guids in notes.items():
                prefixes = ', '.join(f'`{g[:8]}`' for g in guids)
                lines.append(f'  - {prefixes}: {note or "no note"}\n')
    lines.append('\n')
    return lines


def generate_comparison_report(file: str,
                               expected_results: Dict[ResultKey, Dict[str, str]],
                               actual_results: Dict[ResultKey, Dict[str, str]],
                               pass_count: int,
                               fail_count: int,
                               unscored_cells: List[UnscoredCell] = None,
                               cqfm_exclusions: Dict[str, FrozenSet[str]] = None,
                               implementation_issues: Sequence[ImplementationIssue] = (),
                               implementation_file: str = DEFAULT_IMPLEMENTATION_ISSUES_FILE,
                               implementation_count: int = 0,
                               known_issues: Sequence[KnownIssue] = (),
                               known_issues_file: str = DEFAULT_KNOWN_ISSUES_FILE,
                               known_issue_count: int = 0,
                               workaround_count: int = 0,
                               ticketed_coverage_count: int = 0,
                               ticketed_workaround_count: int = 0):
    """Write ``discrepancy_report.md``.

    ``pass_count`` / ``fail_count`` / ``implementation_count`` /
    ``known_issue_count`` / ``workaround_count`` are test-case counts from
    ``scores``, ``implementation_case_count``, ``known_issue_case_count`` and
    ``workaround_case_count``; the five together are the total. Workaround cases
    are deliberately in neither the pass nor the fail count: they match their
    fixture, but only because the CQL works around an open defect.

    ``ticketed_coverage_count`` (from ``ticketed_known_issue_coverage_count``)
    and its ``ticketed_workaround_count`` subset are cross-cutting rather than
    part of that partition: they count cases a ticketed known issue covers
    whichever way ``cell_outcome`` scores them, so the header can report the
    ticketed half of the workaround cases that a single verdict would drop.
    """
    resolved_keys = failing_implementation_keys(expected_results, actual_results,
                                                implementation_issues)
    ticketed_keys = failing_known_issue_keys(expected_results, actual_results,
                                             known_issues, implementation_issues)
    awaiting_keys = failing_known_issue_keys(expected_results, actual_results,
                                             known_issues, implementation_issues,
                                             ticketed=False)

    def awaiting_class(key: ResultKey) -> str:
        issue, _ = covering_issue(key, implementation_issues, known_issues)
        return issue.issue_class if issue is not None else ''

    # An unticketed failing case means different things by class: an engine or
    # translator defect is waiting on a ticket we intend to file, while a
    # content/fixture/harness defect never gets one (the report says ``N/A``
    # beside it). Keep the two apart so the header does not call the second
    # "needs ticket".
    awaiting_ticket_keys = [k for k in awaiting_keys
                            if awaiting_class(k) in TICKETABLE_CLASSES]
    awaiting_no_ticket_keys = [k for k in awaiting_keys
                               if awaiting_class(k) not in TICKETABLE_CLASSES]
    # Groups that match only because a workaround is applied. Not mismatches, but
    # the open defect behind them must stay in the report.
    workaround_key_set = workaround_keys(expected_results, actual_results, known_issues)
    # Every mismatching group, whatever its issue state. Resolved ones stay in
    # the tables, labelled with the issue that resolves them.
    discrepancies = capture_discrepancies_by_measure(expected_results, actual_results,
                                                     workaround_keys=workaround_key_set)
    resolved = resolved_keys | ticketed_keys
    covered = resolved | awaiting_keys
    awaiting_ticket_case_count = len({(k.measure_name, k.patient_guid)
                                      for k in awaiting_ticket_keys})
    awaiting_no_ticket_case_count = len({(k.measure_name, k.patient_guid)
                                         for k in awaiting_no_ticket_keys})

    def discrepancy_keys(measure: str, discrepancy: MeasureDiscrepancy) -> List[ResultKey]:
        return (list(discrepancy.missing_results)
                + [mp.result_key for mp in discrepancy.missing_populations]
                + [ResultKey(measure, t.patient_guid, t.group)
                   for t in discrepancy.mismatched_test_cases])

    measure_keys = {measure: discrepancy_keys(measure, d) for measure, d in discrepancies.items()}
    # Unattributed: test cases with a group no implementation issue or ticketed
    # known issue resolves -- the FAIL verdict.
    unattributed_cases = {measure: {k.patient_guid for k in keys if k not in resolved}
                          for measure, keys in measure_keys.items()}

    def issue_cell(key: ResultKey) -> str:
        """``I-73 (implementation)``, ``I-78 (workaround reverted)``, a bare
        ``I-26`` / ``I-65`` for a known issue, or blank.

        The parenthetical qualifier only stays when it says something the
        `Ticketed` column beside it cannot say: ``(implementation)`` names the
        issue class (steward data vs. upstream defect) and
        ``(workaround reverted)`` says the case is failing again. The ``ticketed``
        and ``needs ticket`` qualifiers used to live here too, but they restate
        what the `Ticketed` column already shows (the ticket number, ``pending``,
        or ``N/A``), so a known issue's cell is now just its id.
        """
        issue, status = covering_issue(key, implementation_issues, known_issues)
        if issue is None:
            return ''
        if status in ("ticketed", "needs ticket"):
            return issue.issue_id
        return f'{issue.issue_id} ({status})'

    def workaround_issue_cell(key: ResultKey) -> str:
        """`I-78 (workaround applied)`, or blank.

        Unlike ``issue_cell`` this is for a *matching* group, so the status is
        fixed: ``covering_issue`` describes failing groups, and would report a
        workaround-applied issue as reverted here.
        """
        issue = implementation_issue_for(key, known_issues)
        return f'{issue.issue_id} (workaround applied)' if issue is not None else ''

    def ticketed_cell(key: ResultKey) -> str:
        """`pending`, `N/A`, a link to the upstream ticket, or blank.

        Blank means the row has no issue, matching the ``Issue`` cell next to it.
        A recorded ticket -- GitHub issue/PR or HL7 JIRA -- always renders as a
        markdown link, whichever class the issue is in: a vendored-library
        defect (e.g. I-63's FHIRCommon ticket) is tracked upstream even though
        no ticket is *owed* for the class. ``N/A`` therefore means the issue has
        no ticket and its class is outside ``TICKETABLE_CLASSES`` (neither
        ``engine`` nor ``translator``): the root cause is our own content,
        fixture, or harness, so nothing an upstream ticket could track is
        expected. Inside ``TICKETABLE_CLASSES`` an issue without a ticket reads
        ``pending``: an upstream defect still waiting to be filed.

        Deliberately does not use ``covering_issue``: that describes *failing*
        groups, so a matching workaround group would come back as
        ``workaround reverted``. Only the ticket matters here, so the two issue
        lists are consulted directly, in the precedence ``covering_issue`` uses.
        """
        if implementation_issue_for(key, implementation_issues) is not None:
            return 'N/A'
        issue = implementation_issue_for(key, known_issues)
        if issue is None:
            return ''
        if issue.ticket:
            return f'[{ticket_number(issue.ticket)}]({issue.ticket})'
        if issue.issue_class not in TICKETABLE_CLASSES:
            return 'N/A'
        return 'pending'

    def workaround_notes(keys: Sequence[ResultKey]) -> List[str]:
        """Distinct notes of the issues holding the given passing groups up."""
        notes: List[str] = []
        for key in sort_result_keys(list(keys)):
            issue = implementation_issue_for(key, known_issues)
            if issue is not None and issue.note and issue.note not in notes:
                notes.append(issue.note)
        return notes

    total_cases = (pass_count + fail_count + implementation_count
                   + known_issue_count + workaround_count)

    with open(file, "w", newline="") as f:
        f.write('# Discrepancy Report\n')
        total_measures = len(set([k.measure_name for k in expected_results.keys()]))
        def count_with_pct(count: int) -> str:
            return f'{count} ({count / total_cases * 100:.2f}%)' if total_cases else '0'

        detail_rows = [
            ['Generated', datetime.now()],
            ['Total Measures', total_measures],
            ['Total Test Cases', total_cases],
            ['Measures with Discrepancies', len(discrepancies)],
            ['Pass Count', count_with_pct(pass_count)],
        ]
        if workaround_count:
            detail_rows.append(['Workaround Count', count_with_pct(workaround_count)])
            if ticketed_workaround_count:
                detail_rows.append(['&nbsp;&nbsp;— covered by a ticketed known issue',
                                    count_with_pct(ticketed_workaround_count)])
        if implementation_count:
            detail_rows.append(['Implementation Issue Count', count_with_pct(implementation_count)])
        if known_issue_count:
            detail_rows.append(['Known Issue Count (ticketed)', count_with_pct(known_issue_count)])
        detail_rows.append(['Fail Count', count_with_pct(fail_count)])
        if awaiting_ticket_case_count:
            detail_rows.append(['&nbsp;&nbsp;— known issue, needs ticket',
                                count_with_pct(awaiting_ticket_case_count)])
        if awaiting_no_ticket_case_count:
            detail_rows.append(['&nbsp;&nbsp;— known issue, no ticket expected',
                                count_with_pct(awaiting_no_ticket_case_count)])
        if ticketed_coverage_count:
            detail_rows.append(['Known issues with an upstream ticket',
                                count_with_pct(ticketed_coverage_count)])
        resolved_parts = [name for name, count in (('Implementation', implementation_count),
                                                    ('Known Issue', known_issue_count))
                          if count]
        if resolved_parts or workaround_count:
            detail_rows.append([f'Resolved without workaround ({" + ".join(["Pass"] + resolved_parts)})',
                                count_with_pct(pass_count + implementation_count
                                               + known_issue_count)])
        f.writelines(create_markdown_table(['Details', 'Value'], detail_rows))
        # Spell out the buckets so "Resolved" is not misread as "everything but Fail".
        buckets = [f'{pass_count} Pass']
        buckets += [f'{count} {name}' for name, count in (
            ('Implementation', implementation_count),
            ('Known Issue', known_issue_count),
            ('Workaround', workaround_count)) if count]
        buckets.append(f'{fail_count} Fail')
        f.write(f'_Every test case is in exactly one bucket: {" + ".join(buckets)} = '
                f'{total_cases}. Resolved without workaround counts Pass, Implementation '
                '(the steward\'s test case is wrong; the CQL is right) and Known Issue (an '
                'engine or translator defect with an upstream ticket). Workaround cases are '
                'left out because they match only through CQL that works around an open '
                'issue, so each needs re-checking once its workaround is removed._\n\n')
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
                ],
                [
                    'Workarounds',
                    len(set([m for m, d in discrepancies.items() if d.workarounds])),
                    sum([len(d.workarounds) for d in discrepancies.values()])
                ],
                [
                    'Unattributed Discrepancies',
                    sum(1 for cases in unattributed_cases.values() if cases),
                    sum(len(cases) for cases in unattributed_cases.values())
                ]
            ],
            '|---|:---:|:---:|\n'))
        f.write('\n')
        f.write('_Note: Measures can have multiple discrepancies, so the Measures with '
                'Discrepancies count may not match the summary counts. Unattributed '
                'Discrepancies are those no implementation issue or ticketed known issue '
                'resolves. Workarounds are test cases that match their fixture only because '
                'the CQL works around an open issue: they count as neither a pass nor a '
                'failure, and the workaround is removed once the root cause is fixed._\n')
        f.write('\n')

        f.writelines(render_cqfm_exclusions_section(cqfm_exclusions or {},
                                                    unscored_cells or []))

        f.writelines(render_i28_workaround_note_section(
            measures_with_cql_marker(I28_MARKER)))

        non_discrepancy_measures = [
            m for m in sort_measure_names(list(set([k.measure_name for k in expected_results.keys()])))
            if m not in discrepancies]
        f.writelines(render_no_discrepancy_section(
            non_discrepancy_measures, total_measures))

        if discrepancies:
            f.write(f'## Measures with Discrepancies '
                    f'({len(discrepancies)} of {total_measures})\n')
            f.write('\n')
            f.write('_Every measure with a test case that doesn\'t match its fixture '
                    'MeasureReport, or that matches only because the CQL works around an '
                    'open issue. The `Issue` column names the issue that explains a '
                    'test case: `I-XX (implementation)` is the measure steward\'s test '
                    'data or expectation (see `defect-tracking/known-issues.md`), and '
                    '`I-XX (workaround reverted)` means the case is failing again. Any '
                    'other `I-XX` is a known issue, and the `Ticketed` column beside it '
                    'says whether a ticket is owed: `N/A` for an implementation issue '
                    'or a defect in our own content, fixture, or harness (nothing an '
                    'upstream ticket tracks), `pending` for an engine/translator defect '
                    'whose ticket is not filed yet, and a link to it once one is. A '
                    'test case nothing resolves is counted as Unattributed._\n')
            f.write('\n')
            summary_headers = ['Measure', 'Total Test Cases', 'Missing Results',
                               'Missing Populations', 'Mismatched Test Cases', 'Workarounds',
                               'Unattributed']
            summary_separator = '|---|:---:|:---:|:---:|:---:|:---:|:---:|\n'
            summary_rows = []
            for measure, discrepancy in discrepancies.items():
                row = [
                    f'[{measure}](#{measure.lower()})',
                    len(discrepancy.all_test_cases),
                    len(discrepancy.missing_results),
                    len(discrepancy.missing_populations),
                    f'{len(discrepancy.mismatched_test_cases)/len(discrepancy.all_test_cases)*100:.2f}%   '
                    f'({len(discrepancy.mismatched_test_cases)})',
                    len(discrepancy.workarounds),
                    len(unattributed_cases[measure])
                ]
                summary_rows.append(row)
            f.writelines(create_markdown_table(summary_headers, summary_rows,
                                               summary_separator))
            f.write('\n')

            for measure, discrepancy in discrepancies.items():
                f.write(f'#### {measure}\n')
                f.write(f'{cql_file_link(measure, "[cql]")} '
                        f'{test_results_file_link(measure, "[test results]")}\n\n')
                # The column appears only on measures with a row an issue covers.
                show_issue = any(k in covered for k in measure_keys[measure])

                if discrepancy.missing_results:
                    f.write(f'Missing Results ({len(discrepancy.missing_results)} of '
                            f'{len(discrepancy.all_test_cases)} test cases)\n')
                    missing_results_headers = ['Test Case', 'Group']
                    if show_issue:
                        missing_results_headers += ['Issue', 'Ticketed']
                    missing_results_rows = []
                    for missing_key in sort_result_keys(list(discrepancy.missing_results)):
                        row = [measure_report_file_link(missing_key.measure_name,
                                                        missing_key.patient_guid),
                               missing_key.group]
                        if show_issue:
                            row += [issue_cell(missing_key), ticketed_cell(missing_key)]
                        missing_results_rows.append(row)
                    f.writelines(create_markdown_table(
                        missing_results_headers, missing_results_rows))

                if discrepancy.missing_populations:
                    f.write(f'Missing Populations ({len(discrepancy.missing_populations)} of '
                            f'{len(discrepancy.all_test_cases)} test cases)\n')
                    f.writelines(create_markdown_table(
                        ['Test Case', 'Group', 'Population']
                        + (['Issue', 'Ticketed'] if show_issue else []),
                        [[
                            measure_report_file_link(missing_id.measure_name, missing_id.patient_guid),
                            missing_id.group,
                            ','.join(populations)
                        ] + ([issue_cell(missing_id), ticketed_cell(missing_id)]
                             if show_issue else [])
                            for (missing_id, populations) in sort_missing_populations(
                            list(discrepancy.missing_populations))]))

                if discrepancy.mismatched_test_cases:
                    f.write(f'Mismatched Test Cases ({len(discrepancy.mismatched_test_cases)} of '
                            f'{len(discrepancy.all_test_cases)})\n')
                    mismatched_headers = ['Test Case', 'Group', 'Population', 'Expected', 'Actual']
                    mismatched_separator = '|---|---|---|:---:|:---:|'
                    if show_issue:
                        mismatched_headers += ['Issue', 'Ticketed']
                        mismatched_separator += '---|---|'
                    mismatched_separator += '\n'
                    mismatched_rows = []
                    for test_group_id, populations in sort_mismatched_test_cases(
                            discrepancy.mismatched_test_cases):
                        ordered = sort_populations(populations.keys())
                        row = [
                            measure_report_file_link(measure, test_group_id.patient_guid),
                            test_group_id.group,
                            '<br>'.join(ordered),
                            '<br>'.join([populations[p].expected for p in ordered]),
                            '<br>'.join([populations[p].actual for p in ordered])]
                        if show_issue:
                            key = ResultKey(
                                measure, test_group_id.patient_guid, test_group_id.group)
                            row += [issue_cell(key), ticketed_cell(key)]
                        mismatched_rows.append(row)
                    f.writelines(create_markdown_table(
                        mismatched_headers, mismatched_rows, mismatched_separator))

                if discrepancy.workarounds:
                    f.write(f'Workarounds ({len(discrepancy.workarounds)} of '
                            f'{len(discrepancy.all_test_cases)} test cases)\n')
                    f.write('_These cases match their fixture only because the measure\'s '
                            'CQL works around an open issue. Removing the workaround makes '
                            'them fail again, so they count as neither a pass nor a '
                            'failure._\n')
                    for note in workaround_notes(discrepancy.workarounds):
                        f.write(f'_{note}_\n')
                    f.write('\n')
                    f.writelines(create_markdown_table(
                        ['Test Case', 'Group', 'Issue', 'Ticketed'],
                        [[measure_report_file_link(w.measure_name, w.patient_guid),
                          w.group, workaround_issue_cell(w), ticketed_cell(w)]
                         for w in sort_result_keys(list(discrepancy.workarounds))]))

                # Workaround groups are included so their issue is listed here too:
                # only the `implementation` branch reads the status, so a matching
                # group renders the usual class/ticket/note bullet.
                f.writelines(render_measure_issue_notes(
                    measure_keys[measure] + list(discrepancy.workarounds),
                    implementation_issues, known_issues))
                f.write('\n')

        f.write('\n_Known issues are listed in '
                '`defect-tracking/known-issues.md`; the test cases they explain, '
                f'and their tickets, in `{known_issues_file}` and '
                f'`{implementation_file}`._\n')


def main(expected_file: str, actual_file: str, output_file: str,
         comparison_report: str, measure_resource_dir: str = None,
         implementation_file: str = DEFAULT_IMPLEMENTATION_ISSUES_FILE,
         known_issues_file: str = DEFAULT_KNOWN_ISSUES_FILE):
    # Exclusions are computed once and applied symmetrically to expected and
    # actual, so a cell is either scored on both sides or neither.
    cqfm_exclusions = load_cqfm_aggregation_exclusions(
        measure_resource_dir or DEFAULT_MEASURE_RESOURCE_DIR)

    expected_results = capture_results(expected_file, cqfm_exclusions)
    actual_results = capture_results(actual_file, cqfm_exclusions)

    implementation_issues = load_implementation_issues(implementation_file)
    print(f"Implementation issues: {len(implementation_issues)} "
          f"from {implementation_file!r}")

    known_issues = load_known_issues(known_issues_file)
    print(f"Known issues: {len(known_issues)} case rows "
          f"({sum(1 for i in known_issues if i.ticketed)} ticketed, "
          f"{sum(1 for i in known_issues if i.workaround_applied)} workaround) "
          f"from {known_issues_file!r}")

    pass_count, fail_count = generate_output(output_file, expected_results.rows,
                                             actual_results.rows, implementation_issues,
                                             known_issues)
    implementation_count = implementation_case_count(
        expected_results.rows, actual_results.rows, implementation_issues, known_issues)
    known_count = known_issue_case_count(
        expected_results.rows, actual_results.rows, implementation_issues, known_issues)
    workaround_count = workaround_case_count(
        expected_results.rows, actual_results.rows, implementation_issues, known_issues)
    ticketed_coverage_count = ticketed_known_issue_coverage_count(
        expected_results.rows, actual_results.rows, implementation_issues, known_issues)
    ticketed_workaround_count = ticketed_workaround_case_count(
        expected_results.rows, actual_results.rows, implementation_issues, known_issues)
    total = (pass_count + fail_count + implementation_count + known_count
             + workaround_count)

    def pct(count: int) -> str:
        return f"{(count / total * 100) if total else 0.0:.2f}%"

    print(f"PASS (test cases): {pass_count} ({pct(pass_count)})")
    if implementation_count:
        print(f"IMPLEMENTATION (test cases): {implementation_count} ({pct(implementation_count)})")
    if known_count:
        print(f"KNOWN_ISSUE (test cases): {known_count} ({pct(known_count)})")
    if workaround_count:
        print(f"WORKAROUND (test cases): {workaround_count} ({pct(workaround_count)})")
        if ticketed_workaround_count:
            print(f"  covered by a ticketed known issue: {ticketed_workaround_count}")
    print(f"FAIL (test cases): {fail_count} ({pct(fail_count)})")
    if ticketed_coverage_count:
        print(f"Known issues with an upstream ticket (test cases): "
              f"{ticketed_coverage_count} ({pct(ticketed_coverage_count)})")

    unscored = list(expected_results.unscored) + list(actual_results.unscored)
    generate_comparison_report(comparison_report, expected_results.groups,
                               actual_results.groups, pass_count, fail_count,
                               unscored_cells=unscored,
                               cqfm_exclusions=cqfm_exclusions,
                               implementation_issues=implementation_issues,
                               implementation_file=implementation_file,
                               implementation_count=implementation_count,
                               known_issues=known_issues,
                               known_issues_file=known_issues_file,
                               known_issue_count=known_count,
                               workaround_count=workaround_count,
                               ticketed_coverage_count=ticketed_coverage_count,
                               ticketed_workaround_count=ticketed_workaround_count)


def parse_args(argv: List[str]) -> Tuple[str, str, str, str, Optional[str]]:
    """Map `argv` (without the program name) to main()'s arguments.

    Returns (expected, actual, output, report, measure_resource_dir).

    The flag is removed from the positional list, so the two kinds of argument can
    appear in any order. Values pass through verbatim -- no URI conversion, no
    path normalisation -- because Windows and POSIX callers both use this and
    `open()` handles either spelling.
    """
    args = list(argv)
    measure_resource_dir = None

    flag = "--measure-resource-dir"
    if flag in args:
        idx = args.index(flag)
        if idx + 1 < len(args):
            measure_resource_dir = args[idx + 1]
        args = args[:idx] + args[idx + 2:]

    defaults = ["./scripts/comparison/expected_results.csv",
                "./scripts/comparison/actual_results.csv",
                "./scripts/comparison/output_results.csv",
                "./scripts/comparison/discrepancy_report.md"]
    positional = (args + defaults[len(args):])[:4]
    return (positional[0], positional[1], positional[2], positional[3],
            measure_resource_dir)


if __name__ == '__main__':
    (expected_file, actual_file, output_file, comparison_report,
     measure_resource_dir) = parse_args(sys.argv[1:])

    main(expected_file, actual_file, output_file, comparison_report,
         measure_resource_dir=measure_resource_dir)
