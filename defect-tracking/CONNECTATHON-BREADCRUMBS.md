# Connectathon Breadcrumbs

Running list of open issues where the root cause is understood but the fix was deliberately
**not applied**, left instead as a documented option for the CQL/FHIR experts at this weekend's
Connectathon.

The reasoning behind leaving these open: each has a confirmed root cause and a candidate fix that
was verified in isolation, but choosing *whether* to apply it is a modelling decision — scope,
tradeoffs, or which clinical pattern is correct — rather than a bug fix. Documenting them beats
deciding them unilaterally. Every other confirmed issue is in `known-issues.md`; anything already
applied is in `change-log.md`.

Each entry: measure, issue ID(s), what's understood, what's still a judgment call, and where the
full evidence lives. Keep this list current — add an entry the same turn a breadcrumb is flagged,
and update/remove entries once the Connectathon resolves them one way or the other.

## CMS68FHIRDocumentationCurrentMeds

- **I-37 (not applied — breadcrumb)**: test case `f2e2e1c0` produces Missing Results across all 4
  Group_1 populations. Root cause confirmed: `CMS68FHIRDocumentationCurrentMeds.cql:65` calls
  `MedicationsNotDocumented.recorded ( )` on a `ProcedureNotDone`, and `USQualityCoreCommon`
  declares both `recorded(Procedure)` and `recorded(ProcedureNotDone)`. Because
  `ProcedureNotDone`'s model info declares `target="Procedure"`, `cql-to-elm`'s
  `TypeBuilder.dataTypeToQName` serializes both overloads to the identical QName, so
  `FunctionRefEvaluator.pickFunctionDef` finds two "identical" candidates and throws. The error is
  uncaught, so the whole library evaluates nothing — hence Missing rather than wrong values.
  Candidate fix — the `.ext('.../us-quality-core-recorded').value as FHIR.dateTime` bypass — is
  **already applied and verified on CMS108 and CMS190** (see I-55), so this is a known-good,
  like-for-like port rather than a novel fix. Isolation repro:
  `input/cql/testI37RecordedAmbiguousOverload.cql` (self-contained; needs no fixture data, since
  the ambiguity fires at dispatch time regardless of retrieved content).
  **Judgment call for the Connectathon**: the `.ext()` bypass works but hard-codes an extension URL
  at every call site, trading a readable fluent accessor for a brittle string. The cleaner fix is
  upstream — disambiguate the overloads in `USQualityCoreCommon`, or fix
  `dataTypeToQName` so sibling profiles don't collide (I-18 tracks the upstream defect). Worth
  deciding whether to keep porting the bypass measure-by-measure (CMS68, CMS996 still carry the old
  field) or hold for an upstream fix. Full dossier: I-37, and I-18 "Deep-dive" Issue 1.

## CMS22FHIRPCSBPScreeningFollowUp

- **I-59 (applied)**: `.reasonCode` → `.reasonRefused()` fix applied to all 6 `ServiceNotRequested`
  negation defines — unambiguous migration-idiom fix, fixes 10 of 12 previously-failing cases,
  zero regressions.
- **I-52 (not applied — breadcrumb)**: 2 remaining cases (f9417a57, c41f9946) numerator-over-fire
  because 6 positive `ServiceRequest`/`MedicationRequest` retrieves have no `doNotPerform`
  exclusion. Candidate fix (`X.doNotPerform is not true` on each) verified via isolated
  `cql_execute` testing to resolve both cases with zero regressions, then deliberately reverted.
  **Judgment call for the Connectathon**: should this exclusion be applied broadly across CMS22 (and
  potentially other measures sharing the pattern), or does it risk suppressing legitimate cases
  elsewhere that haven't been tested? Full evidence in I-52's 2026-09-16 note and I-59's
  "Remaining 2 cases" section.

## CMS2FHIRPCSDepScreenAndFollowUp

- **I-60 (not applied — breadcrumb)**: 8 cms-only cases, previously misclassified under I-36 as
  an engine defect. Actual cause: the `ObservationCancelled`-based negation logic is entirely
  commented out, with the original author's own TODO proposing a rework toward
  `ServiceRequest` + `TaskRejected` (pattern 3 — "rejection of a proposal" — per `/usqualitycore`'s
  negation-pattern taxonomy) instead of `ObservationCancelled` (pattern 1 — "event not done, for a
  reason"). **Judgment call for the Connectathon**: which negation pattern is clinically correct
  for this measure's depression-screening-declined scenario, and what should the replacement CQL
  look like? Not attempted here — re-authoring negation logic from scratch is a bigger lift than a
  one-line accessor fix and deserves domain-expert sign-off on the target pattern first. Full
  evidence in I-60.
- **Scoped 2026-09-18**: the commented-out blocks are
  `CMS2FHIRPCSDepScreenAndFollowUp.cql:74-84` (`define "Denominator Exceptions": false`, real body
  commented out) and `:151-168` (the two `ObservationCancelled` supporting defines). All 8 cases
  confirmed to trace here: every failing cell is `Group_1:Denominator Exception`, all `1→0`, and
  the define returns a literal `false` — so no retrieve happens and I-36 cannot be the mechanism.
  `cases.csv` attribution moved I-36 → I-60.

## Methodology note: fixtures missing patient-reference fields (repo-wide sweep not yet done)

- **I-07 (fixed for CMS816, 2026-09-18)**: 17 of 28 CMS816 fixture Encounter resources (19 files)
  omitted `subject` entirely. Under `context Patient`, an Encounter with no `subject` is silently
  filtered out of every `[Encounter: "..."]` retrieve regardless of type/status/period — same
  mechanism as `Task.for` (I-46), just never checked for on Encounter/Observation/
  MedicationAdministration until now. Fixed by extending `scripts/validate_test_fixtures.py`'s
  `REQUIRED_PATIENT_FIELDS` and running `--fix-required-fields --apply`. Full writeup:
  `known-issues.md`'s "Broken or typo'd patient reference" section, `change-log.md`.
- **Judgment call for the Connectathon / next pass**: the enhanced validator has only been run
  against CMS816 (fixed) and CMS986 (spot-checked clean, 0 findings) so far — **no repo-wide
  sweep has been performed**. Since the same silent-drop mechanism applies to any measure whose
  CQL retrieves Encounter, Observation, or MedicationAdministration under `context Patient`,
  other measures' fixtures may carry the same undetected defect, misfiled under a different (or
  no) issue. Recommended next step: `python scripts/validate_test_fixtures.py
  --fix-required-fields` (dry-run, no `--apply`) across the full fixture tree, then triage
  per-measure before applying — a repo-wide `--apply` without review risks silently
  reclassifying/fixing cases currently (correctly or incorrectly) attributed elsewhere.

## Unaudited (flagged, not yet investigated)

- **CMS771FHIRUrinarySymptomScoreBPH**, **CMS177FHIRChildMDDSuicideAssmt**: no negation-profile
  retrieves exist in either measure's CQL at all, so their I-36 "engine" classification rests on
  some other mechanism not covered by the reason-accessor audit that found I-59/I-60. Neither
  confirmed nor refuted as genuine engine issues — needs separate investigation before the
  Connectathon if there's time, otherwise flag as-is for the experts.

## Still assumed genuinely engine-side (per I-36, unaudited beyond the reason-accessor check)

CMS135FHIRACEIorARBorARNIforHF, CMS144FHIRHFBetaBlockerForLVSD, CMS645FHIRBoneDensityPCADTherapy,
CMS71FHIRSTKAnticoagAFFlutter, CMS996FHIRAptTxforSTEMI, CMS646FHIRIntravesicalBCGTherapy,
CMS145FHIRCADBBlockerTPMIorLVSD, CMS104FHIRSTKDCAntithrombotic — the 2026-09-16 audit found none
of these share the `.reasonCode`-vs-fluent-accessor anti-pattern (their negation profiles read
genuinely-populated base elements, confirmed against fixture data), so I-36's engine
classification stands for these 8 from this specific angle. Not re-verified from any other angle.
