library testI69IsIntervalNullBound version '0.0.1'

// [I-69] `is Interval<T>` returns false when the interval has a null boundary (engine `IsEvaluator`)
// Upstream ticket: https://github.com/cqframework/clinical_quality_language/pull/1857
// Affected test cases: none — engine-only probe, no model and no data (QI-Core side: CMS347 1ba7b147, CMS646 ab48e0c0)

// Same dispatch as QICoreCommon.toInterval(), cut down to the DateTime / Interval<DateTime> branches
define function localToInterval(choice Choice<DateTime, Interval<DateTime>>):
  case
    when choice is DateTime then Interval[choice as DateTime, choice as DateTime]
    when choice is Interval<DateTime> then choice as Interval<DateTime>
    else null as Interval<DateTime>
  end

define function choiceIsNull(choice Choice<DateTime, Interval<DateTime>>):
  choice is null

define function choiceIsInterval(choice Choice<DateTime, Interval<DateTime>>):
  choice is Interval<DateTime>

// --- direct `is` on literals
define "A1 closed is Interval<DateTime>":
  Interval[@2026-04-02T08:00:00.000Z, @2026-04-03T08:00:00.000Z] is Interval<DateTime>
define "A2 open-high is Interval<DateTime>":
  Interval[@2026-04-02T08:00:00.000Z, null) is Interval<DateTime>
define "A3 open-low is Interval<DateTime>":
  Interval(null, @2026-04-02T08:00:00.000Z] is Interval<DateTime>
define "A4 open-high Integer is Interval<Integer>":
  Interval[1, null) is Interval<Integer>
define "A5 open-high value is null":
  Interval[@2026-04-02T08:00:00.000Z, null) is null

// --- through a Choice-typed argument, as in toInterval(onset)
define "B1 closed via choice: toInterval":
  localToInterval(Interval[@2026-04-02T08:00:00.000Z, @2026-04-03T08:00:00.000Z])
define "B2 open-high via choice: toInterval":
  localToInterval(Interval[@2026-04-02T08:00:00.000Z, null))
define "B3 open-high via choice: arg is null":
  choiceIsNull(Interval[@2026-04-02T08:00:00.000Z, null))
define "B4 open-high via choice: arg is Interval<DateTime>":
  choiceIsInterval(Interval[@2026-04-02T08:00:00.000Z, null))
define "B5 DateTime via choice: toInterval":
  localToInterval(@2026-04-02T08:00:00.000Z)
