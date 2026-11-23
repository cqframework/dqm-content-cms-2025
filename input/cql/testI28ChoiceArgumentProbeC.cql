/*
###############################################################################
# testI28ChoiceArgumentProbeC — TEMPORARY probe for the I-28 root cause (part C)
###############################################################################
#
# WHAT PARTS A AND B ESTABLISHED
#   A: The union of the two sibling USQualityCore condition profiles types as
#      List<Choice<ConditionEncounterDiagnosis, ConditionProblemsHealthConcerns>>,
#      and `.prevalenceInterval()` on it reproduces the recorded I-28 error
#      verbatim:
#        Could not resolve call to operator prevalenceInterval with signature
#        (choice<USQualityCore.ConditionEncounterDiagnosis,
#                USQualityCore.ConditionProblemsHealthConcerns>).
#      A locally declared `probeInterval(Choice<...>)` DOES accept that union
#      argument, and a local `isVerified(Choice<...>)` does too. So the recorded
#      claim (testE15ConditionUnionPrevalence.cql:42-44, "a Choice is not accepted
#      as a fluent function parameter type") is WRONG: Choice parameters work.
#
#   B: The obstacle is the BODY of a reintroduced local
#      `prevalenceInterval(Choice<...>)`, not its parameter list:
#        - unqualified fluent body  -> circular reference (I-19), because a bare
#          profile-typed argument prefers the local Choice overload over
#          FHIRCommon's base Condition overload, so the narrowed self-call
#          re-binds to itself;
#        - qualified non-fluent body -> rejected: "is a fluent function and can
#          only be invoked with fluent syntax" (testE15:47-50 was right about
#          this half).
#      Delegation is therefore closed off in both directions.
#
# WHAT THIS FILE TESTS
#   The third option: keep the local Choice overload and INLINE the base body,
#   narrowing to a member instead of delegating. Nothing in the body is named
#   prevalenceInterval, so nothing can re-bind to the function itself.
#
# DEFINES
#   C1 probeTrivial(Choice<>) with a null body — resolution control: does a
#      trivially-bodied local Choice overload bind to the union argument?
#   C2 THE FIX CANDIDATE: local prevalenceInterval(Choice<>) with an inlined
#      body (structural stand-in for FHIRCommon's; omits the clinicalStatus
#      branch, which needs FHIRCommon's status codes and is not what is under
#      test). Expect: compiles, no circularity, union argument binds here.
#   C3 with C2 present: union -> .prevalenceInterval()   Expect: binds LOCAL,
#      i.e. the reintroduced overload intercepts the call that currently fails.
#   C4 with C2 present: base [FHIR.Condition] -> .prevalenceInterval()
#      Expect: binds FHIRCommon, not local. If instead it binds LOCAL, the
#      overload would hijack the 30-measure base-retrieve workaround and change
#      behavior beyond I-28 — a regression the fix must account for.
#
# READ: cql_view_elm on this path; per FunctionRef libraryName + signature, plus
#   the CqlToElmError annotations (message, errorType, startLine).
#
# DISPOSAL
#   Retained as a hand-off artifact (2026-10-19), alongside
#   testE15ConditionUnionPrevalence / testE15Passing, and recorded in
#   defect-tracking/change-log.md. Not measure content; no CMS measure includes it.
#   The C5 define was added after this file's first translation, so a language
#   server that still holds the earlier snapshot will not show it until the file
#   is re-read — it translates clean in a fresh session.
###############################################################################
*/
library testI28ChoiceArgumentProbeC version '0.0.000'

using USQualityCore version '0.1.0-cibuild'
using USCore version '6.1.0-derived'
using FHIR version '4.0.1'

include hl7.fhir.uv.cql.FHIRHelpers version '4.0.1' called FHIRHelpers
include hl7.fhir.uv.cql.FHIRCommon version '2.0.0' called FHIRCommon

codesystem "SNOMEDCT": 'http://snomed.info/sct'

code "Pregnancy": '72892002' from "SNOMEDCT" display 'Pregnancy'

parameter "Measurement Period" Interval<DateTime>
  default Interval[@2026-01-01T00:00:00.000Z, @2027-01-01T00:00:00.000Z)

context Patient

/*
############################  C1) RESOLUTION CONTROL  #########################
*/
define "PROBE C1 - union to probeTrivial(Choice) with null body":
  exists (
    "Pregnancy Dx Union" PregnancyDxC1
      where PregnancyDxC1.probeTrivial() overlaps "Measurement Period"
  )

/*
##########################  C2) THE FIX CANDIDATE  ############################
# Local Choice overload, base body inlined, narrowed member calls only.
###############################################################################
*/
define "PROBE C2 - union to local prevalenceInterval(Choice) with inlined body":
  exists (
    "Pregnancy Dx Union" PregnancyDxC2
      where PregnancyDxC2.prevalenceInterval() overlaps "Measurement Period"
  )

/*
#############################  C3) INTERCEPTION  ##############################
*/
define "PROBE C3 - union to .prevalenceInterval() with local overload present":
  exists (
    "Pregnancy Dx Union" PregnancyDxC3
      where PregnancyDxC3.prevalenceInterval() overlaps "Measurement Period"
  )

/*
########################  C4) WORKAROUND REGRESSION  ##########################
*/
define "PROBE C4 - base retrieve to .prevalenceInterval() with local overload present":
  exists (
    [FHIR.Condition: "Pregnancy"] PregnancyDxC4
      where PregnancyDxC4.prevalenceInterval() overlaps "Measurement Period"
  )

/*
###########################  C5) PROFILE ARGUMENT  ############################
# A bare profile-typed element (the shape used by the other 29 measures' current
# code) against the reintroduced local Choice overload. Per the binding rule that
# made CMS22:418 live, this is expected to bind LOCAL rather than FHIRCommon —
# i.e. adding the overload would re-route existing profile-argument call sites.
# Correctness then depends on the local body matching FHIRCommon's semantics.
###############################################################################
*/
define "PROBE C5 - single profile retrieve to .prevalenceInterval()":
  exists (
    [ConditionProblemsHealthConcerns: "Pregnancy"] PregnancyDxC5
      where PregnancyDxC5.prevalenceInterval() overlaps "Measurement Period"
  )

/*
##############################  SHARED BITS  ##################################
*/
define "Pregnancy Dx Union":
  ( [ConditionProblemsHealthConcerns: "Pregnancy"]
      union [ConditionEncounterDiagnosis: "Pregnancy"] ) PregnancyDx
    where PregnancyDx.clinicalStatus is not null

define fluent function probeTrivial(condition Choice<ConditionProblemsHealthConcerns, ConditionEncounterDiagnosis>):
  null as Interval<DateTime>

define fluent function prevalenceInterval(condition Choice<ConditionProblemsHealthConcerns, ConditionEncounterDiagnosis>):
  if condition is ConditionProblemsHealthConcerns then
    Interval[
      start of (condition as ConditionProblemsHealthConcerns).onset.toInterval(),
      end of (condition as ConditionProblemsHealthConcerns).abatementInterval()
    ]
  else
    Interval[
      start of (condition as ConditionEncounterDiagnosis).onset.toInterval(),
      end of (condition as ConditionEncounterDiagnosis).abatementInterval()
    ]
