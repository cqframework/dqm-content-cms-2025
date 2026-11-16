library testCMS72IschemicStrokeEncounterCount

using USQualityCore version '0.1.0-cibuild'
using FHIR version '4.0.1'

include hl7.fhir.uv.cql.FHIRHelpers version '4.0.1' called FHIRHelpers
include CQMCommon version '5.1.000' called CQMCommon
include TJCOverall version '9.1.000' called TJC
include CMS72FHIRSTKAntithromboticDay2 called CMS72

parameter "Measurement Period" Interval<DateTime>
  default Interval[@2026-01-01T00:00:00.000Z, @2027-01-01T00:00:00.000Z)

context Patient

define "WithAge ids": TJC."Non Elective Inpatient Encounter With Age" E return E.id
define "WithAge count": Count(TJC."Non Elective Inpatient Encounter With Age")
define "Ischemic ids": TJC."Ischemic Stroke Encounter" E return E.id
define "PD per encounter":
  TJC."Non Elective Inpatient Encounter With Age" E
    return Tuple { id: E.id, pd: E.principalDiagnosis().diagnosis, claimDx: Count(E.claimDiagnosis()) }
define "Claims": [Claim] C return C.id

// population membership by encounter id
define "DenExcl ids": CMS72."Denominator Exclusions" E return E.id
define "Thrombolytic ids": CMS72."Encounter With Thrombolytic Therapy Given Prior To Arrival Or During Hospitalization" E return E.id
define "LessThan2Days ids": CMS72."Encounter Less Than Two Days" E return E.id
define "Numerator ids": CMS72."Numerator" E return E.id
