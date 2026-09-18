import json
import unittest
from collections import namedtuple
from typing import Dict, NamedTuple

from scripts.extract_population_actual import *

# Run tests from project root
# python -m scripts.tests.test_extract_population_actual

class MeasureCriteria(NamedTuple):
    measure_data: Dict
    expected_criteria: Dict

class TestExtractPopulationActual(unittest.TestCase):

    def test_parse_count_true_returns_1(self):
        """Test for parse_count returns 1 for true"""
        self.assertEqual(parse_count('true'), 1)
        self.assertEqual(parse_count('True'), 1)
        self.assertEqual(parse_count('TRUE'), 1)
    
    def test_parse_count_false_returns_0(self):
        """Test for parse_count returns 0 for false"""
        self.assertEqual(parse_count('false'), 0)
        self.assertEqual(parse_count('False'), 0)
        self.assertEqual(parse_count('FALSE'), 0)

    # These five previously called `validate_numerator(populations)`, which was
    # removed when scoring validation was widened into
    # `validate_measure_population_counts(measurename, populations)`. The tests
    # were never updated, so they had been failing with NameError ever since.
    # Retargeted at the successor, which keeps the same mutate-in-place contract
    # on `populations` and adds a measure name for logging.

    def test_validate_scoring_denom_true_numer_true_then_numer_true(self):
        populations = {
            'Denominator': 1,
            'Numerator': 1
        }
        validate_measure_population_counts('CMS-test', populations)
        self.assertEqual(populations['Denominator'], 1)
        self.assertEqual(populations['Numerator'], 1)

    def test_validate_scoring_denom_false_numer_true_then_numer_false(self):
        populations = {
            'Denominator': 0,
            'Numerator': 1
        }
        validate_measure_population_counts('CMS-test', populations)
        self.assertEqual(populations['Denominator'], 0)
        self.assertEqual(populations['Numerator'], 0)

    def test_validate_scoring_denom_true_denex_false_numer_true_then_numer_true(self):
        populations = {
            'Denominator': 1,
            'Denominator Exclusion': 0,
            'Numerator': 1
        }
        validate_measure_population_counts('CMS-test', populations)
        self.assertEqual(populations['Denominator'], 1)
        self.assertEqual(populations['Denominator Exclusion'], 0)
        self.assertEqual(populations['Numerator'], 1)

    def test_validate_scoring_denom_true_denex_true_numer_true_then_denom_false_numer_false(self):
        populations = {
            'Denominator': 1,
            'Denominator Exclusion': 1,
            'Numerator': 1
        }
        validate_measure_population_counts('CMS-test', populations)
        self.assertEqual(populations['Denominator'], 1)
        self.assertEqual(populations['Denominator Exclusion'], 1)
        self.assertEqual(populations['Numerator'], 0)

    def test_validate_scoring_denom_true_numer_true_denexp_true_then_denexp_zeroed(self):
        """Expectation deliberately changed from the pre-removal version.

        The old `validate_numerator` left Denominator Exception at 1 here. The
        successor zeroes it, which is the conformant behaviour: a patient who
        meets the Numerator cannot also be a Denominator Exception (an exception
        removes a patient from the denominator only when they did *not* meet the
        numerator). See the proportion-measure scoring rules linked in
        `validate_measure_population_counts`. The old assertion encoded the bug.
        """
        populations = {
            'Denominator': 1,
            'Denominator Exception': 1,
            'Numerator': 1,
        }
        validate_measure_population_counts('CMS-test', populations)
        self.assertEqual(populations['Denominator'], 1)
        self.assertEqual(populations['Numerator'], 1)
        self.assertEqual(populations['Denominator Exception'], 0)

    def test_convert_results_to_rows(self):
        results = {
            MeasureResultId('measureA', 'guidA', 'groupA'): {
                'denom': 1,
                'numer': 1,
            },
            MeasureResultId('measureA', 'guidA', 'groupB'): {
                'denom': 0,
                'numer': 0,
            },
            MeasureResultId('measureB', 'guidB', 'groupA'): {
                'denom': 1,
                'numer': 0,
            }
        }

        expected_rows = [
            ['measureA', 'guidA', 'groupA:denom', 1],
            ['measureA', 'guidA', 'groupA:numer', 1],
            ['measureA', 'guidA', 'groupB:denom', 0],
            ['measureA', 'guidA', 'groupB:numer', 0],
            ['measureB', 'guidB', 'groupA:denom', 1],
            ['measureB', 'guidB', 'groupA:numer', 0],
        ]

        actual_rows = convert_results_to_rows(results)
        self.assertListEqual(expected_rows, actual_rows)

    def test_load_measure_sections(self):
        with open('./scripts//tests/resources/sample_results/.test_case_data/.load_measure_test_case_data.json', 'r') as file:
            test_case_data = json.load(file)

        for measure_section in load_measure_sections('./scripts/tests/resources/sample_results'):
            self.assertIn(measure_section.section, test_case_data['expected_results'][measure_section.measure])
            
            # remove the section from the list, 
            # later will check that the expected list is empty
            # this will prove all expected items were found
            test_case_data['expected_results'][measure_section.measure].remove(measure_section.section)
            if not test_case_data['expected_results'][measure_section.measure]:
                test_case_data['expected_results'].pop(measure_section.measure)
        
        self.assertFalse(test_case_data['expected_results'])

    def test_capture_results(self):
        with open('./scripts/tests/resources/sample_results/.test_case_data/.capture_results_test_case_data.json', 'r') as file:
            test_case_data = json.load(file)
        
        actual_results = capture_results(load_measure_sections('./scripts/tests/resources/sample_results'), test_case_data['all_measure_criteria'])
        actual_results_as_dict = {f'{measure_id.Measure}:{measure_id.PatientGUID}:{measure_id.GroupId}': population_count for measure_id, population_count in actual_results.items()}
        self.assertDictEqual(test_case_data['expected_results'], actual_results_as_dict)
    
    def test_create_empty_populations(self):
        measure_criteria = {
            'Group_1': {
                'Denominator 1': "Denominator",
                'Numerator': "Numerator",
            },
            'Group_2': {
                'Denominator 2': "Denominator",
                'Numerator': "Numerator",
            }
        }
        measure_name = 'some_measure'
        patient_guid = '335cae91-96fc-4337-88f6-b8d9f06ade01'
        expected_results = {
            MeasureResultId(measure_name, patient_guid, 'Group_1'): {'Denominator': 0, 'Numerator': 0},
            MeasureResultId(measure_name, patient_guid, 'Group_2'): {'Denominator': 0, 'Numerator': 0}
        }
        actual_results = create_empty_populations(measure_name, patient_guid, measure_criteria)
        self.assertDictEqual(expected_results, actual_results)

    @classmethod
    def get_test_case(cls, file_path: str) -> MeasureCriteria:
        with open(file_path, "r") as f:
            test_case_data = json.load(f)
            return MeasureCriteria(test_case_data['measure_data'], test_case_data['expected_results'])

    def test_extract_measure_criteria_simple(self):
        test_case_data = TestExtractPopulationActual.get_test_case('./scripts//tests/resources/sample_measure_definitions/simple_mapping.json')
        actual_criteria = extract_measure_criteria(test_case_data.measure_data)
        self.assertDictEqual(test_case_data.expected_criteria, actual_criteria)

    def test_extract_measure_criteria_multiple_groups(self):
        test_case_data = TestExtractPopulationActual.get_test_case('./scripts//tests/resources/sample_measure_definitions/sample_multiple_groups.json')
        actual_criteria = extract_measure_criteria(test_case_data.measure_data)
        self.assertDictEqual(test_case_data.expected_criteria, actual_criteria)

    def test_find_all_groups_by_expression(self):
        measure_criteria = {
            "Group_1": {
                "Initial Population 1": "Initial Population",
                "Denominator 1": "Denominator",
                "Numerator": "Numerator"
            },
            "Group_2": {
                "Initial Population 2": "Initial Population",
                "Denominator 2": "Denominator",
                "Numerator": "Numerator"
            }
        }
        self.assertDictEqual(
            {
                'Group_1': 'Numerator',
                'Group_2': 'Numerator'
            }, 
            find_all_groups_by_expression(measure_criteria, 'Numerator'))
        
        self.assertDictEqual(
            {
                'Group_2': 'Denominator'
            }, 
            find_all_groups_by_expression(measure_criteria, 'Denominator 2'))

if __name__ == '__main__':
    unittest.main()