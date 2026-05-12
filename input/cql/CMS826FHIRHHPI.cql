/*
NOTE: For use by March 2026 US Realm Connectathon participants for internal use only. Not for use or distribution in commercial products.
*/
library CMS826FHIRHHPI version '1.1.000'

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

codesystem "LOINC": 'http://loinc.org'

valueset "Encounter Inpatient": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.666.5.307'
valueset "Not Present On Admission or Documentation Insufficient to Determine": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113762.1.4.1147.198'
valueset "Present on Admission or Clinically Undetermined": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113762.1.4.1147.197'
valueset "Pressure Injury Deep Tissue": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113762.1.4.1147.112'
valueset "Pressure Injury Deep Tissue Diagnoses": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113762.1.4.1147.194'
valueset "Pressure Injury Stage 2, 3, 4 or Unstageable": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113762.1.4.1147.113'
valueset "Pressure Injury Stage 2, 3, 4, or Unstageable Diagnoses": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113762.1.4.1147.196'

code "Physical findings of Skin": '8709-8' from "LOINC" display 'Physical findings of Skin'

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
  "Encounter With Age 18 And Older"

define "Denominator":
  "Initial Population"

define "Denominator Exclusions":
  "Encounter With Deep Tissue Pressure Injury POA By Indicator Or Skin Exam Within First 72 Hours"
    union "Encounter With Stage 2, 3, 4 Or Unstageable Pressure Injury POA"

define "Numerator":
  "Encounter With New Deep Tissue Pressure Injury"
    union "Encounter With New Stage 2, 3, 4 Or Unstageable Pressure Injury"

define "Encounter With Age 18 And Older":
  ["Encounter": "Encounter Inpatient"] InpatientEncounter
    where AgeInYearsAt(date from start of InpatientEncounter.period) >= 18
      and InpatientEncounter.period ends during day of "Measurement Period"
      and InpatientEncounter.status = 'finished'

define "Encounter With Deep Tissue Pressure Injury POA By Indicator Or Skin Exam Within First 72 Hours":
  "Encounter With Deep Tissue Pressure Injury POA By Indicator"
    union "Encounter With Deep Tissue Pressure Injury POA By Skin Exam Within First 72 Hours"

define "Encounter With Stage 2, 3, 4 Or Unstageable Pressure Injury POA":
  "Encounter With Stage 2, 3, 4, Or Unstageable Pressure Injury Present On Admission By POA Indicator"
    union "Encounter With Stage 2, 3, 4 Or Unstageable Pressure Injury POA By Skin Exam Within 24 Hours"

define "Encounter With New Deep Tissue Pressure Injury":
  "Encounter With New Deep Tissue Pressure Injury Not POA By Indicator"
    union "Encounter With New Deep Tissue Pressure Injury By Skin Exam After First 72 Hours"

define "Encounter With New Stage 2, 3, 4 Or Unstageable Pressure Injury":
  "Encounter With New Stage 2, 3, 4 Or Unstageable Pressure Injury Not POA By Indicator"
    union "Encounter With New Stage 2, 3, 4 Or Unstageable Pressure Injury By Skin Exam After First 24 Hours"

define "Encounter With Deep Tissue Pressure Injury POA By Indicator":
  "Encounter With Age 18 And Older" InpatientHospitalization
    where InpatientHospitalization.isDiagnosisPresentOnAdmission ( "Pressure Injury Deep Tissue Diagnoses", "Present on Admission or Clinically Undetermined" )

define "Encounter With Deep Tissue Pressure Injury POA By Skin Exam Within First 72 Hours":
  "Encounter With Age 18 And Older" InpatientHospitalization
    let hospitalizationPeriod: InpatientHospitalization.hospitalizationWithObservation ( )
    with "Skin Exams With Pressure Injury" SkinExam
      such that SkinExam.effective.toInterval ( ) starts during Interval[start of hospitalizationPeriod, start of hospitalizationPeriod + 72 hours]

define "Encounter With Stage 2, 3, 4, Or Unstageable Pressure Injury Present On Admission By POA Indicator":
  "Encounter With Age 18 And Older" InpatientHospitalization
    where InpatientHospitalization.isDiagnosisPresentOnAdmission ( "Pressure Injury Stage 2, 3, 4, or Unstageable Diagnoses", "Present on Admission or Clinically Undetermined" )

define "Encounter With Stage 2, 3, 4 Or Unstageable Pressure Injury POA By Skin Exam Within 24 Hours":
  "Encounter With Age 18 And Older" InpatientHospitalization
    let hospitalizationPeriod: InpatientHospitalization.hospitalizationWithObservation ( )
    with "Skin Exams With Pressure Injury" SkinExam
      such that SkinExam.effective.toInterval ( ) starts during Interval[start of hospitalizationPeriod, start of hospitalizationPeriod + 24 hours]

define "Encounter With New Deep Tissue Pressure Injury Not POA By Indicator":
  "Encounter With Age 18 And Older" InpatientHospitalization
    where InpatientHospitalization.isDiagnosisPresentOnAdmission ( "Pressure Injury Deep Tissue Diagnoses", "Not Present On Admission or Documentation Insufficient to Determine" )

define "Encounter With New Deep Tissue Pressure Injury By Skin Exam After First 72 Hours":
  "Encounter With Age 18 And Older" InpatientHospitalization
    let hospitalizationPeriod: InpatientHospitalization.hospitalizationWithObservation ( )
    with "Skin Exams With Pressure Injury" SkinExam
      such that SkinExam.effective.toInterval ( ) starts during Interval[start of hospitalizationPeriod + 72 hours, end of hospitalizationPeriod]

define "Encounter With New Stage 2, 3, 4 Or Unstageable Pressure Injury Not POA By Indicator":
  "Encounter With Age 18 And Older" InpatientHospitalization
    where InpatientHospitalization.isDiagnosisPresentOnAdmission ( "Pressure Injury Stage 2, 3, 4, or Unstageable Diagnoses", "Not Present On Admission or Documentation Insufficient to Determine" )

define "Encounter With New Stage 2, 3, 4 Or Unstageable Pressure Injury By Skin Exam After First 24 Hours":
  "Encounter With Age 18 And Older" InpatientHospitalization
    let hospitalizationPeriod: InpatientHospitalization.hospitalizationWithObservation ( )
    with "Skin Exams With Pressure Injury" SkinExam
      such that SkinExam.effective.toInterval ( ) starts during Interval[start of hospitalizationPeriod + 24 hours, end of hospitalizationPeriod]

define "Clinical Skin Exams With Pressure Injury":
  ["ObservationClinicalResult": "Physical findings of Skin"] ClinicalSkinExam
    where ClinicalSkinExam.isIn ( "Pressure Injury Stage 2, 3, 4 or Unstageable" )

define "Simple Skin Exams With Pressure Injury":
  ["SimpleObservation": "Physical findings of Skin"] ObsSkinExam
    where ObsSkinExam.isIn ( "Pressure Injury Stage 2, 3, 4 or Unstageable" )

// @description Skin exams may be either a SimpleObservation or an ObservationClinicalResult in QI-Core. The definition below allows both QI-Core resource representations for more comprehensive data capture.


define "Skin Exams With Pressure Injury":
  "Clinical Skin Exams With Pressure Injury"
    union "Simple Skin Exams With Pressure Injury"

// @description This function, attached to either a SimpleObseration or an ObservationClinicalResult, is used to determine if the observation is completed and its value is in the given value set
// @example  ExampleObservation.isIn("Pressure Injury Stage 2, 3, 4 or Unstageable")



define fluent function isIn(observation Choice<"SimpleObservation", "ObservationClinicalResult">, vset System.ValueSet):
  observation.status in { 'final', 'amended', 'corrected' }
    and observation.effective.toInterval ( ) during "Measurement Period"
    and case
      when observation is SimpleObservation then ( observation as SimpleObservation ).value as FHIR.CodeableConcept in vset
      when observation is ObservationClinicalResult then ( observation as ObservationClinicalResult ).value as FHIR.CodeableConcept in vset 
      else null end