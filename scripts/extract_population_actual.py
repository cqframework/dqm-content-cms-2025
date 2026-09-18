import os
import argparse
import json
import re
import csv
from collections import namedtuple
from typing import Generator, List, Dict, Union, Tuple

VERBOSE=False

MeasureSection = namedtuple('MeasureSection', ['measure', 'section'])
MeasureResultId = namedtuple('MeasureResultId', ['Measure', 'PatientGUID', 'GroupId'])

header = ["measure_name", "guid", "population", "count"]

allowed_display_names = {
    "Initial Population",
    "Initial Population 1",
    "Initial Population 2",
    "Denominator",
    "Denominator 1",
    "Denominator 2",
    "Denominator Exclusion",
    "Denominator Exclusions",
    "Denominator Exception",
    "Denominator Exceptions",
    "Denominator Observation",
    "Numerator",
    "Numerator 1",
    "Numerator 2",
    "Numerator Exclusion",
    "Numerator Exclusions",
    "Numerator Observation",
    "Measure Population",
    "Measure Population Observation",
    "Measure Population Observations",
    "Measure Population Exclusion",
    "Measure Population Exclusions"
}

patient_pattern = re.compile(r'Patient\s*=\s*Patient\(id=(?P<id>[a-f0-9\-]+)\)')
json_patient_pattern = re.compile(r'Patient\(id=(?P<id>[a-f0-9\-]+)\)')
expression_pattern = re.compile(rf'^(?P<expression>(?:{"|".join(list(allowed_display_names))})(?:\s*\d*))\s*=\s*(?P<value>.*)')
section_pattern = re.compile(r'\n\s*\n')   # Split sections by two line breaks instead of hyphens

def log(message: str):
    if VERBOSE:
        print(message)

def find_all_groups_by_expression(measure_criteria: Dict[str, Dict[str, str]], expression: str) -> Dict[str, str]:
    return {group: criteria_map[expression] for group, criteria_map in measure_criteria.items() if expression in criteria_map}

def extract_measure_criteria(measure_data: Dict) -> Dict[str, Dict[str, str]]:
    """Extract Measure Criteria 

    Args:
        measure_data (Dict): measure results data from a CQL results txt file

    Returns:
        Dict[str, Dict[str, str]]: Measure Criteria as Dict[<GROUP ID>, Dict[<EXPRESSION>, <POPULATION>]]
    """
    measure_criteria = {}
    for group in measure_data.get('group', []):
        criteria_map = measure_criteria.setdefault(group['id'], {})
        for pop in group.get('population', []):
            expression = pop.get('criteria', {}).get('expression', '')
            if pop.get('id', '') == 'MeasureObservation_1_1':
                population = 'Denominator Observation'
            elif pop.get('id', '') == 'MeasureObservation_1_2':
                population = 'Numerator Observation'
            else:
                population = pop.get('code', {}).get('coding', [{}])[0].get('display', '')
            # Index by measure_name, group_id, and expression
            criteria_map[expression] = population
    return measure_criteria

def load_measure_criteria(measure_resource_dir: str) -> Dict[str, Dict[str, Dict[str, str]]]:
    """Load Measure Criteria from all files in the specified directory

    Args:
        measure_resource_dir (str): path to directory with measure resource files

    Returns:
        Dict[str, Dict[str, Dict[str, str]]]: All Measure Criteria as Dict[<MEASURE NAME>, Dict[<GROUP ID>, Dict[<EXPRESSION>, <POPULATION>]]]
    """
    measure_criteria_map = {}
    for measure_file in os.listdir(measure_resource_dir):
        if measure_file.endswith('.json'):
            measure_path = os.path.join(measure_resource_dir, measure_file)
            measure_name = os.path.splitext(measure_file)[0]
            with open(measure_path, 'r') as f:
                measure_data = json.load(f)
                measure_criteria = extract_measure_criteria(measure_data)
                measure_criteria_map[measure_name] = measure_criteria
    return measure_criteria_map

def parse_count(result_value: str) -> Union[int, str]:
    result_value = result_value.strip()
    if result_value.lower() == "true":
        return 1
    elif result_value.lower() == "false":
        return 0
    elif result_value.lower() == "null":
        return 0
    elif result_value.startswith("[") and result_value.endswith("]"):
        items = [item.strip() for item in result_value[1:-1].split(",") if item.strip()]
        return items
    else:
        return result_value  # fallback, could be a number or string

def validate_measure_population_counts(measurename: str, populations: Dict[str, str]):
    # scoring validation based on https://build.fhir.org/ig/HL7/cqf-measures/measure-conformance.html#proportion-measure-scoring
    inital = populations.get('Initial Population', 0)
    denom = populations.get('Denominator', 0)
    denex = populations.get('Denominator Exclusion', 0)
    numer = populations.get('Numerator', 0)
    numex = populations.get('Numerator Exclusion', 0)
    denexc = populations.get('Denominator Exception', 0)
    measurepop = populations.get('Measure Population', 0)
    measurepopexc = populations.get('Measure Population Exclusion', 0)
    
    initial_count = len(inital) if isinstance(inital, list) else inital
    denom_count = len(denom) if isinstance(denom, list) else denom
    numer_count = len(numer) if isinstance(numer, list) else numer
    denex_count = len(denex) if isinstance(denex, list) else denex
    numex_count = len(numex) if isinstance(numex, list) else numex
    denexc_count = len(denexc) if isinstance(denexc, list) else denexc
    measurepop_count = len(measurepop) if isinstance(measurepop, list) else measurepop
    measurepopexc_count = len(measurepopexc) if isinstance(measurepopexc, list) else measurepopexc

    
    if denom_count < 2:
        if not numer and numex and (denom and denex):
            numer_count = 0
            numex_count = 0
        if numer and not numex and (denom and denex) or not denom:
            numer_count = 0
        if not numer and numex:
            numex_count = 0
        if not denom and denex:
            denex_count = 0
        if not numer and not denom:
            denexc_count = 0
        if numer and denom:
            denexc_count = 0
    else:
        if numer and not numex:
            if isinstance(numer, list) and isinstance(denex, list):
                for item in numer:
                    if item in denex:
                        numer_count -= 1
            else:
                if denex >= 1 and numer > 1:
                    numer_count = numer_count - denex_count

    # save updated scoring back to population, but only if the value already existed in the population
    if 'Numerator'in populations:
        populations['Numerator'] = numer_count
    if 'Denominator Exclusion'in populations:
        populations['Denominator Exclusion'] = denex_count
    if 'Numerator Exclusion'in populations:
        populations['Numerator Exclusion'] = numex_count
    if 'Denominator Exception'in populations:
        populations['Denominator Exception'] = denexc_count
    if 'Denominator'in populations:
        populations['Denominator'] = denom_count
    if 'Initial Population'in populations:
        populations['Initial Population'] = initial_count
    if 'Measure Population'in populations:
        populations['Measure Population'] = measurepop_count
    if 'Measure Population Exclusion'in populations:
        populations['Measure Population Exclusion'] = measurepopexc_count

def detect_results_format(dir_path: str) -> str:
    """Determine the result file format present in dir_path.

    Flat *.txt result files may live directly in dir_path or inside a per-measure
    subdirectory dir_path/<MEASURE NAME>/. JSON test case result files live only
    inside per-measure subdirectories. The presence of any *.txt file takes
    precedence and selects the text format.

    Args:
        dir_path (str): path to directory with VSCode CQL Extension result files

    Returns:
        str: 'txt' when any *.txt result file is found, otherwise 'json'.
    """
    for entry in sorted(os.listdir(dir_path)):
        if entry.startswith('.'):
            continue
        entry_path = os.path.join(dir_path, entry)
        if os.path.isdir(entry_path):
            for file_name in sorted(os.listdir(entry_path)):
                if not file_name.startswith('.') and file_name.endswith('.txt'):
                    return 'txt'
        elif os.path.isfile(entry_path) and entry.endswith('.txt'):
            return 'txt'
    return 'json'

def load_measure_sections(dir_path: str) -> Generator['MeasureSection', None, None]:
    """Load Measure Sections from flat VS Code CQL Extension result files.

    Flat *.txt result files may live directly in dir_path or inside a per-measure
    subdirectory dir_path/<MEASURE NAME>/.

    Args:
        dir_path (str): path to directory with VSCode CQL Extension result files

    Yields:
        Generator['MeasureSection', None, None]: A generator object that yields MeasureSections
    """
    for entry in sorted(os.listdir(dir_path)):
        # Skip hidden/system files like .DS_Store
        if entry.startswith('.'):
            continue
        entry_path = os.path.join(dir_path, entry)
        if os.path.isdir(entry_path):
            for file_name in sorted(os.listdir(entry_path)):
                if file_name.startswith('.') or not file_name.endswith('.txt'):
                    continue
                log(f' {entry}/{file_name}')
                file_path = os.path.join(entry_path, file_name)
                if os.path.isfile(file_path):
                    measure_name = entry
                    with open(file_path, "r") as f:
                        content = f.read()
                    for section in section_pattern.split(content):
                        yield MeasureSection(measure_name, section)
        elif entry.endswith('.txt') and os.path.isfile(entry_path):
            log(f' {entry}')
            measure_name = os.path.splitext(entry)[0]
            with open(entry_path, "r") as f:
                content = f.read()
            for section in section_pattern.split(content):
                yield MeasureSection(measure_name, section)

def load_json_results(dir_path: str) -> Generator['MeasureSection', None, None]:
    """Load Measure Sections from VSCode CQL Extension JSON Test Case result files.

    JSON results are written to input/tests/results/<MEASURE NAME>/TestCaseResult-<testCaseId>.json.

    Args:
        dir_path (str): path to directory containing one subdirectory per measure

    Yields:
        Generator['MeasureSection', None, None]: A generator that yields MeasureSections
            whose section is the parsed JSON dict of a single test case.
    """
    for entry in sorted(os.listdir(dir_path)):
        if entry.startswith('.') or not os.path.isdir(os.path.join(dir_path, entry)):
            continue
        measure_path = os.path.join(dir_path, entry)
        for file_name in sorted(os.listdir(measure_path)):
            if file_name.startswith('.') or not file_name.endswith('.json'):
                continue
            log(f' {entry}/{file_name}')
            file_path = os.path.join(measure_path, file_name)
            if os.path.isfile(file_path):
                with open(file_path, "r") as f:
                    data = json.load(f)
                measure_name = data.get('libraryName') or entry
                yield MeasureSection(measure_name, data)

def create_empty_populations(measure_name:str, patient_guid: str, measure_criteria: Dict[str, Dict[str, str]]) -> Dict[MeasureResultId, Dict[str, str]]:
    return {
        MeasureResultId(measure_name, patient_guid, group): {population: 0 for population in expression_population_map.values()}
        for group, expression_population_map in measure_criteria.items()
    }

def capture_results(measure_sections: Generator['MeasureSection', None, None], all_measure_criteria: Dict[str, Dict[str, Dict[str, str]]]) -> Dict[MeasureResultId, Dict[str, str]]:
    """Convert measure sections (data from VSCode CQL extension results)

    Args:
        measure_sections (Generator[&#39;MeasureSection&#39;, None, None]): A generator object that yields MeasureSections
        all_measure_criteria (Dict[str, Dict[str, Dict[str, str]]]): All Measure Criteria as Dict[<MEASURE NAME>, Dict[<GROUP ID>, Dict[<EXPRESSION>, <POPULATION>]]]

    Returns:
        Dict[MeasureResultId, Dict[str, str]]: Results that match the allowed_display_names.
    """
    results = {}
    for measure_section in measure_sections:
        measure_name = measure_section.measure
        section_data = measure_section.section
        if isinstance(section_data, dict):
            results.update(capture_json_results(measure_name, section_data, all_measure_criteria))
            continue
        patient_guid_match = patient_pattern.search(section_data)
        if patient_guid_match:
            patient_guid = patient_guid_match.group('id')
            results.update(create_empty_populations(measure_name, patient_guid, all_measure_criteria[measure_section.measure]))
            for line in section_data.splitlines():
                expression_match = expression_pattern.search(line)
                if expression_match:
                    measure_criteria = all_measure_criteria[measure_name]
                    for group, population in find_all_groups_by_expression(measure_criteria, expression_match.group('expression')).items():
                        results[MeasureResultId(measure_name, patient_guid, group)][population] = parse_count(expression_match.group('value'))
    return results

def capture_json_results(measure_name: str, section_data: Dict, all_measure_criteria: Dict[str, Dict[str, Dict[str, str]]]) -> Dict[MeasureResultId, Dict[str, str]]:
    """Convert a single JSON test case result (data from VSCode CQL extension JSON results)

    Args:
        measure_name (str): name of the measure/library
        section_data (Dict): parsed JSON test case result
        all_measure_criteria (Dict[str, Dict[str, Dict[str, str]]]): All Measure Criteria as Dict[<MEASURE NAME>, Dict[<GROUP ID>, Dict[<EXPRESSION>, <POPULATION>]]]

    Returns:
        Dict[MeasureResultId, Dict[str, str]]: Results that match the allowed_display_names.
    """
    results = {}
    if section_data.get('errors'):
        log(f'   ({measure_name}) skipping test case with errors: {section_data.get("testCaseName")}')
        return results
    patient_guid = section_data.get('testCaseName')
    if not patient_guid:
        patient_value = next((result.get('value', '') for result in section_data.get('results', []) if result.get('name') == 'Patient'), '')
        patient_guid_match = json_patient_pattern.search(patient_value)
        if not patient_guid_match:
            return results
        patient_guid = patient_guid_match.group('id')
    results.update(create_empty_populations(measure_name, patient_guid, all_measure_criteria[measure_name]))
    measure_criteria = all_measure_criteria[measure_name]
    for result in section_data.get('results', []):
        expression = result.get('name')
        if not expression:
            continue
        for group, population in find_all_groups_by_expression(measure_criteria, expression).items():
            results[MeasureResultId(measure_name, patient_guid, group)][population] = parse_count(str(result.get('value')))
    return results

def convert_results_to_rows(results: Dict[MeasureResultId, Dict[str, str]]) -> List[List[str]]:
    # convert results dict to rows
    # during conversion verify that proper proportional eCQM population criteria rules are followed
    rows = []
    for measure_id, populations in results.items():
        validate_measure_population_counts(measure_id.Measure,populations)
        for population, count in populations.items():
            rows.append([measure_id.Measure, measure_id.PatientGUID, f'{measure_id.GroupId}:{population}', count])
    return rows

def save_results(output_file: str, rows: List[List[str]]):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header)
        writer.writerows(rows)


_MEASURE_RESOURCE_DIR = "./input/resources/measure"
_DEFAULT_OUTPUT = "./scripts/comparison/actual_results.csv"
_DEFAULT_RESULTS_DIR = "./input/tests/results"


def main(argv=None):
    """Parse argv (or sys.argv) and run the extract.

    Exposed as a function so other scripts (notably ``run_reports.py`` step 0/6)
    can call into the same logic without re-implementing the wiring or
    spawning a subprocess.
    """
    global VERBOSE
    VERBOSE = True

    parser = argparse.ArgumentParser(description="Extract actual population counts from CQL engine result files.")
    parser.add_argument("--results-dir", default=_DEFAULT_RESULTS_DIR,
                        help=f"Directory containing result files. Defaults to '{_DEFAULT_RESULTS_DIR}'.")
    parser.add_argument("--output", default=_DEFAULT_OUTPUT,
                        help=f"Where to write the extracted CSV. Defaults to '{_DEFAULT_OUTPUT}'.")
    format_group = parser.add_mutually_exclusive_group()
    format_group.add_argument("-jr", "--json-results", action="store_true",
                              help="Read JSON test case result files (input/tests/results/<MEASURE NAME>/TestCaseResult-*.json).")
    format_group.add_argument("-txt", "--text-results", action="store_true",
                              help="Read flat text result files (*.txt), either directly in the results directory or in per-measure subdirectories.")
    args = parser.parse_args(argv)

    log("Loading Measure Criteria")
    all_measure_criteria = load_measure_criteria(_MEASURE_RESOURCE_DIR)

    log("Loading Measures")
    if args.json_results:
        measure_sections = load_json_results(args.results_dir)
    elif args.text_results:
        measure_sections = load_measure_sections(args.results_dir)
    else:
        results_format = detect_results_format(args.results_dir)
        log(f"No result format flag provided; detected '{results_format}' format in '{args.results_dir}'.")
        if results_format == 'txt':
            measure_sections = load_measure_sections(args.results_dir)
        else:
            measure_sections = load_json_results(args.results_dir)

    log("Capturing Results")
    results = capture_results(measure_sections, all_measure_criteria)

    log("Analyzing Results")
    rows = convert_results_to_rows(results)

    log("Saving Results")
    save_results(args.output, rows)


if __name__ == '__main__':
    main()
