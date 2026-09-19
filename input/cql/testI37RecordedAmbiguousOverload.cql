/*
###############################################################################
# testI37RecordedAmbiguousOverload — engine/translator unit-test repro for I-37/I-18
###############################################################################
#
# PURPOSE
#   Demonstrates defect I-37/I-18 (defect-tracking/known-issues.md): calling the
#   `recorded()` fluent function on a `ProcedureNotDone` throws at runtime:
#
#     Ambiguous call to operator 'recorded(...)' in library 'USQualityCoreCommon'
#
#   Root cause: `USQualityCoreCommon.cql` declares both `recorded(procedure Procedure)` and
#   `recorded(procedureNotDone ProcedureNotDone)`. `ProcedureNotDone`'s model-info declares
#   `target="Procedure"`; `cql-to-elm`'s `TypeBuilder.dataTypeToQName` substitutes `target` for
#   the type's own name when building the ELM QName, so both overloads serialize to the identical
#   QName `(ns, "Procedure")`. The engine's `FunctionRefEvaluator.pickFunctionDef` finds two
#   "identical" candidates and throws. Full dossier: I-18.md "Deep-dive" section, Issue 1.
#
#   This is the CMS68FHIRDocumentationCurrentMeds root cause
#   (`CMS68FHIRDocumentationCurrentMeds.cql:64`, `MedicationsNotDocumented.recorded()`) — the
#   single cause of test case f2e2e1c0's Missing Results across all 4 Group_1 populations.
#
# FIX / WORKAROUND
#   Bypass `.recorded()` entirely; read the underlying extension directly:
#     `procedureNotDone.ext('http://fhir.org/guides/astp/us-quality-core/StructureDefinition/us-quality-core-recorded').value as FHIR.dateTime`
#   `ext()` is declared generically on `DomainResource`/`Element` — no sibling-profile overload to
#   collide with. Verified working on CMS108FHIRVTEProphylaxis.cql and CMS190FHIRVTEProphylaxisICU.cql.
#   NOT applied to CMS68 — left as a deliberate Connectathon breadcrumb. See
#   defect-tracking/CONNECTATHON-BREADCRUMBS.md and defect-tracking/known-issues.md.
#
# SELF-CONTAINED
#   No FHIR fixture data required — the ambiguity fires at ELM-serialization/dispatch time from
#   the `recorded()` overload declarations, independent of any retrieved resource content. A bare
#   `[ProcedureNotDone]` retrieve is enough to trigger it once `.recorded()` is invoked.
#
# Build/engine: VSCode-extension CQL engine + translator (see defect-tracking/known-issues.md).
###############################################################################
*/
library testI37RecordedAmbiguousOverload version '0.0.000'

using USQualityCore version '0.1.0-cibuild'

include USQualityCoreCommon version '0.1.0-cibuild' called Common

context Patient

/*
############################  FAILING (I-37/I-18)  ############################
# Reproduces: Ambiguous call to operator 'recorded(...)' in library
# 'USQualityCoreCommon'.
###############################################################################
*/
define "FAILING Recorded On ProcedureNotDone":
  [ProcedureNotDone] p
    return p.recorded()

/*
#############################  PASSING (FIX)  #################################
# Equivalent working replacement: bypass the fluent function, read the
# extension directly.
###############################################################################
*/
define "PASSING Recorded Extension Bypass":
  [ProcedureNotDone] p
    return p.ext('http://fhir.org/guides/astp/us-quality-core/StructureDefinition/us-quality-core-recorded').value as FHIR.dateTime
