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


def write_json(directory, filename, data, derive_id=True):
    # Default a missing ``id`` from a ``<resourceType>-<id>.json`` filename so
    # fixtures stay well-formed for the resource-ID checks; pass
    # ``derive_id=False`` to write the resource exactly as given.
    prefix = f"{data.get('resourceType')}-" if isinstance(data, dict) else None
    if (derive_id and prefix and "id" not in data
            and filename.startswith(prefix) and filename.endswith(".json")):
        data = {**data, "id": filename[len(prefix):-len(".json")]}
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

    def test_apply_communication_subject_fix_injects_and_positions(self):
        from scripts.validate_test_fixtures import (
            apply_communication_subject_fix,
            collect_required_field_findings,
        )
        write_json(self.case, "Communication-c.json", {
            "resourceType": "Communication",
            "id": "c1",
            "status": "not-done",
            "category": [{"coding": [{"code": "428341000124108"}]}],
        })
        findings, _ = validate(self._cases())
        fixable = collect_required_field_findings(findings)
        self.assertEqual(len(fixable), 1)
        path = os.path.join(self.case, "Communication-c.json")
        self.assertTrue(apply_communication_subject_fix(fixable[0], tests_root=self.tests_root))
        with open(path) as fh:
            data = json.load(fh)
        keys = list(data.keys())
        self.assertEqual(data["subject"], {"reference": f"Patient/{self.good}"})
        # `subject` is re-inserted immediately after `status`; nothing else changed.
        self.assertEqual(keys.index("subject"), keys.index("status") + 1)
        self.assertEqual(data["id"], "c1")
        self.assertEqual(len(data), 5)
        # A second apply is a no-op.
        self.assertFalse(apply_communication_subject_fix(fixable[0], tests_root=self.tests_root))

    def test_apply_required_field_fix_dispatches_by_resource_type(self):
        from scripts.validate_test_fixtures import apply_required_field_fix, collect_required_field_findings
        write_json(self.case, "Task-t.json", {"resourceType": "Task"})
        write_json(self.case, "Encounter-e.json", {"resourceType": "Encounter", "status": "finished"})
        write_json(self.case, "MedicationAdministration-m.json",
                   {"resourceType": "MedicationAdministration", "status": "completed"})
        write_json(self.case, "Observation-o.json", {"resourceType": "Observation", "status": "final"})
        write_json(self.case, "Communication-c.json", {"resourceType": "Communication", "status": "not-done"})
        findings, _ = validate(self._cases())
        fixable = collect_required_field_findings(findings)
        self.assertEqual(len(fixable), 5)
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
        with open(os.path.join(self.case, "Communication-c.json")) as fh:
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


GUID = "11111111-1111-1111-1111-111111111111"


class ResourceIdChecksTest(unittest.TestCase):
    """ID-FILENAME-MISMATCH / ID-DUPLICATE / EVALUATED-REF-* (I-10 residue)."""

    def setUp(self):
        self._tmp = tempfile.mkdtemp()
        self.case = os.path.join(self._tmp, "CMS819X", GUID)
        os.makedirs(self.case)
        make_patient(self.case, GUID)

    def tearDown(self):
        import shutil
        shutil.rmtree(self._tmp, ignore_errors=True)

    def files(self):
        return [os.path.join(self.case, f) for f in sorted(os.listdir(self.case))]

    def categories(self, check_references=False):
        findings, _ = validate([("CMS819X", GUID, self.files())],
                               check_references=check_references)
        return [(f[2], f[4], f[5], f[6]) for f in findings]

    def test_clean_folder_has_no_id_findings(self):
        write_json(self.case, "Encounter-e.json", {
            "resourceType": "Encounter", "subject": {"reference": f"Patient/{GUID}"}})
        self.assertEqual(self.categories(), [])

    def test_filename_id_mismatch_flagged(self):
        write_json(self.case, "Encounter-e.json", {
            "resourceType": "Encounter", "id": "other",
            "subject": {"reference": f"Patient/{GUID}"}})
        self.assertEqual(self.categories(), [
            ("Encounter-e.json", "Encounter/other", "Encounter-other.json",
             "ID-FILENAME-MISMATCH")])

    def test_missing_id_flagged(self):
        write_json(self.case, "Encounter-e.json", {
            "resourceType": "Encounter", "subject": {"reference": f"Patient/{GUID}"}},
            derive_id=False)
        self.assertEqual(self.categories(), [
            ("Encounter-e.json", "(missing)", "(no id)", "ID-FILENAME-MISMATCH")])

    def test_duplicate_id_across_files_flagged(self):
        for name in ("MedicationAdministration-m.json", "MedicationAdministration-m-copy.json"):
            write_json(self.case, name, {
                "resourceType": "MedicationAdministration", "id": "m",
                "subject": {"reference": f"Patient/{GUID}"}})
        dups = [c for c in self.categories() if c[3] == "ID-DUPLICATE"]
        self.assertEqual(sorted(dups), [
            ("MedicationAdministration-m-copy.json", "MedicationAdministration/m", "2 files", "ID-DUPLICATE"),
            ("MedicationAdministration-m.json", "MedicationAdministration/m", "2 files", "ID-DUPLICATE")])

    def test_repeated_and_dangling_evaluated_resources(self):
        # Mirrors CMS819 73b0c1fe: three administrations collapsed onto one id.
        write_json(self.case, "MedicationAdministration-m.json", {
            "resourceType": "MedicationAdministration",
            "subject": {"reference": f"Patient/{GUID}"}})
        write_json(self.case, "MeasureReport-r.json", {
            "resourceType": "MeasureReport",
            "evaluatedResource": [
                {"reference": f"Patient/{GUID}"},
                {"reference": "MedicationAdministration/m"},
                {"reference": "MedicationAdministration/m"},
                {"reference": "MedicationAdministration/m"},
                {"reference": "Encounter/gone"},
                {"reference": "#contained-params"},
                {"reference": "#contained-params"},
            ]})
        self.assertEqual(self.categories(), [
            ("MeasureReport-r.json", "Encounter/gone", "(no file)", "EVALUATED-REF-DANGLING"),
            ("MeasureReport-r.json", "MedicationAdministration/m", "3x", "EVALUATED-REF-REPEATED")])

    def test_unresolved_references_are_opt_in_and_split_by_type(self):
        write_json(self.case, "Location-here.json", {"resourceType": "Location"})
        write_json(self.case, "Encounter-e.json", {
            "resourceType": "Encounter",
            "subject": {"reference": f"Patient/{GUID}"},
            "location": [{"location": {"reference": "Location/HSLOC-1096-7"}},
                         {"location": {"reference": "Location/here"}}],
            "participant": [{"individual": {"reference": "Practitioner/p1"}}],
            "serviceProvider": {"reference": "https://example.org/fhir/Organization/o1"},
            "basedOn": [{"reference": "#contained"}, {"reference": "urn:uuid:abc"}]})
        self.assertEqual(self.categories(), [])
        findings, _ = validate([("CMS819X", GUID, self.files())], check_references=True)
        self.assertEqual(sorted((f[3], f[4], f[6]) for f in findings), [
            ("Encounter.location.location", "Location/HSLOC-1096-7", "REF-UNRESOLVED-CLINICAL"),
            ("Encounter.participant.individual", "Practitioner/p1", "REF-UNRESOLVED-ACTOR")])

    def test_versioned_reference_resolves(self):
        write_json(self.case, "Condition-c.json", {
            "resourceType": "Condition", "subject": {"reference": f"Patient/{GUID}"}})
        write_json(self.case, "Encounter-e.json", {
            "resourceType": "Encounter", "subject": {"reference": f"Patient/{GUID}"},
            "diagnosis": [{"condition": {"reference": "Condition/c/_history/2"}}]})
        self.assertEqual(self.categories(check_references=True), [])

    def test_basename_split_on_every_platform_separator(self):
        # | Platform              | Path                                   | Basename         |
        # | macOS / Linux         | /tmp/case/Encounter-e.json             | Encounter-e.json |
        # | Windows backslash     | C:\tmp\case\Encounter-e.json           | Encounter-e.json |
        # | Windows forward slash | C:/tmp/case/Encounter-e.json           | Encounter-e.json |
        from scripts.validate_test_fixtures import _basename
        for path in ("/tmp/case/Encounter-e.json", "C:\\tmp\\case\\Encounter-e.json",
                     "C:/tmp/case/Encounter-e.json"):
            self.assertEqual(_basename(path), "Encounter-e.json", path)


def ma_entry(rid, code, start, patient="p"):
    return {"fullUrl": f"https://madie.cms.gov/MedicationAdministration/{rid}",
            "resource": {"resourceType": "MedicationAdministration", "id": rid,
                         "medicationCodeableConcept": {"coding": [{"code": code}]},
                         "subject": {"reference": f"Patient/{patient}"},
                         "effectivePeriod": {"start": start}}}


def patient_entry(pid="p"):
    return {"fullUrl": f"https://madie.cms.gov/Patient/{pid}",
            "resource": {"resourceType": "Patient", "id": pid}}


class BundleCheckTest(unittest.TestCase):
    """--bundle mode: duplicate ids in a MADiE source Bundle, before splitting."""

    # Reduction of the CMS819 627a80a1... export behind I-10: three
    # administrations (naloxone in OR, later opioid, later naloxone) share one id.
    CMS819_BUNDLE = {"resourceType": "Bundle", "type": "collection", "entry": [
        ma_entry("5f32cff097c3b600003f7cb9", "1010600", "2028-02-01T09:00:00.000+00:00"),
        ma_entry("5f32d03297c3b600003f7cd9", "1659929", "2028-02-01T10:00:00.000+00:00"),
        ma_entry("5f32d03297c3b600003f7cd9", "1010600", "2028-02-07T08:00:00.000+00:00"),
        ma_entry("5f32d03297c3b600003f7cd9", "1870933", "2028-02-07T20:00:00.000+00:00"),
    ]}

    def test_cms819_collision_is_divergent(self):
        from scripts.validate_test_fixtures import check_bundle
        self.assertEqual(check_bundle(self.CMS819_BUNDLE), [
            {"kind": "resource", "key": "MedicationAdministration/5f32d03297c3b600003f7cd9",
             "indices": [1, 2, 3], "identical": False},
            {"kind": "fullUrl",
             "key": "https://madie.cms.gov/MedicationAdministration/5f32d03297c3b600003f7cd9",
             "indices": [1, 2, 3], "identical": False}])

    def test_identical_duplicates_reported_as_identical(self):
        from scripts.validate_test_fixtures import check_bundle
        entry = ma_entry("a", "1010600", "2026-01-01T00:00:00Z")
        results = check_bundle({"resourceType": "Bundle", "entry": [entry, json.loads(json.dumps(entry))]})
        self.assertEqual([r["identical"] for r in results], [True, True])

    def test_clean_bundle_has_no_findings(self):
        from scripts.validate_test_fixtures import check_bundle
        bundle = {"resourceType": "Bundle", "entry": [
            ma_entry("a", "1010600", "2026-01-01T00:00:00Z"),
            ma_entry("b", "1010600", "2026-01-02T00:00:00Z")]}
        self.assertEqual(check_bundle(bundle), [])

    def test_duplicate_fullurl_with_different_ids(self):
        from scripts.validate_test_fixtures import check_bundle
        a, b = ma_entry("a", "1", "2026-01-01"), ma_entry("b", "1", "2026-01-01")
        b["fullUrl"] = a["fullUrl"]
        self.assertEqual(check_bundle({"resourceType": "Bundle", "entry": [a, b]}), [
            {"kind": "fullUrl", "key": a["fullUrl"], "indices": [0, 1], "identical": False}])

    def run_main(self, bundle):
        from unittest import mock
        from scripts import validate_test_fixtures
        tmp = tempfile.mkdtemp()
        try:
            path = write_json(tmp, "bundle.json", bundle, derive_id=False)
            with mock.patch("sys.argv", ["validate_test_fixtures.py", "--bundle", path]), \
                    mock.patch("sys.stdout"):
                try:
                    validate_test_fixtures.main()
                except SystemExit as exc:
                    return exc.code
            return 0
        finally:
            import shutil
            shutil.rmtree(tmp, ignore_errors=True)

    def test_cli_exit_codes(self):
        self.assertEqual(self.run_main(self.CMS819_BUNDLE), 1)
        self.assertEqual(self.run_main({"resourceType": "Bundle", "entry": [
            patient_entry(), ma_entry("a", "1", "2026-01-01")]}), 0)

    def test_cli_warnings_alone_exit_zero_errors_exit_one(self):
        warn = {"resourceType": "Bundle", "entry": [
            patient_entry(),
            {"resource": {"resourceType": "Encounter", "id": "e",
                          "subject": {"reference": "Patient/p"},
                          "location": [{"location": {"reference": "Location/gone"}}]}}]}
        self.assertEqual(self.run_main(warn), 0)
        missing_subject = {"resourceType": "Bundle", "entry": [
            patient_entry(), {"resource": {"resourceType": "Encounter", "id": "e"}}]}
        self.assertEqual(self.run_main(missing_subject), 1)


class LintBundleTest(unittest.TestCase):
    """--bundle per-resource checks: what MADiE's JS engine tolerates."""

    def lint(self, *entries):
        from scripts.validate_test_fixtures import lint_bundle
        return [(f["key"], f["field"], f["referenced"], f["category"])
                for f in lint_bundle({"resourceType": "Bundle", "entry": list(entries)})]

    def test_clean_bundle(self):
        self.assertEqual(self.lint(patient_entry(), ma_entry("a", "1", "2026-01-01")), [])

    def test_wrong_patient_flagged(self):
        self.assertEqual(self.lint(patient_entry(), ma_entry("a", "1", "2026-01-01", patient="q")), [
            ("MedicationAdministration/a", "subject", "Patient/q", "BUNDLE-WRONG-PATIENT")])

    def test_missing_required_subject_flagged(self):
        entry = ma_entry("a", "1", "2026-01-01")
        del entry["resource"]["subject"]
        self.assertEqual(self.lint(patient_entry(), entry), [
            ("MedicationAdministration/a", "subject", "(missing)", "MISSING-REQUIRED-FIELD")])

    def test_no_or_several_patients_flagged(self):
        self.assertEqual(self.lint(ma_entry("a", "1", "2026-01-01")), [
            (None, "Patient", "(none)", "BUNDLE-PATIENT-AMBIGUOUS")])
        self.assertEqual(self.lint(patient_entry("p"), patient_entry("q"))[0][3],
                         "BUNDLE-PATIENT-AMBIGUOUS")

    def test_unresolved_reference_split_by_type(self):
        enc = {"resource": {"resourceType": "Encounter", "id": "e",
                            "subject": {"reference": "Patient/p"},
                            "location": [{"location": {"reference": "Location/gone"}}],
                            "serviceProvider": {"reference": "Organization/o"}}}
        self.assertEqual(sorted(self.lint(patient_entry(), enc)), [
            ("Encounter/e", "Encounter.location.location", "Location/gone", "REF-UNRESOLVED-CLINICAL"),
            ("Encounter/e", "Encounter.serviceProvider", "Organization/o", "REF-UNRESOLVED-ACTOR")])


RXNORM = "http://www.nlm.nih.gov/research/umls/rxnorm"
SCT = "http://snomed.info/sct"
UQC_MA = ("http://fhir.org/guides/astp/us-quality-core/StructureDefinition/"
          "us-quality-core-medicationadministration")
QICORE_MA = "http://hl7.org/fhir/us/qicore/StructureDefinition/qicore-medicationadministration"
CASE_GUID = "73b0c1fe-874b-4982-8cb2-3c30520441de"
SRC_PATIENT = "1994e69a-472b-4e32-80c1-5c692f36acce"
SC_ROUTE = {"route": {"coding": [{"system": SCT, "code": "34206005",
                                  "display": "Subcutaneous route (qualifier value)"}]}}


def med_admin(rid, profile, patient, code, display, start, end=None, route=False):
    period = {"start": start, **({"end": end} if end else {})}
    resource = {"resourceType": "MedicationAdministration", "id": rid,
                "meta": {"profile": [profile]}, "status": "completed",
                "medicationCodeableConcept": {"coding": [
                    {"system": RXNORM, "code": code, "display": display}]},
                "subject": {"reference": f"Patient/{patient}"}, "effectivePeriod": period}
    if route:
        resource["dosage"] = SC_ROUTE
    return resource


def encounter(rid, patient, year):
    return {"resourceType": "Encounter", "id": rid, "status": "finished",
            "class": {"system": "http://terminology.hl7.org/CodeSystem/v3-ActCode", "code": "IMP"},
            "type": [{"coding": [{"system": SCT, "code": "183452005"}]}],
            "subject": {"reference": f"Patient/{patient}"},
            "period": {"start": f"{year}-01-08T08:00:00.000+00:00",
                       "end": f"{year}-02-08T08:15:00.000+00:00"},
            "location": [{"location": {"reference": "Location/HSLOC-1096-7"},
                          "period": {"start": f"{year}-02-01T08:00:00.000+00:00",
                                     "end": f"{year}-02-01T10:15:00.000+00:00"}}]}


# CMS819 73b0c1fe as exported from MADiE (2028 dates, QI-Core profiles, one id on
# three administrations), reduced to the fields the restore logic reads.
CMS819_SOURCE = {"resourceType": "Bundle", "type": "collection", "entry": [{"resource": r} for r in [
    {"resourceType": "Patient", "id": SRC_PATIENT, "birthDate": "1983-11-14"},
    encounter("5f32cfdc97c3b600003f7c9c", SRC_PATIENT, 2028),
    med_admin("5f32cff097c3b600003f7cb9", QICORE_MA, SRC_PATIENT, "1010600", "Opioid",
              "2028-02-01T09:00:00.000+00:00", "2028-02-01T09:00:00.000+00:00"),
    med_admin("5f32d03297c3b600003f7cd9", QICORE_MA, SRC_PATIENT, "1659929", "Naloxone",
              "2028-02-01T10:00:00.000+00:00", route=True),
    med_admin("5f32d03297c3b600003f7cd9", QICORE_MA, SRC_PATIENT, "1010600", "Opioid",
              "2028-02-07T08:00:00.000+00:00", "2028-02-07T08:15:00.000+00:00"),
    med_admin("5f32d03297c3b600003f7cd9", QICORE_MA, SRC_PATIENT, "1870933", "Naloxone",
              "2028-02-07T20:00:00.000+00:00", route=True),
]]}


class RestoreFromBundleTest(unittest.TestCase):
    """--restore-from-bundle: draft what a duplicate-id bundle lost (I-76)."""

    def setUp(self):
        self._tmp = tempfile.mkdtemp()
        self.tests_root = os.path.join(self._tmp, "measure")
        self.case = os.path.join(self.tests_root, "CMS819X", CASE_GUID)
        os.makedirs(self.case)
        # The fixture as split, before the 2026-10-13 fix: 2026 dates, US Quality
        # Core profiles, new ids, only the last of the three colliding entries.
        write_json(self.case, f"Patient-{CASE_GUID}.json",
                   {"resourceType": "Patient", "id": CASE_GUID, "birthDate": "1981-11-14"})
        write_json(self.case, "Encounter-52b6c77f.json", encounter("52b6c77f", CASE_GUID, 2026))
        write_json(self.case, "MedicationAdministration-6d2c5396.json", med_admin(
            "6d2c5396", UQC_MA, CASE_GUID, "1010600", "Opioid",
            "2026-02-01T09:00:00.000+00:00", "2026-02-01T09:00:00.000+00:00"))
        write_json(self.case, "MedicationAdministration-6a7ab547.json", med_admin(
            "6a7ab547", UQC_MA, CASE_GUID, "1870933", "Naloxone",
            "2026-02-07T20:00:00.000+00:00", route=True))
        write_json(self.case, "MeasureReport-15d9e04f.json", {
            "resourceType": "MeasureReport", "evaluatedResource": [
                {"reference": f"Patient/{CASE_GUID}"}, {"reference": "Encounter/52b6c77f"},
                {"reference": "MedicationAdministration/6d2c5396"},
                {"reference": "MedicationAdministration/6a7ab547"},
                {"reference": "MedicationAdministration/6a7ab547"},
                {"reference": "MedicationAdministration/6a7ab547"}]})

    def tearDown(self):
        import shutil
        shutil.rmtree(self._tmp, ignore_errors=True)

    def files(self):
        return [os.path.join(self.case, f) for f in sorted(os.listdir(self.case))]

    def plan(self):
        from scripts.validate_test_fixtures import plan_restore
        ids = iter(["new-1", "new-2", "new-3"])
        return plan_restore(CMS819_SOURCE, self.files(), CASE_GUID, new_id=lambda: next(ids))

    def test_shift_date(self):
        from scripts.validate_test_fixtures import _shift_date
        self.assertEqual(_shift_date("2028-02-07T20:00:00.000+00:00", -2),
                         "2026-02-07T20:00:00.000+00:00")
        self.assertEqual(_shift_date("1983-11-14", -2), "1981-11-14")
        self.assertEqual(_shift_date("2028", -2), "2026")
        self.assertEqual(_shift_date("2028-02-29", -1), "2027-02-28")
        self.assertEqual(_shift_date("2028-02-29", -4), "2024-02-29")
        self.assertEqual(_shift_date("1659929", -2), "1659929")
        self.assertEqual(_shift_date("2028-02-07", 0), "2028-02-07")

    def test_codes_are_not_shifted(self):
        from scripts.validate_test_fixtures import _map_dates
        self.assertEqual(_map_dates({"code": "1984", "start": "1984"}, 1),
                         {"code": "1984", "start": "1985"})

    def test_detects_year_shift(self):
        from scripts.validate_test_fixtures import detect_year_shift, load_json
        fixtures = [load_json(p) for p in self.files()]
        bundle = [e["resource"] for e in CMS819_SOURCE["entry"]]
        self.assertEqual(detect_year_shift(bundle, fixtures), -2)
        self.assertEqual(detect_year_shift(bundle[:1], fixtures), -2)  # Patient birthDate alone
        self.assertEqual(detect_year_shift(fixtures, fixtures), 0)     # already in fixture years
        self.assertEqual(detect_year_shift([], fixtures), 0)           # no evidence

    def test_drafts_reproduce_the_hand_restored_files(self):
        plan = self.plan()
        self.assertEqual(plan["year_shift"], -2)
        self.assertEqual(plan["notes"], [])
        self.assertEqual([(m["status"], m.get("fixture_key") or m.get("draft_key"))
                          for m in plan["groups"][0]["members"]], [
            ("lost", "MedicationAdministration/new-1"),
            ("lost", "MedicationAdministration/new-2"),
            ("present", "MedicationAdministration/6a7ab547")])
        self.assertEqual(plan["drafts"], {
            "MedicationAdministration-new-1.json": med_admin(
                "new-1", UQC_MA, CASE_GUID, "1659929", "Naloxone",
                "2026-02-01T10:00:00.000+00:00", route=True),
            "MedicationAdministration-new-2.json": med_admin(
                "new-2", UQC_MA, CASE_GUID, "1010600", "Opioid",
                "2026-02-07T08:00:00.000+00:00", "2026-02-07T08:15:00.000+00:00")})

    def test_measure_report_rewritten_in_bundle_order(self):
        name, report = self.plan()["measure_report"]
        self.assertEqual(name, "MeasureReport-15d9e04f.json")
        self.assertEqual([e["reference"] for e in report["evaluatedResource"]][3:], [
            "MedicationAdministration/new-1", "MedicationAdministration/new-2",
            "MedicationAdministration/6a7ab547"])

    def test_nothing_to_restore_once_fixed(self):
        write_json(self.case, "MedicationAdministration-a3ebcb6c.json", med_admin(
            "a3ebcb6c", UQC_MA, CASE_GUID, "1659929", "Naloxone",
            "2026-02-01T10:00:00.000+00:00", route=True))
        write_json(self.case, "MedicationAdministration-18cc43f1.json", med_admin(
            "18cc43f1", UQC_MA, CASE_GUID, "1010600", "Opioid",
            "2026-02-07T08:00:00.000+00:00", "2026-02-07T08:15:00.000+00:00"))
        plan = self.plan()
        self.assertEqual(plan["drafts"], {})
        self.assertIsNone(plan["measure_report"])
        self.assertEqual({m["status"] for m in plan["groups"][0]["members"]}, {"present"})

    def test_shared_full_url_with_distinct_ids_is_restored(self):
        # CMS819 31b40acc: Encounter-2 and Encounter-1 share one fullUrl; the
        # split kept the last (Encounter-1), dropping the second encounter.
        from scripts.validate_test_fixtures import plan_restore
        url = "https://madie.cms.gov/Encounter/Encounter-1"
        late = encounter("Encounter-2", SRC_PATIENT, 2028)
        late["period"] = {"start": "2028-10-30T08:00:00.000+00:00",
                          "end": "2028-11-09T08:15:00.000+00:00"}
        del late["location"]
        bundle = {"resourceType": "Bundle", "entry": [
            {"fullUrl": f"https://madie.cms.gov/Patient/{SRC_PATIENT}", "resource": CMS819_SOURCE["entry"][0]["resource"]},
            {"fullUrl": url, "resource": late},
            {"fullUrl": url, "resource": encounter("Encounter-1", SRC_PATIENT, 2028)}]}
        write_json(self.case, "MeasureReport-15d9e04f.json", {
            "resourceType": "MeasureReport", "evaluatedResource": [
                {"reference": "Encounter/52b6c77f"}, {"reference": "Encounter/52b6c77f"}]})
        plan = plan_restore(bundle, self.files(), CASE_GUID, new_id=lambda: "new-enc")
        self.assertEqual([(m["status"], m.get("fixture_key") or m.get("draft_key"))
                          for m in plan["groups"][0]["members"]],
                         [("lost", "Encounter/new-enc"), ("present", "Encounter/52b6c77f")])
        draft = plan["drafts"]["Encounter-new-enc.json"]
        self.assertEqual(draft["period"], {"start": "2026-10-30T08:00:00.000+00:00",
                                           "end": "2026-11-09T08:15:00.000+00:00"})
        self.assertEqual(draft["subject"], {"reference": f"Patient/{CASE_GUID}"})
        self.assertEqual([e["reference"] for e in plan["measure_report"][1]["evaluatedResource"]],
                         ["Encounter/new-enc", "Encounter/52b6c77f"])

    def test_bundle_without_collisions_restores_nothing(self):
        from scripts.validate_test_fixtures import plan_restore
        clean = {"resourceType": "Bundle", "entry": CMS819_SOURCE["entry"][:3]}
        plan = plan_restore(clean, self.files(), CASE_GUID)
        self.assertEqual((plan["groups"], plan["drafts"], plan["measure_report"]), ([], {}, None))

    def test_cli_writes_drafts_to_out_only(self):
        from unittest import mock
        from scripts import validate_test_fixtures
        before = {f: open(os.path.join(self.case, f)).read() for f in os.listdir(self.case)}
        bundle_path = write_json(self._tmp, "bundle.json", CMS819_SOURCE, derive_id=False)
        out = os.path.join(self._tmp, "out")
        argv = ["validate_test_fixtures.py", "--restore-from-bundle", bundle_path,
                "--case", f"CMS819X/{CASE_GUID}", "--out", out]
        with mock.patch("sys.argv", argv), mock.patch("sys.stdout"), \
                mock.patch.object(validate_test_fixtures, "TESTS_ROOT", self.tests_root):
            validate_test_fixtures.main()
        written = sorted(os.listdir(os.path.join(out, "restore", "CMS819X", CASE_GUID)))
        self.assertEqual(len([f for f in written if f.startswith("MedicationAdministration-")]), 2)
        self.assertIn("MeasureReport-15d9e04f.json", written)
        self.assertIn("restore-report.md", written)
        self.assertEqual({f: open(os.path.join(self.case, f)).read()
                          for f in os.listdir(self.case)}, before)


if __name__ == "__main__":
    unittest.main()
