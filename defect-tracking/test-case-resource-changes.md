# Test Case Resource Changes Required for Passing eCQM Tests

This report compiles all FHIR test-case resource changes applied across `dqm-content-cms-2025` to enable test cases to evaluate correctly and match their fixture `MeasureReport` expectations.

> [!NOTE]
> None of these modifications altered clinical measure intent, CQL logic, or expected population counts. All changes resolved either extraction artifacts, Java/HAPI CQL engine scoping constraints, or data-entry errors.

---

## 1. Summary of Changes by Category

| Category | Issue IDs | Core Mechanism | Measures Affected | Test Cases Affected |
| --- | --- | --- | --- | :---: |
| **MADiE Bundle Split Collisions** | I-76 | Colliding resource IDs overwritten during file extraction; restored from source bundles | CMS72, CMS104, CMS819, CMS871, CMS1028, CMS1154 | 12 |
| **Missing Patient Scoping Fields** | I-07, I-39, I-46 | Resources missing required patient-context reference fields (`subject`, `for`) | CMS108, CMS142, CMS149, CMS816 | 21+ |
| **Wrong / Corrupted Patient References** | I-11, I-41, I-42, I-51 | Resources referencing wrong patient GUIDs or corrupted with whitespace | CMS159, CMS347, CMS645, CMS646, Repo-wide | 15+ |
| **Claim-to-Encounter Linkage** | I-74 | Missing `item.encounter` and diagnosis sequence links on institutional claims | CMS72, CMS104 | 3 |
| **Observation Profile Re-Attribution** | I-40, I-47, I-48 | Observations mis-profiled as screening assessments instead of US Core profiles | CMS69, CMS135, CMS165, Repo-wide | 20 |
| **Non-Canonical UCUM URIs** | I-43, I-50 | System URL `https://ucum.org` crashing engine `ToQuantity` conversions | CMS69, CMS347 | 3 |
| **Measurement Period & Date Alignment** | I-49, I-66 | Clinical dates authored in 2027 instead of 2026 measurement period | CMS177, CMS1264, NHSN | 56 |
| **Dangling Encounter Diagnosis Reference** | I-12 | `Encounter.reasonReference` was a malformed id with no matching resource; repointed at the delivery Condition | CMS0334 | 1 |

---

## 2. Detailed Breakdown by Category

### Category 1: MADiE Bundle-Split Collision Restorations (I-76)

* **Mechanism**: MADiE evaluated test cases using an in-memory JavaScript CQL engine. That engine treated every resource in the test transaction bundle as belonging to the patient, regardless of duplicate `id`s or `fullUrl`s. When cqf-tooling's `-BundleToResources` split the bundles into individual `<ResourceType>-<id>.json` files, resources with duplicate IDs silently overwrote each other. Only the last written resource survived on disk, causing essential clinical evidence to disappear.
* **Remediation**: Re-extracted the colliding resources from the source MADiE export bundles, assigned unique identifiers, and restored them to the test folders while updating the `MeasureReport.evaluatedResource` list.

#### Affected Measures and Resources:
1. **CMS819FHIRHHORAE** (Commits `b6971267a`, `cf1163f31`):
   * Case `73b0c1fe-874b-4982-8cb2-3c30520441de`:
     * Added [`MedicationAdministration-18cc43f1-4c96-4d17-9cce-eb25ed09b465.json`](../input/tests/measure/CMS819FHIRHHORAE/73b0c1fe-874b-4982-8cb2-3c30520441de/MedicationAdministration-18cc43f1-4c96-4d17-9cce-eb25ed09b465.json)
     * Added [`MedicationAdministration-a3ebcb6c-50f4-4b1b-9705-4aeeb3cc0535.json`](../input/tests/measure/CMS819FHIRHHORAE/73b0c1fe-874b-4982-8cb2-3c30520441de/MedicationAdministration-a3ebcb6c-50f4-4b1b-9705-4aeeb3cc0535.json)
     * Updated [`MeasureReport-15d9e04f-4116-4856-b61a-f7c7b38e3325.json`](../input/tests/measure/CMS819FHIRHHORAE/73b0c1fe-874b-4982-8cb2-3c30520441de/MeasureReport-15d9e04f-4116-4856-b61a-f7c7b38e3325.json)
   * Case `31b40acc-ca5f-4d1d-bd83-4b1a14eb822e`:
     * Added [`Encounter-776faeb3-f3e6-496b-aacf-af36ef6b71ed.json`](../input/tests/measure/CMS819FHIRHHORAE/31b40acc-ca5f-4d1d-bd83-4b1a14eb822e/Encounter-776faeb3-f3e6-496b-aacf-af36ef6b71ed.json)
     * Updated [`MeasureReport-c93e2b69-18fd-425e-8c71-b52eb967eda0.json`](../input/tests/measure/CMS819FHIRHHORAE/31b40acc-ca5f-4d1d-bd83-4b1a14eb822e/MeasureReport-c93e2b69-18fd-425e-8c71-b52eb967eda0.json)
2. **CMS871FHIRHHHyper** (Commit `10079d3b9`):
   * Case `113a6e72-7049-4a7f-90cf-5ec3435b0dee`:
     * Updated [`MeasureReport-0ac4f7d5-15a2-4c2f-b38d-c2d2ff7775e2.json`](../input/tests/measure/CMS871FHIRHHHyper/113a6e72-7049-4a7f-90cf-5ec3435b0dee/MeasureReport-0ac4f7d5-15a2-4c2f-b38d-c2d2ff7775e2.json) to reference the patient instead of `Patient/null`.
3. **CMS1028FHIRPCSevereOBComps** (Commit `14355c41a`):
   * Case `763d86f9-d93f-4873-8b64-8439566b242e`:
     * Added [`Claim-2a83353c-a7b0-469e-a6a7-51439e2c6d05.json`](../input/tests/measure/CMS1028FHIRPCSevereOBComps/763d86f9-d93f-4873-8b64-8439566b242e/Claim-2a83353c-a7b0-469e-a6a7-51439e2c6d05.json)
     * Updated [`MeasureReport-7ca90ad8-935e-4d56-80d9-5470c8a98481.json`](../input/tests/measure/CMS1028FHIRPCSevereOBComps/763d86f9-d93f-4873-8b64-8439566b242e/MeasureReport-7ca90ad8-935e-4d56-80d9-5470c8a98481.json)
4. **CMS1154ScreeningPrediabetesFHIR** (Commit `14355c41a`):
   * Case `bc9c82ca-72b5-41c4-a9a3-7e3860a9ac2d`:
     * Added [`Condition-18617b19-1ea4-46cc-a7e2-91b6d531152a.json`](../input/tests/measure/CMS1154ScreeningPrediabetesFHIR/bc9c82ca-72b5-41c4-a9a3-7e3860a9ac2d/Condition-18617b19-1ea4-46cc-a7e2-91b6d531152a.json)
     * Updated [`MeasureReport-466dec57-6ceb-4f37-8daa-40f26f14a191.json`](../input/tests/measure/CMS1154ScreeningPrediabetesFHIR/bc9c82ca-72b5-41c4-a9a3-7e3860a9ac2d/MeasureReport-466dec57-6ceb-4f37-8daa-40f26f14a191.json)
5. **CMS72FHIRSTKAntithromboticDay2** (Commit `0ff0843eb`):
   * Case `5a329008-fcc1-4168-ab9c-89cb5dd6ff32`: Restored 1 stroke Claim (`Claim-8b852968-1ff0-4578-8466-66e6f11d3d2b.json`) and updated MeasureReport.
   * Case `cb7c95fc-6d6b-4e07-81e8-a79385142b94`: Restored 2 stroke Claims (`Claim-1cb6ea3f-*.json`, `Claim-81f827a1-*.json`) and updated MeasureReport.
   * Case `febd4b3e-99bc-4c55-bba9-3b2136c2160b`: Restored 3 stroke Claims (`Claim-29a3a936-*.json`, `Claim-4467c699-*.json`, `Claim-53697eb1-*.json`) and updated MeasureReport.
6. **CMS104FHIRSTKDCAntithrombotic** (Commit `0ff0843eb`):
   * Restored 8 stroke Claim resources across 4 multi-encounter test cases:
     * `348471db-5aaa-4bf3-a280-75222f20d599` (2 Claims: `Claim-a86c4aaf-*.json`, `Claim-f0b94078-*.json`)
     * `451b6853-3734-4c1c-b37e-5904629e0350` (2 Claims: `Claim-09dbe4fd-*.json`, `Claim-cddeebd4-*.json`)
     * `a2b8327c-eaf4-4552-863e-851426e729d4` (2 Claims: `Claim-759868e8-*.json`, `Claim-b93086eb-*.json`)
     * `c15bee15-84c1-494a-ac82-2159b06da175` (2 Claims: `Claim-4813ea0f-*.json`, `Claim-c187e025-*.json`)

---

### Category 2: Missing Patient Scoping Elements (I-07, I-39, I-46)

* **Mechanism**: In Java HAPI CQL, execution is scoped to `context Patient`. The engine resolves patient context by strictly checking specific path elements declared in the modelinfo:
  * `Encounter.subject`
  * `Communication.subject`
  * `Task.for`
  * `MedicationAdministration.subject`
  * `Observation.subject`
  When these elements were completely absent, the engine silently filtered the resources out of all retrieves.
* **Remediation**: Injected `{"reference": "Patient/<folder-guid>"}` into the required fields using [`validate_test_fixtures.py --fix-required-fields`](../scripts/validate_test_fixtures.py).

#### Affected Measures and Resources:
1. **CMS816FHIRHHHypo** (I-07, Commit `90d0ad955`):
   * 17 `Encounter` resources across 12 test cases were missing `subject`. Injected `subject: {"reference": "Patient/<guid>"}`.
2. **CMS142FHIRCommWithDrManagingDiab** (I-39, Commit `08f9bda3d`):
   * 10 `Communication` resources across cases `03b74242`, `05f1e2a6`, `28492651`, `2dd72971`, `41ae0086`, `7628a506`, `9f28df13`, `af49880f`, `b61b7fcf`, and `d8e34ebc` were missing `subject`. Injected patient reference.
3. **CMS149FHIRDementiaCognitiveAssess** (I-39, Commit `08f9bda3d`):
   * Case `9e1ffb55`: `Observation-459eed2c-d5c3-4108-ba45-f32af90efb8a.json` was missing `subject`. Injected patient reference.
4. **CMS108FHIRVTEProphylaxis** (I-46):
   * Injected `Task.for` across cases (`182103c1`, `2eff6dbd`, `3c854f27`, etc.).

---

### Category 3: Wrong / Corrupted Patient References (I-11, I-41, I-42, I-51)

* **Mechanism**: Resources contained references pointing to different patient IDs (copy-paste artifacts from other test cases or template defaults like `Patient/null`) or syntax corruption.
* **Remediation**: Repointed patient references to the exact case patient GUID.

#### Affected Measures and Resources:
1. **CMS159FHIRDepRemissionat12Months** (I-11, Commit `a63ba94ae`):
   * Cases `2b4c52e3`, `491f554e`, and `96b6579c`: Hospice `ServiceRequest.subject` pointed to foreign patient GUIDs; repointed to case patient GUIDs.
2. **CMS645FHIRBoneDensityPCADTherapy** (I-11, Commit `a63ba94ae`):
   * Case `4d648e0d`: `Observation-6459f9f6-0de7-4c0d-8db5-b76d36c27dd2.json` `subject.reference` pointed to wrong patient; corrected.
3. **CMS646FHIRIntravesicalBCGTherapy** (I-11, Commit `a63ba94ae`):
   * Case `6e9a1974`: `MedicationAdministration-404ce24c-e068-41ea-b85a-79c0c906a2fc.json` `subject.reference` pointed to wrong patient; corrected.
4. **CMS347FHIRStatinPreventionTxCVD** (I-51):
   * Case `1d3021bb`: Encounter and FACIT-Pal Observation (`71007-9`) contained stray spaces splitting the patient GUID (`"Patient/1d3021bb-b593-4efc-af5b-3  20243bbe9b7"`). Stripped spaces via `fix_cms347_fixture_data.py`.
5. **Repo-wide Core Sweep** (I-41, I-42, I-46):
   * Automated rewrite applied via [`validate_test_fixtures.py --fix --apply`](../scripts/validate_test_fixtures.py) ensuring `Claim.patient`, `Coverage.beneficiary`, `AllergyIntolerance.patient`, and `Condition.subject` match the case patient.

---

### Category 4: Claim-to-Encounter Linkage (I-74)

* **Mechanism**: Stroke measures require institutional inpatient claims (`Claim`) to establish the principal diagnosis for hospital admission. The measure logic matches claims by evaluating `item.encounter` and `item.diagnosisSequence`. If the claim does not reference the inpatient encounter ID or sequence, the diagnosis is not attributed to the encounter.
* **Remediation**: Linked the Claim item to the case's inpatient encounter and set diagnosis sequence (Commit `637fffd5e`).

#### Affected Measures and Resources:
1. **CMS72FHIRSTKAntithromboticDay2**:
   * Case `e126cdec-dbc8-4ee8-964f-e88e46c04f88`:
     * File: `Claim-5ca62962b8484628b8de1ec5.json`
     * Change: Added `encounter = [{"reference": "Encounter/09e99a80-1a73-455b-bf5a-c5615d6c8e03"}]` and `diagnosisSequence = [1]` to `item[0]`.
2. **CMS104FHIRSTKDCAntithrombotic**:
   * Case `0b1aa8ee-e8bf-49f5-b968-48c5a9702843`:
     * File: `Claim-5ca62962b8484628b8de1ec5.json`
     * Change: Linked `item[0]` to the case's inpatient encounter.
   * Case `e84c89f7-3c9e-4ee9-b71a-5025aadb5990`:
     * File: `Claim-5ca62962b8484628b8de1ec5.json`
     * Change: Linked `item[0]` to the case's inpatient encounter.

---

### Category 5: Observation Profile Re-Attribution (I-47, I-48)

* **Mechanism**: In measures where CQL retrieves via specific US Core profiles (`[USCore.BMIProfile]`, `[USCore.BloodPressureProfile]`, `[USCore.ObservationPregnancyStatusProfile]`), the Java engine strictly compares `meta.profile`. During the initial QI-Core to US Quality Core refactoring, fixtures had been re-attributed to `us-quality-core-observation-screening-assessment`. Because the profile URIs did not match, the retrieves evaluated to empty lists.
* **Remediation**: Re-attributed the `meta.profile` URIs of the qualifying observations using `scripts/reattribute_uscore_profiles.py`.

#### Affected Measures and Resources:
1. **CMS69FHIRPCSBMIScreenAndFollowUp** (I-47):
   * 16 Numerator cases (`050201c2`, `1102009b`, `1e23fb8f`, `27849d59`, `42e6b4d6`, `461fdfab`, `463dd868`, `7902e3dc`, `8835a50b`, `8e38b797`, `9d92be1d`, `c3caf126`, `c84bf29f`, `d4d064be`, `e0821eec`, `f5ae6269`):
     * Target: BMI Observation (LOINC `39156-5`)
     * Replaced: `http://fhir.org/guides/astp/us-quality-core/StructureDefinition/us-quality-core-observation-screening-assessment`
     * With: `http://hl7.org/fhir/us/core/StructureDefinition/us-core-bmi`
   * 1 Denominator Exclusion case (`e25fc2f1`):
     * Target: Pregnancy Status Observation (LOINC `82810-3`)
     * Replaced with: `http://hl7.org/fhir/us/core/StructureDefinition/us-core-observation-pregnancystatus`
2. **CMS165FHIRControllingHighBP** (I-48):
   * Cases `6f37e357` and `f2d1fd7e`:
     * Target: Blood Pressure panel Observation (LOINC `85354-9`)
     * Replaced with: `http://hl7.org/fhir/us/core/StructureDefinition/us-core-blood-pressure`
3. **CMS135FHIRACEIorARBorARNIforHF** (I-48):
   * Case `6a86918d`:
     * Target: Pregnancy Status Observation (LOINC `82810-3`)
     * Replaced with: `http://hl7.org/fhir/us/core/StructureDefinition/us-core-observation-pregnancystatus`

---

### Category 6: Non-Canonical UCUM URIs (I-50)

* **Mechanism**: FHIR `Quantity.system` must use the canonical UCUM URL (`http://unitsofmeasure.org`). Several fixture resources used `https://ucum.org`. The HAPI library helper `FHIRHelpers.ToQuantity` threw an invalid quantity exception on `https://ucum.org`, terminating evaluation and resulting in `MISSING` results for all populations.
* **Remediation**: Substituted `https://ucum.org` with `http://unitsofmeasure.org` using `scripts/fix_cms347_fixture_data.py`.

#### Affected Measures and Resources:
1. **CMS347FHIRStatinPreventionTxCVD**:
   * Case `6da189af-32d8-4a57-810a-3c5ad41a8767`:
     * Target: LDL Cholesterol Observation (LOINC `13457-7`) `valueQuantity.system`
     * Change: Corrected to `http://unitsofmeasure.org` (recovered 20 test cells across 4 groups from `MISSING`).
2. **CMS69FHIRPCSBMIScreenAndFollowUp**:
   * Cases `7b34e64e` and `45b1ce40`:
     * Target: BMI Observation (LOINC `39156-5`) `valueQuantity.system`
     * Change: Corrected to `http://unitsofmeasure.org`.

---

### Category 7: Date Shifts & Measurement Period Realignment (I-49, I-66)

* **Mechanism**: Test cases were authored with clinical dates aligned to a 2027 measurement period instead of the standard 2026 measurement period (`@2026`), or encounter dates disagreed with MADiE timing.

#### Affected Measures and Resources:
1. **CMS1264FHIRECATREHQR** (I-49):
   * Applied repo-wide date shift via `scripts/rekey_cms1264_fixtures_to_2026.py`:
   * Shifted all date tokens (`YYYY-MM-DD`) by exactly -1 year (2027 -> 2026) across all 54 test cases, covering `Encounter`, `Condition`, `Claim`, `ServiceRequest`, `Coverage`, and `MeasureReport.period`.
2. **CMS177FHIRChildMajorDepressionScreen** (I-66, Commit `45a7f2d49`):
   * Case `85e6225c`:
     * Target: `Encounter-85e6225c-*.json`
     * Change: Shifted encounter period start/end from inside the measurement period (`2026-02-11`) to before it (`2025-11-15`), and added missing `meta.profile`.
3. **NHSNAcuteCareHospitalMonthlyInitialPopulation1**:
   * Updated fixture resource years to 2026.

---

### Category 8: Dangling Encounter Diagnosis Reference (I-12)

* **Mechanism**: The case's Encounter named its delivery diagnosis with `reasonReference` `delivery-of-singleton-0997`. That isn't a valid `Type/id` reference, and no resource in the case carries that id (the Condition was re-identified to a GUID on import). `CQMCommon.encounterDiagnosis()` therefore found nothing.
* **Remediation**: Repointed the reference at the delivery Condition already present in the case.

#### Affected Measures and Resources:
1. **CMS0334FHIRPCCesareanBirth** (Commit `2ba4c4ded`):
   * Case `c58acff5-248b-49c9-b18d-69e4a84a08d9`:
     * Updated [`Encounter-9d6ea959-0e00-4cd6-bf60-a90e1d6e90c1.json`](../input/tests/measure/CMS0334FHIRPCCesareanBirth/c58acff5-248b-49c9-b18d-69e4a84a08d9/Encounter-9d6ea959-0e00-4cd6-bf60-a90e1d6e90c1.json): `reasonReference[0].reference` `delivery-of-singleton-0997` → `Condition/8f7d2289-fe66-4bde-8ed8-3223de1da063`.

---

## 3. Summary of Automation Tools Used

The following utility scripts in `scripts/` automate and guard these fixture repairs:

1. [`dqm-content-cms-2025/scripts/validate_test_fixtures.py`](../scripts/validate_test_fixtures.py):
   * Validates and repairs patient-identity scoping fields (`subject`, `patient`, `beneficiary`, `for`).
2. `scripts/reattribute_uscore_profiles.py`:
   * Idempotently re-attributes Observation `meta.profile` entries from USQC screening assessment to US Core profiles.
3. `scripts/fix_cms347_fixture_data.py`:
   * Corrects invalid `https://ucum.org` quantity URIs and strips corrupting whitespace in GUID references.
4. `scripts/rekey_cms1264_fixtures_to_2026.py`:
   * Re-keys out-of-cycle fixture dates by decrementing years uniformly while preserving clinical intervals.
