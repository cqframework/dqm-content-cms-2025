library testCMS104IschemicStrokeEncounterCount

using USQualityCore version '0.1.0-cibuild'
using FHIR version '4.0.1'

include hl7.fhir.uv.cql.FHIRHelpers version '4.0.1' called FHIRHelpers
include CQMCommon version '5.1.000' called CQMCommon
include TJCOverall version '9.1.000' called TJC
include CMS104FHIRSTKDCAntithrombotic called CMS104

parameter "Measurement Period" Interval<DateTime>
  default Interval[@2026-01-01T00:00:00.000Z, @2027-01-01T00:00:00.000Z)

context Patient

define "WithAge ids": TJC."Non Elective Inpatient Encounter With Age" E return E.id
define "PD per encounter":
  TJC."Non Elective Inpatient Encounter With Age" E
    return Tuple { id: E.id, pd: E.principalDiagnosis().diagnosis, claimDx: Count(E.claimDiagnosis()) }
define "IP ids": CMS104."Initial Population" E return E.id
define "DenExcl ids": CMS104."Denominator Exclusions" E return E.id
define "Numerator ids": CMS104."Numerator" E return E.id
define "DenExcep ids": CMS104."Denominator Exceptions" E return E.id
