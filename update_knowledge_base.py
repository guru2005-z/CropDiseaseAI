"""
Helper script to update disease_data/diseases.json and disease_data/translations.json
with scientifically validated Maize knowledge and translations across TE, HI, TA, KN.
Preserves all 13 existing Paddy records intact.
"""
import json
from pathlib import Path

root = Path(__file__).resolve().parent

diseases_file = root / "disease_data" / "diseases.json"
translations_file = root / "disease_data" / "translations.json"

# ----------------------------------------------------
# 1. Update diseases.json
# ----------------------------------------------------
with diseases_file.open("r", encoding="utf-8") as f:
    diseases_data = json.load(f)

paddy_records = [r for r in diseases_data.get("diseases", []) if r.get("crop") == "paddy"]
print(f"Existing Paddy records found: {len(paddy_records)}")
assert len(paddy_records) == 13, f"Expected 13 Paddy records, found {len(paddy_records)}"

maize_records = [
    {
        "crop": "maize",
        "disease_id": "common_rust",
        "display_name": "Common Rust of Maize",
        "scientific_name": "Puccinia sorghi",
        "disease_type": "Fungal",
        "affected_parts": [
            "Leaf blades (upper and lower surfaces)",
            "Leaf sheaths",
            "Ear husks"
        ],
        "symptoms": [
            "Small, scattered circular to elongate golden-brown to cinnamon-brown powdery pustules (uredinia) erupting on both leaf surfaces",
            "Pustules darken to brownish-black late in the season as teleutospores form",
            "Severe infections lead to chlorosis, premature leaf death, and reduced kernel weight"
        ],
        "possible_causes": [
            "Airborne fungal urediniospores carried long distances by wind currents from warmer overwintering zones",
            "Moderate temperatures (16-25°C), high relative humidity (>95%), and extended leaf wetness (6+ hours of dew)"
        ],
        "prevention": [
            "Select high-yielding rust-resistant or tolerant corn hybrids adapted to the agro-ecological region",
            "Plant early in the season to evade peak spore showers and late-season infection windows",
            "Avoid excessive nitrogen fertilization that promotes overly lush, susceptible leaf canopy"
        ],
        "management": [
            "Regularly scout lower and middle canopy leaves from vegetative stage V8 through silking",
            "Prioritize intervention if pustules appear prior to tasseling/silking on susceptible hybrids"
        ],
        "organic_management": [
            "Seed treatment with Trichoderma harzianum or Bacillus subtilis to enhance systemic plant defense",
            "Foliar spray of 5% neem seed kernel extract (NSKE) or fermented butter-milk solution at early pustule detection"
        ],
        "chemical_management": [
            "Foliar fungicide application is warranted only when pustules appear prior to silking on susceptible hybrids under favorable cool, moist weather. Recommended labeled chemistries include Mancozeb 75% WP (2 g/L) or Azoxystrobin 18.2% + Difenoconazole 11.4% SC (1 mL/L). Always consult local agricultural extension officers and strictly follow registered container label safety instructions and pre-harvest intervals (PHI)."
        ],
        "severity_notes": "Can cause 10-25% yield reduction when early foliar blighting limits grain fill; distinguished from Southern Rust (Puccinia polysora) by pustules occurring equally on both leaf surfaces.",
        "source": "ICAR-Indian Institute of Maize Research (IIMR) & University Extension Crop Pathology Bulletins",
        "last_reviewed": "2026-11-17"
    },
    {
        "crop": "maize",
        "disease_id": "gray_leaf_spot",
        "display_name": "Gray Leaf Spot of Maize",
        "scientific_name": "Cercospora zeae-maydis",
        "disease_type": "Fungal",
        "affected_parts": [
            "Lower leaf blades initially, advancing upward to ear leaves and upper canopy",
            "Leaf sheaths"
        ],
        "symptoms": [
            "Initial pinpoint tan lesions with faint chlorotic haloes on lower leaves",
            "Lesions elongate into characteristic rectangular, vein-delimited tan to gray necrotic lesions (1-6 cm long)",
            "Lesions turn grayish when the fungus produces conidia under humid conditions",
            "Extensive lesion coalescence causes severe blighting, premature stalk lodging, and reduced ear fill"
        ],
        "possible_causes": [
            "Inoculum overwinters as mycelium and conidia on infected corn stover on the soil surface",
            "Warm, humid weather (25-32°C), high relative humidity (>90%), and recurring heavy morning dew or rainfall"
        ],
        "prevention": [
            "Practice crop rotation with non-cereal host crops (soybeans, pulses) for at least 1-2 seasons",
            "Manage crop residue through clean tillage where conservation practices permit to accelerate stover breakdown",
            "Plant hybrids with validated moderate to high genetic resistance to Gray Leaf Spot",
            "Avoid high planting densities that restrict airflow and prolong canopy humidity"
        ],
        "management": [
            "Scout leaves beginning 2-3 weeks before tasseling; monitor progression toward the ear leaf",
            "Improve field drainage and control grass weeds that can elevate microclimate humidity"
        ],
        "organic_management": [
            "Apply antagonistic biocontrol agents (Trichoderma asperellum or Bacillus amyloliquefaciens) to soil and residue",
            "Apply foliar bio-fungicides or neem formulations during early vegetative development to reduce spore viability"
        ],
        "chemical_management": [
            "Chemical control is economically justified when lesions reach the third leaf below the ear prior to silking in favorable weather on susceptible hybrids. Verified options include Propiconazole 25% EC (1 mL/L), Pyraclostrobin 20% WG (0.5 g/L), or Azoxystrobin 23% SC (1 mL/L). Consult local agricultural extension guidance and adhere strictly to product label rates, timing, and pre-harvest restrictions."
        ],
        "severity_notes": "A premier yield-limiting foliar disease in continuous corn systems; causes premature plant death and stalk rot.",
        "source": "ICAR-IIMR Disease Management Guide & CIMMYT Maize Pathology Manual",
        "last_reviewed": "2026-11-17"
    },
    {
        "crop": "maize",
        "disease_id": "northern_leaf_blight",
        "display_name": "Northern Corn Leaf Blight",
        "scientific_name": "Exserohilum turcicum (syn. Helminthosporium turcicum)",
        "disease_type": "Fungal",
        "affected_parts": [
            "Leaf blades",
            "Leaf sheaths",
            "Outer husks in severe cases"
        ],
        "symptoms": [
            "Large, elongated, elliptical or cigar-shaped grayish-green to tan necrotic lesions (3-15 cm long)",
            "Lesions have smooth margins with tapered ends, crossing parallel leaf veins without vein limitation",
            "Dark olive-green to black fungal spore mats develop on lesion centers during damp weather",
            "Complete leaf desiccation and burned appearance across the canopy in epidemic situations"
        ],
        "possible_causes": [
            "Fungal conidia surviving on infected maize residue splashed by rain or dispersed by wind onto lower leaves",
            "Moderate temperatures (18-27°C), heavy dews, frequent rain, and prolonged leaf wetness (6-12 hours)"
        ],
        "prevention": [
            "Cultivate adapted hybrids possessing specific Ht resistance genes (Ht1, Ht2, HtN) or quantitative polygenic resistance",
            "Implement 1 to 2-year crop rotation away from corn to diminish soil residue inoculum",
            "Ensure balanced potassium and nitrogen nutrition; avoid potassium deficiency which aggravates blight severity"
        ],
        "management": [
            "Routinely inspect lower canopy for cigar-shaped lesions from knee-high stage through grain fill",
            "Deeply incorporate crop residue post-harvest where agronomically appropriate"
        ],
        "organic_management": [
            "Seed treatment with Trichoderma viride (10 g/kg seed) or Pseudomonas fluorescens (10 g/kg seed)",
            "Foliar spray of botanical bio-extracts (5% NSKE) or bio-control agents (Bacillus subtilis) at initial symptom appearance"
        ],
        "chemical_management": [
            "When 2 to 3 lesions appear on leaves below the ear before silking under humid weather forecasts, apply recommended protectant/systemic fungicides such as Mancozeb 75% WP (2-2.5 g/L), Azoxystrobin 18.2% + Difenoconazole 11.4% SC (1 mL/L), or Propiconazole 25% EC (1 mL/L). Adhere strictly to regional agricultural university advisories, container label directions, and pre-harvest intervals."
        ],
        "severity_notes": "Diagnostic Label Uncertainty: Raw dataset label is abbreviated as 'Blight'. Provenance (PlantVillage) and visual morphology confirm Northern Corn Leaf Blight (Exserohilum turcicum); however, Southern Blight (Bipolaris maydis) and bacterial blights may produce overlapping foliar necrosis. Microscopic spore verification is recommended for ambiguous field samples.",
        "source": "ICAR-IIMR Maize Pathology Bulletin & CIMMYT / University Extension Plant Disease Guides",
        "last_reviewed": "2026-11-17"
    },
    {
        "crop": "maize",
        "disease_id": "healthy",
        "display_name": "Healthy Maize Plant",
        "scientific_name": "Zea mays (Healthy)",
        "disease_type": "None",
        "affected_parts": [],
        "symptoms": [
            "Uniform vibrant green leaves without chlorotic streaks, necrotic lesions, or pustules",
            "Strong, erect stalk with normal internode spacing and sturdy brace root development",
            "Normal vegetative and reproductive growth appropriate for hybrid phenological stage"
        ],
        "possible_causes": [],
        "prevention": [
            "Perform soil test-based balanced NPK fertilization with essential micronutrient (Zinc, Boron) supplementation",
            "Maintain optimal field drainage to prevent waterlogging, particularly during seedling and tasseling stages",
            "Conduct regular weekly scouting for invasive insect pests (e.g. Fall Armyworm) and early foliar spots",
            "Practice integrated weed management during the critical early crop competition window (first 30-45 days)"
        ],
        "management": [
            "Continue regular agronomic care, timely irrigation, and split application of nitrogen at knee-high and tasseling stages"
        ],
        "organic_management": [
            "Incorporate well-decomposed farmyard manure (FYM) or vermicompost to foster beneficial soil microflora",
            "Conserve beneficial natural predators (spiders, ladybird beetles, Trichogramma parasitoids) through ecological field borders"
        ],
        "chemical_management": [
            "None required for healthy crops"
        ],
        "severity_notes": "Not applicable - plant displays healthy vegetative and reproductive growth traits.",
        "source": "ICAR-Indian Institute of Maize Research (IIMR) & CIMMYT Maize Production Manual",
        "last_reviewed": "2026-11-17"
    }
]

diseases_data["diseases"] = paddy_records + maize_records

with diseases_file.open("w", encoding="utf-8") as f:
    json.dump(diseases_data, f, indent=2, ensure_ascii=False)

print(f"Successfully saved {diseases_file}! Total records: {len(diseases_data['diseases'])}")

# ----------------------------------------------------
# 2. Update translations.json
# ----------------------------------------------------
with translations_file.open("r", encoding="utf-8") as f:
    trans_data = json.load(f)

maize_translations = {
    "te": {
        "common_rust": {
            "display_name": "మొక్కజొన్న కుంకుమ తెగులు (కామన్ రస్ట్)",
            "symptoms": [
                "ఆకుల పై మరియు కింది భాగాలలో గుండ్రని లేదా పొడవాటి ఎరుపు-గోధుమ రంగు పొక్కులు (కుంకుమ మచ్చలు) ఏర్పడతాయి",
                "తీవ్రమైన దశలో ఈ పొక్కులు నల్లగా మారి ఆకులు ఎండిపోయి రాలిపోతాయి"
            ],
            "prevention": [
                "తెగులును తట్టుకునే రకాలను ఎంపిక చేసుకోండి",
                "సకాలంలో విత్తనం వేయడం ద్వారా తెగులు ఉధృతిని తగ్గించవచ్చు",
                "నత్రజని ఎరువులను అధికంగా వాడకుండా సమతుల్య ఎరువులు వేయండి"
            ],
            "organic": [
                "విత్తనశుద్ధి కోసం ట్రైకోడెర్మా హర్జియానం లేదా సుడోమోనాస్ వాడండి",
                "తెగులు ప్రారంభ దశలో 5% వేప గింజల కషాయం (NSKE) లేదా పులిసిన మజ్జిగ ద్రావణాన్ని పిచికారీ చేయండి"
            ],
            "chemical": [
                "తెగులు లక్షణాలు కనపడిన వెంటనే మాంకోజెబ్ 75% WP (2 గ్రా/లీ) లేదా అజోక్సీస్ట్రోబిన్ + డైఫెనోకోనజోల్ (1 మి.లీ/లీ) పిచికారీ చేయండి. సరైన మోతాదు మరియు సలహాల కోసం స్థానిక వ్యవసాయ విస్తరణాధికారిని సంప్రదించండి."
            ]
        },
        "gray_leaf_spot": {
            "display_name": "మొక్కజొన్న బూడిద రంగు ఆకుమచ్చ తెగులు (గ్రే లీఫ్ స్పాట్)",
            "symptoms": [
                "ఆకుల ఈనెల మధ్య దీర్ఘచతురస్రాకారంలో బూడిద లేదా గోధుమ రంగు మచ్చలు ఏర్పడతాయి",
                "మచ్చలు కలిసిపోయి ఆకులు పూర్తిగా ఎండిపోయి మొక్కలు త్వరగా చనిపోతాయి"
            ],
            "prevention": [
                "పంట మార్పిడి పద్ధతిని పాటించండి (పప్పుధాన్యాలు లేదా సోయాబీన్ తో మార్పిడి)",
                "గత పంట వ్యర్థాలను పొలంలో లేకుండా శుభ్రం చేయండి లేదా లోతు దుక్కి చేయండి",
                "తట్టుకునే హైబ్రిడ్ రకాలను సాగు చేయండి"
            ],
            "organic": [
                "ట్రైకోడెర్మా కల్చర్ తో మట్టి చికిత్స చేయండి",
                "బాసిల్లస్ సబ్టిలిస్ ఆధారిత జీవ శిలీంద్రనాశినులను పిచికారీ చేయండి"
            ],
            "chemical": [
                "ఆకులపై మచ్చలు గమనించినప్పుడు ప్రొపికోనజోల్ 25% EC (1 మి.లీ/లీ) లేదా అజోక్సీస్ట్రోబిన్ 23% SC (1 మి.లీ/లీ) పిచికారీ చేయండి. స్థానిక వ్యవసాయ అధికారి సూచనల ప్రకారం మందులను ఉపయోగించండి."
            ]
        },
        "northern_leaf_blight": {
            "display_name": "మొక్కజొన్న ఆకు ఎండు తెగులు (నార్తర్న్ లీఫ్ బ్లైట్)",
            "symptoms": [
                "ఆకులపై పొడవాటి చుట్ట ఆకారపు (సిగార్ ఆకారపు) బూడిద-గోధుమ రంగు మచ్చలు ఏర్పడతాయి",
                "మచ్చలు ఆకు ఈనెలతో సంబంధం లేకుండా వేగంగా విస్తరించి ఆకులను మాడ్చివేస్తాయి (కాలినట్లు కనిపిస్తాయి)"
            ],
            "prevention": [
                "Ht జన్యువులు కలిగిన తెగులును తట్టుకునే హైబ్రిడ్ విత్తనాలను ఎంచుకోండి",
                "పంట మార్పిడి పాటించండి మరియు సమతుల్య పొటాష్ ఎరువులను అందించండి",
                "గమనిక: ఇతర ఆకు ఎండు తెగుళ్ల (సదరన్ బ్లైట్) లక్షణాలు కూడా ఇలాగే ఉండవచ్చు; అనుమానం ఉంటే నిపుణులను సంప్రదించండి"
            ],
            "organic": [
                "ట్రైకోడెర్మా విరిడేతో విత్తనశుద్ధి (10 గ్రా/కిలో విత్తనం) చేయండి",
                "వేప నూనె లేదా జీవ శిలీంద్రనాశినులను మొలక దశ నుండి పిచికారీ చేయండి"
            ],
            "chemical": [
                "తెగులు ఉధృతి ఎక్కువగా ఉన్నప్పుడు మాంకోజెబ్ (2-2.5 గ్రా/లీ) లేదా అజోక్సీస్ట్రోబిన్ + డైఫెనోకోనజోల్ (1 మి.లీ/లీ) పిచికారీ చేయండి. లేబుల్ సూచనలు మరియు స్థానిక వ్యవసాయ సలహాలను పాటించండి."
            ]
        },
        "healthy": {
            "display_name": "ఆరోగ్యకరమైన మొక్కజొన్న మొక్క",
            "symptoms": [
                "ఆకులు ఎటువంటి మచ్చలు, కుంకుమ పొక్కులు లేకుండా పచ్చగా, బలంగా ఉంటాయి",
                "మొక్క కాండం బలంగా ఉండి సాధారణ ఎదుగుదల కనబరుస్తుంది"
            ],
            "prevention": [
                "మట్టి పరీక్ష ఆధారంగా సమతుల్య ఎరువులు (NPK మరియు జింక్) అందించండి",
                "పొలంలో నీరు నిల్వ ఉండకుండా మురుగు నీటి కాల్వలను నిర్వహించండి",
                "క్రమం తప్పకుండా తెగుళ్లు, పురుగుల (కత్తెర పురుగు) కోసం పొలాన్ని పరిశీలించండి"
            ],
            "organic": [
                "నాణ్యమైన పశువుల ఎరువు లేదా వర్మీకంపోస్ట్ ను నేలకు అందించండి",
                "మిత్రపురుగులను కాపాడుకోండి"
            ],
            "chemical": [
                "ఆరోగ్యకరమైన పంటకు ఎటువంటి రసాయన మందులు అవసరం లేదు."
            ]
        }
    },
    "hi": {
        "common_rust": {
            "display_name": "मक्का का सामान्य रतुआ (कॉमन रस्ट)",
            "symptoms": [
                "पत्तियों की दोनों सतहों पर छोटे, गोल से लेकर लंबे लाल-भूरे रंग के उभरे हुए फफोले (रस्ट पुस्ट्यूल) दिखाई देते हैं",
                "रोग बढ़ने पर यह फफोले भूरे-काले रंग में बदल जाते हैं और पत्तियां सूखने लगती हैं"
            ],
            "prevention": [
                "रोग प्रतिरोधी या सहनशील मक्का की संकर किस्मों का चयन करें",
                "समय पर बुवाई करें ताकि फफूंद के बीजाणुओं के प्रसार से बचा जा सके",
                "संतुलित मात्रा में उर्वरकों का उपयोग करें; अत्यधिक नाइट्रोजन से बचें"
            ],
            "organic": [
                "ट्राइकोडर्मा हरजिएनम से बीज उपचार करें",
                "प्रारंभिक अवस्था में 5% नीम के बीज के अर्क (NSKE) या खट्टी छाछ का छिड़काव करें"
            ],
            "chemical": [
                "रोग के लक्षण दिखाई देने पर मैंकोजेब 75% WP (2 ग्राम/लीटर) या एजोक्सीस्ट्रोबिन + डाइफेनोकोनाजोल (1 मिली/लीटर) का छिड़काव करें। अनुमोदित मात्रा के लिए स्थानीय कृषि प्रसार अधिकारी से सलाह लें।"
            ]
        },
        "gray_leaf_spot": {
            "display_name": "मक्का का ग्रे लीफ स्पॉट (धूसर पत्ती धब्बा)",
            "symptoms": [
                "पत्तियों की नसों के बीच आयताकार (रेक्टैंगुलर) भूरे या धूसर रंग के लंबे धब्बे बनते हैं",
                "धब्बे आपस में मिलकर पूरी पत्ती को सुखा देते हैं, जिससे पौधे कमजोर होकर गिर सकते हैं"
            ],
            "prevention": [
                "दलहनी फसलों या सोयाबीन के साथ फसल चक्र (क्रॉप रोटेशन) अपनाएं",
                "पिछली फसल के अवशेषों को नष्ट करें या गहरी जुताई करें",
                "सहनशील संकर बीजों की बुवाई करें"
            ],
            "organic": [
                "ट्राइकोडर्मा आधारित जैविक फफूंदनाशियों का प्रयोग करें",
                "स्यूडोमोनास फ्लोरेसेंस का छिड़काव करें"
            ],
            "chemical": [
                "पत्तियों पर आयताकार धब्बे दिखने पर प्रोपिकोनाजोल 25% EC (1 मिली/लीटर) या एजोक्सीस्ट्रोबिन 23% SC (1 मिली/लीटर) का छिड़काव करें। उत्पाद लेबल के निर्देशों का पालन करें।"
            ]
        },
        "northern_leaf_blight": {
            "display_name": "मक्का का उत्तरी पत्ती झुलसा (नार्दर्न लीफ ब्लाइट)",
            "symptoms": [
                "पत्तियों पर लंबे, सिगार के आकार के (नाव जैसे) धूसर-हरे से भूरे रंग के बड़े धब्बे बनते हैं",
                "धब्बे नसों की सीमा को पार करते हुए तेजी से फैलते हैं और पत्तियां झुलसी हुई नजर आती हैं"
            ],
            "prevention": [
                "Ht जीन युक्त रोग प्रतिरोधी किस्मों की बुवाई करें",
                "फसल चक्र अपनाएं और संतुलित पोटाश व नाइट्रोजन उर्वरक दें",
                "नोट: अन्य झुलसा रोगों (जैसे साउदर्न ब्लाइट) के लक्षण भी मिलते-जुलते हो सकते हैं; संदेह होने पर कृषि विशेषज्ञ से पुष्टि करें"
            ],
            "organic": [
                "ट्राइकोडर्मा विरिडी (10 ग्राम/किग्रा बीज) से बीज शोधन करें",
                "नीम तेल या जैविक कवकनाशी का छिड़काव करें"
            ],
            "chemical": [
                "गंभीर संक्रमण होने पर मैंकोजेब (2-2.5 ग्राम/लीटर) या एजोक्सीस्ट्रोबिन + डाइफेनोकोनाजोल (1 मिली/लीटर) का छिड़काव करें। कृषि विश्वविद्यालय की सलाह का पालन करें।"
            ]
        },
        "healthy": {
            "display_name": "स्वस्थ मक्का का पौधा",
            "symptoms": [
                "पत्तियां किसी भी प्रकार के धब्बे या फफूंद से मुक्त, चमकदार हरी और मजबूत होती हैं",
                "पौधे का तना मजबूत और सामान्य वानस्पतिक विकास प्रदर्शित करता है"
            ],
            "prevention": [
                "मृदा परीक्षण के आधार पर संतुलित NPK और जिंक खाद का प्रयोग करें",
                "खेत में जलभराव न होने दें और उचित जल निकासी की व्यवस्था रखें",
                "कीटों (जैसे फॉल आर्मीवॉर्म) और रोगों की समय-समय पर निगरानी करें"
            ],
            "organic": [
                "अच्छी तरह सड़ी गोबर की खाद या वर्मीकम्पोस्ट का प्रयोग करें",
                "लाभकारी कीटों का संरक्षण करें"
            ],
            "chemical": [
                "स्वस्थ फसल में किसी रासायनिक कीटनाशक या फफूंदनाशक के छिड़काव की आवश्यकता नहीं है।"
            ]
        }
    },
    "ta": {
        "common_rust": {
            "display_name": "மக்காச்சோள பொது துரு நோய் (காமன் ரஸ்ட்)",
            "symptoms": [
                "இலைகளின் மேல் மற்றும் கீழ் பரப்புகளில் சிறிய, வட்டமான செம்பழுப்பு நிற கொப்புளங்கள் தோன்றும்",
                "முதிர்ந்த நிலையில் இந்த கொப்புளங்கள் கருப்பாக மாறி இலைகள் காய்ந்துவிடும்"
            ],
            "prevention": [
                "நோய் எதிர்ப்புத்திறன் கொண்ட கலப்பின விதைகளை பயிரிடுங்கள்",
                "பருவத்தில் சரியான நேரத்தில் விதைப்பு செய்யுங்கள்",
                "தழைச்சத்தை (நைட்ரஜன்) அளவுக்கு அதிகமாக இடுவதைத் தவிர்க்கவும்"
            ],
            "organic": [
                "டிரைக்கோடெர்மா ஹார்சியானம் கொண்டு விதை நேர்த்தி செய்யுங்கள்",
                "5% வேப்பங்கொட்டை சாறு (NSKE) தெளிக்கவும்"
            ],
            "chemical": [
                "துரு நோய் தென்பட்டால் மேன்கோசெப் 75% WP (2 கிராம்/லிட்டர்) அல்லது அசாசிஸ்ட்ரோபின் + டைபனோகோனசோல் (1 மி.லி/லிட்டர்) தெளிக்கவும். வட்டார வேளாண் விரிவாக்க அலுவலரை அணுகவும்."
            ]
        },
        "gray_leaf_spot": {
            "display_name": "மக்காச்சோள சாம்பல் இலைப்புள்ளி நோய் (கிரே லீப் ஸ்பாட்)",
            "symptoms": [
                "இலை நரம்புகளுக்கு இடையே செவ்வக வடிவிலான சாம்பல் அல்லது பழுப்பு நிற புள்ளிகள் தோன்றும்",
                "புள்ளிகள் ஒன்றுசேர்ந்து இலைகளை முற்றிலும் கருகச் செய்யும்"
            ],
            "prevention": [
                "பயறு வகைகளுடன் பயிர் சுழற்சி முறையை கடைப்பிடிக்கவும்",
                "பயிர்க் கழிவுகளை அகற்றவும் அல்லது ஆழ உழவு செய்யவும்"
            ],
            "organic": [
                "சூடோமோனாஸ் புளோரசன்ஸ் அல்லது பேசிலஸ் கொண்டு தெளிக்கவும்"
            ],
            "chemical": [
                "புள்ளிகள் தென்படும்போது புரோபிகோனசோல் 25% EC (1 மி.லி/லிட்டர்) அல்லது அசாசிஸ்ட்ரோபின் 23% SC (1 மி.லி/லிட்டர்) தெளிக்கவும்."
            ]
        },
        "northern_leaf_blight": {
            "display_name": "மக்காச்சோள வடக்கு இலை கருகல் நோய் (நார்தர்ன் லீப் பிளைட்)",
            "symptoms": [
                "இலைகளில் நீண்ட படகு அல்லது சுருட்டு வடிவ சாம்பல்-பழுப்பு நிற பெரிய கருகல் புள்ளிகள் தோன்றும்",
                "இலைகள் தீய்ந்தது போல் காட்சியளிக்கும்"
            ],
            "prevention": [
                "எதிர்ப்புத்திறன் கொண்ட ரகங்களை தேர்வு செய்யவும்",
                "சமச்சீர் உர மேலாண்மை மற்றும் சாம்பல் சத்து (பொட்டாஷ்) இடவும்",
                "குறிப்பு: பிற இலை கருகல் நோய்களும் இதே போன்ற அறிகுறிகளை வெளிப்படுத்தலாம்; கள ஆய்வு செய்யவும்"
            ],
            "organic": [
                "டிரைக்கோடெர்மா விரிடி (10 கிராம்/கிலோ விதை) கொண்டு விதை நேர்த்தி செய்யவும்"
            ],
            "chemical": [
                "நோய் தீவிரமடையும் போது மேன்கோசெப் (2-2.5 கிராம்/லிட்டர்) தெளிக்கவும். வேளாண் வழிகாட்டுதல்களைப் பின்பற்றவும்."
            ]
        },
        "healthy": {
            "display_name": "ஆரோக்கியமான மக்காச்சோள பயிர்",
            "symptoms": [
                "இலைகளில் எவ்வித புள்ளிகளும் இல்லாமல் பசுமையாகவும் ஆரோக்கியமாகவும் இருக்கும்",
                "தண்டு உறுதியாகவும் முறையான வளர்ச்சியுடனும் காணப்படும்"
            ],
            "prevention": [
                "மண் பரிசோதனை அடிப்படையில் சமச்சீர் உரம் இடவும்",
                "பாசன நீர் தேங்காமல் வடிகால் வசதி அமைக்கவும்",
                "வழக்கமான கள ஆய்வு மேற்கொள்ளவும்"
            ],
            "organic": [
                "மட்கிய தொழுவுரம் அல்லது மண்புழு உரம் இடவும்"
            ],
            "chemical": [
                "ஆரோக்கியமான பயிர்களுக்கு எந்தவொரு ரசாயன தெளிப்பும் தேவையில்லை."
            ]
        }
    },
    "kn": {
        "common_rust": {
            "display_name": "ಮೆಕ್ಕೆಜೋಳದ ತುಕ್ಕು ರೋಗ (ಕಾಮನ್ ರಸ್ಟ್)",
            "symptoms": [
                "ಎಲೆಗಳ ಎರಡೂ ಬದಿಗಳಲ್ಲಿ ಸಣ್ಣ, ದುಂಡಗಿನ ಅಥವಾ ಉದ್ದನೆಯ ಕೆಂಪು-ಕಂದು ಬಣ್ಣದ ಪುಡಿ ತುಂಬಿದ ಗುಳ್ಳೆಗಳು ಕಾಣಿಸಿಕೊಳ್ಳುತ್ತವೆ",
                "ರೋಗ ಉಲ್ಬಣಿಸಿದಾಗ ಗುಳ್ಳೆಗಳು ಕಪ್ಪು ಬಣ್ಣಕ್ಕೆ ತಿರುಗಿ ಎಲೆಗಳು ಒಣಗುತ್ತವೆ"
            ],
            "prevention": [
                "ರೋಗ ನಿರೋಧಕ ತಳಿಗಳನ್ನು ಆಯ್ಕೆ ಮಾಡಿ",
                "ಸಕಾಲದಲ್ಲಿ ಬಿತ್ತನೆ ಮಾಡಿ ಮತ್ತು ಸಾರಜನಕ ಗೊಬ್ಬರದ ಅತಿಯಾದ ಬಳಕೆಯನ್ನು ತಪ್ಪಿಸಿ"
            ],
            "organic": [
                "ಟ್ರೈಕೋಡರ್ಮಾ ಮೂಲಕ ಬೀಜೋಪಚಾರ ಮಾಡಿ",
                "ಆರಂಭಿಕ ಹಂತದಲ್ಲಿ 5% ಬೇವಿನ ಬೀಜದ ಕಷಾಯ (NSKE) ಸಿಂಪಡಿಸಿ"
            ],
            "chemical": [
                "ರೋಗದ ಲಕ್ಷಣಗಳು ಕಂಡಾಗ ಮ್ಯಾಂಕೋಜೆಬ್ 75% WP (2 ಗ್ರಾಂ/ಲೀಟರ್) ಅಥವಾ ಅಜೋಕ್ಸಿಸ್ಟ್ರೋಬಿನ್ + ಡೈಫೆನೊಕೊನಾಜೋಲ್ (1 ಮಿ.ಲೀ/ಲೀಟರ್) ಸಿಂಪಡಿಸಿ. ಸ್ಥಳೀಯ ಕೃಷಿ ಅಧಿಕಾರಿಗಳ ಮಾರ್ಗದರ್ಶನ ಪಡೆಯಿರಿ."
            ]
        },
        "gray_leaf_spot": {
            "display_name": "ಮೆಕ್ಕೆಜೋಳದ ಬೂದು ಎಲೆ ಚುಕ್ಕೆ ರೋಗ (ಗ್ರೇ ಲೀಫ್ ಸ್ಪಾಟ್)",
            "symptoms": [
                "ಎಲೆಯ ನರಗಳ ನಡುವೆ ಆಯತಾಕಾರದ ಬೂದು ಅಥವಾ ಕಂದು ಬಣ್ಣದ ಚುಕ್ಕೆಗಳು ಉಂಟಾಗುತ್ತವೆ",
                "ಚುಕ್ಕೆಗಳು ಒಟ್ಟಾಗಿ ಹರಡಿ ಇಡೀ ಎಲೆಯು ಒಣಗಿ ಹೋಗುತ್ತದೆ"
            ],
            "prevention": [
                "ದ್ವಿದಳ ಧಾನ್ಯಗಳೊಂದಿಗೆ ಬೆಳೆ ಪರಿವರ್ತನೆ (ಬೆಳೆ ಸರದಿ) ಮಾಡಿ",
                "ಹಿಂದಿನ ಬೆಳೆಯ ಉಳಿಕೆಗಳನ್ನು ಆಳವಾಗಿ ಉಳುಮೆ ಮಾಡಿ ಮಣ್ಣಿನಲ್ಲಿ ಸೇರಿಸಿ"
            ],
            "organic": [
                "ಸ್ಯೂಡೋಮೊನಾಸ್ ಫ್ಲೋರೊಸೆನ್ಸ್ ಜೈವಿಕ ಶಿಲೀಂಧ್ರನಾಶಕವನ್ನು ಸಿಂಪಡಿಸಿ"
            ],
            "chemical": [
                "ಚುಕ್ಕೆಗಳು ಕಂಡಾಗ ಪ್ರೊಪಿಕೊನಾಜೋಲ್ 25% EC (1 ಮಿ.ಲೀ/ಲೀಟರ್) ಅಥವಾ ಅಜೋಕ್ಸಿಸ್ಟ್ರೋಬಿನ್ 23% SC (1 ಮಿ.ಲೀ/ಲೀಟರ್) ಸಿಂಪಡಿಸಿ."
            ]
        },
        "northern_leaf_blight": {
            "display_name": "ಮೆಕ್ಕೆಜೋಳದ ಉತ್ತರದ ಎಲೆ ಸುಟ್ಟ ರೋಗ (ನಾರ್ದರ್ನ್ ಲೀಫ್ ಬ್ಲೈಟ್)",
            "symptoms": [
                "ಎಲೆಗಳ ಮೇಲೆ ಉದ್ದನೆಯ ಸುರುಳಿ (ಸಿಗಾರ್) ಆಕಾರದ ಬೂದು-ಕಂದು ಬಣ್ಣದ ದೊಡ್ಡ ಕಲೆಗಳು ಉಂಟಾಗುತ್ತವೆ",
                "ಎಲೆಗಳು ಸುಟ್ಟಂತೆ ಒಣಗಿ ಇಳುವರಿ ಕಡಿಮೆಯಾಗುತ್ತದೆ"
            ],
            "prevention": [
                "ರೋಗ ನಿರೋಧಕ ಶಕ್ತಿಯುಳ್ಳ ಹೈಬ್ರಿಡ್ ತಳಿಗಳನ್ನು ಬೆಳೆಯಿರಿ",
                "ಪೊಟ್ಯಾಷ್ ಗೊಬ್ಬರವನ್ನು ಸಮತೋಲನದಲ್ಲಿ ನೀಡಿ",
                "ಗಮನಿಸಿ: ಇತರ ಎಲೆ ರೋಗಗಳ ಲಕ್ಷಣಗಳೂ ಹೀಗೆಯೇ ಇರಬಹುದು; ಸಂದೇಹವಿದ್ದರೆ ಕೃಷಿ ತಜ್ಞರನ್ನು ಸಂಪರ್ಕಿಸಿ"
            ],
            "organic": [
                "ಟ್ರೈಕೋಡರ್ಮಾ ವಿರಿಡೆ (10 ಗ್ರಾಂ/ಕೆಜಿ ಬೀಜ) ಯಿಂದ ಬೀಜೋಪಚಾರ ಮಾಡಿ"
            ],
            "chemical": [
                "ತೀವ್ರ ಹಂತದಲ್ಲಿ ಮ್ಯಾಂಕೋಜೆಬ್ (2-2.5 ಗ್ರಾಂ/ಲೀಟರ್) ಸಿಂಪಡಿಸಿ. ಶಿಫಾರಸು ಮಾಡಿದ ಪ್ರಮಾಣವನ್ನು ಮಾತ್ರ ಬಳಸಿ."
            ]
        },
        "healthy": {
            "display_name": "ಆರೋಗ್ಯಕರ ಮೆಕ್ಕೆಜೋಳದ ಸಸ್ಯ",
            "symptoms": [
                "ಎಲೆಗಳು ಯಾವುದೇ ಚುಕ್ಕೆ ಅಥವಾ ಗುಳ್ಳೆಗಳಿಲ್ಲದೆ ದಟ್ಟ ಹಸಿರಾಗಿದ್ದು ಬಲಿಷ್ಠವಾಗಿರುತ್ತವೆ",
                "ಕಾಂಡವು ಗಟ್ಟಿಯಾಗಿದ್ದು ಸಮರ್ಪಕ ಬೆಳವಣಿಗೆ ಹೊಂದಿರುತ್ತದೆ"
            ],
            "prevention": [
                "ಮಣ್ಣು ಪರೀಕ್ಷೆಯ ಆಧಾರದ ಮೇಲೆ ಸಮತೋಲಿತ ಗೊಬ್ಬರ (NPK ಮತ್ತು ಸತು) ನೀಡಿ",
                "ಜಮೀನಿನಲ್ಲಿ ನೀರು ನಿಲ್ಲದಂತೆ ಉತ್ತಮ ಬಸಿಗಾಲುವೆ ವ್ಯವಸ್ಥೆ ಕಲ್ಪಿಸಿ",
                "ನಿಯಮಿತವಾಗಿ ಬೆಳೆ ಪರಿಶೀಲನೆ ನಡೆಸಿ"
            ],
            "organic": [
                "ಉತ್ತಮವಾಗಿ ಕಳಿತ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ ಅಥವಾ ಎರೆಹುಳು ಗೊಬ್ಬರ ಬಳಸಿ"
            ],
            "chemical": [
                "ಆರೋಗ್ಯಕರ ಬೆಳೆಗೆ ಯಾವುದೇ ರಾಸಾಯನಿಕ ಔಷಧಿ ಸಿಂಪಡಣೆ ಅಗತ್ಯವಿಲ್ಲ."
            ]
        }
    }
}

for lang, classes in maize_translations.items():
    if lang not in trans_data["diseases"]:
        trans_data["diseases"][lang] = {}
    for cls_id, data in classes.items():
        trans_data["diseases"][lang][cls_id] = data

with translations_file.open("w", encoding="utf-8") as f:
    json.dump(trans_data, f, indent=2, ensure_ascii=False)

print(f"Successfully saved {translations_file}!")
print("Knowledge base update complete.")

