#!/usr/bin/env python3
"""Validate FHIR test-case fixtures for internal-reference consistency.

Each test-case folder under ``input/tests/measure/<Measure>/<patient-guid>/`` is
self-contained and holds exactly one ``Patient-<guid>.json``.  CQL evaluates in a
``context Patient`` scoped to that single patient, so any resource whose
patient-identity reference points at a *different* (or non-existent) patient is
invisible to the measure logic and silently produces empty retrieves / false
populations (a data-authoring error, not a CQL bug - see
``defect-tracking/known-issues.md``, I-41 / I-42 / I-46).

This script walks every test-case folder, determines the authoritative patient
GUID (the ``id`` of the lone ``Patient-*.json``), discovers every top-level
field that carries a ``Patient/...`` reference, and classifies each mismatch.

Folders whose Patient resource is misnamed (e.g. a template artifact like
``null-null.json`` instead of ``Patient-<guid>.json``) are reported as fixable
structural anomalies; ``--fix --apply`` renames them and injects the folder
GUID as ``id``.

Fields split into two tiers:

* **Core** patient-identity fields - ``subject``, ``patient``, ``beneficiary``.
  These are the ones the engine's ``context Patient`` scoping actually keys on,
  so a mismatch here is what breaks measure logic (e.g. ``subject`` on
  Encounter/Condition/Observation, ``patient`` on Claim/AllergyIntolerance,
  ``beneficiary`` on Coverage).  Auto-fix rewrites only these.
* **Broad** patient-reference fields discovered elsewhere (e.g. ``Task.for`` /
  ``Task.focus``, ``Coverage.subscriber`` / ``Coverage.policyHolder``,
  ``MedicationRequest.requester`` / ``MedicationRequest.reportedReference``).
  These are reported but never auto-fixed, because they may legitimately
  reference a different actor (a practitioner, a reporter) or a different
  person (subscriber vs beneficiary).

A presence check is additionally enforced for a small set of fields the engine
*requires* on a given resource type for ``context Patient`` scoping to work at
all: e.g. ``Task.for`` is the model's patient ``contextPath`` for Task
retrieves, so a Task missing it is silently filtered out of every
``[Task...]`` retrieve (an empty result is a data-authoring error, not a CQL
bug) - the same is true of ``subject`` on Encounter, Observation, and
MedicationAdministration.  See ``REQUIRED_PATIENT_FIELDS``. This is exactly
what was needed to fix CMS816FHIRHHHypo's 12 failing test cases (I-07): 17 of
its 28 fixture Encounter resources had no ``subject`` at all, so the engine
silently dropped them from every retrieve regardless of how correctly their
type/status/period were authored.
``--fix-required-fields`` injects the missing reference
(``Patient/<folder patient guid>``) using a dedicated fixer function per
resource type (``apply_task_for_fix``, ``apply_encounter_subject_fix``,
``apply_medicationadministration_subject_fix``,
``apply_observation_subject_fix``); it is scrubbed separately from the CORE
auto-fix so the generic patient-reference rewrite never touches it.

Run from the repo root (Python 3.12):

    python ./scripts/validate_test_fixtures.py                 # report only
    python ./scripts/validate_test_fixtures.py --measure CMS104 # one measure
    python ./scripts/validate_test_fixtures.py --json          # machine output
    python ./scripts/validate_test_fixtures.py --fix --apply   # rewrite CORE fields
    python ./scripts/validate_test_fixtures.py --fix-required-fields --apply  # inject missing for/subject

    python ./scripts/validate_test_fixtures.py --fix-profile-ns               # dry-run: report only
    python ./scripts/validate_test_fixtures.py --fix-profile-ns --apply       # migrate onc->astp base

``--fix-profile-ns`` migrates fixtures that still carry the legacy
``onc/us-quality-core`` universal-profile base to ``astp/us-quality-core``.  It
implies dry-run unless ``--apply`` is given, rewrites only ``*.json`` files
under ``input/tests/measure``, is anchored to the ``us-quality-core`` token (so
unrelated ``onc/*`` strings like the ``onc/not108`` DOI are untouched), and
never commits anything - ``--apply`` leaves the change unstaged for review.
"""

import argparse
import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple

# Fixtures and this script both live in this repo; paths below are relative to
# the repo root, matching every other script under scripts/ (run with
# `python ./scripts/validate_test_fixtures.py` from the repo root).
TESTS_ROOT = os.path.join("input", "tests", "measure")

# Core patient-identity fields - the ones that CQL `context Patient` scoping and
# measure-retrieve logic depend on.  Auto-fix is restricted to this set.
CORE_PATIENT_FIELDS = ("subject", "patient", "beneficiary")

PATIENT_REF_RE = re.compile(r"^Patient/(?P<id>[A-Za-z0-9\-]+)$")

# Patient-identity fields that MUST be present on a given resourceType for the
# engine's `context Patient` scoping to work.  The engine evaluates the model's
# patient `contextPath` per resource (BaseRetrieveProvider.filterByContext); if
# the path resolves to nothing the resource is silently skipped, so a Task
# without `for` is invisible to every `[Task...]` retrieve that references it.
# A field that is present but not a well-formed `Patient/<guid>` reference is
# treated the same as missing.
REQUIRED_PATIENT_FIELDS = {
    "Task": ("for",),
    "Encounter": ("subject",),
    "MedicationAdministration": ("subject",),
    "Observation": ("subject",),
}

Finding = Tuple[str, str, str, str, str, str, str]  # (measure, patient, file, field, referenced, expected, category)

# Universal profile namespace: the US Quality Core IG base.  Fixtures generated
# under the older `onc` publisher namespace carry `http://fhir.org/guides/onc/
# us-quality-core/StructureDefinition/...`; the canonical base is now `astp`.
# This exact-token replacement is anchored to `us-quality-core` so other `onc/*`
# tokens (e.g. the `onc/not108` DOI cited in measure resources) are untouched.
UNIVERSAL_PROFILE_OLD = "onc/us-quality-core"
UNIVERSAL_PROFILE_NEW = "astp/us-quality-core"


def load_json(path: str) -> Optional[Dict]:
    """Load a JSON file, returning None on any parse error."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def _patient_ref_guid(value) -> Optional[str]:
    """Return the patient GUID if ``value`` is a {reference: 'Patient/<guid>'}
    dict, else None.  Ignores non-reference (e.g. display-style) shapes."""
    if not isinstance(value, dict):
        return None
    ref = value.get("reference")
    if not isinstance(ref, str):
        return None
    match = PATIENT_REF_RE.match(ref)
    if not match:
        return None
    return match.group("id")


def collect_test_cases(tests_root: str = TESTS_ROOT) -> List[Tuple[str, str, List[str]]]:
    """Return [(measure, patient_guid, [resource_json_paths])] for every test-case
    folder.  A measure is every immediate subdir of <tests_root>; a test case is
    every subdir of a measure.  Folders with no Patient resource are still yielded
    so the caller can flag the structural anomaly."""
    cases: List[Tuple[str, str, List[str]]] = []
    if not os.path.isdir(tests_root):
        return cases
    for measure in sorted(os.listdir(tests_root)):
        measure_dir = os.path.join(tests_root, measure)
        if not os.path.isdir(measure_dir):
            continue
        for guid in sorted(os.listdir(measure_dir)):
            case_dir = os.path.join(measure_dir, guid)
            if not os.path.isdir(case_dir):
                continue
            resources = [os.path.join(case_dir, f) for f in sorted(os.listdir(case_dir))
                         if f.endswith(".json")]
            cases.append((measure, guid, resources))
    return cases


def expected_patient_for(patient_files: List[str]) -> Optional[str]:
    """Determine the authoritative patient GUID from the folder's Patient
    resource(s): the ``id`` field of the Patient file whose basename match
    ``Patient-<guid>.json``.  Returns None if there isn't exactly one
    unambiguous Patient file."""
    ids: Set[str] = set()
    for pf in patient_files:
        data = load_json(pf)
        if data and data.get("resourceType") == "Patient":
            pid = data.get("id")
            if isinstance(pid, str):
                ids.add(pid)
            base = os.path.basename(pf)
            if base.startswith("Patient-") and base.endswith(".json"):
                ids.add(base[len("Patient-"):-len(".json")])
    if len(ids) == 1:
        return next(iter(ids))
    return None


def is_patient_resource(path: str) -> bool:
    """True if the JSON at ``path`` is a FHIR Patient resource regardless of the
    file's name (misnamed templates like ``null-null.json`` still count)."""
    data = load_json(path)
    return bool(data) and data.get("resourceType") == "Patient"


def patient_resource_files(resources: List[str]) -> List[str]:
    """The subset of resource file paths whose JSON is a Patient resource."""
    return [p for p in resources if is_patient_resource(p)]


def misnamed_patient_file(resources: List[str]) -> Optional[str]:
    """Return the basename of the misnamed but otherwise-valid Patient resource in
    a folder, or None.  A folder is a fixable anomaly when it holds exactly one
    Patient-typed resource (``null-null.json`` is the known template artifact)
    whose name does not follow the ``Patient-<guid>.json`` convention."""
    patient_files = patient_resource_files(resources)
    if len(patient_files) != 1:
        return None
    base = os.path.basename(patient_files[0])
    if base.startswith("Patient-") and base.endswith(".json"):
        return None
    return base


def discover_patient_fields(resource_paths: List[str]) -> Set[str]:
    """Auto-discovery: return every top-level field that carries a Patient/
    reference across the given resource files."""
    fields: Set[str] = set()
    for path in resource_paths:
        data = load_json(path)
        if not data or data.get("resourceType") == "MeasureReport":
            continue
        for key, value in data.items():
            if _patient_ref_guid(value) is not None:
                fields.add(key)
    return fields


def classify(referenced: str, expected: str, patient_ids: Set[str], field: str,
             measure: str) -> str:
    """Classify a patient-reference mismatch into a category string.

    Categories:
      CORE-WRONG    - core field points at a real-but-different patient GUID
      CORE-PLACEHOLDER - core field points at a GUID that is not any real patient
                      (template-generation artifact, e.g. d170a0a8-...)
      BROAD-NOT-FIXED - non-core field mismatch (reported, never auto-fixed)
    """
    tier = "CORE" if field in CORE_PATIENT_FIELDS else "BROAD"
    if referenced not in patient_ids:
        kind = "PLACEHOLDER"
    else:
        kind = "WRONG"
    return f"{tier}-{kind}-{'FIXABLE' if tier == 'CORE' else 'NOT-FIXED'}"


def repo_wide_patient_ids(tests_root: str = TESTS_ROOT) -> Set[str]:
    """Return every patient GUID that exists anywhere as a real test case (folder
    name or Patient resource id).  Computed against the full tree so that the
    placeholder-vs-wrong classification is stable regardless of a `--measure`
    scope filter."""
    return patient_ids_from_cases(collect_test_cases(tests_root))


def patient_ids_from_cases(test_cases) -> Set[str]:
    """Derive the universe of real patient GUIDs from a list of test cases
    (test_cases are ``(measure, guid, [resource_files])`` tuples).  Includes each
    case's folder GUID plus the ``id`` of every Patient-typed resource file."""
    ids: Set[str] = set()
    for _measure, guid, resources in test_cases:
        ids.add(guid)
        for pf in resources:
            data = load_json(pf)
            if data and data.get("resourceType") == "Patient" and isinstance(data.get("id"), str):
                ids.add(data["id"])
    return ids


def validate(test_cases, verbose: bool = False,
             all_patient_ids: Optional[Set[str]] = None) -> Tuple[List[Finding], List[str]]:
    """Run validation over all test cases.

    Returns (findings, structural_anomalies).  ``structural_anomalies`` captures
    folders without an unambiguous Patient resource (can't be validated).

    ``all_patient_ids`` is the universe of real patient GUIDs used to
    distinguish "wrong but real patient" from "placeholder/non-existent"; if not
    supplied it is derived from the given ``test_cases`` themselves."""
    findings: List[Finding] = []
    anomalies: List[str] = []

    if all_patient_ids is None:
        all_patient_ids = patient_ids_from_cases(test_cases)

    for measure, guid, resources in test_cases:
        patient_files = patient_resource_files(resources)
        if not patient_files:
            anomalies.append(f"{measure}/{guid}: cannot determine patient (found "
                             f"0 Patient resource(s))")
            if verbose:
                print(f"  [anomaly] {measure}/{guid} - no Patient resource")
            continue
        misnamed = misnamed_patient_file(resources)
        if misnamed is not None:
            expected = guid
            anomalies.append(f"{measure}/{guid}: Patient resource {misnamed} "
                             f"misnamed (expected Patient-{guid}.json)")
            if verbose:
                print(f"  [anomaly] {measure}/{guid} - misnamed Patient {misnamed}")
        else:
            expected = expected_patient_for(patient_files)
            if expected is None:
                anomalies.append(f"{measure}/{guid}: cannot determine patient (found "
                                 f"{len(patient_files)} Patient resource(s))")
                if verbose:
                    print(f"  [anomaly] {measure}/{guid} - no unambiguous Patient")
                continue

        resource_files = [f for f in resources if f not in patient_files]
        # Auto-discover fields from the whole folder (could include resource files
        # only; Patient file is excluded but harmless to skip).
        fields = discover_patient_fields(resources)

        for path in resource_files:
            data = load_json(path)
            if not data:
                continue
            if data.get("resourceType") == "MeasureReport":
                continue
            for field in sorted(fields):
                value = data.get(field)
                referenced = _patient_ref_guid(value)
                if referenced is None or referenced == expected:
                    continue
                category = classify(referenced, expected, all_patient_ids, field, measure)
                findings.append((measure, guid, os.path.basename(path), field,
                                 referenced, expected, category))
                if verbose:
                    print(f"  [{category}] {measure}/{guid} {os.path.basename(path)} "
                          f".{field} -> {referenced} (expected {expected})")
            for req_field in REQUIRED_PATIENT_FIELDS.get(data.get("resourceType"), ()):
                value = data.get(req_field)
                if _patient_ref_guid(value) is not None:
                    continue
                findings.append((measure, guid, os.path.basename(path), req_field,
                                 "(missing)", expected, "MISSING-REQUIRED-FIELD"))
                if verbose:
                    print(f"  [MISSING-REQUIRED-FIELD] {measure}/{guid} "
                          f"{os.path.basename(path)} .{req_field} "
                          f"(expected Patient/{expected})")
    return findings, anomalies


def collect_fixable(findings: List[Finding]) -> List[Finding]:
    """Return only CORE findings eligible for auto-fix."""
    return [f for f in findings if f[6].startswith("CORE")]


def apply_fix_finding(finding: Finding, tests_root: str = TESTS_ROOT) -> bool:
    """Rewrite one core-field finding's reference to the expected patient GUID,
    in place.  Returns True if the file was actually edited."""
    measure, guid, filename, field, _referenced, expected, _cat = finding
    path = os.path.join(tests_root, measure, guid, filename)
    data = load_json(path)
    if data is None:
        return False
    value = data.get(field)
    if _patient_ref_guid(value) is None:
        return False
    value["reference"] = f"Patient/{expected}"
    data[field] = value
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")
    return True


def collect_required_field_findings(findings: List[Finding]) -> List[Finding]:
    """Return findings a ``--fix-required-fields`` run would repair (any resource
    whose ``REQUIRED_PATIENT_FIELDS`` patient reference is missing or not a
    well-formed Patient/ reference)."""
    return [f for f in findings if f[6] == "MISSING-REQUIRED-FIELD"]


def apply_task_for_fix(finding: Finding, tests_root: str = TESTS_ROOT) -> bool:
    """Inject the missing ``for`` patient reference into a Task resource in place.

    ``for`` is set to ``Patient/<expected>`` (the folder's own patient GUID) and
    re-inserted after ``focus``/``code`` when present so the JSON reads like its
    sibling fixtures; key order is semantically irrelevant.  Returns True if the
    file was actually edited."""
    measure, guid, filename, _field, _referenced, expected, _cat = finding
    path = os.path.join(tests_root, measure, guid, filename)
    data = load_json(path)
    if data is None or data.get("resourceType") != "Task":
        return False
    if _patient_ref_guid(data.get("for")) is not None:
        return False
    keys = list(data.keys())
    if "focus" in keys:
        pos = keys.index("focus") + 1
    elif "code" in keys:
        pos = keys.index("code") + 1
    else:
        pos = len(keys)
    rebuilt = {}
    for i, key in enumerate(keys):
        if i == pos:
            rebuilt["for"] = {"reference": f"Patient/{expected}"}
        rebuilt[key] = data[key]
    if "for" not in rebuilt:
        rebuilt["for"] = {"reference": f"Patient/{expected}"}
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(rebuilt, fh, indent=2)
        fh.write("\n")
    return True


def apply_encounter_subject_fix(finding: Finding, tests_root: str = TESTS_ROOT) -> bool:
    """Inject the missing ``subject`` patient reference into an Encounter
    resource in place. ``subject`` is set to ``Patient/<expected>`` (the
    folder's own patient GUID) and re-inserted right after ``status`` when
    present so the JSON reads like its sibling fixtures; key order is
    semantically irrelevant. Returns True if the file was actually edited."""
    measure, guid, filename, _field, _referenced, expected, _cat = finding
    path = os.path.join(tests_root, measure, guid, filename)
    data = load_json(path)
    if data is None or data.get("resourceType") != "Encounter":
        return False
    if _patient_ref_guid(data.get("subject")) is not None:
        return False
    keys = list(data.keys())
    if "status" in keys:
        pos = keys.index("status") + 1
    else:
        pos = len(keys)
    rebuilt = {}
    for i, key in enumerate(keys):
        if i == pos:
            rebuilt["subject"] = {"reference": f"Patient/{expected}"}
        rebuilt[key] = data[key]
    if "subject" not in rebuilt:
        rebuilt["subject"] = {"reference": f"Patient/{expected}"}
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(rebuilt, fh, indent=2)
        fh.write("\n")
    return True


def apply_medicationadministration_subject_fix(finding: Finding, tests_root: str = TESTS_ROOT) -> bool:
    """Inject the missing ``subject`` patient reference into a
    MedicationAdministration resource in place. ``subject`` is set to
    ``Patient/<expected>`` (the folder's own patient GUID) and re-inserted
    right after ``status`` when present so the JSON reads like its sibling
    fixtures; key order is semantically irrelevant. Returns True if the file
    was actually edited."""
    measure, guid, filename, _field, _referenced, expected, _cat = finding
    path = os.path.join(tests_root, measure, guid, filename)
    data = load_json(path)
    if data is None or data.get("resourceType") != "MedicationAdministration":
        return False
    if _patient_ref_guid(data.get("subject")) is not None:
        return False
    keys = list(data.keys())
    if "status" in keys:
        pos = keys.index("status") + 1
    else:
        pos = len(keys)
    rebuilt = {}
    for i, key in enumerate(keys):
        if i == pos:
            rebuilt["subject"] = {"reference": f"Patient/{expected}"}
        rebuilt[key] = data[key]
    if "subject" not in rebuilt:
        rebuilt["subject"] = {"reference": f"Patient/{expected}"}
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(rebuilt, fh, indent=2)
        fh.write("\n")
    return True


def apply_observation_subject_fix(finding: Finding, tests_root: str = TESTS_ROOT) -> bool:
    """Inject the missing ``subject`` patient reference into an Observation
    resource in place. ``subject`` is set to ``Patient/<expected>`` (the
    folder's own patient GUID) and re-inserted right after ``status`` when
    present so the JSON reads like its sibling fixtures; key order is
    semantically irrelevant. Returns True if the file was actually edited."""
    measure, guid, filename, _field, _referenced, expected, _cat = finding
    path = os.path.join(tests_root, measure, guid, filename)
    data = load_json(path)
    if data is None or data.get("resourceType") != "Observation":
        return False
    if _patient_ref_guid(data.get("subject")) is not None:
        return False
    keys = list(data.keys())
    if "status" in keys:
        pos = keys.index("status") + 1
    else:
        pos = len(keys)
    rebuilt = {}
    for i, key in enumerate(keys):
        if i == pos:
            rebuilt["subject"] = {"reference": f"Patient/{expected}"}
        rebuilt[key] = data[key]
    if "subject" not in rebuilt:
        rebuilt["subject"] = {"reference": f"Patient/{expected}"}
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(rebuilt, fh, indent=2)
        fh.write("\n")
    return True


def apply_required_field_fix(finding: Finding, tests_root: str = TESTS_ROOT) -> bool:
    """Dispatch a MISSING-REQUIRED-FIELD finding to the specific fixer function
    for its resource type. Returns True if the file was actually edited."""
    measure, guid, filename, _field, _referenced, _expected, _cat = finding
    path = os.path.join(tests_root, measure, guid, filename)
    data = load_json(path)
    if data is None:
        return False
    resource_type = data.get("resourceType")
    if resource_type == "Task":
        return apply_task_for_fix(finding, tests_root=tests_root)
    if resource_type == "Encounter":
        return apply_encounter_subject_fix(finding, tests_root=tests_root)
    if resource_type == "MedicationAdministration":
        return apply_medicationadministration_subject_fix(finding, tests_root=tests_root)
    if resource_type == "Observation":
        return apply_observation_subject_fix(finding, tests_root=tests_root)
    return False


def collect_anomaly_fixes(test_cases) -> List[Tuple[str, str, str]]:
    """Return [(measure, guid, misnamed_basename)] for every folder whose sole
    Patient resource file is misnamed (fixable structural anomaly)."""
    fixes: List[Tuple[str, str, str]] = []
    for measure, guid, resources in test_cases:
        base = misnamed_patient_file(resources)
        if base is not None:
            fixes.append((measure, guid, base))
    return fixes


def apply_misnamed_patient_fix(measure: str, guid: str, misnamed_basename: str,
                               tests_root: str = TESTS_ROOT) -> bool:
    """Rename a misnamed Patient resource to ``Patient-<guid>.json`` and inject
    a matching ``id`` field if missing.  Returns True if the folder changed."""
    src = os.path.join(tests_root, measure, guid, misnamed_basename)
    if not os.path.isfile(src):
        return False
    data = load_json(src)
    if not data or data.get("resourceType") != "Patient":
        return False
    if data.get("id") != guid:
        data["id"] = guid
    dst = os.path.join(tests_root, measure, guid, f"Patient-{guid}.json")
    if src == dst:
        return False
    with open(dst, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")
    os.remove(src)
    return True


def _read_text(path: str) -> Optional[str]:
    """Read a file as UTF-8 text, returning None on any error."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except (OSError, ValueError):
        return None


def profile_namespace_occurrences(path: str) -> int:
    """Count `onc/us-quality-core` occurrences in a file, or -1 if unreadable."""
    text = _read_text(path)
    if text is None:
        return -1
    return text.count(UNIVERSAL_PROFILE_OLD)


def _replace_profile_namespace_text(text: str, old: str = UNIVERSAL_PROFILE_OLD,
                                    new: str = UNIVERSAL_PROFILE_NEW) -> str:
    """Rewrite ``onc/us-quality-core`` -> ``astp/us-quality-core`` in ``text``.

    The token is anchored to the full ``us-quality-core`` segment so unrelated
    ``onc/*`` strings (e.g. an ``onc/not108`` DOI) are preserved verbatim.
    """
    return text.replace(old, new)


def migrate_profile_namespace(path: str, dry_run: bool = False) -> int:
    """Migrate a fixture file's universal-profile base namespace in place.

    Returns the number of tokens rewritten (0 if none or unreadable, or None if
    the file name is excluded from migration).  ``dry_run`` rewrites nothing but
    still reports the count.  Only ``*.json`` files under a measure tree are
    touched; the migration is a plain-text substring rewrite and does not try to
    re-serialize/format the JSON (preserving the file's existing encoding and
    layout).
    """
    if not path.endswith(".json"):
        return 0
    text = _read_text(path)
    if text is None:
        return 0
    rewritten = _replace_profile_namespace_text(text)
    count = rewritten.count(UNIVERSAL_PROFILE_NEW) - text.count(UNIVERSAL_PROFILE_NEW)
    if count <= 0:
        return 0
    if not dry_run:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(rewritten)
    return count


def migrate_profile_namespace_tree(tests_root: str = TESTS_ROOT,
                                   dry_run: bool = False) -> Dict:
    """Walk the test-fixture tree and migrate every `onc/us-quality-core` token.

    Returns a summary dict: ``files`` (paths changed, or would-be-changed in a
    dry run), ``tokens`` (total rewritten), and ``scanned`` (JSON files checked).
    """
    result: Dict = {"files": [], "tokens": 0, "scanned": 0}
    cases = collect_test_cases(tests_root)
    for _measure, _guid, resources in cases:
        for rel_or_abs in resources:
            result["scanned"] += 1
            count = migrate_profile_namespace(path=rel_or_abs, dry_run=dry_run)
            if count > 0:
                result["tokens"] += count
                result["files"].append(rel_or_abs)
    return result


def still_uses_old_namespace(tests_root: str = TESTS_ROOT) -> List[str]:
    """Return every fixture file under ``tests_root`` still containing the old
    `onc/us-quality-core` base.  Used to assert the migration is complete."""
    old = []
    for _measure, _guid, resources in collect_test_cases(tests_root):
        for path in resources:
            if profile_namespace_occurrences(path) > 0:
                old.append(path)
    return old


def render_profile_ns_report(result: Dict) -> str:
    """Render a short markdown summary of a profile-namespace migration run."""
    files = result["files"]
    lines = [
        f"- **Files**: {len(files)} fixture file(s) affected",
        f"- **Occurrences rewritten**: {result['tokens']}",
        f"- **Files scanned**: {result['scanned']}",
        "",
    ]
    if files:
        from collections import Counter
        measures = Counter(os.path.basename(os.path.dirname(os.path.dirname(f)))
                           for f in files)
        lines.append("| Measure | Files |")
        lines.append("| --- | --- |")
        for m in sorted(measures):
            lines.append(f"| {m} | {measures[m]} |")
        lines.append("")
    return "\n".join(lines)


def render_report(findings: List[Finding], anomalies: List[str]) -> str:
    """Render a markdown report suitable for scripts/comparison/."""
    lines = [
        "# Test Fixture Validation Report",
        "",
        f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        f"- **Findings**: {len(findings)} patient-reference mismatch(es)",
        f"- **Structural anomalies**: {len(anomalies)}",
        "",
        "## Mismatch categories",
        "",
        "| Category | Count |",
        "| --- | --- |",
    ]
    from collections import Counter
    counts = Counter(f[6] for f in findings)
    for cat in sorted(counts):
        lines.append(f"| {cat} | {counts[cat]} |")
    lines.append("")
    lines.append("| Measure | Findings |")
    lines.append("| --- | --- |")
    measure_counts = Counter(f[0] for f in findings)
    for m in sorted(measure_counts):
        lines.append(f"| {m} | {measure_counts[m]} |")
    lines.append("")
    lines.append("## Details")
    lines.append("")
    lines.append("| Measure | Patient | Resource file | Field | Referenced patient | Expected patient | Category |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for (measure, guid, filename, field, referenced, expected, cat) in findings:
        lines.append(f"| {measure} | {guid} | {filename} | {field} | {referenced} | {expected} | {cat} |")
    lines.append("")
    if anomalies:
        lines.append("## Structural anomalies")
        lines.append("")
        for a in anomalies:
            lines.append(f"- {a}")
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--measure", metavar="NAME",
                        help="Only validate a single measure directory (e.g. CMS104FHIRSTKDCAntithrombotic)")
    parser.add_argument("--json", action="store_true", dest="as_json",
                        help="Emit findings as JSON to stdout instead of a markdown report")
    parser.add_argument("--fix", action="store_true",
                        help="Enable fixing; implies dry-run unless --apply is given")
    parser.add_argument("--fix-required-fields", action="store_true",
                        help="Inject a missing required patient reference into Task "
                             "(`for`), Encounter (`subject`), MedicationAdministration "
                             "(`subject`), and Observation (`subject`) resources; "
                             "implies dry-run unless --apply is given")
    parser.add_argument("--apply", action="store_true",
                        help="Actually write fixes (only CORE patient-identity fields). Requires --fix.")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Print each finding as discovered")
    parser.add_argument("--out", metavar="PATH", default="out",
                        help="Output directory for the report (default: ./out, gitignored)")
    parser.add_argument("--fix-profile-ns", action="store_true",
                        help="Migrate fixtures' universal-profile base from onc to astp; "
                             "implies dry-run unless --apply is given")
    args = parser.parse_args()

    if args.fix_profile_ns:
        result = migrate_profile_namespace_tree(dry_run=not args.apply)
        print("PROFILE-NS " + ("DRY-RUN" if not args.apply else "APPLIED") + ":")
        print(render_profile_ns_report(result))
        if not args.apply:
            print("Pass --apply to write the migration (no commit is made).")
        if args.apply:
            remaining = still_uses_old_namespace()
            print(f"Remaining files with old base: {len(remaining)}")
            for p in remaining[:20]:
                print(f"  {p}")
        return

    test_cases = collect_test_cases()
    all_patient_ids = repo_wide_patient_ids()
    if args.measure:
        test_cases = [tc for tc in test_cases if tc[0] == args.measure]

    findings, anomalies = validate(test_cases, verbose=args.verbose,
                                   all_patient_ids=all_patient_ids)

    if args.as_json:
        records = [
            {"measure": m, "patient": g, "file": f, "field": field,
             "referenced": ref, "expected": exp, "category": cat}
            for (m, g, f, field, ref, exp, cat) in findings
        ]
        print(json.dumps({"findings": records, "anomalies": anomalies}, indent=2))
        return

    # --- fixing ---
    if args.fix:
        fixable = collect_fixable(findings)
        anomaly_fixes = collect_anomaly_fixes(test_cases)
        summary = (f"FIX DRY-RUN: {len(fixable)} core finding(s) and "
                   f"{len(anomaly_fixes)} misnamed-Patient file(s) would be rewritten.")
        if args.apply:
            fixed = 0
            for finding in fixable:
                if apply_fix_finding(finding):
                    fixed += 1
            anomalies_fixed = 0
            for measure, guid, base in anomaly_fixes:
                if apply_misnamed_patient_fix(measure, guid, base):
                    anomalies_fixed += 1
            summary = (f"FIX APPLIED: rewrote {fixed} of {len(fixable)} core finding(s) "
                       f"and {anomalies_fixed} of {len(anomaly_fixes)} misnamed-Patient "
                       f"file(s). Review with `git diff` (no commit made).")
        # Re-run validation after any apply so the report reflects final state.
        findings, anomalies = validate(collect_test_cases(),
                                       all_patient_ids=all_patient_ids)
        if args.measure:
            test_cases = [tc for tc in collect_test_cases() if tc[0] == args.measure]
            findings, anomalies = validate(test_cases, all_patient_ids=all_patient_ids)
        print(summary)

    # --- required-field injection (Task.for, Encounter/Observation/
    # MedicationAdministration.subject) - separate from the CORE patient-
    # reference fixer, since this fixes a *missing* field rather than a
    # *wrong* one.
    if args.fix_required_fields:
        required_field_findings = collect_required_field_findings(findings)
        if args.apply:
            applied = 0
            for finding in required_field_findings:
                if apply_required_field_fix(finding):
                    applied += 1
            summary = (f"REQUIRED-FIELDS APPLIED: injected the missing reference into "
                       f"{applied} of {len(required_field_findings)} resource(s). "
                       f"Review with `git diff` (no commit made).")
            # Re-run validation after apply so the report reflects final state.
            findings, anomalies = validate(collect_test_cases(),
                                           all_patient_ids=all_patient_ids)
            if args.measure:
                test_cases = [tc for tc in collect_test_cases() if tc[0] == args.measure]
                findings, anomalies = validate(test_cases, all_patient_ids=all_patient_ids)
        else:
            summary = (f"REQUIRED-FIELDS DRY-RUN: {len(required_field_findings)} "
                       f"resource(s) missing a required patient reference would be "
                       f"fixed. Pass --apply to write.")
        print(summary)

    report = render_report(findings, anomalies)
    os.makedirs(args.out, exist_ok=True)
    report_name = f"fixture_validation_report-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
    report_path = os.path.join(args.out, report_name)
    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write(report)

    print(report)
    print(f"\nReport written to {report_path}")


if __name__ == "__main__":
    main()
