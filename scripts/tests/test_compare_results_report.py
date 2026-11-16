"""Tests for the discrepancy report's shared scoring and layout.

Covers the per-case verdict rule (``side_status``) that the implementation-issue
and known-issue scoring build on, CQFM exclusions at the read point, the report's
table shapes and headings, and command-line parsing.
"""
import os
import re
import shutil
import tempfile
import unittest

from scripts.compare_results import (
    ResultKey,
    capture_results,
    generate_comparison_report,
    generate_output,
    parse_args,
    render_no_discrepancy_section,
    side_status,
)

MEASURE = "CMS999FHIRTestMeasure"
GUID_A = "aaaaaaaa-1111-4111-8111-aaaaaaaaaaaa"
GUID_B = "bbbbbbbb-2222-4222-8222-bbbbbbbbbbbb"

CSV_HEADER = "measure_name,guid,population,count\n"


def _csv(*rows):
    return CSV_HEADER + "".join(f"{r}\n" for r in rows)


def _write(path, text):
    with open(path, "w", newline="") as f:
        f.write(text)
    return path


class SideStatusTest(unittest.TestCase):
    """`side_status` decides PASS / FAIL / MISSING for one test case."""

    def test_passes_when_every_expected_population_matches(self):
        expected = {"Initial Population": "1", "Denominator": "1", "Numerator": "1"}
        self.assertEqual(side_status(expected, dict(expected)), "PASS")

    def test_passes_on_extra_populations_the_engine_reports(self):
        # A population the fixture does not list is not a mismatch: the report
        # only ever checks what is expected.
        expected = {"Denominator": "1"}
        actual = {"Initial Population": "1", "Denominator": "1", "Numerator": "0"}
        self.assertEqual(side_status(expected, actual), "PASS")

    def test_fails_when_a_value_differs(self):
        self.assertEqual(
            side_status({"Denominator": "1"}, {"Denominator": "0"}), "FAIL")

    def test_fails_when_an_expected_population_is_omitted(self):
        # Absence is not agreement: a measure that never emitted a row has not
        # reproduced the expectation.
        self.assertEqual(
            side_status({"Denominator": "1", "Numerator": "1"}, {"Denominator": "1"}),
            "FAIL")

    def test_missing_when_there_is_no_result(self):
        self.assertEqual(side_status({"Denominator": "1"}, None), "MISSING")

    def test_empty_expectation_passes(self):
        self.assertEqual(side_status({}, {}), "PASS")

    def test_compares_stringified_counts_like_row_outcome(self):
        # Counts arrive as CSV strings, but an int must not read as a mismatch.
        self.assertEqual(side_status({"Denominator": "1"}, {"Denominator": 1}), "PASS")


class CqfmExclusionsTest(unittest.TestCase):
    """CQFM-excluded cells are routed to `unscored`, never compared."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)

    def test_excluded_cell_is_unscored_on_both_sides(self):
        exclusions = {MEASURE: frozenset({"Group_1:Measure Observation"})}
        expected = capture_results(_write(os.path.join(self.tmp, "e.csv"), _csv(
            f"{MEASURE},{GUID_A},Group_1:Denominator,1",
            f"{MEASURE},{GUID_A},Group_1:Measure Observation,1")), exclusions)
        # The engine emits no observation row at all; that must not read as a
        # missing population.
        actual = capture_results(_write(os.path.join(self.tmp, "a.csv"), _csv(
            f"{MEASURE},{GUID_A},Group_1:Denominator,1")), exclusions)
        key = ResultKey(MEASURE, GUID_A, "Group_1")
        self.assertEqual(expected.groups[key], {"Denominator": "1"})
        self.assertEqual(side_status(expected.groups[key], actual.groups[key]), "PASS")
        self.assertEqual([(c.population, c.reason) for c in expected.unscored],
                         [("Group_1:Measure Observation", "cqfm-aggregation-excluded")])


class ReportTablesTest(unittest.TestCase):
    """Table shapes of the per-measure discrepancy sections."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)

    def test_tables_have_the_engine_columns_only(self):
        expected = _write(os.path.join(self.tmp, "expected.csv"), _csv(
            f"{MEASURE},{GUID_A},Group_1:Initial Population,1",
            f"{MEASURE},{GUID_A},Group_1:Denominator,1",
            f"{MEASURE},{GUID_A},Group_1:Numerator,1",
            f"{MEASURE},{GUID_B},Group_1:Denominator,1",
        ))
        actual = _write(os.path.join(self.tmp, "actual.csv"), _csv(
            f"{MEASURE},{GUID_A},Group_1:Initial Population,1",
            f"{MEASURE},{GUID_A},Group_1:Denominator,1",
            f"{MEASURE},{GUID_A},Group_1:Numerator,0",
        ))
        output = os.path.join(self.tmp, "output.csv")
        report = os.path.join(self.tmp, "report.md")
        expected_r, actual_r = capture_results(expected), capture_results(actual)
        pass_count, fail_count = generate_output(output, expected_r.rows, actual_r.rows)
        generate_comparison_report(report, expected_r.groups, actual_r.groups,
                                   pass_count, fail_count)
        with open(report) as f:
            text = f.read()
        self.assertNotIn("QI-Core", text)
        self.assertIn("| Measure | Total Test Cases | Missing Results | "
                      "Missing Populations | Mismatched Test Cases | Workarounds | "
                      "Unattributed |\n"
                      "|---|:---:|:---:|:---:|:---:|:---:|:---:|\n", text)
        self.assertIn("| Test Case | Group |\n", text)
        self.assertIn("| Test Case | Group | Population | Expected | Actual |\n"
                      "|---|---|---|:---:|:---:|\n", text)
        row_a = next(l for l in text.splitlines() if GUID_A in l and l.startswith("|"))
        self.assertTrue(row_a.rstrip().endswith("| Numerator | 1 | 0 |"), row_a)


class DiscrepancyHeadingTest(unittest.TestCase):
    """`## Measures with Discrepancies` states its share of the corpus."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)

    def test_heading_is_discrepant_of_total_measures(self):
        other = "CMS888FHIROtherMeasure"
        e = capture_results(_write(os.path.join(self.tmp, "e.csv"), _csv(
            f"{MEASURE},{GUID_A},Group_1:Denominator,1",
            f"{other},{GUID_B},Group_1:Denominator,1")))
        a = capture_results(_write(os.path.join(self.tmp, "a.csv"), _csv(
            f"{MEASURE},{GUID_A},Group_1:Denominator,0",
            f"{other},{GUID_B},Group_1:Denominator,1")))
        report = os.path.join(self.tmp, "r.md")
        generate_comparison_report(report, e.groups, a.groups, 1, 0)
        with open(report) as f:
            text = f.read()
        self.assertIn("## Measures with Discrepancies (1 of 2)", text)
        self.assertIn("## Measures with No Discrepancies (1 of 2)", text)


class NoDiscrepancyGridTest(unittest.TestCase):
    """The clean-measure grid: several measures per row, order preserved."""

    def _grid(self, measures):
        text = "".join(render_no_discrepancy_section(measures, len(measures) + 1))
        rows = [r for r in text.splitlines() if r.startswith('| [')]
        return text, [[c.strip() for c in r.strip().strip('|').split('|')]
                      for r in rows]

    def test_measures_are_laid_out_column_major_in_given_order(self):
        measures = [f"CMS{100 + i}FHIRTest{i}" for i in range(8)]
        text, grid = self._grid(measures)
        self.assertEqual(len(grid[0]), 3)
        self.assertIn("## Measures with No Discrepancies (8 of 9)", text)
        # Column-major: reading down column 1 then column 2 reproduces the
        # caller's order. A row-major grid would put CMS102 in row 1.
        read_down = [re.match(r"\[ (\S+) \]", c).group(1)
                     for column in zip(*grid) for c in column if c]
        self.assertEqual(read_down, measures)

    def test_padding_falls_only_in_the_last_column(self):
        # 7 measures over 3 columns needs 3 rows: 3, 3, 1. Column-major fills
        # whole columns before starting the next, so the two short rows are
        # both in the last column.
        _, grid = self._grid([f"CMS{200 + i}FHIRTest{i}" for i in range(7)])
        self.assertEqual([len(row) for row in grid], [3, 3, 3])
        empties = [(r, c) for r, row in enumerate(grid)
                   for c, cell in enumerate(row) if not cell]
        self.assertEqual(empties, [(1, 2), (2, 2)])

    def test_every_cell_carries_the_cql_link(self):
        _, grid = self._grid(["CMS300FHIRTest"])
        cell = grid[0][0]
        self.assertEqual(
            cell, "[ CMS300FHIRTest ](../../input/cql/CMS300FHIRTest.cql)")

    def test_no_measures_renders_no_section(self):
        self.assertEqual(render_no_discrepancy_section([], 74), [])


class ParseArgsTest(unittest.TestCase):
    """The flag and positionals can appear in any order; paths pass through as-is."""

    def test_defaults_when_no_arguments(self):
        self.assertEqual(parse_args([]), (
            "./scripts/comparison/expected_results.csv",
            "./scripts/comparison/actual_results.csv",
            "./scripts/comparison/output_results.csv",
            "./scripts/comparison/discrepancy_report.md",
            None))

    def test_positional_arguments(self):
        self.assertEqual(parse_args(["e.csv", "a.csv", "o.csv", "r.md"]),
                         ("e.csv", "a.csv", "o.csv", "r.md", None))

    def test_positional_defaults_fill_in_the_tail(self):
        expected, actual, _, report, _ = parse_args(["e.csv"])
        self.assertEqual(expected, "e.csv")
        self.assertEqual(actual, "./scripts/comparison/actual_results.csv")
        self.assertEqual(report, "./scripts/comparison/discrepancy_report.md")

    def test_measure_resource_dir_paths_pass_through_without_normalisation(self):
        # macOS/Linux, Windows backslash, Windows forward slash, relative, home.
        for path in ("/tmp/measures", r"C:\data\measures", "C:/data/measures",
                     "./a/b/../measures", "~/measures"):
            with self.subTest(path=path):
                *_, measure_dir = parse_args(["--measure-resource-dir", path])
                self.assertEqual(measure_dir, path)

    def test_flag_after_positionals(self):
        self.assertEqual(
            parse_args(["e.csv", "a.csv", "o.csv", "r.md",
                        "--measure-resource-dir", "/tmp/measures"]),
            ("e.csv", "a.csv", "o.csv", "r.md", "/tmp/measures"))

    def test_flag_before_positionals(self):
        expected, _, _, _, measure_dir = parse_args(
            ["--measure-resource-dir", "/tmp/measures", "e.csv"])
        self.assertEqual(expected, "e.csv")
        self.assertEqual(measure_dir, "/tmp/measures")


if __name__ == "__main__":
    unittest.main()
