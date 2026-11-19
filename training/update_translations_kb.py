"""Script to populate Groundnut translations in translations.json across all 5 languages."""

from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TRANSLATIONS_JSON = PROJECT_ROOT / "disease_data" / "translations.json"

GROUNDNUT_TRANSLATIONS = {
    "en": {
        "early_leaf_spot": {
            "display_name": "Early Leaf Spot of Groundnut (Tikka Disease)",
            "scientific_name": "Cercospora arachidicola",
            "symptoms": [
                "Subcircular reddish-brown to dark-brown spots (1-10 mm) predominantly on upper leaflet surfaces",
                "Prominent, bright yellow chlorotic halo characteristically surrounding each necrotic lesion",
                "Severe premature leaflet dropping (defoliation) leaving bare stems"
            ],
            "prevention": [
                "Practice 2-year crop rotation with non-legume crops (sorghum, pearl millet, maize)",
                "Perform deep summer ploughing to bury fungal conidia and infested haulms",
                "Sow disease-tolerant cultivars (e.g. Kadiri-6, Girnar, ICGV series)",
                "Maintain optimal plant spacing (30 x 10 cm) for canopy aeration"
            ],
            "causes": [
                "Soil-borne conidia and infected crop debris surviving from previous crop seasons",
                "Warm temperatures (25-30°C), high relative humidity (>80%), and prolonged leaf wetness"
            ],
            "limitations": [
                "Early lesions may resemble initial Late Leaf Spot spots; upper-leaf position and distinct bright yellow halos indicate Early Leaf Spot.",
                "Deep learning predictions are probabilistic screening aids. Always verify lesion morphology in the field."
            ],
            "organic": [
                "Seed treatment with Trichoderma viride or T. harzianum (4-5 g/kg seed) to reduce initial soil-borne inoculum.",
                "Foliar spray of 5% Neem Seed Kernel Extract (NSKE; 50 g/L) at first lesion sighting provides protective suppression under low disease pressure."
            ],
            "chemical": [
                "Apply registered fungicides when leaflet infection reaches 5-10%: Carbendazim 12% + Mancozeb 63% WP (2 g/L; PHI 30 days), Tebuconazole 25.9% EC (1.0-1.5 mL/L; PHI 49 days), or Hexaconazole 5% SC (2.0 mL/L; PHI 30 days) per CIB&RC approved labels."
            ]
        },
        "late_leaf_spot": {
            "display_name": "Late Leaf Spot of Groundnut (Tikka Disease)",
            "scientific_name": "Phaeoisariopsis personata",
            "symptoms": [
                "Nearly circular, dark brown to carbonaceous black spots appearing predominantly on lower leaf surfaces",
                "Lesions typically lack a distinct yellow halo or possess only a very narrow, faint halo",
                "Rough, velvety concentric rings of fungal fruiting structures visible on the underside of spots",
                "Rapid extensive leaf drop, leaving bare stems with only topmost leaves attached"
            ],
            "prevention": [
                "Rotate with non-host cereals (pearl millet, sorghum, maize) for at least 2 seasons",
                "Adopt wider row spacing (30-40 cm) to facilitate air circulation and leaf drying",
                "Cultivate tolerant varieties (e.g. Girnar-2, Girnar-3, GPBD-4, ICGV series)",
                "Collect and burn or bury infected haulms post-harvest"
            ],
            "causes": [
                "Infected crop residue in soil and airborne conidia from nearby fields",
                "Temperatures between 20-26°C, relative humidity >85%, and extended leaf wetness (8+ hours)"
            ],
            "limitations": [
                "Late Leaf Spot frequently co-occurs with groundnut rust in the field, producing a combined foliar disease complex.",
                "Examine lower leaf surface conidial cushions to distinguish from Early Leaf Spot."
            ],
            "organic": [
                "Seed biopriming with Trichoderma viride (4 g/kg seed).",
                "Foliar application of 5% Neem Seed Kernel Extract (NSKE) at initial spot appearance on lower canopy leaves."
            ],
            "chemical": [
                "When spots appear on lower leaves around flowering/pegging: Tebuconazole 25.9% EC (1.0-1.5 mL/L; PHI 49 days) or Carbendazim 12% + Mancozeb 63% WP (2 g/L; PHI 30 days) per CIB&RC approved label."
            ]
        },
        "rust": {
            "display_name": "Groundnut Foliar Rust",
            "scientific_name": "Puccinia arachidis",
            "symptoms": [
                "Small, raised circular blisters/pustules (uredinia) measuring 0.5-1.5 mm on the lower leaf surface",
                "Pustules rupture releasing bright orange to cinnamon-brown powdery mass of urediniospores",
                "Corresponding upper leaf surface displays pale yellow chlorotic flecks",
                "Infected leaves curl, turn necrotic, dry out, and remain attached to the plant without premature defoliation"
            ],
            "prevention": [
                "Sow rust-resistant/tolerant cultivars (e.g., GPBD-4, ICGV-91114, Girnar-1, ALR-3)",
                "Avoid staggered sowings in neighboring fields to break continuous infection cycle",
                "Intercrop groundnut with non-host cereals (pearl millet, sorghum, maize)",
                "Eradicate volunteer self-sown groundnut plants between seasons"
            ],
            "causes": [
                "Airborne fungal urediniospores transported across long distances by wind",
                "Moderate temperatures (20-25°C), high relative humidity (>85%), and frequent dew or light showers"
            ],
            "limitations": [
                "Early rust flecks resemble early leaf spots or mite feeding stipples before pustules erupt.",
                "Rub lesion with a clean white tissue; orange-brown powder residue confirms active rust sporulation."
            ],
            "organic": [
                "Foliar spray of 5% Neem Seed Kernel Extract (NSKE) or 3% neem oil upon observing initial pustules.",
                "Cultivate resistant genotypes like GPBD-4."
            ],
            "chemical": [
                "Apply registered fungicides when pustules appear on lower leaves: Hexaconazole 5% SC (2.0 mL/L; PHI 30 days), Tebuconazole 25.9% EC (1.0-1.5 mL/L; PHI 49 days), or Mancozeb 75% WP (2.0-2.5 g/L; PHI 30 days) per approved CIB&RC labels."
            ]
        },
        "nutrition_deficiency": {
            "display_name": "Nutrient Deficiency in Groundnut (Abiotic Chlorosis)",
            "scientific_name": "Abiotic Nutrient Deficiency (Arachis hypogaea)",
            "symptoms": [
                "Iron Chlorosis: Vivid interveinal yellowing of young apical leaflets while veins remain sharply green",
                "Zinc Deficiency: Stunted growth, 'little leaf' rosette symptom, and chlorotic interveinal mottling",
                "Nitrogen Deficiency: Uniform light yellow discoloration of older basal leaves advancing upward",
                "Complete absence of fungal pustules, necrotic spots with yellow halos, or fungal spore mats"
            ],
            "prevention": [
                "Conduct soil testing prior to sowing to determine exact micronutrient and macronutrient status",
                "Incorporate well-rotted farmyard manure (FYM; 10-12 t/ha) or vermicompost to improve soil chelation",
                "Apply Gypsum (400-500 kg/ha in 2 splits: sowing and 40-45 DAS) for calcium and sulfur",
                "Inoculate seeds with Rhizobium and Phosphate Solubilizing Bacteria (PSB)"
            ],
            "causes": [
                "Calcareous soils with high pH (>7.5) immobilizing iron and zinc into insoluble forms",
                "Imbalanced fertilizer application, waterlogging, or low soil organic matter"
            ],
            "limitations": [
                "Interveinal chlorosis can resemble early Groundnut Bud Necrosis Virus (GBNV) mottling; absence of concentric rings and presence across whole young leaves confirms nutrient deficiency.",
                "This is a non-infectious physiological disorder; synthetic fungicides are completely ineffective."
            ],
            "organic": [
                "Apply well-decomposed FYM (10-12 t/ha). Inoculate seeds with Rhizobium and PSB biofertilizers.",
                "Incorporate green manure crops (sunnhemp or sesbania) before sowing."
            ],
            "chemical": [
                "DO NOT apply fungicides. Apply targeted foliar micronutrients: Iron Chlorosis: Ferrous Sulphate (FeSO4, 0.5% = 5 g/L) + Citric acid (0.1% = 1 g/L) at 30 and 45 DAS; Zinc Deficiency: Zinc Sulphate (ZnSO4, 0.5% = 5 g/L); General Chlorosis: 19:19:19 water-soluble NPK (1.0%)."
            ]
        },
        "healthy": {
            "display_name": "Healthy Groundnut Foliage",
            "scientific_name": "Arachis hypogaea (Healthy)",
            "symptoms": [
                "Uniform vibrant green tetrafoliate leaves with intact leaflets and smooth margins",
                "Sturdy erect or spreading stems with healthy flowering nodes and normal peg penetration",
                "Complete absence of fungal spots, rust pustules, chlorotic streaks, or deficiency yellowing"
            ],
            "prevention": [
                "Maintain balanced soil fertility (NPK 20-40-40 kg/ha or soil-test recommendation)",
                "Apply gypsum (400-500 kg/ha) at flowering/pegging for pod filling and kernel development",
                "Perform regular weekly scouting for foliar spots, leaf miners, and sucking pests",
                "Ensure optimal field drainage to prevent waterlogging"
            ],
            "causes": [],
            "limitations": [
                "Visual health confirms absence of foliar symptoms at the time of inspection.",
                "Continue periodic scouting throughout flowering and pod development as weather conditions fluctuate."
            ],
            "organic": [
                "Apply compost or vermicompost (2.5 t/ha). Inoculate seeds with Rhizobium and PSB biofertilizers.",
                "Conserve beneficial generalist predators (spiders, ladybird beetles) by avoiding unnecessary prophylactic chemical sprays."
            ],
            "chemical": [
                "None required for healthy crops. Do NOT apply synthetic chemical fungicides or pesticides to healthy plants."
            ]
        }
    },
    "te": {
        "early_leaf_spot": {
            "display_name": "వేరుశనగ తొలి ఆకుమచ్చ తెగులు (తిక్కా తెగులు)",
            "scientific_name": "సెర్కోస్పోరా అరాచిడికోలా (Cercospora arachidicola)",
            "symptoms": [
                "పై ఆకుల ఉపరితలంపై గుండ్రని లేదా అండాకార ఎరుపు-గోధుమ రంగు మచ్చలు (1-10 మి.మీ)",
                "ప్రతి మచ్చ చుట్టూ స్పష్టమైన, ప్రకాశవంతమైన పసుపు రంగు వలయం (హేలో) ఏర్పడటం",
                "తీవ్రమైన దశలో ఆకులు పసుపు రంగులోకి మారి రాలిపోయి కొమ్మలు మాత్రమే మిగలడం"
            ],
            "prevention": [
                "పప్పుదినుసులు కాని పంటలతో (జొన్న, సజ్జ, మొక్కజొన్న) రెండేళ్ల పంట మార్పిడి చేయాలి",
                "వేసవిలో లోతు దుక్కులు చేసి శిలీంద్ర అవశేషాలను నాశనం చేయాలి",
                "తెగులును తట్టుకునే రకాలను (కదిరి-6, గిర్నార్, ICGV రకాలు) సాగు చేయాలి",
                "గాలి వెలుతురు సరిగ్గా సోకేలా సరైన మొక్కల దూరం (30 x 10 సెం.మీ) పాటించాలి"
            ],
            "causes": [
                "నేలలోని మునుపటి పంట అవశేషాల ద్వారా మరియు గాలి ద్వారా వ్యాపించే శిలీంద్ర సిద్ధబీజాలు",
                "వెచ్చని వాతావరణం (25-30°C), అధిక తేమ (>80%), మరియు ఆకులపై ఎక్కువ సమయం మంచు/నీరు నిలవడం"
            ],
            "limitations": [
                "తొలి ఆకుమచ్చ మలి ఆకుమచ్చలా కనిపించవచ్చు; ఆకుపై భాగంలో ఏర్పడటం మరియు స్పష్టమైన పసుపు వలయం ఉండటం తొలి ఆకుమచ్చ ప్రత్యేకత.",
                "ఈ ఫలితం ముందస్తు అంచనా మాత్రమే; రసాయన మందులు వాడే ముందు క్షేత్రస్థాయిలో నిర్ధారించుకోండి."
            ],
            "organic": [
                "ట్రైకోడెర్మా విరిడే (4-5 గ్రా/కేజీ విత్తనానికి) తో విత్తన శుద్ధి చేయాలి.",
                "తెగులు ప్రారంభ దశలో 5% వేప గింజల కషాయం (NSKE) లేదా వేప నూనె (3 మి.లీ/లీ) పిచికారీ చేయాలి."
            ],
            "chemical": [
                "ఆకులలో 5-10% మచ్చలు గమనించినప్పుడు: కార్బెండజిమ్ 12% + మాంకోజెబ్ 63% WP (2 గ్రా/లీ; PHI 30 రోజులు) లేదా టెబుకొనజోల్ 25.9% EC (1.0-1.5 మి.లీ/లీ; PHI 49 రోజులు) లేదా హెక్సాకొనజోల్ 5% SC (2.0 మి.లీ/లీ; PHI 30 రోజులు) పిచికారీ చేయండి."
            ]
        },
        "late_leaf_spot": {
            "display_name": "వేరుశనగ మలి ఆకుమచ్చ తెగులు (తిక్కా తెగులు)",
            "scientific_name": "ఫియోయిసారియోప్సిస్ పర్సోనేటా (Phaeoisariopsis personata)",
            "symptoms": [
                "ఆకు అడుగు భాగంలో నల్లటి, ముదురు గోధుమ రంగు గుండ్రని మచ్చలు ఏర్పడటం",
                "మచ్చల చుట్టూ పసుపు రంగు వలయం ఉండదు లేదా చాలా సన్నగా కనిపించడం",
                "మచ్చల అడుగు భాగంలో బొగ్గు వంటి నల్లటి శిలీంద్ర బీజాల సమూహాలు ఉండటం",
                "ఆకులు వేగంగా ఎండిపోయి రాలిపోవడం వల్ల తీవ్రమైన పంట నష్టం వాటిల్లుతుంది"
            ],
            "prevention": [
                "సజ్జ, జొన్న లేదా మొక్కజొన్నతో 2 సీజన్ల పాటు పంట మార్పిడి పాటించాలి",
                "మొక్కల మధ్య సరైన దూరం (30-40 సెం.మీ) ఉంచి గాలి ప్రసరణ పెంచాలి",
                "గిర్నార్-2, గిర్నార్-3, GPBD-4 వంటి తట్టుకునే రకాలను సాగు చేయాలి",
                "పంట కోత తర్వాత మిగిలిన మోడులను కాల్చడం లేదా లోతుగా పాతిపెట్టడం చేయాలి"
            ],
            "causes": [
                "నేలలోని మునుపటి పంట మోళ్ళు మరియు గాలి ద్వారా వ్యాపించే శిలీంద్ర బీజాలు",
                "అధిక తేమ (>85%), 20-26°C ఉష్ణోగ్రత మరియు రాత్రిపూట ఎక్కువ మంచు కురవడం"
            ],
            "limitations": [
                "మలి ఆకుమచ్చ తెగులు తరచుగా తుప్పు తెగులుతో కలిసి ఒకే సమయంలో సోకుతుంది.",
                "ఆకు అడుగు భాగాన్ని పరిశీలించి నల్లటి బీజాల ద్వారా తొలి ఆకుమచ్చ నుండి వేరు చేయవచ్చు."
            ],
            "organic": [
                "ట్రైకోడెర్మా విరిడే (4 గ్రా/కేజీ విత్తనానికి) తో విత్తన శుద్ధి చేయాలి.",
                "ఆకులపై తెగులు ప్రారంభమైనప్పుడు 5% వేప గింజల కషాయం (NSKE) పిచికారీ చేయాలి."
            ],
            "chemical": [
                "పూత/ఊడలు దిగే దశలో మచ్చలు కనిపించినప్పుడు: టెబుకొనజోల్ 25.9% EC (1.0-1.5 మి.లీ/లీ; PHI 49 రోజులు) లేదా కార్బెండజిమ్ 12% + మాంకోజెబ్ 63% WP (2 గ్రా/లీ; PHI 30 రోజులు) పిచికారీ చేయండి."
            ]
        },
        "rust": {
            "display_name": "వేరుశనగ తుప్పు తెగులు",
            "scientific_name": "పక్సినియా అరాచిడిస్ (Puccinia arachidis)",
            "symptoms": [
                "ఆకు అడుగు భాగంలో గుండ్రని నారింజ-గోధుమ రంగు పొక్కులు (పుస్టుల్స్) ఏర్పడటం",
                "పొక్కులు పగిలి నారింజ-ఎరుపు రంగు పొడి వంటి శిలీంద్ర బీజాలు వెలువడటం",
                "ఆకు పైభాగంలో లేత పసుపు రంగు చిన్న మచ్చలు కనిపించడం",
                "ఆకులు పైకి ముడుచుకుని, ఎండిపోయి మొక్కకే అతుక్కుని ఉండటం (ఆకులు రాలవు)"
            ],
            "prevention": [
                "తుప్పు తెగులును తట్టుకునే రకాలను (GPBD-4, ICGV-91114, గిర్నార్-1) విత్తుకోవాలి",
                "పక్క పొలాల్లో ఆలస్యంగా విత్తడం నివారించి ఒకేసారి సాగు చేయాలి",
                "సజ్జ లేదా జొన్నతో అంతరపంటగా సాగు చేయాలి",
                "సీజన్ల మధ్య స్వచ్ఛందంగా మొలిచిన వేరుశనగ మొక్కలను పీకి నాశనం చేయాలి"
            ],
            "causes": [
                "గాలి ద్వారా దూర ప్రాంతాల నుండి కొట్టుకొచ్చే శిలీంద్ర యురెడినోస్పోర్లు",
                "20-25°C ఉష్ణోగ్రత, 85% కంటే ఎక్కువ గాలిలో తేమ మరియు తరచూ చిరుజల్లులు"
            ],
            "limitations": [
                "పొక్కులు పగలక ముందు ఆకుమచ్చ తెగులులా లేదా నల్లి గాయాల్లా కనిపించవచ్చు.",
                "తెల్లటి కాగితం లేదా వేలితో రుద్దినప్పుడు నారింజ రంగు పొడి అంటితే తుప్పు తెగులుగా నిర్ధారించవచ్చు."
            ],
            "organic": [
                "మొదటి పొక్కులు కనిపించిన వెంటనే 5% వేప గింజల కషాయం (NSKE) లేదా 3% వేప నూనె పిచికారీ చేయాలి.",
                "GPBD-4 వంటి నిరోధక రకాలను ఎంచుకోవాలి."
            ],
            "chemical": [
                "తెగులు కనిపించినప్పుడు: హెక్సాకొనజోల్ 5% SC (2.0 మి.లీ/లీ; PHI 30 రోజులు) లేదా టెబుకొనజోల్ 25.9% EC (1.0-1.5 మి.లీ/లీ; PHI 49 రోజులు) లేదా మాంకోజెబ్ 75% WP (2.0-2.5 గ్రా/లీ; PHI 30 రోజులు) పిచికారీ చేయండి."
            ]
        },
        "nutrition_deficiency": {
            "display_name": "వేరుశనగలో పోషకాల లోపం (క్లోరోసిస్ / పాలిపోవుట)",
            "scientific_name": "అబయోటిక్ న్యూట్రియంట్ డెఫిషియెన్సీ (Arachis hypogaea)",
            "symptoms": [
                "ఇనుము (ఐరన్) లోపం: లేత చిగురు ఆకులు ఈనెలు పచ్చగా ఉండి మధ్య భాగం పసుపు రంగులోకి మారడం",
                "జింక్ లోపం: మొక్క ఎదుగుదల లోపించడం, చిన్న ఆకులు (లిటిల్ లీఫ్) మరియు ఆకుల మధ్య పసుపు చారలు",
                "నత్రజని లోపం: క్రింది ముదిరిన ఆకులు పూర్తిగా పసుపు రంగులోకి మారి మొక్క పాలిపోవడం",
                "శిలీంద్ర మచ్చలు, పొక్కులు లేదా నల్లటి బీజాలు ఎక్కడా కనిపించవు"
            ],
            "prevention": [
                "విత్తే ముందు నేల పరీక్ష చేయించి లోపించిన పోషకాలను గుర్తించాలి",
                "బాగా కుళ్ళిన పశువుల ఎరువు (10-12 టన్నులు/హెక్టారుకు) లేదా వర్మీకంపోస్ట్ వేయాలి",
                "కాల్షియం, గంధకం కోసం జిప్సం (400-500 కేజీ/హెక్టారుకు) రెండు దఫాలుగా వేయాలి",
                "రైజోబియం మరియు భాస్వరం కరిగించే బ్యాక్టీరియా (PSB) తో విత్తన శుద్ధి చేయాలి"
            ],
            "causes": [
                "సున్నం అధికంగా ఉన్న నేలల్లో (pH > 7.5) ఇనుము, జింక్ మొక్కకు అందకపోవడం",
                "అసంతులిత ఎరువుల వాడకం లేదా నేలలో నీరు నిలిచి వేర్లకు గాలి అందకపోవడం"
            ],
            "limitations": [
                "ఐరన్ లోపం వైరస్ తెగులులా అనిపించవచ్చు; ఆకుపై వలయాలు లేకపోవడం మరియు కొత్త ఆకులన్నింటికీ ఒకేలా రావడం పోషక లోప లక్షణం.",
                "ఇది శిలీంద్ర తెగులు కాదు; దీనికి ఫంగిసైడ్ మందులు అస్సలు పనిచేయవు."
            ],
            "organic": [
                "ఎకరానికి 4-5 టన్నుల పశువుల ఎరువు వేయాలి. రైజోబియం కల్చర్ వాడాలి.",
                "జీలుగ లేదా జనుము వంటి పచ్చిరొట్ట ఎరువులను కలియదున్నాలి."
            ],
            "chemical": [
                "శిలీంద్ర నాశినులు వాడవద్దు. లోప నివారణకు: ఇనుము లోపం అయితే అన్నభేది (ఫెర్రస్ సల్ఫేట్ 5 గ్రా/లీ) + నిమ్మ ఉప్పు (1 గ్రా/లీ) కలిపి పిచికారీ చేయాలి; జింక్ లోపానికి జింక్ సల్ఫేట్ (5 గ్రా/లీ); సాధారణ పాలిపోవుటకు 19:19:19 (10 గ్రా/లీ) పిచికారీ చేయండి."
            ]
        },
        "healthy": {
            "display_name": "ఆరోగ్యకరమైన వేరుశనగ మొక్క",
            "scientific_name": "అరాచిస్ హైపోజియా (Arachis hypogaea - Healthy)",
            "symptoms": [
                "ఆకుపచ్చని దృఢమైన ఆకులు మరియు సరైన ఎదుగుదల",
                "ఎలాంటి మచ్చలు, తుప్పు పొక్కులు, లేదా పోషక లోపాలు లేకపోవడం",
                "సరైన పూత మరియు ఊడలు ఆరోగ్యంగా నేలలోకి దిగడం"
            ],
            "prevention": [
                "నేల పరీక్ష ఆధారంగా సమతుల్య NPK ఎరువులు వేయాలి",
                "ఊడలు దిగే దశలో ఎకరానికి 200 కేజీల జిప్సం వేయాలి",
                "క్రమం తప్పకుండా చీడపీడల కోసం పొలాన్ని పరిశీలిస్తుండాలి",
                "పొలంలో నీరు నిల్వ ఉండకుండా చూసుకోవాలి"
            ],
            "causes": [],
            "limitations": [
                "ప్రస్తుతం మొక్కపై ఎలాంటి వ్యాధి లక్షణాలు లేవు.",
                "వాతావరణంలో మార్పులు వస్తే తెగుళ్ళు సోకే అవకాశం ఉన్నందున వారానికోసారి పొలాన్ని గమనించండి."
            ],
            "organic": [
                "పశువుల ఎరువు లేదా వర్మీకంపోస్ట్ వాడండి. మిత్రపురుగులను కాపాడుకోండి.",
                "అనవసర రసాయన మందులు వాడకండి."
            ],
            "chemical": [
                "ఆరోగ్యకరమైన పంటపై ఎలాంటి రసాయన మందులు పిచికారీ చేయవలసిన అవసరం లేదు."
            ]
        }
    },
    "hi": {
        "early_leaf_spot": {
            "display_name": "मूंगफली का अगेती पत्ती धब्बा रोग (टिक्का रोग)",
            "scientific_name": "सर्कोस्पोरा अराकिडिकोला (Cercospora arachidicola)",
            "symptoms": [
                "पत्तियों की ऊपरी सतह पर गोल या अंडाकार लाल-भूरे धब्बे (1-10 मिमी)",
                "प्रत्येक धब्बे के चारों ओर स्पष्ट चमकदार पीला घेरा (हेलो) दिखाई देना",
                "गंभीर संक्रमण में पत्तियां पीली होकर समय से पहले गिर जाती हैं"
            ],
            "prevention": [
                "गैर-दलहनी फसलों (ज्वार, बाजरा, मक्का) के साथ 2 वर्ष का फसल चक्र अपनाएं",
                "गर्मियों में गहरी जुताई करें ताकि कवक अवशेष नष्ट हो जाएं",
                "रोग प्रतिरोधी किस्में (कदिरि-6, गिरनार, ICGV) लगाएं",
                "हवा के संचार के लिए कतारों के बीच उचित दूरी (30 x 10 सेमी) रखें"
            ],
            "causes": [
                "मिट्टी में पड़े पुराने फसल अवशेष और हवा द्वारा फैलने वाले कवक बीजाणु",
                "गर्म तापमान (25-30°C), उच्च आर्द्रता (>80%) और पत्तियों पर देर तक ओस रहना"
            ],
            "limitations": [
                "अगेती धब्बा पछेती धब्बे जैसा लग सकता है; ऊपरी सतह पर पीला घेरा अगेती रोग की पहचान है।",
                "यह केवल प्रारंभिक जांच है; दवा छिड़कने से पहले खेत में पुष्टि करें।"
            ],
            "organic": [
                "ट्राइकोडर्मा विरिडी (4-5 ग्राम/किग्रा बीज) से बीजोपचार करें।",
                "प्रारंभिक लक्षण दिखने पर 5% नीम गिरी अर्क (NSKE) का छिड़काव करें।"
            ],
            "chemical": [
                "पत्तियों पर 5-10% धब्बे दिखने पर: कार्बेन्डाजिम 12% + मैंकोजेब 63% WP (2 ग्राम/लीटर; PHI 30 दिन) या टेबुकोनाजोल 25.9% EC (1.0-1.5 मिली/लीटर; PHI 49 दिन) का छिड़काव करें।"
            ]
        },
        "late_leaf_spot": {
            "display_name": "मूंगफली का पछेती पत्ती धब्बा रोग (टिक्का रोग)",
            "scientific_name": "फियोआइसारियोप्सिस परसोनेटा (Phaeoisariopsis personata)",
            "symptoms": [
                "पत्तियों की निचली सतह पर गहरे काले-भूरे गोल धब्बे बनना",
                "धब्बों के चारों ओर पीला घेरा नहीं होता या बहुत हल्का होता है",
                "धब्बों के नीचे काले मखमली बीजाणुओं के छल्ले दिखाई देते हैं",
                "पत्तियां तेजी से सूखकर झड़ जाती हैं और केवल तने बचते हैं"
            ],
            "prevention": [
                "बाजरा, मक्का या ज्वार के साथ 2 मौसम तक फसल चक्र अपनाएं",
                "हवा के आवागमन के लिए उचित दूरी (30-40 सेमी) रखें",
                "सहनशील किस्में (गिरनार-2, गिरनार-3, GPBD-4) बोएं",
                "कटाई के बाद अवशेषों को जलाएं या मिट्टी में गहरा दबाएं"
            ],
            "causes": [
                "मिट्टी में संक्रमित फसल अवशेष और हवा से उड़कर आने वाले बीजाणु",
                "तापमान 20-26°C, आर्द्रता >85% और पत्तियों पर 8+ घंटे नमी रहना"
            ],
            "limitations": [
                "पछेती धब्बा रोग अक्सर गेरूई (रस्ट) के साथ मिलकर हमला करता है।",
                "निचली सतह पर काले उभारों को देखकर अगेती धब्बे से अलग पहचानें।"
            ],
            "organic": [
                "ट्राइकोडर्मा विरिडी (4 ग्राम/किग्रा) से बीजोपचार करें।",
                "निचली पत्तियों पर धब्बे दिखते ही 5% नीम गिरी अर्क (NSKE) छिड़कें।"
            ],
            "chemical": [
                "फूल व खूंटी बनने के समय लक्षण दिखने पर: टेबुकोनाजोल 25.9% EC (1.0-1.5 मिली/लीटर; PHI 49 दिन) या कार्बेन्डाजिम 12% + मैंकोजेब 63% WP (2 ग्राम/लीटर; PHI 30 दिन) छिड़कें।"
            ]
        },
        "rust": {
            "display_name": "मूंगफली का गेरूई / रस्ट रोग",
            "scientific_name": "पक्सिनिया अराकिडिस (Puccinia arachidis)",
            "symptoms": [
                "पत्तियों की निचली सतह पर उभरे हुए गोल नारंगी-भूरे फफोले (पुस्ट्यूल)",
                "फफोलों के फटने पर नारंगी-लाल रंग का चूर्ण जैसा पाउडर निकलता है",
                "ऊपरी सतह पर हल्के पीले छोटे धब्बे दिखाई देते हैं",
                "संक्रमित पत्तियां मुड़कर सूख जाती हैं परंतु पौधे से गिरती नहीं हैं"
            ],
            "prevention": [
                "रोग रोधी किस्में (GPBD-4, ICGV-91114, गिरनार-1) उगाएं",
                "पड़ोसी खेतों में देर से बुवाई करने से बचें",
                "ज्वार या बाजरा के साथ अंतर्वर्ती फसल लें",
                "मौसम के बीच उगे मूंगफली के पौधों को नष्ट करें"
            ],
            "causes": [
                "हवा द्वारा दूर से उड़कर आने वाले कवक बीजाणु (यूरेडिनोस्पोर्स)",
                "तापमान 20-25°C, आर्द्रता >85% और हल्की वर्षा या भारी ओस"
            ],
            "limitations": [
                "फफोले फूटने से पहले यह धब्बा रोग जैसा लग सकता है।",
                "सफेद कपड़े या उंगली से रगड़ने पर नारंगी पाउडर लगे तो यह रस्ट है।"
            ],
            "organic": [
                "शुरुआती लक्षण दिखते ही 5% नीम अर्क या 3% नीम तेल का छिड़काव करें।",
                "GPBD-4 जैसी प्रतिरोधी किस्में अपनाएं।"
            ],
            "chemical": [
                "लक्षण दिखने पर: हेक्साकोनाजोल 5% SC (2.0 मिली/लीटर; PHI 30 दिन) या टेबुकोनाजोल 25.9% EC (1.0-1.5 मिली/लीटर; PHI 49 दिन) या मैंकोजेब 75% WP (2.0-2.5 ग्राम/लीटर; PHI 30 दिन) का छिड़काव करें।"
            ]
        },
        "nutrition_deficiency": {
            "display_name": "मूंगफली में पोषक तत्वों की कमी (अजैविक पीलापन)",
            "scientific_name": "अजैविक पोषक तत्व कमी (Arachis hypogaea)",
            "symptoms": [
                "आयरन की कमी: नई ऊपरी पत्तियों की नसें हरी रहती हैं और बीच का भाग पीला हो जाता है",
                "जिंक की कमी: पौधों की वृद्धि रुकना, छोटी पत्तियां और नसों के बीच पीलापन",
                "नाइट्रोजन की कमी: निचली पुरानी पत्तियां पूरी तरह पीली पड़ना",
                "कवक के धब्बे, फफोले या बीजाणु बिल्कुल नहीं पाए जाते"
            ],
            "prevention": [
                "बुवाई से पहले मिट्टी की जांच करवाकर पोषक तत्वों का संतुलन बनाएं",
                "खेत में 10-12 टन/हेक्टेयर सड़ी गोबर की खाद या वर्मीकम्पोस्ट डालें",
                "कैल्शियम व सल्फर के लिए जिप्सम (400-500 किग्रा/हे.) दो बार डालें",
                "राइजोबियम और पीएसबी कल्चर से बीजोपचार करें"
            ],
            "causes": [
                "चूनेदार मिट्टी (pH > 7.5) में लोहा और जिंक पौधों को नहीं मिल पाना",
                "असंतुलित खाद डालना या खेत में पानी भरा रहने से जड़ों का दम घुटना"
            ],
            "limitations": [
                "आयरन की कमी वायरस रोग जैसी लग सकती है; छल्ले न होना और सभी नई पत्तियों का पीला होना पोषण कमी की पहचान है।",
                "यह कोई बीमारी नहीं है; फफूंदनाशक दवाएं इस पर बिल्कुल बेअसर हैं।"
            ],
            "organic": [
                "गोबर की खाद डालें और राइजोबियम कल्चर का प्रयोग करें।",
                "बुवाई से पहले सनई या ढैंचा की हरी खाद खेत में दबाएं।"
            ],
            "chemical": [
                "फफूंदनाशक न डालें। आयरन की कमी में फेरस सल्फेट (5 ग्राम/ली) + नींबू का सत्त (1 ग्राम/ली); जिंक की कमी में जिंक सल्फेट (5 ग्राम/ली) का छिड़काव करें।"
            ]
        },
        "healthy": {
            "display_name": "स्वस्थ मूंगफली का पौधा",
            "scientific_name": "अराकिडिस हाइपोजिया (Arachis hypogaea - Healthy)",
            "symptoms": [
                "गहरी हरी स्वस्थ पत्तियां और सामान्य वानस्पतिक वृद्धि",
                "किसी भी प्रकार के धब्बे, फफोले या पीलेपन का न होना",
                "फूल व खूंटियों का मिट्टी में सामान्य रूप से प्रवेश करना"
            ],
            "prevention": [
                "संतुलित उर्वरकों (NPK) का समय पर उपयोग करें",
                "खूंटी बनने पर जिप्सम 200 किग्रा/एकड़ की दर से डालें",
                "कीट व रोगों के लिए नियमित खेत का निरीक्षण करें",
                "खेत में जल निकास का उचित प्रबंध रखें"
            ],
            "causes": [],
            "limitations": [
                "वर्तमान में पौधा पूरी तरह रोगमुक्त है।",
                "मौसम बदलने पर निगरानी बनाए रखें।"
            ],
            "organic": [
                "जैविक खाद डालें और मित्र कीटों का संरक्षण करें।",
                "अनावश्यक रासायनिक कीटनाशकों से बचें।"
            ],
            "chemical": [
                "स्वस्थ फसल पर किसी भी प्रकार के रासायनिक छिड़काव की आवश्यकता नहीं है।"
            ]
        }
    },
    "ta": {
        "early_leaf_spot": {
            "display_name": "நிலக்கடலை முந்தைய இலைப்புள்ளி நோய் (திக்கா நோய்)",
            "scientific_name": "செர்கோஸ்போரா அராச்சிடிகோலா (Cercospora arachidicola)",
            "symptoms": [
                "இலைகளின் மேல் பகுதியில் வட்டமான அல்லது முட்டை வடிவ சிவப்பு-பழுப்பு நிற புள்ளிகள்",
                "ஒவ்வொரு புள்ளியையும் சுற்றி தெளிவான மஞ்சள் நிற வளையம் (வளைய வளையம்) காணப்படுதல்",
                "தீவிர நிலையில் இலைகள் மஞ்சள் நிறமாகி உதிர்ந்து தண்டு மட்டும் நிற்கும்"
            ],
            "prevention": [
                "தானிய பயிர்களுடன் (சோளம், கம்பு) 2 ஆண்டுகள் பயிர் சுழற்சி செய்ய வேண்டும்",
                "கோடை உழவு செய்து பூஞ்சாண வித்துக்களை அழிக்க வேண்டும்",
                "நோய் எதிர்ப்பு ரகங்களை (கதிரி-6, கிர்னார்) பயிரிட வேண்டும்",
                "காற்று ஓட்டத்திற்கு உகந்த பயிர் இடைவெளி (30 x 10 செ.மீ) பராமரிக்கவும்"
            ],
            "causes": [
                "மண்ணில் உள்ள பயிர் கழிவுகள் மற்றும் காற்றில் பரவும் பூஞ்சை வித்துக்கள்",
                "வெப்பம் (25-30°C), அதிக ஈரப்பதம் (>80%) மற்றும் இலைகளில் பனி தேங்குதல்"
            ],
            "limitations": [
                "முந்தைய இலைப்புள்ளி பிந்தைய புள்ளி போல் தெரியலாம்; மஞ்சள் வளையம் முந்தைய புள்ளியின் அடையாளம்.",
                "இது முன்னறிவிப்பு மட்டுமே; மருந்து தெளிக்கும் முன் வயலில் உறுதிப்படுத்தவும்."
            ],
            "organic": [
                "ட்ரைக்கோடெர்மா விரிடி (4-5 கிராம்/கிலோ விதை) கொண்டு விதை நேர்த்தி செய்யவும்.",
                "தொடக்கத்தில் 5% வேப்பங்கொட்டை சாறு (NSKE) தெளிக்கவும்."
            ],
            "chemical": [
                "5-10% புள்ளிகள் தென்படும் போது: கார்பென்டாசிம் 12% + மான்கோசெப் 63% WP (2 கிராம்/லி; PHI 30 நாட்கள்) அல்லது டெபுகோனசோல் 25.9% EC (1.0-1.5 மி.லி/லி; PHI 49 நாட்கள்) தெளிக்கவும்."
            ]
        },
        "late_leaf_spot": {
            "display_name": "நிலக்கடலை பிந்தைய இலைப்புள்ளி நோய் (திக்கா நோய்)",
            "scientific_name": "பியோயிசாரியோப்சிஸ் பெர்சனேட்டா (Phaeoisariopsis personata)",
            "symptoms": [
                "இலைகளின் கீழ் பகுதியில் கருமை கலந்த பழுப்பு நிற வட்ட புள்ளிகள்",
                "புள்ளிகளை சுற்றி மஞ்சள் வளையம் இருக்காது அல்லது மிகவும் மெல்லியதாக இருக்கும்",
                "புள்ளிகளின் அடியில் கரிய போன்ற பூஞ்சை வித்துக்கள் காணப்படும்",
                "இலைகள் மிக வேகமாக காய்ந்து உதிர்ந்து விடும்"
            ],
            "prevention": [
                "கம்பு அல்லது சோளத்துடன் 2 பருவங்களுக்கு பயிர் சுழற்சி முறை பின்பற்றவும்",
                "பயிர் இடைவெளியை (30-40 செ.மீ) அகலப்படுத்தி காற்று வசதியை பெருக்கவும்",
                "கிர்னார்-2, GPBD-4 போன்ற எதிர்ப்பு ரகங்களை பயிரிடவும்"
            ],
            "causes": [
                "மண்ணில் உள்ள பயிர் எச்சங்கள் மற்றும் காற்றில் பரவும் வித்துக்கள்",
                "ஈரப்பதம் >85%, வெப்பநிலை 20-26°C மற்றும் இலைகளில் அதிக நேரம் பனி தங்குதல்"
            ],
            "limitations": [
                "பிந்தைய இலைப்புள்ளி பெரும்பாலும் துரு நோயுடன் இணைந்து தோன்றும்.",
                "இலையின் அடிப்பகுதியை ஆய்வு செய்து கருமை நிறம் மூலம் முந்தைய புள்ளியிலிருந்து வேறுபடுத்தலாம்."
            ],
            "organic": [
                "ட்ரைக்கோடெர்மா விரிடி கொண்டு விதை நேர்த்தி செய்யவும். 5% வேப்பங்கொட்டை சாறு தெளிக்கவும்."
            ],
            "chemical": [
                "டெபுகோனசோல் 25.9% EC (1.0-1.5 மி.லி/லி; PHI 49 நாட்கள்) அல்லது கார்பென்டாசிம் + மான்கோசெப் (2 கிராம்/லி; PHI 30 நாட்கள்) தெளிக்கவும்."
            ]
        },
        "rust": {
            "display_name": "நிலக்கடலை துரு நோய்",
            "scientific_name": "பக்சினியா அராச்சிடிஸ் (Puccinia arachidis)",
            "symptoms": [
                "இலையின் அடிப்பகுதியில் வட்டமான செம்பழுப்பு நிற கொப்புளங்கள் தோன்றுதல்",
                "கொப்புளங்கள் வெடித்து செம்பழுப்பு தூள் போன்ற வித்துக்கள் வெளியேறுதல்",
                "இலையின் மேல் பகுதியில் வெளிறிய மஞ்சள் புள்ளிகள் காணப்படுதல்",
                "இலைகள் காய்ந்து சுருங்கி செடியிலேயே ஒட்டிக்கொண்டிருக்கும் (உதிராது)"
            ],
            "prevention": [
                "துரு நோய் எதிர்ப்பு ரகங்களை (GPBD-4, ICGV-91114) பயிரிடவும்",
                "பக்கத்து வயல்களில் காலதாமதமாக விதைப்பதை தவிர்க்கவும்",
                "சோளம் அல்லது கம்புடன் ஊடுபயிராக சாகுபடி செய்யவும்"
            ],
            "causes": [
                "காற்றில் வெகுதூரம் அடித்து வரப்படும் பூஞ்சை வித்துக்கள்",
                "20-25°C வெப்பநிலை, 85% மேல் காற்றில் ஈரப்பதம் மற்றும் தூறல் மழை"
            ],
            "limitations": [
                "கொப்புளங்கள் வெடிக்கும் முன் இலைப்புள்ளி நோய் போல் தெரியலாம்.",
                "வெள்ளை துணியால் துடைக்கும் போது ஆரஞ்சு தூள் ஒட்டினால் துரு நோய் என உறுதி செய்யலாம்."
            ],
            "organic": [
                "அறிகுறிகள் தென்பட்டவுடன் 5% வேப்பங்கொட்டை சாறு அல்லது 3% வேப்ப எண்ணெய் தெளிக்கவும்."
            ],
            "chemical": [
                "ஹெக்சாகோனசோல் 5% SC (2.0 மி.லி/லி; PHI 30 நாட்கள்) அல்லது டெபுகோனசோல் 25.9% EC (1.0-1.5 மி.லி/லி; PHI 49 நாட்கள்) தெளிக்கவும்."
            ]
        },
        "nutrition_deficiency": {
            "display_name": "நிலக்கடலையில் ஊட்டச்சத்து குறைபாடு (குளோரோசிஸ்)",
            "scientific_name": "அபயோடிக் ஊட்டச்சத்து குறைபாடு (Arachis hypogaea)",
            "symptoms": [
                "இரும்புச்சத்து குறைபாடு: புதிய தளிர் இலைகளின் நரம்புகள் பச்சையாகவும் இடைப்பகுதி மஞ்சளாகவும் மாறுதல்",
                "துத்தநாக குறைபாடு: செடி வளர்ச்சி குன்றுதல், சிறிய இலைகள்",
                "தழைச்சத்து குறைபாடு: முதிர்ந்த கீழ் இலைகள் சீராக மஞ்சள் நிறமாக மாறுதல்",
                "பூஞ்சை புள்ளிகளோ, கொப்புளங்களோ முற்றிலும் இருக்காது"
            ],
            "prevention": [
                "விதைப்பதற்கு முன் மண் பரிசோதனை செய்து ஊட்டச்சத்துக்களை இடவும்",
                "மக்கிய தொழு உரம் (10-12 டன்/ஹெக்டர்) இட வேண்டும்",
                "ஜிப்சம் (400-500 கிலோ/ஹெக்டர்) இரு முறை இடவும்",
                "ரைசோபியம் மற்றும் பாஸ்போபாக்டீரியா கொண்டு விதை நேர்த்தி செய்யவும்"
            ],
            "causes": [
                "சுண்ணாம்பு நிலங்களில் (pH > 7.5) இரும்பு, துத்தநாகம் கிடைக்காமல் போவது",
                "தண்ணீர் தேங்குதல் மற்றும் சமச்சீரற்ற உரமிடுதல்"
            ],
            "limitations": [
                "இரும்பு குறைபாடு நச்சுயிரி நோய் போல் தெரியலாம்; நரம்புகள் பச்சையாக இருப்பது இதன் சிறப்பு.",
                "இது தொற்று நோய் அல்ல; பூஞ்சாண மருந்துகள் பயன் தராது."
            ],
            "organic": [
                "தொழு உரம் இடவும். தக்கைப்பூண்டு அல்லது சணப்பை பயிரிட்டு மடக்கி உழவும்."
            ],
            "chemical": [
                "பூஞ்சாண மருந்து தெளிக்க வேண்டாம். இரும்பு குறைபாட்டிற்கு அன்னபேதி (5 கிராம்/லி) + எலுமிச்சை உப்பு (1 கிராம்/லி); துத்தநாக குறைபாட்டிற்கு துத்தநாக சல்பேட் (5 கிராம்/லி) தெளிக்கவும்."
            ]
        },
        "healthy": {
            "display_name": "ஆரோக்கியமான நிலக்கடலை செடி",
            "scientific_name": "அராச்சிஸ் ஹைபோஜியா (Arachis hypogaea - Healthy)",
            "symptoms": [
                "பச்சை நிற ஆரோக்கியமான இலைகள் மற்றும் சீரான வளர்ச்சி",
                "எந்தவித புள்ளிகளும், கொப்புளங்களும் இல்லாத தூய்மையான இலைகள்",
                "சீரான பூக்கள் மற்றும் விழுதுகள் மண்ணில் இறங்குதல்"
            ],
            "prevention": [
                "மண் பரிசோதனை அடிப்படையில் சமச்சீர் உரங்களை இடவும்",
                "விழுது இறங்கும் போது ஜிப்சம் இடவும்",
                "வாரம் ஒருமுறை பயிரை ஆய்வு செய்யவும்"
            ],
            "causes": [],
            "limitations": [
                "தற்போது பயிரில் எந்தவித நோய்களும் இல்லை.",
                "பருவநிலை மாறும்போது தொடர்ந்து கண்காணிக்கவும்."
            ],
            "organic": [
                "இயற்கை உரங்களை இடவும் மற்றும் நன்மை செய்யும் பூச்சிகளை பாதுகாக்கவும்."
            ],
            "chemical": [
                "ஆரோக்கியமான பயிருக்கு எந்தவித பூச்சிக்கொல்லியும் தேவையில்லை."
            ]
        }
    },
    "kn": {
        "early_leaf_spot": {
            "display_name": "ಕಡಲೆಕಾಯಿ ಆರಂಭಿಕ ಎಲೆ ಚುಕ್ಕೆ ರೋಗ (ತಿಕ್ಕಾ ರೋಗ)",
            "scientific_name": "ಸರ್ಕೋಸ್ಪೊರಾ ಅರಾಚಿಡಿಕೊಲಾ (Cercospora arachidicola)",
            "symptoms": [
                "ಎಲೆಗಳ ಮೇಲ್ಭಾಗದಲ್ಲಿ ವೃತ್ತಾಕಾರದ ಅಥವಾ ಅಂಡಾಕಾರದ ಕೆಂಪು-ಕಂದು ಬಣ್ಣದ ಚುಕ್ಕೆಗಳು",
                "ಪ್ರತಿ ಚುಕ್ಕೆಯ ಸುತ್ತಲೂ ಎದ್ದು ಕಾಣುವ ಪ್ರಕಾಶಮಾನವಾದ ಹಳದಿ ಬಣ್ಣದ ಬಳೆ (ಹಾಲೋ)",
                "ತೀವ್ರ ಹಂತದಲ್ಲಿ ಎಲೆಗಳು ಉದುರಿ ಬರೀ ಕಾಂಡಗಳು ಮಾತ್ರ ಉಳಿಯುತ್ತವೆ"
            ],
            "prevention": [
                "ದ್ವಿದಳ ಧಾನ್ಯವಲ್ಲದ ಬೆಳೆಗಳೊಂದಿಗೆ (ಜೋಳ, ಸಜ್ಜೆ, ಮೆಕ್ಕೆಜೋಳ) 2 ವರ್ಷ ಬೆಳೆ ಪರಿವರ್ತನೆ ಮಾಡಿ",
                "ಬೇಸಿಗೆಯಲ್ಲಿ ಆಳವಾದ ಉಳುಮೆ ಮಾಡಿ ಶಿಲೀಂಧ್ರ ಅವಶೇಷಗಳನ್ನು ನಾಶಮಾಡಿ",
                "ರೋಗ ನಿರೋಧಕ ತಳಿಗಳನ್ನು (ಕದಿರಿ-6, ಗಿರ್ನಾರ್) ಬೆಳೆಯಿರಿ",
                "ಗಾಳಿಯಾಡಲು ಸೂಕ್ತ ಸಸಿಗಳ ಅಂತರ (30 x 10 ಸೆಂ.ಮೀ) ಕಾಪಾಡಿಕೊಳ್ಳಿ"
            ],
            "causes": [
                "ಮಣ್ಣಿನಲ್ಲಿರುವ ಬೆಳೆ ಕಸ ಮತ್ತು ಗಾಳಿಯ ಮೂಲಕ ಹರಡುವ ಶಿಲೀಂಧ್ರ ಬೀಜಕಗಳು",
                "ಬೆಚ್ಚನೆಯ ವಾತಾವರಣ (25-30°C), ಹೆಚ್ಚಿನ ತೇವಾಂಶ (>80%) ಮತ್ತು ಇಬ್ಬನಿ"
            ],
            "limitations": [
                "ಆರಂಭಿಕ ಚುಕ್ಕೆ ತಡವಾದ ಚುಕ್ಕೆಯಂತೆ ಕಾಣಬಹುದು; ಹಳದಿ ಬಳೆ ಆರಂಭಿಕ ಚುಕ್ಕೆಯ ಪ್ರಮುಖ ಲಕ್ಷಣ.",
                "ಇದು ಮುನ್ನೆಚ್ಚರಿಕೆ ಮಾಹಿತಿ ಮಾತ್ರ; ಔಷಧಿ ಸಿಂಪಡಿಸುವ ಮುನ್ನ ಹೊಲದಲ್ಲಿ ಪರಿಶೀಲಿಸಿ."
            ],
            "organic": [
                "ಟ್ರೈಕೋಡರ್ಮಾ ವಿರಿಡೆ (4-5 ಗ್ರಾಂ/ಕೆಜಿ ಬೀಜಕ್ಕೆ) ಬೀಜೋಪಚಾರ ಮಾಡಿ.",
                "ಆರಂಭದಲ್ಲಿ 5% ಬೇವಿನ ಬೀಜದ ಕಷಾಯ (NSKE) ಸಿಂಪಡಿಸಿ."
            ],
            "chemical": [
                "ಶೇ 5-10 ರಷ್ಟು ಎಲೆಗಳಲ್ಲಿ ಚುಕ್ಕೆಗಳು ಕಂಡಾಗ: ಕಾರ್ಬೆಂಡಾಜಿಮ್ 12% + ಮ್ಯಾಂಕೋಜೆಬ್ 63% WP (2 ಗ್ರಾಂ/ಲೀ; PHI 30 ದಿನ) ಅಥವಾ ಟೆಬುಕೊನಜೋಲ್ 25.9% EC (1.0-1.5 ಮಿ.ಲೀ/ಲೀ; PHI 49 ದಿನ) ಸಿಂಪಡಿಸಿ."
            ]
        },
        "late_leaf_spot": {
            "display_name": "ಕಡಲೆಕಾಯಿ ತಡವಾದ ಎಲೆ ಚುಕ್ಕೆ ರೋಗ (ತಿಕ್ಕಾ ರೋಗ)",
            "scientific_name": "ಫಿಯೋಯಿಸಾರಿಯೊಪ್ಸಿಸ್ ಪರ್ಸೊನೇಟಾ (Phaeoisariopsis personata)",
            "symptoms": [
                "ಎಲೆಗಳ ಕೆಳಭಾಗದಲ್ಲಿ ಕಡು ಕಪ್ಪು-ಕಂದು ಬಣ್ಣದ ದುಂಡಗಿನ ಚುಕ್ಕೆಗಳು",
                "ಚುಕ್ಕೆಗಳ ಸುತ್ತ ಹಳದಿ ಬಳೆ ಇರುವುದಿಲ್ಲ ಅಥವಾ ಅಸ್ಪಷ್ಟವಾಗಿರುತ್ತದೆ",
                "ಚುಕ್ಕೆಗಳ ಕೆಳಭಾಗದಲ್ಲಿ ಕಪ್ಪು ಬಣ್ಣದ ವೆಲ್ವೆಟ್ ನಂತಹ ಶಿಲೀಂಧ್ರದ ಉಬ್ಬುಗಳು",
                "ಎಲೆಗಳು ವೇಗವಾಗಿ ಒಣಗಿ ಉದುರಿಹೋಗುತ್ತವೆ"
            ],
            "prevention": [
                "ಜೋಳ ಅಥವಾ ಸಜ್ಜೆಯೊಂದಿಗೆ 2 ಋತುಗಳ ಕಾಲ ಬೆಳೆ ಪರಿವರ್ತನೆ ಮಾಡಿ",
                "ಬೆಳೆಯ ಸಾಲುಗಳ ನಡುವೆ ಸೂಕ್ತ ಅಂತರ (30-40 ಸೆಂ.ಮೀ) ಇರಲಿ",
                "ಗಿರ್ನಾರ್-2, GPBD-4 ನಂತಹ ತಡೆದುಕೊಳ್ಳುವ ತಳಿಗಳನ್ನು ಬೆಳೆಯಿರಿ"
            ],
            "causes": [
                "ಮಣ್ಣಿನಲ್ಲಿರುವ ಬೆಳೆಯ ಅವಶೇಷಗಳು ಮತ್ತು ಗಾಳಿಯಿಂದ ಬರುವ ಬೀಜಕಗಳು",
                "ಹೆಚ್ಚಿನ ತೇವಾಂಶ (>85%), 20-26°C ತಾಪಮಾನ ಮತ್ತು ದೀರ್ಘಕಾಲದ ಇಬ್ಬನಿ"
            ],
            "limitations": [
                "ತಡವಾದ ಎಲೆ ಚುಕ್ಕೆ ಹೆಚ್ಚಾಗಿ ತುಕ್ಕು ರೋಗದೊಂದಿಗೆ ಒಟ್ಟಿಗೆ ಬರುತ್ತದೆ.",
                "ಎಲೆಯ ಕೆಳಭಾಗದಲ್ಲಿ ಕಪ್ಪು ಉಬ್ಬುಗಳನ್ನು ನೋಡಿ ಆರಂಭಿಕ ಚುಕ್ಕೆಯಿಂದ ಪ್ರತ್ಯೇಕಿಸಬಹುದು."
            ],
            "organic": [
                "ಟ್ರೈಕೋಡರ್ಮಾ ವಿರಿಡೆಯಿಂದ ಬೀಜೋಪಚಾರ ಮಾಡಿ. 5% ಬೇವಿನ ಕಷಾಯ ಸಿಂಪಡಿಸಿ."
            ],
            "chemical": [
                "ಹೂವಾಡುವ/ಕಾಯಿ ಕಟ್ಟುವ ಹಂತದಲ್ಲಿ ಚುಕ್ಕೆಗಳು ಕಂಡಾಗ: ಟೆಬುಕೊನಜೋಲ್ 25.9% EC (1.0-1.5 ಮಿ.ಲೀ/ಲೀ; PHI 49 ದಿನ) ಅಥವಾ ಕಾರ್ಬೆಂಡಾಜಿಮ್ + ಮ್ಯಾಂಕೋಜೆಬ್ (2 ಗ್ರಾಂ/ಲೀ; PHI 30 ದಿನ) ಸಿಂಪಡಿಸಿ."
            ]
        },
        "rust": {
            "display_name": "ಕಡಲೆಕಾಯಿ ತುಕ್ಕು ರೋಗ",
            "scientific_name": "ಪಕ್ಸಿನಿಯಾ ಅರಾಚಿಡಿಸ್ (Puccinia arachidis)",
            "symptoms": [
                "ಎಲೆಯ ಕೆಳಭಾಗದಲ್ಲಿ ದುಂಡಗಿನ ಕಿತ್ತಳೆ-ಕಂದು ಬಣ್ಣದ ಬೊಬ್ಬೆಗಳು (ಪುಸ್ಟ್ಯೂಲ್ಸ್)",
                "ಬೊಬ್ಬೆಗಳು ಒಡೆದು ಕಿತ್ತಳೆ ಬಣ್ಣದ ಪುಡಿ ಬೀಜಕಗಳು ಹೊರಬರುತ್ತವೆ",
                "ಎಲೆಯ ಮೇಲ್ಭಾಗದಲ್ಲಿ ತಿಳಿ ಹಳದಿ ಚುಕ್ಕೆಗಳು ಕಾಣಿಸಿಕೊಳ್ಳುತ್ತವೆ",
                "ರೋಗಗ್ರಸ್ತ ಎಲೆಗಳು ಸುರುಟಿಕೊಂಡು ಒಣಗುತ್ತವೆ ಆದರೆ ಗಿಡದಿಂದ ಉದುರುವುದಿಲ್ಲ"
            ],
            "prevention": [
                "ತುಕ್ಕು ನಿರೋಧಕ ತಳಿಗಳನ್ನು (GPBD-4, ICGV-91114) ಬಿತ್ತನೆ ಮಾಡಿ",
                "ಹತ್ತಿರದ ಹೊಲಗಳಲ್ಲಿ ತಡವಾಗಿ ಬಿತ್ತುವುದನ್ನು ತಪ್ಪಿಸಿ",
                "ಜೋಳ ಅಥವಾ ಸಜ್ಜೆಯೊಂದಿಗೆ ಮಿಶ್ರಬೆಳೆಯಾಗಿ ಬೆಳೆಯಿರಿ"
            ],
            "causes": [
                "ಗಾಳಿಯ ಮೂಲಕ ದೂರದಿಂದ ಬರುವ ಶಿಲೀಂಧ್ರ ಬೀಜಕಗಳು",
                "20-25°C ತಾಪಮಾನ, 85% ಕ್ಕಿಂತ ಹೆಚ್ಚಿನ ತೇವಾಂಶ ಮತ್ತು ಮಳೆ ಹನಿಗಳು"
            ],
            "limitations": [
                "ಬೊಬ್ಬೆಗಳು ಒಡೆಯುವ ಮುನ್ನ ಚುಕ್ಕೆ ರೋಗದಂತೆ ಕಾಣಬಹುದು.",
                "ಬೆರಳು ಅಥವಾ ಬಿಳಿ ಬಟ್ಟೆಯಿಂದ ಉಜ್ಜಿದಾಗ ಕಿತ್ತಳೆ ಪುಡಿ ಅಂಟಿದರೆ ತುಕ್ಕು ರೋಗವೆಂದು ದೃಢಪಡಿಸಬಹುದು."
            ],
            "organic": [
                "ಲಕ್ಷಣಗಳು ಕಂಡ ತಕ್ಷಣ 5% ಬೇವಿನ ಕಷಾಯ ಅಥವಾ 3% ಬೇವಿನ ಎಣ್ಣೆ ಸಿಂಪಡಿಸಿ."
            ],
            "chemical": [
                "ಹೆಕ್ಸಾಕೊನಜೋಲ್ 5% SC (2.0 ಮಿ.ಲೀ/ಲೀ; PHI 30 ದಿನ) ಅಥವಾ ಟೆಬುಕೊನಜೋಲ್ 25.9% EC (1.0-1.5 ಮಿ.ಲೀ/ಲೀ; PHI 49 ದಿನ) ಸಿಂಪಡಿಸಿ."
            ]
        },
        "nutrition_deficiency": {
            "display_name": "ಕಡಲೆಕಾಯಿಯಲ್ಲಿ ಪೋಷಕಾಂಶಗಳ ಕೊರತೆ (ಹಳದಿ ರೋಗ)",
            "scientific_name": "ಅಜೈವಿಕ ಪೋಷಕಾಂಶ ಕೊರತೆ (Arachis hypogaea)",
            "symptoms": [
                "ಕಬ್ಬಿಣದ ಕೊರತೆ: ಹೊಸ ಚಿಗುರೆಲೆಗಳ ನಾಳಗಳು ಹಸಿರಾಗಿದ್ದು ಮಧ್ಯದ ಭಾಗ ಹಳದಿಯಾಗುವುದು",
                "ಸತುವಿನ ಕೊರತೆ: ಗಿಡದ ಬೆಳವಣಿಗೆ ಕುಂಠಿತ, ಸಣ್ಣ ಎಲೆಗಳು",
                "ಸಾರಜನಕದ ಕೊರತೆ: ಹಳೆಯ ಕೆಳ ಎಲೆಗಳು ಸಂಪೂರ್ಣ ಹಳದಿಯಾಗುವುದು",
                "ಶಿಲೀಂಧ್ರದ ಚುಕ್ಕೆಗಳಾಗಲಿ, ಬೊಬ್ಬೆಗಳಾಗಲಿ ಇರುವುದಿಲ್ಲ"
            ],
            "prevention": [
                "ಬಿತ್ತನೆಗೆ ಮುನ್ನ ಮಣ್ಣು ಪರೀಕ್ಷೆ ಮಾಡಿಸಿ ಪೋಷಕಾಂಶಗಳನ್ನು ಒದಗಿಸಿ",
                "ಎಕರೆಗೆ 4-5 ಟನ್ ಕೊಳೆತ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ ಹಾಕಿ",
                "ಕ್ಯಾಲ್ಸಿಯಂ ಮತ್ತು ಗಂಧಕಕ್ಕಾಗಿ ಜಿಪ್ಸಮ್ (400-500 ಕೆಜಿ/ಹೆಕ್ಟೇರ್) ಹಾಕಿ",
                "ರೈಜೋಬಿಯಂ ಮತ್ತು ಪಿ.ಎಸ್.ಬಿ ಜೈವಿಕ ಗೊಬ್ಬರಗಳಿಂದ ಬೀಜೋಪಚಾರ ಮಾಡಿ"
            ],
            "causes": [
                "ಸುಣ್ಣದ ಅಂಶ ಹೆಚ್ಚಿರುವ ಮಣ್ಣಿನಲ್ಲಿ (pH > 7.5) ಕಬ್ಬಿಣ ಮತ್ತು ಸತು ಲಭ್ಯವಾಗದಿರುವುದು",
                "ನೀರು ನಿಲ್ಲುವುದು ಮತ್ತು ಅಸಮತೋಲನ ಗೊಬ್ಬರ ಬಳಕೆ"
            ],
            "limitations": [
                "ಕಬ್ಬಿಣದ ಕೊರತೆ ವೈರಸ್ ರೋಗದಂತೆ ಕಾಣಬಹುದು; ನಾಳಗಳು ಹಸಿರಾಗಿರುವುದು ಪೋಷಕಾಂಶ ಕೊರತೆಯ ಲಕ್ಷಣ.",
                "ಇದು ರೋಗವಲ್ಲ; ಶಿಲೀಂಧ್ರನಾಶಕಗಳು ಯಾವುದೇ ಪರಿಣಾಮ ಬೀರುವುದಿಲ್ಲ."
            ],
            "organic": [
                "ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ ಬಳಸಿ. ಸೆಣಬು ಅಥವಾ ಡಯಾಂಚ ಹಸಿರೆಲೆ ಗೊಬ್ಬರವನ್ನು ಮಣ್ಣಿಗೆ ಸೇರಿಸಿ."
            ],
            "chemical": [
                "ಶಿಲೀಂಧ್ರನಾಶಕ ಸಿಂಪಡಿಸಬೇಡಿ. ಕಬ್ಬಿಣದ ಕೊರತೆಗೆ ಅನ್ನಭೇದಿ (5 ಗ್ರಾಂ/ಲೀ) + ನಿಂಬೆ ಉಪ್ಪು (1 ಗ್ರಾಂ/ಲೀ); ಸತುವಿನ ಕೊರತೆಗೆ ಜಿಂಕ್ ಸಲ್ಫೇಟ್ (5 ಗ್ರಾಂ/ಲೀ) ಸಿಂಪಡಿಸಿ."
            ]
        },
        "healthy": {
            "display_name": "ಆರೋಗ್ಯಕರ ಕಡಲೆಕಾಯಿ ಗಿಡ",
            "scientific_name": "ಅರಾಚಿಸ್ ಹೈಪೋಜಿಯಾ (Arachis hypogaea - Healthy)",
            "symptoms": [
                "ಹಸಿರಾದ ಗಿಡ ಮತ್ತು ಎಲೆಗಳ ಸಾಮಾನ್ಯ ಬೆಳವಣಿಗೆ",
                "ಯಾವುದೇ ಚುಕ್ಕೆಗಳು, ತುಕ್ಕು ಅಥವಾ ಹಳದಿ ರೋಗವಿಲ್ಲದಿರುವುದು",
                "ಸಾಮಾನ್ಯ ಹೂವಾಡುವಿಕೆ ಮತ್ತು ಕಾಯಿ ಕಟ್ಟುವಿಕೆ"
            ],
            "prevention": [
                "ಮಣ್ಣು ಪರೀಕ್ಷೆ ಆಧಾರದ ಮೇಲೆ ಸಮತೋಲಿತ ರಸಗೊಬ್ಬರಗಳನ್ನು ನೀಡಿ",
                "ಕಾಯಿ ಕಟ್ಟುವ ಹಂತದಲ್ಲಿ ಜಿಪ್ಸಮ್ ಒದಗಿಸಿ",
                "ನಿಯಮಿತವಾಗಿ ಕೀಟ ಮತ್ತು ರೋಗಗಳಿಗಾಗಿ ಹೊಲವನ್ನು ಪರಿಶೀಲಿಸಿ"
            ],
            "causes": [],
            "limitations": [
                "ಪ್ರಸ್ತುತ ಗಿಡವು ಸಂಪೂರ್ಣ ರೋಗಮುಕ್ತವಾಗಿದೆ.",
                "ಹವಾಮಾನ ಬದಲಾದಂತೆ ನಿಯಮಿತ ನಿಗಾ ಇರಿಸಿ."
            ],
            "organic": [
                "ಸಾವಯವ ಗೊಬ್ಬರಗಳನ್ನು ಬಳಸಿ ಮತ್ತು ಉಪಕಾರಿ ಕೀಟಗಳನ್ನು ರಕ್ಷಿಸಿ."
            ],
            "chemical": [
                "ಆರೋಗ್ಯಕರ ಬೆಳೆಗೆ ಯಾವುದೇ ರಾಸಾಯನಿಕ ಸಿಂಪಡಣೆ ಅಗತ್ಯವಿಲ್ಲ."
            ]
        }
    }
}

UI_UPDATES = {
    "en": {
        "crop_groundnut": "Groundnut / Peanut",
        "all_crops": "All Crops (Paddy, Maize & Groundnut)",
    },
    "te": {
        "crop_groundnut": "వేరుశనగ",
        "all_crops": "అన్ని పంటలు (వరి, మొక్కజొన్న & వేరుశనగ)",
    },
    "hi": {
        "crop_groundnut": "मूंगफली",
        "all_crops": "सभी फसलें (धान, मक्का और मूंगफली)",
    },
    "ta": {
        "crop_groundnut": "நிலக்கடலை",
        "all_crops": "அனைத்து பயிர்கள் (நெல், மக்காச்சோளம் & நிலக்கடலை)",
    },
    "kn": {
        "crop_groundnut": "ಕಡಲೆಕಾಯಿ",
        "all_crops": "ಎಲ್ಲಾ ಬೆಳೆಗಳು (ಭತ್ತ, ಮೆಕ್ಕೆಜೋಳ & ಕಡಲೆಕಾಯಿ)",
    },
}


def update_translations():
    with open(TRANSLATIONS_JSON, "r", encoding="utf-8") as f:
        t = json.load(f)

    # 1. Update UI keys
    for lang, kvs in UI_UPDATES.items():
        if lang in t.get("ui", {}):
            for k, v in kvs.items():
                t["ui"][lang][k] = v

    # 2. Update disease translations
    for lang, dis_dict in GROUNDNUT_TRANSLATIONS.items():
        if lang not in t.get("diseases", {}):
            t["diseases"][lang] = {}
        for dis_id, content in dis_dict.items():
            t["diseases"][lang][dis_id] = content

    with open(TRANSLATIONS_JSON, "w", encoding="utf-8") as f:
        json.dump(t, f, indent=2, ensure_ascii=False)

    print("Successfully updated translations.json for all 5 languages!")


if __name__ == "__main__":
    update_translations()
