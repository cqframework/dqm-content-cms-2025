# Known Issues

Every issue the test suite has surfaced so far, with its root-cause class and
current status. **This file is maintained by hand — edit it freely.** Nothing
generates it and no script reads it, so a bad edit cannot break the reporting.

The file is in two parts. **Open issues** is the actionable list. **Resolved —
reference patterns** keeps the closed issues around for a different reason: a
resolved issue is a catalogued *failure fingerprint*, and several of the open
ones were first misdiagnosed as something already sitting in that list.

If you fix something, move its row into **Resolved — reference patterns** under
the matching family, reduce it to a one-line fingerprint plus the fix, and cite
the `I-` id in your `change-log.md` entry. If you find something new, add a row
to **Open issues** with the next free `I-` id.

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
| `baseline` | the QI-Core baseline `qicore-2025-actual-results.csv` disagrees with the fixture MeasureReports while the CMS engine matches |

## Statuses

| Status | Means |
|---|---|
| `Open — confirmed` | reproduced, root cause understood |
| `Open — suspected` | reproduced, root cause still a hypothesis |
| `Open — needs re-confirmation` | previously confirmed, but the evidence no longer matches any failing cell |
| `Worked around` | mitigated in CQL; the underlying defect is still live |
| `Fix applied — unverified` | fix is in the repo but no engine re-run has confirmed the cells recover |
| `Fixed` | fix applied **and** verified against engine output |
| `Retired` | withdrawn, superseded, or never assigned |

Do not promote anything to `Fixed` without confirming the fix is actually
present in the repo and that the engine agrees — I-44 sat at `Fixed` for weeks
while the valueset it needed had never been committed.

## Open issues (43)

| ID | Issue | Class | Status | Measures |
|---|---|---|---|---|
| I-01 | QI-Core baseline disagrees with fixture MeasureReports on 670 cases / 26 measures; CMS engine matches, baseline is fresh | `baseline` | Open — confirmed | 26 measures |
| I-04 | CMS986 malnutrition Measure-Observation component rows | `content` | Open — confirmed | CMS986 |
| I-05 | CMS1017 fall-prevention HHFI Denominator/Numerator/Measure-Observation rows | `content` | Open — confirmed | CMS1017 |
| I-07 | CMS816 HH Hypoglycemia fixture MR/Denominator authoring mismatch | `content` | Open — confirmed | CMS816 |
| I-08 | CMS871 HH Hyperglycemia fixture MR/Denominator authoring mismatch. **Needs re-confirmation (2026-09-18):** after the I-44 fix CMS871 has 10 failing cells, all `MISSING` and all attributable to I-63; no currently-failing cell matches this authoring-mismatch symptom | `content` | Open — needs re-confirmation | CMS871 |
| I-10 | CMS819 HH Opioid-Related Adverse Events fixture MR authoring mismatch | `content` | Open — confirmed | CMS819 |
| I-11 | CMS159 Depression Remission fixture MR authoring mismatch | `content` | Open — confirmed | CMS159 |
| I-12 | CMS0334 Cesarean Birth fixture MR authoring mismatch | `content` | Open — confirmed | CMS0334 |
| I-13 | CMS1218 HH Respiratory Failure fixture MR authoring mismatch | `content` | Open — confirmed | CMS1218 |
| I-14 | CMSFHIR844 fixture MR hand-authors Initial Population; both engines compute 0/1 against an expected 1/2 | `content` | Open — confirmed | CMSFHIR844 |
| I-15 | CMS72 / CMS104 / CMS646 / CMS71 fixture MRs author Denominator-Exception / Denominator / Numerator / IP counts that neither engine can compute from the resources present | `content` | Open — confirmed | CMS1028, CMS104, CMS145 +5 more |
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
| I-28 | Sibling-profile Condition union fed to `prevalenceInterval(Choice<ConditionEncounterDiagnosis, ConditionProblemsHealthConcerns>)` will not resolve — `FHIRCommon.cql` declares only the base `FHIR.Condition` overload and the translator cannot widen a Choice | `engine` | Worked around | CMS1154, CMS1157, CMS117 +29 more |
| I-29 | `PCMaternal.cql` cast type change (`.value as DateTime` → `.value as FHIR.dateTime`) | `engine` | Open — suspected | CMS0334, CMS1028 |
| I-31 | `overlaps` on a half-open null-high interval (`[start, null)`) evaluates false | `engine` | Open — confirmed | CMS1154, CMS347 |
| I-32 | `us-quality-core-*` profile retrieves return empty (broader than ObservationScreeningAssessment alone) | `engine` | Open — confirmed | CMS108, CMS131, CMS190, CMS56 |
| I-33 | Raw `FHIR.dateTime` returned from a define breaks `sort` and a mixed-type `Interval` endpoint — `"Values FHIR.dateTime and FHIR.dateTime are not comparable"` (CMS156 Index Prescription Start Date; the post-I-28 reappearance of the I-16/I-17 family) | `engine` | Worked around | CMS156 |
| I-34 | `doNotPerform` negative-indication `MedicationRequest`s counted as positive orders by CMS347's statin logic | `engine` | Open — confirmed | CMS347 |
| I-36 | `us-quality-core-*` profile retrieves return empty across the screening-assessment, observation, medication and procedure profile families (I-32 extended; corroborated on 7 measures: CMS135 ACEI/ARB HF, CMS144 HFrEF beta-blocker, CMS771 urinary-symptom, CMS177 MDD-screening, CMS645 CAD-bone-density, CMS71 anticoagulation-flutter) | `engine` | Open — confirmed | CMS135, CMS144, CMS145 +6 more |
| I-37 | Ambiguous `recorded(...)` overload in `USQualityCoreCommon` throws, aborting CMS68 test case `f2e2e1c0` across all 4 populations (Missing Results) | `engine` | Open — confirmed | CMS68 |
| I-38 | QI-Core engine-side regressions surfaced by 2026-09-05 fresh re-run | `engine` | Open — confirmed | CMS1028, CMS108, CMS129 +10 more |
| I-39 | `[CommunicationNotDone: category in ...]` retrieve returns no resources when the category-bearing resource has `subject: null` | `engine` | Open — suspected | CMS142 |
| I-45 | Sparse `MedicationRequest` dosage fixtures trip `singleton from empty list` | `fixture` | Worked around | CMS156 |
| I-52 | `doNotPerform` not excluded from MedicationRequest/ServiceRequest retrieves | `migration` | Worked around | CMS104, CMS135, CMS144 +4 more |
| I-55 | Field swapped `.recorded` → `.effective`/`.performed` to dodge a translator ambiguity | `migration` | Worked around | CMS108, CMS190, CMS68, CMS996 |
| I-56 | `AHAOverall.cql` Choice narrowing dropped `ConditionProblemsHealthConcerns` support (CMS144) | `migration` | Open — confirmed | CMS144 |
| I-57 | Vendored `CMD.cql` `convert…to days` null / calendar-unit bug (medication dispense side) | `vendored` | Worked around | CMS128 |
| I-58 | Vendored `CumulativeMedicationDuration` 6.0.000 model adaptation (CMS156) | `vendored` | Worked around | CMS156 |
| I-60 | CMS2: depression-screening negation logic (`ObservationCancelled`) commented out entirely | `content` | Open — confirmed | CMS2 |
| I-61 | Translator's ChoiceType compatibility check bypasses a registered FHIRHelpers conversion when a union produces divergent tuple-element types, leaving raw `FHIR.instant` `INRLabTest.issued` unconverted (CMS108/CMS190 INR Low Risk Indicator); corroborated on CMS986's bare-value `union` of raw `authoredOn` with an already-converted `System.DateTime` branch (Hospice/Dietitian Referral defines) | `translator` | Worked around | CMS108, CMS190, CMS986 |
| I-62 | Comparison harness cannot invoke per-member `cqfm-aggregateMethod` measure-observations for ratio / continuous-variable measures, so those cells are excluded from automated scoring | `harness` | Worked around | CMS1017, CMS871, CMS986 |
| I-63 | `Invalid Interval - the ending boundary (0) must be greater than or equal to the starting boundary (1).` aborts CMS871 cases `98533ccd` and `fd579f44`, 10 cells (both, all 5 populations MISSING). An integer `[1, 0]` interval, suggesting a range built over an empty list; root cause not yet traced and the error appears nowhere else in `input/tests/results/`. `fd579f44` only surfaced once I-44 was fixed — the ValueSet error had been masking it | `engine` | Open — confirmed | CMS871 |

## Resolved — reference patterns

Kept for pattern-matching, not for tracking: if an undiagnosed failure looks
like one of these, start there. Each bullet names the concrete field, URI or
operator involved, because that — not the measure name — is what transfers.
The fix itself is recorded in `change-log.md`.

### Profile URI mismatch empties a retrieve

- **I-40** `fixture` — 2,679 fixtures kept `meta.profile` and extension URLs on
  `.../guides/onc/us-quality-core/...` after the IG renamed the namespace to
  `astp`, so profile-typed retrieves matched nothing. Fixed by a bulk
  `onc` → `astp` replacement.
- **I-47** `fixture` — 16 CMS69 BMI Observations (LOINC `39156-5`) and one
  pregnancy-status Observation (`82810-3` / SCT `77386006`) were profiled
  `us-quality-core-observation-screening-assessment`, so `[USCore.BMIProfile]`
  and `[USCore.ObservationPregnancyStatusProfile]` retrieved nothing. Fixed by
  re-attributing `meta.profile` to `us-core-bmi` /
  `us-core-observation-pregnancystatus`.
  - **Latent, not yet fixed:** 4 CMS69 Observations still carry a malformed
    `us-quality-core-observationcancelled` profile (missing hyphen).
- **I-48** `fixture` — same shape on CMS165/CMS135: blood-pressure panels
  (LOINC `85354-9` / `8480-6` / `8462-4`) and an `82810-3` pregnancy
  Observation carried `...observation-screening-assessment`, emptying
  `[USCore.BloodPressureProfile]`. Fixed by re-attributing to
  `us-core-blood-pressure` / `us-core-observation-pregnancystatus`.

### Broken or typo'd patient reference

A reference that does not resolve produces a silent zero, never an error — the
resource simply never attaches to the patient.

- **I-41** `fixture` — 40 `Condition` / `Encounter` / `Observation` /
  `MedicationRequest` / `Procedure` / `ServiceRequest` files had a typo'd
  Patient GUID in `subject.reference` (stray character, embedded double space).
- **I-42** `fixture` — 188 files' `Claim.patient` / `Coverage.beneficiary` /
  `AllergyIntolerance.patient` pointed at two fixed placeholder GUIDs left
  behind by a generation template; no such test cases ever existed.
- **I-46** `fixture` — 229 files' `subject` / `patient` / `beneficiary` pointed
  at the wrong Patient GUID, plus a `null-null.json` (CMS871) and a
  misnamed CMS1264 Claim. Repaired by `scripts/validate_test_fixtures.py`.
- **I-51** `fixture` — CMS347 `1d3021bb` carried
  `Patient/1d3021bb-b593-4efc-af5b-3  20243bbe9b7` (two stray spaces splitting
  the GUID) on Encounter `9d311cdd` (CPT `99385`) and FACIT-Pal Observation
  `ea2c69a6` (LOINC `71007-9`), zeroing IP / Denominator / Denominator
  Exception.

### Non-canonical UCUM `system`

`https://ucum.org` instead of `http://unitsofmeasure.org`. Note the two very
different failure modes — a silent mismatch versus a hard throw that takes out
the whole library.

- **I-43** `fixture` — 3 Observations (CMS347 ×1, CMS69 ×2) used the wrong
  system URI; failed silently.
- **I-50** `fixture` — CMS347 `6da189af`'s LDL Observation `dce97708` (LOINC
  `13457-7`) threw
  `FHIRHelpers.ToQuantity.InvalidFHIRQuantity: Invalid FHIR Quantity code: mg/dL (https://ucum.org|mg/dL)`,
  killing the library and producing Missing Results across 20 cells.

### Terminology content missing or truncated

- **I-03** `content` — the committed valueset files held only the first page of
  a paged `$expand`, so `[Condition: "Cancer"]`
  (`2.16.840.1.113883.3.526.3.1010`) silently missed `C00.0` / `80914001`.
  42 of 45 expansions were repaired from the IG Publisher `txcache`.
  **Detection signature: `expansion.contains` shorter than
  `expansion.total`.** Note what is *not* the signature — the
  `expansion.parameter` `count: 1000 / offset: 0` block is ordinary VSAC
  `$expand` response metadata and appears on healthy files too.
  **Before "completing" any expansion, check for CPT codes:** a valueset
  containing `http://www.ama-assn.org/go/cpt` codes must never be committed
  with more than 1000 entries, an AMA licensing restriction. This is why I-03's
  repair was scoped to non-CPT valuesets.
- **I-06** `content` — **a misdiagnosis worth remembering.** CMS157's
  Initial Population of 0 was first attributed to a fixture `Encounter.type`
  mismatch against `"Office Visit"` / `"Audio Visual Telehealth Encounter"`.
  That conclusion was retracted: the real cause was I-03's empty `"Cancer"`
  expansion. A population that collapses to 0 looks like an attribution bug and
  is often a terminology bug.
- **I-44** `fixture` — **the "Fixed" status was a phantom.**
  `ValueSet-2.16.840.1.113762.1.4.1196.394` ("Hypoglycemics Treatment
  Medications") was recorded as fixed by "committing the external valueset
  source file", but the file had never been committed. The engine threw
  `Unable to locate ValueSet …1196.394` on every run and
  `Encounter with Hypoglycemic Medication` was `[]` for every patient.
  Committed from the IG Publisher `txcache` on 2026-09-18 (238 RxNorm codes,
  complete expansion, no CPT). **Verified:** CMS871 went from 20 failing cells
  to 10, cases `7507debb` and `35719b1a` now pass, and no other measure moved.
  Two lessons: confirm a `Fixed` status is actually present in the repo, and
  note that a hard terminology error **masks** everything downstream of it —
  fixing this one exposed I-63 on a third case that had looked like a pure
  I-44 failure.

### CQL authored against the wrong element or overload

- **I-53** `migration` — choice-typed `.effective` / `.performed` fed straight
  into a temporal operator with no `.toInterval()` conversion. Fixed on
  CMS72/CMS646.
- **I-54** `migration` — `.onset.toInterval()` used where
  `.prevalenceInterval()` was meant. `.onset.toInterval()` yields a zero-width
  point at onset, which can never `overlaps` a measurement period years later,
  so chronic / still-active checks never fire. Fixed at 16 sites by moving to a
  base `[FHIR.Condition: ...]` retrieve plus `prevalenceInterval()` (see I-28).
- **I-59** `migration` — CMS22's 6 `ServiceNotRequested` negation defines
  filtered base FHIR `.reasonCode in "Patient Declined"`, but US Quality Core
  carries the decline reason in the `us-quality-core-doNotPerformReason`
  extension, so the Denominator Exception under-fired. Fixed by switching to
  the `.reasonRefused()` accessor.
  - 2 CMS22 cases (`f9417a57`, `c41f9946`) remain open under I-52 — a
    positive-retrieve over-fire needing a `doNotPerform is not true` filter.
    See `CONNECTATHON-BREADCRUMBS.md`.

### Measurement-period / date-window mismatch

- **I-49** `fixture` — every CMS1264 fixture date sat in 2027/2028 while the
  measurement-period override was `@2026-01-01 .. @2027-01-01`, so 57 of 58
  cases evaluated 0. Note case `9bac5045` inverted instead (`exp=0, act=1`) —
  a uniform date offset can push a case *into* a population as easily as out.
  Fixed by re-keying 653 date tokens back one year and setting the CQL default
  measurement period from `@2027` to `@2026`.

### No CQL authored

- **I-02** `content` — CMS145 and CMS149 had no CQL at all; not a conversion or
  engine defect. Fixed by porting the libraries from QI-Core.

### Retired or superseded ids

- **I-09** `content`, retired 2026-09-10 — **another misdiagnosis.** CMS142's 5
  cases with `Group_1:Denominator Exception` = 0 were filed as fixture MR
  authoring. Expected values and fixture data were both correct; the
  category-bearing `CommunicationNotDone` has `subject: null`, so
  `[CommunicationNotDone: category in ...]` returns `[]`. All 5 cases moved to
  I-39.
- **I-30** `engine`, retired 2026-08-29 — duplicate of I-28 (same missing
  `FHIRCommon` Choice overload for `prevalenceInterval`). Rolled into I-28 and
  the `[I-30]` CQL comments renamed.
- **I-35** — never assigned. The number was skipped, and the slot is kept as a
  permanent gap rather than renumbered into.
