# dqm-content-cms-2025
Draft CMS dQM Measure Content (Using USCore 6.1.0-derived, USQualityCore 0.1.0-cibuild, based on FHIR R4 v4.0.1)

> This repository contains draft 2025AU content refactored to use the USQualityCore 0.1.0-cibuild, and US Core 6.1.0-derived models. All measure content in this repository was copied from the dqm-content-qicore-2025 repository and refactored using the VSCode CQL Authoring plugin.

Measures in this repository were refactored following the [US Quality Core Update Process](USQualityCoreUpdateProcess.md)

Commits to this repository will automatically trigger a build of the continuous integration build, available here:

https://build.fhir.org/ig/cqframework/dqm-content-cms-2025

## Repository Structure

This repository is setup like any HL7 FHIR IG project but also includes the CQL files and test data which means the file structure will be as follows:

```
   |-- _genonce.bat
   |-- _genonce.sh
   |-- _refresh.bat
   |-- _refresh.sh
   |-- _updatePublisher.bat
   |-- _updatePublisher.sh
   |-- _updateCQFTooling.bat
   |-- _updateCQFTooling.sh
   |-- ig.ini
   |-- bundles
       |-- mat
           |-- <bundle files>
       |-- measure
           |-- <bundles>
   |-- input
       |-- dqm-content-cms-2025.xml
       |-- cql
           |-- <library name>.cql
       |-- pagecontent
       |-- resources
           |-- library
               |-- <library name>.json
           |-- measure
               |-- <measure name>.json
       |-- tests
           |-- measure
               |-- <measure name>
                   |-- <test case patient id>
                       |-- <test case resource files>
                   |-- ...
       |-- vocabulary
           |-- valueset
               |-- external
```

## Extracting MAT Packages

CQF Tooling provides support for extracting a MAT exported package into the
directories of this repository so that the measure is included in the published
implementation guide. To do this, place the MAT export files (unzipped) in a
directory in the `bundles\mat` directory, and then run the following tooling
command:

```
[tooling-jar] -ExtractMatBundle bundles\mat\[bundle-directory]\[bundle-file]
```

For example:

```
input-cache\tooling-cli-3.9.1.jar -ExtractMATBundle bundles\mat\CLONE124_v6_03-Artifacts\measure-json-bundle.json
```

## Refresh IG Processing

CQF Tooling provides a "refresh" operation that performs the following functions:

* Translates and validates all CQL source files
* Encodes CQL and ELM content in the corresponding FHIR Library resources
* Refreshes generated content for each knowledge artifact (Library, Measure, PlanDefinition, ActivityDefinition) including parameters, dependencies, and effective data requirements

Whenever changes are made to the CQL, Library, or Measure resources, run the `_refresh` command to refresh the implementation guide content with the new content, and then run `_genonce` to run the publication tooling on the implementation guide (the same process that the continuous integration build uses to publish the implementation guide when commits are made to this repository).


## Measure Package Prep Process

1. Download Measure Zip folder to `bundles\mat` directory.
2. Unzip the folder, then unzip the MeasureExport and TestCaseExport folders within it.
3. Run `_updateCQFTooling.sh` script to ensure CQF tooling jar is present.
4. Update `_extractMATBundle.sh` so that `mat_bundle` points to the JSON file within the MeasureExport directory.
5. Run `_extractMATBundle.sh` to load Measure Resources.
6. Create a directory under `input\tests\measure` with the Measure ID.
7. Copy all files from the TestCaseExport directory to this newly created directory.
8. Update `_extractBundleResources.sh` so that `mat_bundle` points to this newly created directory.
9. Run `_extractBundleResources.sh` to populate test case resources.
10. Run `_refresh.sh` to refresh IG content.
