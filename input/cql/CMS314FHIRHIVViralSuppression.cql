/*
NOTE: For use by March 2026 US Realm Connectathon participants for internal use only. Not for use or distribution in commercial products.
*/
library CMS314FHIRHIVViralSuppression version '1.1.000'

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

valueset "Annual Wellness Visit": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1240'
valueset "Face-to-Face Interaction": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113762.1.4.1248.375'
valueset "HIV": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.120.12.1003'
valueset "HIV Viral Load Tests": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113762.1.4.1248.377'
valueset "Home Healthcare Services": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.101.12.1016'
valueset "Office Visit": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.101.12.1001'
valueset "Outpatient Consultation": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.101.12.1008'
valueset "Preventive Care Services Established Office Visit, 18 and Up": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.101.12.1025'
valueset "Preventive Care Services Initial Office Visit, 18 and Up": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.101.12.1023'
valueset "Preventive Care Services Other": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.101.11.1150'
valueset "Preventive Care Services, Initial Office Visit, 0 to 17": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.101.12.1022'
valueset "Preventive Care, Established Office Visit, 0 to 17": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.101.12.1024'
valueset "Telephone Visits": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.101.12.1080'

code "Below threshold level (qualifier value)": '260988000' from "SNOMEDCT" display 'Below threshold level (qualifier value)'
code "Not detected (qualifier value)": '260415000' from "SNOMEDCT" display 'Not detected (qualifier value)'

parameter "Measurement Period" Interval<DateTime>
  default Interval[@2026-01-01T00:00:00.000Z, @2027-01-01T00:00:00.000Z)

context Patient

define "Denominator":
  "Initial Population"

define "Has Active HIV Diagnosis Before or in First 90 Days of Measurement Period":
  exists ( ["ConditionProblemsHealthConcerns": "HIV"]
    union ["ConditionEncounterDiagnosis": "HIV"] ) HIVDx
    where HIVDx.onset.toInterval ( ) starts before day of ( start of "Measurement Period" + 90 days )
      and HIVDx.isVerified ( )

define "Initial Population":
  "Has Active HIV Diagnosis Before or in First 90 Days of Measurement Period"
    and "Has Qualifying Encounter During First 240 Days of Measurement Period"

define "Most Recent Viral Load Test During Measurement Period":
  Last(["LaboratoryResultObservation": "HIV Viral Load Tests"] ViralLoad
      where ViralLoad.status in { 'final', 'amended', 'corrected' }
        and ViralLoad.effective.latest() during day of "Measurement Period"
      sort by effective.earliest()
  )

define "Has Qualifying Encounter During First 240 Days of Measurement Period":
/*Note: applied workaround using value set 'Preventive Care Services Other', as a DRC cannot be used directly from an encounter retrieve; additional info can be found in CQLIT-368*/
  
  exists ( ["Encounter": "Office Visit"]
    union ["Encounter": "Outpatient Consultation"]
    union ["Encounter": "Annual Wellness Visit"]
    union ["Encounter": "Face-to-Face Interaction"]
    union ["Encounter": "Home Healthcare Services"]
    union ["Encounter": "Preventive Care Services Established Office Visit, 18 and Up"]
    union ["Encounter": "Preventive Care Services Initial Office Visit, 18 and Up"]
    union ["Encounter": "Preventive Care Services, Initial Office Visit, 0 to 17"]
    union ["Encounter": "Preventive Care, Established Office Visit, 0 to 17"]
    union ["Encounter": "Telephone Visits"]
    union ["Encounter": "Preventive Care Services Other"] ) QualifyingEncounter
    where QualifyingEncounter.period during day of Interval[start of "Measurement Period", start of "Measurement Period" + 240 days]
      and QualifyingEncounter.status = 'finished'

define "Numerator":
  "Most Recent Viral Load Test During Measurement Period".value < 200 '{copies}/mL'
    or "Most Recent Viral Load Test During Measurement Period".value ~ "Below threshold level (qualifier value)"
    or "Most Recent Viral Load Test During Measurement Period".value ~ "Not detected (qualifier value)"

define fluent function isVerified(condition Choice<ConditionProblemsHealthConcerns, ConditionEncounterDiagnosis>):
  condition.verificationStatus is not null implies ( condition.verificationStatus ~ Status."confirmed"
      or condition.verificationStatus ~ Status."unconfirmed"
      or condition.verificationStatus ~ Status."provisional"
      or condition.verificationStatus ~ Status."differential"
  )

define "SDE Ethnicity":
  SDE."SDE Ethnicity"

define "SDE Payer":
  SDE."SDE Payer"

define "SDE Race":
  SDE."SDE Race"

define "SDE Sex":
  SDE."SDE Sex"