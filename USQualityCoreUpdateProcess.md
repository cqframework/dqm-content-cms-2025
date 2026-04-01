This topic describes a process for refactoring [FHIR-based 2025 AU draft CMS measures](http://github.com/cqframework/dqm-content-qicore-2025) expressed using QI Core version 6.0.0 to:

1. Use the [US Quality Core Implementation Guide](http://build.fhir.org/ig/FHIR/us-quality-core) as the model
2. Make use of shared artifacts in the [Common CQL Artifacts for FHIR (US-Based) Implementation Guide](https://build.fhir.org/ig/HL7/us-cql-ig)

> NOTE: Throughout this discussion, we use the version `0.1.0-cibuild` for the US Quality Core references. This is because we are referencing a pre-publication draft. When US Quality Core publishes, the versions will be updated to the published version (most likely `1.0.0`).

For the purposes of this discussion, we will be focusing on the following 5 measures:

| Measure | QI Core | US Quality Core |
|----|----|----|
| CMS2: Preventive Care and Screening: Depression Screening and Followup | [QICore](https://github.com/cqframework/dqm-content-qicore-2025/blob/master/input/cql/CMS2FHIRPCSDepScreenAndFollowUp.cql) | [USQualityCore](https://github.com/cqframework/dqm-content-cms-2025/blob/main/input/cql/CMS2FHIRPCSDepScreenAndFollowUp.cql) |
| CMS108: VTE Prophylaxis | | |
| CMS122: Diabetes: Glycemic Status Assessment | [QICore](https://github.com/cqframework/dqm-content-qicore-2025/blob/master/input/cql/CMS122FHIRDiabetesAssessGT9Pct.cql) | [USQualityCore](https://github.com/cqframework/dqm-content-cms-2025/blob/main/input/cql/CMS122FHIRDiabetesAssessGT9Pct.cql)* |
| CMS125: Breast Cancer Screening | [QICore](https://github.com/cqframework/dqm-content-qicore-2025/blob/master/input/cql/CMS125FHIRBreastCancerScreen.cql) | [USQualityCore](https://github.com/cqframework/dqm-content-cms-2025/blob/main/input/cql/CMS125FHIRBreastCancerScreen.cql) |
| CMS130: Colon Cancer Screening | [QICore](https://github.com/cqframework/dqm-content-qicore-2025/blob/master/input/cql/CMS130FHIRColorectalCancerScrn.cql) | [USQualityCore](https://github.com/cqframework/dqm-content-cms-2025/blob/main/input/cql/CMS130FHIRColorectalCancerScrn.cql)* |
| CMS135: CMS135FHIRACEIorARBorARNIforHF | | |
| CMS165: Controlling High Blood Pressure | [QICore](https://github.com/cqframework/dqm-content-qicore-2025/blob/master/input/cql/CMS165FHIRControllingHighBP.cql) | [USQualityCore](https://github.com/cqframework/dqm-content-cms-2025/blob/main/input/cql/CMS165FHIRControllingHighBP.cql)* |
| CMS986: Global Malnutrition Score | | |
| CMS1206: Excessive Radiation: Outpatient Quality Reporting | | |
| NHSN Glycemic Control | | |

Note: Measures marked with an asterisk are still in progress

These are all EC measures that make use of the following shared libraries:

| Shared Library | QI Core | US Quality Core |
|----|----|----|
| AdultOutpatientEncounters | [QICore](https://github.com/cqframework/dqm-content-qicore-2025/blob/master/input/cql/AdultOutpatientEncounters.cql) | [USQualityCore](https://github.com/cqframework/dqm-content-cms-2025/blob/main/input/cql/AdultOutpatientEncounters.cql) |
| AdvancedIllnessandFrailty | [QICore](https://github.com/cqframework/dqm-content-qicore-2025/blob/master/input/cql/AdvancedIllnessandFrailty.cql) | [USQualityCore](https://github.com/cqframework/dqm-content-cms-2025/blob/main/input/cql/AdvancedIllnessandFrailty.cql) |
| AHAOverall | | |
| AlaraCommonFunctions | | |
| CumulativeMedicationDuration | [QICore](https://github.com/cqframework/dqm-content-qicore-2025/blob/master/input/cql/CumulativeMedicationDuration.cql) | [USQualityCore](https://build.fhir.org/ig/HL7/us-cql-ig/en/Library-CumulativeMedicationDuration.html) |
| Hospice | [QICore](https://github.com/cqframework/dqm-content-qicore-2025/blob/master/input/cql/Hospice.cql) | [USQualityCore](https://github.com/cqframework/dqm-content-cms-2025/blob/main/input/cql/Hospice.cql) |
| PalliativeCare | [QICore](https://github.com/cqframework/dqm-content-qicore-2025/blob/master/input/cql/PalliativeCare.cql) | [USQualityCore](https://github.com/cqframework/dqm-content-cms-2025/blob/main/input/cql/PalliativeCare.cql) |
| QICoreCommon | [QICore](https://github.com/cqframework/dqm-content-qicore-2025/blob/master/input/cql/QICoreCommon.cql) | [USQualityCore](https://github.com/cqframework/dqm-content-cms-2025/blob/main/input/cql/QICoreCommon.cql) |
| Status | [QICore](https://github.com/cqframework/dqm-content-qicore-2025/blob/master/input/cql/Status.cql) | [USQualityCore](https://github.com/cqframework/dqm-content-cms-2025/blob/main/input/cql/Status.cql) |
| SupplementalDataElements | [QICore](https://github.com/cqframework/dqm-content-qicore-2025/blob/master/input/cql/SupplementalDataElements.cql) | [USQualityCore](https://github.com/cqframework/dqm-content-cms-2025/blob/main/input/cql/SupplementalDataElements.cql) |
| TJCOverall | | |
| VTE | | |

These shared libraries had already been updated to use the QICore 7.0.0 (a derived model info) so these were just brought in and updated to use the USQualityCore model instead, no other changes were required to the shared libraries.

> NOTE: Hospital measures and related shared libraries (CQMCommon, PCMaternal, TJCOverall, and others) are still in progress.

This topic will use CMS125: Breast Cancer Screening as a running example

### Step 1: Update Models

To facilitate reuse across models, the `USQualityCore 0.1.0` and `USCore 6.1.0-derived` models provide model information for CQL that provides a "derived" view of FHIR profiles.

For example, in QI Core 6.0.0, a QI Core Encounter is effectively a _base_ class. However, in US Quality Core, a US Quality Core Encounter is a _derived_ class, derived from a US Core Encounter, which is in turn derived from a FHIR Encounter:

QI Core:

```
Encounter
```

US Quality Core:

```
FHIR.Encounter
    |- USCore.Encounter
        |- QICore.Encounter
```

For almost all the measure logic, this change is transparent and the only thing that needs to happen is to change the version of the model being used:

QI Core:

```cql
using QICore version '6.0.0'
```

US Quality Core:

```cql
using USQualityCore version '0.1.0-cibuild'
using USCore version '6.1.0-derived'
using FHIR version '4.0.1'
```

### Step 2: Update Libraries

Once the models have been updated, we need to update the shared library references:

| Library | QI Core version | US Quality Core version |
|----|----|----|
| AdultOutpatientEncounters | 4.19.000 | 5.1.000 |
| AdvancedIllnessandFrailty | 1.27.000 | 2.1.000 |
| AHAOverall | 4.1.000 | 5.1.000 |
| AlaraCommonFunctions | 1.10.000 | 2.1.000 |
| CQMCommon | 4.1.000 | 5.1.000 |
| CumulativeMedicationDuration | 6.0.000 | hl7.fhir.us.cql.CumulativeMedicationDuration version 2.0.0-ballot |
| FHIRHelpers | 4.4.000 | hl7.fhir.uv.cql.FHIRHelpers version 4.0.1 |
| FHIRCommon | - | hl7.fhir.uv.cql.FHIRCommon version 2.0.0 |
| Hospice | 6.18.000 | 7.1.000 |
| NHSNHelpers | 0.1.000 | 1.1.000 |
| PalliativeCare | 1.18.000 | 2.1.000 |
| QICoreCommon | 4.0.000 | (refactored into FHIRCommon, USCoreCommon, and USQualityCoreCommon) |
| Status | 1.15.000 | 2.1.000 |
| SupplementalDataElements | 5.1.000 | 6.1.000 |
| TJCOverall | 8.25.000 | 9.1.000 |
| VTE | 8.18.000 | 9.1.000 |
| USCoreCommon | - | hl7.fhir.us.cql.USCoreCommon version 2.0.0-ballot |
| USCoreElements | - | hl7.fhir.us.cql.USCoreElements version 2.0.0-ballot |
| USQualityCoreCommon | - | USQualityCoreCommon version 0.1.0-cibuild |

For example, the following snippet is the includes section of the CMS125 QI Core 6.0.0 Breast Cancer Screening measure:

```cql
include FHIRHelpers version '4.4.000' called FHIRHelpers
include SupplementalDataElements version '5.1.000' called SDE
include QICoreCommon version '4.0.000' called QICoreCommon
include AdultOutpatientEncounters version '4.19.000' called AdultOutpatientEncounters
include Hospice version '6.18.000' called Hospice
include Status version '1.15.000' called Status
include PalliativeCare version '1.18.000' called PalliativeCare
include AdvancedIllnessandFrailty version '1.27.000' called AIFrailLTCF
```

And the equivalent section for the CMS125 US Quality Core Breast Cancer Screening measure:

```cql
include hl7.fhir.uv.cql.FHIRHelpers version '4.0.1' called FHIRHelpers
include hl7.fhir.uv.cql.FHIRCommon version '2.0.0' called FHIRCommon
include hl7.fhir.us.cql.USCoreCommon version '2.0.0-ballot' called USCoreCommon
include hl7.fhir.us.cql.USCoreElements version '2.0.0-ballot' called USCoreElements

include USQualityCoreCommon version '0.1.0-cibuild' called USQualityCoreCommon
include SupplementalDataElements version '6.1.000' called SDE
include Status version '2.1.000' called Status
include AdultOutpatientEncounters version '5.1.000' called AdultOutpatientEncounters
include AdvancedIllnessandFrailty version '2.1.000' called AIFrailLTCF
include Hospice version '7.1.000' called Hospice
include PalliativeCare version '2.1.000' called PalliativeCare
```

### Step 3: Update Types

When a CQL library includes multiple models, there is a possibility of having classes with the same name in each model. This will result in an "ambiguous type" error, where the translator cannot determine which model should be used.

QI Core (flat):

```cql
define "Bilateral Mastectomy Procedure":
  ( ( [Procedure: "Bilateral Mastectomy"] ).isProcedurePerformed ( ) ) BilateralMastectomyPerformed
    where BilateralMastectomyPerformed.performed.toInterval ( ) ends on or before end of "Measurement Period"
```

US Quality Core (derived):

```cql
define "Bilateral Mastectomy Procedure":
  ( ( [USQualityCore.Procedure: "Bilateral Mastectomy"] ).isProcedurePerformed ( ) ) BilateralMastectomyPerformed
    where BilateralMastectomyPerformed.performed.toInterval ( ) ends on or before end of "Measurement Period"
```

> DISCUSS: Should we propose that when using multiple models, type names SHALL be qualified

In addition, the possibility of derived profiles means that some logic can be simplified. For example, in QICore 6.0.0, ConditionEncounterDiagnosis and ConditionProblemHealthConcerns are separate types, whereas in USQualityCore, they both ultimately derive from Condition, allowing logic that needs to deal with both to be written at the FHIR.Condition level, rather than the USQualityCore EncounterDiagnosis and ProblemHealthConcern level:

QI Core (flat):

```cql
define "Bilateral Mastectomy Diagnosis":
  ( ( [ConditionEncounterDiagnosis: "History of bilateral mastectomy"]
      union [ConditionProblemsHealthConcerns: "History of bilateral mastectomy"]
  ).verified ( ) ) BilateralMastectomyHistory
    where BilateralMastectomyHistory.prevalenceInterval ( ) starts on or before end of "Measurement Period"
```

US Quality Core (derived):

```cql
define "Bilateral Mastectomy Diagnosis":
  ( ( [FHIR.Condition: "History of bilateral mastectomy"] ).verified ( ) ) BilateralMastectomyHistory
    where BilateralMastectomyHistory.prevalenceInterval ( ) starts on or before end of "Measurement Period"
```

### Step 3: Replace extension elements:

In the derived models, extensions and slices are no longer created as first-class elements, rather they are represented as fluent functions:

QI Core:

```cql
    and Patient.sex = '248152002'
```

US Quality Core:

```cql
    and Patient.sex() = '248152002'
```

### Step 4: Consider Functions

QI Core:

```cql
define "Initial Population":
  AgeInYearsAt(date from end of "Measurement Period") in Interval[42, 74]
```

US Quality Core:

```cql
define "Initial Population":
  Patient.ageInYearsAt(date from end of "Measurement Period") in Interval[42, 74]
```

### Step 5: Consider Elements and Patterns

And finally, consider whether the patterns documented in the CQL US Common IG can be applied to the measure logic. For example, the [Mammography](https://build.fhir.org/ig/HL7/us-cql-ig/en/patterns-service.html#mammography) pattern proposes that in addition to Observation resources, Mammographies may be represented in FHIR data as DiagnosticReport resources:

QI Core:

```cql
define "Numerator":
  exists ( ( [ObservationClinicalResult: "Mammography"] ).isDiagnosticStudyPerformed ( ) ) Mammogram
    where Mammogram.effective.toInterval ( ) ends during day of Interval["October 1 Two Years Prior to the Measurement Period", end of "Measurement Period"]
```

US Quality Core:

```cql
define "Numerator":
  exists ( 
    ( ( [USQualityCore.ObservationClinicalResult: "Mammography"] ).isDiagnosticStudyPerformed ( ) ) Mammogram
      where Mammogram.effective.toInterval ( ) ends during day of Interval["October 1 Two Years Prior to the Measurement Period", end of "Measurement Period"]
  ) or exists (
    ( ( [USQualityCore.DiagnosticReportNote: "Mammography"] ).complete ( ) ) Mammogram
      where Mammogram.effective.toInterval ( ) ends during day of Interval["October 1 Two Years Prior to the Measurement Period", end of "Measurement Period"]
  )
```
