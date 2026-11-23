"""Tests for scoring test cases explained by a ticketed known issue.

A failing case explained by a catalogued issue (`defect-tracking/known-issues.md`)
is listed in `known_issues.csv`. It counts as resolved only once its issue has a
GitHub ticket: its failing cells then score KNOWN_ISSUE instead of FAIL. Without
a ticket the case stays FAIL and the report labels it as needing one -- but only
for an engine/translator defect, where an upstream ticket is the right tracker.
A known issue in any other class (our content, fixture, harness, ...) reads N/A
instead: nothing upstream tracks it, so no ticket is owed and `pending` would
mislead.

A row also carries the issue's `status`. When that is `workaround-applied` the
measure's CQL already works around the defect, so the case is *expected to pass*
and a matching cell scores WORKAROUND: a passing case that still counts as a
discrepancy, because the defect is open and the workaround is to be reverted.

These tests pin those rules, the loader's validation, and the report rendering.
"""
import csv
import os
import shutil
import tempfile
import unittest

from scripts.compare_results import (
    IMPLEMENTATION,
    KNOWN_ISSUE,
    WORKAROUND,
    ImplementationIssue,
    KnownIssue,
    capture_results,
    cell_outcome,
    failing_known_issue_keys,
    known_issue_case_count,
    load_known_issues,
    main,
    scores,
    sort_issue_ids,
    ticket_link,
    ticket_number,
    ticketed_known_issue_cases,
    ticketed_known_issue_coverage_count,
    ticketed_workaround_case_count,
    workaround_case_count,
    workaround_keys,
)
# Imported under another name: pytest would collect a bare `test_case_outcomes`.
from scripts.compare_results import test_case_outcomes as case_outcomes

MEASURE = "CMS999FHIRTestMeasure"
GUID_A = "aaaaaaaa-1111-4111-8111-aaaaaaaaaaaa"
GUID_B = "bbbbbbbb-2222-4222-8222-bbbbbbbbbbbb"
GUID_C = "cccccccc-3333-4333-8333-cccccccccccc"
TICKET = "https://github.com/cqframework/clinical_quality_language/issues/1855"

CSV_HEADER = "measure_name,guid,population,count\n"
KNOWN_HEADER = "issue_id,class,ticket,measure_name,guid,group,note\n"
KNOWN_HEADER_STATUS = "issue_id,class,status,ticket,measure_name,guid,group,note\n"
IMPL_HEADER = "issue_id,measure_name,guid,group,note\n"


def _csv(*rows):
    return CSV_HEADER + "".join(f"{r}\n" for r in rows)


def _known(guid, ticket=TICKET, group="", issue_id="I-26", issue_class="engine",
           status="confirmed"):
    """One `KnownIssue`; `status` defaults to a non-workaround so existing cases
    keep their old verdicts."""
    return KnownIssue(issue_id, issue_class, status, ticket, MEASURE, guid, group,
                      "Engine note.")


class KnownIssueLoaderTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)

    def _load(self, text):
        path = os.path.join(self.tmp, "known.csv")
        with open(path, "w", newline="") as f:
            f.write(text)
        return load_known_issues(path)

    def test_absent_file_means_no_issues(self):
        self.assertEqual(load_known_issues(os.path.join(self.tmp, "none.csv")), [])
        self.assertEqual(load_known_issues(None), [])

    def test_reads_ticketed_and_unticketed_rows(self):
        issues = self._load(KNOWN_HEADER
                            + f"I-18,translator,{TICKET},{MEASURE},{GUID_A},,\n"
                            + f'I-26,engine,,{MEASURE},{GUID_B},Group_1,"Reference, not code."\n')
        self.assertEqual([(i.issue_id, i.ticketed, i.group, i.note) for i in issues],
                         [("I-18", True, "", ""),
                          ("I-26", False, "Group_1", "Reference, not code.")])

    def test_pull_request_url_is_a_ticket(self):
        url = "https://github.com/cqframework/clinical_quality_language/pull/1857"
        issues = self._load(KNOWN_HEADER + f"I-69,engine,{url},{MEASURE},{GUID_A},,\n")
        self.assertTrue(issues[0].ticketed)

    def test_placeholder_ticket_is_rejected(self):
        for ticket in ("TBD", "#1855", "https://example.com/issues/1",
                       "https://github.com/cqframework/clinical_quality_language"):
            with self.subTest(ticket=ticket), self.assertRaisesRegex(ValueError, "GitHub"):
                self._load(KNOWN_HEADER + f"I-26,engine,{ticket},{MEASURE},{GUID_A},,\n")

    def test_implementation_class_points_to_its_own_file(self):
        with self.assertRaisesRegex(ValueError, "implementation_issues.csv"):
            self._load(KNOWN_HEADER + f"I-73,implementation,,{MEASURE},{GUID_A},,\n")

    def test_unknown_class_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "not one of"):
            self._load(KNOWN_HEADER + f"I-26,runtime,,{MEASURE},{GUID_A},,\n")

    def test_rows_of_one_issue_must_share_the_ticket(self):
        with self.assertRaisesRegex(ValueError, "I-26 rows disagree"):
            self._load(KNOWN_HEADER
                       + f"I-26,engine,{TICKET},{MEASURE},{GUID_A},,\n"
                       + f"I-26,engine,,{MEASURE},{GUID_B},,\n")

    def test_status_column_marks_a_workaround(self):
        issues = self._load(KNOWN_HEADER_STATUS
                            + f"I-78,translator,workaround-applied,{TICKET},{MEASURE},"
                              f"{GUID_A},,Cast applied.\n")
        self.assertEqual(issues[0].status, "workaround-applied")
        self.assertTrue(issues[0].workaround_applied)

    def test_status_is_optional_and_empty_by_default(self):
        issues = self._load(KNOWN_HEADER + f"I-26,engine,{TICKET},{MEASURE},{GUID_A},,\n")
        self.assertEqual(issues[0].status, "")
        self.assertFalse(issues[0].workaround_applied)

    def test_rows_of_one_issue_must_share_the_status(self):
        with self.assertRaisesRegex(ValueError, "I-78 rows disagree"):
            self._load(KNOWN_HEADER_STATUS
                       + f"I-78,translator,workaround-applied,{TICKET},{MEASURE},"
                         f"{GUID_A},,\n"
                       + f"I-78,translator,confirmed,{TICKET},{MEASURE},{GUID_B},,\n")

    def test_missing_column_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing column.*ticket"):
            self._load(IMPL_HEADER + f"I-26,{MEASURE},{GUID_A},,\n")

    def test_unquoted_comma_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "more fields than columns"):
            self._load(KNOWN_HEADER + f"I-26,engine,,{MEASURE},{GUID_A},,a,b\n")


class KnownIssueScoringTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)

    def _rows(self, *rows):
        path = os.path.join(self.tmp, f"{len(os.listdir(self.tmp))}.csv")
        with open(path, "w", newline="") as f:
            f.write(_csv(*rows))
        return capture_results(path)

    def test_ticketed_failing_cell_scores_known_issue(self):
        key = (MEASURE, GUID_A, "Group_1:Denominator")
        self.assertEqual(cell_outcome(key, "1", None, (), [_known(GUID_A)]),
                         (KNOWN_ISSUE, "MISSING"))

    def test_unticketed_failing_cell_stays_fail(self):
        key = (MEASURE, GUID_A, "Group_1:Denominator")
        self.assertEqual(cell_outcome(key, "1", "0", (), [_known(GUID_A, ticket="")]),
                         ("FAIL", "0"))

    def test_passing_cell_stays_pass(self):
        key = (MEASURE, GUID_A, "Group_1:Denominator")
        self.assertEqual(cell_outcome(key, "1", "1", (), [_known(GUID_A)]), ("PASS", "1"))

    def test_matching_cell_under_a_workaround_scores_workaround(self):
        key = (MEASURE, GUID_A, "Group_1:Denominator")
        known = [_known(GUID_A, issue_id="I-78", issue_class="translator",
                        status="workaround-applied")]
        self.assertEqual(cell_outcome(key, "1", "1", (), known), (WORKAROUND, "1"))

    def test_failing_cell_under_a_reverted_workaround_is_not_a_workaround(self):
        key = (MEASURE, GUID_A, "Group_1:Denominator")
        known = [_known(GUID_A, ticket="", issue_id="I-78", issue_class="translator",
                        status="workaround-applied")]
        self.assertEqual(cell_outcome(key, "1", "0", (), known), ("FAIL", "0"))

    def test_implementation_issue_takes_precedence(self):
        key = (MEASURE, GUID_A, "Group_1:Denominator")
        impl = [ImplementationIssue("I-73", MEASURE, GUID_A, "", "")]
        self.assertEqual(cell_outcome(key, "1", "0", impl, [_known(GUID_A)])[0],
                         IMPLEMENTATION)

    def test_case_outcomes_and_counts(self):
        # GUID_A: ticketed -> KNOWN_ISSUE. GUID_B: unticketed -> FAIL.
        # GUID_C: Group_1 implementation, Group_2 ticketed -> KNOWN_ISSUE.
        expected = self._rows(
            f"{MEASURE},{GUID_A},Group_1:Denominator,1",
            f"{MEASURE},{GUID_B},Group_1:Denominator,1",
            f"{MEASURE},{GUID_C},Group_1:Denominator,1",
            f"{MEASURE},{GUID_C},Group_2:Denominator,1")
        actual = self._rows(
            f"{MEASURE},{GUID_A},Group_1:Denominator,0",
            f"{MEASURE},{GUID_B},Group_1:Denominator,0",
            f"{MEASURE},{GUID_C},Group_1:Denominator,0",
            f"{MEASURE},{GUID_C},Group_2:Denominator,0")
        impl = [ImplementationIssue("I-73", MEASURE, GUID_C, "Group_1", "")]
        known = [_known(GUID_A), _known(GUID_C, group="Group_2"),
                 _known(GUID_B, ticket="", issue_id="I-63")]
        self.assertEqual(case_outcomes(expected.rows, actual.rows, impl, known), {
            (MEASURE, GUID_A): KNOWN_ISSUE,
            (MEASURE, GUID_B): "FAIL",
            (MEASURE, GUID_C): KNOWN_ISSUE,
        })
        self.assertEqual(scores(expected.rows, actual.rows, impl, known), (0, 1))
        self.assertEqual(known_issue_case_count(expected.rows, actual.rows, impl, known), 2)
        self.assertEqual(
            {(k.patient_guid, k.group) for k in
             failing_known_issue_keys(expected.groups, actual.groups, known, impl)},
            {(GUID_A, "Group_1"), (GUID_C, "Group_2")})
        self.assertEqual(
            {(k.patient_guid, k.group) for k in
             failing_known_issue_keys(expected.groups, actual.groups, known, impl,
                                      ticketed=False)},
            {(GUID_B, "Group_1")})

    def test_workaround_case_is_in_neither_count(self):
        # GUID_A passes only because of the workaround; GUID_B just passes.
        expected = self._rows(
            f"{MEASURE},{GUID_A},Group_1:Denominator,1",
            f"{MEASURE},{GUID_B},Group_1:Denominator,1")
        actual = self._rows(
            f"{MEASURE},{GUID_A},Group_1:Denominator,1",
            f"{MEASURE},{GUID_B},Group_1:Denominator,1")
        known = [_known(GUID_A, issue_id="I-78", issue_class="translator",
                        status="workaround-applied")]
        self.assertEqual(case_outcomes(expected.rows, actual.rows, (), known), {
            (MEASURE, GUID_A): WORKAROUND,
            (MEASURE, GUID_B): "PASS",
        })
        self.assertEqual(scores(expected.rows, actual.rows, (), known), (1, 0))
        self.assertEqual(workaround_case_count(expected.rows, actual.rows, (), known), 1)
        self.assertEqual(
            {(k.patient_guid, k.group) for k in
             workaround_keys(expected.groups, actual.groups, known)},
            {(GUID_A, "Group_1")})

    def test_workaround_keys_need_a_matching_case(self):
        expected = self._rows(f"{MEASURE},{GUID_A},Group_1:Denominator,1")
        actual = self._rows(f"{MEASURE},{GUID_A},Group_1:Denominator,0")
        known = [_known(GUID_A, issue_id="I-78", issue_class="translator",
                        status="workaround-applied")]
        self.assertEqual(workaround_keys(expected.groups, actual.groups, known), set())


class KnownIssueReportTest(unittest.TestCase):
    """End to end through main(), with no implementation issues."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)

    def _write(self, name, text):
        path = os.path.join(self.tmp, name)
        with open(path, "w", newline="") as f:
            f.write(text)
        return path

    def _run(self, expected_rows, actual_rows, known_text):
        e = self._write("e.csv", _csv(*expected_rows))
        a = self._write("a.csv", _csv(*actual_rows))
        known = self._write("known.csv", known_text)
        self.output = os.path.join(self.tmp, "o.csv")
        report = os.path.join(self.tmp, "r.md")
        main(e, a, self.output, report, measure_resource_dir=self.tmp,
             implementation_file=os.path.join(self.tmp, "no-impl.csv"),
             known_issues_file=known)
        with open(report) as f:
            return f.read()

    def test_ticketed_issue_resolves_the_case(self):
        text = self._run(
            [f"{MEASURE},{GUID_A},Group_1:Denominator,1",
             f"{MEASURE},{GUID_B},Group_1:Denominator,1"],
            [f"{MEASURE},{GUID_B},Group_1:Denominator,1"],
            KNOWN_HEADER + f"I-18,translator,{TICKET},{MEASURE},{GUID_A},,Overload ambiguity.\n")
        self.assertIn("| Known Issue Count (ticketed) | 1 (50.00%) |", text)
        self.assertIn("| Fail Count | 0 (0.00%) |", text)
        self.assertIn("| Resolved without workaround (Pass + Known Issue) | 2 (100.00%) |", text)
        self.assertIn("_Every test case is in exactly one bucket: "
                      "1 Pass + 1 Known Issue + 0 Fail = 2.", text)
        self.assertNotIn("(needs ticket)", text)
        self.assertNotIn("## Known Issues", text)
        # Still listed, labelled as resolved by its ticketed issue.
        self.assertIn("| Measures with Discrepancies | 1 |", text)
        self.assertIn("| Unattributed Discrepancies | 0 | 0 |", text)
        self.assertIn(f"| {GUID_A} | Group_1 | I-18 | [1855]({TICKET}) |", text)
        self.assertIn("- **I-18** (`translator`, "
                      f"[cqframework/clinical_quality_language#1855]({TICKET})): "
                      "Overload ambiguity.\n", text)
        with open(self.output, newline="") as f:
            results = {r["guid"]: r["result"] for r in csv.DictReader(f)}
        self.assertEqual(results, {GUID_A: KNOWN_ISSUE, GUID_B: "PASS"})

    def test_unticketed_issue_stays_failing_and_is_labelled(self):
        text = self._run(
            [f"{MEASURE},{GUID_A},Group_1:Denominator,1",
             f"{MEASURE},{GUID_B},Group_1:Denominator,1",
             f"{MEASURE},{GUID_C},Group_1:Denominator,1"],
            [f"{MEASURE},{GUID_B},Group_1:Denominator,0",
             f"{MEASURE},{GUID_C},Group_1:Denominator,0"],
            KNOWN_HEADER + f"I-26,engine,,{MEASURE},{GUID_A},,\n"
            + f"I-26,engine,,{MEASURE},{GUID_B},,\n")
        self.assertIn("| Fail Count | 3 (100.00%) |", text)
        self.assertIn("| &nbsp;&nbsp;— known issue, needs ticket | 2 (66.67%) |", text)
        self.assertNotIn("Known Issue Count (ticketed)", text)
        self.assertNotIn("| Resolved without workaround", text)
        self.assertIn("| Unattributed Discrepancies | 1 | 3 |", text)
        self.assertIn("- **I-26** (`engine`)\n", text)
        # In the discrepancy tables, with the issue named; GUID_C has none.
        self.assertIn(f"| {GUID_A} | Group_1 | I-26 | pending |", text)
        self.assertRegex(text, rf"\| {GUID_B} \| Group_1 \| Denominator \| 1 \| 0 \| "
                               r"I-26 \| pending \|")
        self.assertRegex(text, rf"\| {GUID_C} \| Group_1 \| Denominator \| 1 \| 0 \|  \|  \|")
        with open(self.output, newline="") as f:
            results = {r["guid"]: r["result"] for r in csv.DictReader(f)}
        self.assertEqual(set(results.values()), {"FAIL"})

    def test_unticketed_non_ticketable_class_reads_na_and_is_not_needs_ticket(self):
        # `content` is not in TICKETABLE_CLASSES: no upstream ticket is owed, so the
        # cell reads N/A and the header line counts it separately from the
        # engine/translator cases that really are waiting on a ticket.
        text = self._run(
            [f"{MEASURE},{GUID_A},Group_1:Denominator,1",
             f"{MEASURE},{GUID_B},Group_1:Denominator,1",
             f"{MEASURE},{GUID_C},Group_1:Denominator,1"],
            [f"{MEASURE},{GUID_B},Group_1:Denominator,0",
             f"{MEASURE},{GUID_C},Group_1:Denominator,0"],
            KNOWN_HEADER + f"I-65,content,,{MEASURE},{GUID_A},,\n"
            + f"I-65,content,,{MEASURE},{GUID_B},,\n")
        self.assertIn("| Fail Count | 3 (100.00%) |", text)
        self.assertIn("| &nbsp;&nbsp;— known issue, no ticket expected | 2 (66.67%) |", text)
        self.assertNotIn("known issue, needs ticket", text)
        self.assertNotIn("Known Issue Count (ticketed)", text)
        self.assertIn("- **I-65** (`content`)\n", text)
        self.assertIn(f"| {GUID_A} | Group_1 | I-65 | N/A |", text)
        self.assertRegex(text, rf"\| {GUID_B} \| Group_1 \| Denominator \| 1 \| 0 \| "
                               r"I-65 \| N/A \|")
        with open(self.output, newline="") as f:
            results = {r["guid"]: r["result"] for r in csv.DictReader(f)}
        self.assertEqual(set(results.values()), {"FAIL"})

    def test_no_failing_covered_case_renders_no_section(self):
        text = self._run(
            [f"{MEASURE},{GUID_A},Group_1:Denominator,1"],
            [f"{MEASURE},{GUID_A},Group_1:Denominator,1"],
            KNOWN_HEADER + f"I-26,engine,,{MEASURE},{GUID_A},,\n")
        self.assertNotIn("## Known Issues", text)
        self.assertNotIn("| Issue |", text)
        self.assertNotIn("\nIssues\n", text)
        self.assertIn("| Unattributed Discrepancies | 0 | 0 |", text)


class MeasureIssueSectionTest(unittest.TestCase):
    """Every issue state in one measure section, in place of the old issue sections."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)

    def _write(self, name, text):
        path = os.path.join(self.tmp, name)
        with open(path, "w", newline="") as f:
            f.write(text)
        return path

    def _run(self, expected_rows, actual_rows, known_text, impl_text=IMPL_HEADER):
        e = self._write("e.csv", _csv(*expected_rows))
        a = self._write("a.csv", _csv(*actual_rows))
        report = os.path.join(self.tmp, "r.md")
        main(e, a, os.path.join(self.tmp, "o.csv"), report, measure_resource_dir=self.tmp,
             implementation_file=self._write("impl.csv", impl_text),
             known_issues_file=self._write("known.csv", known_text))
        with open(report) as f:
            return f.read()

    def test_mixed_issue_states(self):
        guid_d = "dddddddd-4444-4444-8444-dddddddddddd"
        other = "CMS998FHIRCleanMeasure"
        text = self._run(
            [f"{MEASURE},{g},Group_1:Denominator,1" for g in (GUID_A, GUID_B, GUID_C, guid_d)]
            + [f"{other},{GUID_A},Group_1:Denominator,1"],
            [f"{MEASURE},{g},Group_1:Denominator,0" for g in (GUID_A, GUID_B, GUID_C, guid_d)]
            + [f"{other},{GUID_A},Group_1:Denominator,1"],
            KNOWN_HEADER + f"I-65,content,,{MEASURE},{GUID_B},,Needs work.\n"
            + f"I-26,engine,{TICKET},{MEASURE},{GUID_C},,Engine note.\n",
            IMPL_HEADER + f"I-73,{MEASURE},{GUID_A},,Steward data.\n")
        # A resolved (I-73, I-26), B explained by an unticketed content issue,
        # D has no issue: 2 unattributed.
        self.assertIn("| Unattributed Discrepancies | 1 | 2 |", text)
        self.assertIn(f"| [{MEASURE}](#{MEASURE.lower()}) | 4 | 0 | 0 | 100.00%   (4) | 0 | 2 |",
                      text)
        self.assertIn("| Test Case | Group | Population | Expected | Actual | Issue | Ticketed |\n"
                      "|---|---|---|:---:|:---:|---|---|\n", text)
        self.assertIn(f"| {GUID_A} | Group_1 | Denominator | 1 | 0 | I-73 (implementation) | N/A |",
                      text)
        # I-65 is `content`, so no upstream ticket is owed: N/A, not pending.
        self.assertIn(f"| {GUID_B} | Group_1 | Denominator | 1 | 0 | I-65 | N/A |", text)
        self.assertIn(f"| {GUID_C} | Group_1 | Denominator | 1 | 0 | I-26 | [1855]({TICKET}) |", text)
        # No issue, so the Ticketed cell is blank like the Issue cell.
        self.assertIn(f"| {guid_d} | Group_1 | Denominator | 1 | 0 |  |  |", text)
        # Issue notes in numeric order.
        notes = [l for l in text.splitlines() if l.startswith("- **I-")]
        self.assertEqual([l.split("**")[1] for l in notes], ["I-26", "I-65", "I-73"])
        # A measure is listed under exactly one of the two measure sections.
        clean, discrepant = text.split("## Measures with Discrepancies")
        self.assertIn(other, clean.split("## Measures with No Discrepancies")[1])
        self.assertNotIn(MEASURE, clean.split("## Measures with No Discrepancies")[1])
        self.assertNotIn(other, discrepant)

    def test_missing_tables_carry_the_ticketed_column(self):
        text = self._run(
            [f"{MEASURE},{GUID_A},Group_1:Denominator,1",
             f"{MEASURE},{GUID_B},Group_1:Denominator,1"],
            # A has the group but not the population; B has no results at all.
            [f"{MEASURE},{GUID_A},Group_1:Initial Population,1"],
            KNOWN_HEADER + f"I-65,content,,{MEASURE},{GUID_A},,Needs work.\n"
            + f"I-26,engine,{TICKET},{MEASURE},{GUID_B},,Engine note.\n")
        self.assertIn("| Test Case | Group | Issue | Ticketed |\n", text)
        self.assertIn(f"| {GUID_B} | Group_1 | I-26 | [1855]({TICKET}) |", text)
        self.assertIn("| Test Case | Group | Population | Issue | Ticketed |\n", text)
        # I-65 is `content`: the Ticketed column still renders, as N/A.
        self.assertIn(f"| {GUID_A} | Group_1 | Denominator | I-65 | N/A |", text)

    def test_distinct_notes_of_one_issue_get_sub_bullets(self):
        text = self._run(
            [f"{MEASURE},{GUID_A},Group_1:Denominator,1",
             f"{MEASURE},{GUID_B},Group_1:Denominator,1",
             f"{MEASURE},{GUID_C},Group_1:Denominator,1"],
            [f"{MEASURE},{GUID_A},Group_1:Denominator,0",
             f"{MEASURE},{GUID_B},Group_1:Denominator,0",
             f"{MEASURE},{GUID_C},Group_1:Denominator,0"],
            KNOWN_HEADER + f"I-65,content,,{MEASURE},{GUID_A},,First cause.\n"
            + f"I-65,content,,{MEASURE},{GUID_B},,Second cause.\n"
            + f"I-65,content,,{MEASURE},{GUID_C},,First cause.\n")
        self.assertIn("- **I-65** (`content`)\n"
                      "  - `aaaaaaaa`, `cccccccc`: First cause.\n"
                      "  - `bbbbbbbb`: Second cause.\n", text)


class WorkaroundReportTest(unittest.TestCase):
    """A case that passes only because of a workaround is still a discrepancy.

    The point of the report is to surface defects. A workaround makes the grid
    match, but the defect is open and the workaround is to be reverted, so the
    measure must stay under `## Measures with Discrepancies` and the case must
    not be counted as a pass.
    """

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)

    def _write(self, name, text):
        path = os.path.join(self.tmp, name)
        with open(path, "w", newline="") as f:
            f.write(text)
        return path

    def _run(self, expected_rows, actual_rows, known_text):
        e = self._write("e.csv", _csv(*expected_rows))
        a = self._write("a.csv", _csv(*actual_rows))
        self.output = os.path.join(self.tmp, "o.csv")
        report = os.path.join(self.tmp, "r.md")
        main(e, a, self.output, report, measure_resource_dir=self.tmp,
             implementation_file=os.path.join(self.tmp, "no-impl.csv"),
             known_issues_file=self._write("known.csv", known_text))
        with open(report) as f:
            return f.read()

    def test_workaround_keeps_the_measure_in_the_report(self):
        text = self._run(
            [f"{MEASURE},{GUID_A},Group_1:Denominator,1",
             f"{MEASURE},{GUID_B},Group_1:Denominator,1"],
            [f"{MEASURE},{GUID_A},Group_1:Denominator,1",
             f"{MEASURE},{GUID_B},Group_1:Denominator,1"],
            KNOWN_HEADER_STATUS
            + f"I-78,translator,workaround-applied,{TICKET},{MEASURE},{GUID_A},,"
              "Cast applied.\n")
        # Counted as neither a pass nor a failure.
        self.assertIn("| Pass Count | 1 (50.00%) |", text)
        self.assertIn("| Workaround Count | 1 (50.00%) |", text)
        self.assertIn("| Fail Count | 0 (0.00%) |", text)
        # Resolved leaves the workaround out, and the bucket line shows the sum.
        self.assertIn("| Resolved without workaround (Pass) | 1 (50.00%) |", text)
        self.assertIn("_Every test case is in exactly one bucket: "
                      "1 Pass + 1 Workaround + 0 Fail = 2.", text)
        # It is also a ticketed known issue, and the header says so rather than
        # reporting only the workaround half of the story.
        self.assertIn("| &nbsp;&nbsp;— covered by a ticketed known issue | 1 (50.00%) |",
                      text)
        self.assertIn("| Known issues with an upstream ticket | 1 (50.00%) |", text)
        # And the measure stays a discrepancy, with its own table.
        self.assertIn("| Measures with Discrepancies | 1 |", text)
        self.assertIn("| Workarounds | 1 | 1 |", text)
        self.assertIn("| Unattributed Discrepancies | 0 | 0 |", text)
        self.assertIn(f"| [{MEASURE}](#{MEASURE.lower()}) | 2 | 0 | 0 | 0.00%   (0) | 1 "
                      "| 0 |", text)
        self.assertIn("Workarounds (1 of 2 test cases)", text)
        self.assertIn("| Test Case | Group | Issue | Ticketed |\n", text)
        self.assertIn(f"| {GUID_A} | Group_1 | I-78 (workaround applied) | [1855]({TICKET}) |", text)
        self.assertIn("_Cast applied._", text)
        # The issue is listed under the measure too, like any other it cites.
        self.assertIn("- **I-78** (`translator`, **workaround applied**)", text)
        self.assertNotIn("## Measures with No Discrepancies", text)
        with open(self.output, newline="") as f:
            results = {r["guid"]: r["result"] for r in csv.DictReader(f)}
        self.assertEqual(results, {GUID_A: WORKAROUND, GUID_B: "PASS"})

    def test_reverted_workaround_is_reported_as_a_failure(self):
        # No actual results at all: the case fails once the workaround is gone.
        text = self._run(
            [f"{MEASURE},{GUID_A},Group_1:Denominator,1"],
            [],
            KNOWN_HEADER_STATUS
            + f"I-78,translator,workaround-applied,,{MEASURE},{GUID_A},,Cast applied.\n")
        self.assertIn("| Fail Count | 1 (100.00%) |", text)
        self.assertNotIn("| Workaround Count |", text)
        # Unticketed, so nothing claims ticket coverage for it either.
        self.assertNotIn("covered by a ticketed known issue", text)
        self.assertNotIn("Known issues with an upstream ticket", text)
        self.assertIn("| Workarounds | 0 | 0 |", text)
        self.assertIn(f"| {GUID_A} | Group_1 | I-78 (workaround reverted) | pending |", text)
        # The bullet tracks the issue's catalog state, not the row's resolution.
        self.assertIn("- **I-78** (`translator`, **workaround applied**)", text)

    def test_ticketed_rollup_spans_workaround_and_failing_cases(self):
        # A case that a ticketed issue covers *and* a workaround props up gets a
        # single WORKAROUND verdict, and a ticketed failure gets KNOWN_ISSUE, so
        # neither count alone reports the ticketed coverage. Three cases: one
        # propped up, one failing for a ticketed issue, one for an unticketed one.
        text = self._run(
            [f"{MEASURE},{GUID_A},Group_1:Denominator,1",
             f"{MEASURE},{GUID_B},Group_1:Denominator,1",
             f"{MEASURE},{GUID_C},Group_1:Denominator,1"],
            [f"{MEASURE},{GUID_A},Group_1:Denominator,1",
             f"{MEASURE},{GUID_B},Group_1:Denominator,0"],
            KNOWN_HEADER_STATUS
            + f"I-78,translator,workaround-applied,{TICKET},{MEASURE},{GUID_A},,"
              "Cast applied.\n"
            + f"I-26,engine,confirmed,{TICKET},{MEASURE},{GUID_B},,\n"
            + f"I-33,engine,confirmed,,{MEASURE},{GUID_C},,\n")
        self.assertIn("| Workaround Count | 1 (33.33%) |", text)
        self.assertIn("| &nbsp;&nbsp;— covered by a ticketed known issue | 1 (33.33%) |",
                      text)
        self.assertIn("| Known Issue Count (ticketed) | 1 (33.33%) |", text)
        self.assertIn("| Fail Count | 1 (33.33%) |", text)
        # The two ticketed cases, counted across the verdicts that separated them;
        # the unticketed failure is not among them.
        self.assertIn("| Known issues with an upstream ticket | 2 (66.67%) |", text)
        # The roll-up is cross-cutting: it is not one of the five that total.
        self.assertIn("| Total Test Cases | 3 |", text)
        with open(self.output, newline="") as f:
            results = {r["guid"]: r["result"] for r in csv.DictReader(f)}
        self.assertEqual(results, {GUID_A: WORKAROUND, GUID_B: KNOWN_ISSUE, GUID_C: "FAIL"})


class HelpersTest(unittest.TestCase):

    def test_ticket_link(self):
        self.assertEqual(ticket_link(TICKET),
                         f"[cqframework/clinical_quality_language#1855]({TICKET})")
        self.assertEqual(ticket_link(""), "")

    def test_ticket_number(self):
        self.assertEqual(ticket_number(TICKET), "1855")
        self.assertEqual(ticket_number(
            "https://github.com/cqframework/clinical_quality_language/pull/1968"), "1968")
        self.assertEqual(ticket_number(""), "")

    def test_sort_issue_ids_is_numeric(self):
        self.assertEqual(sort_issue_ids(["I-26", "I-9", "I-100"]), ["I-9", "I-26", "I-100"])


if __name__ == "__main__":
    unittest.main()
