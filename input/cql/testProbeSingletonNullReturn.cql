library testProbeSingletonNullReturn version '0.0.1'

// Minimal analogue of FHIRCommon 2.0.0 prevalenceInterval() else-branch (FHIRCommon.cql:400-405)
// [I-31] Singleton query over null source evaluates to null (CQL §Non-Retrieve Queries)
// Upstream ticket: https://jira.hl7.org/browse/FHIR-59708 (re-authorship of FHIRCommon.cql)
// Affected test cases: none (System-types probe; CMS108 'before'+CMS71 history-of-atrial-ablation
// join isolates the same null path using CMS71 fixtures — see testPrevalenceIntervalNullPath.cql)

define "Onset": @2025-12-31T00:00:00.000Z

// 1. Bare singleton query, null vs non-null source
define "NullSource":
  (null as DateTime) X return if X is null then 'open' else 'closed'

define "NonNullSource":
  (@2026-06-01T00:00:00.000Z) X return if X is null then 'open' else 'closed'

// 2. Same shape as prevalenceInterval: end of a null interval as the source
define "NullAbatementInterval": null as Interval<DateTime>

define "QueryForm_NullAbatement":
  (end of "NullAbatementInterval") abatementDate
    return
      if abatementDate is null then
        Interval["Onset", abatementDate)
      else
        Interval["Onset", abatementDate]

define "QueryForm_NonNullAbatement":
  (end of Interval[@2026-06-01T00:00:00.000Z, @2026-06-01T00:00:00.000Z]) abatementDate
    return
      if abatementDate is null then
        Interval["Onset", abatementDate)
      else
        Interval["Onset", abatementDate]

// 3. if/else form (as in CMS108 localPrevalenceInterval) for the null case
define "IfElseForm_NullAbatement":
  if end of "NullAbatementInterval" is null then
    Interval["Onset", null as DateTime)
  else
    Interval["Onset", end of "NullAbatementInterval"]

// 4. Downstream effect: overlaps against a look-back period
define "LookBack": Interval[@2024-01-01T00:00:00.000Z, @2025-12-31T23:59:59.999Z]

define "QueryForm_Overlaps": "QueryForm_NullAbatement" overlaps day of "LookBack"

define "IfElseForm_Overlaps": "IfElseForm_NullAbatement" overlaps day of "LookBack"

// 5. Open vs closed null high bound (closed null = unbounded, open null = unknown per CQL spec)
define "ClosedNullHigh": Interval["Onset", null as DateTime]

define "ClosedNullHigh_Overlaps": "ClosedNullHigh" overlaps day of "LookBack"

define "HalfOpen_StartsBefore": "IfElseForm_NullAbatement" starts before @2026-06-01T00:00:00.000Z

define "HalfOpen_End": end of "IfElseForm_NullAbatement"

define "ClosedNull_End": end of "ClosedNullHigh"
