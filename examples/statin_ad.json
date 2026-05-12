{
  "meta": {
    "title": "Statins and Alzheimer's Disease",
    "network": "TriNetX US Collaborative Network",
    "date": "July 2025",
    "author": "Novak et al."
  },
  "nodes": [
    {
      "id": "n_source",
      "kind": "source",
      "label": "TriNetX US Collaborative Network",
      "body": "July 2025",
      "n": 131075626,
      "position": "center"
    },
    {
      "id": "n_age",
      "kind": "inclusion",
      "label": "Age > 45",
      "body": "",
      "n": 67255316,
      "position": "center"
    },
    {
      "id": "n_excl",
      "kind": "exclusion_panel",
      "label": "Exclusion Criteria: AD Comorbidities",
      "body": "Parkinson's Disease (G20): (n=511,070)\nOther systemic atrophy primarily affecting CNS (G13.1): (n=3,168)\nUnspecified dementia (F03): (n=1,305,148)\nUnspecified psychosis (F29): (n=667,319)\nEpilepsy and recurrent seizures (G40): (n=1,811,352)\nNicotine Dependence (F17): (n=8,409,900)\nAlcohol related disorders (F10): (n=3,120,532)\nPersonal history of nicotine dependence (Z87.891): (n=6,960,111)\nSleep Disorders (G47): (n=10,194,859)\nCerebral Infarction (I63): (n=2,012,158)\nHeart disease (I51): (n=3,560,023)\nVascular Dementia (F01): (n=279,841)\nCerebrovascular diseases (I60-I69): (n=4,881,403)\nType 2 Diabetes Mellitus (E11): (n=9,743,432)\nHbA1c \u2265 7%: (n=19,652,261)\nHypothyroidism, unspecified (E03.9): (n=5,650,192)\nPrion and other viral diseases (A80-A89): (n=80,554)\nHerpes Simplex Infections (B00): (n=1,220,530)\nVaricella Zoster Glycoprotein (RxNorm: 1986821): (n=2,103,331)\nLate syphilis (A52): (n=48,583)\nAutoimmune thyroiditis (E06.3): (n=616,762)\nDown syndrome (Q90): (n=104,003)\nDonepezil (RxNorm: 135447): (n=747,534)\nRivastigmine (RxNorm: 183379): (n=112,255)\nGalantamine (RxNorm: 4637): (n=30,531)\nMemantine (RxNorm: 6719): (n=497,728)\nLecanemab (RxNorm: 2626143): (n=1,098)",
      "position": "right"
    },
    {
      "id": "n_pool",
      "kind": "pool",
      "label": "Total pool meeting inclusion criteria",
      "body": "Control Group Event:\nDisorders of lipoprotein metabolism (E78)\n(n=19,321,802)\n\nStatin Event:\nDisorders of lipoprotein metabolism (E78)\n(n=19,321,802) and a statin (n=13,559,028)",
      "position": "center"
    },
    {
      "id": "n_index",
      "kind": "index_event",
      "label": "Analysis Time Frame Relative to Index Event",
      "body": "One day following diagnosis of Disorders of lipoprotein metabolism (E78) and statin prescription",
      "position": "center"
    },
    {
      "id": "n_pre_ctrl",
      "kind": "cohort_pre_psm",
      "label": "Total meeting inclusion criteria for Control Group",
      "n": 2092006,
      "position": "left"
    },
    {
      "id": "n_psm",
      "kind": "psm",
      "label": "Propensity Score Matching (PSM) Characteristics:",
      "body": "- Age at Index\n- Male\n- Female\n- White\n- Black/African-American\n- Hispanic/Latino\n- Asian\n- Hypertensive Diseases (I10-I1A)\n- Chronic ischemic heart disease (I25)\n- BMI\n- Triglyceride\n- LDL Cholesterol labs\n- Beta blockers/related\n- Diuretics\n- Antiarrhythmics\n- ACE inhibitors\n- Calcium channel blockers\n- Angiotensin II inhibitor",
      "position": "center"
    },
    {
      "id": "n_pre_stat",
      "kind": "cohort_pre_psm",
      "label": "Total meeting inclusion criteria for Statin Group",
      "n": 991987,
      "position": "right"
    },
    {
      "id": "n_exposure",
      "kind": "exposure_panel",
      "label": "Received at least one of the following at any dosage:",
      "body": "Atorvastatin (RxNorm: 83367): (n=9,839,782)\nSimvastatin (RxNorm: 36567): (n=3,117,048)\nRosuvastatin (RxNorm: 381542): (n=3,538,535)\nPravastatin (RxNorm: 42463): (n=1,964,663)\nLovastatin (RxNorm: 6472): (n=439,209)\nPitavastatin (RxNorm: 861634): (n=73,101)\nFluvastatin (RxNorm: 41127): (n=31,664)",
      "position": "right"
    },
    {
      "id": "n_post_ctrl",
      "kind": "cohort_post_psm",
      "label": "Control Group After PSM",
      "n": 838217,
      "position": "left"
    },
    {
      "id": "n_post_stat",
      "kind": "cohort_post_psm",
      "label": "Statin Group After PSM",
      "n": 838217,
      "position": "right"
    },
    {
      "id": "n_outcome",
      "kind": "outcome",
      "label": "Outcome: Alzheimer's Disease (G30)",
      "n": 594379,
      "position": "center"
    },
    {
      "id": "n_term_ctrl",
      "kind": "terminal",
      "label": "No Statin Group",
      "body": "Total: 836,540\nAD: 1,035 (0.12%)",
      "position": "left"
    },
    {
      "id": "n_term_stat",
      "kind": "terminal",
      "label": "Statin Group",
      "body": "Total: 837,405\nAD Diagnosis: 710 (0.08%)",
      "position": "right"
    }
  ],
  "edges": [
    {"id": "e1", "from_id": "n_source", "to_id": "n_age", "style": "solid"},
    {"id": "e2", "from_id": "n_age", "to_id": "n_pool", "style": "solid"},
    {"id": "e3", "from_id": "n_excl", "to_id": "n_age", "style": "dashed"},
    {"id": "e4", "from_id": "n_pool", "to_id": "n_index", "style": "solid"},
    {"id": "e5", "from_id": "n_index", "to_id": "n_pre_ctrl", "style": "solid"},
    {"id": "e6", "from_id": "n_index", "to_id": "n_pre_stat", "style": "solid"},
    {"id": "e7", "from_id": "n_pre_ctrl", "to_id": "n_psm", "style": "solid"},
    {"id": "e8", "from_id": "n_pre_stat", "to_id": "n_psm", "style": "solid"},
    {"id": "e9", "from_id": "n_psm", "to_id": "n_post_ctrl", "style": "solid"},
    {"id": "e10", "from_id": "n_psm", "to_id": "n_post_stat", "style": "solid"},
    {"id": "e10b", "from_id": "n_exposure", "to_id": "n_pre_stat", "style": "dashed"},
    {"id": "e11", "from_id": "n_post_ctrl", "to_id": "n_outcome", "style": "solid"},
    {"id": "e12", "from_id": "n_post_stat", "to_id": "n_outcome", "style": "solid"},
    {"id": "e13", "from_id": "n_outcome", "to_id": "n_term_ctrl", "style": "solid"},
    {"id": "e14", "from_id": "n_outcome", "to_id": "n_term_stat", "style": "solid"}
  ]
}
