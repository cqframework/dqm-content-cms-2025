library testCMS72INRDenominatorException

using USQualityCore version '0.1.0-cibuild'
using FHIR version '4.0.1'

include hl7.fhir.uv.cql.FHIRHelpers version '4.0.1' called FHIRHelpers
include CQMCommon version '5.1.000' called CQMCommon
include TJCOverall version '9.1.000' called TJC

valueset "INR": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.117.1.7.1.213'

parameter "Measurement Period" Interval<DateTime>
  default Interval[@2026-01-01T00:00:00.000Z, @2027-01-01T00:00:00.000Z)

context Patient

define "Stroke Encounter ids": TJC."Ischemic Stroke Encounter" E return E.id
define "Hospitalization start": TJC."Ischemic Stroke Encounter" E return start of E.hospitalizationWithObservation()
define "Window": TJC."Ischemic Stroke Encounter" E return (start of E.hospitalizationWithObservation()).calendarDayOfOrDayAfter()
define "All lab Observations": [USQualityCore.LaboratoryResultObservation] O return O.id
define "INR retrieve": [USQualityCore.LaboratoryResultObservation: "INR"] O return O.id
define "Base Observation INR": [FHIR.Observation: "INR"] O return O.id
define "INR value": [USQualityCore.LaboratoryResultObservation: "INR"] O return O.value as Quantity
define "INR value unit": [USQualityCore.LaboratoryResultObservation: "INR"] O return (O.value as Quantity).unit
define "INR gt 3.5": [USQualityCore.LaboratoryResultObservation: "INR"] O return (O.value as Quantity) > 3.5
define "INR status ok": [USQualityCore.LaboratoryResultObservation: "INR"] O return O.status in { 'final', 'amended', 'corrected' }
define "INR issued": [USQualityCore.LaboratoryResultObservation: "INR"] O return O.issued
define "Encounters with INR gt 3.5":
  TJC."Ischemic Stroke Encounter" E
    with [USQualityCore.LaboratoryResultObservation: "INR"] O
      such that O.value as Quantity > 3.5
    return E.id
define "Control 100 '1' gt 3.5": 100 '1' > 3.5
define "Control 100 '0' gt 3.5": 100 '0' > 3.5
define "Control 100 '0' converted to '1'": ConvertQuantity(100 '0', '1')
define "Control 100 '0' equal 100 '1'": 100 '0' = 100 '1'
