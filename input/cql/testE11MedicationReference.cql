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
# REPRO vs PASSING
#   The FAILING define below retrieves by `medicationReference`-only data and
#   reproduces the `Unable to extract codes from fhirType Reference` error. The
#   PASSING define retrieves the identical medication carried as
#   `medicationCodeableConcept` and evaluates cleanly. This isolates the defect
#   to the Reference branch of the choice path (no translate error, no other
#   CQL in the way).
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
#   fixture: input/tests/measure/testE11MedicationReference/<patient-id>/
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
############################  FAILING (I-26)  ################################
# Terminology-filtered retrieve over `MedicationRequest.medication` where the
# fixture carries the medication as `medicationReference` (no
# `medicationCodeableConcept`). The Reference branch of the choice path reaches
# `CodeExtractor.getCodesFromBase`, which throws:
#   Unable to extract codes from fhirType Reference
# This reproduces the CMS165 `AdvancedIllnessandFrailty.cql:77` /
# CMS135 `[MedicationRequest: medication in ...]` crash in isolation — the error
# aborts before this `define` (or any other) body evaluates.
###############################################################################
*/
define "FAILING Reference-Only Medication":
  [FHIR.MedicationRequest: "Rivastigmine"]

/*
#############################  PASSING (FIX)  ################################
# The identical medication carried as `medicationCodeableConcept` (the 10
# working CMS165 fixtures). The choice path resolves to a `CodeableConcept`,
# so `CodeExtractor.getCodesFromBase` extracts RxNorm 312836 successfully and
# the retrieve returns the resource (no crash).
###############################################################################
*/
define "PASSING CodeableConcept Medication":
  [FHIR.MedicationRequest: "Rivastigmine"]
