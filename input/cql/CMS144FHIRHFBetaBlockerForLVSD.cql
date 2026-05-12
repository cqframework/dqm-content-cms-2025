/*
NOTE: For use by March 2026 US Realm Connectathon participants for internal use only. Not for use or distribution in commercial products.
*/
library CMS144FHIRHFBetaBlockerForLVSD version '1.1.000'

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
include AHAOverall version '5.1.000' called AHA

codesystem "SNOMEDCT": 'http://snomed.info/sct'

valueset "Allergy to Beta Blocker Therapy": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1177'
valueset "Arrhythmia": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.366'
valueset "Asthma": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.362'
valueset "Atrioventricular Block": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.367'
valueset "Beta Blocker Therapy for LVSD": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1184'
valueset "Beta Blocker Therapy Ingredient": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1493'
valueset "Bradycardia": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.412'
valueset "Cardiac Pacer": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113762.1.4.1178.53'
valueset "Cardiac Pacer in Situ": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.368'
valueset "Hypotension": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.370'
valueset "Intolerance to Beta Blocker Therapy": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1178'
valueset "Medical Reason": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1007'
valueset "Patient Reason": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1008'

code "Substance with beta adrenergic receptor antagonist mechanism of action (substance)": '373254001' from "SNOMEDCT" display 'Substance with beta adrenergic receptor antagonist mechanism of action (substance)'

parameter "Measurement Period" Interval<DateTime>
  default Interval[@2026-01-01T00:00:00.000Z, @2027-01-01T00:00:00.000Z)

context Patient

define "Initial Population":
  AHA."Is Adult With Two Qualifying Outpatient Encounters and One Heart Failure Outpatient Encounter During the Measurement Period"

define "Denominator":
  "Initial Population"
    and exists AHA."Heart Failure Outpatient Encounter with History of Moderate or Severe LVSD"

define "Denominator Exclusions":
  AHA."Has Heart Transplant"
    or AHA."Has Heart Transplant Complications"
    or AHA."Has Left Ventricular Assist Device"
    or AHA."Has Left Ventricular Assist Device Complications"

define "Numerator":
  "Has Beta Blocker Therapy for LVSD Ordered"
    or "Is Currently Taking Beta Blocker Therapy for LVSD"

define "Denominator Exceptions":
  "Has Consecutive Heart Rates Less than 50"
    or "Has Medical or Patient Reason for Not Ordering Beta Blocker for LVSD"
    or "Has Arrhythmia Diagnosis"
    or "Has Hypotension Diagnosis"
    or "Has Asthma Diagnosis"
    or "Has Diagnosis of Allergy or Intolerance to Beta Blocker Therapy"
    or "Has Bradycardia Diagnosis"
    or "Has Allergy or Intolerance to Beta Blocker Therapy Ingredient"
    or "Atrioventricular Block without Cardiac Pacer"

define "SDE Ethnicity":
  SDE."SDE Ethnicity"

define "SDE Payer":
  SDE."SDE Payer"

define "SDE Race":
  SDE."SDE Race"

define "SDE Sex":
  SDE."SDE Sex"

define "Atrioventricular Block without Cardiac Pacer":
  "Has Atrioventricular Block Diagnosis"
    and not "Has Diagnosis of Cardiac Pacer in Situ"
    and not "Has Cardiac Pacer Device Implanted"

define "Has Cardiac Pacer Device Implanted":
  exists ( [Procedure: "Cardiac Pacer"] ImplantedCardiacPacer
      with AHA."Heart Failure Outpatient Encounter with History of Moderate or Severe LVSD" ModerateOrSevereLVSDHFOutpatientEncounter
        such that ImplantedCardiacPacer.performed.toInterval ( ) starts before end of ModerateOrSevereLVSDHFOutpatientEncounter.period
      where ImplantedCardiacPacer.status = 'completed'
  )

define "Is Currently Taking Beta Blocker Therapy for LVSD":
  exists ( ["MedicationRequest": "Beta Blocker Therapy for LVSD"] ActiveBetaBlocker
      where ActiveBetaBlocker.overlapsAfterHeartFailureOutpatientEncounter ( )
  )

define "Has Hypotension Diagnosis":
  exists ( ( ["ConditionProblemsHealthConcerns": "Hypotension"]
      union ["ConditionEncounterDiagnosis": "Hypotension"] ) HypotensionAlias
      where HypotensionAlias.overlapsHeartFailureOutpatientEncounter ( )
        and HypotensionAlias.isVerified ( )
  )

define "Has Diagnosis of Cardiac Pacer in Situ":
  exists ( ( ["ConditionProblemsHealthConcerns": "Cardiac Pacer in Situ"]
      union ["ConditionEncounterDiagnosis": "Cardiac Pacer in Situ"] ) CardiacPacerDiagnosis
      where CardiacPacerDiagnosis.overlapsAfterHeartFailureOutpatientEncounter ( )
        and CardiacPacerDiagnosis.isVerified ( )
  )

define "Has Diagnosis of Allergy or Intolerance to Beta Blocker Therapy":
  exists ( ( ( ["ConditionProblemsHealthConcerns": "Allergy to Beta Blocker Therapy"]
        union ["ConditionEncounterDiagnosis": "Allergy to Beta Blocker Therapy"]
    )
      union ( ["ConditionProblemsHealthConcerns": "Intolerance to Beta Blocker Therapy"] )
      union ["ConditionEncounterDiagnosis": "Intolerance to Beta Blocker Therapy"] ) BetaBlockerAllergyOrIntoleranceDiagnosis
      where BetaBlockerAllergyOrIntoleranceDiagnosis.overlapsAfterHeartFailureOutpatientEncounter ( )
        and BetaBlockerAllergyOrIntoleranceDiagnosis.isVerified ( )
  )

define "Has Bradycardia Diagnosis":
  exists ( ( [ConditionProblemsHealthConcerns: "Bradycardia"]
      union [ConditionEncounterDiagnosis: "Bradycardia"] ) BradycardiaAlias
      where BradycardiaAlias.overlapsHeartFailureOutpatientEncounter ( )
        and BradycardiaAlias.isVerified ( )
  )

define "Has Consecutive Heart Rates Less than 50":
  exists ( from
      ["USCore.HeartRateProfile"] HeartRate,
      AHA."Heart Failure Outpatient Encounter with History of Moderate or Severe LVSD" ModerateOrSevereLVSDHFOutpatientEncounter
      let PriorHeartRate: Last(["USCore.HeartRateProfile"] MostRecentPriorHeartRate
          where MostRecentPriorHeartRate.effective.toInterval() during ModerateOrSevereLVSDHFOutpatientEncounter.period
            and MostRecentPriorHeartRate.effective.toInterval() before HeartRate.effective.toInterval()
          sort by start of effective.toInterval()
      )
      where HeartRate.effective.toInterval ( ) during ModerateOrSevereLVSDHFOutpatientEncounter.period
        and HeartRate.status in { 'final', 'amended', 'corrected' }
        and HeartRate.value < 50 '/min'
        and PriorHeartRate.value < 50 '/min'
      return HeartRate
  )

define "Has Allergy or Intolerance to Beta Blocker Therapy Ingredient":
  exists ( ( [AllergyIntolerance: "Beta Blocker Therapy Ingredient"]
      union [AllergyIntolerance: "Substance with beta adrenergic receptor antagonist mechanism of action (substance)"] ) BetaBlockerAllergyIntolerance
      where BetaBlockerAllergyIntolerance.overlapsAfterHeartFailureOutpatientEncounter ( )
        and BetaBlockerAllergyIntolerance.isVerified ( )
  )

define "Has Arrhythmia Diagnosis":
  exists ( ( [ConditionProblemsHealthConcerns: "Arrhythmia"]
      union [ConditionEncounterDiagnosis: "Arrhythmia"] ) ArrhythmiaAlias
      where ArrhythmiaAlias.overlapsHeartFailureOutpatientEncounter ( )
        and ArrhythmiaAlias.isVerified ( )
  )

define "Has Asthma Diagnosis":
  exists ( ( [ConditionProblemsHealthConcerns: "Asthma"]
      union [ConditionEncounterDiagnosis: "Asthma"] ) AsthmaAlias
      where AsthmaAlias.overlapsHeartFailureOutpatientEncounter ( )
        and AsthmaAlias.isVerified ( )
  )

define "Has Atrioventricular Block Diagnosis":
  exists ( ( [ConditionProblemsHealthConcerns: "Atrioventricular Block"]
      union [ConditionEncounterDiagnosis: "Atrioventricular Block"] ) AtrioventricularBlockAlias
      where AtrioventricularBlockAlias.overlapsHeartFailureOutpatientEncounter ( )
        and AtrioventricularBlockAlias.isVerified ( )
  )

define "Has Beta Blocker Therapy for LVSD Ordered":
  exists ( [MedicationRequest: medication in "Beta Blocker Therapy for LVSD"] BetaBlockerOrdered
      where BetaBlockerOrdered.isOrderedDuringHeartFailureOutpatientEncounter ( )
  )

define "Has Medical or Patient Reason for Not Ordering Beta Blocker for LVSD":
  exists ( ["MedicationNotRequested": medication in "Beta Blocker Therapy for LVSD"] NoBetaBlockerOrdered
      with AHA."Heart Failure Outpatient Encounter with History of Moderate or Severe LVSD" ModerateOrSevereLVSDHFOutpatientEncounter
        such that NoBetaBlockerOrdered.authoredOn during day of ModerateOrSevereLVSDHFOutpatientEncounter.period
      where ( NoBetaBlockerOrdered.reasonCode in "Medical Reason"
          or NoBetaBlockerOrdered.reasonCode in "Patient Reason"
      )
  )
  
 /*
@description: Returns true if the given condition either has no verification status or has a verification status of confirmed, unconfirmed, provisional, or differential
*/


define fluent function isVerified(allergyIntolerance AllergyIntolerance):
  allergyIntolerance.verificationStatus is not null implies ( allergyIntolerance.verificationStatus ~ USQualityCoreCommon."allergy-confirmed"
      or allergyIntolerance.verificationStatus ~ USQualityCoreCommon."allergy-unconfirmed"
  )

define fluent function isVerified(condition Choice<ConditionEncounterDiagnosis, ConditionProblemsHealthConcerns>):
  condition.verificationStatus is not null implies ( condition.verificationStatus ~ Status."confirmed"
      or condition.verificationStatus ~ Status."unconfirmed"
      or condition.verificationStatus ~ Status."provisional"
      or condition.verificationStatus ~ Status."differential"
  )