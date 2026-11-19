"""Populate Banana and Wheat records into:
1. disease_data/diseases.json
2. disease_data/translations.json (en, te, hi, ta, kn)
3. config/crops.json
"""

import json
from pathlib import Path

ROOT = Path(".")

# 1. New disease entries for disease_data/diseases.json
NEW_DISEASES = [
    # --- BANANA ---
    {
        "crop": "banana",
        "disease_id": "cordana_leaf_spot",
        "display_name": "Cordana Leaf Spot of Banana",
        "scientific_name": "Cordana musae",
        "disease_type": "Fungal",
        "affected_parts": ["Leaves"],
        "symptoms": [
            "Large oval or diamond-shaped pale brown lesions with prominent bright yellow halo borders",
            "Lesions typically start along the leaf margins and expand inward with faint concentric zonations",
            "Under humid conditions, grayish-brown velvety fungal sporulation develops on the underside of necrotic spots"
        ],
        "possible_causes": [
            "Prolonged leaf wetness and warm temperatures (24-30°C)",
            "Poor field drainage and dense unpruned plantation canopies"
        ],
        "prevention": [
            "Maintain optimal plant spacing (1.8 x 1.8 m or 2.1 x 2.1 m) to improve canopy aeration",
            "Regular desuckering and removal of dead hanging leaves to reduce humidity",
            "Ensure proper surface and sub-surface soil drainage during monsoon seasons"
        ],
        "management": [
            "Prune and safely burn or bury heavily spotted lower leaves before fungal sporulation",
            "Apply foliar protective sprays during early monsoon or initial symptom detection"
        ],
        "organic_management": [
            "Foliar spray of Copper Oxychloride 50% WP @ 2.5 g/L with sticker",
            "Spray Pseudomonas fluorescens @ 10 g/L or Trichoderma viride @ 5 g/L",
            "Neem seed kernel extract (NSKE 5%) or 1% horticultural mineral oil spray"
        ],
        "chemical_management": [
            "Mancozeb 75% WP @ 2.5 g/L or Chlorothalonil 75% WP @ 2.0 g/L at early lesion appearance",
            "Propiconazole 25% EC @ 1.0 ml/L or Difenoconazole 25% EC @ 1.0 ml/L; observe 21-day PHI"
        ],
        "severity_notes": "Cordana leaf spot causes significant functional photosynthetic area loss in banana plantations during rainy seasons, leading to smaller bunch sizes.",
        "source": "ICAR-NRCB National Research Centre for Banana / FAO Banana Compendium",
        "last_reviewed": "2026-11-19"
    },
    {
        "crop": "banana",
        "disease_id": "healthy",
        "display_name": "Healthy Banana Plant",
        "scientific_name": "Musa acuminata / Musa balbisiana (Healthy)",
        "disease_type": "None",
        "affected_parts": [],
        "symptoms": [
            "Broad, erect, glossy emerald green leaves without necrotic lesions or chlorosis",
            "Sturdy pseudostem with clean sheath overlap and vigorous continuous bunch emergence",
            "Well-anchored root system with active white feeder rootlets"
        ],
        "possible_causes": [],
        "prevention": [
            "Balanced fertigation scheduling (N-P-K based on tissue and soil testing)",
            "Regular desuckering keeping only one mother plant and one selected follower ratoon",
            "Mulching around pseudostem base to conserve moisture and regulate root temperature"
        ],
        "management": [
            "Continue standard agronomic practices, weed management, and periodic pest monitoring"
        ],
        "organic_management": [
            "Apply well-decomposed FYM (20 kg/plant) or vermicompost (5 kg/plant) with biofertilizers (Azospirillum, PSB)"
        ],
        "chemical_management": [
            "None required for healthy crops"
        ],
        "severity_notes": "Not applicable - plant displays vigorous healthy vegetative growth.",
        "source": "ICAR-NRCB Banana Package of Practices",
        "last_reviewed": "2026-11-19"
    },
    {
        "crop": "banana",
        "disease_id": "pestalotiopsis_leaf_spot",
        "display_name": "Pestalotiopsis Leaf Spot of Banana",
        "scientific_name": "Pestalotiopsis palmarum (Pestalotiopsis microspora)",
        "disease_type": "Fungal",
        "affected_parts": ["Leaves", "Leaf Tips"],
        "symptoms": [
            "Small yellowish or reddish-brown circular spots expanding into irregular bleached grayish-white lesions",
            "Dark brown to black raised margin separating diseased necrotic tissue from green blade",
            "Tiny black punctiform pustules (acervuli) visible under hand lens on the bleached central zone"
        ],
        "possible_causes": [
            "Opportunistic fungal colonization following wind damage, mechanical bruising, or insect punctures",
            "Persistent high relative humidity (>85%) and temperature between 22°C and 28°C"
        ],
        "prevention": [
            "Erect windbreaks around banana plantations to prevent wind tear and mechanical leaf tearing",
            "Avoid damaging foliage during weeding and de-suckering operations",
            "Maintain soil potassium levels to strengthen epidermal leaf cell walls"
        ],
        "management": [
            "Sanitize canopy by cutting off dried necrotic leaf tips and diseased leaves",
            "Ensure rapid canopy drying by pruning unproductive side suckers"
        ],
        "organic_management": [
            "Copper Hydroxide 77% WP @ 2.0 g/L or Bordeaux mixture 1% spray",
            "Foliar spray of Bacillus subtilis biocontrol formulations @ 5 g/L"
        ],
        "chemical_management": [
            "Chlorothalonil 75% WP @ 2.0 g/L or Mancozeb 75% WP @ 2.5 g/L",
            "Carbendazim 50% WP @ 1.0 g/L or Tebuconazole 25.9% EC @ 1.0 ml/L for advancing infections"
        ],
        "severity_notes": "Pestalotiopsis weakens functional leaf surface and accelerates premature senescence, especially when combined with wind damage.",
        "source": "ICAR-NRCB Tiruchirappalli Technical Manual / CABI Crop Protection",
        "last_reviewed": "2026-11-19"
    },
    {
        "crop": "banana",
        "disease_id": "sigatoka_leaf_spot",
        "display_name": "Sigatoka Leaf Spot (Black / Yellow Sigatoka)",
        "scientific_name": "Pseudocercospora musae (Yellow) / Pseudocercospora fijiensis (Black)",
        "disease_type": "Fungal",
        "affected_parts": ["Leaves"],
        "symptoms": [
            "Small faint yellowish-green specks parallel to leaf veins developing into reddish-brown to black spindle streaks",
            "Centers of older lesions become sunken, bleached ash-grey with prominent dark brown margins and bright yellow halos",
            "Extensive coalescence of spots leads to rapid leaf blighting, premature leaf collapse, and unfilled bunches"
        ],
        "possible_causes": [
            "Warm humid tropical weather with frequent rainfall or heavy dew (>90% RH, 25-30°C)",
            "Stagnant microclimate in densely planted stands with poor air circulation"
        ],
        "prevention": [
            "Adhere to recommended wider spacing (2.1 x 2.1 m) to maximize wind passage",
            "Systematic de-leafing: remove and bury severely infected leaves at weekly intervals during rainy periods",
            "Avoid overhead sprinkler irrigation; prefer drip systems to keep foliar canopy dry"
        ],
        "management": [
            "Implement early-season fungicide rotations targeting younger emerging leaves (first 3-4 leaves)"
        ],
        "organic_management": [
            "Spray horticultural mineral oil (1% emulsion) combined with Copper Oxychloride @ 2.0 g/L",
            "Bio-fungicide foliar applications of Pseudomonas fluorescens @ 10 g/L + cow urine 5%"
        ],
        "chemical_management": [
            "Propiconazole 25% EC @ 1.0 ml/L or Difenoconazole 25% EC @ 1.0 ml/L mixed with 1% mineral oil",
            "Azoxystrobin 23% SC @ 1.0 ml/L or Trifloxystrobin 25% + Tebuconazole 50% WG @ 0.7 g/L; rotate chemical classes to prevent resistance"
        ],
        "severity_notes": "Sigatoka is the most economically devastating foliar disease of banana worldwide, causing up to 50% yield reduction and premature ripening of bunches during transit.",
        "source": "CIMMYT / ICAR-NRCB Banana Pathology Guidelines",
        "last_reviewed": "2026-11-19"
    },
    # --- WHEAT ---
    {
        "crop": "wheat",
        "disease_id": "healthy",
        "display_name": "Healthy Wheat Plant",
        "scientific_name": "Triticum aestivum (Healthy)",
        "disease_type": "None",
        "affected_parts": [],
        "symptoms": [
            "Uniform vibrant green upright leaf blades without chlorosis, pustules, or blotches",
            "Vigorous tillering and healthy crown root development",
            "Uniform spike emergence and clean glumes"
        ],
        "possible_causes": [],
        "prevention": [
            "Sow certified disease-free seeds treated with Trichoderma or standard seed protectant",
            "Balanced fertilizer application (120:60:40 kg NPK/ha based on soil test)",
            "Timely irrigation at critical growth stages (crown root initiation, tillering, jointing, flowering, milk stage)"
        ],
        "management": [
            "Continue standard wheat field management, weed control, and periodic rust scouting"
        ],
        "organic_management": [
            "Application of well-cured compost (10 t/ha), Azotobacter and PSB seed treatment"
        ],
        "chemical_management": [
            "None required for healthy crops"
        ],
        "severity_notes": "Not applicable - plant displays healthy vegetative growth.",
        "source": "ICAR-IIWBR Karnal Wheat Package of Practices",
        "last_reviewed": "2026-11-19"
    },
    {
        "crop": "wheat",
        "disease_id": "leaf_rust",
        "display_name": "Wheat Leaf Rust (Brown Rust)",
        "scientific_name": "Puccinia triticina",
        "disease_type": "Fungal",
        "affected_parts": ["Leaves", "Leaf Sheaths"],
        "symptoms": [
            "Small, circular to oval orange-brown or reddish-brown powdery pustules (uredinia) scattered randomly over the upper leaf surface",
            "Pustules rupture the upper leaf epidermis, shedding millions of fine rust-colored spores upon contact",
            "Severely rusted leaves turn yellow, chlorotic, and wither prematurely, shriveling grain fill"
        ],
        "possible_causes": [
            "Moderate temperatures (15-25°C) coupled with overnight dew formation and free moisture on leaf blades",
            "Airborne transport of urediniospores from warm winter-growing regions"
        ],
        "prevention": [
            "Cultivate certified rust-resistant wheat varieties (e.g., HD-2967, DBW-187, DBW-303, PBW-725)",
            "Avoid late sowing to prevent exposure to warm late-spring rust buildup",
            "Avoid excessive nitrogen fertilization which creates succulent foliage highly susceptible to rust colonization"
        ],
        "management": [
            "Regular weekly scouting of flag leaves during booting and flowering; initiate action at first pustule appearance"
        ],
        "organic_management": [
            "Foliar spray of 5% Neem Seed Kernel Extract (NSKE) or bio-fungicide Bacillus amyloliquefaciens @ 5 g/L",
            "Foliar spray of cow urine (10%) mixed with fermented butter milk"
        ],
        "chemical_management": [
            "Propiconazole 25% EC @ 1.0 ml/L (500 ml/ha in 500 L water) at the very first sign of brown pustules",
            "Tebuconazole 25.9% EC @ 1.0 ml/L or Azoxystrobin 18.2% + Difenoconazole 11.4% SC @ 1.0 ml/L; observe 30-day PHI"
        ],
        "severity_notes": "Leaf rust can reduce wheat yield by 20% to 50% and severely decrease thousand-kernel weight (TKW) when flag leaves are infected before grain filling.",
        "source": "ICAR-IIWBR Indian Institute of Wheat & Barley Research / CIMMYT Wheat Pathology",
        "last_reviewed": "2026-11-19"
    },
    {
        "crop": "wheat",
        "disease_id": "nitrogen_deficiency",
        "display_name": "Wheat Nitrogen Deficiency",
        "scientific_name": "Abiotic Plant Nutritional Disorder (Nitrogen Deficit)",
        "disease_type": "Nutritional Deficiency",
        "affected_parts": ["Lower Leaves", "Whole Plant"],
        "symptoms": [
            "Generalized uniform pale green to pale yellow discoloration (chlorosis) initiating on the oldest lower leaves",
            "Yellowing begins at the leaf tip and progresses down the midrib toward the leaf base in a distinct 'V' shape",
            "Stunted erect plant growth, reduced tiller numbers, thin stems, and small pale spikes"
        ],
        "possible_causes": [
            "Insufficient nitrogen fertilizer application or severe leaching in sandy soils due to excessive irrigation or heavy rains",
            "Waterlogged soil conditions inducing denitrification and inhibiting root nitrogen absorption"
        ],
        "prevention": [
            "Conduct pre-sowing soil fertility tests to calculate nitrogen deficit",
            "Split application of nitrogen: 50% basal dose at sowing, 25% at first irrigation (CRI stage), and 25% at second irrigation (tillering/jointing)",
            "Incorporate green manure crops (Sesbania) or farmyard manure prior to field preparation"
        ],
        "management": [
            "Apply immediate nitrogen top-dressing before irrigating the crop",
            "For rapid leaf absorption, administer foliar urea sprays"
        ],
        "organic_management": [
            "Foliar application of liquid Jeevamrut @ 10% or vermiwash @ 5% during vegetative stages",
            "Seed inoculation with Azotobacter biofertilizer (200 g/10 kg seed)"
        ],
        "chemical_management": [
            "Top-dressing with Prilled Urea @ 25-35 kg/acre just prior to irrigation",
            "Foliar spray of 2.0% Urea solution (20 g Urea/L water) for rapid recovery under standing crop conditions"
        ],
        "severity_notes": "Nitrogen deficiency directly curtails tillering capacity and grain protein content, leading to drastic yield reductions (up to 40%).",
        "source": "ICAR-IIWBR Nutrient Management Guidelines / FAO Fertilizer Manual",
        "last_reviewed": "2026-11-19"
    }
]

# 2. Multilingual translations
TRANSLATIONS = {
    # BANANA
    "cordana_leaf_spot": {
        "en": {
            "display_name": "Cordana Leaf Spot of Banana",
            "symptoms": ["Oval pale brown lesions with bright yellow halos", "Concentric zonation along leaf margins"],
            "prevention": ["Optimal plantation spacing (1.8m)", "Desuckering and removing dead leaves", "Good drainage"],
            "causes": ["Cordana musae fungus", "Prolonged leaf wetness and warm humid conditions"],
            "organic_management": ["Copper oxychloride @ 2.5 g/L", "Pseudomonas fluorescens spray", "Neem oil 1%"],
            "chemical_management": ["Mancozeb 75% WP @ 2.5 g/L", "Propiconazole 25% EC @ 1.0 ml/L"],
            "limitations": "Morphologically similar to early Sigatoka; verify oval diamond shape and marginal origin."
        },
        "te": {
            "display_name": "అరటి కోర్దానా ఆకు మచ్చ తెగులు",
            "symptoms": ["పసుపు రంగు వలయాలతో కూడిన లేత గోధుమ రంగు అండాకార మచ్చలు", "ఆకు అంచుల నుండి లోపలికి వ్యాపించే మచ్చలు"],
            "prevention": ["మొక్కల మధ్య తగిన దూరం పాటించడం", "ఎండిన ఆకులను తొలగించి శుభ్రపరచడం", "మురుగు నీటి పారుదల కల్పించడం"],
            "causes": ["కోర్దానా మ్యూసే శిలీంధ్రం", "అధిక తేమ మరియు వెచ్చని వాతావరణం"],
            "organic_management": ["కాపర్ ఆక్సిక్లోరైడ్ 2.5 గ్రా/లీ", "సూడోమోనాస్ ఫ్లోరోసెన్స్ ద్రావణం"],
            "chemical_management": ["మాంకోజెబ్ 2.5 గ్రా/లీ లేదా ప్రొపికొనాజోల్ 1 మి.లీ/లీ స్ప్రే చేయండి"],
            "limitations": "సిగటోకా తెగులుతో పోలిక ఉండవచ్చు; అండాకారపు మచ్చలను పరిశీలించండి."
        },
        "hi": {
            "display_name": "केले का कोरडाना पत्ती धब्बा रोग",
            "symptoms": ["चमकीले पीले छल्ले वाले अंडाकार हल्के भूरे धब्बे", "पत्तियों के किनारों से शुरू होने वाले धब्बे"],
            "prevention": ["उचित पौधे की दूरी", "संक्रमित पत्तियों को हटाना", "उचित जल निकासी"],
            "causes": ["कोरडाना म्यूसी कवक", "लगातार नमी और गर्म तापमान"],
            "organic_management": ["कॉपर ऑक्सीक्लोराइड 2.5 ग्राम/लीटर", "स्यूडोमोनास फ्लोरोसेंस"],
            "chemical_management": ["मैंकोजेब 2.5 ग्राम/लीटर या प्रोपिकोनाजोल 1 मिली/लीटर"],
            "limitations": "सिगाटोका से समानता हो सकती है; अंडाकार आकार की पुष्टि करें।"
        },
        "ta": {
            "display_name": "வாழை கோர்டானா இலைப்புள்ளி நோய்",
            "symptoms": ["மஞ்சள் வளையங்களுடன் கூடிய முட்டை வடிவ பழுப்பு நிற புள்ளிகள்", "இலை ஓரங்களில் தொடங்கி உள்நோக்கி பரவும் புள்ளிகள்"],
            "prevention": ["சரியான இடைவெளி பராமரிப்பு", "காய்ந்த இலைகளை அகற்றுதல்", "வடிகால் வசதி"],
            "causes": ["கோர்டானா மியூசே பூஞ்சை", "அதிக ஈரப்பதம்"],
            "organic_management": ["காப்பர் ஆக்ஸிகுளோரைடு 2.5 கி/லி", "சூடோமோனாஸ் தெளிப்பு"],
            "chemical_management": ["மேன்கோசெப் 2.5 கி/லி அல்லது புரோபிகோனசோல் 1 மி.லி/லி"],
            "limitations": "சிகாடோகா புள்ளிகளுடன் குழப்பம் ஏற்படலாம்."
        },
        "kn": {
            "display_name": "ಬಾಳೆ ಕೊರ್ಡಾನಾ ಎಲೆ ಚುಕ್ಕೆ ರೋಗ",
            "symptoms": ["ಹಳದಿ ಅಂಚಿನ ಅಂಡಾಕಾರದ ತಿಳಿ ಕಂದು ಚುಕ್ಕೆಗಳು", "ಎಲೆಯ ಅಂಚಿನಿಂದ ಹರಡುವ ಕಲೆಗಳು"],
            "prevention": ["ಸೂಕ್ತ ಗಿಡಗಳ ಅಂತರ", "ಒಣಗಿದ ಎಲೆಗಳನ್ನು ತೆಗೆಯುವುದು", "ನೀರು ಬಸಿದು ಹೋಗುವ ವ್ಯವಸ್ಥೆ"],
            "causes": ["ಕೊರ್ಡಾನಾ ಮ್ಯೂಸೆ ಶಿಲೀಂಧ್ರ", "ಹೆಚ್ಚಿನ ತೇವಾಂಶ"],
            "organic_management": ["ಕಾಪರ್ ಆಕ್ಸಿಕ್ಲೋರೈಡ್ 2.5 ಗ್ರಾಂ/ಲೀ", "ಸ್ಯೂಡೋಮೊನಾಸ್ ಸಿಂಪಡಣೆ"],
            "chemical_management": ["ಮ್ಯಾಂಕೋಜೆಬ್ 2.5 ಗ್ರಾಂ/ಲೀ ಅಥವಾ ಪ್ರೊಪಿಕೊನಜೋಲ್ 1 ಮಿ.ಲೀ/ಲೀ"],
            "limitations": "ಸಿಕಾಟೋಕಾ ರೋಗದ ಲಕ್ಷಣಗಳೊಂದಿಗೆ ಹೋಲಿಕೆ ಇರುತ್ತದೆ."
        }
    },
    "pestalotiopsis_leaf_spot": {
        "en": {
            "display_name": "Pestalotiopsis Leaf Spot of Banana",
            "symptoms": ["Irregular grayish-white lesions with dark brown raised borders", "Tiny black fruiting specks (acervuli) in center"],
            "prevention": ["Windbreaks to prevent leaf tearing", "Avoid wounding during field operations", "Adequate potassium nutrition"],
            "causes": ["Pestalotiopsis palmarum fungus", "High humidity and wind injury"],
            "organic_management": ["Copper Hydroxide 77% WP @ 2.0 g/L", "Bacillus subtilis biocontrol"],
            "chemical_management": ["Chlorothalonil 75% WP @ 2.0 g/L", "Mancozeb @ 2.5 g/L"],
            "limitations": "Commonly occurs on leaves injured by wind or sunburn."
        },
        "te": {
            "display_name": "అరటి పెస్టలోషియాప్సిస్ ఆకు మచ్చ తెగులు",
            "symptoms": ["ముదురు గోధుమ అంచులు గల బూడిద-తెలుపు రంగు మచ్చలు", "మచ్చల మధ్యలో చిన్న నల్లని చుక్కలు"],
            "prevention": ["గాలి తాకిడిని తగ్గించడానికి రక్షణ కంచెలు", "ఆకులకు గాయాలు కాకుండా జాగ్రత్తలు", "పొటాష్ ఎరువులు అందించడం"],
            "causes": ["పెస్టలోషియాప్సిస్ పాల్మారమ్ శిలీంధ్రం", "తేమ మరియు గాయపడిన ఆకులు"],
            "organic_management": ["కాపర్ హైడ్రాక్సైడ్ 2.0 గ్రా/లీ", "బాసిల్లస్ సబ్టిలిస్ పిచికారీ"],
            "chemical_management": ["క్లోరోథలోనిల్ 2.0 గ్రా/లీ లేదా మాంకోజెబ్ 2.5 గ్రా/లీ"],
            "limitations": "గాలి వల్ల చిరిగిన లేదా దెబ్బతిన్న ఆకులపై ఎక్కువగా కనిపిస్తుంది."
        },
        "hi": {
            "display_name": "केले का पेस्टालोटिओप्सिस पत्ती धब्बा रोग",
            "symptoms": ["गहरे भूरे किनारों वाले भूरे-सफेद धब्बे", "केंद्र में छोटे काले दाने"],
            "prevention": ["हवा से बचाव के लिए वायुरोधी वृक्ष", "पत्तियों को चोट से बचाना", "पोटाश उर्वरक"],
            "causes": ["पेस्टालोटिओप्सिस कवक", "उच्च आर्द्रता और यांत्रिक क्षति"],
            "organic_management": ["कॉपर हाइड्रॉक्साइड 2 ग्राम/लीटर", "बैसिलस सबटिलिस"],
            "chemical_management": ["क्लोरोथैलोनिल 2 ग्राम/लीटर या मैंकोजेब 2.5 ग्राम/लीटर"],
            "limitations": "हवा से क्षतिग्रस्त पत्तियों पर अधिक देखा जाता है।"
        },
        "ta": {
            "display_name": "வாழை பெஸ்டலோசியோப்சிஸ் இலைப்புள்ளி நோய்",
            "symptoms": ["சாம்பல்-வெள்ளை புள்ளிகள் மற்றும் கரும்பழுப்பு ஓரங்கள்", "மையத்தில் சிறிய கருப்பு புள்ளிகள்"],
            "prevention": ["காற்றுத்தடை மரங்கள் அமைத்தல்", "இலை காயங்களை தவிர்த்தல்", "சாம்பல் சத்து உரம்"],
            "causes": ["பெஸ்டலோசியோப்சிஸ் பூஞ்சை", "ஈரப்பதம்"],
            "organic_management": ["காப்பர் ஹைட்ராக்சைடு 2 கி/லி", "பேசில்லஸ் தெளிப்பு"],
            "chemical_management": ["குளோரோதலோனில் 2 கி/லி அல்லது மேன்கோசெப் 2.5 கி/லி"],
            "limitations": "காற்றினால் கிழிந்த இலைகளில் விரைவாக பரவும்."
        },
        "kn": {
            "display_name": "ಬಾಳೆ ಪೆಸ್ಟಾಲೋಟಿಯೊಪ್ಸಿಸ್ ಎಲೆ ಚುಕ್ಕೆ ರೋಗ",
            "symptoms": ["ಕಂದು ಅಂಚುಳ್ಳ ಬೂದು-ಬಿಳಿ ಚುಕ್ಕೆಗಳು", "ಮಧ್ಯಭಾಗದಲ್ಲಿ ಕಪ್ಪು ಸಣ್ಣ ಚುಕ್ಕೆಗಳು"],
            "prevention": ["ಗಾಳಿ ತಡೆಯುವ ಮರಗಳನ್ನು ಬೆಳೆಸುವುದು", "ಎಲೆಗಳಿಗೆ ಗಾಯವಾಗದಂತೆ ನೋಡಿಕೊಳ್ಳುವುದು"],
            "causes": ["ಪೆಸ್ಟಾಲೋಟಿಯೊಪ್ಸಿಸ್ ಶಿಲೀಂಧ್ರ", "ಹೆಚ್ಚಿನ ತೇವಾಂಶ"],
            "organic_management": ["ಕಾಪರ್ ಹೈಡ್ರಾಕ್ಸೈಡ್ 2 ಗ್ರಾಂ/ಲೀ", "ಬ್ಯಾಸಿಲಸ್ ಸಿಂಪಡಣೆ"],
            "chemical_management": ["ಕ್ಲೋರೋಥಲೋನಿಲ್ 2 ಗ್ರಾಂ/ಲೀ ಅಥವಾ ಮ್ಯಾಂಕೋಜೆಬ್ 2.5 ಗ್ರಾಂ/ಲೀ"],
            "limitations": "ಗಾಳಿಯಿಂದ ಹಾನಿಯಾದ ಎಲೆಗಳಲ್ಲಿ ಸಾಮಾನ್ಯವಾಗಿ ಕಂಡುಬರುತ್ತದೆ."
        }
    },
    "sigatoka_leaf_spot": {
        "en": {
            "display_name": "Sigatoka Leaf Spot (Black / Yellow Sigatoka)",
            "symptoms": ["Narrow yellow-green streaks turning dark brown/black spindle streaks", "Lesions with sunken grey centers and yellow halos", "Premature foliage death"],
            "prevention": ["Adequate plant spacing (2.1m)", "Regular de-leafing of diseased leaves", "Avoid sprinkler overhead watering"],
            "causes": ["Pseudocercospora musae / Pseudocercospora fijiensis", "High humidity (>90%) and rain splash"],
            "organic_management": ["Mineral oil 1% + Copper Oxychloride @ 2.0 g/L", "Pseudomonas fluorescens 10 g/L"],
            "chemical_management": ["Propiconazole 25% EC @ 1.0 ml/L + 1% mineral oil", "Azoxystrobin 23% SC @ 1.0 ml/L; rotate MOA"],
            "limitations": "Severe economic impact; requires timely rotation of systemic and contact fungicides."
        },
        "te": {
            "display_name": "అరటి సిగటోకా ఆకు మచ్చ తెగులు",
            "symptoms": ["ఆకులపై పసుపు-ఆకుపచ్చ గీతలు క్రమంగా ముదురు గోధుమ/నలుపు చారలుగా మారడం", "మచ్చల మధ్య భాగం బూడిద రంగులోకి మారి ఆకులు ఎండిపోవడం"],
            "prevention": ["మొక్కల మధ్య 2.1 మీటర్ల దూరం పాటించడం", "తెగులు సోకిన ఆకులను ఎప్పటికప్పుడు కత్తిరించి నాశనం చేయడం", "డ్రిప్ నీటి పారుదల వాడటం"],
            "causes": ["స్యూడోసెర్కోస్పోరా శిలీంధ్రం", "అధిక తేమ మరియు వర్షపు జల్లులు"],
            "organic_management": ["ఖనిజ నూనె 1% + కాపర్ ఆక్సిక్లోరైడ్ 2.0 గ్రా/లీ పిచికారీ", "సూడోమోనాస్ 10 గ్రా/లీ"],
            "chemical_management": ["ప్రొపికొనాజోల్ 1 మి.లీ/లీ లేదా అజోక్సిస్ట్రోబిన్ 1 మి.లీ/లీ నూనెతో కలిపి స్ప్రే చేయండి"],
            "limitations": "దిగుబడిని తీవ్రంగా దెబ్బతీసే ప్రధాన తెగులు; నిరంతర పర్యవేక్షణ అవసరం."
        },
        "hi": {
            "display_name": "केले का सिगाटोका पत्ती धब्बा रोग",
            "symptoms": ["पीली-हरी धारियां जो काली-धूसर धारियों में बदल जाती हैं", "पत्तियों का समय से पहले सूखना"],
            "prevention": ["पौधों में 2.1 मीटर की दूरी", "संक्रमित पत्तियों को काटना", "टपक सिंचाई अपनाना"],
            "causes": ["स्यूडोसर्कोस्पोरा कवक", "उच्च आर्द्रता और वर्षा"],
            "organic_management": ["खनिज तेल 1% + कॉपर ऑक्सीक्लोराइड 2 ग्राम/लीटर", "स्यूडोमोनस"],
            "chemical_management": ["प्रोपिकोनाजोल 1 मिली/लीटर खनिज तेल के साथ या एजोक्सीस्ट्रोबिन 1 मिली/लीटर"],
            "limitations": "गंभीर उपज हानि करता है; तुरंत प्रबंधन आवश्यक है।"
        },
        "ta": {
            "display_name": "வாழை சிகாடோகா இலைப்புள்ளி நோய்",
            "symptoms": ["மஞ்சள்-பச்சை கோடுகள் பின்னர் கரும்பழுப்பு நிறமாக மாறுதல்", "இலைகள் காய்ந்து உதிர்தல்"],
            "prevention": ["2.1 மீ இடைவெளி நடுதல்", "பாதிக்கப்பட்ட இலைகளை வெட்டி அழித்தல்", "சொட்டு நீர் பாசனம்"],
            "causes": ["சூடோசெர்கோஸ்போரா பூஞ்சை", "அதிக மழை மற்றும் ஈரப்பதம்"],
            "organic_management": ["மினரல் ஆயில் 1% + காப்பர் ஆக்ஸிகுளோரைடு 2 கி/லி", "சூடோமோனாஸ்"],
            "chemical_management": ["புரோபிகோனசோல் 1 மி.லி/லி அல்லது அசோக்ஸிஸ்ட்ரோபின் 1 மி.லி/லி"],
            "limitations": "வாழையின் மிக முக்கியமான நோய்; சரியான நேரத்தில் மருந்தடிக்க வேண்டும்."
        },
        "kn": {
            "display_name": "ಬಾಳೆ ಸಿಕಾಟೋಕಾ ಎಲೆ ಚುಕ್ಕೆ ರೋಗ",
            "symptoms": ["ಹಳದಿ-ಹಸಿರು ಗೆರೆಗಳು ನಂತರ ಕಪ್ಪು ಪಟ್ಟೆಗಳಾಗಿ ಬದಲಾಗುವುದು", "ಎಲೆಗಳು ಒಣಗಿ ಉದುರುವುದು"],
            "prevention": ["2.1 ಮೀ ಅಂತರದಲ್ಲಿ ನಾಟಿ", "ರೋಗಪೀಡಿತ ಎಲೆಗಳನ್ನು ತೆಗೆಯುವುದು", "ಹನಿ ನೀರಾವರಿ"],
            "causes": ["ಸ್ಯೂಡೋಸರ್ಕೋಸ್ಪೊರಾ ಶಿಲೀಂಧ್ರ", "ಹೆಚ್ಚಿನ ಮಳೆ ಮತ್ತು ತೇವಾಂಶ"],
            "organic_management": ["ಖನಿಜ ತೈಲ 1% + ಕಾಪರ್ ಆಕ್ಸಿಕ್ಲೋರೈಡ್ 2 ಗ್ರಾಂ/ಲೀ", "ಸ್ಯೂಡೋಮೊನಾಸ್"],
            "chemical_management": ["ಪ್ರೊಪಿಕೊನಜೋಲ್ 1 ಮಿ.ಲೀ/ಲೀ ಅಥವಾ ಅಜೋಕ್ಸಿಸ್ಟ್ರೋಬಿನ್ 1 ಮಿ.ಲೀ/ಲೀ"],
            "limitations": "ಅತ್ಯಂತ ಹಾನಿಕಾರಕ ರೋಗ; ಕ್ರಮಬದ್ಧ ಔಷಧ ಸಿಂಪಡಣೆ ಅಗತ್ಯ."
        }
    },
    # WHEAT
    "leaf_rust": {
        "en": {
            "display_name": "Wheat Leaf Rust (Brown Rust)",
            "symptoms": ["Small round-to-oval orange-brown powdery pustules scattered on upper leaf surface", "Pustules shed reddish-brown spores", "Premature chlorosis and leaf drying"],
            "prevention": ["Plant certified rust-resistant cultivars", "Timely planting to avoid late heat", "Avoid excessive nitrogen"],
            "causes": ["Puccinia triticina fungus", "Moderate temps (15-25°C) and dew/leaf wetness"],
            "organic_management": ["Neem Seed Kernel Extract 5%", "Bacillus amyloliquefaciens 5 g/L", "Fermented butter milk 10%"],
            "chemical_management": ["Propiconazole 25% EC @ 1.0 ml/L at first appearance", "Tebuconazole 25.9% EC @ 1.0 ml/L"],
            "limitations": "Examine pustule distribution (scattered vs striped in yellow rust)."
        },
        "te": {
            "display_name": "గోధుమ ఆకు తుప్పు తెగులు (బ్రౌన్ రస్ట్)",
            "symptoms": ["ఆకు పైభాగంలో నారింజ-గోధుమ రంగు చిన్న గుండ్రని పొడి మచ్చలు (పస్టుల్స్)", "తాకినప్పుడు చేతికి అంటుకునే తుప్పు రంగు పొడి", "ఆకులు పసుపు రంగులోకి మారి ఎండిపోవడం"],
            "prevention": ["తెగులును తట్టుకునే రకాలను నాటడం (HD-2967, DBW-187)", "సరైన సమయంలో విత్తుకోవడం", "నత్రజని అధికంగా వాడకపోవడం"],
            "causes": ["పక్సీనియా ట్రిటిసినా శిలీంధ్రం", "మితమైన ఉష్ణోగ్రత (15-25°C) మరియు మంచు బిందువులు"],
            "organic_management": ["వేప గింజల కషాయం (NSKE 5%)", "పులిసిన మజ్జిగ ద్రావణం 10%"],
            "chemical_management": ["ప్రొపికొనాజోల్ 25% EC 1.0 మి.లీ/లీ లేదా టెబుకొనాజోల్ 1.0 మి.లీ/లీ మొదటి మచ్చ కనిపించగానే పిచికారీ చేయండి"],
            "limitations": "పసుపు తుప్పు తెగులుతో కాకుండా గుండ్రటి నారింజ మచ్చలను జాగ్రత్తగా గమనించండి."
        },
        "hi": {
            "display_name": "गेहूं का भूरा रतुआ (पत्ती रतुआ)",
            "symptoms": ["पत्तियों की ऊपरी सतह पर नारंगी-भूरे रंग के गोल-अंडाकार चूर्ण वाले फफोले", "स्पर्श करने पर हाथ में रतुआ पाउडर लगना", "पत्तियों का पीला पड़कर सूखना"],
            "prevention": ["प्रतिरोधी किस्में (HD-2967, DBW-187) बोएं", "समय पर बुआई करें", "अत्यधिक यूरिया के प्रयोग से बचें"],
            "causes": ["पक्सीनिया ट्रिटिसिना कवक", "मध्यम तापमान (15-25°C) और रात की ओस"],
            "organic_management": ["नीम बीज अर्क 5%", "खट्टी छाछ 10% का छिड़काव"],
            "chemical_management": ["प्रोपिकोनाजोल 25% ईसी 1 मिली/लीटर या टेबुकोनाजोल 1 मिली/लीटर पहले लक्षण दिखते ही छिड़कें"],
            "limitations": "पीले रतुआ (धारियों) और भूरे रतुआ (बिखरे हुए फफोले) में अंतर पहचानें।"
        },
        "ta": {
            "display_name": "கோதுமை இலை துரு நோய் (பழுப்பு துரு)",
            "symptoms": ["இலையின் மேற்பரப்பில் ஆரஞ்சு-பழுப்பு நிற தூள் போன்ற கொப்புளங்கள்", "இலைகள் மஞ்சள் நிறமாகி உதிர்தல்"],
            "prevention": ["நோய் எதிர்ப்பு ரகங்களை பயிரிடுதல்", "சரியான பருவத்தில் விதைத்தல்", "அதிக தழைச்சத்து தவிர்த்தல்"],
            "causes": ["பக்சீனியா டிரிட்டிசினா பூஞ்சை", "பனிப்பொழிவு மற்றும் மிதமான வெப்பநிலை"],
            "organic_management": ["வேப்பங்கொட்டை கரைசல் 5%", "புளித்த மோர் 10%"],
            "chemical_management": ["புரோபிகோனசோல் 1 மி.லி/லி அல்லது டெபுகோனசோல் 1 மி.லி/லி"],
            "limitations": "மஞ்சள் துரு நோயிலிருந்து வேறுபடுத்தி பார்க்க வேண்டும்."
        },
        "kn": {
            "display_name": "ಗೋಧಿ ಎಲೆ ತುಕ್ಕು ರೋಗ (ಕಂದು ತುಕ್ಕು)",
            "symptoms": ["ಎಲೆಗಳ ಮೇಲೆ ಕಿತ್ತಳೆ-ಕಂದು ಬಣ್ಣದ ಸಣ್ಣ ಪುಡಿ ಗುಳ್ಳೆಗಳು", "ಎಲೆಗಳು ಹಳದಿಯಾಗಿ ಒಣಗುವುದು"],
            "prevention": ["ರೋಗ ನಿರೋಧಕ ತಳಿಗಳನ್ನು ಬಿತ್ತನೆ ಮಾಡುವುದು", "ಸಕಾಲಿಕ ಬಿತ್ತನೆ", "ಹೆಚ್ಚು ಯೂರಿಯಾ ಬಳಸದಿರುವುದು"],
            "causes": ["ಪಕ್ಸೀನಿಯಾ ಟ್ರಿಟಿಸಿನಾ ಶಿಲೀಂಧ್ರ", "ಇಬ್ಬನಿ ಮತ್ತು ಮಧ್ಯಮ ತಾಪಮಾನ"],
            "organic_management": ["ಬೇವಿನ ಕಷಾಯ 5%", "ಹುಳಿ ಮಜ್ಜಿಗೆ ಸಿಂಪಡಣೆ"],
            "chemical_management": ["ಪ್ರೊಪಿಕೊನಜೋಲ್ 1 ಮಿ.ಲೀ/ಲೀ ಅಥವಾ ಟೆಬುಕೊನಜೋಲ್ 1 ಮಿ.ಲೀ/ಲೀ"],
            "limitations": "ಹಳದಿ ತುಕ್ಕು ರೋಗಕ್ಕಿಂತ ಭಿನ್ನವಾದ ದುಂಡಗಿನ ಕಲೆಗಳನ್ನು ಗಮನಿಸಿ."
        }
    },
    "nitrogen_deficiency": {
        "en": {
            "display_name": "Wheat Nitrogen Deficiency",
            "symptoms": ["General pale yellowing starting from oldest lower leaves", "V-shaped yellowing along midrib from tip", "Stunted tillers and small spikes"],
            "prevention": ["Soil testing", "Split nitrogen application (basal, CRI, tillering)", "Incorporate green manure"],
            "causes": ["Insufficient nitrogen fertilizer or severe leaching/waterlogging"],
            "organic_management": ["Liquid Jeevamrut 10%", "Vermiwash 5%", "Azotobacter biofertilizer"],
            "chemical_management": ["Top-dress Urea @ 25-35 kg/acre before irrigation", "Foliar spray of 2% Urea solution for rapid relief"],
            "limitations": "Distinguish from moisture stress or sulfur deficiency (which affects younger leaves)."
        },
        "te": {
            "display_name": "గోధుమ నత్రజని లోపం",
            "symptoms": ["క్రింది పాత ఆకుల నుండి మొదలై పైకి వ్యాపించే లేత పసుపు రంగు", "ఆకు కొన నుండి ఈనె వెంబడి 'V' ఆకారంలో పసుపు రంగులోకి మారడం", "మొక్క ఎదుగుదల లోపించడం, పిలకలు తగ్గడం"],
            "prevention": ["నేల పరీక్ష ఆధారంగా ఎరువులు వేయడం", "నత్రజనిని విడతల వారీగా వేయడం (విత్తేటప్పుడు, మొదటి నీరు, పిలకల దశ)", "పచ్చిరొట్ట ఎరువులు వాడటం"],
            "causes": ["నేలలో నత్రజని కొరత లేదా అధిక నీటి వల్ల కొట్టుకుపోవడం"],
            "organic_management": ["జీవామృతం 10% లేదా వర్మివాష్ పిచికారీ", "అజటోబాక్టర్ జీవ ఎరువు వాడకం"],
            "chemical_management": ["తడి ఇచ్చే ముందు ఎకరానికి 25-35 కిలోల యూరియా చల్లడం", "త్వరిత ఉపశమనం కోసం 2% యూరియా ద్రావణం (20 గ్రా/లీ) పిచికారీ"],
            "limitations": "గంధకం లోపం నుండి వేరుగా గుర్తించండి (గంధకం లోపంలో పై లేత ఆకులు పసుపుగా మారుతాయి)."
        },
        "hi": {
            "display_name": "गेहूं में नाइट्रोजन की कमी",
            "symptoms": ["निचली पुरानी पत्तियों से शुरू होने वाला पीलापन", "पत्ती की नोक से मध्य शिरा के साथ 'V' आकार में पीलापन", "कम कल्ले और बौना पौधा"],
            "prevention": ["मिट्टी परीक्षण", "नाइट्रोजन का विभाजित प्रयोग (बुआई, पहली सिंचाई, कल्ले फूटते समय)", "हरी खाद"],
            "causes": ["नाइट्रोजन उर्वरक की कमी या जलभराव से निक्षालन"],
            "organic_management": ["जीवामृत 10%", "वर्मीवाश 5%", "एजोटोबैक्टर"],
            "chemical_management": ["सिंचाई से पहले 25-35 किग्रा/एकड़ यूरिया का छिड़काव", "तुरंत राहत के लिए 2% यूरिया घोल का पर्णीय छिड़काव"],
            "limitations": "सल्फर की कमी से अलग पहचानें (सल्फर में नई पत्तियां पीली होती हैं)।"
        },
        "ta": {
            "display_name": "கோதுமை தழைச்சத்து (நைட்ரஜன்) பற்றாக்குறை",
            "symptoms": ["கீழ் பழைய இலைகளில் இருந்து தொடங்கும் வெளிர் மஞ்சள் நிறம்", "நுனியில் இருந்து 'V' வடிவில் மஞ்சள் நிறமாதல்", "குறைந்த தூர்கள்"],
            "prevention": ["மண் பரிசோதனை", "பிரித்து உரம் இடுதல்", "பசுந்தாள் உரம்"],
            "causes": ["மண்ணில் தழைச்சத்து குறைவு அல்லது நீரில் அடித்துச் செல்லப்படுதல்"],
            "organic_management": ["ஜீவாமிர்தம் 10%", "அசோட்டோபாக்டர்"],
            "chemical_management": ["நீர்ப்பாசனத்திற்கு முன் ஏக்கருக்கு 25-35 கிலோ யூரியா இடுதல்", "2% யூரியா கரைசல் தெளித்தல்"],
            "limitations": "கந்தகக் குறைபாட்டிலிருந்து வேறுபடுத்தி அறிய வேண்டும்."
        },
        "kn": {
            "display_name": "ಗೋಧಿ ಸಾರಜನಕದ (ನೈಟ್ರೋಜನ್) ಕೊರತೆ",
            "symptoms": ["ಕೆಳಗಿನ ಹಳೆಯ ಎಲೆಗಳಿಂದ ಪ್ರಾರಂಭವಾಗುವ ತಿಳಿ ಹಳದಿ ಬಣ್ಣ", "ಎಲೆಯ ತುದಿಯಿಂದ 'V' ಆಕಾರದ ಹಳದಿ ಕಲೆ", "ಕಡಿಮೆ ಕವಲುಗಳು"],
            "prevention": ["ಮಣ್ಣು ಪರೀಕ್ಷೆ", "ಹಂತ ಹಂತವಾಗಿ ಯೂರಿಯಾ ನೀಡುವುದು", "ಹಸಿರೆಲೆ ಗೊಬ್ಬರ"],
            "causes": ["ಮಣ್ಣಿನಲ್ಲಿ ಸಾರಜನಕದ ಕೊರತೆ ಅಥವಾ ಅತಿಯಾದ ನೀರಿನಿಂದ ಸೋರಿಕೆ"],
            "organic_management": ["ಜೀವಾಮೃತ 10%", "ಅಜಟೊಬ್ಯಾಕ್ಟರ್ ಜೈವಿಕ ಗೊಬ್ಬರ"],
            "chemical_management": ["ನೀರಾವರಿಗೆ ಮುನ್ನ ಎಕರೆಗೆ 25-35 ಕೆಜಿ ಯೂರಿಯಾ ಮೇಲುಗೊಬ್ಬರ", "2% ಯೂರಿಯಾ ದ್ರಾವಣ ಸಿಂಪಡಣೆ"],
            "limitations": "ಗಂಧಕದ ಕೊರತೆಯಿಂದ ಪ್ರತ್ಯೇಕಿಸಿ (ಗಂಧಕದಲ್ಲಿ ಹೊಸ ಎಲೆಗಳು ಹಳದಿಯಾಗುತ್ತವೆ)."
        }
    }
}

def main():
    print("=== POPULATING BANANA & WHEAT METADATA ===")
    
    # 1. Update disease_data/diseases.json
    diseases_path = ROOT / "disease_data" / "diseases.json"
    with open(diseases_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    existing_keys = {(d["crop"], d["disease_id"]) for d in data["diseases"]}
    added_count = 0
    for nd in NEW_DISEASES:
        key = (nd["crop"], nd["disease_id"])
        if key not in existing_keys:
            data["diseases"].append(nd)
            existing_keys.add(key)
            added_count += 1
            print(f"Added disease: {key}")
    
    with open(diseases_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Updated {diseases_path} (+{added_count} records)")

    # 2. Update disease_data/translations.json
    trans_path = ROOT / "disease_data" / "translations.json"
    with open(trans_path, "r", encoding="utf-8") as f:
        trans_data = json.load(f)
    
    for cond_id, lang_dict in TRANSLATIONS.items():
        for lang, content in lang_dict.items():
            if lang in trans_data["diseases"]:
                if cond_id not in trans_data["diseases"][lang]:
                    trans_data["diseases"][lang][cond_id] = content
                    print(f"Added translation: {cond_id} -> {lang}")
    
    with open(trans_path, "w", encoding="utf-8") as f:
        json.dump(trans_data, f, indent=2, ensure_ascii=False)
    print(f"Updated {trans_path}")

    # 3. Update config/crops.json
    config_path = ROOT / "config" / "crops.json"
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = json.load(f)
    
    config_data["crops"]["banana"] = {
        "display_name": "Banana / Plantain",
        "scientific_name": "Musa acuminata / Musa balbisiana",
        "model_path": "models/banana_model.keras",
        "image_size": [224, 224],
        "class_names": [
            "cordana_leaf_spot",
            "healthy",
            "pestalotiopsis_leaf_spot",
            "sigatoka_leaf_spot"
        ],
        "confidence_threshold": 0.60,
        "description": "Banana foliar disease diagnostic module covering major fungal spot complexes (Cordana, Pestalotiopsis, Sigatoka) and healthy foliage."
    }

    config_data["crops"]["wheat"] = {
        "display_name": "Wheat / Cereal",
        "scientific_name": "Triticum aestivum",
        "model_path": "models/wheat_model.keras",
        "image_size": [224, 224],
        "class_names": [
            "healthy",
            "leaf_rust",
            "nitrogen_deficiency"
        ],
        "confidence_threshold": 0.60,
        "description": "Wheat diagnostic module detecting leaf rust (Puccinia triticina), nitrogen deficiency, and healthy wheat foliage."
    }

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2)
    print(f"Updated {config_path} with banana and wheat configurations")

if __name__ == "__main__":
    main()
