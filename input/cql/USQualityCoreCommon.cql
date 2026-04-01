/*
@description: Common terminologies and functions used in USQualityCore-based CQL artifacts
@comment: The modelinfo included with the published IG is using [derived modelinfo](https://hl7.org/fhir/uv/cql/using-modelinfo.html#derived-modelinfo)
to enable reuse of data elements and libraries defined in the [US Core](https://hl7.org/fhir/us/core) 
and [US CQL](https://hl7.org/fhir/us/cql) Common IGs. This library is derived from the QICoreCommon shared library used in FHIR-based 
quality measure specifications. However, most of the functionality that was defined in QICoreCommon is now either in [FHIRCommon](https://hl7.org/fhir/uv/cql/Library-FHIRCommon.html)
or [USCoreCommon](https://hl7.org/fhir/us/cql/Library-USCoreCommon.html).
*/
library USQualityCoreCommon version '0.1.0-cibuild'

using USQualityCore version '0.1.0-cibuild'

include hl7.fhir.uv.cql.FHIRHelpers version '4.0.1'
include hl7.fhir.uv.cql.FHIRCommon version '2.0.0'

codesystem "ActCode": 'http://terminology.hl7.org/CodeSystem/v3-ActCode'
codesystem "TaskCodeSystem": 'http://hl7.org/fhir/CodeSystem/task-code' 

// Encounter Class Codes
code "ambulatory": 'AMB' from ActCode display 'ambulatory'
code "emergency": 'EMER' from ActCode display 'emergency'
code "field": 'FLD' from ActCode display 'field'
code "home health": 'HH' from ActCode display 'home health'
code "inpatient encounter": 'IMP' from ActCode display 'inpatient encounter'
code "inpatient acute": 'ACUTE' from ActCode display 'inpatient acute'
code "inpatient non-acute": 'NONAC' from ActCode display 'inpatient non-acute'
code "observation encounter": 'OBSENC' from ActCode display 'observation encounter'
code "pre-admission": 'PRENC' from ActCode display 'pre-admission'
code "short stay": 'SS' from ActCode display 'short stay'
code "virtual": 'VR' from ActCode display 'Virtual'

//Task codes
code "Fulfill": 'fulfill' from "TaskCodeSystem" display 'Fulfill'

context Patient

/*
@description: Returns the id of the given uri (i.e. everything after the last slash)
*/
define fluent function getId(uri String):
  Last(Split(uri, '/'))

/*
@description: Returns the System.ValueSet instance with the url and version (if present) of the given canonical reference
*/
define fluent function toValueSet(canonical FHIR.canonical):
  System.ValueSet {
    id: canonical.url(),
    version: canonical.version()
  }

/*
@description: Converts the activity extent pattern used to represent negated activities to either a codeableConcept or a value set
@seealso: [Negation In US Quality Core](negation.html)
*/
define fluent function toActivityExtent(codeable Choice<FHIR.CodeableConcept, FHIR.canonical>):
  case
    when codeable is FHIR.canonical then codeable.toValueSet()
    else codeable as FHIR.CodeableConcept
  end

/*
@description: Returns the value of the recorded extension for a Communication Not Done
*/
define fluent function recorded(communicationNotDone CommunicationNotDone):
  communicationNotDone.ext('http://fhir.org/guides/astp/us-quality-core/StructureDefinition/us-quality-core-recorded').value as FHIR.dateTime

/*
@description: Returns the negated activity extent for a Communication Not Done
@seealso: [Negation In US Quality Core](negation.html)
*/
define fluent function topic(communicationNotDone CommunicationNotDone):
  communicationNotDone.topic.ext('http://fhir.org/guides/astp/us-quality-core/StructureDefinition/us-quality-core-notDoneValueSet').value.toActivityExtent()

/*
@description: Returns the value of the doNotPerformReason extension for a Device Not Requested
*/
define fluent function doNotPerformReason(deviceNotRequested DeviceNotRequested):
  deviceNotRequested.ext('http://fhir.org/guides/astp/us-quality-core/StructureDefinition/us-quality-core-doNotPerformReason').value as FHIR.CodeableConcept

/*
@description: Returns the value of the doNotPerform extension for a Device Not Requested
*/
define fluent function doNotPerform(deviceNotRequested DeviceNotRequested):
  deviceNotRequested.ext('http://hl7.org/fhir/5.0/StructureDefinition/extension-DeviceRequest.doNotPerform').value as FHIR.boolean

/*
@description: Returns the negated activity extent for a Device Not Requested
@seealso: [Negation In US Quality Core](negation.html)
*/
define fluent function code(deviceNotRequested DeviceNotRequested):
  deviceNotRequested.code.ext('http://fhir.org/guides/astp/us-quality-core/StructureDefinition/us-quality-core-notDoneValueSet').value.toActivityExtent()

/*
@description: Returns the value of the abatement extension for a FamilyMemberHistory
*/
define fluent function abatement(familyMemberHistory FamilyMemberHistory):
  familyMemberHistory.ext('hl7.org/fhir/StructureDefinition/familymemberhistory-abatement').value as Choice<FHIR.date, FHIR.Age, FHIR.boolean>

/*
@description: Returns the value of the severity extension for a FamilyMemberHistory
*/
define fluent function severity(familyMemberHistory FamilyMemberHistory):
  familyMemberHistory.ext('hl7.org/fhir/StructureDefinition/familymemberhistory-severity').value as FHIR.CodeableConcept

/*
@description: Returns the negated activity extent for an Immunization Not Done
@seealso: [Negation In US Quality Core](negation.html)
*/
define fluent function vaccineCode(immunizationNotDone ImmunizationNotDone):
  immunizationNotDone.vaccineCode.ext('http://fhir.org/guides/astp/us-quality-core/StructureDefinition/us-quality-core-notDoneValueSet').value.toActivityExtent()

/*
@description: Returns the value of the recorded extension for a Medication Administration Not Done
*/
define fluent function recorded(medicationAdministrationNotDone MedicationAdministrationNotDone):
  medicationAdministrationNotDone.ext('http://fhir.org/guides/astp/us-quality-core/StructureDefinition/us-quality-core-recorded').value as FHIR.dateTime

/*
@description: Returns the negated activity extent for a Medication Administration Not Done
@seealso: [Negation In US Quality Core](negation.html)
*/
define fluent function medication(medicationAdministrationNotDone MedicationAdministrationNotDone):
  medicationAdministrationNotDone.medication.ext('http://fhir.org/guides/astp/us-quality-core/StructureDefinition/us-quality-core-notDoneValueSet').value.toActivityExtent()

/*
@description: Returns the value of the recorded extension for a Medication Dispense Declined
*/
define fluent function recorded(medicationDispenseDeclined MedicationDispenseDeclined):
  medicationDispenseDeclined.ext('http://fhir.org/guides/astp/us-quality-core/StructureDefinition/us-quality-core-recorded').value as FHIR.dateTime

/*
@description: Returns the negated activity extent for a Medication Dispense Declined
@seealso: [Negation In US Quality Core](negation.html)
*/
define fluent function medication(medicationDispenseDeclined MedicationDispenseDeclined):
  (medicationDispenseDeclined.medication as FHIR.CodeableConcept).ext('http://fhir.org/guides/astp/us-quality-core/StructureDefinition/us-quality-core-notDoneValueSet').value.toActivityExtent()

/*
@description: Returns the negated activity extent for a Medication Not Requested
@seealso: [Negation In US Quality Core](negation.html)
*/
define fluent function medication(medicationNotRequested MedicationNotRequested):
  medicationNotRequested.medication.ext('http://fhir.org/guides/astp/us-quality-core/StructureDefinition/us-quality-core-notDoneValueSet').value.toActivityExtent()

/*
@description: Returns the notDoneReason for an ObservationCancelled
*/
define fluent function notDoneReason(observationCancelled ObservationCancelled):
  observationCancelled.ext('http://fhir.org/guides/astp/us-quality-core/StructureDefinition/us-quality-core-notDoneReason').value as FHIR.CodeableConcept

/*
@description: Returns the negated activity extent for an ObservationCancelled
@seealso: [Negation In US Quality Core](negation.html)
*/
define fluent function code(observationCancelled ObservationCancelled):
  observationCancelled.code.ext('http://fhir.org/guides/astp/us-quality-core/StructureDefinition/us-quality-core-notDoneValueSet').value.toActivityExtent()

/*
@description: Returns the value of the recorded extension for a Procedure
*/
define fluent function recorded(procedure Procedure):
  procedure.ext('http://fhir.org/guides/astp/us-quality-core/StructureDefinition/us-quality-core-recorded').value as FHIR.dateTime

/*
@description: Returns the value of the recorded extension for a Medication Administration Not Done
*/
define fluent function recorded(procedureNotDone ProcedureNotDone):
  procedureNotDone.ext('http://fhir.org/guides/astp/us-quality-core/StructureDefinition/us-quality-core-recorded').value as FHIR.dateTime

/*
@description: Returns the negated activity extent for a Procedure Not Done
@seealso: [Negation In US Quality Core](negation.html)
*/
define fluent function code(procedureNotDone ProcedureNotDone):
  procedureNotDone.code.ext('http://fhir.org/guides/astp/us-quality-core/StructureDefinition/us-quality-core-notDoneValueSet').value.toActivityExtent()

/*
@description: Returns the value of the recorded extension for a Medication Administration Not Done
*/
define fluent function reasonRefused(serviceNotRequested ServiceNotRequested):
  serviceNotRequested.ext('http://fhir.org/guides/astp/us-quality-core/StructureDefinition/us-quality-core-doNotPerformReason').value as FHIR.CodeableConcept

/*
@description: Returns the negated activity extent for a Service Not Requested
@seealso: [Negation In US Quality Core](negation.html)
*/
define fluent function code(serviceNotRequested ServiceNotRequested):
  serviceNotRequested.code.ext('http://fhir.org/guides/astp/us-quality-core/StructureDefinition/us-quality-core-notDoneValueSet').value.toActivityExtent()

/*
@description: Returns the negated activity extent for a Task Rejected
@seealso: [Negation In US Quality Core](negation.html)
*/
define fluent function code(taskRejected TaskRejected):
  taskRejected.code.ext('http://fhir.org/guides/astp/us-quality-core/StructureDefinition/us-quality-core-notDoneValueSet').value.toActivityExtent()

/*
@description: Creates a list of integers from 1 to how many days are in the interval. Note, this wont create an index for
the final day if it is less than 24 hours. This also includes the first 24 hour period.
*/
define fluent function toDayNumbers(Period Interval<DateTime>):
  ( expand { Interval[1, duration in days between start of Period and end of Period]} ) DayNumber
    return end of DayNumber

/*
@description: Creates a list of 24 hour long intervals in an interval paired with the index (1 indexed) to which 24 hour interval it is.
Note that the result will include intervals that are closed at the beginning and open at the end
*/
define fluent function daysInPeriod(Period Interval<DateTime>):
  ( Period.toDayNumbers()) DayIndex
    let startPeriod: start of Period + (24 hours * (DayIndex - 1)),
    endPeriod: if (hours between startPeriod and end of Period < 24) then startPeriod
      else start of Period + (24 hours * DayIndex)
    return Tuple {
      dayIndex: DayIndex,
      dayPeriod: Interval[startPeriod, endPeriod)
    }
  