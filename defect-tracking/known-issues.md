# Known Issues

Every issue the test suite has surfaced so far, with its root-cause class and
current status. The **Open issues** table is generated from the project's issue
catalog, so don't edit it by hand; it's replaced on the next update. Everything
else in this file is maintained by hand. No script reads this file.

The file is in two parts. **Open issues** is the actionable list. **Resolved —
reference patterns** keeps the closed issues around for a different reason: a
resolved issue is a catalogued *failure fingerprint*, and several of the open
ones were first misdiagnosed as something already sitting in that list.

If you fix something, add it to **Resolved — reference patterns** under the
matching family as a one-line fingerprint plus the fix, and cite the `I-` id in
your `change-log.md` entry. Its row leaves **Open issues** on the next update.
To report something new, open an issue on this repository.

Issue ids also appear in CQL comments next to the affected logic. Use the full block —
issue id, one-line summary, upstream ticket, affected test cases — e.g.

```cql
// [I-28] base FHIR.Condition retrieve (defect-tracking/known-issues.md)
// Upstream ticket: https://github.com/cqframework/clinical_quality_language/issues/1872
// Affected test cases: all 45 CMS117 cases (library-wide translate failure)
```

`Upstream ticket:` is required; use `(pending)` when no ticket is filed yet. When code
was replaced, keep the original commented out immediately above the replacement under
an `// original` line, with every line of that block starting `//` in the same column.

## Root-cause classes

| Class | Means |
|---|---|
| `engine` | the CQL runtime engine misbehaves at evaluation time |
| `translator` | `cql-to-elm` misbehaves at compile time |
| `content` | measure authoring gap — no CQL written, wrong valueset |
| `migration` | a bug introduced converting QI-Core → US Quality Core |
| `fixture` | bad or incomplete test data |
| `vendored` | a bug in an upstream-authored CQL library vendored here |
| `implementation` | the measure steward's test data or expectation misuses FHIR/CQL semantics; the CQL is correct, and the steward fixes the test case |
| `harness` | a limitation of the test-case reporting scripts, not of the content |

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

<!-- OPEN_ISSUES_BEGIN: generated from the issue catalog; don't edit by hand -->

## Open issues (31)

| ID | Issue | Class | Status | Ticket | Measures |
|---|---|---|---|---|---|
| I-08 | CMS871 HH Hyperglycemia fixture MeasureReport / Denominator authoring mismatch. Needs re-confirmation: since the I-44 fix, every failing CMS871 cell is a missing result explained by I-63, and none matches this symptom | `content` | Open — needs re-confirmation | — | CMS871 |
| I-14 | CMSFHIR844 fixture MeasureReport hand-authors the Initial Population; the engine computes 0 / 1 where 1 / 2 is expected (2 cases) | `content` | Open — confirmed | — | CMSFHIR844 |
| I-15 | CMS646 fixture MeasureReport expects Denominator Exclusion 0 for `10cec7db`, but the resources present give 1 | `content` | Open — confirmed | — | CMS646 |
| I-16 | `Min()` over DateTime throws | `engine` | Worked around | — | CMS1173, CMS871 |
| I-17 | Raw `FHIR.dateTime` / choice-typed `X.effective` in temporal operators fails | `engine` | Worked around | — | CMS1173 |
| I-18 | Fluent overload ambiguity between sibling profiles that share a runtime class | `translator` | Worked around | [cqframework/clinical_quality_language#1855](https://github.com/cqframework/clinical_quality_language/issues/1855) | CMS68, CMS996, CMS108 +3 more |
| I-19 | Choice-type self-reference circular dispatch | `engine` | Worked around | — | CMS90, CMS133, CMS142 +5 more |
| I-20 | Sibling overloads ambiguous at runtime (same Java class) | `engine` | Worked around | — | CMS90, CMS133, CMS142 +6 more |
| I-21 | `as` cannot widen Choice to ancestor type | `engine` | Worked around | — | — |
| I-24 | Quantity division across dimensions rounds to zero (`mg / d` normalizes to g/s and rounds to `0E-8`). Worked around in CMS156 `averageDailyDose()` (see `change-log.md`); spec question HL7 Jira FHIR-58137 | `engine` | Worked around | [cqframework/clinical_quality_language#1690](https://github.com/cqframework/clinical_quality_language/issues/1690) | CMS156 |
| I-25 | `singleton from empty list` throws instead of returning null | `engine` | Worked around | — | CMS156 |
| I-26 | `Unable to extract codes from fhirType Reference`: a terminology-filtered medication retrieve throws when `MedicationRequest.medication` is a `Reference(Medication)`, so the case produces no results | `engine` | Open — confirmed | [cqframework/clinical_quality_language#1868](https://github.com/cqframework/clinical_quality_language/issues/1868) | CMS135, CMS165 |
| I-28 | Sibling-profile Condition union fed to `prevalenceInterval(Choice<ConditionEncounterDiagnosis, ConditionProblemsHealthConcerns>)` will not resolve — `FHIRCommon.cql` declares no Choice overload for those two profiles (only base `FHIR.Condition`) and the translator will not widen the Choice | `translator` | Worked around | [cqframework/clinical_quality_language#1872](https://github.com/cqframework/clinical_quality_language/issues/1872) | CMS347, CMS117, CMS138 +28 more |
| I-31 | FHIRCommon prevalenceInterval() returns null for a non-active or no-status Condition with no abatement end because its non-active branch queries a null source; spec-mandated CQL semantics return null. Worked around with measure-local if/else in CMS108 and CMS71; the vendored-library fix lives at HL7 JIRA FHIR-59708 (GitHub #1879 closed 2026-10-29, #1880 withdrawn) and the workaround stays in place until that fix lands | `vendored` | Worked around (CMS108, CMS71) | [FHIR-59708](https://jira.hl7.org/browse/FHIR-59708) | CMS108, CMS71 |
| I-33 | Raw `FHIR.dateTime` returned from a define breaks `sort` and a mixed-type `Interval` endpoint — `"Values FHIR.dateTime and FHIR.dateTime are not comparable"` (CMS156 Index Prescription Start Date; CMS646 `342d2bec`) | `engine` | Worked around (CMS156); CMS646 `342d2bec` open | [cqframework/clinical_quality_language#1878](https://github.com/cqframework/clinical_quality_language/issues/1878) | CMS156, CMS646 |
| I-37 | Ambiguous `recorded(...)` overload in `USQualityCoreCommon` threw and aborted CMS68 `f2e2e1c0`; the overload was removed and its call sites bypassed (see `change-log.md`) | `translator` | Worked around | [cqframework/clinical_quality_language#1855](https://github.com/cqframework/clinical_quality_language/issues/1855) | CMS68, CMS190 |
| I-55 | Field swapped `.recorded` → `.effective`/`.performed` to dodge a translator ambiguity | `migration` | Worked around | [cqframework/clinical_quality_language#1855](https://github.com/cqframework/clinical_quality_language/issues/1855) | CMS190, CMS996, CMS108, CMS68, CMS646 |
| I-61 | Translator's ChoiceType compatibility check bypasses a registered FHIRHelpers conversion when a union produces divergent tuple-element types, leaving raw `FHIR.instant` `INRLabTest.issued` unconverted (CMS108/CMS190 INR Low Risk Indicator); also seen in CMS986's `union` of raw `authoredOn` with a converted `System.DateTime` (Hospice/Dietitian Referral defines) | `translator` | Worked around | — | CMS108, CMS190, CMS986 |
| I-62 | The test-case report cannot invoke per-member `cqfm-aggregateMethod` measure-observations for ratio / continuous-variable measures, so those cells are excluded from automated scoring | `harness` | Worked around | — | CMS1017, CMS871, CMS986 |
| I-63 | CMS871 test cases `98533ccd` and `fd579f44`, whose encounter periods are shorter than 24 hours, aborted before any population evaluated with `Invalid Interval - the ending boundary … must be greater than or equal to the starting boundary …`. The root cause is FHIRCommon's `toDayNumbers` / `daysInPeriod` (see I-81); CMS871 now uses measure-local replacements, so the cases evaluate while the upstream defect remains open | `vendored` | Worked around | [FHIR-59691](https://jira.hl7.org/browse/FHIR-59691) | CMS871 |
| I-67 | CMS347 `1ba7b147`: the test case uses a start-only `abatementPeriod` to mean "resolved 2025-12-31". FHIRCommon correctly reads the missing `end` as open-ended, so `prevalenceInterval()` runs to end of time and `"Has ESRD Diagnosis"` fires (`Group_4:Denominator Exception` 0 → 1). Confirmed with SME 2026-10-08. The steward should use `abatementDateTime` or add an `end`. No CQL change | `implementation` | Open — confirmed | — | CMS347 |
| I-68 | Interval selector returns `null` when both bounds evaluate to null (`Interval[null, null)`) instead of an interval with unknown bounds. No result difference for `overlaps`; a start-sensitive consumer (`starts before`) loses rows the spec would keep. No affected case found yet | `engine` | Open — confirmed | [cqframework/clinical_quality_language#1850](https://github.com/cqframework/clinical_quality_language/issues/1850) | CMS347 |
| I-69 | `is Interval<T>` returns `false` when the interval has a null boundary, which also nulls an open-ended interval passed to a `Choice`-typed function parameter. FHIRCommon tests `is FHIR.Period` and isn't affected; one latent exposure (NHSN `"Normalize Interval"`), no affected case. Fixed upstream (`fb8055df`, merged 2026-10-08), not yet released | `engine` | Open — confirmed | [cqframework/clinical_quality_language#1857](https://github.com/cqframework/clinical_quality_language/pull/1857) | CMS347, CMS646 |
| I-70 | CMS646 `ab48e0c0`: the test expects Numerator 0 because the BCG was given before staging results came back, but the CQL measures from the start of the staging Procedure, and the BCG dose and the staging Procedure both start 2026-04-02T08:00, so `"First BCG Administered"` qualifies (`Group_1:Numerator` expected 0, actual 1). The steward should move the BCG before the staging start or expect Numerator 1. No CQL change | `implementation` | Open — confirmed | — | CMS646 |
| I-71 | CMS996 `f6c7dbc1`: the test expects Denominator Exclusion 0 because the thrombolytic allergy "starts before and ends before ED", but it marks the end with `onsetPeriod.end` on an allergy that is still `active` with no `allergyintolerance-abatement`. `onset[x]` only says when the allergy began, so FHIRCommon `prevalenceInterval()` correctly runs to end of time and overlaps the ED encounter (expected 0, actual 1). The steward should mark the allergy resolved with an abatement, or expect Denominator Exclusion 1. No CQL change | `implementation` | Open — confirmed | — | CMS996 |
| I-72 | CMS145 `1f70822b`: the test expects no `Group_2:Denominator Exception` because the patient-reason beta-blocker not-ordered falls on the first visit, but `"Has Medical or Patient Reason for Not Ordering Beta Blocker Therapy"` accepts the reason at any `"Qualifying CAD Encounter and Prior MI"`, and both visits qualify (expected 0, actual 1). Twin case `b19af44d`, with the reason at the last visit, expects 1. The steward should change the expectation or the CQL. No CQL change | `implementation` | Open — confirmed | — | CMS145 |
| I-75 | CMS72 `be5c4068`: the test expects a `Denominator Exception` for an INR > 3.5, but INR Observation `dfde458a` carries `valueQuantity` `{value: 100, unit: "0", system: UCUM}` with no `code`. `FHIRHelpers.ToQuantity` takes the unit from `Coalesce(code, unit, '1')`, and UCUM reads a bare `"0"` as a factor of zero, so the INR evaluates as `0 '1'` and `"Encounter With An INR Greater Than 3.5"` is empty (expected 1, actual 0). A copy with `unit`/`code` `"1"` matches the fixture. Pending SME confirmation; if a fixture fix is preferred it becomes a `fixture` issue. No CQL change | `implementation` | Open — suspected | — | CMS72 |
| I-78 | In CMS145 `overlapsAfterDayOfEncounter`, whose parameter is `Choice<AllergyIntolerance, ConditionProblemsHealthConcerns>`, the translator binds `isVerified()` and `prevalenceInterval()` in the Condition branch to the AllergyIntolerance overloads, so a beta-blocker allergy or intolerance diagnosis never meets the Denominator Exception. Explicit casts are applied as a temporary workaround, so the five affected test cases pass while the defect remains open | `translator` | Worked around | [cqframework/clinical_quality_language#1872](https://github.com/cqframework/clinical_quality_language/issues/1872) | CMS145 |
| I-79 | CMS646 case `6e9a1974` scores Numerator 1 against an expected 0 once its MedicationAdministration references the right patient | `content` | Open — suspected | — | CMS646 |
| I-80 | When a `union` combines lists whose tuple element types diverge, the engine can silently drop an entire branch — any tuple with a `null` element, or an empty branch, makes the translator-inserted type cast evaluate to null. Worked around in CMS771 by giving both branches identical tuple element types | `engine` | Open — confirmed | [cqframework/clinical_quality_language#1875](https://github.com/cqframework/clinical_quality_language/issues/1875) | CMS771 |
| I-81 | FHIRCommon `toDayNumbers` builds `Interval[1, duration in days between start and end]`, which is the invalid interval `[1, 0]` for any period shorter than 24 hours, so a library using `daysInPeriod` aborts before any population evaluates; `daysInPeriod` also produces a degenerate final-day segment once the day count is clamped. Worked around in CMS871 with measure-local replacements | `vendored` | Open — confirmed | [FHIR-59691](https://jira.hl7.org/browse/FHIR-59691) | CMS871 |

<!-- OPEN_ISSUES_END -->

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
  - The follow-up that called `us-quality-core-observationcancelled` malformed
    (missing hyphen) was closed 2026-10-15: it is the model info's identifier,
    matches every other unhyphenated USQC negation profile and QI-Core's
    `qicore-observationcancelled`, and 22 cases across 6 measures pass because
    `[ObservationCancelled]` matches it.
- **I-48** `fixture` — same shape on CMS165/CMS135: blood-pressure panels
  (LOINC `85354-9` / `8480-6` / `8462-4`) and an `82810-3` pregnancy
  Observation carried `...observation-screening-assessment`, emptying
  `[USCore.BloodPressureProfile]`. Fixed by re-attributing to
  `us-core-blood-pressure` / `us-core-observation-pregnancystatus`.

### Broken or typo'd patient reference

A reference that does not resolve produces a silent zero, never an error — the
resource simply never attaches to the patient.

- **I-41** `fixture` — 40 fixture files (CMS347 35, CMS72 3, CMS108 1, NHSN 1)
  had a `subject.reference` that did not point at their own patient: 36 at
  another patient's GUID, 4 at a typo of the right one (stray or dropped
  character, embedded double space). Fixed 2026-09-01 (`fe41c7bcc`, 38 files)
  and 2026-09-18 (`f0e8eb172`, the 2 `1d3021bb` files, also I-51).
- **I-42** `fixture` — 188 files' `Claim.patient` / `Coverage.beneficiary` /
  `AllergyIntolerance.patient` pointed at two fixed placeholder GUIDs left
  behind by a generation template; no such test cases ever existed.
- **I-46** `fixture` — 229 files' `subject` / `patient` / `beneficiary` pointed
  at the wrong Patient GUID, plus a `null-null.json` (CMS871) and a
  misnamed CMS1264 Claim. Repaired by `scripts/validate_test_fixtures.py`.
- **I-07** `fixture` — CMS816's 12 failing Initial Population/Denominator cases
  (2 also Numerator) were originally filed as a `content` "fixture MR hand-
  authors expected values that don't reproduce" mismatch. The real cause was
  narrower and mechanical: the `Encounter` resources for 17 of CMS816's 28
  test-case patients (19 files) had **no `subject` element at all**, so `context Patient` scoping
  silently dropped them from `["Encounter": "Encounter Inpatient"]` regardless
  of how correctly type/status/period were authored — confirmed by direct CQL
  execution (`["Encounter": "Encounter Inpatient"]` returned empty *before* any
  `where` filter applied) and by a control check (every failing case's
  Encounter lacked `subject`; every passing case's had it). 5 of the 17
  patients hadn't produced a visible mismatch (expected value was `0`
  regardless), so the defect was wider than the 12 originally filed. Fixed by
  extending `scripts/validate_test_fixtures.py`'s required-field presence
  check from `Task.for` only to also cover `Encounter` / `MedicationAdministration`
  / `Observation` `subject` (`--fix-required-fields --apply`), which injected
  `subject: {"reference": "Patient/<folder guid>"}` into all 19 files.
  **Verified 2026-09-18**: CMS816FHIRHHHypo now passes all 28 test cases
  (84/84 population cells). See `change-log.md`.
- **I-39** `fixture` — CMS142's 5 failing Denominator Exception cases (expected
  1, actual 0): in each, the CommunicationNotDone carrying the `category` the
  "Medical or Patient Reason for Not Communicating ..." defines retrieve on had
  **no `subject`**, so `[CommunicationNotDone: category in ...]` was correctly
  empty under `context Patient`. The test cases were authored in MADiE, whose
  engine treats every resource in a test case as the patient's without checking
  references, so its expected results counted the subject-less resources. A
  repo-wide scan found 11 such resources (10 CMS142 Communications in 7 cases, 1
  CMS149 Observation); `subject: {"reference": "Patient/<folder guid>"}` was
  injected into all 11, and `scripts/validate_test_fixtures.py` now checks
  Communication `subject` too. **Verified 2026-10-16**: CMS142 passes all 32
  test cases (128/128 cells); CMS149 still passes all 33. See `change-log.md`.
- **I-51** `fixture` — CMS347 `1d3021bb` carried
  `Patient/1d3021bb-b593-4efc-af5b-3  20243bbe9b7` (two stray spaces splitting
  the GUID) on Encounter `9d311cdd` (CPT `99385`) and FACIT-Pal Observation
  `ea2c69a6` (LOINC `71007-9`), zeroing IP / Denominator / Denominator
  Exception.
- **I-74** `fixture` — the stroke Claim in CMS72 `e126cdec` had
  `item.encounter` `Encounter//5c954893b848462de0ae623a` (matches no encounter),
  and in CMS104 `0b1aa8ee` / `e84c89f7` had no `item.encounter` or
  `item.diagnosisSequence`. `CQMCommon.claimDiagnosis()` needs both, so
  `principalDiagnosis()` was null and `TJC."Ischemic Stroke Encounter"` was
  empty, zeroing IP / Denominator and the exclusion or exception (both engines).
  Fixed by linking each Claim to the inpatient encounter. **Verified
  2026-10-09**: all 9 cells recover, no other cell moves.

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
- **I-45** `fixture` — sparse `MedicationRequest` dosage fixtures tripped the
  I-25 `singleton from empty list` bug. Fixed in the probe fixtures; the real
  CMS156 fixtures pass without enrichment (watch closed 2026-10-15).
- **I-52** `migration` — unqualified `[MedicationRequest: …]` / `[ServiceRequest: …]`
  retrieves also returned the `doNotPerform` (`…notrequested`) resources, so a
  declined order counted as a real one. Fixed 2026-10-01 by qualifying them as
  `[USQualityCore.MedicationRequest: …]` / `[USQualityCore.ServiceRequest: …]`
  (`e1714e2c`, `217a29f1`) in CMS347, CMS104, CMS71, CMS135, CMS144, CMS645 and
  CMS22; no `doNotPerform` filter was needed. The same fix covers the 23 CMS347
  cases first filed as I-34 and the CMS108 / CMS190 / CMS135 cases first filed as
  I-32 / I-36 (all retired 2026-10-15), and 9 CMS135 / CMS144 / CMS645 cases
  moved from I-65 the same day.
- **I-59** `migration` — CMS22's 6 `ServiceNotRequested` negation defines
  filtered base FHIR `.reasonCode in "Patient Declined"`, but US Quality Core
  carries the decline reason in the `us-quality-core-doNotPerformReason`
  extension, so the Denominator Exception under-fired. Fixed by switching to
  the `.reasonRefused()` accessor.
  - The 2 remaining CMS22 cases (`f9417a57`, `c41f9946`, filed under I-52) were
    a positive-retrieve over-fire. Fixed 2026-10-01 (`e1714e2c`, confirmed on
    the 2026-10-07 grid) by qualifying the
    unqualified `[ServiceRequest: …]` retrieves as
    `[USQualityCore.ServiceRequest: …]`; no `doNotPerform` filter was needed.
- **I-60** `content` — CMS2's `"Denominator Exceptions"` was hardcoded to
  `false`, with its two `ObservationCancelled` negation defines commented out.
  Fixed by restoring them and reading the reason with the `notDoneReason()`
  fluent function instead of the `.notDoneReason` element. All 8 cases
  (`Group_1:Denominator Exception` 1→0) now pass and match QI-Core.

### Measurement-period / date-window mismatch

- **I-66** `fixture` — CMS177 `85e6225c` ("psychotherapy encounter before MP")
  had its Encounter dated 2026-02-11, inside the 2026 measurement period, and no
  `meta.profile`. The MADiE source has 2025-02-11 and `qicore-encounter`. CMS
  over-included it (Initial Population 0→1). QI-Core returned 0 only because its
  Encounter retrieve requires the profile. Fixed by restoring the 2025 date and
  setting `us-quality-core-encounter`. Not a CQL, translator or engine issue;
  the earlier I-36 attribution was wrong.
- **I-49** `fixture` — every CMS1264 fixture date sat in 2027/2028 while the
  measurement-period override was `@2026-01-01 .. @2027-01-01`, so 57 of 58
  cases evaluated 0. Note case `9bac5045` inverted instead (`exp=0, act=1`) —
  a uniform date offset can push a case *into* a population as easily as out.
  Fixed by re-keying 653 date tokens back one year and setting the CQL default
  measurement period from `@2027` to `@2026`.

### No CQL authored

- **I-02** `content` — CMS145 and CMS149 had no CQL at all; not a conversion or
  engine defect. Fixed by porting the libraries from QI-Core.

### Fixed by an engine upgrade

- **I-22**, **I-23** `engine` — `convert <Duration> to days` returning null and
  `convert` / `ConvertQuantity` rejecting calendar-word units (`'day'`) no
  longer reproduce on translator/engine 5.4.0 (probe 2026-10-15). The
  `ToDays()` workaround the dossiers described was never committed.
- **I-57** `vendored` — the packaged CMD `2.0.0-ballot` dispense path
  (`convert D.daysSupply to days`) returns the days supply on engine 5.4.0; no
  CMS128-local workaround exists or is needed.

### Retired or superseded ids

- **I-09** `content`, retired 2026-09-10 — **another misdiagnosis.** CMS142's 5
  cases with `Group_1:Denominator Exception` = 0 were filed as fixture MR
  authoring. Expected values and fixture data were both correct; the
  category-bearing `CommunicationNotDone` has `subject: null`, so
  `[CommunicationNotDone: category in ...]` returns `[]`. All 5 cases moved to
  I-39.
- **I-10** `content`, retired 2026-10-14 — **another misdiagnosis.** CMS819's 2
  cases were filed as fixture MR authoring. The expected values were right; the
  resources they need were lost to duplicate ids in the MADiE source bundles.
  Both cases moved to I-76 (`73b0c1fe` fixed 2026-10-13, `31b40acc` fixed
  2026-10-14).
- **I-04** `content`, retired 2026-10-15 — superseded by I-62. The CMS986
  Measure Observation diagnosis had already been retracted to the harness
  aggregation gap; every CMS986 cell passes.
- **I-13** `content`, retired 2026-10-15 — no longer reproduces. CMS1218
  `ea9c34ee` has passed since the 2026-09-18 resync; QI-Core agrees. The
  mechanism was not isolated.
- **I-27** `engine`, retired 2026-10-15 — **another misdiagnosis.** The 18
  "union branch evaluates empty" cases (CMS104, CMS108, CMS190) had
  `TaskRejected` fixtures with no `Task.for`, so patient scoping dropped them.
  Fixed by the 2026-09-18 Task fixture repair; moved to I-46.
- **I-29** `engine`, retired 2026-10-15 — unconfirmed and never tied to a
  failing cell. The `PCMaternal.cql` `as FHIR.dateTime` casts remain a latent
  I-16 / I-17 / I-33-family hazard.
- **I-32**, **I-36** `engine`, retired 2026-10-15 — "`us-quality-core-*`
  profile retrieve returns empty" never had a confirmed instance. Every cited
  case was fixed or re-attributed under I-52, I-55, I-31, I-66, I-65, I-71 or
  I-33; several were over-fires, not empty retrieves.
- **I-34** `engine`, retired 2026-10-15 — the CMS347 instance of I-52 (same
  mechanism, same 2026-10-01 qualifier fix); its 23 cases moved to I-52.
- **I-58** `vendored`, retired 2026-10-15 — nothing distinct from I-22 /
  I-23 / I-24. The vendored CMD 6.0.000 copy it described never existed in
  the repo; CMS156's only live adaptation is the I-24 `averageDailyDose()` fix.
- **I-30** `engine`, retired 2026-08-29 — duplicate of I-28 (same missing
  `FHIRCommon` Choice overload for `prevalenceInterval`). Rolled into I-28 and
  the `[I-30]` CQL comments renamed.
- **I-35** — never assigned. The number was skipped, and the slot is kept as a
  permanent gap rather than renumbered into.
