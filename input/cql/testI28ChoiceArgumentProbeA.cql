/*
###############################################################################
# testI28ChoiceArgumentProbeA — TEMPORARY probe for the I-28 root cause (part A)
###############################################################################
#
# QUESTION
#   I-28's recorded root cause is that the union of the two sibling USQualityCore
#   condition profiles types its result as
#       List<Choice<ConditionEncounterDiagnosis, ConditionProblemsHealthConcerns>>
#   and cql-to-elm cannot resolve `.prevalenceInterval()` on it, because
#   `ChoiceType` does not override `isSubTypeOf` (so the whole-argument subtype
#   test against FHIRCommon's `prevalenceInterval(Condition)` fails) and
#   `findChoiceConversion` tests each member with `findConversion`, which has no
#   subtype rule of its own.
#
#   The recorded conclusion (testE15ConditionUnionPrevalence.cql:38-51) was that
#   re-declaring the QI-Core overload (QICoreCommon.cql:452) is NOT viable:
#   "a Choice is not accepted as a fluent function parameter type". That claim is
#   contradicted by the tree: CMS22:418, CMS1173:211, CMS506:174 and ~20 other
#   measures declare local `isVerified(Choice<...>)` functions, three of them are
#   actually CALLED, and those measures pass 220/220, 260/260 and 204/204 cells.
#   So a Choice-typed PARAMETER works.
#
#   Untested anywhere in the tree is a Choice-typed ARGUMENT (the union) reaching a
#   Choice-typed parameter. That is this file's question. Part B
#   (testI28ChoiceArgumentProbeB.cql) tests whether the QI-Core overload can be
#   reintroduced without recursing.
#
# PREDICTION
#   `Signature.isConvertibleTo` tests `first.isSubTypeOf(second)` on the whole
#   argument before any conversion; `ChoiceType` inherits `BaseDataType.isSubTypeOf`,
#   which falls through to `currentType == other` — and `==` is `equals`, which
#   `ChoiceType` DOES override by comparing its type list. Two structurally equal
#   Choice types should satisfy the test. Prediction: B and C compile and bind to
#   the local overload.
#
# DEFINES
#   A  I-28 control: union -> .prevalenceInterval()      expect COMPILE FAIL
#   B  PROBE:        union -> local probeInterval(Choice<>)  expect COMPILE OK, binds local
#   C  control:      union -> local isVerified(Choice<>) expect COMPILE OK, binds local
#   D  workaround:   base [FHIR.Condition] -> .prevalenceInterval()  expect COMPILE OK
#
#   This file deliberately declares NO local `prevalenceInterval`, so A keeps
#   reproducing the original I-28 failure unmodified.
#
# READ: cql_view_elm on this path; FunctionRef signature + libraryName per define,
#   and each local FunctionDef's operandTypeSpecifier (expected to be the
#   degenerate choice: [Condition, Condition], because both profiles carry
#   target="Condition" in usqualitycore-modelinfo-0.1.0-cibuild.xml:937/:982).
#
# DISPOSAL
#   Retained as a hand-off artifact (2026-10-19), alongside
#   testE15ConditionUnionPrevalence / testE15Passing, and recorded in
#   defect-tracking/change-log.md. Not measure content; no CMS measure includes it.
#   Like testI37RecordedAmbiguousOverload, PROBE A fails to translate on purpose —
#   that failing define is the point of this file.
###############################################################################
*/
library testI28ChoiceArgumentProbeA version '0.0.000'

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
##############################  A) I-28 CONTROL  ##############################
# The recorded failing shape. Expected: Could not resolve call to operator
# prevalenceInterval with signature (choice<USQualityCore.ConditionEncounterDiagnosis,
# USQualityCore.ConditionProblemsHealthConcerns>).
###############################################################################
*/
define "PROBE A - union to base prevalenceInterval":
  exists (
    "Pregnancy Dx Union" PregnancyDxA
      where PregnancyDxA.prevalenceInterval() overlaps "Measurement Period"
  )

/*
############################  B) THE PROBE ITSELF  ############################
# Same union, call target is a uniquely named local function taking the Choice.
# A unique name removes any shadowing question, so a compile failure here is
# unambiguously about Choice-argument -> Choice-parameter resolution.
###############################################################################
*/
define "PROBE B - union to local probeInterval(Choice)":
  exists (
    "Pregnancy Dx Union" PregnancyDxB
      where PregnancyDxB.probeInterval() overlaps "Measurement Period"
  )

/*
###############################  C) CONTROL  ##################################
# Identical shape to B under a name the tree already proves works with a profile
# argument (CMS22 / CMS1173 / CMS506). Separates "Choice argument fails" from
# "this particular function body fails".
###############################################################################
*/
define "PROBE C - union to local isVerified(Choice)":
  exists (
    "Pregnancy Dx Union" PregnancyDxC
      where PregnancyDxC.isVerified( )
  )

/*
#############################  D) WORKAROUND  #################################
# The pattern currently applied across all 30 measures. Control.
###############################################################################
*/
define "PROBE D - base retrieve to base prevalenceInterval":
  exists (
    [FHIR.Condition: "Pregnancy"] PregnancyDxD
      where PregnancyDxD.prevalenceInterval() overlaps "Measurement Period"
  )

/*
##############################  SHARED BITS  ##################################
*/
define "Pregnancy Dx Union":
  ( [ConditionProblemsHealthConcerns: "Pregnancy"]
      union [ConditionEncounterDiagnosis: "Pregnancy"] ) PregnancyDx
    where PregnancyDx.clinicalStatus is not null

define fluent function probeInterval(condition Choice<ConditionProblemsHealthConcerns, ConditionEncounterDiagnosis>):
  if condition is ConditionProblemsHealthConcerns then
    (condition as ConditionProblemsHealthConcerns).prevalenceInterval()
  else
    (condition as ConditionEncounterDiagnosis).prevalenceInterval()

define fluent function isVerified(condition Choice<ConditionProblemsHealthConcerns, ConditionEncounterDiagnosis>):
  condition.verificationStatus is not null implies ( condition.verificationStatus ~ FHIRCommon."confirmed"
      or condition.verificationStatus ~ FHIRCommon."unconfirmed"
      or condition.verificationStatus ~ FHIRCommon."provisional"
      or condition.verificationStatus ~ FHIRCommon."differential"
  )
