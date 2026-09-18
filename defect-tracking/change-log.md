# Defect-Tracking Change Log

Records actual CQL, FHIR resource, valueset, and similar content changes. An
entry may cite the `I-XX` issue it resolves or relates to when one is known,
but this is not required — not every change traces back to a tracked issue.

Where possible, an entry describing a CQL code change should include an
**Example** subsection with fenced `before`/`after` snippets so another
developer can see exactly what changed without cross-referencing another
file. For a change applied identically at many call sites, one representative
snippet plus a note of how many sites is enough — not one copy per site.

> **This file is the authoritative record of applied content changes**, and it
> is maintained by hand — add an entry whenever you change CQL, a FHIR
> resource/fixture, or a valueset.
>
> Two categories of change are absent from the **Measures Affected** lines
> below, because those lines only carry `CMS*` names: edits to shared libraries
> (e.g. `input/cql/TJCOverall.cql`) and to the `test*` / `defectHelper` scaffold
> probe libraries. Both are called out in the relevant entry text instead.
>
> Entries before 2026-09-18 were written while the detailed per-issue dossiers
> still lived in this repo, so some cite `defect-tracking/issues/I-XX.md` or
> other files that have since moved to the internal tooling repo. The `I-XX`
> ids themselves are still valid — look them up in `known-issues.md`.

## Replace `ConditionProblemsHealthConcerns`/`ConditionEncounterDiagnosis` union with a single `Condition` retrieve

**Problem:** the Choice-typed union of two sibling profiles that compile to the same runtime Java
class caused ambiguous/circular resolution errors in `prevalenceInterval()` and related calls
(engine issue I-28).

**Fix:** replaced the union retrieve with a single base `[FHIR.Condition: ...]` retrieve, rolled
out in three stages (13 measures, then 9 more, then a final 4 — CMS133/CMS128/CMS56/CMS131) plus
a dedicated CMS156 pass. Added a `verificationStatusIsNotInvalid` fluent helper and isolation test
fixtures to support the rollout.

**Measures Affected:** CMS90, CMS128, CMS129, CMS131, CMS133, CMS136, CMS138, CMS142, CMS143,
CMS153, CMS155, CMS156, CMS157, CMS159, CMS347, CMS951, CMS56, CMS996, CMS1154, CMS1157, CMS117,
CMS124, CMS314, CMS349, CMS75, CMS1188, CMS22, CMS645, CMS646, CMS69, CMS71, CMS771

## Fix raw `FHIR.dateTime` comparison failures

**Problem:** raw `FHIR.dateTime` values fed directly into temporal operators / `sort` failed at
runtime with "not comparable" errors (engine issues I-16/I-33).

**Fix:** unwrap via `.value` / convert with `.toInterval()` before comparing.

**Measures Affected:** CMS1173, CMS156

## Port CMS149 CQL from QICore

**Problem:** CMS149 had no CQL authored at all under USQualityCore — a content gap, not a
conversion bug.

**Fix:** ported the QICore CQL over; comes up fully passing.

**Measures Affected:** CMS149

## Fix measurement-period/date issues on CMS1264 and NHSN

**Problem:** CMS1264's measurement period and an NHSN measure's fixture resource year were out of
sync with the current cycle.

**Fix:** adjusted CMS1264's measurement period; updated NHSN's fixture resource year.

**Measures Affected:** CMS1264, NHSNAcuteCareHospitalMonthlyInitialPopulation1

## Sweep remaining `onc`→`astp` namespace/resource-reference issues; extend comparison tooling

**Problem:** some fixtures still carried the stale `onc` profile-namespace/resource-reference
issues after the initial bulk fix; the comparison/discrepancy-report tooling needed more detail to
keep diagnosing the remaining mismatches.

**Fix:** fixed the residual `onc`→`astp` issues on affected fixtures; extended the
comparison/discrepancy-report tooling (qi-core diff detail, a global measurement-period
parameter, test-case analysis support).

**Measures Affected:** CMS50, CMS56, CMS68, CMS69, CMS74, CMS75, CMS90, CMS129, CMS135, CMS165,
CMS347, NHSNGlycemicControlHypoglycemiaInitialPopulation

## Fix CMS347 fixture data (UCUM URI, whitespace reference)

**Problem:** an Observation fixture carried a non-canonical UCUM system URI, and an Encounter's
`subject.reference` was whitespace-corrupted (GUID split).

**Fix:** repaired both fixture defects directly; also added hygiene fixes to the known-issues
catalog (boolean `resolved` field instead of stringly-typed).

**Measures Affected:** CMS347

## Broaden I-32 profile-retrieve gap; classify new content-authoring gaps

**Problem:** the I-32 profile-retrieve engine bug was confirmed to affect more
`us-quality-core-*` profile types than originally scoped. Separately, several fixtures'
hand-authored MeasureReports encoded population/observation values that the CQL and resources
present couldn't actually reproduce — a content-authoring gap, not an engine bug.

**Fix:** broadened I-32 to the additional profile types; catalogued the authoring gaps as I-04
through I-14.

**Measures Affected:** CMS108, CMS190 (I-32); CMS986, CMS1017, CMS157, CMS816, CMS871, CMS142,
CMS819, CMS159, CMS0334, CMS1218, CMSFHIR844 (content-authoring gaps)

## Diagnose I-37; extend I-15 authoring-gap residuals; fix GUID-truncation bug

**Problem:** CMS68's `recorded()` operator threw on an ambiguous call; I-15's authoring-gap
residuals needed to be extended to more measures; the issue tracker had been storing 8-char GUID
prefixes that no longer matched the full 36-char GUIDs.

**Fix:** diagnosed and catalogued I-37; extended I-15 across the additional measures; replaced
the truncated GUID prefixes with full GUIDs in the tracker.

**Measures Affected:** CMS68 (I-37); CMS72, CMS104, CMS646, CMS71, CMS1154 (I-15)

## Repair truncated non-CPT valuesets

**Problem:** 46 non-CPT valuesets had been committed with only the first 1000-code page of a
paged `$expand` (`expansion.contains < expansion.total`), silently under-matching
terminology-based retrieves.

**Fix:** repaired all 46 by pulling the complete expansion from the IG Publisher's terminology
cache; confirmed CPT valuesets were unaffected (none exceed 1000 codes); documented which
valuesets were updated.

**Measures Affected:** cross-cutting (terminology cache, not measure-scoped in the diff itself);
known to have resolved the CMS157 "Cancer" valueset mismatch documented elsewhere

## Resync resources after IG Publisher refresh; bypass fix for CMS108

**Problem:** an IG Publisher refresh required a full resource resync across fixtures; CMS108
separately needed a targeted workaround.

**Fix:** did the full resource resync; applied the CMS108 bypass fix.

**Measures Affected:** resource resync touched nearly all measures' fixtures repo-wide; CMS108
(bypass fix)

**Example** (`input/cql/CMS108FHIRVTEProphylaxis.cql`):

Medication negation arm (line ~327, "No VTE Prophylaxis Medication Administered Or Ordered"):

```cql
-- before
authoredOn: NoMedicationAdm.effective

-- after
authoredOn: NoMedicationAdm.recorded()
```

Device negation arm (lines ~409-412, `ProcedureNotDone`):

```cql
-- before
let DeviceNotDoneTiming: DeviceNotApplied.performed
...
authoredOn: DeviceNotDoneTiming

-- after
authoredOn: DeviceNotApplied.ext('http://fhir.org/guides/astp/us-quality-core/StructureDefinition/us-quality-core-recorded').value as FHIR.dateTime
```

## Port CMS108's negation fix to CMS190; reclassify affected cases

**Problem:** CMS190 carried the same not-done negation `authoredOn` defect already fixed on
CMS108 (cases previously misclassified under I-32 that were actually I-55/I-27).

**Fix:** ported CMS108's `.recorded()`/`.ext()` fix to CMS190; reclassified the affected cases
from I-32 to I-55/I-27; verified under the current engine (13/13 Numerator flips).

**Measures Affected:** CMS190 (CMS108 referenced as the origin of the ported fix)

**Example** (`input/cql/CMS190FHIRVTEProphylaxisICU.cql`):

Medication arm (line ~301, same swap as CMS108):

```cql
-- before
authoredOn: NoMedicationAdm.effective

-- after
authoredOn: NoMedicationAdm.recorded()
```

Device arm (line ~373; removed `let DeviceNotDoneTiming: DeviceNotApplied.performed`):

```cql
-- before
let DeviceNotDoneTiming: DeviceNotApplied.performed
...
authoredOn: DeviceNotDoneTiming

-- after
authoredOn: DeviceNotApplied.ext('http://fhir.org/guides/astp/us-quality-core/StructureDefinition/us-quality-core-recorded').value as FHIR.dateTime
```

End-of-Period workaround reverted (line ~385, "Encounter With VTE Prophylaxis Received Day Of Or
Day After..."):

```cql
-- before
start of NoVTEMedication.authoredOn during day of ( end of AnesthesiaProcedure.performed.toInterval ( ) ).calendarDayOfOrDayAfter ( )

-- after
NoVTEMedication.authoredOn during day of ( end of AnesthesiaProcedure.performed.toInterval ( ) ).calendarDayOfOrDayAfter ( )
```

## Wrap-up: Task fixture fix, doc consolidation, authoredOn tweak

**Problem:** Task resources were missing a required `for` property; conversion-notes/CQL
change-log documentation was scattered outside `defect-tracking/`.

**Fix:** added the missing `for` property; consolidated the conversion-notes and CQL change-log
documentation into `defect-tracking/`; made a final `authoredOn`-handling tweak.

**Measures Affected:** CMS71, CMS72, CMS104, CMS108, CMS138, CMS190

## Fix CMS22 `ServiceNotRequested` negation defines to use `reasonRefused()` instead of `.reasonCode`

**Problem:** 6 negation defines checked base FHIR `.reasonCode in "Patient Declined"` on
`ServiceNotRequested`-profiled `ServiceRequest`s — an element never populated under that profile,
since the decline reason lives in the `us-quality-core-doNotPerformReason` extension instead.
Retracted from I-36 (was misclassified as an engine profile-retrieve defect) and refiled as I-59.

**Fix:** replaced `.reasonCode in "Patient Declined"` with `.reasonRefused() in "Patient Declined"`
(the existing `USQualityCoreCommon.cql` fluent accessor for this extension) at all 6 call sites.
Fixes 10 of 12 previously-failing cases with zero regressions. A related `doNotPerform`-exclusion
gap on 6 positive retrieves (I-52) was identified and verified as a candidate fix for the
remaining 2 cases, but deliberately **not applied** — left as a documented option for the
2026-09-20ish Connectathon rather than a unilateral call (see
`defect-tracking/CONNECTATHON-BREADCRUMBS.md`).

**Measures Affected:** CMS22 (I-59 applied; I-52 gap documented but not applied for this measure)

**Example** (`input/cql/CMS22FHIRPCSBPScreeningFollowUp.cql`; same swap applied at 6 call sites,
e.g. `"NonPharmacological Intervention Not Ordered"` line ~326):

```cql
-- before
and NonPharmIntervention.reasonCode in "Patient Declined"

-- after
and NonPharmIntervention.reasonRefused() in "Patient Declined"
```

## Reclassify CMS104's 9 I-36 cases to I-18/I-27 (no CQL change)

**Problem:** cross-referencing CMS104's currently-failing cases against `dqm-content-qicore-2025`'s
latest discrepancy report showed 100% overlap (69/69 GUIDs), prompting a fresh audit of CMS104's open
issues. The 9 cases attributed to I-36 (`us-quality-core-*` profile-retrieve-width, open/no
workaround) turned out to be two other already-root-caused defects, misclassified during the
2026-09-05 I-36 corroboration sweep.

**Fix (documentation only, no code/fixture change):** split and reclassified:
- 7 cases (`2d54a94c`, `146a6714`, `ac56c496`, `48952352`, `593382e8`, `7b1ac1a8`, `591c23ea`) — all
  `["MedicationNotRequested": ...]` retrieves against valid `MedicationRequest`/
  `us-quality-core-medicationnotrequested`-profiled fixtures — moved to **I-18/I-37** (the
  `TypeBuilder.dataTypeToQName` target-erasure defect; `MedicationNotRequested`→`MedicationRequest`
  was already named as a latent instance in I-37's "Blast radius" list, now corroborated by fixture
  evidence). Static evidence only — this workspace's LS can't currently resolve USCore/USQualityCore
  model info to compile CMS104 for a live ELM trace, so this is not yet a confirmed-by-execution root
  cause.
- 2 cases (`e081bee5`, `5adc911a`) — the `MedicationRequest`+`TaskRejected` union branch — moved to
  **I-27** (already tracked `5adc911a`; `e081bee5` added as the "Medical Reason" arm counterpart).
- CMS104 removed from I-36's `affected_measures`; `cases.csv` updated (9 `I-36` rows removed, 7 `I-18`
  + 2 `I-27` rows added).

**Measures Affected:** CMS104 (classification only; CMS68/CMS996/CMS108/CMS190/CMS144 unaffected —
I-18/I-37's existing scope and fix candidates are unchanged, CMS104 is additive corroboration)

## Convert raw `FHIR.instant` to `DateTime` in CMS108's INR Low Risk Indicator

**Problem:** `"Low Risk Indicator For VTE"`'s INR branch assigned `LowRiskDatetime:
INRLabTest.issued` — a raw `FHIR.instant`, unconverted. Downstream, `"Low Risk For VTE Or
Anticoagulant Administered From Day Of Start Of Hospitalization To Day After Admission"`'s
`during day of` precision comparison against that value silently returned `null` instead of
`true`, so the qualifying encounter never joined and `Numerator` came back empty for 4 cases
(`3db5c5a1`, `5741c41a`, `8bb999a1`, `dc0dcb01`; `Group_1:Numerator 1→0`). These 4 cases were
previously mis-attributed to I-32 (see reclassification note in `I-32.md`); root-caused and
re-filed as **I-61** (suspected engine issue — pending SME confirmation on whether an engine
should implicitly coerce `FHIR.instant` to `DateTime` in this position). **Update 2026-09-17:**
SME confirmed `during day of` should work as defined without requiring `.ToDateTime()`. A
follow-up investigation then root-caused the actual mechanism against the compiled ELM: the
union's three branches return divergent `LowRiskDatetime` types, so the translator emits a
`ChoiceType` for the tuple element; the translator's choice-compatibility check then treats that
`ChoiceType` as compatible with `System.DateTime` because one branch already matches, skipping
the registered `FHIRHelpers.ToDateTime` conversion in favor of a silent no-op cast. This is a
`cql-to-elm` **translator** defect (not the runtime engine — ruled out separately), so I-61's
`category` was reclassified from `engine` to a new `translator` category (see
`defect-tracking/issues/I-61.md` for the full investigation and the ruled-out hypotheses). The
`.ToDateTime()` workaround was briefly reverted during this investigation and had to be restored
— it remains required and must not be removed as "redundant".

**Fix:** wrap the raw value with `.ToDateTime()`, confirmed via CQL debug console A/B testing
(same `day of` qualifier, only the conversion varied: `null` → `true`).

**Measures Affected:** CMS108

**Example** (`input/cql/CMS108FHIRVTEProphylaxis.cql`, `"Low Risk Indicator For VTE"`):

```cql
-- before
return {
  id: INRLabTest.id,
  LowRiskDatetime: INRLabTest.issued
}

-- after
return {
  id: INRLabTest.id,
  LowRiskDatetime: INRLabTest.issued.ToDateTime()
}
```

## Apply I-61's `ToDateTime()` fix to CMS190 (corroborated same translator defect)

**Problem:** `CMS190FHIRVTEProphylaxisICU.cql`'s `"Low Risk Indicator For VTE"` has the
byte-for-byte identical three-branch union as CMS108's (divergent `LowRiskDatetime` types:
`System.DateTime` / raw `FHIR.instant` / `System.DateTime`), so it carries the same I-61
translator defect (see `I-61.md`). Verified live on case `f035a977`: before the fix,
`LowRiskDatetime` traced as `instant#2026-12-06T11:30:00.000Z` and `Numerator` returned `[]`; an
isolated scratch-copy probe with `.ToDateTime()` added flipped both to the correct values. This
case was previously mis-attributed to I-32 (see reclassification note in `I-32.md`).

**Fix:** applied the same `.ToDateTime()` conversion, with the same "do not remove as redundant"
warning comment, to CMS190's `"Low Risk Indicator For VTE"`. Verified via debug console —
`Numerator` now resolves correctly for `f035a977`.

**Measures Affected:** CMS190

**Example** (`input/cql/CMS190FHIRVTEProphylaxisICU.cql`, `"Low Risk Indicator For VTE"`):

```cql
-- before
return {
  id: INRLabTest.id,
  LowRiskDatetime: INRLabTest.issued
}

-- after
return {
  id: INRLabTest.id,
  LowRiskDatetime: INRLabTest.issued.ToDateTime()
}
```

## Retire legacy `E-`/`M-` issue IDs from CQL comments (comment-only, no logic change)

**Problem:** the catalog was renumbered from category-prefixed IDs (`B-`/`C-`/`E-`/`F-`/`M-`/`V-`)
onto the flat `I-XX` scheme, and `defect-tracking/engine-issues.md` was split into
`defect-tracking/issues/`. The CQL comments were never swept, so 37 libraries still cited retired
IDs and pointed readers at a file that no longer exists. `defect-tracking/issues/I-30.md` also
*claimed* the sweep had already happened (`"CQL comments updated from [I-30] to [I-28]"`), which
was untrue — `git log -S'[I-28]' -- input/cql/` returned zero commits.

**Fix:** swept 91 comment lines across 37 files in `input/cql/`:

| Was | Now | Sites |
|---|---|---|
| `E-13` | `I-28` | 149 |
| `E-18` | `I-33` | 3 |
| `E-11` | `I-26` | 3 |
| `E-03` | `I-18` | 2 |
| `M-04` | `I-55` | 2 |
| `defect-tracking/engine-issues.md` | `defect-tracking/issues/I-XX.md` | 79 |

Each mapping was derived from the deleted `engine-issues.md`'s own section headings rather than
inferred: the renumbering ran in contiguous per-category blocks whose boundaries and per-category
counts reconcile exactly against all 62 catalog entries. The mapping is now recorded in
`defect-tracking/issues/_legacy-id-map.md`, which also covers the legacy IDs left in place inside
the dated `conversion-notes.md` / `measure-parity-ledger-2026-08.md` logs.

Verified comment-only mechanically: stripping all `//` and `/* */` comments (string- and
quoted-identifier-aware) and collapsing whitespace leaves the executable CQL **byte-identical** in
all 95 libraries. Harness pass/fail counts are unchanged.

Also corrected `input/cql/testI37RecordedAmbiguousOverload.cql`, whose header claimed the
`.ext()` bypass had been "applied to CMS68". It has not — `CMS68FHIRDocumentationCurrentMeds.cql`
still calls `.recorded ( )`, and CMS68 is a deliberate Connectathon breadcrumb (I-37).

**Not done — known divergence:** 30 `input/resources/measure/*.json` files embed the same stale
comment inside their tooling-generated `contained` Library `effective-data-requirements`. These are
`_refresh.sh` / CQF-tooling output, so they will self-correct on the next IG Publisher refresh and
were deliberately not hand-edited.

**Measures Affected:** comment-only across 34 measure libraries; also `defectHelper.cql` and the
`testE11` / `testE15` / `testE18` / `testI37` scaffold probes (non-`CMS` names, so absent from the
list convention above).

## Repoint CQL issue references to `known-issues.md`; slim the reporting setup

**Problem:** the detailed per-issue dossiers (`defect-tracking/issues/`), the report-generation
pipeline, the cross-engine QI-Core comparison and the 26-file test suite all optimised for an
agent resuming context across sessions. For Connectathon participants working for two days that
is noise, and it buried the three things actually worth reading: what's broken, what's already
been fixed, and what's deliberately left open. 83 CQL comment lines also pointed at
`defect-tracking/issues/I-XX.md`, which no longer exists in this repo.

**Fix:** moved the tooling and the dossiers to a separate internal repo that wraps this one as a
git submodule, and reduced this repo to the original three-step workflow:

- `scripts/` is back to 17 files — `extract_population_expected.py`,
  `extract_population_actual.py`, `compare_results.py`, `comparison/populations.py`, a readme, two
  tests and the committed CSVs. `compare_results.py` went from 1,004 lines to 542; the discrepancy
  report from 2,548 lines to 619, with the QI-Core engine-diff section gone entirely.
- `defect-tracking/` is three hand-maintained files: `known-issues.md` (61 issues, flat table,
  free to edit — nothing generates it and no script reads it), `CONNECTATHON-BREADCRUMBS.md`, and
  this change log.
- Repointed 82 comment lines across 36 CQL libraries from
  `defect-tracking/issues/I-XX.md` to `defect-tracking/known-issues.md`, keeping the `[I-XX]` tag
  so the id still resolves — now against the tracker in this repo.

Two scoring behaviours were deliberately **kept** rather than reverted with the rest, because
removing them would change results rather than just presentation: population-name canonicalisation
(without it CMS986's expected and actual rows can never match) and the CQFM measure-observation
exclusions (without them the three ratio measures report ~1,031 phantom failing cells). Verified:
pass/fail is unchanged at **3,817 pass / 147 fail of 3,964 test cases**, and
`expected_results.csv`, `actual_results.csv` and `output_results.csv` are byte-identical to before
the change.

The CQL edits are comment-only, verified mechanically: stripping all `//` and `/* */` comments
(string- and quoted-identifier-aware) and collapsing whitespace leaves the executable CQL
**byte-identical** in all 95 libraries, and the per-file counts of `//`, `/*`, `*/` and `'` are
unchanged.

**Measures Affected:** comment-only across 34 measure libraries; also `defectHelper.cql` and the
`testE11` / `testE15` / `testE18` / `testI37` scaffold probes (non-`CMS` names, so absent from the
list convention above). No measure logic changed.
