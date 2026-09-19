/*
###############################################################################
# testE15Passing — ISOLATED PASSING (FIX) constructs for I-28
###############################################################################
#
# PURPOSE
#   Isolation library for I-28 (defect-tracking/known-issues.md). The 3 PASSING
#   defines from testE15ConditionUnionPrevalence.cql, in a library with NOTHING
#   else, so the translator's result is a clean green signal attributable 1:1 to
#   the base `FHIR.Condition` retrieve + `.verified()` + `.prevalenceInterval()`
#   pattern (the proven CMS125 form). If this library translates without errors,
#   the fix is confirmed and the FAILING variant in
#   testE15ConditionUnionPrevalence.cql isolates the union->Choice failure.
#
#   Each define uses a single base `FHIR.Condition` retrieve (both sibling
#   profiles derive from `FHIR.Condition`), so no union-built Choice type is ever
#   formed and `prevalenceInterval`/`verified` resolve normally.
#
# REGISTRATION
#   - input/resources/library/testE15Passing.json      (id/version 0.0.000)
#   - input/resources/measure/testE15Passing.json      (measure + library ref)
#   fixture: input/tests/measure/testE15Passing/...
###############################################################################
library testE15Passing version '0.0.000'

using USQualityCore version '0.1.0-cibuild'
using USCore version '6.1.0-derived'
using FHIR version '4.0.1'

include hl7.fhir.uv.cql.FHIRHelpers version '4.0.1' called FHIRHelpers
include hl7.fhir.uv.cql.FHIRCommon version '2.0.0' called FHIRCommon

codesystem "SNOMEDCT": 'http://snomed.info/sct'

code "Pregnancy": '72892002' from "SNOMEDCT" display 'Pregnancy'
code "Breastfeeding": '413712001' from "SNOMEDCT" display 'Breastfeeding (finding)'

parameter "Measurement Period" Interval<DateTime>

context Patient

// C) Base FHIR.Condition retrieve -> direct .prevalenceInterval().
define "PASSING Plain":
  exists (
    [FHIR.Condition: "Pregnancy"] PregnancyDx
      where PregnancyDx.prevalenceInterval() overlaps "Measurement Period"
  )

// D) Base FHIR.Condition retrieve -> .verified() -> .prevalenceInterval().
//    NOTE: fluent-call result (`...verified()`) must be wrapped in parens before a source
//    alias, exactly as the proven CMS125 pattern: `( ( retrieve ).verified() ) Alias`.
define "PASSING Verified":
  exists (
    ( ( [FHIR.Condition: "Pregnancy"] ).verified() ) PregnancyDx
      where PregnancyDx.prevalenceInterval() overlaps "Measurement Period"
  )

// E) Multi-code base FHIR.Condition union -> .verified() -> .prevalenceInterval().
define "PASSING MultiCode Union":
  exists (
    ( ( [FHIR.Condition: "Pregnancy"]
          union [FHIR.Condition: "Breastfeeding"] ).verified() ) PregnancyDx
      where PregnancyDx.prevalenceInterval() overlaps "Measurement Period"
  )
