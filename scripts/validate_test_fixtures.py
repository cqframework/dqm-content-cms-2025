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
bug) - the same is true of ``subject`` on Encounter, Observation,
MedicationAdministration, and Communication.  See ``REQUIRED_PATIENT_FIELDS``. This is exactly
what was needed to fix CMS816FHIRHHHypo's 12 failing test cases (I-07): 17 of
its 28 fixture Encounter resources had no ``subject`` at all, so the engine
silently dropped them from every retrieve regardless of how correctly their
type/status/period were authored. CMS142FHIRCommWithDrManagingDiab's 5
Denominator Exception failures (I-39) were the same defect on Communication:
MADiE's engine treats every resource in a test case as the patient's without
checking references, so its expected results counted resources that carry no
``subject`` at all.
``--fix-required-fields`` injects the missing reference
(``Patient/<folder patient guid>``) using a dedicated fixer function per
resource type (``apply_task_for_fix``, ``apply_encounter_subject_fix``,
``apply_medicationadministration_subject_fix``,
``apply_observation_subject_fix``, ``apply_communication_subject_fix``); it is scrubbed separately from the CORE
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

Resource-ID checks (report-only, never auto-fixed) catch the residue of
duplicate resource ids in the MADiE source bundle.  MADiE used to accept a
bundle in which several entries shared one ``resourceType/id``; splitting it
into ``<resourceType>-<id>.json`` files kept only the last entry, silently
dropping the rest (I-10: CMS819's qualifying opioid / antagonist pair was lost
this way).  Once split, the duplicate itself is gone, so the tree checks look
for what it leaves behind:

* ``ID-FILENAME-MISMATCH`` - basename is not ``<resourceType>-<id>.json`` (or
  ``id`` is missing).  Patient files are covered by the anomaly checks above.
* ``ID-DUPLICATE`` - two files in one folder share a ``resourceType/id``.
* ``EVALUATED-REF-REPEATED`` (warning) - the fixture MeasureReport lists the
  same ``evaluatedResource`` more than once: the usual fingerprint of entries
  collapsed onto one id.  ``expected`` carries the repeat count.
* ``EVALUATED-REF-DANGLING`` - an ``evaluatedResource`` with no file in the
  folder.
* ``REF-UNRESOLVED-CLINICAL`` / ``REF-UNRESOLVED-ACTOR`` (warnings, opt-in via
  ``--check-references``) - a relative reference between fixture resources
  (e.g. ``Encounter.location.location`` -> ``Location/...``) with no file in the
  folder.  CLINICAL targets (``CLINICAL_REF_TYPES``) are ones measure logic can
  dereference; ACTOR covers Practitioner / Organization / Coverage etc.

``--bundle PATH [PATH ...]`` checks MADiE export Bundles *before* they are
split.  MADiE evaluates with the JS CQL engine, which treats every bundle
resource as the patient's, so a bundle can pass in MADiE and still be malformed
for the Java engine (I-76).  Every ``resourceType/id`` and ``fullUrl`` that
occurs more than once is reported as identical (harmless) or divergent (data
lost on split), and each entry gets the per-resource checks (``lint_bundle``):
wrong patient, missing ``REQUIRED_PATIENT_FIELDS``, unresolved references.  The
process exits 1 on a divergent duplicate or any non-warning finding.

``--restore-from-bundle BUNDLE --case MEASURE/GUID`` is a dry run that drafts
the resources a duplicate-id bundle lost when it was split into that fixture
folder (``plan_restore``).  Bundle entries are matched to fixture files by
content (codings plus dates shifted by the detected whole-year offset), never by
id.  Drafts get new ids, the fixture's profile and the folder patient; the
fixture MeasureReport's ``evaluatedResource`` is rewritten in bundle order.
Everything is written under ``<--out>/restore/<MEASURE>/<GUID>/`` with a
``restore-report.md``; ``input/tests/`` is never touched:

    python ./scripts/validate_test_fixtures.py --check-references
    python ./scripts/validate_test_fixtures.py --bundle path/to/madie-export.json
    python ./scripts/validate_test_fixtures.py --restore-from-bundle path/to/madie-export.json \\
        --case CMS819FHIRHHORAE/31b40acc-ca5f-4d1d-bd83-4b1a14eb822e
"""

import argparse
import json
import ntpath
import os
import re
import sys
from collections import Counter
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
    "Communication": ("subject",),
}

Finding = Tuple[str, str, str, str, str, str, str]  # (measure, patient, file, field, referenced, expected, category)

# A relative literal reference (``Type/id``, optionally versioned).  Absolute
# URLs, ``urn:`` and ``#contained`` references deliberately do not match.
RELATIVE_REF_RE = re.compile(
    r"^(?P<type>[A-Z][A-Za-z]+)/(?P<id>[A-Za-z0-9\-.]{1,64})(?:/_history/[^/]+)?$")

# Reference targets that measure logic dereferences (e.g. CMS819's
# ``EncounterLocation.location.getLocation()``), so an unresolved one can change
# a population.  Every other target type is reported as an ACTOR reference.
CLINICAL_REF_TYPES = (
    "Condition", "Device", "DiagnosticReport", "Encounter", "Location",
    "Medication", "MedicationRequest", "Observation", "Procedure",
    "QuestionnaireResponse", "ServiceRequest", "Specimen",
)

# Categories that are informational rather than definite defects.
WARNING_CATEGORIES = ("EVALUATED-REF-REPEATED", "REF-UNRESOLVED-CLINICAL",
                      "REF-UNRESOLVED-ACTOR")

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


def resource_key(data) -> Optional[str]:
    """Return ``"<resourceType>/<id>"`` for a resource dict, or None if either
    part is missing."""
    if not isinstance(data, dict):
        return None
    rtype, rid = data.get("resourceType"), data.get("id")
    if not isinstance(rtype, str) or not isinstance(rid, str):
        return None
    return f"{rtype}/{rid}"


def _basename(path: str) -> str:
    """Basename that splits on both ``/`` and ``\\`` (and drops a ``C:`` drive),
    so ``/a/b.json``, ``C:\\a\\b.json`` and ``C:/a/b.json`` all yield ``b.json``
    whatever platform the script runs on."""
    return ntpath.basename(path)


def check_resource_ids(measure: str, guid: str, resources: List[str]) -> List[Finding]:
    """Flag files whose name disagrees with their ``resourceType``/``id``
    (``ID-FILENAME-MISMATCH``) and ``resourceType/id`` values shared by several
    files in one folder (``ID-DUPLICATE``).  Patient files are left to the
    misnamed-Patient anomaly check."""
    findings: List[Finding] = []
    seen: Dict[str, List[str]] = {}
    for path in resources:
        data = load_json(path)
        if not data or not isinstance(data.get("resourceType"), str):
            continue
        base = _basename(path)
        key = resource_key(data)
        if key is not None:
            seen.setdefault(key, []).append(base)
        if data["resourceType"] == "Patient":
            continue
        expected_name = f"{data['resourceType']}-{data['id']}.json" if key else "(no id)"
        if base != expected_name:
            findings.append((measure, guid, base, "id", key or "(missing)",
                             expected_name, "ID-FILENAME-MISMATCH"))
    for key, files in sorted(seen.items()):
        if len(files) > 1:
            for base in files:
                findings.append((measure, guid, base, "id", key,
                                 f"{len(files)} files", "ID-DUPLICATE"))
    return findings


def folder_resource_keys(resources: List[str]) -> Set[str]:
    """Every ``resourceType/id`` present as a file in a test-case folder."""
    keys: Set[str] = set()
    for path in resources:
        key = resource_key(load_json(path))
        if key is not None:
            keys.add(key)
    return keys


def check_evaluated_resources(measure: str, guid: str, resources: List[str],
                              keys: Set[str]) -> List[Finding]:
    """Check each MeasureReport's ``evaluatedResource`` list: repeated
    references (``EVALUATED-REF-REPEATED``, the trace of ids collapsed on split)
    and references with no file in the folder (``EVALUATED-REF-DANGLING``)."""
    findings: List[Finding] = []
    for path in resources:
        data = load_json(path)
        if not data or data.get("resourceType") != "MeasureReport":
            continue
        refs = [e.get("reference") for e in data.get("evaluatedResource", [])
                if isinstance(e, dict) and isinstance(e.get("reference"), str)]
        counts = Counter(r for r in refs if not r.startswith("#"))
        base = _basename(path)
        for ref in sorted(counts):
            if counts[ref] > 1:
                findings.append((measure, guid, base, "evaluatedResource", ref,
                                 f"{counts[ref]}x", "EVALUATED-REF-REPEATED"))
            match = RELATIVE_REF_RE.match(ref)
            if match and f"{match.group('type')}/{match.group('id')}" not in keys:
                findings.append((measure, guid, base, "evaluatedResource", ref,
                                 "(no file)", "EVALUATED-REF-DANGLING"))
    return findings


def _iter_references(value, path: str):
    """Yield ``(dotted_path, reference)`` for every ``{"reference": str}`` dict
    nested anywhere in ``value``.  List indices are omitted from the path."""
    if isinstance(value, dict):
        ref = value.get("reference")
        if isinstance(ref, str):
            yield path, ref
        for key, child in value.items():
            yield from _iter_references(child, f"{path}.{key}")
    elif isinstance(value, list):
        for child in value:
            yield from _iter_references(child, path)


def _unresolved_references(data: Dict, keys: Set[str]):
    """Yield ``(field, reference, category)`` for each relative non-Patient
    reference in ``data`` whose target is not in ``keys``."""
    for field, ref in _iter_references(data, data["resourceType"]):
        match = RELATIVE_REF_RE.match(ref)
        if not match or match.group("type") == "Patient":
            continue
        if f"{match.group('type')}/{match.group('id')}" in keys:
            continue
        category = ("REF-UNRESOLVED-CLINICAL" if match.group("type") in CLINICAL_REF_TYPES
                    else "REF-UNRESOLVED-ACTOR")
        yield field, ref, category


def check_internal_references(measure: str, guid: str, resources: List[str],
                              keys: Set[str]) -> List[Finding]:
    """Flag relative references between a folder's resources that resolve to no
    file in the folder.  ``Patient/`` references are left to the patient checks;
    MeasureReports are left to ``check_evaluated_resources``."""
    findings: List[Finding] = []
    for path in resources:
        data = load_json(path)
        if not data or data.get("resourceType") in (None, "MeasureReport"):
            continue
        base = _basename(path)
        for field, ref, category in _unresolved_references(data, keys):
            findings.append((measure, guid, base, field, ref, "(no file)", category))
    return findings


def _bundle_entries(bundle) -> List[Dict]:
    """Every well-formed entry (one with a typed ``resource``) of a Bundle."""
    if not isinstance(bundle, dict):
        return []
    return [e for e in bundle.get("entry", [])
            if isinstance(e, dict) and isinstance(e.get("resource"), dict)
            and isinstance(e["resource"].get("resourceType"), str)]


def _bundle_resources(bundle) -> List[Dict]:
    """The ``resource`` of every well-formed entry of a Bundle, in order."""
    return [e["resource"] for e in _bundle_entries(bundle)]


def _bundle_full_urls(bundle) -> List[Optional[str]]:
    """The ``fullUrl`` of every well-formed entry, aligned with ``_bundle_resources``."""
    return [e.get("fullUrl") if isinstance(e.get("fullUrl"), str) else None
            for e in _bundle_entries(bundle)]


def lint_bundle(bundle) -> List[Dict]:
    """Run the per-resource fixture checks on a source Bundle before it is split.

    MADiE's JS engine treats every bundle resource as the patient's, so a bundle
    can pass there and still carry defects that break the Java engine.  Each
    result is ``{"index", "key", "field", "referenced", "category"}``:

    * ``BUNDLE-PATIENT-AMBIGUOUS`` - not exactly one Patient entry.
    * ``BUNDLE-WRONG-PATIENT`` - a CORE patient field points at another patient.
    * ``MISSING-REQUIRED-FIELD`` - a ``REQUIRED_PATIENT_FIELDS`` reference is absent.
    * ``REF-UNRESOLVED-CLINICAL`` / ``REF-UNRESOLVED-ACTOR`` (warnings) - a
      relative reference with no entry in the bundle.
    """
    resources = _bundle_resources(bundle)
    keys = {k for k in (resource_key(r) for r in resources) if k}
    patient_ids = sorted({r.get("id") for r in resources if r["resourceType"] == "Patient"})
    results: List[Dict] = []
    expected = patient_ids[0] if len(patient_ids) == 1 else None
    if expected is None:
        results.append({"index": None, "key": None, "field": "Patient",
                        "referenced": ", ".join(str(p) for p in patient_ids) or "(none)",
                        "category": "BUNDLE-PATIENT-AMBIGUOUS"})
    for index, data in enumerate(resources):
        if data["resourceType"] in ("Patient", "MeasureReport"):
            continue
        key = resource_key(data)
        for field in CORE_PATIENT_FIELDS:
            referenced = _patient_ref_guid(data.get(field))
            if expected and referenced is not None and referenced != expected:
                results.append({"index": index, "key": key, "field": field,
                                "referenced": f"Patient/{referenced}",
                                "category": "BUNDLE-WRONG-PATIENT"})
        for field in REQUIRED_PATIENT_FIELDS.get(data["resourceType"], ()):
            if _patient_ref_guid(data.get(field)) is None:
                results.append({"index": index, "key": key, "field": field,
                                "referenced": "(missing)", "category": "MISSING-REQUIRED-FIELD"})
        for field, ref, category in _unresolved_references(data, keys):
            results.append({"index": index, "key": key, "field": field,
                            "referenced": ref, "category": category})
    return results


def check_bundle(bundle) -> List[Dict]:
    """Report every ``resourceType/id`` and ``fullUrl`` that occurs on more than
    one entry of a source Bundle.  Each result is ``{"kind", "key", "indices",
    "identical"}``; ``identical`` is False when the colliding resources differ,
    i.e. splitting the bundle into one file per id would lose data."""
    results: List[Dict] = []
    if not isinstance(bundle, dict):
        return results
    entries = [e for e in bundle.get("entry", []) if isinstance(e, dict)]
    for kind in ("resource", "fullUrl"):
        groups: Dict[str, List[int]] = {}
        for index, entry in enumerate(entries):
            key = resource_key(entry.get("resource")) if kind == "resource" else entry.get("fullUrl")
            if isinstance(key, str):
                groups.setdefault(key, []).append(index)
        for key, indices in groups.items():
            if len(indices) < 2:
                continue
            bodies = {json.dumps(entries[i].get("resource"), sort_keys=True) for i in indices}
            results.append({"kind": kind, "key": key, "indices": indices,
                            "identical": len(bodies) == 1})
    return results


def render_bundle_report(results_by_path: Dict[str, List[Dict]],
                         lint_by_path: Optional[Dict[str, List[Dict]]] = None) -> str:
    """Render markdown tables of the duplicate keys found by ``check_bundle`` and
    the per-resource findings from ``lint_bundle``."""
    lines = ["| Bundle | Kind | Key | Entries | Duplicate |",
             "| --- | --- | --- | --- | --- |"]
    for path, results in results_by_path.items():
        for r in results:
            lines.append(f"| {path} | {r['kind']} | {r['key']} | "
                         f"{', '.join(str(i) for i in r['indices'])} | "
                         f"{'identical' if r['identical'] else 'DIVERGENT'} |")
    if len(lines) == 2:
        lines = ["No duplicate resource ids or fullUrls found."]
    lint_rows = [(path, f) for path, found in (lint_by_path or {}).items() for f in found]
    if lint_rows:
        lines += ["", "| Bundle | Entry | Resource | Field | Referenced | Category |",
                  "| --- | --- | --- | --- | --- | --- |"]
        for path, f in lint_rows:
            lines.append(f"| {path} | {f['index']} | {f['key']} | {f['field']} | "
                         f"{f['referenced']} | {f['category']} |")
    return "\n".join(lines)


def bundle_has_errors(dups: List[Dict], lint: List[Dict]) -> bool:
    """True if a bundle has a divergent duplicate id or a non-warning lint
    finding - i.e. splitting it into fixtures would lose or hide data."""
    return (any(not d["identical"] for d in dups)
            or any(f["category"] not in WARNING_CATEGORIES for f in lint))


# --- restore-from-bundle (dry run) --------------------------------------------
#
# Re-derives the resources a duplicate-id bundle lost on split (I-76).  Fixture
# ids and dates were rewritten after export (e.g. CMS819 dates moved 2028 ->
# 2026), so bundle entries are matched to fixture files by content - resource
# type, every coding (system, code), and every date shifted by a whole number of
# years - never by id.

DATE_VALUE_RE = re.compile(
    r"^(?P<year>\d{4})(?P<rest>-\d{2}(?:-\d{2}(?:T\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?"
    r"(?:Z|[+-]\d{2}:\d{2})?)?)?)?$")

# Keys whose string values are never dates, even when they look like one
# (a 4-digit code would otherwise read as a year).
NON_DATE_KEYS = ("id", "code", "system", "value", "version", "reference", "display",
                 "url", "lastUpdated")

QICORE_PROFILE_PREFIX = "http://hl7.org/fhir/us/qicore/StructureDefinition/qicore-"
UQC_PROFILE_PREFIX = ("http://fhir.org/guides/astp/us-quality-core/StructureDefinition/"
                      "us-quality-core-")


def _shift_date(value: str, years: int) -> str:
    """Shift a FHIR date/dateTime string by ``years``, leaving anything else
    alone.  Feb 29 shifted into a non-leap year becomes Feb 28."""
    match = DATE_VALUE_RE.match(value)
    if not match or years == 0:
        return value
    year = int(match.group("year")) + years
    rest = match.group("rest") or ""
    if rest.startswith("-02-29") and not (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)):
        rest = "-02-28" + rest[len("-02-29"):]
    return f"{year:04d}{rest}"


def _map_dates(value, years: int, key: Optional[str] = None):
    """Return a copy of ``value`` with every date string shifted by ``years``."""
    if isinstance(value, dict):
        return {k: _map_dates(v, years, k) for k, v in value.items()}
    if isinstance(value, list):
        return [_map_dates(v, years, key) for v in value]
    if isinstance(value, str) and key not in NON_DATE_KEYS:
        return _shift_date(value, years)
    return value


def _dates(value, key: Optional[str] = None) -> List[str]:
    """Every date string in ``value``, in document order."""
    if isinstance(value, dict):
        return [d for k, v in value.items() if k != "meta" for d in _dates(v, k)]
    if isinstance(value, list):
        return [d for v in value for d in _dates(v, key)]
    if isinstance(value, str) and key not in NON_DATE_KEYS and DATE_VALUE_RE.match(value):
        return [value]
    return []


def _codings(value) -> Tuple[Tuple[str, str], ...]:
    """Every ``(system, code)`` pair in ``value``, sorted."""
    found: List[Tuple[str, str]] = []

    def walk(v):
        if isinstance(v, dict):
            if isinstance(v.get("system"), str) and isinstance(v.get("code"), str):
                found.append((v["system"], v["code"]))
            for k, child in v.items():
                if k != "meta":
                    walk(child)
        elif isinstance(v, list):
            for child in v:
                walk(child)
    walk(value)
    return tuple(sorted(found))


def _fingerprint(data: Dict, years: int = 0) -> Tuple:
    """Content identity used to match a bundle entry to a fixture file."""
    return (data.get("resourceType"), _codings(data),
            tuple(sorted(_shift_date(d, years) for d in _dates(data))))


def detect_year_shift(bundle_resources: List[Dict], fixture_resources: List[Dict]) -> int:
    """The whole-year offset (fixture minus bundle) that most bundle entries need
    to line up with a fixture file of the same type and codings; 0 if none."""
    votes: Counter = Counter()
    for b in bundle_resources:
        b_dates = _dates(b)
        if not b_dates:
            continue
        for f in fixture_resources:
            if f.get("resourceType") != b.get("resourceType") or _codings(f) != _codings(b):
                continue
            f_dates = _dates(f)
            if len(f_dates) != len(b_dates):
                continue
            deltas = set()
            for bd, fd in zip(b_dates, f_dates):
                bm, fm = DATE_VALUE_RE.match(bd), DATE_VALUE_RE.match(fd)
                if (bm.group("rest") or "") != (fm.group("rest") or ""):
                    deltas = set()
                    break
                deltas.add(int(fm.group("year")) - int(bm.group("year")))
            if len(deltas) == 1:
                votes[deltas.pop()] += 1
    return votes.most_common(1)[0][0] if votes else 0


def _profile_for(resource_type: str, fixture_resources: List[Dict],
                 bundle_profile: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """Pick the ``meta.profile`` for a draft: the most common one on fixture files
    of the same type, else the bundle's QI-Core profile renamed to US Quality
    Core.  Returns ``(profile, note)``; ``note`` is set when the profile is a guess."""
    seen = Counter(p for r in fixture_resources if r.get("resourceType") == resource_type
                   for p in (r.get("meta") or {}).get("profile", [])[:1])
    if seen:
        return seen.most_common(1)[0][0], None
    if bundle_profile and bundle_profile.startswith(QICORE_PROFILE_PREFIX):
        guess = UQC_PROFILE_PREFIX + bundle_profile[len(QICORE_PROFILE_PREFIX):]
        return guess, f"profile renamed from {bundle_profile}; confirm it exists"
    return bundle_profile, "no fixture file of this type to copy a profile from"


def plan_restore(bundle, fixture_paths: List[str], folder_guid: str,
                 new_id=None) -> Dict:
    """Work out which resources a duplicate-id bundle lost and draft them.

    Only entries that share a ``resourceType/id`` with a *different* entry are
    candidates (the I-76 mechanism).  A candidate whose content matches a fixture
    file survived; the rest are drafted with a new id (``new_id()``, default
    uuid4), dates shifted by the detected year offset, the fixture profile, and
    patient references pointed at ``folder_guid``.  The fixture MeasureReport's
    ``evaluatedResource`` is rewritten in bundle order when the surviving id is
    repeated exactly once per colliding entry.  Nothing is written to disk.
    """
    import copy
    import uuid
    new_id = new_id or (lambda: str(uuid.uuid4()))
    resources = _bundle_resources(bundle)
    fixtures = [(p, d) for p, d in ((p, load_json(p)) for p in fixture_paths)
                if d and isinstance(d.get("resourceType"), str)]
    fixture_data = [d for _p, d in fixtures if d["resourceType"] != "MeasureReport"]
    years = detect_year_shift(resources, fixture_data)
    notes: List[str] = []

    by_fp: Dict[Tuple, List[str]] = {}
    for d in fixture_data:
        by_fp.setdefault(_fingerprint(d), []).append(resource_key(d))

    groups: Dict[str, List[int]] = {}
    for index, data in enumerate(resources):
        key = resource_key(data)
        if key:
            groups.setdefault(key, []).append(index)
    colliding = {k: ix for k, ix in groups.items() if len(ix) > 1
                 and len({json.dumps(resources[i], sort_keys=True) for i in ix}) > 1}
    # A shared fullUrl with distinct ids also marks a collision: a re-exported
    # bundle can carry the old fullUrl after the duplicate id was renamed (CMS819
    # 31b40acc: Encounter-1 and Encounter-2 under one fullUrl, while the fixture
    # kept only one).  Skip groups an id collision already covers.
    full_urls: Dict[str, List[int]] = {}
    for index, url in enumerate(_bundle_full_urls(bundle)):
        if url:
            full_urls.setdefault(url, []).append(index)
    covered = {i for ix in colliding.values() for i in ix}
    for url, ix in full_urls.items():
        if (len(ix) > 1 and not set(ix) <= covered
                and len({json.dumps(resources[i], sort_keys=True) for i in ix}) > 1):
            colliding[url] = ix
    collided_keys = {resource_key(resources[i]) for ix in colliding.values() for i in ix}

    # Bundle id -> fixture id for entries that are unambiguous and survived, so
    # references inside a draft (e.g. Claim.item.encounter) can be re-pointed.
    id_map: Dict[str, str] = {}
    for key, indices in groups.items():
        if key in collided_keys or resources[indices[0]]["resourceType"] == "Patient":
            continue
        matches = by_fp.get(_fingerprint(resources[indices[0]], years), [])
        if len(matches) == 1:
            id_map[key] = matches[0]

    drafts: Dict[str, Dict] = {}
    report_groups: List[Dict] = []
    rewrites: List[Tuple[str, List[str]]] = []
    used: Set[str] = set()
    for key, indices in colliding.items():
        members = []
        for index in indices:
            data = resources[index]
            survivor = next((k for k in by_fp.get(_fingerprint(data, years), []) if k not in used), None)
            if survivor:
                used.add(survivor)
                members.append({"index": index, "status": "present", "fixture_key": survivor})
                continue
            draft = _map_dates(copy.deepcopy(data), years)
            rid = new_id()
            profile, note = _profile_for(data["resourceType"], fixture_data,
                                         ((data.get("meta") or {}).get("profile") or [None])[0])
            if note:
                notes.append(f"{data['resourceType']}/{rid}: {note}")
            for field, ref in list(_iter_references(draft, data["resourceType"])):
                match = RELATIVE_REF_RE.match(ref)
                if not match:
                    continue
                target = f"{match.group('type')}/{match.group('id')}"
                if match.group("type") == "Patient":
                    _set_reference(draft, ref, f"Patient/{folder_guid}")
                elif target in id_map:
                    _set_reference(draft, ref, id_map[target])
                elif target in collided_keys:
                    notes.append(f"{data['resourceType']}/{rid}: {field} -> {ref} is ambiguous "
                                 f"(that id was reused in the bundle); set it by hand")
                else:
                    notes.append(f"{data['resourceType']}/{rid}: {field} -> {ref} has no "
                                 f"matching fixture resource")
            ordered = {"resourceType": data["resourceType"], "id": rid}
            if profile:
                ordered["meta"] = {"profile": [profile]}
            ordered.update({k: v for k, v in draft.items()
                            if k not in ("resourceType", "id", "meta")})
            drafts[f"{data['resourceType']}-{rid}.json"] = ordered
            members.append({"index": index, "status": "lost",
                            "draft_key": f"{data['resourceType']}/{rid}"})
        report_groups.append({"bundle_key": key, "members": members})
        present = [m["fixture_key"] for m in members if m["status"] == "present"]
        if any(m["status"] == "lost" for m in members):
            if len(present) == 1:
                rewrites.append((present[0], [m.get("fixture_key") or m["draft_key"]
                                              for m in members]))
            else:
                notes.append(f"{key}: {len(present)} surviving fixture match(es); "
                             f"evaluatedResource not rewritten")

    measure_report = None
    for path, data in fixtures:
        if data["resourceType"] != "MeasureReport" or not rewrites:
            continue
        report = copy.deepcopy(data)
        refs = report.get("evaluatedResource", [])
        for survivor, ordered_keys in rewrites:
            positions = [i for i, e in enumerate(refs) if e.get("reference") == survivor]
            if len(positions) != len(ordered_keys):
                notes.append(f"{_basename(path)}: {survivor} appears {len(positions)}x in "
                             f"evaluatedResource, expected {len(ordered_keys)}x; not rewritten")
                continue
            for position, new_key in zip(positions, ordered_keys):
                refs[position] = {**refs[position], "reference": new_key}
        measure_report = (_basename(path), report)
    return {"year_shift": years, "groups": report_groups, "drafts": drafts,
            "measure_report": measure_report, "notes": notes}


def _set_reference(value, old: str, new: str) -> None:
    """Replace every ``{"reference": old}`` nested in ``value`` with ``new``."""
    if isinstance(value, dict):
        if value.get("reference") == old:
            value["reference"] = new
        for child in value.values():
            _set_reference(child, old, new)
    elif isinstance(value, list):
        for child in value:
            _set_reference(child, old, new)


def render_restore_report(case: str, plan: Dict, out_dir: str) -> str:
    """Markdown summary of a ``plan_restore`` result."""
    lines = [f"# Restore dry run: {case}", "",
             f"- **Year shift** (fixture minus bundle): {plan['year_shift']:+d}",
             f"- **Drafts**: {len(plan['drafts'])} resource(s)"
             + (" + MeasureReport" if plan["measure_report"] else ""),
             f"- **Written to**: `{out_dir}` (nothing under `input/tests/` was changed)", ""]
    if not plan["groups"]:
        lines.append("No colliding ids in the bundle: nothing to restore.")
    for group in plan["groups"]:
        lines += [f"## `{group['bundle_key']}`", "", "| Entry | Status | Resource |",
                  "| --- | --- | --- |"]
        for m in group["members"]:
            lines.append(f"| {m['index']} | {m['status']} | "
                         f"{m.get('fixture_key') or m.get('draft_key')} |")
        lines.append("")
    if plan["notes"]:
        lines += ["## Check by hand", ""] + [f"- {n}" for n in plan["notes"]] + [""]
    return "\n".join(lines)


def validate(test_cases, verbose: bool = False,
             all_patient_ids: Optional[Set[str]] = None,
             check_references: bool = False) -> Tuple[List[Finding], List[str]]:
    """Run validation over all test cases.

    Returns (findings, structural_anomalies).  ``structural_anomalies`` captures
    folders without an unambiguous Patient resource (can't be validated).

    ``all_patient_ids`` is the universe of real patient GUIDs used to
    distinguish "wrong but real patient" from "placeholder/non-existent"; if not
    supplied it is derived from the given ``test_cases`` themselves.

    The resource-ID checks run on every folder; ``check_references`` also adds
    the (noisy) unresolved intra-folder reference check."""
    findings: List[Finding] = []
    anomalies: List[str] = []

    if all_patient_ids is None:
        all_patient_ids = patient_ids_from_cases(test_cases)

    for measure, guid, resources in test_cases:
        keys = folder_resource_keys(resources)
        id_findings = check_resource_ids(measure, guid, resources)
        id_findings += check_evaluated_resources(measure, guid, resources, keys)
        if check_references:
            id_findings += check_internal_references(measure, guid, resources, keys)
        findings.extend(id_findings)
        if verbose:
            for f in id_findings:
                print(f"  [{f[6]}] {measure}/{guid} {f[2]} .{f[3]} -> {f[4]} ({f[5]})")

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


def apply_communication_subject_fix(finding: Finding, tests_root: str = TESTS_ROOT) -> bool:
    """Inject the missing ``subject`` patient reference into a Communication
    resource in place. ``subject`` is set to ``Patient/<expected>`` (the
    folder's own patient GUID) and re-inserted right after ``status`` when
    present so the JSON reads like its sibling fixtures; key order is
    semantically irrelevant. Returns True if the file was actually edited."""
    measure, guid, filename, _field, _referenced, expected, _cat = finding
    path = os.path.join(tests_root, measure, guid, filename)
    data = load_json(path)
    if data is None or data.get("resourceType") != "Communication":
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
    if resource_type == "Communication":
        return apply_communication_subject_fix(finding, tests_root=tests_root)
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
        f"- **Findings**: {len(findings)} finding(s)",
        f"- **Structural anomalies**: {len(anomalies)}",
        "",
        f"Warning categories (informational, not definite defects): "
        f"{', '.join(WARNING_CATEGORIES)}.",
        "",
        "## Mismatch categories",
        "",
        "| Category | Count |",
        "| --- | --- |",
    ]
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
    lines.append("| Measure | Patient | Resource file | Field | Referenced | Expected | Category |")
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
    parser.add_argument("--check-references", action="store_true",
                        help="Also report relative references between a folder's resources "
                             "that resolve to no file (REF-UNRESOLVED-CLINICAL / -ACTOR)")
    parser.add_argument("--bundle", nargs="+", metavar="PATH",
                        help="Check source Bundle file(s) instead of the fixture tree: duplicate "
                             "resourceType/id and fullUrl, plus the per-resource patient-reference, "
                             "required-field and unresolved-reference checks; exits 1 on a "
                             "divergent duplicate or a non-warning finding")
    parser.add_argument("--restore-from-bundle", metavar="BUNDLE",
                        help="Dry run: draft the resources a duplicate-id source Bundle lost when "
                             "it was split into the --case fixture folder; writes drafts and a "
                             "report under <--out>/restore/ and never edits input/tests/")
    parser.add_argument("--case", metavar="MEASURE/GUID",
                        help="Fixture folder for --restore-from-bundle, e.g. "
                             "CMS819FHIRHHORAE/31b40acc-ca5f-4d1d-bd83-4b1a14eb822e")
    args = parser.parse_args()

    if args.bundle:
        results_by_path, lint_by_path = {}, {}
        for path in args.bundle:
            bundle = load_json(path)
            if bundle is None:
                print(f"Cannot read {path} as JSON", file=sys.stderr)
                sys.exit(2)
            results_by_path[path] = check_bundle(bundle)
            lint_by_path[path] = lint_bundle(bundle)
        if args.as_json:
            print(json.dumps({"duplicates": results_by_path, "findings": lint_by_path}, indent=2))
        else:
            print(render_bundle_report(results_by_path, lint_by_path))
        if any(bundle_has_errors(results_by_path[p], lint_by_path[p]) for p in results_by_path):
            sys.exit(1)
        return

    if args.restore_from_bundle:
        if not args.case or args.case.replace("\\", "/").count("/") != 1:
            parser.error("--restore-from-bundle needs --case MEASURE/GUID")
        measure, guid = args.case.replace("\\", "/").split("/")
        case_dir = os.path.join(TESTS_ROOT, measure, guid)
        bundle = load_json(args.restore_from_bundle)
        if bundle is None or not os.path.isdir(case_dir):
            print(f"Cannot read {args.restore_from_bundle} or {case_dir}", file=sys.stderr)
            sys.exit(2)
        fixture_paths = [os.path.join(case_dir, f) for f in sorted(os.listdir(case_dir))
                         if f.endswith(".json")]
        plan = plan_restore(bundle, fixture_paths, guid)
        out_dir = os.path.join(args.out, "restore", measure, guid)
        os.makedirs(out_dir, exist_ok=True)
        files = dict(plan["drafts"])
        if plan["measure_report"]:
            files[plan["measure_report"][0]] = plan["measure_report"][1]
        for name, data in files.items():
            with open(os.path.join(out_dir, name), "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2)
                fh.write("\n")
        report = render_restore_report(args.case, plan, out_dir)
        with open(os.path.join(out_dir, "restore-report.md"), "w", encoding="utf-8") as fh:
            fh.write(report + "\n")
        print(report)
        return

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
                                   all_patient_ids=all_patient_ids,
                                   check_references=args.check_references)

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
                                       all_patient_ids=all_patient_ids,
                                       check_references=args.check_references)
        if args.measure:
            test_cases = [tc for tc in collect_test_cases() if tc[0] == args.measure]
            findings, anomalies = validate(test_cases, all_patient_ids=all_patient_ids,
                                           check_references=args.check_references)
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
                                           all_patient_ids=all_patient_ids,
                                           check_references=args.check_references)
            if args.measure:
                test_cases = [tc for tc in collect_test_cases() if tc[0] == args.measure]
                findings, anomalies = validate(test_cases, all_patient_ids=all_patient_ids,
                                               check_references=args.check_references)
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
