/*
NOTE: For use by March 2026 US Realm Connectathon participants for internal use only. Not for use or distribution in commercial products.
*/
library CMS130FHIRColorectalCancerScrn version '1.1.000'

using USQualityCore version '0.1.0-cibuild'
using USCore version '6.1.0-derived'
using FHIR version '4.0.1'

include hl7.fhir.uv.cql.FHIRHelpers version '4.0.1' called FHIRHelpers
include hl7.fhir.uv.cql.FHIRCommon version '2.0.0' called FHIRCommon
include hl7.fhir.us.cql.USCoreCommon version '2.0.0-ballot' called USCoreCommon
include hl7.fhir.us.cql.USCoreElements version '2.0.0-ballot' called USCoreElements

include USQualityCoreCommon version '0.1.0-cibuild' called USQualityCoreCommon
include SupplementalDataElements version '6.1.000' called SDE
include Status version '2.1.000' called Status
include AdultOutpatientEncounters version '5.1.000' called AdultOutpatientEncounters
include AdvancedIllnessandFrailty version '2.1.000' called AIFrailLTCF
include Hospice version '7.1.000' called Hospice
include PalliativeCare version '2.1.000' called PalliativeCare

valueset "Colonoscopy": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.108.12.1020'
valueset "CT Colonography": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.108.12.1038'
valueset "Fecal Occult Blood Test (FOBT)": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.198.12.1011'
valueset "sDNA FIT Test": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.108.12.1039'
valueset "Flexible Sigmoidoscopy": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.198.12.1010'
valueset "Malignant Neoplasm of Colon": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.108.12.1001'
valueset "Total Colectomy": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.198.12.1019'

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

define "Initial Population":
  AgeInYearsAt(date from 
    end of "Measurement Period"
  ) in Interval[46, 75]
    and exists AdultOutpatientEncounters."Qualifying Encounters"

define "Denominator":
  "Initial Population"

define "Denominator Exclusions":
  Hospice."Has Hospice Services"
    or exists "Malignant Neoplasm"
    or exists "Total Colectomy Performed"
    or AIFrailLTCF."Is Age 66 or Older with Advanced Illness and Frailty"
    or AIFrailLTCF."Is Age 66 or Older Living Long Term in a Nursing Home"
    or PalliativeCare."Has Palliative Care in the Measurement Period"

define "Numerator":
  exists "Fecal Occult Blood Test Performed"
    or exists "Stool DNA with FIT Test Performed"
    or exists "Flexible Sigmoidoscopy Performed"
    or exists "CT Colonography Performed"
    or exists "Colonoscopy Performed"

define "Fecal Occult Blood Test Performed":
  ( ( [LaboratoryResultObservation: "Fecal Occult Blood Test (FOBT)"] ).isLaboratoryTestPerformed ( ) ) FecalOccultResult
    where FecalOccultResult.value is not null
      and FecalOccultResult.effective.latest ( ) during day of "Measurement Period"

define "Malignant Neoplasm":
  ( ( [Condition: "Malignant Neoplasm of Colon"] ).verified ( ) ) ColorectalCancer
    where ColorectalCancer.prevalenceInterval ( ) starts on or before day of end of "Measurement Period"

define "Total Colectomy Performed":
  ( ( [Procedure: "Total Colectomy"] ).isProcedurePerformed ( ) ) Colectomy
    where Colectomy.performed.toInterval ( ) ends on or before day of end of "Measurement Period"

define "Stratification 1":
  AgeInYearsAt(date from 
    end of "Measurement Period"
  ) in Interval[46, 49]

define "Stratification 2":
  AgeInYearsAt(date from 
    end of "Measurement Period"
  ) in Interval[50, 75]

define "Colonoscopy Performed":
  ( ( [Procedure: "Colonoscopy"] ).isProcedurePerformed ( ) ) ColonoscopyProcedure
    where ColonoscopyProcedure.performed.toInterval ( ) ends during day of Interval[start of "Measurement Period" - 9 years, end of "Measurement Period"]

define "Flexible Sigmoidoscopy Performed":
  ( ( [Procedure: "Flexible Sigmoidoscopy"] ).isProcedurePerformed ( ) ) FlexibleSigmoidoscopy
    where FlexibleSigmoidoscopy.performed.toInterval ( ) ends during day of Interval[start of "Measurement Period" - 4 years, end of "Measurement Period"]

define "CT Colonography Performed":
  ( ( [ObservationClinicalResult: "CT Colonography"] ).isDiagnosticStudyPerformed ( ) ) Colonography
    where Colonography.effective.toInterval ( ) ends during day of Interval[start of "Measurement Period" - 4 years, end of "Measurement Period"]

define "Stool DNA with FIT Test Performed":
  ( ( [LaboratoryResultObservation: "sDNA FIT Test"] ).isLaboratoryTestPerformed ( ) ) sDNATest
    where sDNATest.value is not null
      and sDNATest.effective.latest ( ) during day of Interval[start of "Measurement Period" - 2 years, end of "Measurement Period"]