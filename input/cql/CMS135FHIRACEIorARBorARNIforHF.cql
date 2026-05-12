/*
NOTE: For use by March 2026 US Realm Connectathon participants for internal use only. Not for use or distribution in commercial products.
*/
library CMS135FHIRACEIorARBorARNIforHF version '1.1.000'

using USQualityCore version '0.1.0-cibuild'
using USCore version '6.1.0-derived'
using FHIR version '4.0.1'

include hl7.fhir.uv.cql.FHIRHelpers version '4.0.1' called FHIRHelpers
include hl7.fhir.uv.cql.FHIRCommon version '2.0.0' called FHIRCommon
include hl7.fhir.us.cql.USCoreCommon version '2.0.0-ballot' called USCoreCommon
include hl7.fhir.us.cql.USCoreElements version '2.0.0-ballot' called USCoreElements

include USQualityCoreCommon version '0.1.0-cibuild' called USQualityCoreCommon
include SupplementalDataElements version '6.1.000' called SDE
include AHAOverall version '5.1.000' called AHA

codesystem "SNOMEDCT": 'http://snomed.info/sct'

valueset "ACE Inhibitor or ARB or ARNI Ingredient": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1489'
valueset "ACE Inhibitor or ARB or ARNI": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1139'
valueset "Allergy to ACE Inhibitor or ARB": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1211'
valueset "Intolerance to ACE Inhibitor or ARB": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1212'
valueset "Medical Reason": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1007'
valueset "Patient Reason": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1008'
valueset "Patient Reason for ACE Inhibitor or ARB Decline": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1140'
valueset "Pregnancy": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.378'

code "Acute renal failure caused by angiotensin-converting-enzyme inhibitor (disorder)": '422593004' from "SNOMEDCT" display 'Acute renal failure caused by angiotensin-converting-enzyme inhibitor (disorder)'
code "Substance with angiotensin II receptor antagonist mechanism of action (substance)": '372913009' from "SNOMEDCT" display 'Substance with angiotensin II receptor antagonist mechanism of action (substance)'
code "Substance with angiotensin-converting enzyme inhibitor mechanism of action (substance)": '372733002' from "SNOMEDCT" display 'Substance with angiotensin-converting enzyme inhibitor mechanism of action (substance)'
code "Substance with neprilysin inhibitor mechanism of action (substance)": '786886009' from "SNOMEDCT" display 'Substance with neprilysin inhibitor mechanism of action (substance)'

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
  "Has ACEI or ARB or ARNI Ordered"
    or "Is Currently Taking ACEI or ARB or ARNI"

define "Denominator Exceptions":
  "Has Medical or Patient Reason for Not Ordering ACEI or ARB or ARNI"
    or "Has Allergy or Intolerance to ACEI or ARB or ARNI Ingredient"
    or "Has Diagnosis of Allergy or Intolerance to ACEI or ARB"
    or "Has Diagnosis of Pregnancy"
    or "Has Diagnosis of Renal Failure Due to ACEI"

define "SDE Ethnicity":
  SDE."SDE Ethnicity"

define "SDE Payer":
  SDE."SDE Payer"

define "SDE Race":
  SDE."SDE Race"

define "SDE Sex":
  SDE."SDE Sex"

define "Has ACEI or ARB or ARNI Ordered":
  exists ( [MedicationRequest: medication in "ACE Inhibitor or ARB or ARNI"] ACEIOrARBOrARNIOrdered
      where ACEIOrARBOrARNIOrdered.isOrderedDuringHeartFailureOutpatientEncounter ( )
  )

define "Has Allergy or Intolerance to ACEI or ARB or ARNI Ingredient":
  exists ( ( [AllergyIntolerance: "ACE Inhibitor or ARB or ARNI Ingredient"]
      union [AllergyIntolerance: "Substance with angiotensin-converting enzyme inhibitor mechanism of action (substance)"]
      union [AllergyIntolerance: "Substance with angiotensin II receptor antagonist mechanism of action (substance)"]
      union [AllergyIntolerance: "Substance with neprilysin inhibitor mechanism of action (substance)"] ) ACEIOrARBOrARNIAllergyIntolerance
      where ACEIOrARBOrARNIAllergyIntolerance.overlapsAfterHeartFailureOutpatientEncounter ( )
  )

define "Has Diagnosis of Allergy or Intolerance to ACEI or ARB":
  exists ( (
    ["ConditionEncounterDiagnosis": "Allergy to ACE Inhibitor or ARB"]
      union ["ConditionEncounterDiagnosis": "Intolerance to ACE Inhibitor or ARB"]
   ) ACEIOrARBAllergyOrIntoleranceDiagnosis
      where ACEIOrARBAllergyOrIntoleranceDiagnosis.overlapsAfterHeartFailureOutpatientEncounter ( )
  )

define "Has Diagnosis of Pregnancy":
  exists ( ( [Condition: "Pregnancy"] ) PregnancyDiagnosis
      with AHA."Heart Failure Outpatient Encounter with History of Moderate or Severe LVSD" ModerateOrSevereLVSDHFOutpatientEncounter
        such that PregnancyDiagnosis.prevalenceInterval ( ) starts 9 months or less before or on start of ModerateOrSevereLVSDHFOutpatientEncounter.period
          and PregnancyDiagnosis.isVerified ( )
  )
    or exists ( [USCore.ObservationPregnancyStatusProfile] PregnantObservation
        with AHA."Heart Failure Outpatient Encounter with History of Moderate or Severe LVSD" ModerateOrSevereLVSDHFOutpatientEncounter
          such that PregnantObservation.effective.toInterval ( ) starts 9 months or less before or on start of ModerateOrSevereLVSDHFOutpatientEncounter.period
            and ( PregnantObservation.value in "Pregnancy"
                and PregnantObservation.status in { 'final', 'amended', 'corrected' }
            )
    )

define "Has Diagnosis of Renal Failure Due to ACEI":
  exists ( ( [ConditionEncounterDiagnosis: "Acute renal failure caused by angiotensin-converting-enzyme inhibitor (disorder)"] ) RenalFailureDueToACEI
      where RenalFailureDueToACEI.overlapsHeartFailureOutpatientEncounter ( )
  )

define "Has Medical or Patient Reason for Not Ordering ACEI or ARB or ARNI":
  exists ( [MedicationNotRequested: medication in "ACE Inhibitor or ARB or ARNI"] NoACEIOrARBOrARNIOrdered
      where NoACEIOrARBOrARNIOrdered.isMedicationNotRequestedOrderedDuringHeartFailureOutpatientEncounter ( )
        and ( NoACEIOrARBOrARNIOrdered.reasonCode in "Medical Reason"
            or NoACEIOrARBOrARNIOrdered.reasonCode in "Patient Reason"
            or NoACEIOrARBOrARNIOrdered.reasonCode in "Patient Reason for ACE Inhibitor or ARB Decline"
        )
  )

define "Is Currently Taking ACEI or ARB or ARNI":
  exists ( [MedicationRequest: medication in "ACE Inhibitor or ARB or ARNI"] ActiveACEIOrARBOrARNI
      where ActiveACEIOrARBOrARNI.overlapsAfterHeartFailureOutpatientEncounter ( )
  )