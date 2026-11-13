# Discrepancy Report
| Details | Value |
| --- | --- |
| Generated | 2026-11-13 16:52:07.855655 |
| Total Measures | 74 |
| Total Test Cases | 3964 |
| Measures with Discrepancies | 12 |
| Pass Count | 3922 (98.94%) |
| Workaround Count | 28 (0.71%) |
| &nbsp;&nbsp;— covered by a ticketed known issue | 28 (0.71%) |
| Implementation Issue Count | 5 (0.13%) |
| Known Issue Count (ticketed) | 5 (0.13%) |
| Fail Count | 4 (0.10%) |
| &nbsp;&nbsp;— known issue, no ticket expected | 4 (0.10%) |
| Known issues with an upstream ticket | 33 (0.83%) |
| Resolved (Pass + Implementation + Known Issue) | 3932 (99.19%) |


| Discrepancy Summary | Measure Count | Test Case Count |
|---|:---:|:---:|
| Missing Results | 3 | 5 |
| Missing Populations | 0 | 0 |
| Mismatched Test Cases | 6 | 9 |
| Workarounds | 5 | 65 |
| Unattributed Discrepancies | 2 | 4 |



_Note: Measures can have multiple discrepancies, so the Measures with Discrepancies count may not match the summary counts. Unattributed Discrepancies are those no implementation issue or ticketed known issue resolves. Workarounds are test cases that match their fixture only because the CQL works around an open issue: they count as neither a pass nor a failure, and the workaround is removed once the root cause is fixed._

## Populations Excluded from Automated Scoring (CQFM Aggregation)

_These populations require invoking a parameterized CQL `measure-observation` function once per member of a `cqfm-criteriaReference` population and then applying `cqfm-aggregateMethod` (Sum/Count/Average) -- a computation this harness's CQL-execution path cannot perform (no scriptable/batch CQL runner; see `defect-tracking/known-issues.md`, I-62). They are intentionally excluded from pass/fail scoring rather than reported as FAIL or silently read as 0. Every other population on these measures (Initial Population, Denominator, Numerator, exclusions, etc.) is unaffected and scored normally. Use the `mcp-cql-debug` per-member probe method documented in I-62 to manually verify any of the expected values below._

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


## Measures with No Discrepancies (62 of 74)

|  |  |  |
| --- | --- | --- |
| [ CMS2FHIRPCSDepScreenAndFollowUp ](../../input/cql/CMS2FHIRPCSDepScreenAndFollowUp.cql) | [ CMS138FHIRTobaccoScrnCessation ](../../input/cql/CMS138FHIRTobaccoScrnCessation.cql) | [ CMS816FHIRHHHypo ](../../input/cql/CMS816FHIRHHHypo.cql) |
| [ CMS22FHIRPCSBPScreeningFollowUp ](../../input/cql/CMS22FHIRPCSBPScreeningFollowUp.cql) | [ CMS139FHIRFallRiskScreening ](../../input/cql/CMS139FHIRFallRiskScreening.cql) | [ CMS819FHIRHHORAE ](../../input/cql/CMS819FHIRHHORAE.cql) |
| [ CMS50FHIRReceiptofSpecialistReport ](../../input/cql/CMS50FHIRReceiptofSpecialistReport.cql) | [ CMS142FHIRCommWithDrManagingDiab ](../../input/cql/CMS142FHIRCommWithDrManagingDiab.cql) | [ CMS826FHIRHHPI ](../../input/cql/CMS826FHIRHHPI.cql) |
| [ CMS56FHIRFuncStatHipReplacement ](../../input/cql/CMS56FHIRFuncStatHipReplacement.cql) | [ CMS143FHIRPOAGOpticNerveEval ](../../input/cql/CMS143FHIRPOAGOpticNerveEval.cql) | [ CMS832FHIRHHAKI ](../../input/cql/CMS832FHIRHHAKI.cql) |
| [ CMS68FHIRDocumentationCurrentMeds ](../../input/cql/CMS68FHIRDocumentationCurrentMeds.cql) | [ CMS144FHIRHFBetaBlockerForLVSD ](../../input/cql/CMS144FHIRHFBetaBlockerForLVSD.cql) | [ CMS951FHIRKidneyHealthEval ](../../input/cql/CMS951FHIRKidneyHealthEval.cql) |
| [ CMS69FHIRPCSBMIScreenAndFollowUp ](../../input/cql/CMS69FHIRPCSBMIScreenAndFollowUp.cql) | [ CMS146FHIRApproTestPharyngitis ](../../input/cql/CMS146FHIRApproTestPharyngitis.cql) | [ CMS986FHIRMalnutritionScore ](../../input/cql/CMS986FHIRMalnutritionScore.cql) |
| [ CMS74FHIRDentalCariesPrevention ](../../input/cql/CMS74FHIRDentalCariesPrevention.cql) | [ CMS149FHIRDementiaCognitiveAssess ](../../input/cql/CMS149FHIRDementiaCognitiveAssess.cql) | [ CMS1017FHIRHHFI ](../../input/cql/CMS1017FHIRHHFI.cql) |
| [ CMS75FHIRChildrenDentalDecay ](../../input/cql/CMS75FHIRChildrenDentalDecay.cql) | [ CMS153FHIRChlamydiaScreening ](../../input/cql/CMS153FHIRChlamydiaScreening.cql) | [ CMS1028FHIRPCSevereOBComps ](../../input/cql/CMS1028FHIRPCSevereOBComps.cql) |
| [ CMS90FHIRFSAforHeartFailure ](../../input/cql/CMS90FHIRFSAforHeartFailure.cql) | [ CMS154FHIRAppropriateTxforURI ](../../input/cql/CMS154FHIRAppropriateTxforURI.cql) | [ CMS1056FHIRCTClinical ](../../input/cql/CMS1056FHIRCTClinical.cql) |
| [ CMS104FHIRSTKDCAntithrombotic ](../../input/cql/CMS104FHIRSTKDCAntithrombotic.cql) | [ CMS155FHIRWgtAssessCounseling ](../../input/cql/CMS155FHIRWgtAssessCounseling.cql) | [ CMS1074FHIRCTIQR ](../../input/cql/CMS1074FHIRCTIQR.cql) |
| [ CMS117FHIRChildImmunStatus ](../../input/cql/CMS117FHIRChildImmunStatus.cql) | [ CMS157FHIRPainIntensityQuantified ](../../input/cql/CMS157FHIRPainIntensityQuantified.cql) | [ CMS1154ScreeningPrediabetesFHIR ](../../input/cql/CMS1154ScreeningPrediabetesFHIR.cql) |
| [ CMS122FHIRDiabetesAssessGT9Pct ](../../input/cql/CMS122FHIRDiabetesAssessGT9Pct.cql) | [ CMS159FHIRDepRemissionat12Months ](../../input/cql/CMS159FHIRDepRemissionat12Months.cql) | [ CMS1157FHIRHIVRetention ](../../input/cql/CMS1157FHIRHIVRetention.cql) |
| [ CMS124FHIRCervicalCancerScreen ](../../input/cql/CMS124FHIRCervicalCancerScreen.cql) | [ CMS177FHIRChildMDDSuicideAssmt ](../../input/cql/CMS177FHIRChildMDDSuicideAssmt.cql) | [ CMS1173FHIRDiagnosticDelayVTE ](../../input/cql/CMS1173FHIRDiagnosticDelayVTE.cql) |
| [ CMS125FHIRBreastCancerScreen ](../../input/cql/CMS125FHIRBreastCancerScreen.cql) | [ CMS190FHIRVTEProphylaxisICU ](../../input/cql/CMS190FHIRVTEProphylaxisICU.cql) | [ CMS1188FHIRHIVSTITesting ](../../input/cql/CMS1188FHIRHIVSTITesting.cql) |
| [ CMS128FHIRAntidepressantMgmt ](../../input/cql/CMS128FHIRAntidepressantMgmt.cql) | [ CMS314FHIRHIVViralSuppression ](../../input/cql/CMS314FHIRHIVViralSuppression.cql) | [ CMS1206FHIRCTOQR ](../../input/cql/CMS1206FHIRCTOQR.cql) |
| [ CMS129FHIRProstCaBoneScanUse ](../../input/cql/CMS129FHIRProstCaBoneScanUse.cql) | [ CMS0334FHIRPCCesareanBirth ](../../input/cql/CMS0334FHIRPCCesareanBirth.cql) | [ CMS1218FHIRHHRF ](../../input/cql/CMS1218FHIRHHRF.cql) |
| [ CMS130FHIRColorectalCancerScrn ](../../input/cql/CMS130FHIRColorectalCancerScrn.cql) | [ CMS349FHIRHIVScreening ](../../input/cql/CMS349FHIRHIVScreening.cql) | [ CMS1244FHIRECATHOQR ](../../input/cql/CMS1244FHIRECATHOQR.cql) |
| [ CMS131FHIRDiabetesEyeExam ](../../input/cql/CMS131FHIRDiabetesEyeExam.cql) | [ CMS506FHIRSafeUseofOpioids ](../../input/cql/CMS506FHIRSafeUseofOpioids.cql) | [ CMS1264FHIRECATREHQR ](../../input/cql/CMS1264FHIRECATREHQR.cql) |
| [ CMS133FHIRCataracts2040BCVA90Days ](../../input/cql/CMS133FHIRCataracts2040BCVA90Days.cql) | [ CMSFHIR529HybridHospitalWideReadmission ](../../input/cql/CMSFHIR529HybridHospitalWideReadmission.cql) | [ NHSNAcuteCareHospitalMonthlyInitialPopulation1 ](../../input/cql/NHSNAcuteCareHospitalMonthlyInitialPopulation1.cql) |
| [ CMS136FHIRChildADHDMedFollowUp ](../../input/cql/CMS136FHIRChildADHDMedFollowUp.cql) | [ CMS645FHIRBoneDensityPCADTherapy ](../../input/cql/CMS645FHIRBoneDensityPCADTherapy.cql) | [ NHSNGlycemicControlHypoglycemiaInitialPopulation ](../../input/cql/NHSNGlycemicControlHypoglycemiaInitialPopulation.cql) |
| [ CMS137FHIRSUDTxInitEngagement ](../../input/cql/CMS137FHIRSUDTxInitEngagement.cql) | [ CMS771FHIRUrinarySymptomScoreBPH ](../../input/cql/CMS771FHIRUrinarySymptomScoreBPH.cql) |  |


## Measures with Discrepancies (12 of 74)

_Every measure with a test case that doesn't match its fixture MeasureReport, or that matches only because the CQL works around an open issue. The `Issue` column names the issue that explains a test case: `I-XX (implementation)` is the measure steward's test data or expectation (see `defect-tracking/known-issues.md`), and `I-XX (workaround reverted)` means the case is failing again. Any other `I-XX` is a known issue, and the `Ticketed` column beside it says whether a ticket is owed: `N/A` for an implementation issue or a defect in our own content, fixture, or harness (nothing an upstream ticket tracks), `pending` for an engine/translator defect whose ticket is not filed yet, and a link to it once one is. A test case nothing resolves is counted as Unattributed._

| Measure | Total Test Cases | Missing Results | Missing Populations | Mismatched Test Cases | Workarounds | Unattributed |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| [CMS71FHIRSTKAnticoagAFFlutter](#cms71fhirstkanticoagafflutter) | 83 | 0 | 0 | 0.00%   (0) | 2 | 0 |
| [CMS72FHIRSTKAntithromboticDay2](#cms72fhirstkantithromboticday2) | 158 | 0 | 0 | 0.63%   (1) | 0 | 0 |
| [CMS108FHIRVTEProphylaxis](#cms108fhirvteprophylaxis) | 140 | 0 | 0 | 0.00%   (0) | 3 | 0 |
| [CMS135FHIRACEIorARBorARNIforHF](#cms135fhiraceiorarborarniforhf) | 40 | 3 | 0 | 0.00%   (0) | 0 | 0 |
| [CMS145FHIRCADBBlockerTPMIorLVSD](#cms145fhircadbblockertpmiorlvsd) | 106 | 0 | 0 | 0.94%   (1) | 10 | 0 |
| [CMS156FHIRHighRiskMedsElderly](#cms156fhirhighriskmedselderly) | 177 | 0 | 0 | 0.00%   (0) | 48 | 0 |
| [CMS165FHIRControllingHighBP](#cms165fhircontrollinghighbp) | 68 | 1 | 0 | 0.00%   (0) | 0 | 0 |
| [CMS347FHIRStatinPreventionTxCVD](#cms347fhirstatinpreventiontxcvd) | 752 | 0 | 0 | 0.13%   (1) | 0 | 0 |
| [CMS646FHIRIntravesicalBCGTherapy](#cms646fhirintravesicalbcgtherapy) | 38 | 1 | 0 | 7.89%   (3) | 0 | 2 |
| [CMSFHIR844HybridHospitalWideMortality](#cmsfhir844hybridhospitalwidemortality) | 10 | 0 | 0 | 20.00%   (2) | 0 | 2 |
| [CMS871FHIRHHHyper](#cms871fhirhhhyper) | 26 | 0 | 0 | 0.00%   (0) | 2 | 0 |
| [CMS996FHIRAptTxforSTEMI](#cms996fhirapttxforstemi) | 114 | 0 | 0 | 0.88%   (1) | 0 | 0 |



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

Workarounds (3 of 140 test cases)
_These cases match their fixture only because the measure's CQL works around an open issue. Removing the workaround makes them fail again, so they count as neither a pass nor a failure._
_FHIRCommon prevalenceInterval() returns null for a non-active Condition with no abatement end. These cases evaluate correctly only because of the measure-local localPrevalenceInterval() workaround._

| Test Case | Group | Issue | Ticketed |
| --- | --- | --- | --- |
| [ 33d162ce-3bc7-4b0a-8c04-fec0a42a6263 ](../.././input/tests/measure/CMS108FHIRVTEProphylaxis/33d162ce-3bc7-4b0a-8c04-fec0a42a6263/MeasureReport-da823951-b92e-4ee9-904f-839f7e8db8df.json) | Group_1 | I-31 (workaround applied) | [FHIR-59708](https://jira.hl7.org/browse/FHIR-59708) |
| [ d9b7ffa9-ed78-484c-8880-b4cbf2b4b6a1 ](../.././input/tests/measure/CMS108FHIRVTEProphylaxis/d9b7ffa9-ed78-484c-8880-b4cbf2b4b6a1/MeasureReport-43331d8f-cf2d-4a0c-a3a2-e4b8e060a7eb.json) | Group_1 | I-31 (workaround applied) | [FHIR-59708](https://jira.hl7.org/browse/FHIR-59708) |
| [ dd5a1e46-1b99-45a3-b4d3-1fde205d8a11 ](../.././input/tests/measure/CMS108FHIRVTEProphylaxis/dd5a1e46-1b99-45a3-b4d3-1fde205d8a11/MeasureReport-bc945d90-f897-463b-bbc2-f9b922117784.json) | Group_1 | I-31 (workaround applied) | [FHIR-59708](https://jira.hl7.org/browse/FHIR-59708) |


Issues

- **I-31** (`vendored`, **workaround applied**): FHIRCommon prevalenceInterval() returns null for a non-active Condition with no abatement end. These cases evaluate correctly only because of the measure-local localPrevalenceInterval() workaround.


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
| [ 10cec7db-41ae-49ad-b883-022f19d92a8b ](../.././input/tests/measure/CMS646FHIRIntravesicalBCGTherapy/10cec7db-41ae-49ad-b883-022f19d92a8b/MeasureReport-b8b4961d-450b-4980-ac8f-95500c6393d4.json) | Group_1 | Denominator Exclusion | 0 | 1 | I-15 | N/A |
| [ 6e9a1974-7334-4c41-b8dd-8413ae0caa29 ](../.././input/tests/measure/CMS646FHIRIntravesicalBCGTherapy/6e9a1974-7334-4c41-b8dd-8413ae0caa29/MeasureReport-82d2900a-e69c-4b3c-a6f9-c173759b3f1d.json) | Group_1 | Numerator | 0 | 1 | I-79 | N/A |
| [ ab48e0c0-6543-4537-8f00-bfcdcba7a81b ](../.././input/tests/measure/CMS646FHIRIntravesicalBCGTherapy/ab48e0c0-6543-4537-8f00-bfcdcba7a81b/MeasureReport-ea6cfef5-54d2-4d6d-a7aa-48cf8e749eaf.json) | Group_1 | Numerator | 0 | 1 | I-70 (implementation) | N/A |


Issues

- **I-15** (`content`): Fixture MeasureReport expects a value the resources present can't produce.
- **I-33** (`engine`, **workaround applied**): "Values FHIR.dateTime and FHIR.dateTime are not comparable" aborts the case. The FHIRHelpers.ToDateTime() workaround is applied to CMS156 only.
- **I-70** (`implementation`): Test expects Numerator 0 because BCG was given before staging results came back, but the CQL measures from the start of the staging Procedure and the BCG dose starts at the same moment (2026-04-02T08:00), so the case can't fail the Numerator.
- **I-79** (`content`): Correcting the wrong-patient reference (I-11 sweep) made the BCG administration visible to the measure, and the CQL counts it: an in-progress BCG recorded at the same instant as the staging procedure satisfies the measure's "6 months or less after day of staging" rule, while the test case is written to expect no BCG counted. Open question is whether the CQL rule, the fixture timestamps, or the expected value is wrong — the case itself says the BCG "should fail".


#### CMSFHIR844HybridHospitalWideMortality
[ [cql] ](../../input/cql/CMSFHIR844HybridHospitalWideMortality.cql) [ [test results] ](../../input/tests/results/CMSFHIR844HybridHospitalWideMortality.txt)

Mismatched Test Cases (2 of 10)
| Test Case | Group | Population | Expected | Actual | Issue | Ticketed |
|---|---|---|:---:|:---:|---|---|
| [ 6f22a06f-7186-4db1-9310-4f907dc49ff3 ](../.././input/tests/measure/CMSFHIR844HybridHospitalWideMortality/6f22a06f-7186-4db1-9310-4f907dc49ff3/MeasureReport-a02a261f-1274-4f8b-b1f3-5496f7885cbe.json) | Group_1 | Initial Population | 1 | 0 | I-14 | N/A |
| [ af1b9448-3e7a-4b7f-8934-15bb63258b75 ](../.././input/tests/measure/CMSFHIR844HybridHospitalWideMortality/af1b9448-3e7a-4b7f-8934-15bb63258b75/MeasureReport-7afefb0f-3075-4fb8-8d56-474ba1112c38.json) | Group_1 | Initial Population | 2 | 1 | I-14 | N/A |


Issues

- **I-14** (`content`): Fixture MeasureReport hand-authors the Initial Population; the test data supports the computed value.


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


Issues

- **I-71** (`implementation`): Active thrombolytic allergy uses onsetPeriod.end to mean it ended before the ED visit; with no abatement, prevalenceInterval() correctly runs to end of time and overlaps the encounter. The steward should mark it resolved with an allergyintolerance-abatement extension, or expect Denominator Exclusion 1.



_Known issues are listed in `defect-tracking/known-issues.md`; the test cases they explain, and their tickets, in `./scripts/comparison/known_issues.csv` and `./scripts/comparison/implementation_issues.csv`._
