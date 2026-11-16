/*
NOTE: For use by March 2026 US Realm Connectathon participants for internal use only. Not for use or distribution in commercial products.
*/
library CMS68FHIRDocumentationCurrentMeds version '1.1.000'

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

codesystem "SNOMEDCT": 'http://snomed.info/sct'

valueset "Encounter to Document Medications": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.600.1.1834'

code "Acute health crisis (finding)": '705016005' from "SNOMEDCT" display 'Acute health crisis (finding)'
code "Documentation of current medications (procedure)": '428191000124101' from "SNOMEDCT" display 'Documentation of current medications (procedure)'

parameter "Measurement Period" Interval<DateTime>
  default Interval[@2026-01-01T00:00:00.000Z, @2027-01-01T00:00:00.000Z)

context Patient

define "SDE Ethnicity":
  SDE."SDE Ethnicity"

define "SDE Payer":
  SDE."SDE Payer"

define "SDE Race":
  SDE."SDE Race"

define "SDE Sex":
  SDE."SDE Sex"

define "Denominator":
  "Initial Population"

define "Qualifying Encounter During Day of Measurement Period":
  ["Encounter": "Encounter to Document Medications"] ValidEncounter
    where ValidEncounter.status = 'finished'
      and ValidEncounter.period during day of "Measurement Period"

define "Initial Population":
  "Qualifying Encounter During Day of Measurement Period" QualifyingEncounter

define "Numerator":
  "Qualifying Encounter During Day of Measurement Period" QualifyingEncounter
    with [Procedure: "Documentation of current medications (procedure)"] MedicationsDocumented
      such that MedicationsDocumented.performed.toInterval ( ) starts during day of QualifyingEncounter.period
        and MedicationsDocumented.performed.toInterval ( ).hasEnd ( )
        and MedicationsDocumented.status = 'completed'

define "Denominator Exceptions":
  "Qualifying Encounter During Day of Measurement Period" QualifyingEncounter
    with [USQualityCore.ProcedureNotDone: code ~ "Documentation of current medications (procedure)"] MedicationsNotDocumented
      // [I-55] `recordedProcedureNotDone()` instead of `.recorded()`: recorded(ProcedureNotDone) is ambiguous with recorded(Procedure) - dodges the I-18 overload ambiguity
      // Upstream ticket: https://github.com/cqframework/clinical_quality_language/issues/1855
      // Affected test cases: all 19 CMS68 cases (library-wide .ext() bypass)
      // original
      //   such that MedicationsNotDocumented.recorded ( ) during day of QualifyingEncounter.period
      such that MedicationsNotDocumented.recordedProcedureNotDone() during day of QualifyingEncounter.period
        and MedicationsNotDocumented.status = 'not-done'
        and exists ( MedicationsNotDocumented.reasonCode reasonItem
            where reasonItem ~ "Acute health crisis (finding)"
        )

// [I-55] `.ext()` instead of `.recorded()`: the shared `recorded()` overload is ambiguous for ProcedureNotDone - dodges the I-18 overload ambiguity
// Upstream ticket: https://github.com/cqframework/clinical_quality_language/issues/1855
// Affected test cases: all 19 CMS68 cases (library-wide .ext() bypass)
define fluent function recordedProcedureNotDone(procedureNotDone ProcedureNotDone):
  procedureNotDone.ext('http://fhir.org/guides/astp/us-quality-core/StructureDefinition/us-quality-core-recorded').value as FHIR.dateTime
