/*
@description: I-28 defect-neutralizing helper library for USQualityCore Condition profile choices.
@comment: I-28 (see defect-tracking/known-issues.md) is a translator gap: FHIRCommon (hl7.fhir.uv.cql v2.0.0)
declares a single prevalenceInterval(Condition) fluent. A union of two sibling USQualityCore Condition
profiles, e.g. [ConditionProblemsHealthConcerns] union [ConditionEncounterDiagnosis], produces a
Choice<ConditionEncounterDiagnosis, ConditionProblemsHealthConcerns>, which cannot widen to FHIR.Condition,
so the FHIRCommon fluents fail to resolve (translate-time error).

This library provides Choice-typed overloads of the FHIRCommon condition functions, faithful ports of:
  - abatementInterval (FHIRCommon.cql line 371)
  - prevalenceInterval (FHIRCommon.cql line 394)
  - isVerified       (FHIRCommon.cql line 427)
  - verified         (FHIRCommon.cql line 438)

Design notes:
  1. Why not in FHIRCommon? hl7.fhir.uv.cql FHIRCommon is model-agnostic; a Choice-typed overload that
     references USQualityCore profile types would introduce a cross-model dependency. It must live in a
     USQualityCore-flavored library.
  2. The bodies never widen the Choice operand to FHIR.Condition and never call Condition-typed fluents
     (e.g. condition.abatementInterval()): abatement is computed inline at the property/datatype level via
     the local (non-fluent) abatementInterval(Choice) helper. A prior experiment that called the FHIRCommon
     fluent from a Choice overload body reproduced the widening failure and produced internal translator errors.
  3. Choice-typed fluent parameters themselves ARE supported by the translator: CMS347FHIRStatinPreventionTxCVD.cql
     (line 259) declares a local isVerified(condition Choice<ConditionEncounterDiagnosis, ConditionProblemsHealthConcerns>)
     and translates without error.
 */
library defectHelper version '1.0.000'

using USQualityCore version '0.1.0-cibuild'

include hl7.fhir.uv.cql.FHIRHelpers version '4.0.1' called FHIRHelpers
include hl7.fhir.uv.cql.FHIRCommon version '2.0.0' called FHIRCommon

codesystem "ConditionClinicalStatusCodes": 'http://terminology.hl7.org/CodeSystem/condition-clinical'
codesystem "ConditionVerificationStatusCodes": 'http://terminology.hl7.org/CodeSystem/condition-ver-status'

code "active": 'active' from "ConditionClinicalStatusCodes"
code "recurrence": 'recurrence' from "ConditionClinicalStatusCodes"
code "relapse": 'relapse' from "ConditionClinicalStatusCodes"
code "confirmed": 'confirmed' from "ConditionVerificationStatusCodes"
code "unconfirmed": 'unconfirmed' from "ConditionVerificationStatusCodes"
code "provisional": 'provisional' from "ConditionVerificationStatusCodes"
code "differential": 'differential' from "ConditionVerificationStatusCodes"

context Patient

/*
@description: Returns an interval representing the normalized abatement period of a given USQualityCore
Condition profile choice. Local (non-fluent) port of FHIRCommon.abatementInterval, operating only on the
property-level datatypes so the Choice operand never needs to widen to FHIR.Condition.
@comment: Per FHIRCommon, the Age/Range branches compute patient-age-based intervals from Patient.birthDate,
and the String branch throws a run-time exception when used with a String abatement value.
*/
// [I-28] DISABLED: Choice-overload convenience functions not viable on Translator 5.2.0 / Engine 5.2.0
// (see defect-tracking/known-issues.md and testE15ConditionUnionPrevalence.cql). Re-enabled if
// the engine adds support for Choice-typed fluent parameters / Choice overload resolution.
// define function abatementInterval(condition Choice<ConditionEncounterDiagnosis, ConditionProblemsHealthConcerns>):
//   if condition.abatement is FHIR.dateTime then
//     Interval[FHIRHelpers.ToDateTime(condition.abatement as FHIR.dateTime), FHIRHelpers.ToDateTime(condition.abatement as FHIR.dateTime)]
//   else if condition.abatement is FHIR.Period then
//     FHIRHelpers.ToInterval(condition.abatement as FHIR.Period)
//   else if condition.abatement is FHIR.string then
//     Message(null as Interval<DateTime>, true, 'NOT_IMPLEMENTED', 'Error', 'Calculation of an interval from a String value is not supported')
//   else if condition.abatement is FHIR.Age then
//     Interval[FHIRHelpers.ToDate(Patient.birthDate) + FHIRHelpers.ToQuantity(condition.abatement as FHIR.Age),
//       FHIRHelpers.ToDate(Patient.birthDate) + FHIRHelpers.ToQuantity(condition.abatement as FHIR.Age) + 1 year)
//   else if condition.abatement is FHIR.Range then
//     Interval[FHIRHelpers.ToDate(Patient.birthDate) + FHIRHelpers.ToQuantity((condition.abatement as FHIR.Range).low),
//       FHIRHelpers.ToDate(Patient.birthDate) + FHIRHelpers.ToQuantity((condition.abatement as FHIR.Range).high) + 1 year)
//   else if condition.abatement is FHIR.boolean then
//     Interval[end of condition.onset.toInterval(), condition.recordedDate)
//   else
//     null

/*
@description: Returns an interval representing the normalized prevalence period of a given USQualityCore
Condition profile choice. Faithful port of FHIRCommon.prevalenceInterval, using the local
abatementInterval(Choice) helper in place of the FHIRCommon Condition-typed fluent.
*/
// define fluent function prevalenceInterval(condition Choice<ConditionEncounterDiagnosis, ConditionProblemsHealthConcerns>):
//   if condition.clinicalStatus ~ "active"
//     or condition.clinicalStatus ~ "recurrence"
//     or condition.clinicalStatus ~ "relapse" then
//     Interval[start of condition.onset.toInterval(), end of defectHelper.abatementInterval(condition)]
//   else
//     (end of defectHelper.abatementInterval(condition)) abatementDate
//       return
//         if abatementDate is null then
//           Interval[start of condition.onset.toInterval(), abatementDate)
//         else
//           Interval[start of condition.onset.toInterval(), abatementDate]

/*
@description: Returns true if the given condition has a verification status of confirmed, unconfirmed,
provisional, or differential (or no verification status). Faithful port of FHIRCommon.isVerified.
*/
// define fluent function isVerified(condition Choice<ConditionEncounterDiagnosis, ConditionProblemsHealthConcerns>):
//   condition.verificationStatus is not null implies
//     (condition.verificationStatus ~ "confirmed"
//       or condition.verificationStatus ~ "unconfirmed"
//       or condition.verificationStatus ~ "provisional"
//       or condition.verificationStatus ~ "differential"
//     )

/*
@description: Returns conditions in the given list that either have no verification status or have a
verification status of confirmed, unconfirmed, provisional, or differential. Faithful port of
FHIRCommon.verified for the USQualityCore Condition profile choice.
*/
// define fluent function verified(conditions List<Choice<ConditionEncounterDiagnosis, ConditionProblemsHealthConcerns>>):
//   conditions C
//     where C.verificationStatus is not null implies
//       (C.verificationStatus ~ "confirmed"
//         or C.verificationStatus ~ "unconfirmed"
//         or C.verificationStatus ~ "provisional"
//         or C.verificationStatus ~ "differential"
//       )