/*
NOTE: For use by March 2026 US Realm Connectathon participants for internal use only. Not for use or distribution in commercial products.
*/
library CMS1206FHIRCTOQR version '1.1.000'

using USQualityCore version '0.1.0-cibuild'
using USCore version '6.1.0-derived'
using FHIR version '4.0.1'

include hl7.fhir.uv.cql.FHIRHelpers version '4.0.1' called FHIRHelpers
include hl7.fhir.uv.cql.FHIRCommon version '2.0.0' called FHIRCommon
include hl7.fhir.us.cql.USCoreCommon version '2.0.0-ballot' called USCoreCommon
include hl7.fhir.us.cql.USCoreElements version '2.0.0-ballot' called USCoreElements

include USQualityCoreCommon version '0.1.0-cibuild' called USQualityCoreCommon
include SupplementalDataElements version '6.1.000' called SDE
include CQMCommon version '5.1.000' called CQMCommon
include AlaraCommonFunctions version '2.1.000' called AlaraCommonFunctions

codesystem "LOINC": 'http://loinc.org'

valueset "Encounter Inpatient": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.666.5.307'

code "CT dose and image quality category": '96914-7' from "LOINC" display 'CT dose and image quality category'
code "Full Body": 'LA31771-1' from "LOINC" display 'Full Body'

parameter "Measurement Period" Interval<DateTime>
  default Interval[@2026-01-01T00:00:00.000Z, @2027-01-01T00:00:00.000Z)

context Patient

define "Denominator":
  "Qualified Scan With Values"

// TODO: Note that this used to use a .coding contains "Full Body", presumably to allow for other codings, so long as at least Full Body is present
// But that is the definition of concept equivalent within CQL, so it should be the same to just use the ~ operator. Please confirm.
define "Denominator Exclusion":
  "Qualified Scan With Values" CTScanWithValues
    where ( CTScanWithValues.value as FHIR.CodeableConcept ) ~ "Full Body"

define "Initial Population":
  "Qualified Scan Without Inpatient Encounter"

define "Numerator":
  "Qualified Scan With Values" CTScanWithValues
    where CTScanWithValues.ctScanQualifies ( )

define "Qualified Scan With Values":
  "Qualified Scan Without Inpatient Encounter" CTScan
    where CTScan.globalNoiseValue ( ) is not null
      and CTScan.sizeAdjustedValue ( ) is not null
      and CTScan.value is not null

define "Qualified Scan Without Inpatient Encounter":
  "Qualified Scan" QualifiedCTScan
    without [Encounter: "Encounter Inpatient"] InpatientEncounter
      such that InpatientEncounter.status ~ 'finished'
        and InpatientEncounter.period ends during day of "Measurement Period"
        and QualifiedCTScan.effective.toInterval ( ) starts during InpatientEncounter.period

define "Qualified Scan":
  [USQualityCore.ObservationClinicalResult: "CT dose and image quality category"] CTScanResult
    where CTScanResult.status in { 'final', 'amended', 'corrected' }
      and CTScanResult.effective.toInterval ( ) ends during day of "Measurement Period"
      and AgeInYearsAt(date from start of "Measurement Period") >= 18

define "SDE Ethnicity":
  SDE."SDE Ethnicity"

define "SDE Payer":
  SDE."SDE Payer"

define "SDE Race":
  SDE."SDE Race"

define "SDE Sex":
  SDE."SDE Sex"