/*
NOTE: For use by March 2026 US Realm Connectathon participants for internal use only. Not for use or distribution in commercial products.
*/
library CMS104FHIRSTKDCAntithrombotic version '1.1.000'

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

include TJCOverall version '9.1.000' called TJC

valueset "Antithrombotic Therapy for Ischemic Stroke": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113762.1.4.1110.62'
valueset "Medical Reason For Not Providing Treatment": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.117.1.7.1.473'
valueset "Patient Refusal": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.117.1.7.1.93'
valueset "Pharmacological Contraindications For Antithrombotic Therapy": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113762.1.4.1110.52'

parameter "Measurement Period" Interval<DateTime>
  default Interval[@2026-01-01T00:00:00.000Z, @2027-01-01T00:00:00.000Z)

context Patient

define "Initial Population":
  TJC."Ischemic Stroke Encounter"

define "Denominator":
  "Initial Population"

define "Denominator Exclusions":
  TJC."Ischemic Stroke Encounters With Discharge Disposition"
    union TJC."Encounter With Comfort Measures During Hospitalization"

define "Numerator":
  TJC."Ischemic Stroke Encounter" IschemicStrokeEncounter
    with ["MedicationRequest": "Antithrombotic Therapy for Ischemic Stroke"] DischargeAntithrombotic
      such that DischargeAntithrombotic.status in { 'active', 'completed' }
        and DischargeAntithrombotic.intent in { 'order', 'original-order', 'reflex-order', 'filler-order', 'instance-order' }
        and ( DischargeAntithrombotic.isCommunity ( )
            or DischargeAntithrombotic.isDischarge ( )
        )
        and DischargeAntithrombotic.authoredOn during IschemicStrokeEncounter.period
        and not exists ( ["TaskRejected"] TaskReject
            where TaskReject.focus.references ( DischargeAntithrombotic )
              and TaskReject.code ~ USQualityCoreCommon."Fulfill"
        )

define "Denominator Exceptions":
  "Encounter With Documented Reason For No Antithrombotic At Discharge"
    union "Encounter With Pharmacological Contraindications For Antithrombotic Therapy At Discharge"

define "Encounter With Documented Reason For No Antithrombotic At Discharge":
  TJC."Ischemic Stroke Encounter" IschemicStrokeEncounter
    with "Reason For Not Giving Antithrombotic At Discharge" NoDischargeAntithrombotic
      such that NoDischargeAntithrombotic.authoredOn during IschemicStrokeEncounter.period

define "Reason For Not Giving Antithrombotic At Discharge":
  ( ["MedicationNotRequested": "Antithrombotic Therapy for Ischemic Stroke"] NoAntithromboticDischarge
      where ( NoAntithromboticDischarge.reasonCode in "Medical Reason For Not Providing Treatment"
          or NoAntithromboticDischarge.reasonCode in "Patient Refusal"
      )
        and ( NoAntithromboticDischarge.isCommunity ( )
            or NoAntithromboticDischarge.isDischarge ( )
        )
        and NoAntithromboticDischarge.status in { 'active', 'completed' }
        and NoAntithromboticDischarge.intent in { 'order', 'original-order', 'reflex-order', 'filler-order', 'instance-order' }
  )
    union ( ["MedicationRequest": "Antithrombotic Therapy for Ischemic Stroke"] MedReqAntithrombotic
        with ["TaskRejected"] TaskReject
          such that TaskReject.focus.references ( MedReqAntithrombotic )
            and ( TaskReject.statusReason in "Medical Reason For Not Providing Treatment"
                or TaskReject.statusReason in "Patient Refusal"
            )
            and MedReqAntithrombotic.status in { 'active', 'completed' }
            and TaskReject.code ~ USQualityCoreCommon."Fulfill"
    )

define "Encounter With Pharmacological Contraindications For Antithrombotic Therapy At Discharge":
  TJC."Ischemic Stroke Encounter" IschemicStrokeEncounter
    with "Pharmacological Contraindications For Antithrombotic Therapy At Discharge" DischargePharmacological
      such that DischargePharmacological.authoredOn during IschemicStrokeEncounter.period

define "Pharmacological Contraindications For Antithrombotic Therapy At Discharge":
  ["MedicationRequest": "Pharmacological Contraindications For Antithrombotic Therapy"] PharmacologicalContraindications
    where ( PharmacologicalContraindications.isCommunity ( )
        or PharmacologicalContraindications.isDischarge ( )
    )
      and PharmacologicalContraindications.status in { 'active', 'completed' }
      and PharmacologicalContraindications.intent in { 'order', 'original-order', 'reflex-order', 'filler-order', 'instance-order' }

define "SDE Ethnicity":
  SDE."SDE Ethnicity"

define "SDE Payer":
  SDE."SDE Payer"

define "SDE Race":
  SDE."SDE Race"

define "SDE Sex":
  SDE."SDE Sex"