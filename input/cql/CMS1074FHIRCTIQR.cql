
/*
NOTE: For use by March 2026 US Realm Connectathon participants for internal use only. Not for use or distribution in commercial products.
*/
library CMS1074FHIRCTIQR version '1.1.000'

using USQualityCore version '0.1.0-cibuild'
using USCore version '6.1.0-derived'
using FHIR version '4.0.1'

include hl7.fhir.uv.cql.FHIRHelpers version '4.0.1' called FHIRHelpers
include hl7.fhir.uv.cql.FHIRCommon version '2.0.0' called FHIRCommon
include hl7.fhir.us.cql.USCoreCommon version '2.0.0-ballot' called USCoreCommon
include hl7.fhir.us.cql.USCoreElements version '2.0.0-ballot' called USCoreElements

include CQMCommon version '5.1.000' called CQMCommon
include USQualityCoreCommon version '0.1.0-cibuild' called USQualityCoreCommon
include SupplementalDataElements version '6.1.000' called SDE
include Status version '2.1.000' called Status
include AlaraCommonFunctions version '2.1.000' called AlaraCommon

codesystem "LOINC": 'http://loinc.org'

valueset "Encounter Inpatient": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.666.5.307'

code "CT dose and image quality category": '96914-7' from "LOINC" display 'CT dose and image quality category'
code "Full Body": 'LA31771-1' from "LOINC" display 'Full Body'

parameter "Measurement Period" Interval<DateTime>
  default Interval[@2026-01-01T00:00:00.000Z, @2027-01-01T00:00:00.000Z)

context Patient

define "Qualifying Inpatient Encounters":
  ["Encounter": "Encounter Inpatient"] InpatientEncounter
    where InpatientEncounter.status ~ 'finished'
      and InpatientEncounter.period ends during day of "Measurement Period"
      and AgeInYearsAt(date from start of "Measurement Period") >= 18

define "SDE Ethnicity":
  SDE."SDE Ethnicity"

define "SDE Payer":
  SDE."SDE Payer"

define "SDE Race":
  SDE."SDE Race"

define "SDE Sex":
  SDE."SDE Sex"

define "Numerator":
  "Qualifying Scan With Values" CTScanWithValues
    where CTScanWithValues.ctScanQualifies ( )

define "Initial Population":
  "Qualifying Scan During Inpatient Encounter"

define "Denominator":
  "Qualifying Scan With Values"

define "Denominator Exclusion":
  "Qualifying Scan With Values" CTScanWithValues
    where ( CTScanWithValues.value as FHIR.CodeableConcept ) ~ "Full Body"

define "Qualifying Scan With Values":
  "Qualifying Scan During Inpatient Encounter" CTScan
    where CTScan.globalNoiseValue ( ) is not null
      and CTScan.sizeAdjustedValue ( ) is not null
      and CTScan.value is not null

define "Qualifying Scan During Inpatient Encounter":
  [ObservationClinicalResult: "CT dose and image quality category"] CTScan
    with "Qualifying Inpatient Encounters" InpatientEncounters
      such that CTScan.status in { 'final', 'amended', 'corrected' }
        and CTScan.effective.toInterval ( ) starts during InpatientEncounters.period
        and CTScan.effective.toInterval ( ) ends during day of "Measurement Period"