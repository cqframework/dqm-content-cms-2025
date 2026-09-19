/*
###############################################################################
# testE18DateTimeCompare — engine unit-test repro for I-33
###############################################################################
#
# PURPOSE
#   Demonstrates defect I-33 (defect-tracking/known-issues.md): a define that
#   returns a raw `FHIR.dateTime` (no FHIRHelpers conversion) throws
#
#     Values FHIR.dateTime and FHIR.dateTime are not comparable
#
#   at runtime when that value is consumed by either:
#     A) `sort asc` over the returned raw `FHIR.dateTime` list, or
#     B) an `Interval[..., <raw FHIR.dateTime>]` whose other endpoint is a
#        `System.DateTime` (compared during `overlaps`).
#
#   Both failures abort the library and turn every test case into a Missing
#   Result. This is exactly the CMS156 root cause
#   (`CMS156FHIRHighRiskMedsElderly.cql:230-243`, the "…Index Prescription Start
#   Date" defines): all 15 failing fixtures carried only antipsychotic `1006801`
#   or benzodiazepine `1366192` codes, and no passing fixture had either, because
#   only those two defines exercise the sort-over-raw-dateTime path.
#
# WORKAROUND (FIX)
#   Convert the raw `FHIR.dateTime` to `System.DateTime` with
#   `FHIRHelpers.ToDateTime(...)` before sorting or using it as an interval
#   endpoint:
#     - `return FHIRHelpers.ToDateTime(M.authoredOn)` then `sort asc`
#     - `Interval[start of "Measurement Period" - 1 year, FHIRHelpers.ToDateTime(...)]`
#   The FAILING defines below reproduce the error; the PASSING defines are the
#   working replacement. A `date from ...` variant is also shown (the CMS137 /
#   CMS128 idiom), which yields a System.Date and is comparable too.
#
# SELF-CONTAINED
#   Uses only inline codes (no external value sets) so it runs standalone.
#
# REGISTRATION (required — see the "Unit-test (repro) convention" note in
#   conversion-notes.md; without these the engine loads the library with null
#   id/version):
#     - input/resources/library/testE18DateTimeCompare.json   (id/version 0.0.000)
#     - input/resources/measure/testE18DateTimeCompare.json   (measure + library ref)
#   fixture: input/tests/measure/testE18DateTimeCompare/<patient-id>/
#
# Build/engine: VSCode-extension CQL engine + translator (see defect-tracking/known-issues.md).
###############################################################################
*/
library testE18DateTimeCompare version '0.0.000'

using FHIR version '4.0.1'

include hl7.fhir.uv.cql.FHIRHelpers version '4.0.1' called FHIRHelpers

codesystem "SNOMEDCT": 'http://snomed.info/sct'

// Two distinct medications (analogous to CMS156's antipsychotic 1006801 and
// benozodiazepine 1366192) so the source list has >= 2 entries and `sort` is
// genuinely exercised.
code "Medication A": '123456001' from "SNOMEDCT" display 'Medication A'
code "Medication B": '654321002' from "SNOMEDCT" display 'Medication B'

parameter "Measurement Period" Interval<DateTime>
  default Interval[@2026-01-01T00:00:00.000Z, @2027-01-01T00:00:00.000Z)

context Patient

/*
############################  FAILING (I-33)  #################################
# Each reproduces the runtime error on the new engine:
#   Values FHIR.dateTime and FHIR.dateTime are not comparable
#   (raw FHIR.dateTime, no FHIRHelpers conversion).
###############################################################################
*/

// A) `sort asc` over the raw `FHIR.dateTime` list.
define "FAILING sort raw dateTime":
  First(
    ( [FHIR.MedicationRequest: "Medication A"]
        union [FHIR.MedicationRequest: "Medication B"] ) R
      where R.authoredOn during "Measurement Period"
      return R.authoredOn
      sort asc
  )

// B) Mixed-type interval: System.DateTime start vs raw FHIR.dateTime end, compared
//    during `overlaps` (the CMS156 Numerator-2 shape, lines 168/178).
define "FAILING mixed interval overlaps":
  exists (
    ( [FHIR.MedicationRequest: "Medication A"]
        union [FHIR.MedicationRequest: "Medication B"] ) R
      where R.authoredOn during "Measurement Period"
        and ( Interval[start of "Measurement Period" - 1 year, First(
              ( [FHIR.MedicationRequest: "Medication A"]
                  union [FHIR.MedicationRequest: "Medication B"] ) M
                where M.authoredOn during "Measurement Period"
                return M.authoredOn
                sort asc
            ) ] ) overlaps Interval[2026-01-01, 2026-06-30]
  )

/*
#############################  PASSING (FIX)  ################################
# Equivalent working replacements: convert to System.DateTime via
# `FHIRHelpers.ToDateTime(...)` (or `date from` -> System.Date for the sort),
# so `sort` and the `Interval` endpoint are homogeneous and comparable.
###############################################################################
*/

// C) `sort asc` after converting to System.DateTime.
define "PASSING sort via ToDateTime":
  First(
    ( [FHIR.MedicationRequest: "Medication A"]
        union [FHIR.MedicationRequest: "Medication B"] ) R
      where R.authoredOn during "Measurement Period"
      return FHIRHelpers.ToDateTime(R.authoredOn)
      sort asc
  )

// D) `sort asc` using `date from ...` (System.Date) — the CMS137/CMS128 idiom.
define "PASSING sort via date from":
  First(
    ( [FHIR.MedicationRequest: "Medication A"]
        union [FHIR.MedicationRequest: "Medication B"] ) R
      where R.authoredOn during "Measurement Period"
      return date from R.authoredOn
      sort asc
  )

// E) Mixed-type interval with a ToDateTime-converted end (CMS156 Numerator-2 fix).
define "PASSING mixed interval via ToDateTime":
  exists (
    ( [FHIR.MedicationRequest: "Medication A"]
        union [FHIR.MedicationRequest: "Medication B"] ) R
      where R.authoredOn during "Measurement Period"
        and ( Interval[start of "Measurement Period" - 1 year, FHIRHelpers.ToDateTime(First(
              ( [FHIR.MedicationRequest: "Medication A"]
                  union [FHIR.MedicationRequest: "Medication B"] ) M
                where M.authoredOn during "Measurement Period"
                return FHIRHelpers.ToDateTime(M.authoredOn)
                sort asc
            ) )] ) overlaps Interval[2026-01-01, 2026-06-30]
  )
