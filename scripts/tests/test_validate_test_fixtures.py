import json
import os
import tempfile
import unittest

from scripts.validate_test_fixtures import (
    apply_misnamed_patient_fix,
    collect_anomaly_fixes,
    collect_test_cases,
    collect_fixable,
    discover_patient_fields,
    expected_patient_for,
    misnamed_patient_file,
    patient_resource_files,
    validate,
    _patient_ref_guid,
)


def write_json(directory, filename, data):
    path = os.path.join(directory, filename)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh)
    return path


def make_patient(case_dir, guid):
    write_json(case_dir, f"Patient-{guid}.json",
               {"resourceType": "Patient", "id": guid})


class PatientRefHelpersTest(unittest.TestCase):

    def test_patient_ref_guid_extracts_guid(self):
        self.assertEqual(_patient_ref_guid({"reference": "Patient/abc-123"}), "abc-123")

    def test_patient_ref_guid_non_patient_reference(self):
        self.assertIsNone(_patient_ref_guid({"reference": "Encounter/x"}))

    def test_patient_ref_guid_ignores_non_dict(self):
        self.assertIsNone(_patient_ref_guid("Patient/abc"))
        self.assertIsNone(_patient_ref_guid(None))


class ExpectedPatientTest(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.mkdtemp()
        self.case = os.path.join(self._tmp, "CMS104X", "11111111-1111-1111-1111-111111111111")
        os.makedirs(self.case)

    def tearDown(self):
        import shutil
        shutil.rmtree(self._tmp, ignore_errors=True)

    def test_single_patient_returns_id(self):
        make_patient(self.case, "11111111-1111-1111-1111-111111111111")
        files = [f for f in os.listdir(self.case) if f.startswith("Patient-")]
        self.assertEqual(expected_patient_for([os.path.join(self.case, f) for f in files]),
                         "11111111-1111-1111-1111-111111111111")

    def test_no_patient_returns_none(self):
        files = [f for f in os.listdir(self.case) if f.startswith("Patient-")]
        self.assertIsNone(expected_patient_for([os.path.join(self.case, f) for f in files]))

    def test_two_patients_returns_none(self):
        make_patient(self.case, "11111111-1111-1111-1111-111111111111")
        make_patient(self.case, "22222222-2222-2222-2222-222222222222")
        files = [f for f in os.listdir(self.case) if f.startswith("Patient-")]
        self.assertIsNone(expected_patient_for([os.path.join(self.case, f) for f in files]))


class DiscoverPatientFieldsTest(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.mkdtemp()
        self.case = os.path.join(self._tmp, "CMS104X", "11111111-1111-1111-1111-111111111111")
        os.makedirs(self.case)
        make_patient(self.case, "11111111-1111-1111-1111-111111111111")

    def tearDown(self):
        import shutil
        shutil.rmtree(self._tmp, ignore_errors=True)

    def test_discovers_all_patient_ref_fields(self):
        write_json(self.case, "Encounter-e.json", {
            "resourceType": "Encounter",
            "subject": {"reference": "Patient/11111111-1111-1111-1111-111111111111"},
        })
        write_json(self.case, "Task-t.json", {
            "resourceType": "Task",
            "for": {"reference": "Patient/11111111-1111-1111-1111-111111111111"},
            "focus": {"reference": "Patient/11111111-1111-1111-1111-111111111111"},
        })
        files = [os.path.join(self.case, f) for f in os.listdir(self.case)
                 if not f.startswith("Patient-")]
        self.assertEqual(discover_patient_fields(files), {"subject", "for", "focus"})

    def test_ignores_measure_report(self):
        write_json(self.case, "MeasureReport-m.json", {
            "resourceType": "MeasureReport", "subject": {"reference": "Patient/11111111-1111-1111-1111-111111111111"},
        })
        files = [os.path.join(self.case, f) for f in os.listdir(self.case)
                 if not f.startswith("Patient-")]
        self.assertEqual(discover_patient_fields(files), set())


class ValidateTest(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.mkdtemp()
        self.tests_root = self._tmp
        self.good = "11111111-1111-1111-1111-111111111111"
        self.other = "99999999-9999-9999-9999-999999999999"
        self.placeholder = "d170a0a8-b5ad-4303-b6df-e304dd5f92ad"

        # measure CMS104X with two test cases
        self.m1 = os.path.join(self.tests_root, "CMS104X", self.good)
        os.makedirs(self.m1)
        make_patient(self.m1, self.good)

        self.m2 = os.path.join(self.tests_root, "CMS104X", self.other)
        os.makedirs(self.m2)
        make_patient(self.m2, self.other)

        # a second measure to establish that `other`/`placeholder` are cross-measure
        self.m3 = os.path.join(self.tests_root, "CMS72X", self.other)
        os.makedirs(self.m3)
        make_patient(self.m3, self.other)

    def tearDown(self):
        import shutil
        shutil.rmtree(self._tmp, ignore_errors=True)

    def _cases(self):
        return collect_test_cases(self.tests_root)

    def test_correct_reference_not_flagged(self):
        write_json(self.m1, "Encounter-e.json", {
            "resourceType": "Encounter",
            "subject": {"reference": f"Patient/{self.good}"},
        })
        findings, _ = validate(self._cases())
        self.assertEqual(findings, [])

    def test_core_wrong_patient_flagged_fixable(self):
        write_json(self.m1, "Claim-c.json", {
            "resourceType": "Claim",
            "patient": {"reference": f"Patient/{self.other}"},
        })
        findings, _ = validate(self._cases())
        self.assertEqual(len(findings), 1)
        f = findings[0]
        self.assertEqual(f[3], "patient")
        self.assertEqual(f[4], self.other)
        self.assertEqual(f[5], self.good)
        self.assertTrue(f[6].startswith("CORE") and "FIXABLE" in f[6])

    def test_core_placeholder_flagged(self):
        write_json(self.m1, "Claim-c.json", {
            "resourceType": "Claim",
            "patient": {"reference": f"Patient/{self.placeholder}"},
        })
        findings, _ = validate(self._cases())
        self.assertEqual(len(findings), 1)
        f = findings[0]
        self.assertTrue(f[6].startswith("CORE") and "PLACEHOLDER" in f[6])

    def test_core_subject_mismatch_flagged(self):
        write_json(self.m1, "Encounter-e.json", {
            "resourceType": "Encounter",
            "subject": {"reference": f"Patient/{self.other}"},
        })
        findings, _ = validate(self._cases())
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0][3], "subject")

    def test_core_beneficiary_mismatch_flagged(self):
        write_json(self.m1, "Coverage-c.json", {
            "resourceType": "Coverage",
            "beneficiary": {"reference": f"Patient/{self.other}"},
        })
        findings, _ = validate(self._cases())
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0][3], "beneficiary")

    def test_broad_field_mismatch_reported_not_fixable(self):
        write_json(self.m1, "Task-t.json", {
            "resourceType": "Task",
            "for": {"reference": f"Patient/{self.other}"},
        })
        findings, _ = validate(self._cases())
        self.assertEqual(len(findings), 1)
        f = findings[0]
        self.assertEqual(f[3], "for")
        self.assertIn("NOT-FIXED", f[6])
        self.assertFalse(collect_fixable(findings))

    def test_missing_patient_field_not_flagged(self):
        # CORE field entirely absent (not merely wrong) is only flagged when the
        # resource type is also in REQUIRED_PATIENT_FIELDS; Claim is not.
        write_json(self.m1, "Claim-c.json", {"resourceType": "Claim"})
        findings, _ = validate(self._cases())
        self.assertEqual(findings, [])

    def test_structural_anomaly_no_patient(self):
        bad = os.path.join(self.tests_root, "CMS104X", "0000bad")
        os.makedirs(bad)
        write_json(bad, "Encounter-e.json", {"resourceType": "Encounter"})
        findings, anomalies = validate(self._cases())
        self.assertEqual(findings, [])
        self.assertEqual(len(anomalies), 1)

    def test_misnamed_patient_flagged_but_references_validated(self):
        # A Patient resource named null-null.json (template artifact, no id):
        # reported as a fixable anomaly, yet references against the folder GUID
        # are still validated (a matching reference produces no finding).
        bad = os.path.join(self.tests_root, "CMS104X", "bad-guuid")
        os.makedirs(bad)
        write_json(bad, "null-null.json", {"resourceType": "Patient"})
        write_json(bad, "Encounter-e.json", {
            "resourceType": "Encounter",
            "subject": {"reference": "Patient/bad-guuid"},
        })
        findings, anomalies = validate(self._cases())
        self.assertEqual(findings, [])
        self.assertEqual(len([a for a in anomalies if "misnamed" in a]), 1)

    def test_misnamed_patient_reference_mismatch_still_flagged(self):
        bad = os.path.join(self.tests_root, "CMS104X", "bad-guuid")
        os.makedirs(bad)
        write_json(bad, "null-null.json", {"resourceType": "Patient"})
        write_json(bad, "Encounter-e.json", {
            "resourceType": "Encounter",
            "subject": {"reference": f"Patient/{self.other}"},
        })
        findings, anomalies = validate(self._cases())
        self.assertEqual(len([a for a in anomalies if "misnamed" in a]), 1)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0][3], "subject")
        self.assertEqual(findings[0][5], "bad-guuid")

    def test_misnamed_patient_file_only_for_misnamed(self):
        files = [os.path.join(self.m1, f) for f in os.listdir(self.m1)]
        self.assertIsNone(misnamed_patient_file(files))
        self.assertEqual(patient_resource_files(files), [f for f in files
                                                         if f.endswith(f"Patient-{self.good}.json")])

    def test_collect_fixable_only_core(self):
        write_json(self.m1, "Claim-c.json", {
            "resourceType": "Claim", "patient": {"reference": f"Patient/{self.other}"},
        })
        write_json(self.m1, "Task-t.json", {
            "resourceType": "Task", "for": {"reference": f"Patient/{self.other}"},
        })
        findings, _ = validate(self._cases())
        fixable = collect_fixable(findings)
        self.assertEqual(len(fixable), 1)
        self.assertEqual(fixable[0][3], "patient")


class ApplyFixTest(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.mkdtemp()
        self.tests_root = self._tmp
        self.good = "11111111-1111-1111-1111-111111111111"
        self.other = "99999999-9999-9999-9999-999999999999"
        self.case = os.path.join(self.tests_root, "CMS104X", self.good)
        os.makedirs(self.case)
        make_patient(self.case, self.good)

    def tearDown(self):
        import shutil
        shutil.rmtree(self._tmp, ignore_errors=True)

    def test_apply_fix_rewrites_core_field_and_preserves_json(self):
        write_json(self.case, "Claim-c.json", {
            "resourceType": "Claim",
            "patient": {"reference": f"Patient/{self.other}"},
        })
        finding = ("CMS104X", self.good, "Claim-c.json", "patient", self.other, self.good, "CORE-WRONG-FIXABLE")
        path = os.path.join(self.tests_root, "CMS104X", self.good, "Claim-c.json")
        from scripts.validate_test_fixtures import apply_fix_finding
        self.assertTrue(apply_fix_finding(finding, tests_root=self.tests_root))
        with open(path) as fh:
            data = json.load(fh)
        self.assertEqual(data["patient"]["reference"], f"Patient/{self.good}")

    def test_apply_misnamed_patient_fix_renames_and_injects_id(self):
        bad = os.path.join(self.tests_root, "CMS104X", "bad-guuid")
        os.makedirs(bad)
        write_json(bad, "null-null.json", {"resourceType": "Patient"})
        self.assertTrue(apply_misnamed_patient_fix("CMS104X", "bad-guuid", "null-null.json",
                                                   tests_root=self.tests_root))
        new_path = os.path.join(bad, "Patient-bad-guuid.json")
        self.assertTrue(os.path.exists(new_path))
        self.assertFalse(os.path.exists(os.path.join(bad, "null-null.json")))
        with open(new_path) as fh:
            data = json.load(fh)
        self.assertEqual(data["id"], "bad-guuid")
        self.assertFalse(apply_misnamed_patient_fix("CMS104X", "bad-guuid", "null-null.json",
                                                    tests_root=self.tests_root))

    def test_collect_anomaly_fixes_lists_misnamed_only(self):
        bad = os.path.join(self.tests_root, "CMS104X", "bad-guuid")
        os.makedirs(bad)
        write_json(bad, "null-null.json", {"resourceType": "Patient"})
        fixes = collect_anomaly_fixes(collect_test_cases(self.tests_root))
        self.assertEqual(fixes, [("CMS104X", "bad-guuid", "null-null.json")])
        self.assertTrue(apply_misnamed_patient_fix(*fixes[0], tests_root=self.tests_root))
        self.assertEqual(collect_anomaly_fixes(collect_test_cases(self.tests_root)), [])


class RequiredPatientFieldTest(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.mkdtemp()
        self.tests_root = self._tmp
        self.good = "11111111-1111-1111-1111-111111111111"
        self.other = "99999999-9999-9999-9999-999999999999"
        self.case = os.path.join(self.tests_root, "CMS104X", self.good)
        os.makedirs(self.case)
        make_patient(self.case, self.good)

    def tearDown(self):
        import shutil
        shutil.rmtree(self._tmp, ignore_errors=True)

    def _cases(self):
        return collect_test_cases(self.tests_root)

    def test_task_missing_for_flagged(self):
        write_json(self.case, "Task-t.json", {"resourceType": "Task"})
        findings, _ = validate(self._cases())
        self.assertEqual(len(findings), 1)
        f = findings[0]
        self.assertEqual(f[3], "for")
        self.assertEqual(f[4], "(missing)")
        self.assertEqual(f[5], self.good)
        self.assertEqual(f[6], "MISSING-REQUIRED-FIELD")

    def test_task_for_wrong_shape_flagged_missing(self):
        # A `for` that is present but not a well-formed Patient/ reference cannot
        # associate the Task with the patient context at runtime next to one that is.
        write_json(self.case, "Task-t.json", {
            "resourceType": "Task",
            "focus": {"reference": "MedicationRequest/9b5c77d2-ba3b-49a2-a6c2-7060b3221c1a"},
            "for": {"display": "Patient with odd GUID"},
        })
        findings, _ = validate(self._cases())
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0][6], "MISSING-REQUIRED-FIELD")

    def test_task_correct_for_not_flagged(self):
        write_json(self.case, "Task-t.json", {
            "resourceType": "Task",
            "for": {"reference": f"Patient/{self.good}"},
        })
        findings, _ = validate(self._cases())
        self.assertEqual(findings, [])

    def test_task_wrong_patient_for_still_broad(self):
        write_json(self.case, "Task-t.json", {
            "resourceType": "Task",
            "for": {"reference": f"Patient/{self.other}"},
        })
        findings, _ = validate(self._cases())
        self.assertEqual(len(findings), 1)
        f = findings[0]
        self.assertEqual(f[3], "for")
        # `self.other` is not a real patient in this narrow universe, so classify
        # may call it PLACEHOLDER; the invariant is that it stays BROAD/NOT-FIXED
        # (reported, never touched by the CORE auto-fix or --fix-task-for).
        self.assertIn("BROAD", f[6])
        self.assertIn("NOT-FIXED", f[6])
        self.assertFalse(collect_fixable(findings))

    def test_encounter_missing_subject_flagged(self):
        # Same failure mode as Task.for, on a different resource type: a missing
        # `subject` on an Encounter is invisible to `context Patient` scoping
        # (I-07 — CMS816FHIRHHHypo), so it's required too, not just Task.for.
        write_json(self.case, "Encounter-e.json", {"resourceType": "Encounter", "status": "finished"})
        findings, _ = validate(self._cases())
        self.assertEqual(len(findings), 1)
        f = findings[0]
        self.assertEqual(f[3], "subject")
        self.assertEqual(f[4], "(missing)")
        self.assertEqual(f[5], self.good)
        self.assertEqual(f[6], "MISSING-REQUIRED-FIELD")

    def test_medicationadministration_missing_subject_flagged(self):
        write_json(self.case, "MedicationAdministration-m.json",
                   {"resourceType": "MedicationAdministration", "status": "completed"})
        findings, _ = validate(self._cases())
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0][3], "subject")
        self.assertEqual(findings[0][6], "MISSING-REQUIRED-FIELD")

    def test_observation_missing_subject_flagged(self):
        write_json(self.case, "Observation-o.json",
                   {"resourceType": "Observation", "status": "final"})
        findings, _ = validate(self._cases())
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0][3], "subject")
        self.assertEqual(findings[0][6], "MISSING-REQUIRED-FIELD")

    def test_other_resource_missing_patient_field_not_flagged(self):
        # The required-field check is deliberately resource-type-scoped: a
        # resource type not listed in REQUIRED_PATIENT_FIELDS (e.g. Claim) is
        # still not flagged for a merely-absent (not wrong) patient reference.
        write_json(self.case, "Claim-c.json", {"resourceType": "Claim"})
        findings, _ = validate(self._cases())
        self.assertEqual(findings, [])

    def test_missing_for_with_sibling_for_present_flagged(self):
        # A missing `for` must be flagged even when a sibling Task in the same
        # folder carries one (discover_patient_fields is folder-scoped and would
        # otherwise mask it).
        write_json(self.case, "Task-a.json", {"resourceType": "Task"})
        write_json(self.case, "Task-b.json", {
            "resourceType": "Task",
            "for": {"reference": f"Patient/{self.good}"},
        })
        findings, _ = validate(self._cases())
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0][2], "Task-a.json")

    def test_apply_task_for_fix_injects_and_positions(self):
        from scripts.validate_test_fixtures import apply_task_for_fix, collect_required_field_findings
        write_json(self.case, "Task-t.json", {
            "resourceType": "Task",
            "id": "t1",
            "focus": {"reference": "MedicationRequest/9b5c77d2-ba3b-49a2-a6c2-7060b3221c1a"},
            "executionPeriod": {"start": "2026-11-01T09:00:00.000+00:00"},
        })
        findings, _ = validate(self._cases())
        fixable = collect_required_field_findings(findings)
        self.assertEqual(len(fixable), 1)
        path = os.path.join(self.case, "Task-t.json")
        self.assertTrue(apply_task_for_fix(fixable[0], tests_root=self.tests_root))
        with open(path) as fh:
            data = json.load(fh)
        keys = list(data.keys())
        self.assertEqual(data["for"], {"reference": f"Patient/{self.good}"})
        # `for` is re-inserted immediately after `focus`; nothing else changed.
        self.assertEqual(keys.index("for"), keys.index("focus") + 1)
        self.assertEqual(data["id"], "t1")
        self.assertEqual(len(data), 5)
        # A second apply is a no-op.
        self.assertFalse(apply_task_for_fix(fixable[0], tests_root=self.tests_root))

    def test_apply_encounter_subject_fix_injects_and_positions(self):
        from scripts.validate_test_fixtures import (
            apply_encounter_subject_fix,
            collect_required_field_findings,
        )
        write_json(self.case, "Encounter-e.json", {
            "resourceType": "Encounter",
            "id": "e1",
            "status": "finished",
            "class": {"code": "IMP"},
        })
        findings, _ = validate(self._cases())
        fixable = collect_required_field_findings(findings)
        self.assertEqual(len(fixable), 1)
        path = os.path.join(self.case, "Encounter-e.json")
        self.assertTrue(apply_encounter_subject_fix(fixable[0], tests_root=self.tests_root))
        with open(path) as fh:
            data = json.load(fh)
        keys = list(data.keys())
        self.assertEqual(data["subject"], {"reference": f"Patient/{self.good}"})
        # `subject` is re-inserted immediately after `status`; nothing else changed.
        self.assertEqual(keys.index("subject"), keys.index("status") + 1)
        self.assertEqual(data["id"], "e1")
        self.assertEqual(len(data), 5)
        # A second apply is a no-op.
        self.assertFalse(apply_encounter_subject_fix(fixable[0], tests_root=self.tests_root))

    def test_apply_required_field_fix_dispatches_by_resource_type(self):
        from scripts.validate_test_fixtures import apply_required_field_fix, collect_required_field_findings
        write_json(self.case, "Task-t.json", {"resourceType": "Task"})
        write_json(self.case, "Encounter-e.json", {"resourceType": "Encounter", "status": "finished"})
        write_json(self.case, "MedicationAdministration-m.json",
                   {"resourceType": "MedicationAdministration", "status": "completed"})
        write_json(self.case, "Observation-o.json", {"resourceType": "Observation", "status": "final"})
        findings, _ = validate(self._cases())
        fixable = collect_required_field_findings(findings)
        self.assertEqual(len(fixable), 4)
        for finding in fixable:
            self.assertTrue(apply_required_field_fix(finding, tests_root=self.tests_root))
        with open(os.path.join(self.case, "Task-t.json")) as fh:
            self.assertEqual(json.load(fh)["for"], {"reference": f"Patient/{self.good}"})
        with open(os.path.join(self.case, "Encounter-e.json")) as fh:
            self.assertEqual(json.load(fh)["subject"], {"reference": f"Patient/{self.good}"})
        with open(os.path.join(self.case, "MedicationAdministration-m.json")) as fh:
            self.assertEqual(json.load(fh)["subject"], {"reference": f"Patient/{self.good}"})
        with open(os.path.join(self.case, "Observation-o.json")) as fh:
            self.assertEqual(json.load(fh)["subject"], {"reference": f"Patient/{self.good}"})

    def test_collect_required_field_findings_filters_category(self):
        from scripts.validate_test_fixtures import collect_required_field_findings
        good = ("CMS104X", self.good, "Task-t.json", "for", self.good, self.good, "BROAD-WRONG-NOT-FIXED")
        missing = ("CMS104X", self.good, "Task-t.json", "for", "(missing)", self.good,
                   "MISSING-REQUIRED-FIELD")
        self.assertEqual(collect_required_field_findings([good, missing]), [missing])


class ProfileNamespaceMigrationTest(unittest.TestCase):

    OLD = "http://fhir.org/guides/onc/us-quality-core/StructureDefinition"
    NEW = "http://fhir.org/guides/astp/us-quality-core/StructureDefinition"

    def setUp(self):
        self._tmp = tempfile.mkdtemp()
        self.tests_root = self._tmp
        self.measure = os.path.join(self.tests_root, "CMS104X")
        self.case = os.path.join(self.measure, "11111111-1111-1111-1111-111111111111")
        os.makedirs(self.case)

    def tearDown(self):
        import shutil
        shutil.rmtree(self._tmp, ignore_errors=True)

    def test_migrate_rewrites_occurrences_in_place(self):
        write_json(self.case, "Observation-o.json",
                   {"resourceType": "Observation",
                    "meta": {"profile": [self.OLD + "/us-quality-core-observation"]}})
        path = os.path.join(self.case, "Observation-o.json")
        from scripts.validate_test_fixtures import migrate_profile_namespace, profile_namespace_occurrences
        self.assertEqual(profile_namespace_occurrences(path), 1)
        self.assertEqual(migrate_profile_namespace(path), 1)
        with open(path) as fh:
            data = json.load(fh)
        self.assertEqual(data["meta"]["profile"][0],
                         self.NEW + "/us-quality-core-observation")
        self.assertEqual(profile_namespace_occurrences(path), 0)

    def test_migrate_dry_run_does_not_write(self):
        write_json(self.case, "Observation-o.json",
                   {"resourceType": "Observation",
                    "extension": [{"url": self.OLD + "/doNotPerformReason"}]})
        path = os.path.join(self.case, "Observation-o.json")
        from scripts.validate_test_fixtures import migrate_profile_namespace
        self.assertEqual(migrate_profile_namespace(path, dry_run=True), 1)
        with open(path) as fh:
            data = json.load(fh)
        self.assertEqual(data["extension"][0]["url"], self.OLD + "/doNotPerformReason")

    def test_migrate_ignores_unrelated_onc_tokens(self):
        # The `onc/not108` DOI (and any `onc/foo`) must be preserved verbatim.
        write_json(self.case, "Patient-11111111-1111-1111-1111-111111111111.json",
                   {"resourceType": "Patient",
                    "id": "11111111-1111-1111-1111-111111111111",
                    "text": {"status": "generated",
                             "div": "<div>onc/not108 a citation</div>"}})
        path = os.path.join(self.case, "Patient-11111111-1111-1111-1111-111111111111.json")
        from scripts.validate_test_fixtures import migrate_profile_namespace
        self.assertEqual(migrate_profile_namespace(path), 0)
        with open(path) as fh:
            data = json.load(fh)
        self.assertIn("onc/not108", data["text"]["div"])

    def test_migrate_non_json_untouched(self):
        with open(os.path.join(self.case, "notes.txt"), "w", encoding="utf-8") as fh:
            fh.write("onc/us-quality-core\n")
        from scripts.validate_test_fixtures import migrate_profile_namespace
        self.assertEqual(migrate_profile_namespace(os.path.join(self.case, "notes.txt")), 0)

    def test_tree_migration_counts_files_and_tokens(self):
        write_json(self.case, "Observation-a.json",
                   {"resourceType": "Observation",
                    "meta": {"profile": [self.OLD + "/one", self.NEW + "/two"]}})
        write_json(self.case, "Observation-b.json",
                   {"resourceType": "Observation",
                    "meta": {"profile": [self.OLD + "/x"]}})
        from scripts.validate_test_fixtures import migrate_profile_namespace_tree, still_uses_old_namespace
        result = migrate_profile_namespace_tree(self.tests_root, dry_run=True)
        self.assertEqual(result["tokens"], 2)
        self.assertEqual(result["scanned"], 2)
        self.assertEqual(len(result["files"]), 2)
        self.assertEqual(len(still_uses_old_namespace(self.tests_root)), 2)
        result = migrate_profile_namespace_tree(self.tests_root)
        self.assertEqual(result["tokens"], 2)
        self.assertEqual(still_uses_old_namespace(self.tests_root), [])


if __name__ == "__main__":
    unittest.main()
