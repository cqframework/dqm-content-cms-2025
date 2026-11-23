/*
###############################################################################
# testE11MedicationReference — engine unit-test repro for I-26
###############################################################################
#
# PURPOSE
#   Demonstrates defect I-26 (defect-tracking/known-issues.md): a
#   terminology-filtered retrieve over `MedicationRequest.medication` throws
#
#     Unable to extract codes from fhirType Reference
#
#   before any CQL `define` evaluates when a test-case fixture represents the
#   medication with `medicationReference` (pointing to a separate `Medication`
#   resource whose `.code` holds the coding) instead of `medicationCodeableConcept`.
#
#   `MedicationRequest.medication` is a FHIR choice type
#   (`CodeableConcept | Reference(Medication)`), declared in the USQualityCore
#   model info with `primaryCodePath="medication"`. When the engine's
#   `BaseRetrieveProvider.filterByTerminology` runs `[MedicationRequest: <code>]`,
#   it resolves `medication` to the actual value on each resource. A
#   `medicationReference` resolves to a `Reference` object, and
#   `CodeExtractor.getCodesFromBase` (`cqf-fhir-cql`) only extracts codes from
#   `IBaseEnumeration`, `CodeableConcept`, and `Coding` — it throws
#   `IllegalArgumentException` on `Reference`. The engine does not follow the
#   reference to the target `Medication.code`, so a spec-compliant
#   reference-based fixture crashes the retrieve.
#
#   This is the CMS165 / CMS135 root cause:
#     - CMS165 `AdvancedIllnessandFrailty.cql:77`
#       `[FHIR.MedicationRequest: "Dementia Medications"]`
#       -> fixture `45e01fed` uses `medicationReference` only (RxNorm 312836,
#          rivastigmine) -> crashes.
#     - CMS135 `[MedicationRequest: medication in "ACE Inhibitor ..."]` -> the 3
#       ACE/ARB fixtures use `medicationReference` only -> crash.
#   (The other 10 CMS165 test cases use `medicationCodeableConcept` and pass.)
#
# REPRO vs CONTROL
#   The control is a second PATIENT, not a second define. The crash aborts the
#   whole library, so two defines over the same patient can't differ. Run the
#   one define for both patients:
#     - 62577993-8c88-440d-ba30-d4a0a72990f9 (repro): one MedicationRequest with
#       `medicationReference` -> Medication/89f079aa, plus one with
#       `medicationCodeableConcept`. Result: `Unable to extract codes from
#       fhirType Reference`. A single Reference-form request anywhere in the
#       patient's data aborts every define.
#     - 7998aa53-f2dc-4cb6-b0f7-8dc726506601 (control): only the
#       `medicationCodeableConcept` request. Result: one MedicationRequest
#       (d8716091), no error.
#   Same CQL, same code, same engine; only the choice-type form differs.
#
#   Run each patient with the data path scoped to that patient's own folder
#   (`cql_execute` modelUri = .../testE11MedicationReference/<patient-id>).
#   With the data path at the measure folder, the control crashes too: the
#   terminology filter reaches the repro patient's Reference-form request even
#   though the retrieve is in Patient context.
#
# WHY NO CQL WORKAROUND (see conversion-notes "Tried and reverted")
#   Two independent rewrites on CMS135 (explicit Reference branch; valueset
#   filter moved onto `Medication.code`) failed byte-identically, because the
#   failure happens during retrieve code-extraction, BEFORE any `define` body
#   runs (empty trace blocks — no `Patient=`, no population values). Getting the
#   full JVM stack trace to the engine team requires a live breakpoint on
#   `CodeExtractor.getCodesFromBase`; static analysis of CQL/ELM/engine source
#   is exhausted.
#
# WORKAROUND (FIXTURE-SIDE, DEFLECTION ONLY)
#   Populate `medicationCodeableConcept` alongside `medicationReference` so the
#   choice path resolves to a `CodeableConcept` for code extraction. This is a
#   fixture change, NOT an engine fix — the engine bug (no Reference resolution
#   in `CodeExtractor`) remains and needs the upstream stack trace.
#
# SELF-CONTAINED
#   Uses only inline codes (no external value sets) so it runs standalone.
#
# REGISTRATION (required — see the "Unit-test (repro) convention" note in
#   conversion-notes.md; without these the engine loads the library with null
#   id/version):
#     - input/resources/library/testE11MedicationReference.json   (id/version 0.0.000)
#     - input/resources/measure/testE11MedicationReference.json   (measure + library ref)
#   fixtures: input/tests/measure/testE11MedicationReference/<patient-id>/
#     (62577993-... repro, 7998aa53-... control)
#
# Build/engine: VSCode-extension CQL engine + translator (see defect-tracking/known-issues.md).
###############################################################################
*/
library testE11MedicationReference version '0.0.000'

using FHIR version '4.0.1'

include hl7.fhir.uv.cql.FHIRHelpers version '4.0.1' called FHIRHelpers

codesystem "RxNorm": 'http://www.nlm.nih.gov/research/umls/rxnorm'

// The exact medication from the failing CMS165 fixture `45e01fed` —
// rivastigmine 6 MG Oral Capsule, a Dementia Medication
// (Medication/63369663-8430-4c47-841a-49b7d8945518).
code "Rivastigmine": '312836' from "RxNorm" display 'rivastigmine 6 MG Oral Capsule'

parameter "Measurement Period" Interval<DateTime>
  default Interval[@2026-01-01T00:00:00.000Z, @2027-01-01T00:00:00.000Z)

context Patient

/*
# Terminology-filtered retrieve over `MedicationRequest.medication`.
#   repro patient   -> throws `Unable to extract codes from fhirType Reference`
#                      (CodeExtractor.getCodesFromBase on the Reference branch)
#   control patient -> [MedicationRequest(id=d8716091-...)]
# Same shape as CMS165 `AdvancedIllnessandFrailty.cql:77` and the CMS135
# ACE/ARB retrieve.
*/
define "Rivastigmine MedicationRequests":
  [FHIR.MedicationRequest: "Rivastigmine"]
