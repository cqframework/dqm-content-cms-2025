/*
###############################################################################
# testPrevalenceIntervalNullPath — CMS71 "History of Atrial Ablation" isolation
###############################################################################
#
# PURPOSE
#   Separates the two candidate causes for CMS71 cases 0587a75d / 56ae006d
#   ("Encounter With A History Of Atrial Ablation" = [] -> Denominator 1->0):
#     (a) the us-quality-core-* profile retrieve returns empty (I-36), or
#     (b) FHIRCommon.prevalenceInterval() returns null for a Condition with no
#         clinicalStatus and no abatement (singleton-query null source, I-31).
#   Each define reproduces one step of the CMS71 join with the measure's own
#   retrieves. Compares FHIRCommon.prevalenceInterval() against a local if/else
#   variant with a closed null high bound.
#
# Upstream ticket: https://jira.hl7.org/browse/FHIR-59708 (re-authorship of FHIRCommon.cql
# prevalenceInterval(), specifying singleton-query over null returns null per CQL
# [Developer's Guide §Non-Retrieve Queries](https://cql.hl7.org/03-developersguide.html#non-retrieve-queries))
# Affected test cases: CMS71 '0587a75d', '56ae006d' (reproduces on 5.4.0 until fix lands)
#
# NOT REGISTERED - scaffold probe only, no Library/Measure resource.
###############################################################################
*/
library testPrevalenceIntervalNullPath version '0.0.000'

using USQualityCore version '0.1.0-cibuild'
using USCore version '6.1.0-derived'
using FHIR version '4.0.1'

include hl7.fhir.uv.cql.FHIRHelpers version '4.0.1' called FHIRHelpers
include hl7.fhir.uv.cql.FHIRCommon version '2.0.0' called FHIRCommon
include hl7.fhir.us.cql.USCoreCommon version '2.0.0-ballot' called USCoreCommon
include hl7.fhir.us.cql.USCoreElements version '2.0.0-ballot' called USCoreElements

include CQMCommon version '5.1.000' called CQMCommon
include USQualityCoreCommon version '0.1.0-cibuild' called USQualityCoreCommon
include Status version '2.1.000' called Status

include TJCOverall version '9.1.000' called TJC

valueset "History of Atrial Ablation": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113762.1.4.1110.76'

parameter "Measurement Period" Interval<DateTime>
  default Interval[@2026-01-01T00:00:00.000Z, @2027-01-01T00:00:00.000Z)

context Patient

// Step 1: do the CMS71 profile retrieves return the fixture Condition? (rules I-36 in/out)
define "Retrieve ProblemsHealthConcerns":
  ["ConditionProblemsHealthConcerns": "History of Atrial Ablation"]

define "Retrieve EncounterDiagnosis":
  ["ConditionEncounterDiagnosis": "History of Atrial Ablation"]

define "Ischemic Stroke Encounter Start":
  TJC."Ischemic Stroke Encounter" E
    return start of E.period

// Step 2: FHIRCommon.prevalenceInterval() vs local closed form, per retrieved Condition
define "ProblemsHealthConcerns Intervals":
  "Retrieve ProblemsHealthConcerns" C
    return {
      id: C.id,
      clinicalStatusIsNull: C.clinicalStatus is null,
      fhirCommon: C.prevalenceInterval(),
      localClosed: localPrevalenceInterval(C)
    }

define "EncounterDiagnosis Intervals":
  "Retrieve EncounterDiagnosis" C
    return {
      id: C.id,
      clinicalStatusIsNull: C.clinicalStatus is null,
      fhirCommon: C.prevalenceInterval(),
      localClosed: localPrevalenceInterval(C)
    }

// Step 3: the CMS71 join predicate, with each interval form (one join per profile,
// as in CMS71 -- a union of the two sibling profiles hits I-28)
define "Join FHIRCommon ProblemsHealthConcerns":
  TJC."Ischemic Stroke Encounter" E
    with "Retrieve ProblemsHealthConcerns" C
      such that C.prevalenceInterval() starts before start of E.period

define "Join FHIRCommon EncounterDiagnosis":
  TJC."Ischemic Stroke Encounter" E
    with "Retrieve EncounterDiagnosis" C
      such that C.prevalenceInterval() starts before start of E.period

define "Join LocalClosed ProblemsHealthConcerns":
  TJC."Ischemic Stroke Encounter" E
    with "Retrieve ProblemsHealthConcerns" C
      such that localPrevalenceInterval(C) starts before start of E.period

define "Join LocalClosed EncounterDiagnosis":
  TJC."Ischemic Stroke Encounter" E
    with "Retrieve EncounterDiagnosis" C
      such that localPrevalenceInterval(C) starts before start of E.period

define function localPrevalenceInterval(condition FHIR.Condition):
  if condition.clinicalStatus ~ FHIRCommon."active"
    or condition.clinicalStatus ~ FHIRCommon."recurrence"
    or condition.clinicalStatus ~ FHIRCommon."relapse" then
    Interval[start of condition.onset.toInterval(), end of condition.abatementInterval()]
  else if end of condition.abatementInterval() is null then
    Interval[start of condition.onset.toInterval(), null]
  else
    Interval[start of condition.onset.toInterval(), end of condition.abatementInterval()]
