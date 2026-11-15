"""Tests for the report's Open Tickets section.

`open_tickets.csv` lists every upstream ticket an open known issue cites, with a
one-line summary and the issues citing it. The report lists them in an
`## Open Tickets` section after the discrepancy summary table, followed by a
`## Measure Discrepancy Details` heading before the first measure. With no
discrepancies the tickets are still listed, and the details heading is not.

These tests pin the loader's validation and the section's place in the report.
"""
import os
import shutil
import tempfile
import unittest

from scripts.compare_results import (
    OpenTicket,
    load_open_tickets,
    main,
    render_open_tickets_section,
)

MEASURE = "CMS999FHIRTestMeasure"
GUID_A = "aaaaaaaa-1111-4111-8111-aaaaaaaaaaaa"
TICKET = "https://github.com/cqframework/clinical_quality_language/issues/1855"
JIRA = "https://jira.hl7.org/browse/FHIR-59691"

CSV_HEADER = "measure_name,guid,population,count\n"
TICKETS_HEADER = "ticket,summary,issues\n"


def _csv(*rows):
    return CSV_HEADER + "".join(f"{r}\n" for r in rows)


class OpenTicketLoaderTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)

    def _load(self, text):
        path = os.path.join(self.tmp, "tickets.csv")
        with open(path, "w", newline="") as f:
            f.write(text)
        return load_open_tickets(path)

    def test_absent_file_means_no_tickets(self):
        self.assertEqual(load_open_tickets(os.path.join(self.tmp, "nope.csv")), [])
        self.assertEqual(load_open_tickets(None), [])

    def test_reads_github_and_jira_rows(self):
        tickets = self._load(TICKETS_HEADER
                             + f'{TICKET},"Ambiguous call, sibling profiles",I-18 I-20\n'
                             + f"{JIRA},Short periods,I-63\n")
        self.assertEqual(tickets, [
            OpenTicket(TICKET, "Ambiguous call, sibling profiles", ("I-18", "I-20")),
            OpenTicket(JIRA, "Short periods", ("I-63",)),
        ])

    def test_blank_rows_are_skipped(self):
        self.assertEqual(len(self._load(TICKETS_HEADER + f"{TICKET},S,I-1\n,,\n")), 1)

    def test_placeholder_ticket_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "neither a GitHub"):
            self._load(TICKETS_HEADER + "TBD,S,I-1\n")

    def test_missing_column_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing column"):
            self._load("ticket,summary\n" + f"{TICKET},S\n")

    def test_unquoted_comma_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "more fields than columns"):
            self._load(TICKETS_HEADER + f"{TICKET},a, b,I-1\n")


class OpenTicketSectionTest(unittest.TestCase):

    def test_no_tickets_renders_nothing(self):
        self.assertEqual(render_open_tickets_section([]), [])

    def test_rows_link_the_ticket_and_list_the_issues(self):
        text = "".join(render_open_tickets_section([
            OpenTicket(TICKET, "Ambiguous call", ("I-18", "I-20")),
            OpenTicket(JIRA, "Short periods", ("I-63",)),
        ]))
        self.assertIn("## Open Tickets (2)\n", text)
        self.assertIn("| Ticket | Summary | Issues |", text)
        self.assertIn(f"| [cqframework/clinical_quality_language#1855]({TICKET}) "
                      "| Ambiguous call | I-18, I-20 |", text)
        self.assertIn(f"| [FHIR-59691]({JIRA}) | Short periods | I-63 |", text)


class OpenTicketReportTest(unittest.TestCase):
    """End to end through main()."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)

    def _write(self, name, text):
        path = os.path.join(self.tmp, name)
        with open(path, "w", newline="") as f:
            f.write(text)
        return path

    def _run(self, expected_rows, actual_rows):
        report = os.path.join(self.tmp, "r.md")
        main(self._write("e.csv", _csv(*expected_rows)),
             self._write("a.csv", _csv(*actual_rows)),
             os.path.join(self.tmp, "o.csv"), report, measure_resource_dir=self.tmp,
             implementation_file=os.path.join(self.tmp, "no-impl.csv"),
             known_issues_file=os.path.join(self.tmp, "no-known.csv"),
             open_tickets_file=self._write("tickets.csv", TICKETS_HEADER
                                           + f"{TICKET},Ambiguous call,I-18\n"))
        with open(report) as f:
            return f.read()

    def test_tickets_sit_between_the_summary_table_and_the_measure_details(self):
        text = self._run([f"{MEASURE},{GUID_A},Group_1:Denominator,1"],
                         [f"{MEASURE},{GUID_A},Group_1:Denominator,0"])
        summary = text.index("## Measures with Discrepancies (1 of 1)")
        tickets = text.index("## Open Tickets (1)")
        details = text.index("## Measure Discrepancy Details")
        first_measure = text.index(f"#### {MEASURE}")
        self.assertLess(summary, tickets)
        self.assertLess(tickets, details)
        self.assertLess(details, first_measure)
        self.assertEqual(text.count("## Measure Discrepancy Details"), 1)

    def test_tickets_are_listed_without_discrepancies(self):
        text = self._run([f"{MEASURE},{GUID_A},Group_1:Denominator,1"],
                         [f"{MEASURE},{GUID_A},Group_1:Denominator,1"])
        self.assertNotIn("## Measures with Discrepancies", text)
        self.assertNotIn("## Measure Discrepancy Details", text)
        self.assertIn("## Open Tickets (1)", text)
        self.assertIn("| Ambiguous call | I-18 |", text)


if __name__ == "__main__":
    unittest.main()
