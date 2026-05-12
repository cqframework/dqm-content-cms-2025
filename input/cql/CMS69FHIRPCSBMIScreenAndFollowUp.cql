/*
NOTE: For use by March 2026 US Realm Connectathon participants for internal use only. Not for use or distribution in commercial products.
*/
library CMS69FHIRPCSBMIScreenAndFollowUp version '1.1.000'

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
include Hospice version '7.1.000' called Hospice
include PalliativeCare version '2.1.000' called PalliativeCare


codesystem "ActCode": 'http://terminology.hl7.org/CodeSystem/v3-ActCode'
codesystem "ICD10CM": 'http://hl7.org/fhir/sid/icd-10-cm'
codesystem "LOINC": 'http://loinc.org'
codesystem "ObservationCategoryCodes": 'http://terminology.hl7.org/CodeSystem/observation-category'

valueset "Encounter to Evaluate BMI": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.600.1.1751'
valueset "Follow Up for Above Normal BMI": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.600.1.1525'
valueset "Follow Up for Below Normal BMI": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.600.1.1528'
valueset "Medical Reason": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1007'
valueset "Medications for Above Normal BMI": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1561'
valueset "Medications for Below Normal BMI": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1562'
valueset "Overweight or Obese": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113762.1.4.1047.502'
valueset "Patient Declined": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1582'
valueset "Pregnancy or Other Related Diagnoses": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.600.1.1623'
valueset "Referrals Where Weight Assessment May Occur": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.600.1.1527'
valueset "Underweight": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1563'

code "Body mass index (BMI) [Ratio]": '39156-5' from "LOINC" display 'Body mass index (BMI) [Ratio]'
code "virtual": 'VR' from "ActCode" display 'virtual'

parameter "Measurement Period" Interval<DateTime>
  default Interval[@2026-01-01T00:00:00.000Z, @2027-01-01T00:00:00.000Z)

context Patient

define "Initial Population":
  exists "Qualifying Encounter During Day Of Measurement Period" QualifyingEncounter
    where "AgeInYearsAt"(date from start of QualifyingEncounter.period) >= 18

define "Denominator":
  "Initial Population"

define "Denominator Exclusions":
  Hospice."Has Hospice Services"
    or PalliativeCare."Has Palliative Care in the Measurement Period"
    or "Is Pregnant During Measurement Period"

define "Numerator":
  exists "High BMI And Follow Up Provided"
    or exists "Low BMI And Follow Up Provided"
    or "Has Normal BMI"

define "Denominator Exceptions":
  exists "Medical Reason For Not Documenting A Follow Up Plan For Low Or High BMI"
    or exists "Medical Reason Or Patient Reason For Not Performing BMI Exam"

define "BMI During Measurement Period":
  ( ( [USCore.BMIProfile] ).isObservationBMI ( ) ) BMI
    where BMI.value > 0 'kg/m2'
      and BMI.effective.toInterval ( ) during day of "Measurement Period"

define "Documented Low BMI During Measurement Period":
  "BMI During Measurement Period" BMI
    where BMI.value < 18.5 'kg/m2'

define "Documented High BMI During Measurement Period":
  "BMI During Measurement Period" BMI
    where BMI.value >= 25 'kg/m2'

define "Has Normal BMI":
  exists ( "BMI During Measurement Period" BMI
      where BMI.value >= 18.5 'kg/m2'
        and BMI.value < 25 'kg/m2'
  )
    and not ( exists "Documented High BMI During Measurement Period"
        or exists "Documented Low BMI During Measurement Period"
    )

define "High BMI And Follow Up Provided":
  "Documented High BMI During Measurement Period" HighBMI
    with ( "High BMI Interventions Ordered"
      union "High BMI Interventions Performed" ) HighBMIInterventions
      such that Coalesce(HighBMIInterventions.performed.toInterval(), HighBMIInterventions.authoredOn.toInterval()) starts during day of "Measurement Period"

define "High BMI Interventions Ordered":
  ( ( [ServiceRequest: "Follow Up for Above Normal BMI"]
      union [ServiceRequest: "Referrals Where Weight Assessment May Occur"]
      union [MedicationRequest: "Medications for Above Normal BMI"] ) HighInterventionsOrdered
      where HighInterventionsOrdered.reasonCode in "Overweight or Obese"
        or ( exists ( [ConditionProblemsHealthConcerns: "Overweight or Obese"]
            union [ConditionEncounterDiagnosis: "Overweight or Obese"] ) OverweightObese
            where OverweightObese.onset.toInterval ( ) starts before or on day of HighInterventionsOrdered.authoredOn
        )
  )

define "High BMI Interventions Performed":
  ( [Procedure: "Follow Up for Above Normal BMI"] HighInterventionsPerformed
      where HighInterventionsPerformed.reasonCode in "Overweight or Obese"
        or ( exists [ConditionProblemsHealthConcerns: "Overweight or Obese"] OverweightObese
            where OverweightObese.prevalenceInterval ( ) starts before or on day of start of HighInterventionsPerformed.performed.toInterval ( )
              and not ( OverweightObese.prevalenceInterval ( ) ends before day of start of HighInterventionsPerformed.performed.toInterval ( ) )
        )
  )

define "Medical Reason Or Patient Reason For Not Performing BMI Exam":
  [ObservationCancelled: "Body mass index (BMI) [Ratio]"] NoBMI
    with "Qualifying Encounter During Day Of Measurement Period" QualifyingEncounter
      such that NoBMI.effective.toInterval ( ) ends same day as start of QualifyingEncounter.period
    where ( NoBMI.notDoneReason ( ) in "Patient Declined"
        or NoBMI.notDoneReason ( ) in "Medical Reason"
    )

define "Low BMI Interventions Ordered":
  ( ( [ServiceRequest: "Follow Up for Below Normal BMI"]
      union [ServiceRequest: "Referrals Where Weight Assessment May Occur"]
      union [MedicationRequest: "Medications for Below Normal BMI"] ) LowInterventionsOrdered
      where LowInterventionsOrdered.reasonCode in "Underweight"
        or ( exists ( [ConditionProblemsHealthConcerns: "Underweight"]
            union [ConditionEncounterDiagnosis: "Underweight"] ) UnderweightDiagnosis
            where UnderweightDiagnosis.onset.toInterval ( ) starts before or on day of LowInterventionsOrdered.authoredOn
              and LowInterventionsOrdered.authoredOn during day of "Measurement Period"
        )
  )

define "Low BMI Interventions Performed":
  ( [Procedure: "Follow Up for Below Normal BMI"] LowInterventionsPerformed
      where LowInterventionsPerformed.reasonCode in "Underweight"
        and LowInterventionsPerformed.status = 'completed'
        or ( exists [ConditionProblemsHealthConcerns: "Underweight"] UnderweightDiagnosis
            where ( UnderweightDiagnosis.isHealthConcern ( ) )
              and UnderweightDiagnosis.prevalenceInterval ( ) starts before or on day of start of LowInterventionsPerformed.performed.toInterval ( )
              and LowInterventionsPerformed.performed.toInterval ( ) during day of "Measurement Period"
              and not ( UnderweightDiagnosis.prevalenceInterval ( ) ends before day of start of LowInterventionsPerformed.performed.toInterval ( ) )
        )
  )

define "Low BMI And Follow Up Provided":
  ( "Documented Low BMI During Measurement Period" LowBMI
      with ( "Low BMI Interventions Ordered"
        union "Low BMI Interventions Performed" ) LowBMIInterventions
        such that Coalesce(LowBMIInterventions.performed.toInterval(), LowBMIInterventions.authoredOn.toInterval()) starts during day of "Measurement Period"
  )

define "Medical Reason For Not Documenting A Follow Up Plan For Low Or High BMI":
  ( ( [ServiceNotRequested: "Referrals Where Weight Assessment May Occur"]
      union [ServiceNotRequested: "Follow Up for Above Normal BMI"]
      union [ServiceNotRequested: "Follow Up for Below Normal BMI"] ) NoBMIFollowUp
      with "Qualifying Encounter During Day Of Measurement Period" QualifyingEncounter
        such that NoBMIFollowUp.authoredOn same day as start of QualifyingEncounter.period
      where NoBMIFollowUp.status ~ 'completed'
        and NoBMIFollowUp.reasonRefused ( ) in "Medical Reason"
  )
    union ( ( [MedicationNotRequested: "Medications for Above Normal BMI"]
        union [MedicationNotRequested: "Medications for Below Normal BMI"] ) NoBMIFollowUp
        with "Qualifying Encounter During Day Of Measurement Period" QualifyingEncounter
          such that NoBMIFollowUp.authoredOn same day as start of QualifyingEncounter.period
        where NoBMIFollowUp.status ~ 'completed'
          and NoBMIFollowUp.reasonCode in "Medical Reason"
    )

define "Is Pregnant During Measurement Period":
  exists ( ( [ConditionProblemsHealthConcerns: "Pregnancy or Other Related Diagnoses"]
      union [ConditionEncounterDiagnosis: "Pregnancy or Other Related Diagnoses"] ) PregnancyDiagnosis
      where PregnancyDiagnosis.onset.toInterval ( ) overlaps day of "Measurement Period"
  )
    or exists ( [USCore.ObservationPregnancyStatusProfile] PregnantObservation
        where PregnantObservation.effective.toInterval ( ) overlaps day of "Measurement Period"
          and PregnantObservation.status in { 'final', 'amended', 'corrected' }
          and ( PregnantObservation.value in "Pregnancy or Other Related Diagnoses" )
    )

define "Qualifying Encounter During Day Of Measurement Period":
  [Encounter: "Encounter to Evaluate BMI"] BMIEncounter
    where BMIEncounter.period during day of "Measurement Period"
      and BMIEncounter.class !~ "virtual"
      and BMIEncounter.status = 'finished'

define "SDE Ethnicity":
  SDE."SDE Ethnicity"

define "SDE Payer":
  SDE."SDE Payer"

define "SDE Race":
  SDE."SDE Race"

define "SDE Sex":
  SDE."SDE Sex"