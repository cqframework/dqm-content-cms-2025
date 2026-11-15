# Defect-Tracking Change Log

Records actual CQL, FHIR resource, valueset, and similar content changes. An
entry may cite the `I-XX` issue it resolves or relates to when one is known,
but this is not required — not every change traces back to a tracked issue.

## Reword the I-61 comments in CMS108 and CMS190

**Problem:** the comment above `LowRiskDatetime: INRLabTest.issued.ToDateTime()` in `"Low Risk
Indicator For VTE"` called I-61 a translator defect "not fixable at this layer". I-61 is now
classified as a content issue: a union of a raw `FHIR.instant` with `System.DateTime` values is a
Choice, and where a `DateTime` is expected the CQL spec casts the Choice (null for the
`FHIR.instant` member) rather than converting it. The QI-Core original has the same unconverted
value.

**Fix:** reworded the explanation in both comments; kept the "do not remove" warning and the
`// Original:` line. Comment only — no CQL logic changed.

**Measures Affected:** CMS108, CMS190

## Remove the retired I-25 comment from CMS156

**Problem:** `medicationRequestPeriodInDays` in `CMS156FHIRHighRiskMedsElderly.cql` carried an
`[I-25]` comment saying `singleton from` on an empty list throws. I-25 is retired: on engine 5.5.0
`singleton from` an empty list returns null, and the cited cases `c409fbc9` and `07f11229` pass
with no `doseAndRate` in their MedicationRequests.

**Fix:** removed the three-line `[I-25]` comment. Comment only — no CQL logic changed.

**Measures Affected:** CMS156

## Correct the commented original lines in CMS71's I-31 workaround

**Problem:** At all three I-31 workaround sites in `CMS71FHIRSTKAnticoagAFFlutter.cql`, the
commented `// original` line read `.prevalenceInteral ( )`. The original call on `main` is
`.prevalenceInterval ( )`, so the comment misrecorded the code it replaced.

**Fix:** corrected the three commented lines to `.prevalenceInterval ( )`. Comment only — no CQL
logic changed.

**Measures Affected:** CMS71

## Record the CMS0334 `c58acff5` fixture repair and remove the stale I-12 comment

**Problem:** CMS0334 case `c58acff5-248b-49c9-b18d-69e4a84a08d9` failed `Group_1:Denominator` and
`Group_1:Denominator Exclusion`. Its `Encounter-9d6ea959-0e00-4cd6-bf60-a90e1d6e90c1.json` named its
delivery diagnosis with the malformed, dangling `reasonReference` `delivery-of-singleton-0997`, so
`CQMCommon.encounterDiagnosis()` found nothing. An earlier entry (below) documented the case as
deliberately left failing. Commit `2ba4c4ded` (2026-10-20) then repaired the fixture, but this
log, the resource-change tracker and the `[I-12]` comment above the CMS0334 `Denominator` define
were not updated. The comment still said the case was expected to keep failing.

**Fix:**

- **Fixture, applied in `2ba4c4ded`:** `reasonReference[0].reference` in
  `input/tests/measure/CMS0334FHIRPCCesareanBirth/c58acff5-248b-49c9-b18d-69e4a84a08d9/Encounter-9d6ea959-0e00-4cd6-bf60-a90e1d6e90c1.json`
  changed from `delivery-of-singleton-0997` to `Condition/8f7d2289-fe66-4bde-8ed8-3223de1da063`, the
  delivery Condition in the same case. `c58acff5` now passes.
- **CQL, applied 2026-11-13:** removed the eleven-line `[I-12]` comment above `define "Denominator"`
  in `CMS0334FHIRPCCesareanBirth.cql`. Comment only; no CQL logic changed. I-12 is closed as fixed.

**Measures Affected:** CMS0334

## Record the CMS135 and `AHAOverall` Condition-retrieve widening (I-77, I-56)

**Problem:** The QI-Core → US Quality Core conversion narrowed two CMS135 Denominator Exception
defines (`Has Diagnosis of Allergy or Intolerance to ACEI or ARB` and `Has Diagnosis of Renal
Failure Due to ACEI`) to `[USQualityCore.ConditionEncounterDiagnosis: …]`. It also narrowed the
shared `AHAOverall` fluent functions `overlapsHeartFailureOutpatientEncounter` and
`overlapsAfterHeartFailureOutpatientEncounter` to a `USQualityCore.ConditionEncounterDiagnosis`
parameter. As a result, problem-list (`ConditionProblemsHealthConcerns`) diagnoses were ignored.
CMS135 `5b7e720f` and `d18e37a6` failed their Denominator Exception (I-77), and CMS144's seven
exclusion diagnoses lost problem-list support (I-56).

**Fix (applied in `6d7b6166`, 2026-10-19; recorded here 2026-11-13):**

- `AHAOverall.cql`: both overlap functions take base `Condition` instead of
  `USQualityCore.ConditionEncounterDiagnosis`.
- `CMS135FHIRACEIorARBorARNIforHF.cql`: the three exception retrieves use base `[Condition: …]`.

Together with the CMS144 I-28 base `[FHIR.Condition: …]` retrieves (`e11830a0`), this restores
problem-list diagnoses:

- CMS135 `5b7e720f` and `d18e37a6` pass.
- Seven CMS144 cases whose Denominator Exception rests only on a problem-list Condition pass:
  `a45954f4`, `b7060d53`, `cdcbc425`, `23f874f8`, `a6c8dee0`, `00cd231f` and `8c717fb3`.

I-77 is reclassified from `implementation` to `migration`. I-77 and I-56 are both closed as fixed.

**Measures Affected:** CMS135, CMS144 (and any measure calling the `AHAOverall` overlap functions)

## Add runtime probe `testProbeCMS71IntervalPrevalence_05` for the 0587a75d eCQM regression (I-82)

**Problem:** The cql-to-elm 5.5.0 upgrade (visible in the running `cqframework.cql-1.0.0`
extension, language server 5.0.0) regressed CMS71 test case `0587a75d-0dcc-4c6b-bfc0-f5727342ec1f`
from PASS to FAIL. The I-31 measure-local `localPrevalenceInterval` workaround is in place. The
compiled ELM is byte-identical between 5.4.0 and 5.5.0 (the 2026-10-29 phase-A diff has a single
`translatorVersion` token as its only difference); `IsEvaluator.kt` is the only engine
runtime-touching source file that changes between `v5.4.0` and `v5.5.0` — PR #1857 (`fb8055df`)
and the consolidation PR #1864 (`1072c579`) flip a null boundary from "not is" to "skip".

We have evidence the targeted `Is` change happens at primitive level: a probe expression
`Interval[@…T00:00:00.000, null) is Interval<DateTime>` returns `false` on the running 5.4.0
language server bundle and `true` on 5.5.0. We do **not** have direct evidence of the exact
runtime path in CMS71 0587a75d that grows from this change; finding it is Phase C. The probe
below isolates the 5.4.0→5.5.0 engine delta on language-level primitives only, so future
runs of the harness can re-confirm the `Is` flip without re-deriving the ELM diffs.

**Fix:** added a throwaway runtime probe library under `input/cql/`. The probe is
language-level only — no `using FHIR`, no `include FHIRHelpers`, no `context Patient`, no
retrieve. It compiles cleanly and runs end-to-end under both 5.4.0 and 5.5.0 via
`workspace/executeCommand {"command":"org.opencds.cqf.cql.ls.executeCql"}` over JSON-RPC.

- `input/cql/testProbeCMS71IntervalPrevalence_05.cql`:
  - Section A. Raw `Interval[@2025-01-01T00:00:00.000, null)` plus its `start of`, `end of`,
    `before`, `on or before`, `is Interval<DateTime>` accessors. The `is …` row is the
    targeted flip: `false` on 5.4.0, `true` on 5.5.0; everything else is identical across
    versions.
  - Section B. Closed-high `Interval[@…, @…]` control. Identical across versions.
  - Section C. CMS71 exact call-site shape via a fluent function — a primitive
    `fluent …(lowBound DateTime) → Interval[lowBound, null)` invoked as a member on a
    `DateTime` literal. All seven probe defines return identical values across versions.
  - Section D. Mirrors the CMS71 call-site metric directly:
    `start of FluentStartProbe before @2026-11-20T08:00:00.000` (the encounter's start in
    the failing fixture) — `true` on both engines.
  - Section E. Closed-null control.
  - Section F. Mirrors the I-31 `localPrevalenceInterval` body shape with the actual
    fixture values (encounter `Encounter-9e5abea1…`, Condition `6998fd2a…` with
    `onsetDateTime: 2026-11-18T06:00:00.000Z`, no `clinicalStatus`, no `abatement`).
    Interval constructions `Interval[start of onset/toInterval(), end of null-abate-interval)`
    are equivalent to the production `Interval[start of onset.toInterval(), null)` since
    `end of null = null` and `null is null = true`. The shape's result interval is
    `[2026-11-18T06:00:00.000, null)` on both engines, and `… starts before @2026-11-20T08:00:00.000`
    evaluates `true` on both engines.

**Verification:** Both engines execute the probe with 0 translation errors. The 23 probe
defines output identical strings except for the three `is Interval<DateTime>` rows
(`OpenNullHighIsIntervalDateTime`, `FluentHighIsIntervalDateTime`, `ClosedNullHighIsIntervalDateTime`),
which all flip `false → true` from 5.4.0 to 5.5.0. This is PR #1857's documented fix.

**Removal condition:** Remove `testProbeCMS71IntervalPrevalence_05.cql` and this entry when
PR #1857 ships in a cql-language-server release older than this one — i.e. once the running
extension is `cqframework.cql ≥ 1.0.0` and the regression on 0587a75d has been traced to a
specific runtime path, or once I-82 closes via `fixed-upstream`. The probe file is throwaway.

The probe itself is documented alongside the [outer-repository dossier I-82](../../dqm-content-cms-2025-ai-support/defect-tracking/issues/I-82.md)
(only when running from this submodule).

**Measures Affected:** none (probe/scaffold only). Tracked for inventory parity under
defect-tracking/issues/cases.csv as `(I-82, CMS71FHIRSTKAnticoagAFFlutter, 0587a75d-0dcc-4c6b-bfc0-f5727342ec1f)`.

## Retire the I-82 engine hypothesis — the 0587a75d FAIL is content-side, traced to commit `46b11c35`

**Phase C result:** end-to-end reproduction with the same LSP `executeCql` driver (referenced in
`out/elm-diff/PHASE-C-REPORT.md` of the outer tooling repo), the same `cql-ls-server-5.0.0.jar`
(engine 5.5.0), the same patient fixture, and the same `"Measurement Period"` parameter
substitution — toggling only the CQL source file between **working-tree** (with the I-31 fix
restored) and **committed HEAD** (post-`46b11c35`) flips the case-0587a75d result between PASS
and FAIL. The engine is innocent.

The actual root cause: commit `46b11c35` "update known issues" (2026-10-22 10:56, see the
"Restore CMS71 I-31 workaround" entry above for the full diff) silently reintroduced the I-31
defect under a typo'd function name. The committed-but-broken CMS71 declares a fluent
`testPrevalenceInteral(condition Condition)` whose else-branch uses the
singleton-query-over-null-source pattern — `(end of condition.abatementInterval()) abatementDate
return …`. For 0587a75d (and 56ae006d) the Condition has no `abatement`, so the source is null,
the query returns null per CQL spec, and the join row drops out. The fix is already in the
working tree (`localPrevalenceInterval` instead of typo'd `testPrevalenceInteral`, with the
`[I-31]` comment block + the `https://jira.hl7.org/browse/FHIR-59708` upstream-ticket line); it
just needs to be committed.

**Fix:** remove the throwaway probe file from the inner submodule (`input/cql/testProbeCMS71IntervalPrevalence_05.cql`)
and the I-82 `cases.csv` row from the outer tooling repo. The I-82 dossier in the outer repo
is left in place but reclassified to `defect_status = "retired"` with `internal = true` and the
`[public]` table dropped, so the engine `Is` boundary change (PR #1857) stays in the audit
trail as a confirmed engine fix that landed in 5.5.0 without user-visible CMS71 impact.

**Verification:** the `[outer] defect-tracking/issues/I-82.md` is updated, the
`outer cases.csv` no longer carries the I-82 row,
`defect-tracking/issues/cases.csv:205` data rows post-cleanup (was 206), and the outer
`python3 scripts/check_generated.py` continues to pass (the inner-repo working-tree CQL restoration
will be committed as its own change-logged entry — see "Restore CMS71 I-31 workaround"
above — at which point this entry becomes redundant and can be folded into it).

**Measures Affected:** none directly. The relevant CMS71FHIRSTKAnticoagAFFlutter cases
(`0587a75d-0dcc-4c6b-bfc0-f5727342ec1f`, `56ae006d-ab1b-428d-8614-2ccd5d962650`) are resolved
by the "Restore CMS71 I-31 workaround" entry above and will pass on the next harness run.

## Record upstream HL7 JIRA FHIR-59708 filing for the FHIRCommon.cql defect behind I-31

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

## Record upstream HL7 JIRA FHIR-59708 filing for the FHIRCommon.cql defect behind I-31

**Problem:** the JIRA ticket for I-31's vendored-library root cause was still
labelled `(pending HL7 JIRA filing)` in the local ticket dossier and the I-31
upstream-ticket entries on the probe libraries, and the inner catalog's open
issues still showed the I-31 row's `Ticket` cell as `—`. As of 2026-10-29 the
JIRA ticket is filed and GitHub
[`cqframework/clinical_quality_language#1879`](https://github.com/cqframework/clinical_quality_language/issues/1879)
is closed (`return` is a projection; null source ⇒ nothing to project ⇒ `null`,
per CQL [Developer's Guide §Non-Retrieve Queries](https://cql.hl7.org/03-developersguide.html#non-retrieve-queries)).
The measure-level `localPrevalenceInterval` workarounds in CMS108 and CMS71
stay in place until the JIRA fix lands.

**Fix:** comment-only / documentation. No CQL, no fixture, no `meta.profile`.

- `input/cql/testProbeSingletonNullReturn.cql` — added the standard
  `[I-31]` upstream-ticket block pointing at HL7 JIRA FHIR-59708
  (`defect-tracking/known-issues.md`).
- `input/cql/testPrevalenceIntervalNullPath.cql` — header now carries the
  `Upstream ticket:` line with the same JIRA URL and links the affected CMS71
  cases. The probe logic is unchanged.
- The I-31 row of the generated open-issues table now links to JIRA
  FHIR-59708 (regenerated from the tooling repo's updated `I-31` front
  matter).
- No upstream-ticket comment was added at the `// [I-31]` workaround
  headers in CMS108 / CMS71: those markers point at `known-issues.md` and
  are removed together with the workaround when the JIRA fix lands, per
  AGENTS.md.

**Measures Affected:** none (documentation / comment changes only; CMS108 and
CMS71 logic unchanged)

## Restore CMS71 I-31 workaround: rename `testPrevalenceInteral` (typo) back to `localPrevalenceInterval`

**Problem:** commit `46b11c35` (2026-10-22 "update known issues") replaced the
working measure-local `localPrevalenceInterval` with a typo'd `testPrevalenceInteral`
(see `nteral` ≠ `nterval` at every call site and at the function definition).
The replacement function body uses the *singleton-query-over-null* shape —
`(end of condition.abatementInterval()) abatementDate return if abatementDate is null then … else …` —
which is the very defect that HL7 JIRA [FHIR-59708](https://jira.hl7.org/browse/FHIR-59708) tracks in
`FHIRCommon.prevalenceInterval()`. Two consequences:

1. CMS71 cases `0587a75d` and `56ae006d` regress from PASS to FAIL on today's
   grid (`output_results.csv:1316,1318,1416,1418`) — exactly the cases the
   workaround was written for.
2. The "Normalize I-31 workaround comments" change-log entry above claims
   *"comment only, no CQL logic changed"*, but the diff in fact changes the
   CQL logic and breaks the workaround. The trailing `[I-31]` header / `Upstream ticket:`
   comment form is the right pattern, but it carried a typo'd CQL change in
   the same commit, so the comment form was preserving a regression rather
   than the working logic.

**Fix:** comment-only at the call sites, plus removing the typo'd function
definition.

- `input/cql/CMS71FHIRSTKAnticoagAFFlutter.cql` — three call sites (lines 62, 79, 93):
  the active line reverts to `.localPrevalenceInterval()` (the working fix from
  commit `1ff292d5` of 2026-10-07), and the typo'd `.testPrevalenceInteral()`
  call is preserved on the line above as `// original`. AGENTS.md bullet
  format preserved.
- `input/cql/CMS71FHIRSTKAnticoagAFFlutter.cql` — the typo'd function
  `testPrevalenceInteral` (`:183-194`) is removed; the working
  `localPrevalenceInterval` definition already exists at `:173` with the
  correct `if/else` body.
- `scripts/comparison/discrepancy_report.md` — new `## I-31 Workaround Note`
  section documenting the workaround and the upstream FHIR-59708 link
  (parallels the existing `## I-28 Workaround Note`).

**Verification:** CMS71 `0587a75d` and `56ae006d` return to PASS on the
`output_results.csv` grid. The unknown function `testPrevalenceInteral` is no
longer referenced from any active CQL. The notebook of "noted for later"
typos in the working tree is replaced by working code.

**Measures Affected:** CMS71FHIRSTKAnticoagAFFlutter (`0587a75d`,
`56ae006d` Denominator / Numerator pass).

## Normalize I-31 workaround comments in CMS108 and CMS71 and record reclassification (engine → vendored)

**Problem:** the measure-local `localPrevalenceInterval` workarounds in `CMS108FHIRVTEProphylaxis.cql`
(line 235) and `CMS71FHIRSTKAnticoagAFFlutter.cql` (lines 58, 70, 79, and function definition)
had replaced the original calls silently without the AGENTS.md-mandated comment blocks.
Additionally, review following upstream discussion on #1879 confirmed that a singleton query over a
null source evaluating to null is spec-mandated CQL behavior (Developer's Guide §Non-Retrieve Queries),
exonerating the engine and identifying the true root cause as a library defect in `FHIRCommon.cql`
(v2.0.0 `:394-405`), reclassifying I-31 from `engine` to `vendored`.

**Fix:** comment only, no CQL logic changed.

- `input/cql/CMS108FHIRVTEProphylaxis.cql` — added AGENTS.md comment block at line 235 leaving the
  original line commented above the replacement, and added an `[I-31]` header above
  `localPrevalenceInterval`.
- `input/cql/CMS71FHIRSTKAnticoagAFFlutter.cql` — added AGENTS.md comment blocks at all three call
  sites (lines 58, 70, 79) leaving original lines commented above replacements, and added an `[I-31]`
  header above `localPrevalenceInterval`.
- Upstream ticket is noted as `(pending)` pending HL7 JIRA ticket filing.

**Measures Affected:** none (documentation/comment changes only; CMS108 and CMS71 logic unchanged)

## Cite the upstream #1857 fix in the I-69 probe and the NHSN `"Normalize Interval"` exposure

**Problem:** the I-69 marker in the inner repo carried no upstream ticket. The probe
`input/cql/testI69IsIntervalNullBound.cql` used the one-line comment form, and the one latent
CMS-side exposure of the defect — `"Normalize Interval"(choice Choice<DateTime, Interval<DateTime>>)`
in `NHSNAcuteCareHospitalMonthlyInitialPopulation1.cql`, whose `is Interval<DateTime>` test rejects
an interval with a null bound — had no marker at all. The engine fix is merged upstream
(`fb8055df`, 2026-10-08) but not yet released, so a reader of the inner repo had no way to find the
upstream report.

**Fix:** comment only, no CQL logic changed.

- `input/cql/testI69IsIntervalNullBound.cql` — the one-line comment became the standard issue
  block: issue id and a one-line summary, the upstream ticket
  (`https://github.com/cqframework/clinical_quality_language/pull/1857`), and the
  affected-test-cases line (none on the CMS side — the probe has no model and no data; the affected
  cases are QI-Core-side, CMS347 `1ba7b147` and CMS646 `ab48e0c0`).
- `input/cql/NHSNAcuteCareHospitalMonthlyInitialPopulation1.cql` — an `[I-69]` marker above
  `"Normalize Interval"` naming the null-boundary hazard and the same upstream ticket. No NHSN
  fixture carries an open-ended period today, so no result changes.
- The filename reference in the "Update upstream ticket-file references" entry below now reads
  `T1857-is-interval-null-bound.md`; the outer tooling repo renamed the ticket file when the
  upstream pull-request number was assigned.

**Measures Affected:** none (comment only; NHSNAcuteCareHospitalMonthlyInitialPopulation1 touched, no logic change)

## Normalize every known-issue comment to the full issue-comment block

**Problem:** the issue-comment convention has two spellings in this repo. The tooling repo's
`AGENTS.md` prescribes the full block — issue id, one-line summary, `Upstream ticket:`,
`Affected test cases:` — and the six most recent exemplars (CMS0334 I-12, CMS135 I-26, CMS145
I-78, CMS871 I-63, CMS144 I-28, CMS156 I-24) all use it. But 74 of the 95 issue-comment sites
still used the older one-line form (`// [I-28] base FHIR.Condition retrieve
(defect-tracking/known-issues.md)`), and 10 sites that carry a known defect had no marker at
all: the I-33 `FHIRHelpers.ToDateTime()` conversions in CMS156, the I-25 `singleton from` sites
in CMS156, the I-26 dementia-medications retrieve in `AdvancedIllnessandFrailty`, the `.ext()`
bypass in CMS108 / CMS190 / CMS68, and the commented-out `recorded(ProcedureNotDone)` overload
in `USQualityCoreCommon`. The same `.ext()` bypass was documented four different ways across
five files. A reader could not tell which upstream ticket a workaround belonged to, or how far
its blast radius reached.

**Fix (comment only, no logic change):** every issue-comment site now carries the full block.

1. **74 legacy sites normalized** — 71 I-28 sites (70 across 30 measures, plus the
   `defectHelper` scaffold) and 3 I-55 sites (CMS996 ×2, CMS646 ×1) gained the two missing
   lines. The issue id and the measure-specific description of each site were left untouched;
   only `Upstream ticket:` and `Affected test cases:` were inserted, directly after the marker
   line and before the existing `// Original:` block. The I-28 ticket is
   `cqframework/clinical_quality_language#1872`; the I-55 ticket is `#1855`. Because I-28 and
   I-55 have no per-case attribution in `cases.csv` by design, the affected-case line uses the
   library-wide form already established by CMS144's I-28 sites: `all N <Measure> cases`, where
   `N` is the measure's distinct test-case count in the harness grid
   (`scripts/comparison/expected_results.csv`) — verified to equal the case-directory count.
   I-28's parenthetical is `(library-wide translate failure)`, I-55's is
   `(library-wide .ext() bypass)`.
2. **8 sites restructured** — in CMS124, CMS138, CMS56, CMS69 (×3) and CMS90 (×2) the marker
   was a trailing comment on a code line (`union ( // [I-28] …`). The marker was moved to a
   standalone comment block immediately above the code line so that every line of the block
   starts `//` in the same column, as the convention requires. Only the trailing comment was
   removed from the code line; no token changed.
3. **10 missing markers added** — I-33 (CMS156 ×2, the `FHIRHelpers.ToDateTime()` conversion
   that makes `sort asc` comparable), I-25 (CMS156, the `singleton from` sites), I-26
   (`AdvancedIllnessandFrailty`, the CMS165 dementia-medications fix-site), I-55 (CMS108,
   CMS190, CMS68 ×2 — the `.ext()` bypass and the measure-local `recordedProcedureNotDone()`),
   and I-18 (`USQualityCoreCommon`, the commented-out overload). The four `.ext()` bypass sites
   that had no issue id now all carry `[I-55]`, matching the three that already did; the
   ambiguity they dodge is named in the summary line (I-18).
4. **Two label deviations fixed** — CMS0334's I-12 and CMS135's I-26 used
   `Affected <Measure> cases:`; both now use the standard `Affected test cases:` label.

Two of the new markers document a defect site rather than a CQL workaround, and are marked as
such in their summary line: I-25's workaround is fixture-side enrichment
(`workaround = "Fixture-side enrichment"`), and I-26 has no CQL workaround at all
(`workaround = "**None (CQL) — fixture-side deflection only**"`). Neither site carries an
`// original` block, because neither replaced any code. I-25 and I-33 have no upstream ticket
in the catalog, so their blocks carry `Upstream ticket: (pending)`.

**Example — legacy site normalized (I-28, one of 74):**

```cql
// before
// [I-28] base FHIR.Condition retrieve (defect-tracking/known-issues.md)
// Original:

// after
// [I-28] base FHIR.Condition retrieve (defect-tracking/known-issues.md)
// Upstream ticket: https://github.com/cqframework/clinical_quality_language/issues/1872
// Affected test cases: all 45 CMS117 cases (library-wide translate failure)
// Original:
```

**Example — trailing marker restructured (I-28, one of 8):**

```cql
// before
    union ( // [I-28] base FHIR.Condition retrieve (defect-tracking/known-issues.md)

// after
    // [I-28] base FHIR.Condition retrieve (defect-tracking/known-issues.md)
    // Upstream ticket: https://github.com/cqframework/clinical_quality_language/issues/1872
    // Affected test cases: all 34 CMS124 cases (library-wide translate failure)
    union (
```

**Example — missing marker added (I-33, CMS156):**

```cql
// before
      where AntipsychoticMedication.authoredOn during "Measurement Period"
      return FHIRHelpers.ToDateTime(AntipsychoticMedication.authoredOn)

// after
      where AntipsychoticMedication.authoredOn during "Measurement Period"
      // [I-33] Raw FHIR.dateTime fed to `sort` throws "Values FHIR.dateTime and FHIR.dateTime are not comparable"
      // Upstream ticket: (pending)
      // Affected test cases: all 59 CMS156 cases (library-wide index-prescription defines)
      // original
      //   return AntipsychoticMedication.authoredOn
      return FHIRHelpers.ToDateTime(AntipsychoticMedication.authoredOn)
```

**Example — `.ext()` bypass given an issue id (I-55, CMS108):**

```cql
// before
          // Original: authoredOn: DeviceNotApplied.performed
          // Proposed: authoredOn: DeviceNotApplied.recorded()
          // ** Proposed solution won't work because of an ambiguous call at runtime between the 2 Procedure recorded **
          // ** fluent functions in USQualityCoreCommon.cql library. See the library file for more details            **
// Issue Reported here: https://github.com/cqframework/clinical_quality_language/issues/1855

// after
          // [I-55] `.ext()` instead of `.recorded()`: recorded(ProcedureNotDone) is ambiguous with recorded(Procedure) - dodges the I-18 overload ambiguity
          // Upstream ticket: https://github.com/cqframework/clinical_quality_language/issues/1855
          // Affected test cases: all 140 CMS108 cases (library-wide .ext() bypass)
          // original
          //   authoredOn: DeviceNotApplied.performed
          // proposed (not applied - ambiguous overload)
          //   authoredOn: DeviceNotApplied.recorded()
```

**Verified 2026-10-21:** comment-only change, so no translation or behavior change — the
compiled ELM and every test result are unchanged. All 95 issue-comment sites now carry an
issue id, an upstream ticket, and an affected-test-cases line.

**Measures Affected:** CMS0334FHIRPCCesareanBirth, CMS108FHIRVTEProphylaxis,
CMS1154ScreeningPrediabetesFHIR, CMS1157FHIRHIVRetention, CMS117FHIRChildImmunStatus,
CMS1188FHIRHIVSTITesting, CMS124FHIRCervicalCancerScreen, CMS128FHIRAntidepressantMgmt,
CMS129FHIRProstCaBoneScanUse, CMS131FHIRDiabetesEyeExam, CMS133FHIRCataracts2040BCVA90Days,
CMS135FHIRACEIorARBorARNIforHF, CMS136FHIRChildADHDMedFollowUp,
CMS138FHIRTobaccoScrnCessation, CMS142FHIRCommWithDrManagingDiab,
CMS143FHIRPOAGOpticNerveEval, CMS153FHIRChlamydiaScreening, CMS155FHIRWgtAssessCounseling,
CMS156FHIRHighRiskMedsElderly, CMS157FHIRPainIntensityQuantified,
CMS159FHIRDepRemissionat12Months, CMS190FHIRVTEProphylaxisICU, CMS314FHIRHIVViralSuppression,
CMS347FHIRStatinPreventionTxCVD, CMS349FHIRHIVScreening, CMS56FHIRFuncStatHipReplacement,
CMS645FHIRBoneDensityPCADTherapy, CMS646FHIRIntravesicalBCGTherapy,
CMS68FHIRDocumentationCurrentMeds, CMS69FHIRPCSBMIScreenAndFollowUp,
CMS75FHIRChildrenDentalDecay, CMS771FHIRUrinarySymptomScoreBPH,
CMS90FHIRFSAforHeartFailure, CMS951FHIRKidneyHealthEval, CMS996FHIRAptTxforSTEMI.
Also edited: the shared libraries `AdvancedIllnessandFrailty.cql` (I-26) and
`USQualityCoreCommon.cql` (I-18), and the `defectHelper.cql` scaffold probe (I-28).

## Ticket I-55 upstream and state the issue-comment convention once

**Problem:** I-55 (`defect_status = workaround-applied`) had an empty `[references]` block in
its dossier, so it had no upstream ticket even though the underlying translator ambiguity is
filed upstream as `cqframework/clinical_quality_language#1855` — the same report cited by its
sibling issues I-18 and I-37, and named in I-55's own status line ("I-18 ambiguity still open
upstream"). Separately, this repo's `AGENTS.md` and `known-issues.md` still documented the old
one-line issue-comment form, which contradicted the full form the tooling repo prescribes and
that the recent exemplars use.

**Fix:**

1. `defect-tracking/issues/I-55.md` gained
   `upstream_issue = "https://github.com/cqframework/clinical_quality_language/issues/1855"`
   in `[references]`, plus a body note naming the ticket. The catalog was regenerated
   (`build_catalog.py`, `generate_engine_issues_doc.py`, `generate_inner_issue_files.py`).
   I-55 has no per-case rows in `cases.csv` by design, so `known_issues.csv` and
   `implementation_issues.csv` are unchanged and the report's `FAIL` → `KNOWN_ISSUE` routing
   is unaffected; only the ticket cell of the Open issues table changes.
2. This repo's `AGENTS.md` and `defect-tracking/known-issues.md` now document the full
   issue-comment block (issue id, one-line summary, `Upstream ticket:`,
   `Affected test cases:`), state that `Upstream ticket:` is required with `(pending)` as the
   placeholder for an unfiled ticket, and state that a replaced original is kept commented out
   immediately above the replacement under an `// original` line.

**Verified 2026-10-21:** `python3 scripts/check_generated.py` reports no drift and
`python3 -m pytest` passes in the tooling repo.

**Measures Affected:** none (issue-catalog and documentation change only).

## Tag the CMS156 `averageDailyDose()` workaround with its issue id (I-24)

**Problem:** the comment above `averageDailyDose()` documented the defect in prose and pointed at
the upstream ticket, but it carried no `I-24` id, no `Upstream ticket:` line, and no affected
test cases, so it did not match the issue-comment convention the other measures follow (CMS871
I-63, CMS145 I-78, CMS144 I-28, CMS135 I-26).

**Fix (comment only, no logic change):** rewrote the comment header in the canonical order —
issue id and a one-line summary, then `Upstream ticket:`, then `Affected test cases:` — and kept
the original function commented out below it. The compiled CQL and every test result are
unchanged; only the provenance of the workaround is now machine-readable. The 2026-10-02 date
was dropped from the comment because no other measure's issue comment carries one; the date
stays in this log.

**Example:**

```cql
// before
// 2026-10-02
// - the function returns grams/second
// - the resultant is so small the value gets truncated and 0.00000000 is returned
// - Issue is related to https://github.com/cqframework/clinical_quality_language/issues/1690
// original

// after
// [I-24] Quantity division across dimensions rounds to zero (`mg / d` normalizes to g/s and rounds to `0E-8`)
// The function returned grams/second; the result was so small it truncated to 0.00000000, so the
// `> 0.125 'mg/d'` and `> 6 'mg/d'` comparisons could never be true.
// Upstream ticket: https://github.com/cqframework/clinical_quality_language/issues/1690
// Affected test cases: 4aa75d19 (GUID prefixes)
// original
```

**Verified 2026-10-21:** comment-only change, so no translation or behavior change. Test case
`4aa75d19` stays green under the I-24 workaround — 12/12 cells `WORKAROUND` in
`scripts/comparison/output_results.csv`.

**Measures Affected:** CMS156FHIRHighRiskMedsElderly

## Surface the I-28 workaround (preferred pattern) in `discrepancy_report.md`

**Problem:** I-28's base-`FHIR.Condition` workaround is applied library-wide in 31 measures, but
the report only surfaces workarounds that have a per-case `known_issues.csv` row. I-28 has none by
design (no individual case is attributable to it), so all 31 measures read as unqualified passes and
both the open translator defect and the pending revert were invisible to a report reader.

**Fix (harness, no content change):** `scripts/compare_results.py` gained an
`## I-28 Workaround Note` section. It is emitted whenever a measure's CQL carries the `[I-28]`
comment marker (`measures_with_cql_marker()`, which also requires a test-case suite, so helper
libraries such as `defectHelper.cql` are excluded). The note lists the **affected measures only**
— never individual test cases, because the workaround is library-wide — and states that the
base-`Condition` retrieve is the preferred CQL pattern while I-28 is open, that it is a workaround
rather than a fix, and that
[cqframework/clinical_quality_language#1872](https://github.com/cqframework/clinical_quality_language/issues/1872)
tracks the union/`Choice` widening defect, so the workaround is to be reverted when that ticket
closes. The measure list comes from the CQL marker convention rather than a hand-maintained list,
so it cannot drift.

**Measures Affected:** no CQL, FHIR resource, or valueset changed by this entry. The section lists
the 31 I-28 measures (CMS144 included) on every run.

## Apply I-28's base `FHIR.Condition` retrieve to CMS144 (7 sites)

**Problem:** `CMS144FHIRHFBetaBlockerForLVSD` failed translation library-wide: all 48 test cases,
all 240 population cells `MISSING` against their fixtures. The translator reported seven unresolved
calls, one per conditional-diagnosis define, all of the form
`Could not resolve call to operator overlapsHeartFailureOutpatientEncounter with signature
(choice<USQualityCore.ConditionEncounterDiagnosis,USQualityCore.ConditionProblemsHealthConcerns>)`.
Each define built its Condition set from a `ConditionProblemsHealthConcerns ∪
ConditionEncounterDiagnosis` union, which types as a `Choice<...>` that the translator will not
widen to base `FHIR.Condition` for the AHA fluents or for `.isVerified()` — I-28.

**Fix:** applied the I-28 workaround at the seven defines: each sibling-profile union is replaced
with a single base `[FHIR.Condition: ...]` retrieve. The 4-way Allergy/Intolerance union is
collapsed to two same-type base retrieves joined by one `union` (the CMS347 pattern), so `union`
never mixes operand types. Semantics are unchanged — the profiles only constrain base `Condition`
retrieves, and every union member is a Condition. The unrelated
`[USQualityCore.AllergyIntolerance...] union [...]` retrieve and the dead local
`isVerified(Choice<...>)` overload were deliberately left alone (CMS143/CMS159 precedent).

**Example** (one of seven sites; the other six are the same substitution):

```before
  exists ( ( [USQualityCore.ConditionProblemsHealthConcerns: "Hypotension"]
      union [USQualityCore.ConditionEncounterDiagnosis: "Hypotension"] ) HypotensionAlias
    where HypotensionAlias.overlapsHeartFailureOutpatientEncounter ( )
      and HypotensionAlias.isVerified ( )
```

```after
  // [I-28] base FHIR.Condition retrieve: sibling-profile union -> Choice<...> cannot widen to
  // FHIR.Condition for the AHA overlap fluent and .isVerified() (defect-tracking/known-issues.md)
  // Upstream ticket: https://github.com/cqframework/clinical_quality_language/issues/1872
  // Affected test cases: all 48 CMS144 cases (library-wide translate failure)
  // Original:
  //   exists ( ( [USQualityCore.ConditionProblemsHealthConcerns: "Hypotension"]
  //       union [USQualityCore.ConditionEncounterDiagnosis: "Hypotension"] ) HypotensionAlias
  exists ( [FHIR.Condition: "Hypotension"] HypotensionAlias
    where HypotensionAlias.overlapsHeartFailureOutpatientEncounter ( )
      and HypotensionAlias.isVerified ( )
```

**Verification:** ELM is clean, and the 48 re-executed test cases score 48/48 cases and 240/240
population cells `PASS` (`Pass Count` 3894 → 3942; CMS144 leaves `Measures with Discrepancies`).
The workaround is removed — restoring the original unions and its comment block together — when
#1872 lands.

**Measures Affected:** CMS144FHIRHFBetaBlockerForLVSD

## Accept HL7 JIRA upstream tickets in `known_issues.csv` (ticket validation + display)

**Problem:** `load_known_issues` accepted only GitHub issue/PR ticket URLs (`GITHUB_TICKET_PATTERN`), so a known issue whose upstream ticket lives in HL7 JIRA — e.g. I-63/I-81, whose FHIRCommon defect is tracked by `FHIR-59691` / `FHIR-59689` — could not be published with its ticket: the loader raised `ValueError`, and the Ticketed column silently fell back to `N/A` for the vendored class, hiding an existing upstream ticket.

**Fix:** `scripts/compare_results.py` now recognizes two ticket shapes via `is_ticket_url()`: the existing GitHub issue/PR pattern and `JIRA_TICKET_PATTERN` (`https://jira.hl7.org/browse/<KEY>-<n>`, e.g. `FHIR-59691`). `ticket_link()` renders a JIRA ticket as `[FHIR-59691](url)` (GitHub stays `[owner/repo#n]`-short-form); `ticket_number()` already returned the trailing path segment, which is the JIRA key. `ticketed_cell()` now renders any recorded ticket as a link regardless of the issue's class — a vendored-library defect is tracked upstream even though no ticket is *owed* for the class — and keeps `N/A` for unticketed non-ticketable classes and `pending` for unticketed engine/translator issues. The outer tooling repo's `generate_inner_issue_files.py` validation mirrors this rule (they are deliberately kept in sync so a published ticket can never make this loader raise).

**Measures Affected:** no CQL change; harness only. First consumer: I-63/I-81 (`CMS871FHIRHHHyper`), whose JIRA tickets now appear in `known_issues.csv` and the Ticketed column.

## Bypass FHIRCommon's sub-24-hour `toDayNumbers` / `daysInPeriod` in CMS871 (I-63, root cause I-81)

**Problem:** CMS871 test cases `98533ccd` (4-hour stay, 15:00→19:00) and `fd579f44` (14-hour stay, 08:00→22:00) aborted before any define evaluated, with all 10 population cells scored `MISSING` (actual) against 1s (expected). The engine asserted
`Invalid Interval - the ending boundary (0) must be greater than or equal to the starting boundary (1).`
The library's `daysInPeriod` bound to the vendored `hl7.fhir.uv.cql` FHIRCommon v2.0.0 copy, whose `toDayNumbers` builds `Interval[1, duration in days between start of period and end of period]`. `duration in days` counts whole 24-hour periods and truncates, so any period shorter than 24 hours yields `Interval[1, 0]` — an invalid interval — and the engine correctly rejects the CQL-built operand. A second, latent defect sits behind it in `daysInPeriod`: its partial-day branch returns `endPeriod = startPeriod`, i.e. the degenerate half-open `Interval[startPeriod, startPeriod)`; that branch is dead code upstream (without a clamp the day index implies ≥24 hours remain) but became reachable the moment the day count was clamped to at least 1, producing the second observed error string
`Invalid Interval - the ending boundary (@2026-11-12T15:00:00.000+00:00) must be greater than or equal to the starting boundary (@2026-11-12T15:00:00.000+00:00).`
Upstream tickets: `FHIR-59691` (entry point for the error) and companion `FHIR-59689`. The library defect is tracked as I-81 (vendored); this entry records the CMS871 workaround (I-63).

**Fix:** measure-local replacements in `input/cql/CMS871FHIRHHHyper.cql`. `localToDayNumbers` null-guards the period and clamps the day count with `Max({1, duration in days between start of period and end of period})`, preserving FHIRCommon's 24-hour-period indexing contract — a `difference in days` + 1 rewrite was rejected because it counts *calendar* days and would re-introduce a reversed interval for overnight stays. `localDaysInPeriod` uses `nextDayStart` / `isLastSegment`: full days stay half-open (`[startPeriod, nextDayStart)` per the upstream docstring), and the final partial segment ends at `end of period` and is **closed** (`[startPeriod, endPeriod]`; a spec-valid point interval when they are equal) so a glucose result at end-of-period still counts. The original `relevantPeriod.daysInPeriod ( )` call is left commented out under the `[I-63]` comment block.

**Example:**

before:
```cql
          relevantDays: relevantPeriod.daysInPeriod ( )
```

after:
```cql
          // [I-63] FHIRCommon v2.0.0 daysInPeriod/toDayNumbers build an invalid Interval[1, 0] for stays shorter than 24 hours (root cause: I-81)
          // Upstream ticket: https://jira.hl7.org/browse/FHIR-59691 (companion: https://jira.hl7.org/browse/FHIR-59689)
          // Affected test cases: 98533ccd, fd579f44 (GUID prefixes)
          // original
          // relevantDays: relevantPeriod.daysInPeriod ( )
          relevantDays: relevantPeriod.localDaysInPeriod ( )
```

plus the two new defines `localToDayNumbers` / `localDaysInPeriod` at the bottom of the library.

**Measures Affected:** CMS871FHIRHHHyper

**Verified:** `cql_execute` probe on `98533ccd` with the case fixtures, 2026-10-20: `Days in Hospitalization` yields `dayPeriod: [2026-11-12T15:00:00.000+00:00, 2026-11-12T19:00:00.000+00:00]` (no crash, no degenerate interval) and populations IP 1 / Den 1 / DenExcl 1 / Num 0 / NumExcl 1. Fixture expectations are IP 1 / Den 1 / DenExcl 1 / Num 0 / NumExcl 0 — the Numerator Exclusion cell (expected 0, actual 1; the CQL's `Numerator Exclusions` is the same union define as `Denominator Exclusions`) is an open follow-up to triage separately from this workaround, not a regression of it.

**Removal condition:** remove both local functions, restore the original call, and delete the comment block in one change-logged edit when FHIRCommon ships the I-81 fix; the outer repo's `cases.csv` rows go at the same time.

## Normalize multi-episode Numerator Exclusion scoring in harness (I-05)

**Problem:** In CMS1017 (and generally for multi-episode encounter-based measures), `validate_measure_population_counts()` in `scripts/extract_population_actual.py` did not constrain `Numerator Exclusion` to encounters that were actually members of the `Numerator`. Under HL7 CQF Measures IG v5.0.0 (Conformance Requirement 3.11), a Numerator Exclusion is defined as an exclusion *from the Numerator* (`Numerator ∩ Numerator Exclusion Criteria`). In multi-encounter patients such as `0dfafc1a` and `5ff2713d`, Encounter 1 meets Denominator Exclusion (Fall POA) and was never in Numerator, while Encounter 2 meets Numerator (inpatient fall with injury not POA). Encounter 1 cannot exclude from a Numerator it was never in. The harness's unconstrained list count emitted `actual = 1` vs `expected = 0`, causing two false FAILs.

**Fix:** Updated `validate_measure_population_counts()` in `scripts/extract_population_actual.py` so that when `numex` is present in multi-episode groups (`denom_count >= 2`), `numex` is filtered against `numer` when both are lists (`len([item for item in numex if item in numer])`), zeroed if `numer` is empty, or bounded by `min(numex_count, numer_count)` when scalar counts occur. Added symmetrical list intersection handling in the `< 2` branch. Added unit tests covering disjoint multi-episode numex, matching numex, empty numer, and scalar bounds. Regenerated inner grid artifacts (`actual_results.csv`, `output_results.csv`, `discrepancy_report.md`), resolving both failing cells in CMS1017FHIRHHFI (now 100% pass: 325/325 cells).

## Document why CMS0334 test case `c58acff5` fails its expected Denominator / Denominator Exclusion (I-12)

**Problem:** CMS0334 case `c58acff5` fails two cells (`Group_1:Denominator` and `Group_1:Denominator
Exclusion`, both expected `1`, both `0`). The case's `Encounter-9d6ea959…` names its delivery
diagnosis with `reasonReference: "delivery-of-singleton-0997"` — not a valid `Type/id` reference, and
no resource in the case carries that id (the `Condition` was re-identified to
`8f7d2289-fe66-4bde-8ed8-3223de1da063` when the case was imported). `CQMCommon.encounterDiagnosis()`
therefore returns nothing, `Encounter With Singleton Delivery` is empty, and both populations
collapse to `0`. The `Denominator` define carried no pointer to the issue.

**Fix:** added a ten-line comment above the `Denominator` define citing the issue (`I-12`), the
mechanism, that the fixture is deliberately left as-is, and the one affected CMS0334 case
(`c58acff5`). Comment only — no CQL logic changed.

```cql
// [I-12] Test case c58acff5 does not reproduce its expected Denominator / Denominator
// Exclusions (both expect 1, both evaluate to 0). CQMCommon.encounterDiagnosis() finds the
// qualifying delivery diagnosis through Encounter.reasonReference, and this fixture's
// reference is the malformed, dangling "delivery-of-singleton-0997": no type prefix, and no
// resource in the case carries that id (the Condition was re-identified to a GUID on import).
// encounterDiagnosis() therefore returns nothing, "Encounter With Singleton Delivery" is
// empty, and both populations collapse to 0. The fixture is deliberately left as-is, so this
// case is expected to keep failing; it is a test-data defect, not a translator or engine
// defect.
// Upstream ticket: N/A (fixture data, not a translator/engine issue)
// Affected CMS0334 cases: c58acff5.
define "Denominator":
```

No upstream ticket applies: tickets are filed for translator/engine defects only, so the comment
records `N/A` (unlike the I-26 comment on CMS135, which carries a real ticket URL).

**Measures Affected:** CMS0334

## Mark the `Ticketed` column `N/A` for known-issue classes no upstream ticket covers

**Problem:** the discrepancy report's `Ticketed` cell read `pending` for *any* failing case covered by
an unticketed known issue, implying a ticket was owed. Only `engine` and `translator` issues can
carry an upstream ticket — of the 79 catalog issues, only 7 do, all in those two classes — so a
`content` / `fixture` / `harness` defect read `pending` forever, and the header sub-row
`— known issue, needs ticket` counted those cases too. I-12 (now `fixture`) made this concrete: its
two cells want `N/A`.

**Fix (harness, no scoring change):**

- `scripts/compare_results.py`:
  - new `TICKETABLE_CLASSES = ("engine", "translator")`;
  - `ticketed_cell()` returns `N/A` for any known issue outside it (the `implementation` case
    already did), and keeps `pending` → ticket link for engine/translator;
  - `generate_comparison_report()` splits the old `— known issue, needs ticket` sub-row into
    `— known issue, needs ticket` (engine/translator, still awaiting one) and
    `— known issue, no ticket expected` (our own content, fixture, or harness);
  - module/docstring and the report's explanatory paragraph updated to match.
- `scripts/tests/test_compare_results_known_issues.py`: the two `I-65` (`content`) assertions now
  expect `N/A`, and a new `test_unticketed_non_ticketable_class_reads_na_and_is_not_needs_ticket`
  pins the new sub-row and its absence for engine/translator.

**Not changed:** the five verdict counts and `KNOWN_ISSUE` scoring are untouched — an unticketed
known issue still leaves its cell `FAIL`, and is still counted as `Unattributed`. Only the label
changes.

**Effect on the grid:** 14 previously `pending` cells across I-05, I-12, I-14, I-15, I-65 and I-79
now read `N/A`; the 2 unticketed engine cases (I-63) and 1 I-33 `workaround reverted` row keep
`pending`, and the header now reads `— known issue, needs ticket 3` +
`— known issue, no ticket expected 14`.

**Measures Affected:** CMS0334, CMS646, CMS771, CMSFHIR844, CMS1017 (reporting only)

## Correct wrong-patient `subject.reference` in five CMS159 / CMS645 / CMS646 fixtures (I-11, residual of I-41)

**Problem:** five fixture resources carried the dangling
`http://GoodHealthcare.com/fhir/Patient/46464646` reference instead of their own case's Patient, so
the patient-scoped retrieve never returned them. In CMS159 that suppressed the expected hospice
exclusion on cases `491f554e` and `96b6579c` (the exact pattern I-41 swept for; these files were
missed by that sweep).

**Change:** repointed each `subject.reference` at the case's own Patient, using the relative
`Patient/<guid>` form the sibling resources already use. Five files, one field each:

- `input/tests/measure/CMS159FHIRDepRemissionat12Months/491f554e-…/ServiceRequest-fd6539a4-….json`
- `input/tests/measure/CMS159FHIRDepRemissionat12Months/96b6579c-…/ServiceRequest-1b3d82ab-….json`
- `input/tests/measure/CMS159FHIRDepRemissionat12Months/2b4c52e3-…/ServiceRequest-ed70e254-….json`
- `input/tests/measure/CMS645FHIRBoneDensityPCADTherapy/4d648e0d-…/Observation-6459f9f6-….json`
- `input/tests/measure/CMS646FHIRIntravesicalBCGTherapy/6e9a1974-…/MedicationAdministration-404ce24c-….json`

Example (CMS159 `491f554e`; the other four are the same substitution with their own GUID):

```json
// before
"subject": {
  "reference": "http://GoodHealthcare.com/fhir/Patient/46464646"
},
// after
"subject": {
  "reference": "Patient/491f554e-e897-40c5-ad2b-0983923df4e8"
},
```

**Observed effect on re-run (2026-10-19, engine re-run with the case folder as the data root):**

- CMS159 `491f554e` / `96b6579c`: `Has Hospice Services …` `false` → `true`,
  `Denominator Exclusions` `null` → `true` — the two expected-`1` DenEx cells now reproduce. The
  paired `Numerator` cells (expected `0`) flip too: the raw `Numerator` define stays `true`
  (follow-up PHQ-9 = 3, `3 < 5`), but `extract_population_actual.py` applies proportion scoring
  and zeroes a single patient's Numerator once their denominator exclusion fires, which yields the
  `0` the fixture expects. All 4 I-11 cells now pass.
- CMS159 `2b4c52e3` (revoked order) and CMS645 `4d648e0d`: no value changed.
- CMS646 `6e9a1974`: `First BCG Administered` `null` → the in-progress BCG administration and
  `Numerator` `false` → `true`, which newly mismatches the fixture MR's expected `0` (no exclusion
  fires for that case, so no scoring zeroes it). Filed as `I-79`; the reference itself is correct.

**Measures Affected:** CMS159FHIRDepRemissionat12Months, CMS645FHIRBoneDensityPCADTherapy, CMS646FHIRIntravesicalBCGTherapy

## Correct `testE15ConditionUnionPrevalence` header's stale Choice-parameter claim (I-28)

**Problem:** the header recorded I-28's early conclusion — *"a Choice is not accepted as a fluent
function parameter type"* — as the reason a shared `prevalenceInterval(Choice<…>)` overload cannot
work. The 2026-10-19 probe series refuted that: FHIRCommon itself declares a Choice-typed fluent
parameter (`toInterval(choice Choice<dateTime, Period, Timing, instant, string, Age, Range>)`) and 24
measure-local `isVerified(Choice<…>)` functions compile.

**Change:** comment-only correction of the header's `CHOICE-OVERLOAD EXPERIMENT` section: the
Choice-parameter claim is retracted, and the real blockers are recorded (an unqualified body call
rebinds to the function itself and dies as a `circular reference` — I-19; a qualified non-fluent call
is rejected; the only viable Choice-overload shape inlines the body with `is`/`as` narrowing, as
`testI28ChoiceArgumentProbeC.cql` demonstrates). The base `[FHIR.Condition]` retrieve remains the
shipped fix and I-28 stays `workaround-applied`. No executable CQL line changed.

**Measures Affected:** none (test scaffold; comment only)

## Add `testI28ChoiceArgumentProbeA` / `testI28ChoiceArgumentProbeC` scaffold probes (I-28)

**Problem:** I-28's recorded conclusion — `testE15ConditionUnionPrevalence.cql:42-44`, *"a Choice is
not accepted as a fluent function parameter type"*, therefore the QI-Core Choice overload cannot be
restored — had been inherited by every downstream write-up and is wrong. Three independent facts
contradict it: FHIRCommon itself declares a Choice-typed fluent parameter
(`FHIRCommon-2.0.0.cql:130`, `toInterval(choice Choice<dateTime, Period, Timing, instant, string,
Age, Range>)`); 24 measure-local `isVerified(Choice<ConditionProblemsHealthConcerns,
ConditionEncounterDiagnosis>)` declarations compile and three of them are actually called (CMS22,
CMS1173, CMS506 — all fully passing); and the parameter list was never the failure point.

**Change:** added two scaffold probe libraries. No measure CQL, fixture or valueset change.

- `testI28ChoiceArgumentProbeA` — PROBE A reproduces the I-28 failure verbatim at `:85`
  (`Could not resolve call to operator prevalenceInterval with signature
  (choice<USQualityCore.ConditionEncounterDiagnosis,USQualityCore.ConditionProblemsHealthConcerns>)`),
  so the string previously preserved only in prose is now reproducible on demand. PROBE B/C show the
  same union-built `Choice<...>` argument binding to locally declared `Choice<...>` parameters. Like
  `testI37RecordedAmbiguousOverload`, it fails to translate on purpose.
- `testI28ChoiceArgumentProbeC` — the union against a locally declared
  `prevalenceInterval(Choice<...>)` whose body **inlines** FHIRCommon's logic with `is`/`as`
  narrowing instead of delegating to it. Zero translation errors, and the body's own calls resolve
  (`toInterval` accepts a 7-member Choice argument, `abatementInterval` binds after narrowing).
  Dispatch: union argument → local overload; base `[FHIR.Condition]` → FHIRCommon (the base-retrieve
  workaround is not hijacked); bare profile argument → local overload.

Findings recorded in `defect-tracking/issues/I-28.md`: a delegating body cannot work in either
direction — an unqualified body call re-binds to the function itself and dies as a **circular
reference** (I-19, reproduced), while a qualified non-fluent call is rejected (`… is a fluent
function and can only be invoked with fluent syntax`). The inlined body is therefore the viable
shape. **Deliberately not applied**: the base `[FHIR.Condition]` workaround stays in force and I-28
stays `workaround-applied`. Two further probes used during triage (an unqualified-body I-19
reproduction and a bare-profile dispatch isolate) were deleted rather than kept.

**Measures Affected:** none (scaffold probes only)

## Report the ticketed known issues that the `WORKAROUND` verdict hides

**Problem:** `cell_outcome` reaches `KNOWN_ISSUE` only from a mismatching cell and `WORKAROUND`
only from a matching one, so the two verdicts partition — but they answer different questions, and
a case can be both. I-78's five CMS145 cases are covered by a ticketed known issue
([cqframework/clinical_quality_language#1872](https://github.com/cqframework/clinical_quality_language/issues/1872))
*and* match only because the measure's `ConditionProblemsHealthConcerns` casts work around it.
The single verdict dropped the ticketed half, so the header read `Known Issue Count (ticketed) 4`
when ten cases were in fact covered by a ticketed issue (4 `KNOWN_ISSUE`, 5 I-78, 1 I-24). A
reader could not tell from the summary that I-78 was ticketed at all — only that six cases were
workaround-held.

**Fix (harness, no scoring change):**

- `scripts/compare_results.py`: `ticketed_known_issue_cases()` collects the `(measure, guid)`
  pairs with a scored cell covered by a ticketed issue; `ticketed_known_issue_coverage_count()`
  and `ticketed_workaround_case_count()` count them through the `KNOWN_ISSUE` and `WORKAROUND`
  verdicts. `generate_comparison_report()` gains a `— covered by a ticketed known issue` sub-row
  under `Workaround Count` and a cross-cutting `Known issues with an upstream ticket` row after
  `Fail Count`, and the console output carries both. Only those two explained verdicts are
  counted, so a stale attribution row on a case that genuinely passes cannot inflate the roll-up.
- `scripts/readme.md`: documents the cross-cutting row and why it is not one of the five counts
  that add up to `Total Test Cases`.
- `scripts/tests/test_compare_results_known_issues.py`: a new ticketed-rollup test pins a grid
  with one workaround-held case, one ticketed failure and one unticketed failure; the two existing
  workaround tests now assert the sub-row's presence and absence.

**Not changed:** the five verdict counts, `Total Test Cases` and
`Resolved (Pass + Implementation + Known Issue)` are all exactly as before. `WORKAROUND` stays out
of `Resolved` deliberately — the defect behind I-78 is open, and reverting the casts turns those
five cases into failures.

**Effect on the grid:** header only. `Workaround Count 6 (0.15%)` gains a
`— covered by a ticketed known issue 6 (0.15%)` sub-row, and a new
`Known issues with an upstream ticket 10 (0.25%)` row states the coverage the two separate counts
obscured. Every workaround case in the grid is ticketed.

**Measures Affected:** CMS145, CMS156 (reporting only)

## Fill in I-78's upstream ticket link in CMS145's workaround comment

**Problem:** the `// [I-78]` comment block above the `ConditionProblemsHealthConcerns` casts in
`CMS145FHIRCADBBlockerTPMIorLVSD.cql` has carried `// Upstream ticket: (pending)` since the casts were
applied on 2026-10-16. An unfilled placeholder is not a finished change, and the upstream ticket now
exists.

**Fix:** the upstream translator ticket was filed on 2026-10-18 as
[cqframework/clinical_quality_language#1872](https://github.com/cqframework/clinical_quality_language/issues/1872)
("Overload resolution ignores subtypes when the argument is a Choice"), so the placeholder line now
carries that URL.

```before
        // [I-78] Choice-typed parameter binds Condition-branch calls to the AllergyIntolerance overload
        // Upstream ticket: (pending)
```

```after
        // [I-78] Choice-typed parameter binds Condition-branch calls to the AllergyIntolerance overload
        // Upstream ticket: https://github.com/cqframework/clinical_quality_language/issues/1872
```

One comment line changed; **no CQL logic changed**. The casts themselves are untouched and stay in
place until #1872 lands — the comment block and the casts are removed together at that point, not
merely because the grid passes.

**Measures Affected:** CMS145

## Score deliberate workarounds as `WORKAROUND` so they stay in the discrepancy report

**Problem:** some issues are worked around in the measure's own CQL — I-78's
`ConditionProblemsHealthConcerns` casts in CMS145, I-24's `System.Quantity` construction in
CMS156. The affected cases then *match* their fixture MeasureReport, and `compare_results.py`
scored them `PASS`. That erased the open defect from `discrepancy_report.md`: CMS145 went from a
listed measure to a clean one, because the only thing left differing in it was an unrelated
implementation issue. A reader could not tell a case that genuinely passes from one that passes
only because a workaround is holding it up — and the report exists precisely to keep open defects
visible, since the workaround is to be reverted when the root cause is fixed.

**Fix (harness, no content change):**

- `scripts/comparison/known_issues.csv` gained a `status` column carrying the issue's
  `defect_status` from the catalog (`suspected`, `confirmed`, `workaround-applied`). It is
  generated, so the column appears on the next publish; hand-edited fixtures without it still
  load, and a blank status is never a workaround.
- `scripts/compare_results.py` scores a *matching* cell whose issue carries `workaround-applied`
  as `WORKAROUND` instead of `PASS`. It counts as neither a pass nor a failure
  (`Workaround Count` in the header, a `Workarounds` row and per-measure column in the summary),
  and it keeps the measure under `## Measures with Discrepancies`, listing each case with
  `I-XX (workaround applied)` and the issue's note.
- A workaround-applied issue whose case is *failing* — reverted, or never applied — leaves the
  cells on the ordinary FAIL path and is labelled `I-XX (workaround reverted)`.

**Effect on the grid:** `Pass Count` 3935 → 3929, `Workaround Count` 0 → 6, `Measures with
Discrepancies` 13 → 14. CMS145 now lists its five I-78 cases under `Workarounds`, and CMS156 its
I-24 case. Nothing else moved; the 18 failures are unchanged.

**Measures Affected:** CMS145FHIRCADBBlockerTPMIorLVSD, CMS156FHIRHighRiskMedsElderly (report
only — no CQL, FHIR resource, or valueset changed by this entry).

## Fix CMS142 / CMS149 fixture resources missing `subject`; add Communication to the fixture validator's required-field check

**Problem:** 5 CMS142 test cases failed on Denominator Exception (expected 1, actual 0; I-39).
Each has two CommunicationNotDone resources: one carries the `category` the
"Medical or Patient Reason for Not Communicating ..." defines retrieve on but has no `subject`,
and the other has a `subject` but no `category`. Under `context Patient` a resource with no
reference to the patient is outside the patient's data, so the
`[CommunicationNotDone: category in ...]` retrieves were correctly empty. The test cases were
authored in MADiE, whose engine treats every resource in a test case as the patient's without
checking references, so the defect never showed there: MADiE's expected results counted the
subject-less resources. The MADiE export for `05f1e2a6` has the same shape, so this was not
introduced on conversion.

A repo-wide scan for resources with no patient reference found 10 Communications in 7 CMS142
test cases (the 5 failing cases plus `03b74242`, `2dd72971`, `28492651`, `afe0cb42`) and one
cancelled Observation in CMS149 (`9e1ffb55`), and nothing else.

**Fix:** added `subject: {"reference": "Patient/<folder guid>"}` to all 11 resources, matching
the population MADiE evaluated. No other field changed. `scripts/validate_test_fixtures.py`'s
`REQUIRED_PATIENT_FIELDS` now covers Communication `subject`, with a dedicated
`apply_communication_subject_fix`. **Verified 2026-10-16**: CMS142FHIRCommWithDrManagingDiab
passes all 32 test cases (128/128 cells, previously 27/32) and CMS149FHIRDementiaCognitiveAssess
still passes all 33.

**Example** (`input/tests/measure/CMS142FHIRCommWithDrManagingDiab/05f1e2a6-.../Communication-12e125bd-...json`):

```json
-- before
{
  "resourceType": "Communication",
  "status": "not-done",
  "statusReason": { ... },
  "category": [ { "coding": [ { "code": "428341000124108", ... } ] } ],
  ...
}

-- after
{
  "resourceType": "Communication",
  "status": "not-done",
  "subject": { "reference": "Patient/05f1e2a6-b317-42bb-827f-993ca3995f5b" },
  "statusReason": { ... },
  "category": [ { "coding": [ { "code": "428341000124108", ... } ] } ],
  ...
}
```

**Measures Affected:** CMS142, CMS149

## Generate the Open issues table and the two issue CSVs from the issue catalog

**Problem:** the Open issues table in `known-issues.md`, `scripts/comparison/known_issues.csv`, and
`scripts/comparison/implementation_issues.csv` were edited by hand alongside the project's internal
issue catalog, so they drifted from it (I-26's ticket was recorded in one place and not the other).
Their wording also compared results against QI-Core, which this repo no longer does.

**Fix:** the three are now generated from the issue catalog and rewritten in user-facing terms,
with no QI-Core comparison. The table gains a Ticket column. Every open issue is listed except the
two QI-Core baseline issues (I-01, I-38), so it now has 35 rows, and the `baseline` class is gone
from the class table. `known_issues.csv` gains I-24's ticket and case; `implementation_issues.csv`
gains the four restored I-76 cases. All of these cases pass, so the report totals don't change.
`AGENTS.md`, `scripts/readme.md`, and the report's wording now say these files are generated.

No CQL, FHIR resource, fixture, or valueset content changed.

**Measures Affected:** none (issue tracking and test-case reporting only)

## Remove the QI-Core comparison from the test-case report; zero Denominator Exception when the Denominator is 0

**Problem:** `scripts/compare_results.py` read an optional copy of the QI-Core project's results
(`scripts/comparison/qicore_actual_results.csv`, 24,714 rows) and added QI-Core columns and a
`## QI-Core Parity` section to the report. QI-Core is no longer changing, and the comparison isn't
needed to use this repo as a US Quality Core example. Separately, `extract_population_actual.py`
could leave Denominator Exception at 1 in a group whose Denominator is 0, when a shared define fires
in every group (I-64).

**Fix:**

- Removed the QI-Core input, the `--qicore-actual` option, the QI-Core columns, and the parity
  section from `compare_results.py`. Deleted `scripts/comparison/qicore_actual_results.csv` and
  `scripts/tests/test_compare_results_qicore.py`; the tests in that file that don't involve QI-Core
  moved to `test_compare_results_report.py` and `test_compare_results_implementation.py`. Removed
  the `baseline` class (QI-Core-side drift) from the classes `known_issues.csv` accepts.
- Added an `if not denom: denexc_count = 0` rule to `validate_measure_population_counts`, with four
  tests. No cell on the current grid changes.
- Updated `scripts/readme.md` and regenerated `scripts/comparison/discrepancy_report.md`.

No CQL, FHIR resource, fixture, or valueset content changed.

**Measures Affected:** none (test-case reporting only)

## Add an I-26 / #1868 tracking comment to CMS135's "Has Medical or Patient Reason for Not Ordering ACEI or ARB or ARNI"

**Problem:** the I-26 engine defect (upstream `cqframework/clinical_quality_language#1868`) crashes the
`[USQualityCore.MedicationNotRequested: medication in "ACE Inhibitor or ARB or ARNI"]` retrieve before
any population evaluates, so the affected CMS135 cases produce no result. The define carried no pointer
to the issue.

**Fix:** added a five-line comment above the define citing the issue (`I-26`), the upstream ticket URL
(`https://github.com/cqframework/clinical_quality_language/issues/1868`), a one-line mechanism summary,
and the three affected CMS135 cases (`c095195c`, `cba5a449`, `ec508dbb`). Comment only — no CQL logic changed. (The generated `input/resources/library/…` base64 copy
of the CQL and the Measure's contained logic definitions are refreshed by the IG Publisher, not here.)

**Measures Affected:** CMS135

## Update upstream ticket-file references to the new `TXXXX-*` naming (doc-only path fix)

**Problem:** the outer tooling repo renamed its upstream ticket files from `T-<slug>.md` to
`TXXXX-<slug>.md` (drafts carry a literal `TXXXX` placeholder until the GitHub issue number is
assigned, then become `T<number>-<slug>.md`). Two inner-repo references still pointed at the old
filenames.

**Fix:** updated the stale references — `known-issues.md` (I-69 →
`T1857-is-interval-null-bound.md`) and this file (`TXXXX-prevalence-interval-null-singleton-return.md`).
No CQL, FHIR resource, fixture, or valueset content changed.

**Measures Affected:** none (documentation references only)

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

**Verified 2026-09-18.** The CQL MCP server's workspace setting was first corrected
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

**Verified 2026-09-18** via `cql_execute` against fixture
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

## Remove the ambiguous `recorded(ProcedureNotDone)` overload; bypass it in CMS68 / CMS108 / CMS190 (I-37, I-18)

**Problem:** `USQualityCoreCommon.cql` declared two fluent overloads, `recorded(procedure Procedure)`
and `recorded(procedureNotDone ProcedureNotDone)`. The two profiles are distinct CQL types, so the
translator accepts both, but it compiles them to the same ELM signature (`{http://hl7.org/fhir}Procedure`).
At runtime the engine finds two identical candidates and throws
`Ambiguous call to operator 'recorded(...)' in library 'USQualityCoreCommon'`. The throw is uncaught,
so the whole library evaluates nothing (CMS68 `f2e2e1c0`: Missing Results across all 4 populations;
CMS190: every case reaching `DeviceNotApplied.recorded()`). This is a translator defect, reported
upstream as
[cqframework/clinical_quality_language#1855](https://github.com/cqframework/clinical_quality_language/issues/1855)
(same mechanism as the older, still-open #1435).

**Fix:** a content-side bypass until the translator is fixed. Each call site cites #1855 in a comment.

- **`USQualityCoreCommon.cql`** (shared library): commented out the `recorded(ProcedureNotDone)`
  overload, leaving only `recorded(Procedure)`, with a dated note explaining why. Also corrected two
  copy-pasted `@description` comments (the `recorded` and `reasonRefused` functions both claimed to
  read the recorded extension of a Medication Administration Not Done).
- **`CMS68FHIRDocumentationCurrentMeds.cql`**: `"Denominator Exceptions"` now calls a new
  measure-local fluent function with a unique name, `recordedProcedureNotDone()`, so there is no
  overload to resolve.
- **`CMS108FHIRVTEProphylaxis.cql`** and **`CMS190FHIRVTEProphylaxisICU.cql`**:
  `"No Mechanical VTE Prophylaxis Performed Or Ordered"` reads the `us-quality-core-recorded`
  extension directly via `.ext()`. CMS108 already did this; CMS190 was calling `.recorded()`.

**Example** (CMS68 `"Denominator Exceptions"`):

```cql
// before
such that MedicationsNotDocumented.recorded ( ) during day of QualifyingEncounter.period

// after
such that MedicationsNotDocumented.recordedProcedureNotDone() during day of QualifyingEncounter.period

define fluent function recordedProcedureNotDone(procedureNotDone ProcedureNotDone):
  procedureNotDone.ext('http://fhir.org/guides/astp/us-quality-core/StructureDefinition/us-quality-core-recorded').value as FHIR.dateTime
```

**Verified 2026-10-02** against the harness output committed on this branch
(`scripts/comparison/output_results.csv`), compared with `main`. Failing test cases:
CMS68 1 → **0** (`f2e2e1c0` passes all 4 populations), CMS190 11 → **1**, CMS108 4 → **3**.
No `TestCaseResult-*.json` under `input/tests/results/` still carries an `Ambiguous call` error,
so the remaining CMS108 / CMS190 failures are a different cause. I-37 moves to `Worked around` (not
`Fixed`: the translator defect is still live upstream).

**Measures Affected:** CMS68, CMS108, CMS190 (plus the shared library `USQualityCoreCommon.cql`)
## Build CMS156 `averageDailyDose()` in `mg/d` directly instead of dividing Quantities (I-24)

**Problem:** test case `4aa75d19` has two `MedicationRequest`s that should satisfy
`"Same High Risk Medications Ordered on Different Days"`, but the Group 1 and Group 3 Numerators
came out `0` against an expected `1`. `averageDailyDose()` divided a total-dose Quantity by a
`System.Quantity { value: DaysSupplied, unit: 'd' }`. The engine normalizes a cross-dimension
Quantity division to SI base units (g/s), and the result is so small that it rounds to `0E-8` at
8 decimal places. The `> 0.125 'mg/d'` (digoxin) and `> 6 'mg/d'` (doxepin) comparisons can then
never be true. This is engine issue I-24. The case had been misattributed to I-15 (fixture
authoring mismatch).

**Fix:** compute the total dose as a `let`, then build the result as a Quantity in `mg/d` from
plain decimal division, which avoids the engine's unit normalization. Also added a
`DaysSupplied > 0` guard so the decimal division can't divide by zero. The original function is
kept as a comment above the new one.

**Example:**

```cql
// before
DaysSupplied: Order.medicationRequestPeriodInDays ( )
return if DaysSupplied is not null
  and ( ... ) then ( ( Order.dispenseRequest.quantity * MedicationStrength ) / System.Quantity { value: DaysSupplied, unit: 'd' } )
  else null

// after
DaysSupplied: Order.medicationRequestPeriodInDays ( ),
TotalDose: Order.dispenseRequest.quantity * MedicationStrength
return if DaysSupplied is not null and DaysSupplied > 0
  and ( ... ) then System.Quantity { value: TotalDose.value / DaysSupplied, unit: 'mg/d' }
  else null
```

**Verified 2026-10-02** against the harness output on this branch
(`scripts/comparison/output_results.csv`), compared with `main`: `4aa75d19` Group 1 and Group 3
Numerators now **PASS** (`1`/`1`). CMS156 goes from 2 failing cells to **0** (all 708 cells pass).

**Measures Affected:** CMS156
## Replace FHIRCommon `prevalenceInterval()` with a local `if/else` form in CMS108's prior-VTE branch

**Problem:** `FHIRCommon.prevalenceInterval()` (FHIRCommon 2.0.0, `:400-405`) computes its
non-active branch as a single-value query —
`(end of condition.abatementInterval()) abatementDate return if abatementDate is null then … else …`.
The engine evaluates a single-value query whose source is null to `null` without running its
`return` clause (I-31), so when a Condition has no `abatement[x]` the function returns `null`
instead of an open-ended interval. Every inactive/remission/resolved VTE Condition in the CMS108 fixtures has no
abatement, so `"Encounter With Prior Or Present Diagnosis Of Atrial Fibrillation Or Prior Diagnosis
Of VTE"`'s prior-VTE branch could never match. The intended `Interval[onset, null)` would not have
been right either: a null *open* high bound means the end is unknown (so `end of` is null and
`overlaps` is null), while a null *closed* high bound means no end (the end is the maximum DateTime). Confirmed with the
`testProbeSingletonNullReturn` scaffold probe (translator/engine 5.4.0). Upstream ticket:
`defect-tracking/tickets/TXXXX-prevalence-interval-null-singleton-return.md` (tooling repo).

**Fix:** added a measure-local `localPrevalenceInterval(Condition)` fluent function that uses
`if/else` instead of the singleton query and an open null high bound (`null)`; the consumers
only read the start, so the open bound is sufficient), and switched
the prior-VTE call site to it with `starts before start of QualifyingEncounter.period` (previously
`prevalenceInterval() before start of …`). The AF branch (`:221`) still uses
`FHIRCommon.prevalenceInterval()`. Re-ran cases `d9b7ffa9`, `dd5a1e46`, `33d162ce` via
`cql_execute`: Initial Population / Denominator / Numerator = 1, Denominator Exclusion = 0, matching
their MeasureReports.

Also added the scaffold probe library `input/cql/testProbeSingletonNullReturn.cql` (System types
only, no includes, no fixtures) as the reproducer for the upstream ticket, and
`input/cql/testPrevalenceIntervalNullPath.cql` (CMS71 "History of Atrial Ablation" isolation:
profile retrieve vs `FHIRCommon.prevalenceInterval()` vs the local closed form). Neither is
registered as a Library resource.

**Measures Affected:** CMS108

**Example** (`input/cql/CMS108FHIRVTEProphylaxis.cql`):

```cql
-- before
            and VTEDiagnosis.prevalenceInterval ( ) before start of QualifyingEncounter.period

-- after
            and VTEDiagnosis.localPrevalenceInterval() starts before start of QualifyingEncounter.period

define fluent function localPrevalenceInterval(condition Condition):
  if condition.clinicalStatus ~ FHIRCommon."active"
    or condition.clinicalStatus ~ FHIRCommon."recurrence"
    or condition.clinicalStatus ~ FHIRCommon."relapse" then
    Interval[start of condition.onset.toInterval(), end of condition.abatementInterval()]
  else if end of condition.abatementInterval() is null then
    Interval[start of condition.onset.toInterval(), null)
  else
    Interval[start of condition.onset.toInterval(), end of condition.abatementInterval()]
```

## Add a patient-level control to the `testE11MedicationReference` scaffold probe (I-26)

**Problem:** the probe's FAILING and PASSING defines were the same retrieve,
`[FHIR.MedicationRequest: "Rivastigmine"]`, run over one patient that carries both a
`medicationReference` and a `medicationCodeableConcept` MedicationRequest. The
`Unable to extract codes from fhirType Reference` crash aborts the whole library, so the PASSING
define never produced a result and the probe had no working control.

**Fix:** added a control patient whose only MedicationRequest uses `medicationCodeableConcept`, and
collapsed the two identical defines into one, `"Rivastigmine MedicationRequests"`. Run with
`cql_execute`, each patient with its data path scoped to its own folder:

- `62577993` (repro): `Unable to extract codes from fhirType Reference`
- `7998aa53` (control): `[MedicationRequest(id=d8716091-…)]`

With the data path at the measure folder, the control also crashes; the CQL comment records this.
Scaffold probe only (`test*`), so no `CMS*` measure is affected.

New fixture files (`input/tests/measure/testE11MedicationReference/7998aa53-f2dc-4cb6-b0f7-8dc726506601/`):
`Patient-7998aa53-f2dc-4cb6-b0f7-8dc726506601.json`,
`MedicationRequest-d8716091-48d1-43fe-942d-8535ef8c0b75.json`.

**Measures Affected:** none (scaffold probe `testE11MedicationReference`)

**Example** (`input/cql/testE11MedicationReference.cql`):

```cql
-- before
define "FAILING Reference-Only Medication":
  [FHIR.MedicationRequest: "Rivastigmine"]

define "PASSING CodeableConcept Medication":
  [FHIR.MedicationRequest: "Rivastigmine"]

-- after
define "Rivastigmine MedicationRequests":
  [FHIR.MedicationRequest: "Rivastigmine"]
```

## Use the `notDoneReason()` fluent function for CMS2's depression-screening exceptions (I-60)

**Problem:** CMS2's negation defines read `.notDoneReason` as an element of
`ObservationCancelled`, the way the QI-Core version does. US Quality Core has no such element: it
carries the reason in the `us-quality-core-notDoneReason` extension. The two defines,
`"Medical or Patient Reason for Not Screening Adolescent for Depression"` and
`"… Adult for Depression"`, had been commented out behind TODOs, and `"Denominator Exceptions"` was
hardcoded to `false`. All 8 cases expecting a Denominator Exception came back 0
(`Group_1:Denominator Exception` 1→0), while QI-Core passed them.

**Fix:** read the reason through the `notDoneReason()` fluent function
(`USQualityCoreCommon.cql:158`, which returns the `us-quality-core-notDoneReason` extension value
as a `CodeableConcept`) instead of the `.notDoneReason` element, and restore the three defines on
`[USQualityCore.ObservationCancelled: …]`. Committed as `e2813a63`. CMS2 now has 0 failing cells on
the 2026-10-07 grid and matches QI-Core on all 8 cases.

**Measures Affected:** CMS2

**Example** (`input/cql/CMS2FHIRPCSDepScreenAndFollowUp.cql`):

```cql
-- before
define "Denominator Exceptions":
  false
/*
TODO: Need to reassess how we are representing given no ObservationCancelled profile
  ( exists "Medical or Patient Reason for Not Screening Adolescent for Depression"
  ...
*/

    where ( NoAdolescentScreen.notDoneReason ~ "Depression screening declined (situation)"
        or NoAdolescentScreen.notDoneReason in "Medical Reason"
    )

-- after
define "Denominator Exceptions":
  ( exists "Medical or Patient Reason for Not Screening Adolescent for Depression"
      and not "Has Adolescent Depression Screening"
  )
    or ( exists "Medical or Patient Reason for Not Screening Adult for Depression"
        and not "Has Adult Depression Screening"
    )

    where ( NoAdolescentScreen.notDoneReason() ~ "Depression screening declined (situation)"
        or NoAdolescentScreen.notDoneReason() in "Medical Reason"
    )
```

The same `notDoneReason` → `notDoneReason()` change applies in the Adult define.

## Qualify CMS22's `ServiceRequest` retrieves as `USQualityCore.ServiceRequest` (I-52)

**Problem:** CMS22's positive intervention retrieves used the unqualified `[ServiceRequest: …]` type.
Cases `f9417a57` and `c41f9946` over-fired the Numerator (1→0 expected) because a declined order's code
also matched a positive intervention valueset; QI-Core passed both. These were the last 2 open CMS22
cases, filed under I-52.

**Fix:** qualified every `ServiceRequest` retrieve in the measure as `[USQualityCore.ServiceRequest: …]`,
12 retrieve sites across 6 defines. No `doNotPerform` filter was needed. CMS22 now has 0 failing cells on
the 2026-10-07 grid and matches QI-Core.

**Measures Affected:** CMS22

**Example** (`input/cql/CMS22FHIRPCSBPScreeningFollowUp.cql`; the same change at every
`ServiceRequest` retrieve):

```cql
-- before
define "Follow up with Rescreen Within 6 Months":
  [ServiceRequest: "Follow Up Within 6 Months"] FollowUp
    where FollowUp.intent ~ 'order'

-- after
define "Follow up with Rescreen Within 6 Months":
  [USQualityCore.ServiceRequest: "Follow Up Within 6 Months"] FollowUp
    where FollowUp.intent ~ 'order'
```
## Fix CMS190 `.recorded()` ambiguous-overload regression (I-37)

**Problem:** commit `f0e8eb172` ("fixes for debugged measures", 2026-09-18) applied the I-18
`.ext()` bypass for the ambiguous `recorded(Procedure)`/`recorded(ProcedureNotDone)` overload
(engine issue I-37) correctly to CMS108's `DeviceNotApplied.recorded()` call, but for the
identical `ProcedureNotDone`-derived construct in `"No Mechanical VTE Prophylaxis Performed Or
Ordered"`, pasted the explanatory comment while leaving the buggy `.recorded()` line in place.
This threw the uncaught `"Ambiguous call to operator 'recorded(...)'"` engine error for all 10
`CMS190FHIRVTEProphylaxisICU` Group_1 test cases, producing Missing Results across all 4
population cells for each — these had gone unattributed in the discrepancy report.

**Fix:** applied the same `.ext('http://fhir.org/guides/astp/us-quality-core/StructureDefinition/us-quality-core-recorded').value as FHIR.dateTime`
bypass already verified on CMS108.

**Example** (`input/cql/CMS190FHIRVTEProphylaxisICU.cql`):

```
-- before
authoredOn: DeviceNotApplied.recorded()

-- after
authoredOn: DeviceNotApplied.ext('http://fhir.org/guides/astp/us-quality-core/StructureDefinition/us-quality-core-recorded').value as FHIR.dateTime
```

**Measures Affected:** CMS190

## Use a measure-local `localPrevalenceInterval` in CMS71, as in CMS108 (I-31)

**Problem:** CMS71 had the same `FHIRCommon.prevalenceInterval()` failure as CMS108. Its
"History of Atrial Ablation" Conditions have no `clinicalStatus` and no abatement, so they take the
non-active branch. There the singleton query `(end of abatementInterval()) abatementDate return …`
evaluates to `null` without running `return`, and `prevalenceInterval() starts before start of
IschemicStrokeEncounter.period` is never true. `"Encounter With A History Of Atrial Ablation"` was
`[]`, so cases `0587a75d` and `56ae006d` lost `Denominator` and `Numerator` (1→0) while QI-Core
passed them. Confirmed with `input/cql/testPrevalenceIntervalNullPath.cql`: the profile retrieves
return the Condition, and only the interval is null.

**Fix:** added the same measure-local `localPrevalenceInterval(Condition)` fluent function used in
CMS108 and switched all three CMS71 call sites to it: the two "History of Atrial Ablation" joins
(`ConditionProblemsHealthConcerns` and `ConditionEncounterDiagnosis`) and the AF/Flutter join. The
function returns an open `null)` high bound when there is no abatement end; every CMS71 consumer only
reads the start (`starts before`, `starts on or before`), so that is sufficient. CMS71 has 0 failing
cells on the 2026-10-07 consolidated grid and matches QI-Core.

**Measures Affected:** CMS71

**Example** (`input/cql/CMS71FHIRSTKAnticoagAFFlutter.cql`, same change at all three call sites):

```cql
-- before
            and AtrialAblationDiagnosis.prevalenceInterval ( ) starts before start of IschemicStrokeEncounter.period

-- after
            and AtrialAblationDiagnosis.localPrevalenceInterval ( ) starts before start of IschemicStrokeEncounter.period

define fluent function localPrevalenceInterval(condition Condition):
  if condition.clinicalStatus ~ FHIRCommon."active"
    or condition.clinicalStatus ~ FHIRCommon."recurrence"
    or condition.clinicalStatus ~ FHIRCommon."relapse" then
    Interval[start of condition.onset.toInterval(), end of condition.abatementInterval()]
  else if end of condition.abatementInterval() is null then
    Interval[start of condition.onset.toInterval(), null)
  else
    Interval[start of condition.onset.toInterval(), end of condition.abatementInterval()]
```

## Fix CMS177 `85e6225c` fixture Encounter date and profile (I-66)

**Problem:** test case `85e6225c` ("Patient with psychotherapy encounter before MP") had its Encounter
dated 2026-02-11, inside the 2026 measurement period, and no `meta.profile`. Every other inclusion
criterion is met, so CMS counted it (`Initial Population` / `Denominator` 0→1). The MADiE source has
the encounter on 2025-02-11 with a `qicore-encounter` profile. QI-Core returned the expected 0 only
because its Encounter retrieve requires that profile.

**Fix:** restored the encounter date to 2025-02-11 and set `meta.profile` to `us-quality-core-encounter`.
Verified with `cql_execute`: Initial Population, Denominator and Numerator are all 0, matching the
MeasureReport and QI-Core.

**Measures Affected:** CMS177

**Example** (`input/tests/measure/CMS177FHIRChildMDDSuicideAssmt/85e6225c-a9bb-4338-a228-297564e38c4d/Encounter-3f0ce31f-7c94-4e7d-bf1f-31d40a7defb7.json`):

```json
-- before
  "id": "3f0ce31f-7c94-4e7d-bf1f-31d40a7defb7",
  "status": "finished",
  ...
  "period": {
    "start": "2026-02-11T08:00:00.000+00:00",
    "end": "2026-02-11T08:15:00.000+00:00"
  },

-- after
  "id": "3f0ce31f-7c94-4e7d-bf1f-31d40a7defb7",
  "meta": {
    "profile": [ "http://fhir.org/guides/astp/us-quality-core/StructureDefinition/us-quality-core-encounter" ]
  },
  "status": "finished",
  ...
  "period": {
    "start": "2025-02-11T08:00:00.000+00:00",
    "end": "2025-02-11T08:15:00.000+00:00"
  },
```

## Add `testI69IsIntervalNullBound` scaffold probe; attribute CMS646 `ab48e0c0` to I-70

**Problem:** CMS646 `ab48e0c0` showed as a regression against the QI-Core baseline
(`Group_1:Numerator` QI-Core 0 → CMS 1). Stepping through the QI-Core side showed
`condition.onset.toInterval()` returning null for the Condition's start-only `onsetPeriod`, with
`choice` null inside `toInterval`.

**Change:** added the engine-only `testI69IsIntervalNullBound` scaffold probe (System types only, no
model or data). On translator/engine 5.4.0 it confirms I-69 (`is Interval<T>` is false for an
interval with a null bound). It also shows a second entry point: an open-ended interval passed to a
`Choice<DateTime, Interval<DateTime>>` parameter arrives as null, because the call-site `As` uses
the same type test. The CMS result (1) is what the logic produces; QI-Core on engine 4.9.0 also
gives 1. The fixture's expected 0 can't be produced by the measure logic, so the case is
attributed to the new I-70 (`implementation`, steward to fix). No measure CQL or fixture change.

**Measures Affected:** none (scaffold probe only; CMS646 attribution change)

## Restore `recorded` timing on CMS996 negation Denominator Exceptions

**Problem:** CMS996 cases `7edab122`, `ccc7deaf`, `60823d79`, and `8bb7c40b` returned
`Group_1:Denominator Exception` 0 where QI-Core and the fixture give 1. QI-Core times both negation
defines with `.recorded`. The 2026-04-07 refactor (`355d04f5`) used `.performed` and `.effective`
instead (I-55):

- `ProcedureNotDone.performed` never has a value. The fixtures carry only a
  `data-absent-reason = not-performed` extension, so `performed during` is null.
- `MedicationAdministrationNotDone.effective` is a start-only `effectivePeriod`. FHIRHelpers turns a
  null `end` into a closed null boundary, so the interval runs to the end of time and is never
  `during` the ED encounter.

**Change:** both defines now compare the `us-quality-core-recorded` extension, as QI-Core does.
The PCI define reads it with `.ext()`, because `recorded(ProcedureNotDone)` is ambiguous with
`recorded(Procedure)` (I-18). The fibrinolytic define uses `USQualityCoreCommon.recorded()`. Ran
the 4 cases with `cql_execute` (translator/engine 5.4.0): each now returns its ED encounter in
`Denominator Exceptions`, with no diagnostics.

### Example

```cql
-- before
        and PCINotDone.performed during EDwSTEMI.period
        and FibrinolyticNoMed.effective during EDwSTEMI.period

-- after
        and ( PCINotDone.ext('http://fhir.org/guides/astp/us-quality-core/StructureDefinition/us-quality-core-recorded').value as FHIR.dateTime ) during EDwSTEMI.period
        and FibrinolyticNoMed.recorded() during EDwSTEMI.period
```

**Measures Affected:** CMS996

## Restore `recorded` timing on the CMS646 BCG-not-available Denominator Exception

**Problem:** CMS646 case `e648fa70` returned `Group_1:Denominator Exception` 0 where QI-Core and the
fixture give 1. QI-Core times `"BCG Not Available Within 6 Months After Bladder Cancer Staging"` with
`BCGNotGiven.recorded`. The 2026-04-07 refactor (`355d04f5`) used `BCGNotGiven.effective` instead
(I-55). The timing phrase `6 months or less after day of` needs a point, so the translator compiles
the `Choice<dateTime, Period>` as `FHIRHelpers.ToDateTime(effective as FHIR.dateTime)`. The fixture
carries an `effectivePeriod`, so the cast is null and the `such that` evaluates null.

**Change:** the define now compares `BCGNotGiven.recorded()` (the `us-quality-core-recorded`
extension), as QI-Core does. `recorded(MedicationAdministrationNotDone)` has no sibling-profile
overload, so I-18 doesn't apply. Ran `e648fa70` and the two other CMS646 not-done BCG cases with
`cql_execute` (translator/engine 5.4.0): `e648fa70` now returns Denominator Exception true;
`40ac7a7f` and `e2117038` stay false (expected 0), with no diagnostics.

### Example

```cql
-- before
      such that BCGNotGiven.effective 6 months or less after day of start of FirstBladderCancerStaging.performed.toInterval ( )

-- after
      such that BCGNotGiven.recorded() 6 months or less after day of start of FirstBladderCancerStaging.performed.toInterval ( )
```

**Measures Affected:** CMS646

## Link the stroke Claims to their inpatient encounter in three CMS72 / CMS104 fixtures

**Problem:** `TJC."Ischemic Stroke Encounter"` requires a principal diagnosis, which
`CQMCommon.claimDiagnosis()` reads only from a Claim whose `item.encounter` references the encounter
and whose `item.diagnosisSequence` includes the diagnosis sequence. Three fixtures had a Claim that
couldn't match, so the patient never reached the Initial Population (CMS and QI-Core both 0, expected
1):

- CMS72 `e126cdec`: `item.encounter` was `Encounter//5c954893b848462de0ae623a`, which matches no
  encounter in the fixture.
- CMS104 `0b1aa8ee` and `e84c89f7`: `item` had no `encounter` and no `diagnosisSequence`.

**Change:** pointed each Claim's `item.encounter` at the fixture's inpatient encounter
(`dec37c2b`, `2be30658`, `78fdcacc`) and added `diagnosisSequence: [1]` to the two CMS104 Claims. The
diagnosis codes are unchanged (`I63.00`, and SNOMED `111297002`, which is in "Ischemic Stroke"). Ran
the three cases with `cql_execute` (translator/engine 5.4.0): every population now matches the
fixture MeasureReport (`e126cdec` 1/1/1/0/0, `0b1aa8ee` 1/1/1/0/0, `e84c89f7` 1/1/0/0/1 for
IP/Denom/DenExcl/Numer/DenExcep), with no diagnostics. The QI-Core fixtures were deliberately left
unchanged.

**Verified 2026-10-09** after re-running CMS72 and CMS104 in the CQL plugin and regenerating the
grid: exactly these 9 cells changed (0 → 1, now equal to expected), no other cell in the 23,722-cell
grid moved, and the three `TestCaseResult` files carry no errors. Overall pass rate 3911 → 3914 of
3964 test cases (98.66% → 98.74%). The cells now differ from the QI-Core baseline, which stays 0
(I-38), so they count as CMS-better, not as a regression. Tracked as I-74 (`fixture`, Fixed); the
seven multi-encounter cases with the same Claim template are I-73 and were not changed.

### Example

```jsonc
// before (CMS72 e126cdec)
"encounter": [ { "reference": "Encounter//5c954893b848462de0ae623a" } ]

// after
"encounter": [ { "reference": "Encounter/dec37c2b-06f6-4871-818c-99accd7f863e" } ]
```

**Measures Affected:** CMS72, CMS104

## Score implementation issues as resolved in `compare_results.py`; attribute I-73 and I-75

**Problem:** a test case listed in `scripts/comparison/implementation_issues.csv` (class
`implementation`: the steward's test data or expectation can't produce the fixture result) was kept
out of the QI-Core parity buckets but still scored `FAIL`. An implementation note explains the
failure as well as a match does, so those cases should count as resolved.

**Change:**

- `scripts/compare_results.py`: a mismatching cell in a group covered by an implementation issue is
  written as `IMPLEMENTATION` in `output_results.csv`. A test case is `IMPLEMENTATION` when every
  mismatching cell is covered; one uncovered mismatch keeps it `FAIL`. The report header gains
  `Implementation Issue Count` and `Resolved (Pass + Implementation)`, a new
  `## Implementation Issues` section lists each case with `expected → actual`, its issue ID and note,
  and covered groups leave the per-measure discrepancy tables. Documented in `scripts/readme.md`;
  tests in `scripts/tests/test_compare_results_implementation.py`.
- `scripts/comparison/implementation_issues.csv`: added the 7 I-73 cases (CMS72 `5a329008`,
  `cb7c95fc`, `febd4b3e`; CMS104 `348471db`, `451b6853`, `a2b8327c`, `c15bee15`) and CMS72
  `be5c4068` (I-75, **pending SME confirmation**). No CQL, fixture or MeasureReport change.

**Result:** 3914 pass, 12 implementation, 38 fail of 3964 test cases; 3926 resolved (99.04%).

**Measures Affected:** CMS72, CMS104 (reporting only)

## Label known-issue failures in the discrepancy report; resolve them once ticketed

**Problem:** a failing test case explained by a catalogued `engine`, `translator`, `content` or
`fixture` issue looked the same in `discrepancy_report.md` as an untriaged failure. Such a case
should be shown as known, and should count as resolved only once its issue is tied to a GitHub
ticket.

**Change:**

- `scripts/compare_results.py`: reads a new `scripts/comparison/known_issues.csv`
  (`issue_id,class,ticket,measure_name,guid,group,note`). A mismatching cell covered by an issue
  with a `ticket` is written as `KNOWN_ISSUE` and the case counts as resolved. With no ticket the
  case stays `FAIL`, and a `Known Issue` column in the per-measure tables names the issue. The
  header gains `Known Issue Count (ticketed)` and `— known issue, needs ticket`, and a new
  `## Known Issues` section lists each issue with its class, ticket and status. A ticket must be a
  GitHub issue or pull request URL. The QI-Core parity section is unchanged. Documented in
  `scripts/readme.md`; tests in `scripts/tests/test_compare_results_known_issues.py`.
- `scripts/comparison/known_issues.csv`: the 38 currently failing cases, copied from the
  internal tooling repo's case attributions (I-05, I-10, I-11, I-12, I-14, I-15, I-26, I-31, I-33,
  I-39, I-63, I-65). No issue has a ticket yet. The I-05 rows and the 7 CMS771 I-65 rows are
  flagged in their notes as needing re-triage.
- `known-issues.md`: added the missing I-65 row, and moved I-39 from `engine` / suspected to
  `fixture` / confirmed, matching the internal tooling repo's 2026-09-29 reclassification. No CQL,
  fixture or MeasureReport change.

**Result:** 3914 pass, 12 implementation, 0 known issue, 38 fail (all 38 known, needing a ticket)
of 3964 test cases.

**Measures Affected:** reporting only

## Restore the two MedicationAdministrations lost from CMS819 `73b0c1fe`

**Problem:** CMS819 `73b0c1fe` expects Numerator 1, but both engines returned 0. The MADiE source
bundle (`627a80a15a0d870123c7253e`) gave the id `MedicationAdministration/5f32d03297c3b600003f7cd9` to
three different administrations. MADiE accepted that at the time; it now rejects duplicate ids.
Splitting the bundle into one file per id kept only the last entry, so two were lost:

- naloxone 1659929, subcutaneous, 02-01 10:00 (in the OR)
- opioid 1010600, 02-07 08:00-08:15 (outside the OR)

The surviving naloxone (02-07 20:00, `6a7ab547`) could pair only with the 02-01 09:00 opioid. That
pair is about 6.5 days apart, so `ends 12 hours or less before` was correctly false. The
MeasureReport's `evaluatedResource` listed `6a7ab547` three times, once for each collapsed entry.

**Change:** added the two lost resources as
`MedicationAdministration-a3ebcb6c-50f4-4b1b-9705-4aeeb3cc0535.json` (naloxone) and
`MedicationAdministration-18cc43f1-4c96-4d17-9cce-eb25ed09b465.json` (opioid). Their content comes
from the source bundle, with dates shifted 2028 → 2026 like the existing files, new unique ids, and
the US Quality Core profile. In the MeasureReport, the two repeated `evaluatedResource` references
now point at the new ids, in bundle order. The QI-Core fixtures were deliberately left unchanged.

**Verified 2026-10-13** with `cql_execute` (translator/engine 5.4.0): IP 1, Denominator 1,
Numerator 1, no diagnostics. The opioid ending 02-07 08:15 and the naloxone at 20:00 are 11 h 45 m
apart. `scripts/validate_test_fixtures.py --measure CMS819FHIRHHORAE` no longer reports
`EVALUATED-REF-REPEATED` for this case. The QI-Core baseline stays 0, so the cell counts as
CMS-better. The grid has not been regenerated. Tracked as I-76 (`fixture`; I-10 retired into
it); the other CMS819 case, `31b40acc`, shows the same signature and is still open, pending its
source bundle. The case still has no
`Location/HSLOC-1096-7`, so the "Operating Room Suite" exclusion is not exercised; the 02-01 OR pair
also qualifies.

### Example

```jsonc
// before (MeasureReport-15d9e04f evaluatedResource)
{ "reference": "MedicationAdministration/6a7ab547-7f79-4bd1-a4c9-269dca8fd8e3" },
{ "reference": "MedicationAdministration/6a7ab547-7f79-4bd1-a4c9-269dca8fd8e3" },
{ "reference": "MedicationAdministration/6a7ab547-7f79-4bd1-a4c9-269dca8fd8e3" }

// after
{ "reference": "MedicationAdministration/a3ebcb6c-50f4-4b1b-9705-4aeeb3cc0535" },
{ "reference": "MedicationAdministration/18cc43f1-4c96-4d17-9cce-eb25ed09b465" },
{ "reference": "MedicationAdministration/6a7ab547-7f79-4bd1-a4c9-269dca8fd8e3" }
```

**Measures Affected:** CMS819

## Restore the Encounter lost from CMS819 `31b40acc`

**Problem:** CMS819 `31b40acc` ("Two separate encounters. Only one meets Numerator") expects IP and
Denominator 2, but both engines returned 1. The fixture had one Encounter, and the MeasureReport's
`evaluatedResource` listed `Encounter/de36ea3b` twice, so the second encounter (10-30 to 11-09) was
lost at conversion and the first (07-11 to 07-14) became `de36ea3b` (I-76). In the MADiE bundle as
exported on 2026-10-14 (`tests-NUMERPass-TwoEncountersOneNumerator-bundle`) the two Encounters have
different ids (`Encounter-1`, `Encounter-2`) but still share one `fullUrl`,
`https://madie.cms.gov/Encounter/Encounter-1`. cqf-tooling 3.9.1 `-BundleToResources` names files
from the resource id, not the `fullUrl`, and splits today's export into two Encounter files (probe
2026-10-14), so the loss happened on an earlier version of the bundle. The shared `fullUrl` and the
repeated reference suggest the second encounter was originally also `Encounter-1` and was renamed
later without updating its `fullUrl`; this is not confirmed. The restored content is the same either
way.

**Change:** added `Encounter-776faeb3-f3e6-496b-aacf-af36ef6b71ed.json` with the lost encounter's
content from the source bundle: dates shifted 2028 → 2026 like the rest of the case, a new id, the US
Quality Core profile, and `subject` set to the case patient. Drafted with
`scripts/validate_test_fixtures.py --restore-from-bundle`, then reviewed. In the MeasureReport, the
first of the two `Encounter/de36ea3b` references now points at the new encounter, in bundle order.
The QI-Core fixtures were deliberately left unchanged.

**Verified 2026-10-14** with `cql_execute` (translator/engine 5.4.0): IP 2, Denominator 2,
Numerator 1, no diagnostics, matching the fixture MeasureReport. The new encounter has the 10-31
opioid (`596cf96f`) but no antagonist, so it is in the Denominator only. The QI-Core baseline stays
at 1 for IP and Denominator, so those cells count as CMS-better. The grid has not been regenerated.

### Example

```jsonc
// before (MeasureReport-c93e2b69 evaluatedResource)
{ "reference": "Encounter/de36ea3b-fe15-4411-81e3-18cd1df1cb9b" },
{ "reference": "Encounter/de36ea3b-fe15-4411-81e3-18cd1df1cb9b" }

// after
{ "reference": "Encounter/776faeb3-f3e6-496b-aacf-af36ef6b71ed" },
{ "reference": "Encounter/de36ea3b-fe15-4411-81e3-18cd1df1cb9b" }
```

**Measures Affected:** CMS819

## Point CMS871 `113a6e72` `evaluatedResource` at its Patient instead of `Patient/null`

**Problem:** the fixture MeasureReport `0ac4f7d5` for CMS871 `113a6e72` listed `Patient/null` in
`evaluatedResource`. The MADiE source bundle's Patient had no `id`, and cqf-tooling
`-BundleToResources` names an id-less resource `null-null.json` (the QI-Core fixture still has that
file), so the reference was written with a null id. The UQC folder already has
`Patient-113a6e72-7049-4a7f-90cf-5ec3435b0dee.json`. Populations are unaffected (the case passes);
`validate_test_fixtures.py` reported the reference as dangling.

**Fix:** pointed the reference at the folder's Patient. UQC fixture only; the QI-Core fixture is
unchanged. Related: I-76 (same MADiE-permissive-bundle source).

```json
// before
{ "reference": "Patient/null" }
// after
{ "reference": "Patient/113a6e72-7049-4a7f-90cf-5ec3435b0dee" }
```

**Measures Affected:** CMS871

## Restore the Claim lost from CMS1028 `763d86f9`

**Problem:** CMS1028 `763d86f9` ("Complication (sepsis) on 1ST and 2nd encounter") expects
Numerator 2 in both groups, but both engines returned 1. The SMM diagnosis path
(`isDiagnosisPresentOnAdmission` → `CQMCommon.claimDiagnosis()`) reads only Claim diagnoses whose
`item.encounter` references the encounter. The fixture had one Claim, `2c05d8c2`, and both of its
items referenced the November encounter `df4df224`, so the February encounter `a3da5a2c` had no
claim diagnoses. The MeasureReport's `evaluatedResource` listed `Claim/2c05d8c2` twice (I-76).

The MADiE bundle as exported on 2026-10-15 (`6356dca654e383debade75aa`) has two Claims with
distinct ids and `fullUrl`s: `5ca62962b8484628b8de1ec1` (created 2026-02-01, items → the February
encounter) and `5ca62962b8484628b8de1ec5` (created 2026-11-08, items → the November encounter).
Each carries J45.21 (POA Y) and A32.7 Listerial sepsis (POA N). The surviving fixture Claim is the
second, the last entry. MADiE has since added test-case resource validation and other developers
have fixed test cases there, so the export was most likely corrected after the original split.
Every other resource in the export maps one-to-one to the fixtures.

**Change:** added `Claim-2a83353c-a7b0-469e-a6a7-51439e2c6d05.json` with the lost Claim's content
from the source bundle: a new id, the US Quality Core profile, `created` 2026-02-01 (no date shift;
the export is already in 2026), and both items referencing `Encounter/a3da5a2c`. Provider and
Coverage references follow the surviving Claim. In the MeasureReport, the first of the two
`Claim/2c05d8c2` references now points at the new Claim, in bundle order. The QI-Core fixtures were
deliberately left unchanged.

**Verified 2026-10-15** with `cql_execute` (translator/engine 5.4.0): IP 2, Denominator 2,
Numerator 1 and Numerator 2 each 2, both Numerator Exclusions 0, no diagnostics, matching the
fixture MeasureReport. `SDE SOC Diagnoses Detail` shows Sepsis on both encounters.
`scripts/validate_test_fixtures.py --measure CMS1028FHIRPCSevereOBComps` no longer reports
`EVALUATED-REF-REPEATED` for this case. The grid was regenerated after a CMS1028 rerun on
2026-10-15: every CMS1028 test case passes. The QI-Core baseline stays at 1, so the two Numerator
cells count as CMS-better; CMS1028 now has no regression or shared-failure cells (1,114 parity
pass, 14 CMS-better; the other 12 CMS-better cells predate this fix and are QI-Core drift, I-01 /
I-38). I-76 was reclassified from `fixture` to `implementation` on 2026-10-15: the steward's test
case and its MeasureReport are invalid in both versions.

### Example

```jsonc
// before (MeasureReport-7ca90ad8 evaluatedResource)
{ "reference": "Claim/2c05d8c2-ec55-480d-8dc9-8cc5f9bae9c0" },
{ "reference": "Claim/2c05d8c2-ec55-480d-8dc9-8cc5f9bae9c0" }

// after
{ "reference": "Claim/2a83353c-a7b0-469e-a6a7-51439e2c6d05" },
{ "reference": "Claim/2c05d8c2-ec55-480d-8dc9-8cc5f9bae9c0" }
```

**Measures Affected:** CMS1028

## Restore the Prediabetes Condition lost from CMS1154 `bc9c82ca`

**Problem:** CMS1154 `bc9c82ca` expects `Denominator Exclusion` 1, but both engines returned 0. The
MADiE transaction bundle (`NUMPass-70-on-Jan1-1`) has two Prediabetes Conditions (SNOMED 714628002)
under one id, `Condition/238ec3df-ff96-4356-843f-a89c036fa385`, with the same `fullUrl` and `PUT`
URL: an active one (onset 2020-01-01) and an inactive one (onset 2025-12-31). Splitting the bundle
kept only the last entry, the inactive one (`d463a372`), and the MeasureReport's `evaluatedResource`
listed `Condition/d463a372` twice (I-76). The inactive Condition has no abatement, so
`FHIRCommon.prevalenceInterval()` returns null for it (I-31) and `"Prediabetes Diagnosis Overlaps 2
Year Look Back Period"` was empty. It would not qualify even under FHIRCommon's intended open
`Interval[onset, null)`, so the expected exclusion comes from the lost active Condition. The case was
previously filed under I-31.

**Change:** added `Condition-18617b19-1ea4-46cc-a7e2-91b6d531152a.json` with the lost Condition's
content from the source bundle: a new id, the US Quality Core profile, `clinicalStatus` active, and
onset 2020-01-01 (no date shift; the export is already in 2026). In the MeasureReport, the first of
the two `Condition/d463a372` references now points at the new Condition, in bundle order. The
QI-Core fixtures and FHIRCommon were deliberately left unchanged.

**Verified 2026-10-15** with `cql_execute` (translator/engine 5.4.0): IP 1, Denominator 1,
`Denominator Exclusions` true, Numerator false, no diagnostics, matching the fixture
MeasureReport. `"Prediabetes Diagnosis Overlaps 2 Year Look Back Period"` holds only `18617b19`.
`scripts/validate_test_fixtures.py --measure CMS1154ScreeningPrediabetesFHIR` no longer reports
`EVALUATED-REF-REPEATED` for this case. The QI-Core baseline stays at 0, so the cell counts as
CMS-better. The grid was regenerated on 2026-10-15 and `bc9c82ca` passes. Tracked as I-76, reclassified from `fixture` to
`implementation` on 2026-10-15: the steward's test case and its MeasureReport are invalid in both
versions.

### Example

```jsonc
// before (MeasureReport-466dec57 evaluatedResource)
{ "reference": "Condition/d463a372-3385-4750-a011-05b99f82338c" },
{ "reference": "Condition/d463a372-3385-4750-a011-05b99f82338c" }

// after
{ "reference": "Condition/18617b19-1ea4-46cc-a7e2-91b6d531152a" },
{ "reference": "Condition/d463a372-3385-4750-a011-05b99f82338c" }
```

**Measures Affected:** CMS1154

## Qualify `MedicationRequest` and `ServiceRequest` retrieves with `USQualityCore` (I-52, I-34)

Recorded 2026-10-15 for commits made on 2026-10-01 that had no entry here.

**Problem:** the migrated measures used unqualified `[MedicationRequest: …]` and
`[ServiceRequest: …]` retrieves. These also returned the `doNotPerform` resources
(`us-quality-core-medicationnotrequested` / `servicenotrequested`), so a declined order counted as a
real one (I-52). CMS347's 23 statin cases over-fired the Numerator this way (I-34). QI-Core computed
the expected values for these cases.

**Change:** three commits qualified the retrieve types. No `doNotPerform` filter was added.

- `e1714e2c`: every `ServiceRequest` retrieve becomes `[USQualityCore.ServiceRequest: …]`.
- `217a29f1`: every `MedicationRequest` retrieve becomes `[USQualityCore.MedicationRequest: …]`.
- `2709b513`: the same qualifier on every other retrieve whose type exists only as a USQualityCore
  profile. Its grid diff changes no cell.

**Verified** by each commit's own regenerated grid. `217a29f1` flips CMS347 (111 cells, all 23
I-34 cases), CMS104 (14), CMS135 (12), CMS144 (5) and CMS71 (4) from FAIL to PASS. `e1714e2c` flips
CMS645 (5), CMS22 (2, the `f9417a57` / `c41f9946` cases in the CMS22 entry above), CMS108 (1) and
CMS190 (1). On the 2026-10-15 grid none of these cases diverges from QI-Core.

**Example** (`input/cql/CMS347FHIRStatinPreventionTxCVD.cql:249-251`; the same change at every
retrieve of these types):

```cql
-- before
  ( [MedicationRequest: "Low Intensity Statin Therapy"]
    union [MedicationRequest: "Moderate Intensity Statin Therapy"]
    union [MedicationRequest: "High Intensity Statin Therapy"] ) StatinRequest

-- after
  ( [USQualityCore.MedicationRequest: "Low Intensity Statin Therapy"]
    union [USQualityCore.MedicationRequest: "Moderate Intensity Statin Therapy"]
    union [USQualityCore.MedicationRequest: "High Intensity Statin Therapy"] ) StatinRequest
```

**Measures Affected:** CMS347, CMS104, CMS135, CMS144, CMS71, CMS645, CMS22, CMS108, CMS190 (cells
changed). `2709b513` also touched the CQL of most other measures without changing a cell.

## Fold the issue sections into Measures with Discrepancies

**Problem:** `discrepancy_report.md` listed failures in three places: `## Implementation Issues`,
`## Known Issues` and `## Measures with Discrepancies`. A failure that an issue resolved appeared
only in the first two, and its measure was listed under "Measures with No Discrepancies". It was
hard to see in one place which measures fail and which failures nothing yet explains.

**Change:**

- `scripts/compare_results.py`:
  - `## Implementation Issues` and `## Known Issues` are removed.
  - `## Measures with Discrepancies` lists every measure with a mismatching test case, whatever the
    issue state.
  - The per-measure `Known Issue` column becomes `Issue`. It holds `I-XX (implementation)`,
    `I-XX (ticketed)`, `I-XX (needs ticket)`, or blank.
  - Each measure section ends with an `Issues` list giving each cited issue's class, ticket and
    note.
  - The `Discrepancy Summary` table gains an `Unattributed Discrepancies` row, and the per-measure
    summary gains an `Unattributed` column. Both count test cases that no implementation issue and
    no ticketed known issue resolves, which are the `FAIL` verdicts.
  - "Measures with No Discrepancies" now lists only measures where every test case matches its
    fixture.
  - Documented in `scripts/readme.md`. Tests are in `scripts/tests/test_compare_results_*.py`.

**Result:** reporting only. `output_results.csv` and every count are unchanged: 3918 pass,
12 implementation, 4 known issue and 30 fail out of 3964. Measures with Discrepancies goes from 10
to 15 (CMS72, CMS104, CMS165, CMS347 and CMS996 are now listed with their resolving issues), and
Measures with No Discrepancies goes from 64 to 59. Unattributed Discrepancies: 30 test cases in
10 measures.

**Measures Affected:** none (reporting only)

## Restore the stroke Claim lost from CMS72 `5a329008`

**Problem:** CMS72 `5a329008` ("Testing multiple encounters, one with ED to Inpatient with
antithrombotic, and one with Ed to Obs to Inpatient with tPA") expects IP 2, Denominator 2,
Denominator Exclusion 1, Numerator 1, but both engines returned IP 1. `TJC."Ischemic Stroke
Encounter"` takes the principal diagnosis from `CQMCommon.claimDiagnosis()`, which reads only Claims
whose `item.encounter` references the encounter. The fixture had one Claim (`5ca62962…1ec5`, listed
twice in `evaluatedResource`) pointing at the June encounter `93ad3087`, so the April encounter
`6fac0d25` had no principal diagnosis and dropped out.

The MADiE bundle (`60f82c2f98086b570510e2cd`, test case `LCG2Enc1WithAntithrombic1WithtPA`) has two
Claims under one id, `Claim/5ca62962b8484628b8de1ec5`, with the same `fullUrl`
(`https://madie.cms.gov/claim/5ca62962b8484628b8de1ec5`). The first references the April inpatient
encounter, the second the June one. Splitting the bundle kept only the last entry (I-76). The two
Claims are otherwise identical (I63.00 principal, `created` 2026-12-01). Every other resource in the
bundle maps one-to-one to the fixtures. The case was previously filed under I-73.

**Change:** added `Claim-8b852968-1ff0-4578-8466-66e6f11d3d2b.json` with the lost Claim's content:
a new id, the US Quality Core profile, `created` 2026-12-01 (no date shift), and `item.encounter`
referencing `Encounter/6fac0d25`. Patient, provider and Coverage references follow the surviving
Claim (the source Claims reference `Patient/d170a0a8…`, another patient). In the MeasureReport, the
first of the two `Claim/5ca62962…1ec5` references now points at the new Claim, in bundle order. The
QI-Core fixtures were deliberately left unchanged.

**Verified 2026-10-16** with `cql_execute` (translator/engine 5.4.0): Initial Population and
Denominator hold `6fac0d25` and `93ad3087`, Denominator Exclusions holds `93ad3087` (alteplase
`d48cca8a`), Denominator Exceptions is empty, and the Numerator after exclusions is `6fac0d25`
(antithrombotic `431d0925`). That is 2/2/1/1/0, matching the fixture MeasureReport, with no
diagnostics. `scripts/validate_test_fixtures.py --measure CMS72FHIRSTKAntithromboticDay2` no longer
reports `EVALUATED-REF-REPEATED` for this case. The grid has not yet been regenerated. Tracked as
I-76 (`implementation`): the steward's test case and its MeasureReport are invalid in both versions.

### Example

```jsonc
// before (MeasureReport-dda268cb evaluatedResource)
{ "reference": "Claim/5ca62962b8484628b8de1ec5" },
{ "reference": "Claim/5ca62962b8484628b8de1ec5" }

// after
{ "reference": "Claim/8b852968-1ff0-4578-8466-66e6f11d3d2b" },
{ "reference": "Claim/5ca62962b8484628b8de1ec5" }
```

**Measures Affected:** CMS72

## Restore the two stroke Claims lost from CMS72 `cb7c95fc`

**Problem:** CMS72 `cb7c95fc` (`3Enc2WithAntithrombic1WithtPA`) expects IP 3, Denominator 3,
Denominator Exclusion 1, Numerator 2, but both engines returned IP 1. As in `5a329008` above, only
the July encounter `3312b3d4` had a Claim, so the September (`d047da74`) and October (`24c9a03a`)
encounters had no principal diagnosis and dropped out. The MeasureReport's `evaluatedResource`
listed `Claim/5ca62962…1ec5` three times.

The MADiE bundle (`60f82c2f98086b570510e2bb`) has three Claims under one id and `fullUrl`,
`https://madie.cms.gov/claim/5ca62962b8484628b8de1ec5`, referencing in bundle order the September,
October and July inpatient encounters. Splitting the bundle kept only the last (I-76). The Claims
are otherwise identical (I63.00 principal, `created` 2026-12-01). Every other resource in the
bundle maps one-to-one to the fixtures. The case was previously filed under I-73.

**Change:** added `Claim-81f827a1-5c7a-4f30-af5a-1ee4cd38da16.json` (`item.encounter` →
`Encounter/d047da74`) and `Claim-1cb6ea3f-a1ad-45bf-a8cf-00e4717132dd.json` (`item.encounter` →
`Encounter/24c9a03a`), each a copy of the surviving Claim with a new id (US Quality Core profile,
`created` 2026-12-01, patient, provider and Coverage as on the surviving Claim). In the
MeasureReport, the first two of the three `Claim/5ca62962…1ec5` references now point at the new
Claims, in bundle order. The QI-Core fixtures were deliberately left unchanged.

**Verified 2026-10-16** with `cql_execute` (translator/engine 5.4.0): Initial Population and
Denominator hold all three encounters, Denominator Exclusions holds `3312b3d4` (tPA Procedure
`824551a9`), Denominator Exceptions is empty, and the Numerator is `d047da74` and `24c9a03a`
(antithrombotic `c6b8c3e5`, `d62c123c`). That is 3/3/1/2/0, matching the fixture MeasureReport,
with no diagnostics. `scripts/validate_test_fixtures.py --measure CMS72FHIRSTKAntithromboticDay2`
no longer reports `EVALUATED-REF-REPEATED` for this case. The grid has not yet been regenerated.
Tracked as I-76 (`implementation`).

### Example

```jsonc
// before (MeasureReport-6844e7ed evaluatedResource)
{ "reference": "Claim/5ca62962b8484628b8de1ec5" },
{ "reference": "Claim/5ca62962b8484628b8de1ec5" },
{ "reference": "Claim/5ca62962b8484628b8de1ec5" }

// after
{ "reference": "Claim/81f827a1-5c7a-4f30-af5a-1ee4cd38da16" },
{ "reference": "Claim/1cb6ea3f-a1ad-45bf-a8cf-00e4717132dd" },
{ "reference": "Claim/5ca62962b8484628b8de1ec5" }
```

**Measures Affected:** CMS72

## Restore the three stroke Claims lost from CMS72 `febd4b3e`

**Problem:** CMS72 `febd4b3e` (`4Enc2WithAntithrombic2WithtPA`) expects IP 4, Denominator 4,
Denominator Exclusion 2, Numerator 2, but both engines returned IP 1. As in `5a329008` and
`cb7c95fc` above, only the November encounter `96df9404` had a Claim, so the September
(`11dfdb91`), October (`8eedd582`) and July (`3a6145c7`) encounters had no principal diagnosis and
dropped out. The MeasureReport's `evaluatedResource` listed `Claim/5ca62962…1ec5` four times.

The MADiE bundle (`60f82c2f98086b570510e2cc`) has four Claims under one id and `fullUrl`,
`https://madie.cms.gov/claim/5ca62962b8484628b8de1ec5`, referencing in bundle order the September,
October, July and November inpatient encounters. Splitting the bundle kept only the last (I-76).
The Claims are otherwise identical (I63.00 principal, `created` 2026-12-01). Every other resource
in the bundle maps one-to-one to the fixtures. The case was previously filed under I-73.

**Change:** added `Claim-f89712ea-cace-4383-a982-7b4e014b9307.json` (`item.encounter` →
`Encounter/11dfdb91`), `Claim-43e7677b-c099-4fa3-8f31-74177993b014.json` (→ `Encounter/8eedd582`)
and `Claim-54ea443b-79cc-42b0-b6da-b7d778cb7ae4.json` (→ `Encounter/3a6145c7`), each a copy of the
surviving Claim with a new id (US Quality Core profile, `created` 2026-12-01, patient, provider and
Coverage as on the surviving Claim). In the MeasureReport, the first three of the four
`Claim/5ca62962…1ec5` references now point at the new Claims, in bundle order. The QI-Core
fixtures were deliberately left unchanged.

Not changed: the September encounter's `reasonReference` points at
`Condition/5c953f97b848462de0ae416d`, which exists in neither the MADiE bundle nor the fixture,
and Condition `d99b4ae8` is referenced by no encounter. No population reads `reasonReference` on
this path, so this is left for the steward.

**Verified 2026-10-16** with `cql_execute` (translator/engine 5.4.0): Initial Population and
Denominator hold all four encounters, Denominator Exclusions holds `11dfdb91` (alteplase
`65d451e6`) and `3a6145c7` (tPA Procedure `6062c2bc`), Denominator Exceptions is empty, and the
Numerator is `8eedd582` and `96df9404` (antithrombotic `d35411b4`, `5d8c229c`). That is 4/4/2/2/0,
matching the fixture MeasureReport, with no diagnostics. `scripts/validate_test_fixtures.py
--measure CMS72FHIRSTKAntithromboticDay2` no longer reports `EVALUATED-REF-REPEATED` for any CMS72
case. The grid has not yet been regenerated. Tracked as I-76 (`implementation`).

### Example

```jsonc
// before (MeasureReport-4f80f98a evaluatedResource)
{ "reference": "Claim/5ca62962b8484628b8de1ec5" },
{ "reference": "Claim/5ca62962b8484628b8de1ec5" },
{ "reference": "Claim/5ca62962b8484628b8de1ec5" },
{ "reference": "Claim/5ca62962b8484628b8de1ec5" }

// after
{ "reference": "Claim/f89712ea-cace-4383-a982-7b4e014b9307" },
{ "reference": "Claim/43e7677b-c099-4fa3-8f31-74177993b014" },
{ "reference": "Claim/54ea443b-79cc-42b0-b6da-b7d778cb7ae4" },
{ "reference": "Claim/5ca62962b8484628b8de1ec5" }
```

**Measures Affected:** CMS72

## Restore the stroke Claims lost from four CMS104 multi-encounter cases

**Problem:** four CMS104 multi-encounter stroke cases, `348471db`, `451b6853`, `a2b8327c` and
`c15bee15`, expected IP 2 or 3, but both engines returned IP 1. As in the three CMS72 cases above,
only one encounter per patient had a Claim (the template `5ca62962…1ec5`), so the others had no
principal diagnosis and dropped out. Each MeasureReport listed the Claim once per encounter.

The whole-measure MADiE export of 2026-10-16 (`CMS104FHIR-v1.0.000`, test cases
`NUMERPass-3Enc2WithAntithrombotic2WithExcep`, `-3Enc2WithAntithrombotic1WithExcep1Exclu`,
`-2Enc3WithAntithrombotic` and `-3Enc2WithAntithrombotic1WithExcep`) has one Claim per inpatient
encounter, with distinct ids and `fullUrl`s, otherwise identical to the fixture template. The
fixtures were split from an earlier version in which all of them carried the template id (I-76).
In each case the surviving fixture Claim belongs to the last Claim's encounter in bundle order,
and every other resource count matches. The cases were previously filed under I-73.

**Change:** added seven Claims, each a copy of the case's surviving Claim with a new id and
`item.encounter` pointing at an encounter that had none:

| Case | New Claim → Encounter |
| --- | --- |
| `348471db` | `f0b94078-7d15-4068-b347-c2a6e81b31ba` → `75f7c014`; `a86c4aaf-034a-4670-b422-7b1afced2d35` → `fa6b04db` |
| `451b6853` | `cddeebd4-24ae-465a-b189-680fe0ee8f06` → `b0308413`; `09dbe4fd-1648-47f5-b354-49c2c3dc56e5` → `b9ee5db2` |
| `a2b8327c` | `75f1f336-41a9-4580-ab36-e0c6a591a2ab` → `ae6c08c6` |
| `c15bee15` | `620b9f4e-77f5-47c0-9005-cae9360321c5` → `1a78b4b0`; `e25cde12-fc1c-4339-a3f1-ce6576b5486d` → `c5ea6ecd` |

These MeasureReports list every Encounter before every Claim, so in each the first one or two
repeated `Claim/5ca62962…1ec5` references now point at the new Claims and the last still points at
the original. The QI-Core fixtures were deliberately left unchanged.

**Verified 2026-10-16** with `cql_execute` (translator/engine 5.4.0), IP/Den/DenExcl/Numer/DenExcep
after exclusions: `348471db` 3/3/1/1/1, `451b6853` 3/3/2/1/0, `a2b8327c` 2/2/0/2/0, `c15bee15`
3/3/0/2/1, each matching its fixture MeasureReport, with no diagnostics.
`scripts/validate_test_fixtures.py --measure CMS104FHIRSTKDCAntithrombotic` no longer reports
`EVALUATED-REF-REPEATED` for these cases. The grid has not yet been regenerated. Tracked as I-76
(`implementation`); I-73 is retired.

### Example

```jsonc
// before (MeasureReport-bf54d81d evaluatedResource, 348471db)
{ "reference": "Claim/5ca62962b8484628b8de1ec5" },
{ "reference": "Claim/5ca62962b8484628b8de1ec5" },
{ "reference": "Claim/5ca62962b8484628b8de1ec5" }

// after
{ "reference": "Claim/f0b94078-7d15-4068-b347-c2a6e81b31ba" },
{ "reference": "Claim/a86c4aaf-034a-4670-b422-7b1afced2d35" },
{ "reference": "Claim/5ca62962b8484628b8de1ec5" }
```

**Measures Affected:** CMS104

## Work around the CMS145 Choice-typed overload mis-binding in `overlapsAfterDayOfEncounter`

**Problem:** in `CMS145FHIRCADBBlockerTPMIorLVSD`, `overlapsAfterDayOfEncounter` takes
`Event Choice<AllergyIntolerance, ConditionProblemsHealthConcerns>`. In the
`when Event is ConditionProblemsHealthConcerns` branch, both `FHIRCommon.isVerified()` and
`FHIRCommon.prevalenceInterval()` resolved to the **AllergyIntolerance** overloads, so the ELM
carries `As {http://hl7.org/fhir}AllergyIntolerance` of a Condition. That cast is null at
runtime, so the prevalence interval is null and the Denominator Exception never fires: five
cases expect 1 and got 0 (`5fd0d626`, `61306767`, `fd5fb311`, `4f4a65f4`, `b65680a0`).

The translator accepts a `Choice` component only by **exact equality** — `ChoiceType.isCompatibleWith`
and `ConversionMap.findChoiceConversion` test `param.isCompatibleWith(component)` and never
`isSubTypeOf` — so the base-typed `Condition` overload is not a candidate and the
`AllergyIntolerance` one wins on the exact component match, with no ambiguity reported. This is a
**translator** defect (I-78), not a content defect: the function text is unchanged from the
QI-Core measure, and no US Quality Core rule requires a cast here. QI-Core gets the right answer
only because its `QICoreCommon.prevalenceInterval` declares a single Choice-typed overload; USQC's
`AHAOverall` declares no `isVerified` or `prevalenceInterval` at all, and both calls resolve
against `hl7.fhir.uv.cql.FHIRCommon 2.0.0`, which types them on the base FHIR resources.

**Change:** cast explicitly in the Condition branch so the `FHIR.Condition` overloads bind.

### Example

```cql
// before
when Event is ConditionProblemsHealthConcerns then Event.isVerified()
  and Event.prevalenceInterval() overlaps after day of Visit.period

// after
when Event is ConditionProblemsHealthConcerns then (Event as ConditionProblemsHealthConcerns).isVerified()
  and (Event as ConditionProblemsHealthConcerns).prevalenceInterval() overlaps after day of Visit.period
```

The original two lines are retained above the replacement in an `[I-78]` comment block.

**Verified 2026-10-16** with `cql_execute`: denominator exception 1 true for `5fd0d626`,
`61306767` and `fd5fb311`; denominator exception 2 true for `4f4a65f4` and `b65680a0`; all other
populations unchanged. **Re-verified 2026-10-17** by a full CMS145 suite run — the same five cells
and no others, the other 48 cases identical, so the five move from failing to matching and nothing
else in the measure shifts. The five cases pass **only** because of this workaround and remain cited in
`scripts/comparison/known_issues.csv`; the issue stays open until the translator fix lands, at
which point the casts and their comment block should be removed together. The AllergyIntolerance
branch reads properties on `Event` directly and is unaffected.

**Measures Affected:** CMS145

## Normalize CMS771's IPSS tuple element to `System.Integer`

**Problem:** `Documented IPSS Assessment Result` typed its `valueInteger` return element as
`FHIR.integer` (`IPSSAssessment.value as FHIR.integer`), while
`AUA Symptom Index and Quality of Life Assessment Result` returns `System.Integer` — its `+`
operands are wrapped in `FHIRHelpers.ToInteger`. The two sides of
`Urinary Symptom Score Assessment`'s `union` therefore had different tuple types, so the
translator emitted `List<Choice<Tuple,Tuple>>`: at runtime the union silently dropped the AUA
branch (`051c5977` holds two AUA tuples and the union is `[]`; `3ab3ac1d` has two in, one out),
and the `…valueInteger` access became `Choice<FHIR.integer, System.Integer>`, which the
subtraction in `Urinary Symptom Score Change` could not narrow, returning null. Seven cells
failed: `Group_1:Denominator 1→0` (`051c5977`, `3ab3ac1d`) and `Group_1:Numerator 1→0`
(`4c234ec0`, `9be591a0`, `bc79e5bc`, `bf0f8968`, `e90d90a7`). Malformed CQL, not a tracked
defect.

**Fix:** `valueInteger: FHIRHelpers.ToInteger(IPSSAssessment.value)` — both tuple elements are
now `System.Integer`, so the union is `List<Tuple>` and the subtraction is native integer
arithmetic.

**Example** (`input/cql/CMS771FHIRUrinarySymptomScoreBPH.cql`, `Documented IPSS Assessment Result`):

```cql
-- before
valueInteger: IPSSAssessment.value as FHIR.integer

-- after
valueInteger: FHIRHelpers.ToInteger(IPSSAssessment.value)
```

**Verified 2026-10-19:** CMS771 31/31 cases, 124/124 cells PASS; `Urinary Symptom Score Change`
evaluates 4, 3, 10, 12 and 3 on the five Numerator cases. The comparison grid moves
`PASS 23376→23383` / `FAIL 270→263`, with only the 7 CMS771 rows changed. `5339dd62`, `71846c52`
and `ae8b8236` now evaluate `Numerator = true` at CQL level but still score `PASS`: the
extraction harness reports 0 for a case whose `Denominator Exclusion = 1`, per the
proportion-conformance rule.

**Measures Affected:** CMS771FHIRUrinarySymptomScoreBPH

## Remove the dead `test` link from the report's clean-measures grid (harness)

**Problem:** Every cell of `## Measures with No Discrepancies` in `scripts/comparison/discrepancy_report.md`
carried a `[ test ](../../input/tests/results/{Measure}.txt)` link alongside the CQL link. The CQL
plugin stopped writing those flat `{Measure}.txt` traces — it now writes per-measure
`TestCaseResult-*.json` directories — so no `.txt` trace remains under `input/tests/results/` and
every `test` link in the report 404s.

**Fix:** `render_no_discrepancy_section()` in `scripts/compare_results.py` now emits only the CQL
link (whose label is still the measure name) per cell. `test_results_file_link()` is unchanged and
still serves the `[test results]` links in the per-measure discrepancy sections. Updated the
docstring and the unit test accordingly; regenerated `actual_results.csv`,
`output_results.csv`, and `discrepancy_report.md`.

**Measures Affected:** none (report rendering only; the link removal itself changes no verdict)
