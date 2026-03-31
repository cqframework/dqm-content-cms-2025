/*
NOTE: For use by March 2026 US Realm Connectathon participants for internal use only. Not for use or distribution in commercial products.
*/
library CMS125FHIRBreastCancerScreen version '1.1.000'

using USQualityCore version '0.1.0-cibuild'
using USCore version '6.1.0-derived'
using FHIR version '4.0.1'

include hl7.fhir.uv.cql.FHIRHelpers version '4.0.1' called FHIRHelpers
include hl7.fhir.uv.cql.FHIRCommon version '2.0.0' called FHIRCommon
include hl7.fhir.us.cql.USCoreCommon version '2.0.0-ballot' called USCoreCommon
include hl7.fhir.us.cql.USCoreElements version '2.0.0-ballot' called USCoreElements
//include fhir.guides.astp."us-quality-core".USQualityCoreCommon version '1.0.0' called USQualityCore
//include hl7.fhir.us."us-quality-core".USQualityCoreCommon version '2.0.0' called USQualityCore

include USQualityCoreCommon version '0.1.0-cibuild' called USQualityCoreCommon
include SupplementalDataElements version '6.1.000' called SDE
include Status version '2.1.000' called Status
include AdultOutpatientEncounters version '5.1.000' called AdultOutpatientEncounters
include AdvancedIllnessandFrailty version '2.1.000' called AIFrailLTCF
include Hospice version '7.1.000' called Hospice
include PalliativeCare version '2.1.000' called PalliativeCare

codesystem "SNOMEDCT": 'http://snomed.info/sct'

valueset "Bilateral Mastectomy": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.198.12.1005'
valueset "History of bilateral mastectomy": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.198.12.1068'
valueset "Mammography": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.108.12.1018'
valueset "Status Post Left Mastectomy": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.198.12.1069'
valueset "Status Post Right Mastectomy": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.198.12.1070'
valueset "Unilateral Mastectomy Left": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.198.12.1133'
valueset "Unilateral Mastectomy Right": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.198.12.1134'
valueset "Unilateral Mastectomy, Unspecified Laterality": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.198.12.1071'

code "Left (qualifier value)": '7771000' from "SNOMEDCT" display 'Left (qualifier value)'
code "Right (qualifier value)": '24028007' from "SNOMEDCT" display 'Right (qualifier value)'

parameter "Measurement Period" Interval<DateTime>
  default Interval[@2026-01-01T00:00:00.000Z, @2027-01-01T00:00:00.000Z)

context Patient

define "Initial Population":
  Patient.ageInYearsAt(date from end of "Measurement Period") in Interval[42, 74]
    and Patient.sex() = '248152002'
    and exists AdultOutpatientEncounters."Qualifying Encounters"

define "Denominator":
  "Initial Population"

define "Denominator Exclusions":
  Hospice."Has Hospice Services"
    or ( ( exists ( "Right Mastectomy Diagnosis" )
          or exists ( "Right Mastectomy Procedure" )
      )
        and ( exists ( "Left Mastectomy Diagnosis" )
            or exists ( "Left Mastectomy Procedure" )
        )
    )
    or exists "Bilateral Mastectomy Diagnosis"
    or exists "Bilateral Mastectomy Procedure"
    or AIFrailLTCF."Is Age 66 or Older with Advanced Illness and Frailty"
    or AIFrailLTCF."Is Age 66 or Older Living Long Term in a Nursing Home"
    or PalliativeCare."Has Palliative Care in the Measurement Period"

define "Right Mastectomy Diagnosis":
  ( ( ( [FHIR.Condition: "Status Post Right Mastectomy"] ) RightMastectomyCondition
      union ( ( [FHIR.Condition: "Unilateral Mastectomy, Unspecified Laterality"] ) UnilateralMastectomyDiagnosis
          where exists UnilateralMastectomyDiagnosis.bodySite S
            where S ~ "Right (qualifier value)"
      )
  ).verified ( ) ) RightMastectomy
    where RightMastectomy.prevalenceInterval ( ) starts on or before end of "Measurement Period"

define "Right Mastectomy Procedure":
  ( ( [USQualityCore.Procedure: "Unilateral Mastectomy Right"] ).isProcedurePerformed ( ) ) UnilateralMastectomyRightPerformed
    where UnilateralMastectomyRightPerformed.performed.toInterval ( ) ends on or before end of "Measurement Period"

define "Left Mastectomy Diagnosis":
  ( ( ( [FHIR.Condition: "Status Post Left Mastectomy"] )
      union ( ( [Condition: "Unilateral Mastectomy, Unspecified Laterality"] ) UnilateralMastectomyDiagnosis
          where exists UnilateralMastectomyDiagnosis.bodySite S
            where S ~ "Left (qualifier value)"
      )
  ).verified ( ) ) LeftMastectomy
    where LeftMastectomy.prevalenceInterval ( ) starts on or before end of "Measurement Period"

define "Left Mastectomy Procedure":
  ( ( [USQualityCore.Procedure: "Unilateral Mastectomy Left"] ).isProcedurePerformed ( ) ) UnilateralMastectomyLeftPerformed
    where UnilateralMastectomyLeftPerformed.performed.toInterval ( ) ends on or before end of "Measurement Period"

define "Bilateral Mastectomy Diagnosis":
  ( ( [FHIR.Condition: "History of bilateral mastectomy"] ).verified ( ) ) BilateralMastectomyHistory
    where BilateralMastectomyHistory.prevalenceInterval ( ) starts on or before end of "Measurement Period"

define "Bilateral Mastectomy Procedure":
  ( ( [USQualityCore.Procedure: "Bilateral Mastectomy"] ).isProcedurePerformed ( ) ) BilateralMastectomyPerformed
    where BilateralMastectomyPerformed.performed.toInterval ( ) ends on or before end of "Measurement Period"

define "Numerator":
  exists ( 
    ( ( [USQualityCore.ObservationClinicalResult: "Mammography"] ).isDiagnosticStudyPerformed ( ) ) Mammogram
      where Mammogram.effective.toInterval ( ) ends during day of Interval["October 1 Two Years Prior to the Measurement Period", end of "Measurement Period"]
  ) or exists (
    ( ( [USQualityCore.DiagnosticReportNote: "Mammography"] ).complete ( ) ) Mammogram
      where Mammogram.effective.toInterval ( ) ends during day of Interval["October 1 Two Years Prior to the Measurement Period", end of "Measurement Period"]
  )

define "October 1 Two Years Prior to the Measurement Period":
  DateTime((year from start of "Measurement Period" - 2), 10, 1, 0, 0, 0, 0, 0)

define "SDE Ethnicity":
  SDE."SDE Ethnicity"

define "SDE Payer":
  SDE."SDE Payer"

define "SDE Race":
  SDE."SDE Race"

define "SDE Sex":
  SDE."SDE Sex"

define "Stratification 1":
  AgeInYearsAt(date from 
    end of "Measurement Period"
  ) in Interval[42, 51]

define "Stratification 2":
  AgeInYearsAt(date from 
    end of "Measurement Period"
  ) in Interval[52, 74]