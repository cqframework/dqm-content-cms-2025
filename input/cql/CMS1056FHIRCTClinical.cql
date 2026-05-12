/*
NOTE: For use by March 2026 US Realm Connectathon participants for internal use only. Not for use or distribution in commercial products.
*/
library CMS1056FHIRCTClinical version '1.1.000'

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

code "CT dose and image quality category": '96914-7' from "LOINC" display 'CT dose and image quality category'
code "Full Body": 'LA31771-1' from "LOINC" display 'Full Body'

parameter "Measurement Period" Interval<DateTime>
  default Interval[@2026-01-01T00:00:00.000Z, @2027-01-01T00:00:00.000Z)

context Patient

define "SDE Ethnicity":
  SDE."SDE Ethnicity"

define "SDE Payer":
  SDE."SDE Payer"

define "SDE Race":
  SDE."SDE Race"

define "SDE Sex":
  SDE."SDE Sex"

define "Patients with Qualifying CTScan":
  [ObservationClinicalResult: "CT dose and image quality category"] CTScanResult
    where CTScanResult.status in { 'final', 'amended', 'corrected' }
      and CTScanResult.effective.toInterval ( ) ends during day of "Measurement Period"
      and ( AgeInYearsAt(date from start of "Measurement Period") >= 18 )

define "Patients with Qualifying CTScan with Values":
  "Patients with Qualifying CTScan" CTScan
    where CTScan.globalNoiseValue ( ) is not null
      and CTScan.sizeAdjustedValue ( ) is not null
      and CTScan.value is not null

define "Initial Population":
  exists ( "Patients with Qualifying CTScan" )

define "Denominator":
  exists ( "Patients with Qualifying CTScan with Values" )

define "Denominator Exclusion":
  exists ( "Patients with Qualifying CTScan with Values" CTScanWithValues
      where ( CTScanWithValues.value as FHIR.CodeableConcept ) ~ "Full Body"
  )

define "Numerator":
  exists ( "Patients with Qualifying CTScan with Values" CTScanWithValues
      where CTScanWithValues.ctScanQualifies ( )
  )