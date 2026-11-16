/*
###############################################################################
# testE15ConditionUnionPrevalence — engine/translator unit-test repro for I-28
###############################################################################
#
# PURPOSE
#   Demonstrates defect I-28 (defect-tracking/known-issues.md): a `union` of the
#   two sibling USQualityCore condition profiles —
#       [ConditionProblemsHealthConcerns: <code>]
#         union [ConditionEncounterDiagnosis: <code>]
#   — types the result as `List<Choice<ConditionEncounterDiagnosis,
#   ConditionProblemsHealthConcerns>>`. The cql-to-elm translator cannot widen a
#   union-built Choice to the base `FHIR.Condition`, so any `.prevalenceInterval()`
#   (or `.verified().prevalenceInterval()`) call on the elements fails to resolve:
#
#     Could not resolve call to operator prevalenceInterval with signature
#     (choice<USQualityCore.ConditionEncounterDiagnosis,
#             USQualityCore.ConditionProblemsHealthConcerns>)
#
#   That single translate-time error fails the whole library and turns every
#   test case into a Missing Result (the crash signature seen on CMS347, CMS117,
#   CMS138, CMS153, CMS136, CMS155, CMS69).
#
#   See defect-tracking/_reference/FHIRCommon.cql:
#     - line 394: only `prevalenceInterval(condition Condition)` exists
#       (no Choice overload) -> translate-time resolution failure.
#     - lines 427/438: `isVerified(FHIR.Condition)` / `verified(List<FHIR.Condition>)`
#       exist, so the replacement `[FHIR.Condition: <code>].verified()` resolves
#       cleanly against the base type.
#
# FIX
#   Replace the sibling-profile union with a single base `FHIR.Condition` retrieve.
#   Both profiles derive from `FHIR.Condition`, so a base-type retrieve captures
#   every instance without ever forming the problem Choice type (the working
#   CMS125 pattern). The FAILING defines below reproduce the translator error; the
#   PASSING defines are the equivalent, working replacement the team should ship.
#
# CHOICE-OVERLOAD EXPERIMENT (ANSWERED, NEGATIVE — REMOVED FROM THIS LIBRARY;
#   CORRECTED 2026-10-19 — the original reasons below were wrong, see I-28)
#   A library-level `define fluent function prevalenceInterval(condition
#   Choice<ConditionEncounterDiagnosis, ConditionProblemsHealthConcerns>)` was tried to
#   make the failing union resolve WITHOUT a base-type retrieve. Result: NOT viable —
#   but for different reasons than first recorded here:
#     - CORRECTION: a Choice-typed fluent parameter is legal and translates cleanly.
#       FHIRCommon-2.0.0 declares `toInterval(choice Choice<dateTime, Period, Timing,
#       instant, string, Age, Range>)`, and the 24 measure-local `isVerified(...
#       Choice<...>)` functions compile. The 5.2.0 `<internal translator error>` /
#       `could not determine result type` seen when this was first tried is not evidence
#       that a Choice parameter type is rejected.
#     - A shared Choice overload still cannot be delegated to: an unqualified call from
#       its own body rebinds to the local overload and reports `circular reference`
#       (I-19), and a qualified `FHIRCommon.prevalenceInterval(x)` is rejected with
#       "is a fluent function and can only be invoked with fluent syntax".
#     - The only viable Choice-overload shape inlines FHIRCommon's body with `is`/`as`
#       narrowing (testI28ChoiceArgumentProbeC.cql translates clean) — a per-call-site
#       workaround, not a shared fix.
#     - These errors contaminated the whole library (spurious `Syntax error at PregnancyDx`)
#       and hid attribution of the `.verified()` List<Choice> behaviour, so the overload was
#       removed. The base `[FHIR.Condition: ...]` retrieve (PASSING defines) is the fix and
#       stays in force (I-28 remains workaround-applied, not fixed).
#
# SELF-CONTAINED
#   Uses only inline codes (no external value sets) so it runs standalone.
#
# HANDOFF
#   Hand-off artifact for the engine/translator team. The fixtures live under
#   input/tests/measure/testE15ConditionUnionPrevalence/ and are made resolvable by two
#   registration resources (required, otherwise the engine loads the library with a null
#   id/version):
#     - input/resources/library/testE15ConditionUnionPrevalence.json   (id/version 0.0.000)
#     - input/resources/measure/testE15ConditionUnionPrevalence.json   (measure + library ref)
#   The CQL `library` declaration below must match that Library resource's name/version.
#   A test library becomes "the measure" for the purposes of these test cases.
#
# Build/engine: VSCode-extension CQL engine + translator (see defect-tracking/known-issues.md).
###############################################################################
*/
library testE15ConditionUnionPrevalence version '0.0.000'

using USQualityCore version '0.1.0-cibuild'
using USCore version '6.1.0-derived'
using FHIR version '4.0.1'

include hl7.fhir.uv.cql.FHIRHelpers version '4.0.1' called FHIRHelpers
include hl7.fhir.uv.cql.FHIRCommon version '2.0.0' called FHIRCommon
//include defectHelper version '1.0.000' called defectHelper

codesystem "SNOMEDCT": 'http://snomed.info/sct'

code "Pregnancy": '72892002' from "SNOMEDCT" display 'Pregnancy'
code "Breastfeeding": '413712001' from "SNOMEDCT" display 'Breastfeeding (finding)'

parameter "Measurement Period" Interval<DateTime>
  default Interval[@2026-01-01T00:00:00.000Z, @2027-01-01T00:00:00.000Z)

context Patient

/*
############################  FAILING (I-28)  ################################
# Each of these reproduces the translator error on the new engine:
#   Could not resolve call to operator prevalenceInterval with signature
#   (choice<USQualityCore.ConditionEncounterDiagnosis,
#           USQualityCore.ConditionProblemsHealthConcerns>)
###############################################################################
*/

// 2028-08-28: Can't get the Choice union to work
// // A) Union -> direct .prevalenceInterval() on the Choice element (CMS347/CMS69 pattern).
// define "FAILING Plain Union":
//   exists (
//     ( [ConditionProblemsHealthConcerns: "Pregnancy"]
//         union [ConditionEncounterDiagnosis: "Pregnancy"] ) PregnancyDx1
//       where PregnancyDx1.prevalenceInterval() overlaps "Measurement Period"
//   )

// // B) Union -> .verified() -> .prevalenceInterval() on the Choice element (CMS117/CMS136/CMS138/CMS153/CMS155 pattern).
// define "FAILING Verified Union":
//   exists (
//     ( ( [ConditionProblemsHealthConcerns: "Pregnancy"]
//           union [ConditionEncounterDiagnosis: "Pregnancy"] ).verified() ) PregnancyDx2
//       where PregnancyDx2.prevalenceInterval() overlaps "Measurement Period"
//   )

/*
#############################  PASSING (FIX)  ################################
# Equivalent working replacement: single base FHIR.Condition retrieve, so the
# element type is FHIR.Condition and `prevalenceInterval`/`verified` resolve.
# This is the CMS125-proven pattern.
###############################################################################
*/

// C) Base FHIR.Condition retrieve -> direct .prevalenceInterval().
define "PASSING Plain":
  exists (
    [FHIR.Condition: "Pregnancy"] PregnancyDx3
      where PregnancyDx3.prevalenceInterval() overlaps "Measurement Period"
  )

// D) Base FHIR.Condition retrieve -> .verified() -> .prevalenceInterval().
//    NOTE: fluent-call result (`...verified()`) must be wrapped in parens before a source
//    alias, exactly as the proven CMS125 pattern does: `( ( retrieve ).verified() ) Alias`.
define "PASSING Verified":
  exists (
    ( ( [FHIR.Condition: "Pregnancy"] ).verified() ) PregnancyDx4
      where PregnancyDx4.prevalenceInterval() overlaps "Measurement Period"
  )

// E) Multi-code base FHIR.Condition union (mirrors CMS347 Breastfeeding/Rhabdomyolysis
//    and CMS117 4-way DTaP/HepB/HepA/Varicella sites) — still no Choice type.
//    Same note as D: wrap the `.verified()` result in parens before the alias.
define "PASSING MultiCode Union":
  exists (
    ( ( [FHIR.Condition: "Pregnancy"]
          union [FHIR.Condition: "Breastfeeding"] ).verified() ) PregnancyDx5
      where PregnancyDx5.prevalenceInterval() overlaps "Measurement Period"
  )
