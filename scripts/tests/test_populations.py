"""Tests for the CQFM measure-observation aggregation exclusions (see
defect-tracking/known-issues.md, I-62).

CMS1017FHIRHHFI, CMS871FHIRHHHyper, and CMS986FHIRMalnutritionScore wire
`measure-observation` populations to a parameterized CQL function via
cqfm-criteriaReference/cqfm-aggregateMethod, meant to be invoked once per
member of another population and aggregated. This harness has no scriptable
CQL execution path and fixture MeasureReports store one row per member rather
than a pre-aggregated value, so these cells are excluded from scoring instead
of reported as a misleading FAIL. Detection must stay measure-name-agnostic
(extension-shape-based only), so a future measure adopting this pattern is
picked up automatically.
"""
import json
import os
import tempfile
import unittest

from scripts.comparison.populations import (
    cqfm_population_display_name,
    find_cqfm_aggregation_exclusions,
    load_cqfm_aggregation_exclusions,
)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
MEASURE_RESOURCE_DIR = os.path.join(REPO_ROOT, "input", "resources", "measure")

REF_URL = "http://hl7.org/fhir/us/cqfmeasures/StructureDefinition/cqfm-criteriaReference"
AGG_URL = "http://hl7.org/fhir/us/cqfmeasures/StructureDefinition/cqfm-aggregateMethod"


def _obs_pop(pop_id, expression, ref, agg_url_key="valueString", display="Measure Observation"):
    return {
        "id": pop_id,
        "code": {"coding": [{"code": "measure-observation", "display": display}]},
        "criteria": {"expression": expression},
        "extension": [
            {"url": REF_URL, "valueString": ref},
            {"url": AGG_URL, agg_url_key: "Sum"},
        ],
    }


def _plain_pop(pop_id, code, expression, display):
    return {
        "id": pop_id,
        "code": {"coding": [{"code": code, "display": display}]},
        "criteria": {"expression": expression},
    }


class CqfmPopulationDisplayNameTest(unittest.TestCase):

    def test_single_observation_in_group_uses_coding_display(self):
        group = {"population": [_obs_pop("MO_5", "Total Score", "MP_5")]}
        self.assertEqual(
            cqfm_population_display_name(group["population"][0], group),
            "Measure Observation")

    def test_multiple_observations_in_group_disambiguate_via_expression(self):
        pop1 = _obs_pop("MO_1_1", "Denominator Observation", "Denominator_1")
        pop2 = _obs_pop("MO_1_2", "Numerator Observation", "Numerator_1")
        group = {"population": [pop1, pop2]}
        self.assertEqual(cqfm_population_display_name(pop1, group), "Denominator Observation")
        self.assertEqual(cqfm_population_display_name(pop2, group), "Numerator Observation")

    def test_plural_expression_is_canonicalised(self):
        """CMS871-shaped: plural expressions still resolve to the singular
        canonical form via POPULATION_ALIASES."""
        pop1 = _obs_pop("MO_1_1", "Denominator Observations", "Denominator_1")
        pop2 = _obs_pop("MO_1_2", "Numerator Observations", "Numerator_1")
        group = {"population": [pop1, pop2]}
        self.assertEqual(cqfm_population_display_name(pop1, group), "Denominator Observation")
        self.assertEqual(cqfm_population_display_name(pop2, group), "Numerator Observation")


class FindCqfmAggregationExclusionsTest(unittest.TestCase):

    def test_flags_population_with_both_extensions(self):
        # A single measure-observation population in the group uses the
        # generic coding display ("Measure Observation") -- disambiguation by
        # expression only kicks in with >1 sibling in the same group.
        measure = {"group": [{
            "id": "Group_1",
            "population": [_obs_pop("MO_1", "Denominator Observation", "Denominator_1")],
        }]}
        self.assertEqual(
            find_cqfm_aggregation_exclusions(measure),
            frozenset({"Group_1:Measure Observation"}))

    def test_value_code_is_also_recognised(self):
        """CMS986 uses valueCode instead of valueString for cqfm-aggregateMethod."""
        measure = {"group": [{
            "id": "Group_1",
            "population": [_obs_pop("MO_1", "Measure Observation 1", "MeasurePopulation_1",
                                     agg_url_key="valueCode")],
        }]}
        self.assertIn("Group_1:Measure Observation", find_cqfm_aggregation_exclusions(measure))

    def test_population_with_only_one_extension_is_not_flagged(self):
        pop = _obs_pop("MO_1", "Denominator Observation", "Denominator_1")
        pop["extension"] = [{"url": REF_URL, "valueString": "Denominator_1"}]  # no aggregateMethod
        measure = {"group": [{"id": "Group_1", "population": [pop]}]}
        self.assertEqual(find_cqfm_aggregation_exclusions(measure), frozenset())

    def test_unrelated_extensions_are_ignored(self):
        pop = _plain_pop("Denominator_1", "denominator", "Denominator", "Denominator")
        pop["extension"] = [{"url": "http://example.com/unrelated", "valueString": "x"}]
        measure = {"group": [{"id": "Group_1", "population": [pop]}]}
        self.assertEqual(find_cqfm_aggregation_exclusions(measure), frozenset())

    def test_non_observation_populations_are_never_flagged(self):
        measure = {"group": [{
            "id": "Group_1",
            "population": [
                _plain_pop("InitialPopulation_1", "initial-population", "Initial Population", "Initial Population"),
                _plain_pop("Denominator_1", "denominator", "Denominator", "Denominator"),
                _obs_pop("MO_1", "Denominator Observation", "Denominator_1"),
            ],
        }]}
        excluded = find_cqfm_aggregation_exclusions(measure)
        self.assertNotIn("Group_1:Initial Population", excluded)
        self.assertNotIn("Group_1:Denominator", excluded)

    def test_generic_label_safety_net_is_a_noop_when_it_equals_the_specific_name(self):
        """CMS986-shaped: one observation per group, so the generic label
        already IS the specific excluded cell -- no duplicate-meaning entries."""
        measure = {"group": [{
            "id": "Group_1",
            "population": [_obs_pop("MO_1", "Measure Observation 1", "MeasurePopulation_1")],
        }]}
        self.assertEqual(
            find_cqfm_aggregation_exclusions(measure),
            frozenset({"Group_1:Measure Observation"}))

    def test_group_without_cqfm_observation_contributes_nothing(self):
        measure = {"group": [{
            "id": "Group_1",
            "population": [
                _plain_pop("InitialPopulation_1", "initial-population", "Initial Population", "Initial Population"),
                _plain_pop("Denominator_1", "denominator", "Denominator", "Denominator"),
            ],
        }]}
        self.assertEqual(find_cqfm_aggregation_exclusions(measure), frozenset())


class LoadCqfmAggregationExclusionsTest(unittest.TestCase):

    def test_loads_per_measure_from_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            with_cqfm = {"group": [{
                "id": "Group_1",
                "population": [_obs_pop("MO_1", "Denominator Observation", "Denominator_1")],
            }]}
            without_cqfm = {"group": [{
                "id": "Group_1",
                "population": [
                    _plain_pop("InitialPopulation_1", "initial-population", "Initial Population", "Initial Population"),
                ],
            }]}
            with open(os.path.join(tmp, "MeasureWithCqfm.json"), "w") as fh:
                json.dump(with_cqfm, fh)
            with open(os.path.join(tmp, "MeasureWithoutCqfm.json"), "w") as fh:
                json.dump(without_cqfm, fh)

            result = load_cqfm_aggregation_exclusions(tmp)

        self.assertIn("MeasureWithCqfm", result)
        self.assertNotIn("MeasureWithoutCqfm", result)
        self.assertEqual(
            result["MeasureWithCqfm"],
            frozenset({"Group_1:Measure Observation"}))


class LiveMeasureResourceRegressionTest(unittest.TestCase):
    """Pins the exact, confirmed ground truth against the real Measure
    resources, so a future accidental edit to CQFM wiring is caught by CI
    rather than silently changing what this harness scores."""

    def test_exactly_three_measures_are_affected(self):
        result = load_cqfm_aggregation_exclusions(MEASURE_RESOURCE_DIR)
        self.assertEqual(
            set(result),
            {"CMS1017FHIRHHFI", "CMS871FHIRHHHyper", "CMS986FHIRMalnutritionScore"})

    def test_cms1017_exclusions(self):
        result = load_cqfm_aggregation_exclusions(MEASURE_RESOURCE_DIR)
        self.assertEqual(
            result["CMS1017FHIRHHFI"],
            frozenset({
                "Group_1:Denominator Observation",
                "Group_1:Numerator Observation",
                "Group_1:Measure Observation",
            }))

    def test_cms871_exclusions(self):
        result = load_cqfm_aggregation_exclusions(MEASURE_RESOURCE_DIR)
        self.assertEqual(
            result["CMS871FHIRHHHyper"],
            frozenset({
                "Group_1:Denominator Observation",
                "Group_1:Numerator Observation",
                "Group_1:Measure Observation",
            }))

    def test_cms986_exclusions(self):
        result = load_cqfm_aggregation_exclusions(MEASURE_RESOURCE_DIR)
        self.assertEqual(
            result["CMS986FHIRMalnutritionScore"],
            frozenset({f"Group_{n}:Measure Observation" for n in range(1, 7)}))


if __name__ == "__main__":
    unittest.main()
