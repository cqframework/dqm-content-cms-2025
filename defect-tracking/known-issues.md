# Known Issues

Every issue the test suite has surfaced so far, with its root-cause class and
current status. **This file is maintained by hand — edit it freely.** Nothing
generates it and no script reads it, so a bad edit cannot break the reporting.

If you fix something, change its status and note what you did in
`change-log.md`. If you find something new, add a row with the next free `I-` id.

Issue ids also appear in CQL comments next to the affected logic, e.g.
`// [I-28] base FHIR.Condition retrieve (defect-tracking/known-issues.md)`.

Three issues have a confirmed root cause and a verified candidate fix that was
deliberately **not** applied, because choosing the fix is a modelling decision
rather than a bug fix — see `CONNECTATHON-BREADCRUMBS.md`.

## Root-cause classes

| Class | Means |
|---|---|
| `engine` | the CQL runtime engine misbehaves at evaluation time |
| `translator` | `cql-to-elm` misbehaves at compile time |
| `content` | measure authoring gap — no CQL written, wrong valueset |
| `migration` | a bug introduced converting QI-Core → US Quality Core |
| `fixture` | bad or incomplete test data |
| `vendored` | a bug in an upstream-authored CQL library vendored here |
| `harness` | a limitation of the comparison harness, not of the content |

## Issues (61)

| ID | Issue | Class | Status | Measures |
|---|---|---|---|---|
| I-02 | CMS145 / CMS149 | `content` | Fixed | CMS145, CMS149 |
| I-03 | CMS157 | `content` | Fixed | CMS157 |
| I-04 | CMS986 malnutrition Measure-Observation component rows | `content` | Open — confirmed | CMS986 |
| I-05 | CMS1017 fall-prevention HHFI Denominator/Numerator/Measure-Observation rows | `content` | Open — confirmed | CMS1017 |
| I-06 | CMS157 Pain Intensity Quantified | `content` | Fixed | CMS157 |
| I-07 | CMS816 HH Hypoglycemia fixture MR/Denominator authoring mismatch | `content` | Open — confirmed | CMS816 |
| I-08 | CMS871 HH Hyperglycemia fixture MR/Denominator authoring mismatch | `content` | Open — confirmed | CMS871 |
| I-09 | ~~CMS142 Diabetes Communication Hand-Off fixture MR authoring mismatch (shared %)~~ RETIRED 2026-09-10 | `content` | Retired | — |
| I-10 | CMS819 HH Opioid-Related Adverse Events fixture MR authoring mismatch | `content` | Open — confirmed | CMS819 |
| I-11 | CMS159 Depression Remission fixture MR authoring mismatch | `content` | Open — confirmed | CMS159 |
| I-12 | CMS0334 Cesarean Birth fixture MR authoring mismatch | `content` | Open — confirmed | CMS0334 |
| I-13 | CMS1218 HH Respiratory Failure fixture MR authoring mismatch | `content` | Open — confirmed | CMS1218 |
| I-14 | CMSFHIR844 Hybrid Hospital-Wide Mortality fixture MR Initial Population authoring mismatch (shared %) - both… | `content` | Open — confirmed | CMSFHIR844 |
| I-15 | CMS72 / CMS104 / CMS646 / CMS71 residual fixture MR authoring gaps where both engines agree (Denominator-… | `content` | Open — confirmed | CMS1028, CMS104, CMS145 +5 more |
| I-16 | `Min()` over DateTime throws | `engine` | Worked around | CMS1173, CMS871 |
| I-17 | Raw `FHIR.dateTime` / choice-typed `X.effective` in temporal operators fails | `engine` | Worked around | CMS1173 |
| I-18 | Fluent overload ambiguity (sibling profiles, same Java class) | `engine` | Worked around | CMS104, CMS108, CMS144 +3 more |
| I-19 | Choice-type self-reference circular dispatch | `engine` | Worked around | CMS133, CMS142, CMS143 +5 more |
| I-20 | Sibling overloads ambiguous at runtime (same Java class) | `engine` | Worked around | CMS133, CMS142, CMS143 +6 more |
| I-21 | `as` cannot widen Choice to ancestor type | `engine` | Worked around | — |
| I-22 | `convert Duration to days` returns null | `engine` | Worked around | CMS128, CMS156 |
| I-23 | `ConvertQuantity` rejects calendar-word units from `ToQuantity` | `engine` | Worked around | CMS156 |
| I-24 | Quantity division across dimensions rounds to zero | `engine` | Worked around | CMS156 |
| I-25 | `singleton from empty list` throws instead of returning null | `engine` | Worked around | CMS156 |
| I-26 | `Unable to extract codes from fhirType Reference` | `engine` | Open — confirmed | CMS135, CMS165 |
| I-27 | Union branch evaluates empty despite correct data | `engine` | Open — confirmed | CMS104, CMS108, CMS190 |
| I-28 | Union of `ConditionProblemsHealthConcerns` ∪ `ConditionEncounterDiagnosis` → `Choice<...>` fed to… | `engine` | Worked around | CMS1154, CMS1157, CMS117 +29 more |
| I-29 | `PCMaternal.cql` cast type change (`.value as DateTime` → `.value as FHIR.dateTime`) | `engine` | Open — suspected | CMS0334, CMS1028 |
| I-30 | ~~Union of `ConditionProblemsHealthConcerns` ∪ `ConditionEncounterDiagnosis` → `Choice<...>` fed to… | `engine` | Retired | — |
| I-31 | `overlaps` on a half-open null-high interval (`[start, null)`) evaluates false | `engine` | Open — confirmed | CMS1154, CMS347 |
| I-32 | `us-quality-core-*` profile retrieves return empty (broader than ObservationScreeningAssessment | `engine` | Open — confirmed | CMS108, CMS131, CMS190, CMS56 |
| I-33 | Raw `FHIR.dateTime` returned from a define feeding `sort` and a mixed-type `Interval` endpoint throws… | `engine` | Worked around | CMS156 |
| I-34 | `doNotPerform` negative-indication `MedicationRequest`s counted as positive orders by CMS347's… | `engine` | Open — confirmed | CMS347 |
| I-35 | `(never assigned)` | `engine` | Retired | — |
| I-36 | `us-quality-core-*` profile retrieves return empty for screening-assessment plus service/medication/procedure… | `engine` | Open — confirmed | CMS135, CMS144, CMS145 +6 more |
| I-37 | `recorded(...)` operator ambiguous call in `USQualityCoreCommon` library throws (CMS68 test-case `f2e2e1c0`… | `engine` | Open — confirmed | CMS68 |
| I-38 | QI-Core engine-side regressions surfaced by 2026-09-05 fresh re-run | `engine` | Open — confirmed | CMS1028, CMS108, CMS129 +10 more |
| I-39 | `[CommunicationNotDone: category in ...]` retrieve returns no resources when the category-bearing… | `engine` | Open — suspected | CMS142 |
| I-40 | Stale `onc` → `astp` profile namespace on fixtures | `fixture` | Fixed | CMS104, CMS128, CMS129 +9 more |
| I-41 | Wrong-patient `subject.reference` in fixtures | `fixture` | Fixed | CMS108, CMS347, CMS72, NHSNGlycemicControl |
| I-42 | Wrong-patient `Claim.patient` / `Coverage.beneficiary` / `AllergyIntolerance.patient` | `fixture` | Fixed | CMS1028, CMS104, CMS108 +4 more |
| I-43 | Invalid UCUM `system` URI on Observation fixtures | `fixture` | Fixed | CMS347, CMS69 |
| I-44 | Missing vocabulary source file (CMS871) | `fixture` | Fixed | CMS871 |
| I-45 | Sparse `MedicationRequest` dosage fixtures trip `singleton from empty list` | `fixture` | Worked around | CMS156 |
| I-46 | Automated CORE-field patient-reference fix (validate_test_fixtures.py) | `fixture` | Fixed | CMS1028, CMS104, CMS108 +7 more |
| I-47 | CMS69 BMI & pregnancy-status Observations mis-attributed to `us-quality-core-observation-screening-… | `fixture` | Fixed | CMS69 |
| I-48 | CMS165 & CMS135 blood-pressure / pregnancy Observations mis-attributed to `us-quality-core-observation-… | `fixture` | Fixed | CMS135, CMS165 |
| I-49 | CMS1264 test-case fixtures keyed to the 2027 measurement period instead of 2026 | `fixture` | Fixed | CMS1264 |
| I-50 | CMS347 `6da189af` LDL Observation carries non-canonical UCUM quantity system `https://ucum.org` | `fixture` | Fixed | CMS347 |
| I-51 | CMS347 `1d3021bb` Encounter `subject.reference` whitespace-corrupted (GUID split) | `fixture` | Fixed | CMS347 |
| I-52 | `doNotPerform` not excluded from MedicationRequest/ServiceRequest retrieves | `migration` | Worked around | CMS104, CMS135, CMS144 +4 more |
| I-53 | Choice-typed `.effective`/`.performed` compared without `.toInterval()` | `migration` | Fixed | CMS646, CMS72 |
| I-54 | `.onset.toInterval()` used instead of `.prevalenceInterval()` for chronic conditions | `migration` | Fixed | CMS128, CMS129, CMS133 +10 more |
| I-55 | Field swapped `.recorded` → `.effective`/`.performed` to dodge a translator ambiguity | `migration` | Worked around | CMS108, CMS190, CMS68, CMS996 |
| I-56 | `AHAOverall.cql` Choice narrowing dropped `ConditionProblemsHealthConcerns` support (CMS144) | `migration` | Open — confirmed | CMS144 |
| I-57 | Vendored `CMD.cql` `convert…to days` null / calendar-unit bug (medication dispense side) | `vendored` | Worked around | CMS128 |
| I-58 | Vendored `CumulativeMedicationDuration` 6.0.000 model adaptation (CMS156) | `vendored` | Worked around | CMS156 |
| I-59 | CMS22: `ServiceNotRequested` negation defines checked base FHIR `.reasonCode` instead of the… | `migration` | Fixed | CMS22 |
| I-60 | CMS2: depression-screening negation logic (`ObservationCancelled`) commented out entirely | `content` | Open — confirmed | CMS2 |
| I-61 | Translator's ChoiceType compatibility check bypasses a registered FHIRHelpers conversion when a union… | `translator` | Worked around | CMS108, CMS190 |
| I-62 | Comparison harness cannot compute CQFM measure-observation populations (per-member function invocation +… | `harness` | Worked around | CMS1017, CMS871, CMS986 |
