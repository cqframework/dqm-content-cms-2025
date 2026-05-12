/*
NOTE: For use by March 2026 US Realm Connectathon participants for internal use only. Not for use or distribution in commercial products.
*/
library CMS142FHIRCommWithDrManagingDiab version '1.1.000'

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

codesystem "SNOMEDCT": 'http://snomed.info/sct'
codesystem "ActCode": 'http://terminology.hl7.org/CodeSystem/v3-ActCode'

valueset "Care Services in Long-Term Residential Facility": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.101.12.1014'
valueset "Diabetic Retinopathy": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.327'
valueset "Level of Severity of Retinopathy Findings": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1283'
valueset "Macular Edema Findings Present": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1320'
valueset "Macular Exam": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1251'
valueset "Medical Reason": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1007'
valueset "Nursing Facility Visit": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.101.12.1012'
valueset "Office Visit": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.101.12.1001'
valueset "Ophthalmological Services": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1285'
valueset "Outpatient Consultation": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.101.12.1008'
valueset "Patient Reason": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1008'
valueset "Macular Edema Findings Absent": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.2.1391'

code "virtual": 'VR' from "ActCode" display 'virtual'
// code "Macular edema absent (situation)": '428341000124108' from "SNOMEDCT" display 'Macular edema absent (situation)'

code "AMB": 'AMB' from "ActCode" display 'Ambulatory'

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
  AgeInYearsAt(date from start of "Measurement Period") >= 18
    and exists "Diabetic Retinopathy Encounter"

define "Denominator":
  "Initial Population"
    and exists "Macular Exam Performed"

define "Numerator":
  exists "Level of Severity of Retinopathy Findings Communicated"
    and ( exists "Macular Edema Absence Communicated"
        or exists "Macular Edema Presence Communicated"
    )

define "Denominator Exceptions":
  exists "Medical or Patient Reason for Not Communicating Level of Severity of Retinopathy"
    or exists "Medical or Patient Reason for Not Communicating Absence of Macular Edema"
    or exists "Medical or Patient Reason for Not Communicating Presence of Macular Edema"

define "Qualifying Encounter During Day of Measurement Period":
  ( ["Encounter": "Office Visit"]
    union ["Encounter": "Ophthalmological Services"]
    union ["Encounter": "Outpatient Consultation"]
    union ["Encounter": "Care Services in Long-Term Residential Facility"]
    union ["Encounter": "Nursing Facility Visit"] ) QualifyingEncounter
    where QualifyingEncounter.period during day of "Measurement Period"
      and QualifyingEncounter.status = 'finished'
      and QualifyingEncounter.class !~ "virtual"

define "Diabetic Retinopathy Encounter":
  "Qualifying Encounter During Day of Measurement Period" ValidQualifyingEncounter
    with ( ["ConditionProblemsHealthConcerns": "Diabetic Retinopathy"]
      union ["ConditionEncounterDiagnosis": "Diabetic Retinopathy"] ) DiabeticRetinopathy
      such that DiabeticRetinopathy.onset.toInterval ( ) overlaps day of ValidQualifyingEncounter.period
        and DiabeticRetinopathy.isVerified ( )

define "Macular Exam Performed":
  ["ObservationClinicalResult": "Macular Exam"] MacularExam
    with "Diabetic Retinopathy Encounter" EncounterDiabeticRetinopathy
      such that MacularExam.effective.toInterval ( ) during EncounterDiabeticRetinopathy.period
    where MacularExam.value is not null
      and MacularExam.status in { 'final', 'amended', 'corrected' }

define "Results of Dilated Macular or Fundus Exam Communicated":
  exists "Level of Severity of Retinopathy Findings Communicated"
    and ( exists "Macular Edema Absence Communicated"
        or exists "Macular Edema Presence Communicated"
    )

define "Level of Severity of Retinopathy Findings Communicated":
  ["Communication": category in "Level of Severity of Retinopathy Findings"] LevelOfSeverityCommunicated
    with "Diabetic Retinopathy Encounter" EncounterDiabeticRetinopathy
      such that LevelOfSeverityCommunicated.sent after start of EncounterDiabeticRetinopathy.period
        and LevelOfSeverityCommunicated.sent during day of "Measurement Period"
    where LevelOfSeverityCommunicated.status = 'completed'

define "Macular Edema Absence Communicated":
  ["Communication": category in "Macular Edema Findings Absent"] MacularEdemaAbsentCommunicated
    with "Diabetic Retinopathy Encounter" EncounterDiabeticRetinopathy
      such that MacularEdemaAbsentCommunicated.sent after start of EncounterDiabeticRetinopathy.period
        and MacularEdemaAbsentCommunicated.sent during day of "Measurement Period"
    where MacularEdemaAbsentCommunicated.status = 'completed'

define "Macular Edema Presence Communicated":
  ["Communication": category in "Macular Edema Findings Present"] MacularEdemaPresentCommunicated
    with "Diabetic Retinopathy Encounter" EncounterDiabeticRetinopathy
      such that MacularEdemaPresentCommunicated.sent after start of EncounterDiabeticRetinopathy.period
        and MacularEdemaPresentCommunicated.sent during "Measurement Period"
    where MacularEdemaPresentCommunicated.status = 'completed'

define "Medical or Patient Reason for Not Communicating Level of Severity of Retinopathy":
  [CommunicationNotDone: category in "Level of Severity of Retinopathy Findings"] LevelOfSeverityNotCommunicated
    with "Diabetic Retinopathy Encounter" EncounterDiabeticRetinopathy
      such that LevelOfSeverityNotCommunicated.recorded () during day of EncounterDiabeticRetinopathy.period
    where ( LevelOfSeverityNotCommunicated.statusReason in "Medical Reason"
        or LevelOfSeverityNotCommunicated.statusReason in "Patient Reason"
    )

define "Medical or Patient Reason for Not Communicating Presence of Macular Edema":
  [CommunicationNotDone: category in "Macular Edema Findings Present"] MacularEdemaPresentNotCommunicated
    with "Diabetic Retinopathy Encounter" EncounterDiabeticRetinopathy
      such that MacularEdemaPresentNotCommunicated.sent during day of EncounterDiabeticRetinopathy.period
    where ( MacularEdemaPresentNotCommunicated.statusReason in "Medical Reason"
        or MacularEdemaPresentNotCommunicated.statusReason in "Patient Reason"
    ) 

/* Note: 
below definition workaround for 
https://oncprojectracking.healthit.gov/support/browse/CQLIT-371. Using value set workaround has been applied for now
but when QI Core STU 5 gets in the tool, it may be reverted back to a DRC */


define "Medical or Patient Reason for Not Communicating Absence of Macular Edema":
  [CommunicationNotDone: category in "Macular Edema Findings Absent"] MacularEdemaAbsentNotCommunicated
    with "Diabetic Retinopathy Encounter" EncounterDiabeticRetinopathy
      such that MacularEdemaAbsentNotCommunicated.sent during day of EncounterDiabeticRetinopathy.period
    where ( MacularEdemaAbsentNotCommunicated.statusReason in "Medical Reason"
        or MacularEdemaAbsentNotCommunicated.statusReason in "Patient Reason"
    )

define fluent function isVerified(condition Choice<ConditionEncounterDiagnosis, ConditionProblemsHealthConcerns>):
  condition.verificationStatus is not null implies ( condition.verificationStatus ~ Status."confirmed"
      or condition.verificationStatus ~ Status."unconfirmed"
      or condition.verificationStatus ~ Status."provisional"
      or condition.verificationStatus ~ Status."differential"
  )