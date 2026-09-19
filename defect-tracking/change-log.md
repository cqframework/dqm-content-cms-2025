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
conversion bug (issue I-02, which also covers CMS145).

**Fix:** ported the QICore CQL over; comes up fully passing.

**Measures Affected:** CMS149

## Fix measurement-period/date issues on CMS1264 and NHSN

**Problem:** CMS1264's measurement period and an NHSN measure's fixture resource year were out of
sync with the current cycle (issue I-49).

**Fix:** adjusted CMS1264's measurement period; updated NHSN's fixture resource year.

**Measures Affected:** CMS1264, NHSNAcuteCareHospitalMonthlyInitialPopulation1

## Sweep remaining `onc`→`astp` namespace/resource-reference issues; extend comparison tooling

**Problem:** some fixtures still carried the stale `onc` profile-namespace/resource-reference
issues after the initial bulk fix; the comparison/discrepancy-report tooling needed more detail to
keep diagnosing the remaining mismatches. This is the residual pass for issues I-40 (`onc`→`astp`
namespace) and I-41 / I-42 / I-46 (wrong-patient references); the initial bulk fixes predate this
log and have no entry of their own.

**Fix:** fixed the residual `onc`→`astp` issues on affected fixtures; extended the
comparison/discrepancy-report tooling (qi-core diff detail, a global measurement-period
parameter, test-case analysis support).

**Measures Affected:** CMS50, CMS56, CMS68, CMS69, CMS74, CMS75, CMS90, CMS129, CMS135, CMS165,
CMS347, NHSNGlycemicControlHypoglycemiaInitialPopulation

## Fix CMS347 fixture data (UCUM URI, whitespace reference)

**Problem:** an Observation fixture carried a non-canonical UCUM system URI (issue I-50; the same
`https://ucum.org` defect is tracked more broadly as I-43), and an Encounter's `subject.reference`
was whitespace-corrupted (GUID split — issue I-51).

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
resolved issue I-03 (the CMS157 "Cancer" valueset mismatch) and, with it, I-06 — whose original
fixture `Encounter.type` diagnosis was retracted once this repair landed

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

## Split `known-issues.md` into open issues and resolved reference patterns (docs only)

**Problem:** the 20 `Fixed` / `Retired` rows carried no usable information — several had an Issue
cell that was only a measure name (`I-02 | CMS145 / CMS149`, `I-03 | CMS157`). No `Fixed` id is
cited anywhere in `input/cql/`, and only I-59 was cited in this change log, so those rows had no
consumer and no trail to their own fix. Separately, 11 Issue cells were truncated mid-sentence
with a `…` — residue from when the file was generated from the per-issue dossiers — including
open ones: I-61 ended `"when a union…"` and I-62 ended `"(per-member function invocation +…"`.

**Fix:** restructured `known-issues.md` into two parts:

- **Open issues** — the table, restricted to `Open — confirmed`, `Open — suspected` and
  `Worked around` (42 rows). All 11 truncated cells rewritten as self-contained lines from the
  dossiers, keeping the operator / profile / field identifier. Fixed the `anticoagulation-FLutter`
  typo inherited from I-36's dossier title.
- **Resolved — reference patterns** — the 20 closed issues as a list grouped by failure family
  (profile URI mismatch, broken patient reference, non-canonical UCUM `system`, missing or
  truncated terminology, wrong element/overload, date-window mismatch, no CQL authored, retired
  ids). Each bullet names the concrete artifact rather than the measure, so it reads as a
  recognizable fingerprint — I-03 is "committed valueset files held only page 0 of a paged
  `$expand`, so `[Condition: "Cancer"]` missed `C00.0`", not "CMS157". The two misdiagnoses
  (I-06 → I-03, I-09 → I-39) are called out as such, since a wrong first diagnosis is the most
  transferable part of a closed issue.

Also added the missing I-01 row (QI-Core baseline disagreement, 670 cases across 26 measures) and
the missing `baseline` entry in the root-cause class table, and carried forward a latent lead that
was buried inside a Fixed issue: 4 CMS69 Observations still use a malformed
`us-quality-core-observationcancelled` profile (missing hyphen), noted under I-47.

Backfilled `I-XX` cross-references into the five entries above that described a fix without citing
its issue: I-02 (CMS149 port), I-03/I-06 (valueset repair), I-49 (CMS1264 dates),
I-40/I-41/I-42/I-46 (`onc`→`astp` and reference sweep), I-43/I-50/I-51 (CMS347 fixture data).

**Three resolved issues had no entry in this log** and were left uncited rather than attributed
to an unrelated entry: I-44, I-53 and I-54. All three were traced on 2026-09-18 — see the two
entries below. Tracing I-44 is what revealed it had never been fixed at all.

Verified: all 62 ids appear exactly once, no id was lost against the previous revision, every id
cited in `input/cql/` (I-18, I-26, I-28, I-33, I-37, I-55, I-61 — all open) still resolves, and no
`…` truncation remains apart from the deliberate `convert…to days` operator elision in I-57.

**Measures Affected:** none — documentation only. No CQL, FHIR resource, valueset or modelinfo
file was touched.

## Commit the missing CMS871 "Hypoglycemics Treatment Medications" valueset (I-44)

**Problem:** I-44 was recorded as `Fixed` — "committed the external valueset source file" — but
the file had never been committed. `input/cql/CMS871FHIRHHHyper.cql:26` declares
`2.16.840.1.113762.1.4.1196.394`, and `input/vocabulary/valueset/external/` held the sibling
`...1196.393` but nothing for `.394`; no commit on any branch ever touched that path. The engine
was erroring on it at every run:

```text
Unable to locate ValueSet http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113762.1.4.1196.394
```

`Encounter with Hypoglycemic Medication` evaluated `[]` for every patient in the trace, and 3
test cases (`7507debb`, `35719b1a`, `fd579f44`) produced Missing Results across all 5 populations
— 15 of CMS871's 20 failing cells. The remaining 5 belong to a separate, newly-catalogued error
(I-63).

**Fix:** committed
`input/vocabulary/valueset/external/ValueSet-2.16.840.1.113762.1.4.1196.394-20250227.json`,
copied from the IG Publisher terminology cache at
`input-cache/txcache/vs-4d4e1cfc-8e1d-45e5-ae0e-f62f71192e14.json` with exactly one change — `id`
normalised from `2.16.840.1.113762.1.4.1196.394` to `2.16.840.1.113762.1.4.1196.394-20250227`, to
match the `<oid>-<version>` convention every other committed file uses. All other fields verbatim.

**Example:**

```text
before: (no file)
after:  ValueSet-2.16.840.1.113762.1.4.1196.394-20250227.json
        version 20250227, status active, expansion.total = contains = 238
```

**AMA CPT licensing check — passed.** A valueset containing CPT codes must never be committed
with more than 1000 expanded entries; this is an AMA licensing restriction, not a tooling limit.
All 238 codes here are RxNorm (`http://www.nlm.nih.gov/research/umls/rxnorm`) with zero CPT, and
238 is under 1000 regardless. Audited for context: 179 committed valuesets contain CPT, none
exceeds 1000 expanded codes (largest 596). This is the same constraint that scoped I-03's repair
to *non-CPT* valuesets.

No `expansion.parameter` block was synthesised. The cached resource has none, while committed
files typically carry `count: 1000 / offset: 0`; that block is ordinary VSAC `$expand` response
metadata, not the marker of I-03's defect (whose real signature is `contains < total`). Here
`contains == total == 238`, so the expansion is complete.

**Regression guard:** added `scripts/tests/test_valueset_licensing.py`, which asserts (a) no
valueset under `input/vocabulary/valueset/external/` containing CPT codes exceeds 1000 expanded
entries, and (b) `2.16.840.1.113762.1.4.1196.394` is present with a complete, CPT-free expansion.
Test (b) would have caught I-44's phantom "Fixed" status. Full suite: 37 passing.

**Verified 2026-09-18.** The CQL language server's `CQL_DEBUG_MCP_WORKSPACE` was first corrected
(it still pointed at the pre-repo-split `_repo/dqm-content-cms-2025`, which no longer exists),
then the CMS871 suite was re-run from the VS Code extension and the harness re-run
(`extract_population_actual.py`, `compare_results.py`):

- **CMS871 went from 20 failing cells to 10.** Cases `7507debb` and `35719b1a` now pass
  outright — their `errors` arrays are empty where they previously held
  `Unable to locate ValueSet …1196.394`.
- **Exactly one measure moved.** A per-measure diff of `output_results.csv` before and after
  shows CMS871 `20 -> 10` and no change anywhere else, as expected since only
  `CMS871FHIRHHHyper.cql` references this oid. Suite total: 3,817 -> **3,819** of 3,964 test
  cases passing (96.29% -> 96.34%).

**The fix also unmasked a second defect.** Case `fd579f44` did *not* recover. It had reported
only the ValueSet error because that error aborted the library before evaluation reached the
interval expression; with the valueset resolving, it now reports
`Invalid Interval - the ending boundary (0) must be greater than or equal to the starting
boundary (1).` — the same error as `98533ccd`. I-63 therefore covers 2 cases and 10 cells, not
the 1 case and 5 cells originally catalogued, and the earlier estimate that this fix would
recover 15 cells was wrong: it recovers 10. A hard terminology error masks everything downstream
of it, so per-case attribution taken while one is live will understate the other defects present.

**Reconfirmed 2026-09-18 from a full clean re-run.** All `input/tests/results/` content
(including the `.txt` engine traces, which had gone stale mid-verification above) was deleted and
every measure re-run from scratch, then the harness re-run again. CMS871 still shows exactly the
same 10 failing cells (`98533ccd`, `fd579f44`, both on I-63), and the suite-wide total is
byte-identical: 3,819 / 3,964 passing, 374 failing cells across all measures, with zero other
measures changed versus the prior partial re-run. `.txt` traces no longer exist in this repo's
results at all — only the per-case `TestCaseResult-*.json` files, which is what
`extract_population_actual.py` already preferred, so the earlier staleness caveat no longer
applies.

**Measures Affected:** CMS871

## Trace I-53 / I-54 to their upstream commit (no new content change)

**Problem:** I-53 (`.toInterval()` on choice-typed `.effective`/`.performed`) and I-54
(`.onset.toInterval()` used where `.prevalenceInterval()` was meant) were both recorded as
`Fixed` with no entry in this log, so neither traced to a change.

**Fix:** no new change — both trace to upstream commit `6cccf5ce`, authored by Bryn Rhodes,
"Updated incorrect translation of prevalenceInterval to onset.toInterval throughout".
`git log -S'.toInterval'` over `CMS72FHIRSTKAntithromboticDay2.cql` and
`CMS646FHIRIntravesicalBCGTherapy.cql` returns only that commit and `355d04f5` ("Refactored all
dqms"). Note `6cccf5ce` touches 24+ libraries — considerably wider than I-54's 16 tracked sites —
so the catalog's site count understates its reach. Logged here for traceability only.

**Measures Affected:** none newly changed; `6cccf5ce` itself spans 24+ measure libraries.

## Convert raw `authoredOn` before `union` in CMS986's Hospice/Dietitian Referral defines

**Problem:** `"Intervention Hospice Care"` and `"Intervention Dietitian Referral"` each `union` a
`ServiceRequest` branch that `return`s a raw `FHIR.dateTime` (`...authoredOn`, no conversion) with
a `Procedure` branch that already `return`s a converted `System.DateTime`
(`start of ...performed.toInterval()`). The translator resolves the resulting list as
`Choice<FHIR.dateTime, System.DateTime>` and its overly-permissive choice-compatibility check
skips the registered `FHIRHelpers.ToDateTime` conversion, so the consuming `with ... such that X
during day of QualifyingEncounter.hospitalizationWithObservation()` join silently evaluates to
`null` instead of `true` whenever the raw-typed branch is selected — this is the translator defect
`root_cause_status: open` originally identified on CMS108/CMS190 (issue I-61); CMS986 is the first
bare-value (non-tuple) trigger shape for the same mechanism.

**Fix:** added an explicit `.ToDateTime()` fluent call to both raw `authoredOn` branches, matching
I-61's established workaround style, with a "do not remove as redundant" warning comment (I-61's
own investigation had this stripped once and had to restore it).

**Example:**

```cql
// before
return HospiceStatusOrder.authoredOn

// after
return HospiceStatusOrder.authoredOn.ToDateTime()  // I-61: do not remove as "redundant" — raw FHIR.dateTime unioned with an already-converted System.DateTime branch silently nulls in "during"/"such that" without this
```

The identical change was applied to `"Intervention Dietitian Referral"`'s
`DietitianReferralOrder.authoredOn`.

**Verified 2026-09-18** via `mcp__mcp-cql-debug__cql_execute` against fixture
`a4f53b12-e0e3-4faf-8e66-6ce8193a6477`: `"Intervention Hospice Care"` now resolves to
`[2026-02-04T00:00:00.000+00:00]` (plain `System.DateTime`, no more raw-type tag) and
`"Encounters with Hospice during Eligible Encounter"` to `[Encounter(id=f23b0d3c-...)]`, feeding
`"Measure Population Exclusion"` correctly. Confirmed against the harness after re-running the
measure: all six `Measure Population Exclusion` group cells for that case now **PASS**. Suite
total: 3,819 -> **3,820** of 3,964 test cases passing (96.34% -> 96.37%).

**Measures Affected:** CMS986

## Fix CMS816 fixture Encounters missing `subject`; extend the fixture validator's required-field check beyond Task

**Problem:** CMS816 had 12 failing test cases on Initial Population/Denominator (2 also
Numerator), originally filed as I-07 with `content` category and root cause "fixture MR hand-
authors expected values that don't reproduce with the fixture Resources." Direct CQL execution
against test case `05c8cd12-addd-4b94-8f92-da093c556a84` showed the actual cause was narrower:
`["Encounter": "Encounter Inpatient"]` (`input/cql/CMS816FHIRHHHypo.cql:66-70`) returned an empty
list *before* any `where` filter (age/period/status) even applied. The fixture's Encounter
resource had no `subject` element at all — under `context Patient`, a resource with no reference
to the patient is invisible to the retrieve regardless of how correctly its type/status/period
are authored, the same mechanism already known for `Task.for` (I-46), just never checked for on
Encounter/Observation/MedicationAdministration. Every other piece of fixture data (Patient age,
Encounter type/status/period, MedicationAdministration timing) was correctly authored.

Extending the check confirmed this was uniform across all 12 originally-failing cases (control
check against 3 passing cases, whose Encounters all had `subject` set correctly), and **wider
than originally filed**: 17 unique patients / 19 Encounter resources were missing `subject` — 5
more than the 12 in I-07 (`423a396b-...`, `480245d6-...`, `5570227b-...`, `61a026c6-...`,
`cf9c230a-...`), which hadn't produced a visible mismatch because their expected population value
happened to be `0` regardless.

**Fix:** extended `scripts/validate_test_fixtures.py`'s `REQUIRED_PATIENT_FIELDS` presence check
to also cover `Encounter`, `MedicationAdministration`, and `Observation` `subject` (previously
only `Task.for`), adding one dedicated fixer function per resource type
(`apply_encounter_subject_fix`, `apply_medicationadministration_subject_fix`,
`apply_observation_subject_fix`) rather than a single generic one, so the script stays readable.
Renamed the CLI flag from `--fix-task-for` to `--fix-required-fields` to reflect the broader
scope. Ran `--measure CMS816FHIRHHHypo --fix-required-fields --apply`, which injected
`subject: {"reference": "Patient/<folder guid>"}` into all 19 affected Encounter files.
**Verified 2026-09-18**: CMS816FHIRHHHypo now passes all 28 test cases (84/84 population cells).
I-07 moved to `known-issues.md`'s "Resolved — reference patterns" (`content` → `fixture`).

**Not done — known divergence:** the enhanced validator has only been run against
CMS816FHIRHHHypo. A repo-wide `--fix-required-fields` sweep has not been performed, so other
measures' fixtures may carry the same missing-`subject` defect undetected — see
`CONNECTATHON-BREADCRUMBS.md`. (A spot-check against CMS986FHIRMalnutritionScore on 2026-09-18
came back clean — 0 findings — so this is not universal.)

**Example** (`input/tests/measure/CMS816FHIRHHHypo/05c8cd12-.../Encounter-bddf3a47-...json`):

```json
-- before
{
  "resourceType": "Encounter",
  "status": "finished",
  "class": { "code": "IMP", ... },
  ...
}

-- after
{
  "resourceType": "Encounter",
  "status": "finished",
  "subject": { "reference": "Patient/05c8cd12-addd-4b94-8f92-da093c556a84" },
  "class": { "code": "IMP", ... },
  ...
}
```

**Measures Affected:** CMS816
