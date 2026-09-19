/*
NOTE: For use by March 2026 US Realm Connectathon participants for internal use only. Not for use or distribution in commercial products.
*/
library CMS133FHIRCataracts2040BCVA90Days version '1.1.000'

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

valueset "Acute and Subacute Iridocyclitis": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1241'
valueset "Amblyopia": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1448'
valueset "Best Corrected Visual Acuity Exam Using Snellen Chart": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1560'
valueset "Burn Confined to Eye and Adnexa": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1409'
valueset "Cataract Congenital": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1412'
valueset "Cataract Mature or Hypermature": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1413'
valueset "Cataract Posterior Polar": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1414'
valueset "Cataract Secondary to Ocular Disorders": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1410'
valueset "Cataract Surgery": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1411'
valueset "Central Corneal Ulcer": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1428'
valueset "Certain Types of Iridocyclitis": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1415'
valueset "Choroidal Degenerations": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1450'
valueset "Choroidal Detachment": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1451'
valueset "Choroidal Hemorrhage and Rupture": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1452'
valueset "Chronic Iridocyclitis": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1416'
valueset "Cloudy Cornea": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1417'
valueset "Corneal Edema": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1418'
valueset "Degeneration of Macula and Posterior Pole": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1453'
valueset "Degenerative Disorders of Globe": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1454'
valueset "Diabetic Macular Edema": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1455'
valueset "Diabetic Retinopathy": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.327'
valueset "Disorders of Cornea Including Corneal Opacity": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1419'
valueset "Disorders of Optic Chiasm": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1457'
valueset "Disorders of Visual Cortex": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1458'
valueset "Disseminated Chorioretinitis and Disseminated Retinochoroiditis": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1459'
valueset "Focal Chorioretinitis and Focal Retinochoroiditis": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1460'
valueset "Glaucoma": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1423'
valueset "Glaucoma Associated with Congenital Anomalies and Dystrophies and Systemic Syndromes": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1461'
valueset "Hereditary Choroidal Dystrophies": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1462'
valueset "Hereditary Corneal Dystrophies": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1424'
valueset "Hereditary Retinal Dystrophies": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1463'
valueset "Hypotony of Eye": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1426'
valueset "Injury to Optic Nerve and Pathways": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1427'
valueset "Macular Scar of Posterior Polar": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1559'
valueset "Morgagnian Cataract": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1558'
valueset "Nystagmus and Other Irregular Eye Movements": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1465'
valueset "Open Wound of Eyeball": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1430'
valueset "Optic Atrophy": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1466'
valueset "Optic Neuritis": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1467'
valueset "Other and Unspecified Forms of Chorioretinitis and Retinochoroiditis": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1468'
valueset "Other Background Retinopathy and Retinal Vascular Changes": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1469'
valueset "Other Disorders of Optic Nerve": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1471'
valueset "Other Endophthalmitis": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1473'
valueset "Other Proliferative Retinopathy": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1480'
valueset "Pathologic Myopia": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1432'
valueset "Posterior Lenticonus": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1433'
valueset "Prior Penetrating Keratoplasty": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1475'
valueset "Purulent Endophthalmitis": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1477'
valueset "Retinal Detachment with Retinal Defect": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1478'
valueset "Retinal Vascular Occlusion": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1479'
valueset "Retrolental Fibroplasias": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1438'
valueset "Scleritis": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113762.1.4.1226.1'
valueset "Separation of Retinal Layers": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1482'
valueset "Traumatic Cataract": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1443'
valueset "Uveitis": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1444'
valueset "Vascular Disorders of Iris and Ciliary Body": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1445'
valueset "Visual Acuity 20/40 or Better": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1483'
valueset "Visual Field Defects": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.526.3.1446'

code "Best corrected visual acuity (observable entity)": '419775003' from "SNOMEDCT" display 'Best corrected visual acuity (observable entity)'

parameter "Measurement Period" Interval<DateTime>
  default Interval[@2026-01-01T00:00:00.000Z, @2027-01-01T00:00:00.000Z)

context Patient

define "Denominator":
  "Initial Population"

define "Initial Population":
  "Cataract Surgery Between January and September of Measurement Period" CataractSurgeryPerformed
    where AgeInYearsAt(date from start of "Measurement Period") >= 18

define "Cataract Surgery Between January and September of Measurement Period":
  [Procedure: "Cataract Surgery"] CataractSurgery
    where CataractSurgery.performed.toInterval ( ) during day of "Measurement Period"
      and CataractSurgery.performed.toInterval ( ) starts 92 days or more before day of end of "Measurement Period"
      and CataractSurgery.status = 'completed'

define "Denominator Exclusions":
  "Cataract Surgeries in Patients with Significant Ocular Conditions Impacting the Visual Outcome of Surgery"

define "Cataract Surgeries in Patients with Significant Ocular Conditions Impacting the Visual Outcome of Surgery":
  "Cataract Surgery Between January and September of Measurement Period" CataractSurgeryPerformed
    with (
      // [I-28] base FHIR.Condition retrieves (defect-tracking/known-issues.md)
      // Original: 55 x ( ["ConditionProblemsHealthConcerns": X] union ["ConditionEncounterDiagnosis": X] ) pairs — replaced with base FHIR.Condition retrieves
      [FHIR.Condition: "Acute and Subacute Iridocyclitis"]
        union [FHIR.Condition: "Amblyopia"]
        union [FHIR.Condition: "Burn Confined to Eye and Adnexa"]
        union [FHIR.Condition: "Cataract Secondary to Ocular Disorders"]
        union [FHIR.Condition: "Cataract Congenital"]
        union [FHIR.Condition: "Cataract Mature or Hypermature"]
        union [FHIR.Condition: "Cataract Posterior Polar"]
        union [FHIR.Condition: "Central Corneal Ulcer"]
        union [FHIR.Condition: "Certain Types of Iridocyclitis"]
        union [FHIR.Condition: "Choroidal Degenerations"]
        union [FHIR.Condition: "Choroidal Detachment"]
        union [FHIR.Condition: "Choroidal Hemorrhage and Rupture"]
        union [FHIR.Condition: "Chronic Iridocyclitis"]
        union [FHIR.Condition: "Cloudy Cornea"]
        union [FHIR.Condition: "Corneal Edema"]
        union [FHIR.Condition: "Disorders of Cornea Including Corneal Opacity"]
        union [FHIR.Condition: "Degeneration of Macula and Posterior Pole"]
        union [FHIR.Condition: "Degenerative Disorders of Globe"]
        union [FHIR.Condition: "Diabetic Macular Edema"]
        union [FHIR.Condition: "Diabetic Retinopathy"]
        union [FHIR.Condition: "Disorders of Optic Chiasm"]
        union [FHIR.Condition: "Disorders of Visual Cortex"]
        union [FHIR.Condition: "Disseminated Chorioretinitis and Disseminated Retinochoroiditis"]
        union [FHIR.Condition: "Focal Chorioretinitis and Focal Retinochoroiditis"]
        union [FHIR.Condition: "Glaucoma"]
        union [FHIR.Condition: "Glaucoma Associated with Congenital Anomalies and Dystrophies and Systemic Syndromes"]
        union [FHIR.Condition: "Hereditary Choroidal Dystrophies"]
        union [FHIR.Condition: "Hereditary Corneal Dystrophies"]
        union [FHIR.Condition: "Hereditary Retinal Dystrophies"]
        union [FHIR.Condition: "Hypotony of Eye"]
        union [FHIR.Condition: "Injury to Optic Nerve and Pathways"]
        union [FHIR.Condition: "Macular Scar of Posterior Polar"]
        union [FHIR.Condition: "Morgagnian Cataract"]
        union [FHIR.Condition: "Nystagmus and Other Irregular Eye Movements"]
        union [FHIR.Condition: "Open Wound of Eyeball"]
        union [FHIR.Condition: "Optic Atrophy"]
        union [FHIR.Condition: "Optic Neuritis"]
        union [FHIR.Condition: "Other and Unspecified Forms of Chorioretinitis and Retinochoroiditis"]
        union [FHIR.Condition: "Other Background Retinopathy and Retinal Vascular Changes"]
        union [FHIR.Condition: "Other Disorders of Optic Nerve"]
        union [FHIR.Condition: "Other Endophthalmitis"]
        union [FHIR.Condition: "Other Proliferative Retinopathy"]
        union [FHIR.Condition: "Pathologic Myopia"]
        union [FHIR.Condition: "Posterior Lenticonus"]
        union [FHIR.Condition: "Prior Penetrating Keratoplasty"]
        union [FHIR.Condition: "Purulent Endophthalmitis"]
        union [FHIR.Condition: "Retinal Detachment with Retinal Defect"]
        union [FHIR.Condition: "Retinal Vascular Occlusion"]
        union [FHIR.Condition: "Retrolental Fibroplasias"]
        union [FHIR.Condition: "Scleritis"]
        union [FHIR.Condition: "Separation of Retinal Layers"]
        union [FHIR.Condition: "Traumatic Cataract"]
        union [FHIR.Condition: "Uveitis"]
        union [FHIR.Condition: "Vascular Disorders of Iris and Ciliary Body"]
        union [FHIR.Condition: "Visual Field Defects"]
    ) ComorbidDiagnosis
      such that ComorbidDiagnosis.prevalenceInterval ( ) overlaps before day of CataractSurgeryPerformed.performed.toInterval ( )
        and ComorbidDiagnosis.isVerified ( )

define "Numerator":
  "Cataract Surgery Between January and September of Measurement Period" CataractSurgeryPerformed
    with ( [ObservationClinicalResult: "Best corrected visual acuity (observable entity)"]
      union [ObservationClinicalResult: "Best Corrected Visual Acuity Exam Using Snellen Chart"] ) VisualAcuityExamPerformed
      such that VisualAcuityExamPerformed.effective.toInterval ( ) 90 days or less after day of end of CataractSurgeryPerformed.performed.toInterval ( )
        and VisualAcuityExamPerformed.status in { 'final', 'amended', 'corrected' }
        and VisualAcuityExamPerformed.value as CodeableConcept in "Visual Acuity 20/40 or Better"
        
/*
@description: Returns true if the given Condition has a verification status of "confirmed", "unconfirmed", "provisional", or "differential"
*/


define fluent function isVerified(condition Choice<ConditionEncounterDiagnosis, ConditionProblemsHealthConcerns>):
  condition.verificationStatus is not null implies ( condition.verificationStatus ~ Status."confirmed"
      or condition.verificationStatus ~ Status."unconfirmed"
      or condition.verificationStatus ~ Status."provisional"
      or condition.verificationStatus ~ Status."differential"
  )

define "SDE Ethnicity":
  SDE."SDE Ethnicity"

define "SDE Payer":
  SDE."SDE Payer"

define "SDE Race":
  SDE."SDE Race"

define "SDE Sex":
  SDE."SDE Sex"