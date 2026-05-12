/*
NOTE: For use by March 2026 US Realm Connectathon participants for internal use only. Not for use or distribution in commercial products.
*/
library CMS157FHIRPainIntensityQuantified version '1.1.000'

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

codesystem "CPT": 'http://www.ama-assn.org/go/cpt'

valueset "Audio Visual Telehealth Encounter": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.1444.5.215'
valueset "Cancer": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1010'
valueset "Chemotherapy Administration": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1027'
valueset "Office Visit": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.101.12.1001'
valueset "Radiation Treatment Management": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1026'
valueset "Standardized Pain Assessment Tool": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1028'

code "Radiation treatment management, 5 treatments": '77427' from "CPT" display 'Radiation treatment management, 5 treatments'

parameter "Measurement Period" Interval<DateTime>
  default Interval[@2026-01-01T00:00:00.000Z, @2027-01-01T00:00:00.000Z)

context Patient

define "Denominator 1":
  "Initial Population 1"

define "Denominator 2":
  "Initial Population 2"

define "Initial Population 1":
  "Face to Face or Telehealth Encounter with Ongoing Chemotherapy"

define "Initial Population 2":
  "Radiation Treatment Management During Measurement Period with Cancer Diagnosis"

define "Chemotherapy Within 31 Days Prior and During Measurement Period":
  [Procedure: "Chemotherapy Administration"] ChemoAdministration
    where ChemoAdministration.performed.toInterval ( ) during Interval[start of "Measurement Period" - 31 days, end of "Measurement Period"]
      and ChemoAdministration.status in { 'completed', 'in-progress' }

define "Face to Face or Telehealth Encounter with Ongoing Chemotherapy":
  from
    ( [Encounter: "Office Visit"]
      union [Encounter: "Audio Visual Telehealth Encounter"] ) FaceToFaceOrTelehealthEncounter,
    "Chemotherapy Within 31 Days Prior and During Measurement Period" ChemoBeforeEncounter,
    "Chemotherapy Within 31 Days Prior and During Measurement Period" ChemoAfterEncounter,
    ( [ConditionProblemsHealthConcerns: "Cancer"]
      union [ConditionEncounterDiagnosis: "Cancer"] ) CancerDx
    where CancerDx.onset.toInterval ( ) overlaps day of FaceToFaceOrTelehealthEncounter.period
      and ChemoBeforeEncounter.performed.toInterval ( ) starts 30 days or less on or before day of end of FaceToFaceOrTelehealthEncounter.period
      and ChemoAfterEncounter.performed.toInterval ( ) starts 30 days or less on or after day of end of FaceToFaceOrTelehealthEncounter.period
      and not ( ChemoAfterEncounter.performed.toInterval ( ) same day as ChemoBeforeEncounter.performed.toInterval ( ) )
      and FaceToFaceOrTelehealthEncounter.period during day of "Measurement Period"
      and FaceToFaceOrTelehealthEncounter.status = 'finished'
    return FaceToFaceOrTelehealthEncounter

define "Numerator 1":
  "Face to Face or Telehealth Encounter with Ongoing Chemotherapy" FaceToFaceOrTelehealthEncounterWithChemo
    with "Standard Pain Assessment with Result" PainAssessed
      such that PainAssessed.effective.toInterval ( ) during day of FaceToFaceOrTelehealthEncounterWithChemo.period

define "Radiation Treatment Management During Measurement Period with Cancer Diagnosis":
  ( [Encounter: "Radiation Treatment Management"] ) RadiationTreatmentManagement
    with ( [ConditionProblemsHealthConcerns: "Cancer"]
      union [ConditionEncounterDiagnosis: "Cancer"] ) CancerDx
      such that CancerDx.onset.toInterval ( ) overlaps day of RadiationTreatmentManagement.period
    where RadiationTreatmentManagement.period during day of "Measurement Period"
      and RadiationTreatmentManagement.status = 'finished'

define "Numerator 2":
  "Radiation Treatment Management During Measurement Period with Cancer Diagnosis" RadiationManagementEncounter
    with "Standard Pain Assessment with Result" PainAssessed
      such that case
        when exists ( ( RadiationManagementEncounter.type ) RadiationManagement
            where RadiationManagement ~ "Radiation treatment management, 5 treatments"
        ) then PainAssessed.effective.toInterval ( ) 6 days or less on or before day of start of RadiationManagementEncounter.period 
        else PainAssessed.effective.toInterval ( ) during day of RadiationManagementEncounter.period end

define "SDE Ethnicity":
  SDE."SDE Ethnicity"

define "SDE Payer":
  SDE."SDE Payer"

define "SDE Race":
  SDE."SDE Race"

define "SDE Sex":
  SDE."SDE Sex"

define "Standard Pain Assessment with Result":
  [ObservationScreeningAssessment: "Standardized Pain Assessment Tool"] AssessedPain
    where AssessedPain.value is not null