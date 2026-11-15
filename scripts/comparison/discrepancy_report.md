# Discrepancy Report
| Details | Value |
| --- | --- |
| Generated | 2026-11-15 16:46:34.692712 |
| Total Measures | 74 |
| Total Test Cases | 3964 |
| Measures with Discrepancies | 14 |
| Pass Count | 3904 (98.49%) |
| Workaround Count | 46 (1.16%) |
| &nbsp;&nbsp;— covered by a ticketed known issue | 46 (1.16%) |
| Implementation Issue Count | 9 (0.23%) |
| Known Issue Count (ticketed) | 5 (0.13%) |
| Fail Count | 0 (0.00%) |
| Known issues with an upstream ticket | 51 (1.29%) |
| Resolved without workaround (Pass + Implementation + Known Issue) | 3918 (98.84%) |


_Every test case is in exactly one bucket: 3904 Pass + 9 Implementation + 5 Known Issue + 46 Workaround + 0 Fail = 3964. Resolved without workaround counts Pass, Implementation (the steward's test case is wrong; the CQL is right) and Known Issue (an engine or translator defect with an upstream ticket). Workaround cases are left out because they match only through CQL that works around an open issue, so each needs re-checking once its workaround is removed._

| Discrepancy Summary | Measure Count | Test Case Count |
|---|:---:|:---:|
| Missing Results | 3 | 5 |
| Missing Populations | 0 | 0 |
| Mismatched Test Cases | 6 | 9 |
| Workarounds | 8 | 83 |
| Unattributed Discrepancies | 0 | 0 |



_Note: Measures can have multiple discrepancies, so the Measures with Discrepancies count may not match the summary counts. Unattributed Discrepancies are those no implementation issue or ticketed known issue resolves. Workarounds are test cases that match their fixture only because the CQL works around an open issue: they count as neither a pass nor a failure, and the workaround is removed once the root cause is fixed._

## Populations Excluded from Automated Scoring (CQFM Aggregation)

_These populations require invoking a parameterized CQL `measure-observation` function once per member of a `cqfm-criteriaReference` population and then applying `cqfm-aggregateMethod` (Sum/Count/Average) -- a computation this harness's CQL-execution path cannot perform (no scriptable/batch CQL runner; see `defect-tracking/known-issues.md`, I-62). They are intentionally excluded from pass/fail scoring rather than reported as FAIL or silently read as 0. Every other population on these measures (Initial Population, Denominator, Numerator, exclusions, etc.) is unaffected and scored normally. Use the cql-mcp `cql_execute` per-member probe method documented in I-62 to manually verify any of the expected values below._

| Measure | Excluded Populations |
| --- | --- |
| CMS871FHIRHHHyper | Group_1:Denominator Observation, Group_1:Measure Observation, Group_1:Numerator Observation |
| CMS986FHIRMalnutritionScore | Group_1:Measure Observation, Group_2:Measure Observation, Group_3:Measure Observation, Group_4:Measure Observation, Group_5:Measure Observation, Group_6:Measure Observation |
| CMS1017FHIRHHFI | Group_1:Denominator Observation, Group_1:Measure Observation, Group_1:Numerator Observation |

_2089 cells excluded across 3 measures._

## I-28 Workaround Note

_31 measures include the I-28 workaround: the original sibling-profile `[ConditionProblemsHealthConcerns: ...] union [ConditionEncounterDiagnosis: ...]` retrieves were replaced with a single base `[FHIR.Condition: ...]` retrieve. The base-`Condition` retrieve is the preferred CQL pattern for this content while I-28 is open -- it selects the same Conditions the union expresses, so the change is semantics-preserving, and it is the only form the translator resolves today. It is a workaround, not a fix: the original union code is valid CQL, and I-28 is the translator defect that blocks it (`Choice<...>` arguments are not widened to base `Condition`, for either a shared-library `prevalenceInterval` overload or an ancestor overload). The union defect is tracked by [cqframework/clinical_quality_language#1872](https://github.com/cqframework/clinical_quality_language/issues/1872); once that ticket closes, these measures' workarounds could be reverted to the original union code, but using just Condition is the preferred pattern.Individual test cases are not listed because the workaround is library-wide: every test case of every measure below runs it._

|  |  |  |
| --- | --- | --- |
| [ CMS56FHIRFuncStatHipReplacement ](../../input/cql/CMS56FHIRFuncStatHipReplacement.cql) | [ CMS138FHIRTobaccoScrnCessation ](../../input/cql/CMS138FHIRTobaccoScrnCessation.cql) | [ CMS349FHIRHIVScreening ](../../input/cql/CMS349FHIRHIVScreening.cql) |
| [ CMS69FHIRPCSBMIScreenAndFollowUp ](../../input/cql/CMS69FHIRPCSBMIScreenAndFollowUp.cql) | [ CMS142FHIRCommWithDrManagingDiab ](../../input/cql/CMS142FHIRCommWithDrManagingDiab.cql) | [ CMS645FHIRBoneDensityPCADTherapy ](../../input/cql/CMS645FHIRBoneDensityPCADTherapy.cql) |
| [ CMS75FHIRChildrenDentalDecay ](../../input/cql/CMS75FHIRChildrenDentalDecay.cql) | [ CMS143FHIRPOAGOpticNerveEval ](../../input/cql/CMS143FHIRPOAGOpticNerveEval.cql) | [ CMS646FHIRIntravesicalBCGTherapy ](../../input/cql/CMS646FHIRIntravesicalBCGTherapy.cql) |
| [ CMS90FHIRFSAforHeartFailure ](../../input/cql/CMS90FHIRFSAforHeartFailure.cql) | [ CMS144FHIRHFBetaBlockerForLVSD ](../../input/cql/CMS144FHIRHFBetaBlockerForLVSD.cql) | [ CMS771FHIRUrinarySymptomScoreBPH ](../../input/cql/CMS771FHIRUrinarySymptomScoreBPH.cql) |
| [ CMS117FHIRChildImmunStatus ](../../input/cql/CMS117FHIRChildImmunStatus.cql) | [ CMS153FHIRChlamydiaScreening ](../../input/cql/CMS153FHIRChlamydiaScreening.cql) | [ CMS951FHIRKidneyHealthEval ](../../input/cql/CMS951FHIRKidneyHealthEval.cql) |
| [ CMS124FHIRCervicalCancerScreen ](../../input/cql/CMS124FHIRCervicalCancerScreen.cql) | [ CMS155FHIRWgtAssessCounseling ](../../input/cql/CMS155FHIRWgtAssessCounseling.cql) | [ CMS996FHIRAptTxforSTEMI ](../../input/cql/CMS996FHIRAptTxforSTEMI.cql) |
| [ CMS128FHIRAntidepressantMgmt ](../../input/cql/CMS128FHIRAntidepressantMgmt.cql) | [ CMS156FHIRHighRiskMedsElderly ](../../input/cql/CMS156FHIRHighRiskMedsElderly.cql) | [ CMS1154ScreeningPrediabetesFHIR ](../../input/cql/CMS1154ScreeningPrediabetesFHIR.cql) |
| [ CMS129FHIRProstCaBoneScanUse ](../../input/cql/CMS129FHIRProstCaBoneScanUse.cql) | [ CMS157FHIRPainIntensityQuantified ](../../input/cql/CMS157FHIRPainIntensityQuantified.cql) | [ CMS1157FHIRHIVRetention ](../../input/cql/CMS1157FHIRHIVRetention.cql) |
| [ CMS131FHIRDiabetesEyeExam ](../../input/cql/CMS131FHIRDiabetesEyeExam.cql) | [ CMS159FHIRDepRemissionat12Months ](../../input/cql/CMS159FHIRDepRemissionat12Months.cql) | [ CMS1188FHIRHIVSTITesting ](../../input/cql/CMS1188FHIRHIVSTITesting.cql) |
| [ CMS133FHIRCataracts2040BCVA90Days ](../../input/cql/CMS133FHIRCataracts2040BCVA90Days.cql) | [ CMS314FHIRHIVViralSuppression ](../../input/cql/CMS314FHIRHIVViralSuppression.cql) |  |
| [ CMS136FHIRChildADHDMedFollowUp ](../../input/cql/CMS136FHIRChildADHDMedFollowUp.cql) | [ CMS347FHIRStatinPreventionTxCVD ](../../input/cql/CMS347FHIRStatinPreventionTxCVD.cql) |  |


## Measures with No Discrepancies (60 of 74)

|  |  |  |
| --- | --- | --- |
| [ CMS2FHIRPCSDepScreenAndFollowUp ](../../input/cql/CMS2FHIRPCSDepScreenAndFollowUp.cql) | [ CMS138FHIRTobaccoScrnCessation ](../../input/cql/CMS138FHIRTobaccoScrnCessation.cql) | [ CMS816FHIRHHHypo ](../../input/cql/CMS816FHIRHHHypo.cql) |
| [ CMS22FHIRPCSBPScreeningFollowUp ](../../input/cql/CMS22FHIRPCSBPScreeningFollowUp.cql) | [ CMS139FHIRFallRiskScreening ](../../input/cql/CMS139FHIRFallRiskScreening.cql) | [ CMS819FHIRHHORAE ](../../input/cql/CMS819FHIRHHORAE.cql) |
| [ CMS50FHIRReceiptofSpecialistReport ](../../input/cql/CMS50FHIRReceiptofSpecialistReport.cql) | [ CMS142FHIRCommWithDrManagingDiab ](../../input/cql/CMS142FHIRCommWithDrManagingDiab.cql) | [ CMS826FHIRHHPI ](../../input/cql/CMS826FHIRHHPI.cql) |
| [ CMS56FHIRFuncStatHipReplacement ](../../input/cql/CMS56FHIRFuncStatHipReplacement.cql) | [ CMS143FHIRPOAGOpticNerveEval ](../../input/cql/CMS143FHIRPOAGOpticNerveEval.cql) | [ CMS832FHIRHHAKI ](../../input/cql/CMS832FHIRHHAKI.cql) |
| [ CMS69FHIRPCSBMIScreenAndFollowUp ](../../input/cql/CMS69FHIRPCSBMIScreenAndFollowUp.cql) | [ CMS144FHIRHFBetaBlockerForLVSD ](../../input/cql/CMS144FHIRHFBetaBlockerForLVSD.cql) | [ CMS951FHIRKidneyHealthEval ](../../input/cql/CMS951FHIRKidneyHealthEval.cql) |
| [ CMS74FHIRDentalCariesPrevention ](../../input/cql/CMS74FHIRDentalCariesPrevention.cql) | [ CMS146FHIRApproTestPharyngitis ](../../input/cql/CMS146FHIRApproTestPharyngitis.cql) | [ CMS986FHIRMalnutritionScore ](../../input/cql/CMS986FHIRMalnutritionScore.cql) |
| [ CMS75FHIRChildrenDentalDecay ](../../input/cql/CMS75FHIRChildrenDentalDecay.cql) | [ CMS149FHIRDementiaCognitiveAssess ](../../input/cql/CMS149FHIRDementiaCognitiveAssess.cql) | [ CMS1017FHIRHHFI ](../../input/cql/CMS1017FHIRHHFI.cql) |
| [ CMS90FHIRFSAforHeartFailure ](../../input/cql/CMS90FHIRFSAforHeartFailure.cql) | [ CMS153FHIRChlamydiaScreening ](../../input/cql/CMS153FHIRChlamydiaScreening.cql) | [ CMS1028FHIRPCSevereOBComps ](../../input/cql/CMS1028FHIRPCSevereOBComps.cql) |
| [ CMS104FHIRSTKDCAntithrombotic ](../../input/cql/CMS104FHIRSTKDCAntithrombotic.cql) | [ CMS154FHIRAppropriateTxforURI ](../../input/cql/CMS154FHIRAppropriateTxforURI.cql) | [ CMS1056FHIRCTClinical ](../../input/cql/CMS1056FHIRCTClinical.cql) |
| [ CMS117FHIRChildImmunStatus ](../../input/cql/CMS117FHIRChildImmunStatus.cql) | [ CMS155FHIRWgtAssessCounseling ](../../input/cql/CMS155FHIRWgtAssessCounseling.cql) | [ CMS1074FHIRCTIQR ](../../input/cql/CMS1074FHIRCTIQR.cql) |
| [ CMS122FHIRDiabetesAssessGT9Pct ](../../input/cql/CMS122FHIRDiabetesAssessGT9Pct.cql) | [ CMS157FHIRPainIntensityQuantified ](../../input/cql/CMS157FHIRPainIntensityQuantified.cql) | [ CMS1154ScreeningPrediabetesFHIR ](../../input/cql/CMS1154ScreeningPrediabetesFHIR.cql) |
| [ CMS124FHIRCervicalCancerScreen ](../../input/cql/CMS124FHIRCervicalCancerScreen.cql) | [ CMS159FHIRDepRemissionat12Months ](../../input/cql/CMS159FHIRDepRemissionat12Months.cql) | [ CMS1157FHIRHIVRetention ](../../input/cql/CMS1157FHIRHIVRetention.cql) |
| [ CMS125FHIRBreastCancerScreen ](../../input/cql/CMS125FHIRBreastCancerScreen.cql) | [ CMS177FHIRChildMDDSuicideAssmt ](../../input/cql/CMS177FHIRChildMDDSuicideAssmt.cql) | [ CMS1173FHIRDiagnosticDelayVTE ](../../input/cql/CMS1173FHIRDiagnosticDelayVTE.cql) |
| [ CMS128FHIRAntidepressantMgmt ](../../input/cql/CMS128FHIRAntidepressantMgmt.cql) | [ CMS314FHIRHIVViralSuppression ](../../input/cql/CMS314FHIRHIVViralSuppression.cql) | [ CMS1188FHIRHIVSTITesting ](../../input/cql/CMS1188FHIRHIVSTITesting.cql) |
| [ CMS129FHIRProstCaBoneScanUse ](../../input/cql/CMS129FHIRProstCaBoneScanUse.cql) | [ CMS0334FHIRPCCesareanBirth ](../../input/cql/CMS0334FHIRPCCesareanBirth.cql) | [ CMS1206FHIRCTOQR ](../../input/cql/CMS1206FHIRCTOQR.cql) |
| [ CMS130FHIRColorectalCancerScrn ](../../input/cql/CMS130FHIRColorectalCancerScrn.cql) | [ CMS349FHIRHIVScreening ](../../input/cql/CMS349FHIRHIVScreening.cql) | [ CMS1218FHIRHHRF ](../../input/cql/CMS1218FHIRHHRF.cql) |
| [ CMS131FHIRDiabetesEyeExam ](../../input/cql/CMS131FHIRDiabetesEyeExam.cql) | [ CMS506FHIRSafeUseofOpioids ](../../input/cql/CMS506FHIRSafeUseofOpioids.cql) | [ CMS1244FHIRECATHOQR ](../../input/cql/CMS1244FHIRECATHOQR.cql) |
| [ CMS133FHIRCataracts2040BCVA90Days ](../../input/cql/CMS133FHIRCataracts2040BCVA90Days.cql) | [ CMSFHIR529HybridHospitalWideReadmission ](../../input/cql/CMSFHIR529HybridHospitalWideReadmission.cql) | [ CMS1264FHIRECATREHQR ](../../input/cql/CMS1264FHIRECATREHQR.cql) |
| [ CMS136FHIRChildADHDMedFollowUp ](../../input/cql/CMS136FHIRChildADHDMedFollowUp.cql) | [ CMS645FHIRBoneDensityPCADTherapy ](../../input/cql/CMS645FHIRBoneDensityPCADTherapy.cql) | [ NHSNAcuteCareHospitalMonthlyInitialPopulation1 ](../../input/cql/NHSNAcuteCareHospitalMonthlyInitialPopulation1.cql) |
| [ CMS137FHIRSUDTxInitEngagement ](../../input/cql/CMS137FHIRSUDTxInitEngagement.cql) | [ CMS771FHIRUrinarySymptomScoreBPH ](../../input/cql/CMS771FHIRUrinarySymptomScoreBPH.cql) | [ NHSNGlycemicControlHypoglycemiaInitialPopulation ](../../input/cql/NHSNGlycemicControlHypoglycemiaInitialPopulation.cql) |


## Measures with Discrepancies (14 of 74)

_Every measure with a test case that doesn't match its fixture MeasureReport, or that matches only because the CQL works around an open issue. The `Issue` column names the issue that explains a test case: `I-XX (implementation)` is the measure steward's test data or expectation (see `defect-tracking/known-issues.md`), and `I-XX (workaround reverted)` means the case is failing again. Any other `I-XX` is a known issue, and the `Ticketed` column beside it says whether a ticket is owed: `N/A` for an implementation issue or a defect in our own content, fixture, or harness (nothing an upstream ticket tracks), `pending` for an engine/translator defect whose ticket is not filed yet, and a link to it once one is. A test case nothing resolves is counted as Unattributed._

| Measure | Total Test Cases | Missing Results | Missing Populations | Mismatched Test Cases | Workarounds | Unattributed |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| [CMS68FHIRDocumentationCurrentMeds](#cms68fhirdocumentationcurrentmeds) | 19 | 0 | 0 | 0.00%   (0) | 1 | 0 |
| [CMS71FHIRSTKAnticoagAFFlutter](#cms71fhirstkanticoagafflutter) | 83 | 0 | 0 | 0.00%   (0) | 2 | 0 |
| [CMS72FHIRSTKAntithromboticDay2](#cms72fhirstkantithromboticday2) | 158 | 0 | 0 | 0.63%   (1) | 0 | 0 |
| [CMS108FHIRVTEProphylaxis](#cms108fhirvteprophylaxis) | 140 | 0 | 0 | 0.00%   (0) | 10 | 0 |
| [CMS135FHIRACEIorARBorARNIforHF](#cms135fhiraceiorarborarniforhf) | 40 | 3 | 0 | 0.00%   (0) | 0 | 0 |
| [CMS145FHIRCADBBlockerTPMIorLVSD](#cms145fhircadbblockertpmiorlvsd) | 106 | 0 | 0 | 0.94%   (1) | 10 | 0 |
| [CMS156FHIRHighRiskMedsElderly](#cms156fhirhighriskmedselderly) | 177 | 0 | 0 | 0.00%   (0) | 48 | 0 |
| [CMS165FHIRControllingHighBP](#cms165fhircontrollinghighbp) | 68 | 1 | 0 | 0.00%   (0) | 0 | 0 |
| [CMS190FHIRVTEProphylaxisICU](#cms190fhirvteprophylaxisicu) | 125 | 0 | 0 | 0.00%   (0) | 8 | 0 |
| [CMS347FHIRStatinPreventionTxCVD](#cms347fhirstatinpreventiontxcvd) | 752 | 0 | 0 | 0.13%   (1) | 0 | 0 |
| [CMS646FHIRIntravesicalBCGTherapy](#cms646fhirintravesicalbcgtherapy) | 38 | 1 | 0 | 7.89%   (3) | 0 | 0 |
| [CMSFHIR844HybridHospitalWideMortality](#cmsfhir844hybridhospitalwidemortality) | 10 | 0 | 0 | 20.00%   (2) | 0 | 0 |
| [CMS871FHIRHHHyper](#cms871fhirhhhyper) | 26 | 0 | 0 | 0.00%   (0) | 2 | 0 |
| [CMS996FHIRAptTxforSTEMI](#cms996fhirapttxforstemi) | 114 | 0 | 0 | 0.88%   (1) | 2 | 0 |



#### CMS68FHIRDocumentationCurrentMeds
[ [cql] ](../../input/cql/CMS68FHIRDocumentationCurrentMeds.cql) [ [test results] ](../../input/tests/results/CMS68FHIRDocumentationCurrentMeds.txt)

Workarounds (1 of 19 test cases)
_These cases match their fixture only because the measure's CQL works around an open issue. Removing the workaround makes them fail again, so they count as neither a pass nor a failure._
_ProcedureNotDone timing reads the us-quality-core-recorded extension via .ext() (CMS108, CMS190, CMS996) or a measure-local recordedProcedureNotDone() (CMS68), because .recorded() on a ProcedureNotDone does not resolve while the ambiguous recorded(ProcedureNotDone) overload stays commented out (I-18). Without the bypass the Numerator (CMS108, CMS190) or Denominator Exception (CMS68, CMS996) comes back empty._

| Test Case | Group | Issue | Ticketed |
| --- | --- | --- | --- |
| [ f2e2e1c0-9e35-4592-9579-72a236cb2f56 ](../.././input/tests/measure/CMS68FHIRDocumentationCurrentMeds/f2e2e1c0-9e35-4592-9579-72a236cb2f56/MeasureReport-7384d607-6a08-487a-9129-d90036bae37e.json) | Group_1 | I-55 (workaround applied) | [1855](https://github.com/cqframework/clinical_quality_language/issues/1855) |


Issues

- **I-55** (`migration`, **workaround applied**): ProcedureNotDone timing reads the us-quality-core-recorded extension via .ext() (CMS108, CMS190, CMS996) or a measure-local recordedProcedureNotDone() (CMS68), because .recorded() on a ProcedureNotDone does not resolve while the ambiguous recorded(ProcedureNotDone) overload stays commented out (I-18). Without the bypass the Numerator (CMS108, CMS190) or Denominator Exception (CMS68, CMS996) comes back empty.


#### CMS71FHIRSTKAnticoagAFFlutter
[ [cql] ](../../input/cql/CMS71FHIRSTKAnticoagAFFlutter.cql) [ [test results] ](../../input/tests/results/CMS71FHIRSTKAnticoagAFFlutter.txt)

Workarounds (2 of 83 test cases)
_These cases match their fixture only because the measure's CQL works around an open issue. Removing the workaround makes them fail again, so they count as neither a pass nor a failure._
_FHIRCommon prevalenceInterval() returns null for a non-active Condition with no abatement end. These cases evaluate correctly only because of the measure-local localPrevalenceInterval() workaround._

| Test Case | Group | Issue | Ticketed |
| --- | --- | --- | --- |
| [ 0587a75d-0dcc-4c6b-bfc0-f5727342ec1f ](../.././input/tests/measure/CMS71FHIRSTKAnticoagAFFlutter/0587a75d-0dcc-4c6b-bfc0-f5727342ec1f/MeasureReport-c8a99645-6e7a-467b-87aa-456cdc7cafb9.json) | Group_1 | I-31 (workaround applied) | [FHIR-59708](https://jira.hl7.org/browse/FHIR-59708) |
| [ 56ae006d-ab1b-428d-8614-2ccd5d962650 ](../.././input/tests/measure/CMS71FHIRSTKAnticoagAFFlutter/56ae006d-ab1b-428d-8614-2ccd5d962650/MeasureReport-71b26a14-7533-4479-82e3-7bc54d9ce0db.json) | Group_1 | I-31 (workaround applied) | [FHIR-59708](https://jira.hl7.org/browse/FHIR-59708) |


Issues

- **I-31** (`vendored`, **workaround applied**): FHIRCommon prevalenceInterval() returns null for a non-active Condition with no abatement end. These cases evaluate correctly only because of the measure-local localPrevalenceInterval() workaround.


#### CMS72FHIRSTKAntithromboticDay2
[ [cql] ](../../input/cql/CMS72FHIRSTKAntithromboticDay2.cql) [ [test results] ](../../input/tests/results/CMS72FHIRSTKAntithromboticDay2.txt)

Mismatched Test Cases (1 of 158)
| Test Case | Group | Population | Expected | Actual | Issue | Ticketed |
|---|---|---|:---:|:---:|---|---|
| [ be5c4068-2639-4b0c-bea3-5b7c80a6fe3b ](../.././input/tests/measure/CMS72FHIRSTKAntithromboticDay2/be5c4068-2639-4b0c-bea3-5b7c80a6fe3b/MeasureReport-ad329961-b67b-413b-a186-d6b269572c42.json) | Group_1 | Denominator Exception | 1 | 0 | I-75 (implementation) | N/A |


Issues

- **I-75** (`implementation`): PENDING SME CONFIRMATION. INR Observation valueQuantity has UCUM unit "0" and no code; UCUM reads "0" as a factor of zero, so INR 100 evaluates as 0 and the INR > 3.5 Denominator Exception can't fire. A dimensionless unit (unit/code "1") makes the case match.


#### CMS108FHIRVTEProphylaxis
[ [cql] ](../../input/cql/CMS108FHIRVTEProphylaxis.cql) [ [test results] ](../../input/tests/results/CMS108FHIRVTEProphylaxis.txt)

Workarounds (10 of 140 test cases)
_These cases match their fixture only because the measure's CQL works around an open issue. Removing the workaround makes them fail again, so they count as neither a pass nor a failure._
_ProcedureNotDone timing reads the us-quality-core-recorded extension via .ext() (CMS108, CMS190, CMS996) or a measure-local recordedProcedureNotDone() (CMS68), because .recorded() on a ProcedureNotDone does not resolve while the ambiguous recorded(ProcedureNotDone) overload stays commented out (I-18). Without the bypass the Numerator (CMS108, CMS190) or Denominator Exception (CMS68, CMS996) comes back empty._
_FHIRCommon prevalenceInterval() returns null for a non-active Condition with no abatement end. These cases evaluate correctly only because of the measure-local localPrevalenceInterval() workaround._

| Test Case | Group | Issue | Ticketed |
| --- | --- | --- | --- |
| [ 068814f1-4270-4e10-b470-9a5433bceb3e ](../.././input/tests/measure/CMS108FHIRVTEProphylaxis/068814f1-4270-4e10-b470-9a5433bceb3e/MeasureReport-22ae9d87-29d1-42c3-9908-93eff318d7b1.json) | Group_1 | I-55 (workaround applied) | [1855](https://github.com/cqframework/clinical_quality_language/issues/1855) |
| [ 33d162ce-3bc7-4b0a-8c04-fec0a42a6263 ](../.././input/tests/measure/CMS108FHIRVTEProphylaxis/33d162ce-3bc7-4b0a-8c04-fec0a42a6263/MeasureReport-da823951-b92e-4ee9-904f-839f7e8db8df.json) | Group_1 | I-31 (workaround applied) | [FHIR-59708](https://jira.hl7.org/browse/FHIR-59708) |
| [ 541ccffb-c1be-4c94-ab24-168d52e3a36b ](../.././input/tests/measure/CMS108FHIRVTEProphylaxis/541ccffb-c1be-4c94-ab24-168d52e3a36b/MeasureReport-4b90a8ef-2db7-4e28-aba4-d5404f17eb18.json) | Group_1 | I-55 (workaround applied) | [1855](https://github.com/cqframework/clinical_quality_language/issues/1855) |
| [ 575f2da0-c890-47a3-b17f-f9e134a1096e ](../.././input/tests/measure/CMS108FHIRVTEProphylaxis/575f2da0-c890-47a3-b17f-f9e134a1096e/MeasureReport-1f13d7d0-55ce-47e5-8a23-cb74963fc616.json) | Group_1 | I-55 (workaround applied) | [1855](https://github.com/cqframework/clinical_quality_language/issues/1855) |
| [ 8e2cfc29-0925-45b9-857f-b9ee9b9fa248 ](../.././input/tests/measure/CMS108FHIRVTEProphylaxis/8e2cfc29-0925-45b9-857f-b9ee9b9fa248/MeasureReport-b86669af-57ea-48d3-af7b-87c11d0e94b9.json) | Group_1 | I-55 (workaround applied) | [1855](https://github.com/cqframework/clinical_quality_language/issues/1855) |
| [ b7783b8c-ba46-4509-a75e-203659abab3d ](../.././input/tests/measure/CMS108FHIRVTEProphylaxis/b7783b8c-ba46-4509-a75e-203659abab3d/MeasureReport-097d962a-0304-47fe-9c77-8fd8bd4b48ac.json) | Group_1 | I-55 (workaround applied) | [1855](https://github.com/cqframework/clinical_quality_language/issues/1855) |
| [ ccd7f9d7-35e8-4623-9f2e-f229cf7d829c ](../.././input/tests/measure/CMS108FHIRVTEProphylaxis/ccd7f9d7-35e8-4623-9f2e-f229cf7d829c/MeasureReport-c8c8144b-3bac-4663-aac9-9a786e5c1810.json) | Group_1 | I-55 (workaround applied) | [1855](https://github.com/cqframework/clinical_quality_language/issues/1855) |
| [ d9b7ffa9-ed78-484c-8880-b4cbf2b4b6a1 ](../.././input/tests/measure/CMS108FHIRVTEProphylaxis/d9b7ffa9-ed78-484c-8880-b4cbf2b4b6a1/MeasureReport-43331d8f-cf2d-4a0c-a3a2-e4b8e060a7eb.json) | Group_1 | I-31 (workaround applied) | [FHIR-59708](https://jira.hl7.org/browse/FHIR-59708) |
| [ dba7c9af-eb6f-4836-ba24-650a5acc87e7 ](../.././input/tests/measure/CMS108FHIRVTEProphylaxis/dba7c9af-eb6f-4836-ba24-650a5acc87e7/MeasureReport-7c3e8a2e-61ff-4a73-b3e6-d6b168cb4cc6.json) | Group_1 | I-55 (workaround applied) | [1855](https://github.com/cqframework/clinical_quality_language/issues/1855) |
| [ dd5a1e46-1b99-45a3-b4d3-1fde205d8a11 ](../.././input/tests/measure/CMS108FHIRVTEProphylaxis/dd5a1e46-1b99-45a3-b4d3-1fde205d8a11/MeasureReport-bc945d90-f897-463b-bbc2-f9b922117784.json) | Group_1 | I-31 (workaround applied) | [FHIR-59708](https://jira.hl7.org/browse/FHIR-59708) |


Issues

- **I-31** (`vendored`, **workaround applied**): FHIRCommon prevalenceInterval() returns null for a non-active Condition with no abatement end. These cases evaluate correctly only because of the measure-local localPrevalenceInterval() workaround.
- **I-55** (`migration`, **workaround applied**): ProcedureNotDone timing reads the us-quality-core-recorded extension via .ext() (CMS108, CMS190, CMS996) or a measure-local recordedProcedureNotDone() (CMS68), because .recorded() on a ProcedureNotDone does not resolve while the ambiguous recorded(ProcedureNotDone) overload stays commented out (I-18). Without the bypass the Numerator (CMS108, CMS190) or Denominator Exception (CMS68, CMS996) comes back empty.


#### CMS135FHIRACEIorARBorARNIforHF
[ [cql] ](../../input/cql/CMS135FHIRACEIorARBorARNIforHF.cql) [ [test results] ](../../input/tests/results/CMS135FHIRACEIorARBorARNIforHF.txt)

Missing Results (3 of 40 test cases)
| Test Case | Group | Issue | Ticketed |
| --- | --- | --- | --- |
| [ c095195c-8893-4bf1-aa7d-ad2bfd9bafa5 ](../.././input/tests/measure/CMS135FHIRACEIorARBorARNIforHF/c095195c-8893-4bf1-aa7d-ad2bfd9bafa5/MeasureReport-f2d033da-6f32-46dc-86bc-69fdf82b1cfd.json) | Group_1 | I-26 | [1868](https://github.com/cqframework/clinical_quality_language/issues/1868) |
| [ cba5a449-1c45-4e11-ae0b-ba3974b410f7 ](../.././input/tests/measure/CMS135FHIRACEIorARBorARNIforHF/cba5a449-1c45-4e11-ae0b-ba3974b410f7/MeasureReport-ae8c4b99-af76-4577-b66d-b1230ac09aa3.json) | Group_1 | I-26 | [1868](https://github.com/cqframework/clinical_quality_language/issues/1868) |
| [ ec508dbb-76f6-4878-b8a2-114ea8e82297 ](../.././input/tests/measure/CMS135FHIRACEIorARBorARNIforHF/ec508dbb-76f6-4878-b8a2-114ea8e82297/MeasureReport-d1b704c8-7e95-4cd9-89e7-a8b90f925ce2.json) | Group_1 | I-26 | [1868](https://github.com/cqframework/clinical_quality_language/issues/1868) |


Issues

- **I-26** (`engine`, [cqframework/clinical_quality_language#1868](https://github.com/cqframework/clinical_quality_language/issues/1868)): MedicationRequest.medication is a Reference(Medication); the engine's code extraction throws before any define runs.


#### CMS145FHIRCADBBlockerTPMIorLVSD
[ [cql] ](../../input/cql/CMS145FHIRCADBBlockerTPMIorLVSD.cql) [ [test results] ](../../input/tests/results/CMS145FHIRCADBBlockerTPMIorLVSD.txt)

Mismatched Test Cases (1 of 106)
| Test Case | Group | Population | Expected | Actual | Issue | Ticketed |
|---|---|---|:---:|:---:|---|---|
| [ 1f70822b-c513-4c3a-8162-49f0bb9c914b ](../.././input/tests/measure/CMS145FHIRCADBBlockerTPMIorLVSD/1f70822b-c513-4c3a-8162-49f0bb9c914b/MeasureReport-9b3577fa-355c-409d-8d3f-21e9720fb889.json) | Group_2 | Denominator Exception | 0 | 1 | I-72 (implementation) | N/A |


Workarounds (10 of 106 test cases)
_These cases match their fixture only because the measure's CQL works around an open issue. Removing the workaround makes them fail again, so they count as neither a pass nor a failure._
_Beta-blocker allergy/intolerance diagnosis not counted as a Denominator Exception. The five cases fail against the original CQL and pass only because the workaround is applied._

| Test Case | Group | Issue | Ticketed |
| --- | --- | --- | --- |
| [ 4f4a65f4-a4c6-47e7-b37e-3ad9a9c9342e ](../.././input/tests/measure/CMS145FHIRCADBBlockerTPMIorLVSD/4f4a65f4-a4c6-47e7-b37e-3ad9a9c9342e/MeasureReport-e77c61ff-cc3a-402c-9752-7a97a6727a39.json) | Group_1 | I-78 (workaround applied) | [1872](https://github.com/cqframework/clinical_quality_language/issues/1872) |
| [ 4f4a65f4-a4c6-47e7-b37e-3ad9a9c9342e ](../.././input/tests/measure/CMS145FHIRCADBBlockerTPMIorLVSD/4f4a65f4-a4c6-47e7-b37e-3ad9a9c9342e/MeasureReport-e77c61ff-cc3a-402c-9752-7a97a6727a39.json) | Group_2 | I-78 (workaround applied) | [1872](https://github.com/cqframework/clinical_quality_language/issues/1872) |
| [ 5fd0d626-e9c5-4e6c-a10d-1a1183fa7702 ](../.././input/tests/measure/CMS145FHIRCADBBlockerTPMIorLVSD/5fd0d626-e9c5-4e6c-a10d-1a1183fa7702/MeasureReport-ce1b8712-b9dd-48e2-adf4-554ed641bee5.json) | Group_1 | I-78 (workaround applied) | [1872](https://github.com/cqframework/clinical_quality_language/issues/1872) |
| [ 5fd0d626-e9c5-4e6c-a10d-1a1183fa7702 ](../.././input/tests/measure/CMS145FHIRCADBBlockerTPMIorLVSD/5fd0d626-e9c5-4e6c-a10d-1a1183fa7702/MeasureReport-ce1b8712-b9dd-48e2-adf4-554ed641bee5.json) | Group_2 | I-78 (workaround applied) | [1872](https://github.com/cqframework/clinical_quality_language/issues/1872) |
| [ 61306767-0e74-44b8-ac06-1339c3783355 ](../.././input/tests/measure/CMS145FHIRCADBBlockerTPMIorLVSD/61306767-0e74-44b8-ac06-1339c3783355/MeasureReport-6ea40199-5a45-4c8d-8a2b-c08bf93ebd8a.json) | Group_1 | I-78 (workaround applied) | [1872](https://github.com/cqframework/clinical_quality_language/issues/1872) |
| [ 61306767-0e74-44b8-ac06-1339c3783355 ](../.././input/tests/measure/CMS145FHIRCADBBlockerTPMIorLVSD/61306767-0e74-44b8-ac06-1339c3783355/MeasureReport-6ea40199-5a45-4c8d-8a2b-c08bf93ebd8a.json) | Group_2 | I-78 (workaround applied) | [1872](https://github.com/cqframework/clinical_quality_language/issues/1872) |
| [ b65680a0-9768-4ce4-b08d-972fcd84e28e ](../.././input/tests/measure/CMS145FHIRCADBBlockerTPMIorLVSD/b65680a0-9768-4ce4-b08d-972fcd84e28e/MeasureReport-b5ebd0a9-a2de-4b31-b0d9-588888e95872.json) | Group_1 | I-78 (workaround applied) | [1872](https://github.com/cqframework/clinical_quality_language/issues/1872) |
| [ b65680a0-9768-4ce4-b08d-972fcd84e28e ](../.././input/tests/measure/CMS145FHIRCADBBlockerTPMIorLVSD/b65680a0-9768-4ce4-b08d-972fcd84e28e/MeasureReport-b5ebd0a9-a2de-4b31-b0d9-588888e95872.json) | Group_2 | I-78 (workaround applied) | [1872](https://github.com/cqframework/clinical_quality_language/issues/1872) |
| [ fd5fb311-a466-4c59-966d-48fa7aa88931 ](../.././input/tests/measure/CMS145FHIRCADBBlockerTPMIorLVSD/fd5fb311-a466-4c59-966d-48fa7aa88931/MeasureReport-05ffed3e-5604-40eb-bcf8-99cacecc26c0.json) | Group_1 | I-78 (workaround applied) | [1872](https://github.com/cqframework/clinical_quality_language/issues/1872) |
| [ fd5fb311-a466-4c59-966d-48fa7aa88931 ](../.././input/tests/measure/CMS145FHIRCADBBlockerTPMIorLVSD/fd5fb311-a466-4c59-966d-48fa7aa88931/MeasureReport-05ffed3e-5604-40eb-bcf8-99cacecc26c0.json) | Group_2 | I-78 (workaround applied) | [1872](https://github.com/cqframework/clinical_quality_language/issues/1872) |


Issues

- **I-72** (`implementation`): Test expects no Group_2 Denominator Exception because the patient-reason beta-blocker not-ordered falls on the first visit, but the CQL accepts the reason at any qualifying visit, and both visits qualify. Twin case b19af44d (reason at the last visit) expects 1. The steward must change the expectation or the CQL.
- **I-78** (`translator`, **workaround applied**): Beta-blocker allergy/intolerance diagnosis not counted as a Denominator Exception. The five cases fail against the original CQL and pass only because the workaround is applied.


#### CMS156FHIRHighRiskMedsElderly
[ [cql] ](../../input/cql/CMS156FHIRHighRiskMedsElderly.cql) [ [test results] ](../../input/tests/results/CMS156FHIRHighRiskMedsElderly.txt)

Workarounds (48 of 177 test cases)
_These cases match their fixture only because the measure's CQL works around an open issue. Removing the workaround makes them fail again, so they count as neither a pass nor a failure._
_"Values FHIR.dateTime and FHIR.dateTime are not comparable" aborts the case. The FHIRHelpers.ToDateTime() workaround is applied to CMS156 only._
_Worked around in CMS156 averageDailyDose(); listed for its upstream ticket._

| Test Case | Group | Issue | Ticketed |
| --- | --- | --- | --- |
| [ 1789d80d-bc5b-4e15-ab64-399d05e55a19 ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/1789d80d-bc5b-4e15-ab64-399d05e55a19/MeasureReport-c5842144-5823-4fe2-93dc-a7cc368968fe.json) | Group_1 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ 1789d80d-bc5b-4e15-ab64-399d05e55a19 ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/1789d80d-bc5b-4e15-ab64-399d05e55a19/MeasureReport-c5842144-5823-4fe2-93dc-a7cc368968fe.json) | Group_2 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ 1789d80d-bc5b-4e15-ab64-399d05e55a19 ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/1789d80d-bc5b-4e15-ab64-399d05e55a19/MeasureReport-c5842144-5823-4fe2-93dc-a7cc368968fe.json) | Group_3 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ 2389a7bb-16a7-4800-ba4a-2585ebd98a0a ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/2389a7bb-16a7-4800-ba4a-2585ebd98a0a/MeasureReport-5d66494f-0140-46ae-9010-59ed11eae359.json) | Group_1 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ 2389a7bb-16a7-4800-ba4a-2585ebd98a0a ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/2389a7bb-16a7-4800-ba4a-2585ebd98a0a/MeasureReport-5d66494f-0140-46ae-9010-59ed11eae359.json) | Group_2 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ 2389a7bb-16a7-4800-ba4a-2585ebd98a0a ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/2389a7bb-16a7-4800-ba4a-2585ebd98a0a/MeasureReport-5d66494f-0140-46ae-9010-59ed11eae359.json) | Group_3 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ 42125b07-9cb2-44df-ba1f-78237b0d3ebc ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/42125b07-9cb2-44df-ba1f-78237b0d3ebc/MeasureReport-218cb83f-e1c9-45de-a46b-caa45ab68688.json) | Group_1 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ 42125b07-9cb2-44df-ba1f-78237b0d3ebc ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/42125b07-9cb2-44df-ba1f-78237b0d3ebc/MeasureReport-218cb83f-e1c9-45de-a46b-caa45ab68688.json) | Group_2 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ 42125b07-9cb2-44df-ba1f-78237b0d3ebc ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/42125b07-9cb2-44df-ba1f-78237b0d3ebc/MeasureReport-218cb83f-e1c9-45de-a46b-caa45ab68688.json) | Group_3 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ 4aa75d19-ac8b-49b0-a686-429fbc033d77 ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/4aa75d19-ac8b-49b0-a686-429fbc033d77/MeasureReport-139cc56e-5ffb-46ca-89ce-accd0bb642ab.json) | Group_1 | I-24 (workaround applied) | [1690](https://github.com/cqframework/clinical_quality_language/issues/1690) |
| [ 4aa75d19-ac8b-49b0-a686-429fbc033d77 ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/4aa75d19-ac8b-49b0-a686-429fbc033d77/MeasureReport-139cc56e-5ffb-46ca-89ce-accd0bb642ab.json) | Group_2 | I-24 (workaround applied) | [1690](https://github.com/cqframework/clinical_quality_language/issues/1690) |
| [ 4aa75d19-ac8b-49b0-a686-429fbc033d77 ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/4aa75d19-ac8b-49b0-a686-429fbc033d77/MeasureReport-139cc56e-5ffb-46ca-89ce-accd0bb642ab.json) | Group_3 | I-24 (workaround applied) | [1690](https://github.com/cqframework/clinical_quality_language/issues/1690) |
| [ 5326ef57-57d6-49b8-bdc5-b3179cdcb82d ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/5326ef57-57d6-49b8-bdc5-b3179cdcb82d/MeasureReport-13d2c78d-9ea8-43cb-976a-07636ad51575.json) | Group_1 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ 5326ef57-57d6-49b8-bdc5-b3179cdcb82d ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/5326ef57-57d6-49b8-bdc5-b3179cdcb82d/MeasureReport-13d2c78d-9ea8-43cb-976a-07636ad51575.json) | Group_2 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ 5326ef57-57d6-49b8-bdc5-b3179cdcb82d ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/5326ef57-57d6-49b8-bdc5-b3179cdcb82d/MeasureReport-13d2c78d-9ea8-43cb-976a-07636ad51575.json) | Group_3 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ 5c33755f-40d8-4409-b699-a3499ddddda0 ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/5c33755f-40d8-4409-b699-a3499ddddda0/MeasureReport-a8c9543e-2148-48f9-bd4a-0f5ab6ff7b57.json) | Group_1 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ 5c33755f-40d8-4409-b699-a3499ddddda0 ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/5c33755f-40d8-4409-b699-a3499ddddda0/MeasureReport-a8c9543e-2148-48f9-bd4a-0f5ab6ff7b57.json) | Group_2 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ 5c33755f-40d8-4409-b699-a3499ddddda0 ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/5c33755f-40d8-4409-b699-a3499ddddda0/MeasureReport-a8c9543e-2148-48f9-bd4a-0f5ab6ff7b57.json) | Group_3 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ 64c49012-0f98-41da-a00b-9cd673294d16 ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/64c49012-0f98-41da-a00b-9cd673294d16/MeasureReport-99a65a2b-e608-4f67-918d-ea3f8ceb03f2.json) | Group_1 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ 64c49012-0f98-41da-a00b-9cd673294d16 ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/64c49012-0f98-41da-a00b-9cd673294d16/MeasureReport-99a65a2b-e608-4f67-918d-ea3f8ceb03f2.json) | Group_2 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ 64c49012-0f98-41da-a00b-9cd673294d16 ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/64c49012-0f98-41da-a00b-9cd673294d16/MeasureReport-99a65a2b-e608-4f67-918d-ea3f8ceb03f2.json) | Group_3 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ 68ccf96b-cdd0-4bd7-b0d5-9ed33ec895ca ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/68ccf96b-cdd0-4bd7-b0d5-9ed33ec895ca/MeasureReport-e1513040-9d4e-4b28-9f9d-e6cd97c8e6ec.json) | Group_1 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ 68ccf96b-cdd0-4bd7-b0d5-9ed33ec895ca ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/68ccf96b-cdd0-4bd7-b0d5-9ed33ec895ca/MeasureReport-e1513040-9d4e-4b28-9f9d-e6cd97c8e6ec.json) | Group_2 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ 68ccf96b-cdd0-4bd7-b0d5-9ed33ec895ca ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/68ccf96b-cdd0-4bd7-b0d5-9ed33ec895ca/MeasureReport-e1513040-9d4e-4b28-9f9d-e6cd97c8e6ec.json) | Group_3 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ 7f204655-dbf6-47d7-a684-ff1570cf4b05 ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/7f204655-dbf6-47d7-a684-ff1570cf4b05/MeasureReport-e3454afe-2c47-48c4-8cfa-8a71eb842a52.json) | Group_1 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ 7f204655-dbf6-47d7-a684-ff1570cf4b05 ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/7f204655-dbf6-47d7-a684-ff1570cf4b05/MeasureReport-e3454afe-2c47-48c4-8cfa-8a71eb842a52.json) | Group_2 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ 7f204655-dbf6-47d7-a684-ff1570cf4b05 ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/7f204655-dbf6-47d7-a684-ff1570cf4b05/MeasureReport-e3454afe-2c47-48c4-8cfa-8a71eb842a52.json) | Group_3 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ 8e648527-5b7e-430c-b5ca-fe70a4133d55 ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/8e648527-5b7e-430c-b5ca-fe70a4133d55/MeasureReport-0dcd49bb-3eb9-41be-b9ec-2d4cbb9469fb.json) | Group_1 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ 8e648527-5b7e-430c-b5ca-fe70a4133d55 ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/8e648527-5b7e-430c-b5ca-fe70a4133d55/MeasureReport-0dcd49bb-3eb9-41be-b9ec-2d4cbb9469fb.json) | Group_2 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ 8e648527-5b7e-430c-b5ca-fe70a4133d55 ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/8e648527-5b7e-430c-b5ca-fe70a4133d55/MeasureReport-0dcd49bb-3eb9-41be-b9ec-2d4cbb9469fb.json) | Group_3 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ a550fe5a-03ad-4eb3-9157-dcb64f8b13be ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/a550fe5a-03ad-4eb3-9157-dcb64f8b13be/MeasureReport-1ae70be3-8690-4902-aca5-e8048a6c2de1.json) | Group_1 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ a550fe5a-03ad-4eb3-9157-dcb64f8b13be ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/a550fe5a-03ad-4eb3-9157-dcb64f8b13be/MeasureReport-1ae70be3-8690-4902-aca5-e8048a6c2de1.json) | Group_2 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ a550fe5a-03ad-4eb3-9157-dcb64f8b13be ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/a550fe5a-03ad-4eb3-9157-dcb64f8b13be/MeasureReport-1ae70be3-8690-4902-aca5-e8048a6c2de1.json) | Group_3 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ a6b1d740-d580-4e55-970e-3cb4f1e369c2 ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/a6b1d740-d580-4e55-970e-3cb4f1e369c2/MeasureReport-12fa7bd7-0c1d-4437-8622-2a219942b2e1.json) | Group_1 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ a6b1d740-d580-4e55-970e-3cb4f1e369c2 ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/a6b1d740-d580-4e55-970e-3cb4f1e369c2/MeasureReport-12fa7bd7-0c1d-4437-8622-2a219942b2e1.json) | Group_2 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ a6b1d740-d580-4e55-970e-3cb4f1e369c2 ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/a6b1d740-d580-4e55-970e-3cb4f1e369c2/MeasureReport-12fa7bd7-0c1d-4437-8622-2a219942b2e1.json) | Group_3 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ aeef1eb1-86fa-4af0-b24d-fc7ad8398191 ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/aeef1eb1-86fa-4af0-b24d-fc7ad8398191/MeasureReport-28a51e65-13c2-4fde-b103-93fcb80f0903.json) | Group_1 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ aeef1eb1-86fa-4af0-b24d-fc7ad8398191 ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/aeef1eb1-86fa-4af0-b24d-fc7ad8398191/MeasureReport-28a51e65-13c2-4fde-b103-93fcb80f0903.json) | Group_2 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ aeef1eb1-86fa-4af0-b24d-fc7ad8398191 ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/aeef1eb1-86fa-4af0-b24d-fc7ad8398191/MeasureReport-28a51e65-13c2-4fde-b103-93fcb80f0903.json) | Group_3 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ cb01ddd0-a804-4bbe-8544-d4c753898eca ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/cb01ddd0-a804-4bbe-8544-d4c753898eca/MeasureReport-2efd499c-6b01-4fa8-b4e1-80c5e09571f8.json) | Group_1 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ cb01ddd0-a804-4bbe-8544-d4c753898eca ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/cb01ddd0-a804-4bbe-8544-d4c753898eca/MeasureReport-2efd499c-6b01-4fa8-b4e1-80c5e09571f8.json) | Group_2 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ cb01ddd0-a804-4bbe-8544-d4c753898eca ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/cb01ddd0-a804-4bbe-8544-d4c753898eca/MeasureReport-2efd499c-6b01-4fa8-b4e1-80c5e09571f8.json) | Group_3 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ e00d1066-19b2-4d59-8829-d90f1e7a1233 ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/e00d1066-19b2-4d59-8829-d90f1e7a1233/MeasureReport-5b50ece9-6516-40c2-9c49-d261d06b80d5.json) | Group_1 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ e00d1066-19b2-4d59-8829-d90f1e7a1233 ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/e00d1066-19b2-4d59-8829-d90f1e7a1233/MeasureReport-5b50ece9-6516-40c2-9c49-d261d06b80d5.json) | Group_2 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ e00d1066-19b2-4d59-8829-d90f1e7a1233 ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/e00d1066-19b2-4d59-8829-d90f1e7a1233/MeasureReport-5b50ece9-6516-40c2-9c49-d261d06b80d5.json) | Group_3 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ ea9af1dc-c26e-4bc3-947b-6c4bbd65523c ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/ea9af1dc-c26e-4bc3-947b-6c4bbd65523c/MeasureReport-95607d58-bfa1-43fb-8fe9-8a0e479b8885.json) | Group_1 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ ea9af1dc-c26e-4bc3-947b-6c4bbd65523c ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/ea9af1dc-c26e-4bc3-947b-6c4bbd65523c/MeasureReport-95607d58-bfa1-43fb-8fe9-8a0e479b8885.json) | Group_2 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |
| [ ea9af1dc-c26e-4bc3-947b-6c4bbd65523c ](../.././input/tests/measure/CMS156FHIRHighRiskMedsElderly/ea9af1dc-c26e-4bc3-947b-6c4bbd65523c/MeasureReport-95607d58-bfa1-43fb-8fe9-8a0e479b8885.json) | Group_3 | I-33 (workaround applied) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |


Issues

- **I-24** (`engine`, **workaround applied**): Worked around in CMS156 averageDailyDose(); listed for its upstream ticket.
- **I-33** (`engine`, **workaround applied**): "Values FHIR.dateTime and FHIR.dateTime are not comparable" aborts the case. The FHIRHelpers.ToDateTime() workaround is applied to CMS156 only.


#### CMS165FHIRControllingHighBP
[ [cql] ](../../input/cql/CMS165FHIRControllingHighBP.cql) [ [test results] ](../../input/tests/results/CMS165FHIRControllingHighBP.txt)

Missing Results (1 of 68 test cases)
| Test Case | Group | Issue | Ticketed |
| --- | --- | --- | --- |
| [ 45e01fed-56bb-483d-a860-af3d566bda11 ](../.././input/tests/measure/CMS165FHIRControllingHighBP/45e01fed-56bb-483d-a860-af3d566bda11/MeasureReport-02991ca7-859d-422d-8849-655760f8e10a.json) | Group_1 | I-26 | [1868](https://github.com/cqframework/clinical_quality_language/issues/1868) |


Issues

- **I-26** (`engine`, [cqframework/clinical_quality_language#1868](https://github.com/cqframework/clinical_quality_language/issues/1868)): MedicationRequest.medication is a Reference(Medication); the engine's code extraction throws before any define runs.


#### CMS190FHIRVTEProphylaxisICU
[ [cql] ](../../input/cql/CMS190FHIRVTEProphylaxisICU.cql) [ [test results] ](../../input/tests/results/CMS190FHIRVTEProphylaxisICU.txt)

Workarounds (8 of 125 test cases)
_These cases match their fixture only because the measure's CQL works around an open issue. Removing the workaround makes them fail again, so they count as neither a pass nor a failure._
_ProcedureNotDone timing reads the us-quality-core-recorded extension via .ext() (CMS108, CMS190, CMS996) or a measure-local recordedProcedureNotDone() (CMS68), because .recorded() on a ProcedureNotDone does not resolve while the ambiguous recorded(ProcedureNotDone) overload stays commented out (I-18). Without the bypass the Numerator (CMS108, CMS190) or Denominator Exception (CMS68, CMS996) comes back empty._

| Test Case | Group | Issue | Ticketed |
| --- | --- | --- | --- |
| [ 4c32b73b-abba-431b-a352-f0f454e7c9dd ](../.././input/tests/measure/CMS190FHIRVTEProphylaxisICU/4c32b73b-abba-431b-a352-f0f454e7c9dd/MeasureReport-e9ac894c-9f4c-47d8-8325-7750b25036e0.json) | Group_1 | I-55 (workaround applied) | [1855](https://github.com/cqframework/clinical_quality_language/issues/1855) |
| [ 4fc421c7-e490-4d4e-a326-53d08635efb9 ](../.././input/tests/measure/CMS190FHIRVTEProphylaxisICU/4fc421c7-e490-4d4e-a326-53d08635efb9/MeasureReport-c206bcec-44ba-493e-8114-8ae57bf6b7e6.json) | Group_1 | I-55 (workaround applied) | [1855](https://github.com/cqframework/clinical_quality_language/issues/1855) |
| [ 632831b0-1ebf-47b5-b439-3a124cd77c37 ](../.././input/tests/measure/CMS190FHIRVTEProphylaxisICU/632831b0-1ebf-47b5-b439-3a124cd77c37/MeasureReport-dff9d9bd-b0cc-400f-815b-9255b426e828.json) | Group_1 | I-55 (workaround applied) | [1855](https://github.com/cqframework/clinical_quality_language/issues/1855) |
| [ 9ddea16c-55d3-4dda-a1d8-a256fbff0b64 ](../.././input/tests/measure/CMS190FHIRVTEProphylaxisICU/9ddea16c-55d3-4dda-a1d8-a256fbff0b64/MeasureReport-90c1518e-8e3a-4f2a-b266-9210baffdcbf.json) | Group_1 | I-55 (workaround applied) | [1855](https://github.com/cqframework/clinical_quality_language/issues/1855) |
| [ a9c75661-be1c-41b2-aa15-222cc7d2ca81 ](../.././input/tests/measure/CMS190FHIRVTEProphylaxisICU/a9c75661-be1c-41b2-aa15-222cc7d2ca81/MeasureReport-21816bad-859d-416f-883b-24246a1db64c.json) | Group_1 | I-55 (workaround applied) | [1855](https://github.com/cqframework/clinical_quality_language/issues/1855) |
| [ e8931859-4ad8-49c8-9cdd-8697293456a2 ](../.././input/tests/measure/CMS190FHIRVTEProphylaxisICU/e8931859-4ad8-49c8-9cdd-8697293456a2/MeasureReport-cfc06289-ff74-4caa-ba81-3647f98e3646.json) | Group_1 | I-55 (workaround applied) | [1855](https://github.com/cqframework/clinical_quality_language/issues/1855) |
| [ f82746cf-f6cd-4fcc-bc9e-7e569ae26211 ](../.././input/tests/measure/CMS190FHIRVTEProphylaxisICU/f82746cf-f6cd-4fcc-bc9e-7e569ae26211/MeasureReport-ecd1d81f-c8df-4d19-b85f-5bb0d5c9f771.json) | Group_1 | I-55 (workaround applied) | [1855](https://github.com/cqframework/clinical_quality_language/issues/1855) |
| [ f859dd94-f201-4517-a368-32b98dd486c9 ](../.././input/tests/measure/CMS190FHIRVTEProphylaxisICU/f859dd94-f201-4517-a368-32b98dd486c9/MeasureReport-da236e59-3d0a-46c4-a352-3eec5846dbe6.json) | Group_1 | I-55 (workaround applied) | [1855](https://github.com/cqframework/clinical_quality_language/issues/1855) |


Issues

- **I-55** (`migration`, **workaround applied**): ProcedureNotDone timing reads the us-quality-core-recorded extension via .ext() (CMS108, CMS190, CMS996) or a measure-local recordedProcedureNotDone() (CMS68), because .recorded() on a ProcedureNotDone does not resolve while the ambiguous recorded(ProcedureNotDone) overload stays commented out (I-18). Without the bypass the Numerator (CMS108, CMS190) or Denominator Exception (CMS68, CMS996) comes back empty.


#### CMS347FHIRStatinPreventionTxCVD
[ [cql] ](../../input/cql/CMS347FHIRStatinPreventionTxCVD.cql) [ [test results] ](../../input/tests/results/CMS347FHIRStatinPreventionTxCVD.txt)

Mismatched Test Cases (1 of 752)
| Test Case | Group | Population | Expected | Actual | Issue | Ticketed |
|---|---|---|:---:|:---:|---|---|
| [ 1ba7b147-b701-424c-bade-4e8270547030 ](../.././input/tests/measure/CMS347FHIRStatinPreventionTxCVD/1ba7b147-b701-424c-bade-4e8270547030/MeasureReport-2278c703-994b-4b13-8e3b-c726ba6b8530.json) | Group_4 | Denominator Exception | 0 | 1 | I-67 (implementation) | N/A |


Issues

- **I-67** (`implementation`): ESRD Condition uses a start-only abatementPeriod to mean resolved 2025-12-31; the steward should use abatementDateTime or add an end.


#### CMS646FHIRIntravesicalBCGTherapy
[ [cql] ](../../input/cql/CMS646FHIRIntravesicalBCGTherapy.cql) [ [test results] ](../../input/tests/results/CMS646FHIRIntravesicalBCGTherapy.txt)

Missing Results (1 of 38 test cases)
| Test Case | Group | Issue | Ticketed |
| --- | --- | --- | --- |
| [ 342d2bec-0acc-43e5-aaf7-3c9a65b09f91 ](../.././input/tests/measure/CMS646FHIRIntravesicalBCGTherapy/342d2bec-0acc-43e5-aaf7-3c9a65b09f91/MeasureReport-12cd358b-deb0-4130-a045-4c6b61e110c0.json) | Group_1 | I-33 (workaround reverted) | [1878](https://github.com/cqframework/clinical_quality_language/issues/1878) |


Mismatched Test Cases (3 of 38)
| Test Case | Group | Population | Expected | Actual | Issue | Ticketed |
|---|---|---|:---:|:---:|---|---|
| [ 10cec7db-41ae-49ad-b883-022f19d92a8b ](../.././input/tests/measure/CMS646FHIRIntravesicalBCGTherapy/10cec7db-41ae-49ad-b883-022f19d92a8b/MeasureReport-b8b4961d-450b-4980-ac8f-95500c6393d4.json) | Group_1 | Denominator Exclusion | 0 | 1 | I-15 (implementation) | N/A |
| [ 6e9a1974-7334-4c41-b8dd-8413ae0caa29 ](../.././input/tests/measure/CMS646FHIRIntravesicalBCGTherapy/6e9a1974-7334-4c41-b8dd-8413ae0caa29/MeasureReport-82d2900a-e69c-4b3c-a6f9-c173759b3f1d.json) | Group_1 | Numerator | 0 | 1 | I-70 (implementation) | N/A |
| [ ab48e0c0-6543-4537-8f00-bfcdcba7a81b ](../.././input/tests/measure/CMS646FHIRIntravesicalBCGTherapy/ab48e0c0-6543-4537-8f00-bfcdcba7a81b/MeasureReport-ea6cfef5-54d2-4d6d-a7aa-48cf8e749eaf.json) | Group_1 | Numerator | 0 | 1 | I-70 (implementation) | N/A |


Issues

- **I-15** (`implementation`): Fixture MeasureReport expects a value the resources present can't produce.
- **I-33** (`engine`, **workaround applied**): "Values FHIR.dateTime and FHIR.dateTime are not comparable" aborts the case. The FHIRHelpers.ToDateTime() workaround is applied to CMS156 only.
- **I-70** (`implementation`): Test expects Numerator 0 because BCG was given before staging results came back, but the CQL measures from the start of the staging Procedure and the BCG dose starts at the same moment (2026-04-02T08:00 in ab48e0c0, 2026-04-06T08:00 in 6e9a1974), so neither case can fail the Numerator.


#### CMSFHIR844HybridHospitalWideMortality
[ [cql] ](../../input/cql/CMSFHIR844HybridHospitalWideMortality.cql) [ [test results] ](../../input/tests/results/CMSFHIR844HybridHospitalWideMortality.txt)

Mismatched Test Cases (2 of 10)
| Test Case | Group | Population | Expected | Actual | Issue | Ticketed |
|---|---|---|:---:|:---:|---|---|
| [ 6f22a06f-7186-4db1-9310-4f907dc49ff3 ](../.././input/tests/measure/CMSFHIR844HybridHospitalWideMortality/6f22a06f-7186-4db1-9310-4f907dc49ff3/MeasureReport-a02a261f-1274-4f8b-b1f3-5496f7885cbe.json) | Group_1 | Initial Population | 1 | 0 | I-14 (implementation) | N/A |
| [ af1b9448-3e7a-4b7f-8934-15bb63258b75 ](../.././input/tests/measure/CMSFHIR844HybridHospitalWideMortality/af1b9448-3e7a-4b7f-8934-15bb63258b75/MeasureReport-7afefb0f-3075-4fb8-8d56-474ba1112c38.json) | Group_1 | Initial Population | 2 | 1 | I-14 (implementation) | N/A |


Issues

- **I-14** (`implementation`): Fixture MeasureReport hand-authors the Initial Population; the test data supports the computed value.


#### CMS871FHIRHHHyper
[ [cql] ](../../input/cql/CMS871FHIRHHHyper.cql) [ [test results] ](../../input/tests/results/CMS871FHIRHHHyper.txt)

Workarounds (2 of 26 test cases)
_These cases match their fixture only because the measure's CQL works around an open issue. Removing the workaround makes them fail again, so they count as neither a pass nor a failure._
_Both cases fail with the original FHIRCommon functions and evaluate only because the workaround is applied. Upstream tickets: FHIR-59691, FHIR-59689._

| Test Case | Group | Issue | Ticketed |
| --- | --- | --- | --- |
| [ 98533ccd-24ee-41b3-aab2-ef6cbf89e00d ](../.././input/tests/measure/CMS871FHIRHHHyper/98533ccd-24ee-41b3-aab2-ef6cbf89e00d/MeasureReport-82c8805c-b129-4009-8533-1ed12cf5d18f.json) | Group_1 | I-63 (workaround applied) | [FHIR-59691](https://jira.hl7.org/browse/FHIR-59691) |
| [ fd579f44-757b-4c98-9b09-27b17b935650 ](../.././input/tests/measure/CMS871FHIRHHHyper/fd579f44-757b-4c98-9b09-27b17b935650/MeasureReport-22df2e2a-404d-4ab0-831a-e2ab043197a2.json) | Group_1 | I-63 (workaround applied) | [FHIR-59691](https://jira.hl7.org/browse/FHIR-59691) |


Issues

- **I-63** (`vendored`, **workaround applied**): Both cases fail with the original FHIRCommon functions and evaluate only because the workaround is applied. Upstream tickets: FHIR-59691, FHIR-59689.


#### CMS996FHIRAptTxforSTEMI
[ [cql] ](../../input/cql/CMS996FHIRAptTxforSTEMI.cql) [ [test results] ](../../input/tests/results/CMS996FHIRAptTxforSTEMI.txt)

Mismatched Test Cases (1 of 114)
| Test Case | Group | Population | Expected | Actual | Issue | Ticketed |
|---|---|---|:---:|:---:|---|---|
| [ f6c7dbc1-9ca7-46cd-bcbe-29d8fae4e847 ](../.././input/tests/measure/CMS996FHIRAptTxforSTEMI/f6c7dbc1-9ca7-46cd-bcbe-29d8fae4e847/MeasureReport-f2a63299-25e1-4d91-8e5c-1bdf3b60e9cb.json) | Group_1 | Denominator Exclusion | 0 | 1 | I-71 (implementation) | N/A |


Workarounds (2 of 114 test cases)
_These cases match their fixture only because the measure's CQL works around an open issue. Removing the workaround makes them fail again, so they count as neither a pass nor a failure._
_ProcedureNotDone timing reads the us-quality-core-recorded extension via .ext() (CMS108, CMS190, CMS996) or a measure-local recordedProcedureNotDone() (CMS68), because .recorded() on a ProcedureNotDone does not resolve while the ambiguous recorded(ProcedureNotDone) overload stays commented out (I-18). Without the bypass the Numerator (CMS108, CMS190) or Denominator Exception (CMS68, CMS996) comes back empty._

| Test Case | Group | Issue | Ticketed |
| --- | --- | --- | --- |
| [ 7edab122-3af3-4172-9231-7c1470ecc1e0 ](../.././input/tests/measure/CMS996FHIRAptTxforSTEMI/7edab122-3af3-4172-9231-7c1470ecc1e0/MeasureReport-9d0666d5-6e19-4f7f-b284-1af640b254f3.json) | Group_1 | I-55 (workaround applied) | [1855](https://github.com/cqframework/clinical_quality_language/issues/1855) |
| [ ccc7deaf-98b7-4dad-b190-8fee10f2cf77 ](../.././input/tests/measure/CMS996FHIRAptTxforSTEMI/ccc7deaf-98b7-4dad-b190-8fee10f2cf77/MeasureReport-9d6a333f-3243-42df-9063-031aa80e74ff.json) | Group_1 | I-55 (workaround applied) | [1855](https://github.com/cqframework/clinical_quality_language/issues/1855) |


Issues

- **I-55** (`migration`, **workaround applied**): ProcedureNotDone timing reads the us-quality-core-recorded extension via .ext() (CMS108, CMS190, CMS996) or a measure-local recordedProcedureNotDone() (CMS68), because .recorded() on a ProcedureNotDone does not resolve while the ambiguous recorded(ProcedureNotDone) overload stays commented out (I-18). Without the bypass the Numerator (CMS108, CMS190) or Denominator Exception (CMS68, CMS996) comes back empty.
- **I-71** (`implementation`): Active thrombolytic allergy uses onsetPeriod.end to mean it ended before the ED visit; with no abatement, prevalenceInterval() correctly runs to end of time and overlaps the encounter. The steward should mark it resolved with an allergyintolerance-abatement extension, or expect Denominator Exclusion 1.



_Known issues are listed in `defect-tracking/known-issues.md`; the test cases they explain, and their tickets, in `./scripts/comparison/known_issues.csv` and `./scripts/comparison/implementation_issues.csv`._
