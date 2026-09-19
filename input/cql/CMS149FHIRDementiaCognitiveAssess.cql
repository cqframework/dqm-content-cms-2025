library CMS149FHIRDementiaCognitiveAssess version '1.0.000'

using USQualityCore version '0.1.0-cibuild'
using USCore version '6.1.0-derived'
using FHIR version '4.0.1'

include hl7.fhir.uv.cql.FHIRHelpers version '4.0.1' called FHIRHelpers
include hl7.fhir.uv.cql.FHIRCommon version '2.0.0' called FHIRCommon
include hl7.fhir.us.cql.USCoreCommon version '2.0.0-ballot' called USCoreCommon
include hl7.fhir.us.cql.USCoreElements version '2.0.0-ballot' called USCoreElements

include SupplementalDataElements version '6.1.000' called SDE

include Status version '2.1.000' called Status
include USQualityCoreCommon version '0.1.0-cibuild' called USQualityCoreCommon

valueset "Behavioral or Neuropsych Assessment": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1023'
valueset "Care Services in Long Term Residential Facility": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.101.12.1014'
valueset "Cognitive Assessment": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1332'
valueset "Dementia & Mental Degenerations": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1005'
valueset "Face-to-Face Interaction": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.101.12.1048'
valueset "Home Healthcare Services": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.101.12.1016'
valueset "Nursing Facility Visit": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.101.12.1012'
valueset "Occupational Therapy Evaluation": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1011'
valueset "Office Visit": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.101.12.1001'
valueset "Outpatient Consultation": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.101.12.1008'
valueset "Patient Provider Interaction": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1012'
valueset "Patient Reason": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1008'
valueset "Psych Visit Diagnostic Evaluation": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1492'
valueset "Psych Visit Psychotherapy": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1496'
valueset "Standardized Tools for Assessment of Cognition": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1006'

parameter "Measurement Period" Interval<DateTime>
  default Interval[@2026-01-01T00:00:00.000Z, @2027-01-01T00:00:00.000Z)

context Patient

/***Population Criteria***/


define "Initial Population":
  exists "Dementia Encounter During Measurement Period"
    and ( Count("Qualifying Encounter During Measurement Period") >= 2 )

define "Denominator":
  "Initial Population"

define "Numerator":
  exists "Assessment of Cognition Using Standardized Tools or Alternate Methods"

define "Denominator Exceptions":
  exists "Patient Reason for Not Performing Assessment of Cognition Using Standardized Tools or Alternate Methods"

/***Definitions***/


define "Assessment of Cognition Using Standardized Tools or Alternate Methods":
  ( ["ObservationScreeningAssessment": "Standardized Tools for Assessment of Cognition"]
    union ["ObservationScreeningAssessment": "Cognitive Assessment"] ) CognitiveAssessment
    with "Dementia Encounter During Measurement Period" EncounterDementia
      such that CognitiveAssessment.effective.toInterval ( ) starts 12 months or less on or before day of end of EncounterDementia.period
    where CognitiveAssessment.value is not null
      and CognitiveAssessment.status in { 'final', 'amended', 'corrected' }

define "Dementia Encounter During Measurement Period":
  "Encounter to Assess Cognition" EncounterAssessCognition
    with ( [Condition: "Dementia & Mental Degenerations"] ) Dementia
      such that EncounterAssessCognition.period during day of "Measurement Period"
        and Dementia.prevalenceInterval ( ) overlaps day of EncounterAssessCognition.period
        and ( Dementia.abatement is null
            or end of Dementia.abatement.toInterval ( ) after day of end of "Measurement Period"
        )
        and Dementia.isVerified ( )

define "Encounter to Assess Cognition":
  ( ["Encounter": "Psych Visit Diagnostic Evaluation"]
    union ["Encounter": "Nursing Facility Visit"]
    union ["Encounter": "Care Services in Long Term Residential Facility"]
    union ["Encounter": "Home Healthcare Services"]
    union ["Encounter": "Psych Visit Psychotherapy"]
    union ["Encounter": "Behavioral or Neuropsych Assessment"]
    union ["Encounter": "Occupational Therapy Evaluation"]
    union ["Encounter": "Office Visit"]
    union ["Encounter": "Outpatient Consultation"] ) EncounterAssessCognition
    where EncounterAssessCognition.period during day of "Measurement Period"
      and EncounterAssessCognition.status ~ 'finished'

define "Patient Reason for Not Performing Assessment of Cognition Using Standardized Tools or Alternate Methods":
  ( [ObservationCancelled: code in "Standardized Tools for Assessment of Cognition"]
    union [ObservationCancelled: code in "Cognitive Assessment"] ) NoCognitiveAssessment
    with "Dementia Encounter During Measurement Period" EncounterDementia
      such that NoCognitiveAssessment.issued during day of EncounterDementia.period
    // QI-Core had notDoneReason as a property, but now it is a fluentFunction in USQualityCoreCommon
    // Original:
    // where NoCognitiveAssessment.notDoneReason() in "Patient Reason"
    where NoCognitiveAssessment.notDoneReason() in "Patient Reason"

define fluent function isVerified(condition Choice<ConditionEncounterDiagnosis, ConditionProblemsHealthConcerns>):
  condition.verificationStatus is not null implies ( condition.verificationStatus ~ Status."confirmed"
      or condition.verificationStatus ~ Status."unconfirmed"
      or condition.verificationStatus ~ Status."provisional"
      or condition.verificationStatus ~ Status."differential"
  )

define "Qualifying Encounter During Measurement Period":
  ( "Encounter to Assess Cognition"
    union ["Encounter": "Patient Provider Interaction"] ) ValidEncounter
    where ValidEncounter.period during day of "Measurement Period"
      and ValidEncounter.status = 'finished'

define "SDE Ethnicity":
  SDE."SDE Ethnicity"

define "SDE Race":
  SDE."SDE Race"

define "SDE Sex":
  SDE."SDE Sex"

define "SDE Payer":
  SDE."SDE Payer"