"""Canonical measure-population vocabulary, shared by every report.

Why this exists
---------------
The three CSVs that feed the reports do not agree on population names, because
they are produced by different extractors:

  * ``expected_results.csv`` takes the name from the fixture MeasureReport's
    ``code.coding[0].display``, except for two hardcoded MeasureObservation ids
    (see ``extract_population_expected.py``). CMS986 therefore says
    "Measure Population Observation".
  * ``actual_results.csv`` / ``qicore-2025-actual-results.csv`` say
    "Measure Observation" for that same population.

Comparison keys include the population name, so without a single canonical form
the CMS986 expected rows can never match their actual rows.

Separately, ``compare_results.ValidMeasurePopulationTypes`` historically listed
*plural* spellings ("Numerator Observations", "Denominator Observations") that
appear in none of the CSVs, while the singular forms the data actually uses were
absent. Cells whose population was not on that list were silently skipped by the
scorer -- 1,031 of 24,853 expected cells (4.1%), across CMS986, CMS1017 and
CMS871. Two catalog issues (I-04, I-05) were tracking defects in rows that the
scorer structurally could not fail on.

Canonicalise once, at CSV-read time, so every downstream key agrees.

The canonical names follow the HL7 measure-population CodeSystem
(https://terminology.hl7.org/CodeSystem-measure-population.html), plus the
"Denominator Observation"/"Numerator Observation" refinements the tooling emits
when a group carries more than one measure-observation.
"""

import glob
import json
import os
from typing import Dict, FrozenSet, Tuple

# Populations that participate in scoring, in canonical spelling.
CANONICAL_POPULATIONS: FrozenSet[str] = frozenset({
    "Initial Population",
    "Denominator",
    "Denominator Exclusion",
    "Denominator Exception",
    "Denominator Observation",
    "Numerator",
    "Numerator Exclusion",
    "Numerator Observation",
    "Measure Population",
    "Measure Population Exclusion",
    "Measure Observation",
})

# Non-canonical spellings seen in real inputs -> canonical form.
#
# "Measure Population Observation" is the load-bearing one: it is what the
# expected-results extractor emits for CMS986 while both engines emit
# "Measure Observation". The rest are defensive -- older exports and the
# hyphenated lowercase variants that were carried in the previous allowlist.
POPULATION_ALIASES: Dict[str, str] = {
    "Measure Population Observation": "Measure Observation",
    "Numerator Observations": "Numerator Observation",
    "Denominator Observations": "Denominator Observation",
    "Denominator-exclusion": "Denominator Exclusion",
    "Denominator-exception": "Denominator Exception",
}


def canonical_population(name: str) -> str:
    """Map a raw population name to its canonical spelling.

    Unknown names are returned unchanged so the caller can report them as
    unscored rather than having them silently disappear.
    """
    return POPULATION_ALIASES.get(name, name)


def is_scored(name: str) -> bool:
    """True if ``name`` (raw or canonical) participates in scoring."""
    return canonical_population(name) in CANONICAL_POPULATIONS


def split_population(population: str) -> Tuple[str, str]:
    """Split a ``"Group_N:Population Name"`` cell into (group, canonical name).

    Raises ValueError if the string is not in ``group:population`` form, rather
    than silently mangling it -- a malformed population column means the
    upstream extractor is broken and should fail loudly.
    """
    group, _, name = population.partition(":")
    if not _:
        raise ValueError(
            f"population {population!r} is not in 'Group_N:Population' form")
    return group, canonical_population(name)


def canonical_cell(population: str) -> str:
    """Return the ``"Group_N:Population"`` string with the name canonicalised."""
    group, name = split_population(population)
    return f"{group}:{name}"


# ---------------------------------------------------------------------------
# CQFM measure-observation aggregation exclusions (see defect-tracking/known-issues.md, I-62)
#
# CMS1017FHIRHHFI, CMS871FHIRHHHyper, and CMS986FHIRMalnutritionScore each wire
# one or more `measure-observation` populations via two CQFM extensions:
#
#   * cqfm-criteriaReference -- another population's `id` in the same group,
#     whose members are the source set.
#   * cqfm-aggregateMethod   -- Sum/Count/Average, describing how a *real*
#     measure-scoring engine combines per-member values.
#
# The population's `criteria.expression` names a CQL `define function` that
# takes one parameter, meant to be invoked once per member of the
# criteriaReference population. This repo's comparison harness has no
# scriptable/batch CQL execution path, and the stored TestCaseResult/`.txt`
# artifacts only ever contain directly-evaluated, zero-argument named results
# -- a parameterized function never appears there, so these cells always read
# 0 regardless of correctness. Separately, individual-patient fixture
# MeasureReports store one row *per member* (e.g. `MeasureObservation_5_1`,
# `MeasureObservation_5_2`), not a pre-aggregated value -- so even a fix that
# could invoke the function per member would still need per-member,
# id-indexed matching on both extractors, which is out of scope for now (see
# I-62). These cells are therefore excluded from automated scoring rather
# than reported as a misleading FAIL.
# ---------------------------------------------------------------------------

CQFM_CRITERIA_REFERENCE_URL = "http://hl7.org/fhir/us/cqfmeasures/StructureDefinition/cqfm-criteriaReference"
CQFM_AGGREGATE_METHOD_URL = "http://hl7.org/fhir/us/cqfmeasures/StructureDefinition/cqfm-aggregateMethod"

DEFAULT_MEASURE_RESOURCE_DIR = "./input/resources/measure"


def _ext_value(ext: dict):
    """A CQFM extension's payload.

    Tolerates an inconsistency confirmed across real data: CMS1017/CMS871 use
    `valueString`, CMS986 uses `valueCode`, for the identical extension URL.
    """
    return ext.get("valueString") or ext.get("valueCode")


def _is_measure_observation(pop: dict) -> bool:
    return pop.get("code", {}).get("coding", [{}])[0].get("code") == "measure-observation"


def cqfm_population_display_name(pop: dict, group: dict) -> str:
    """Canonical display name for a `measure-observation` population entry.

    A group with exactly one `measure-observation` population can use the
    generic FHIR coding display ("Measure Observation") verbatim -- the
    Group_N key already disambiguates it (CMS986's shape: one Measure
    Observation per group, six groups).

    A group with MORE than one `measure-observation` population (CMS1017,
    CMS871: two share Group_1) can't use the coding display -- both entries
    say "Measure Observation" -- so the CQL-identifier `criteria.expression`
    is used instead, canonicalised through POPULATION_ALIASES (this is what
    turns CMS871's plural "Denominator Observations" into the same
    "Denominator Observation" spelling CMS1017 and every CSV use).
    """
    coding_display = pop.get("code", {}).get("coding", [{}])[0].get("display", "")
    siblings = [p for p in group.get("population", []) if _is_measure_observation(p)]
    if len(siblings) > 1:
        expression = pop.get("criteria", {}).get("expression", coding_display)
        return canonical_population(expression)
    return canonical_population(coding_display)


def find_cqfm_aggregation_exclusions(measure_json: dict) -> FrozenSet[str]:
    """"Group_N:PopulationName" cells that require per-member CQFM aggregation
    this harness's CQL-execution path cannot perform.

    Detection is purely extension-shape-based (never a measure name/id), so a
    future measure adopting this CQFM pattern is picked up automatically.

    Also excludes the generic "Group_N:Measure Observation" label for every
    group containing at least one flagged population, regardless of that
    population's own specific name. This is a safety net for a confirmed,
    separate bug in extract_population_expected.py: fixture MeasureReports
    list one row per member (e.g. `MeasureObservation_1_1_1`,
    `MeasureObservation_1_1_2` for a 2-member case), and the expected
    extractor's hardcode only relabels the first member's suffixed id -- any
    additional member's row falls through to the generic "Measure
    Observation" display. Without this, a multi-member case would still slip
    through as a spurious, uncaught population. For CMS986 the generic label
    already *is* each group's specific excluded cell, so this is a no-op
    there, not a special case.
    """
    excluded = set()
    for group in measure_json.get("group", []):
        group_id = group.get("id")
        if not group_id:
            continue
        group_has_cqfm_observation = False
        for pop in group.get("population", []):
            exts = pop.get("extension", [])
            has_ref = any(
                e.get("url") == CQFM_CRITERIA_REFERENCE_URL and _ext_value(e)
                for e in exts)
            has_agg = any(
                e.get("url") == CQFM_AGGREGATE_METHOD_URL and _ext_value(e)
                for e in exts)
            if has_ref and has_agg:
                group_has_cqfm_observation = True
                excluded.add(f"{group_id}:{cqfm_population_display_name(pop, group)}")
        if group_has_cqfm_observation:
            excluded.add(f"{group_id}:{canonical_population('Measure Observation')}")
    return frozenset(excluded)


def load_cqfm_aggregation_exclusions(
        measure_resource_dir: str = DEFAULT_MEASURE_RESOURCE_DIR
) -> Dict[str, FrozenSet[str]]:
    """measure_name -> {"Group_N:PopulationName", ...} across every Measure
    resource under `measure_resource_dir`.

    A measure with no CQFM-aggregation populations is simply absent from the
    result (not mapped to an empty set), so callers should do
    `exclusions.get(measure, ())`.
    """
    out: Dict[str, FrozenSet[str]] = {}
    for path in sorted(glob.glob(os.path.join(measure_resource_dir, "*.json"))):
        measure_name = os.path.splitext(os.path.basename(path))[0]
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        excluded = find_cqfm_aggregation_exclusions(data)
        if excluded:
            out[measure_name] = excluded
    return out
