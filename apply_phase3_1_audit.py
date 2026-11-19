"""
Phase 3.1: Quality Audit & Knowledge Base Refinement Script.

Updates disease_data/diseases.json and disease_data/translations.json with:
1. Audited CIB&RC/ICAR-IIMR chemical recommendations with exact citations.
2. Scientifically qualified biological management.
3. Explicit Northern Leaf Blight label uncertainty & diagnostic limitations.
4. Farmer-friendly translations across English, Telugu, Hindi, Tamil, and Kannada.
5. 100% preservation of all 13 Paddy records.
"""

from __future__ import annotations

import json
from pathlib import Path

root = Path(__file__).resolve().parent

diseases_file = root / "disease_data" / "diseases.json"
translations_file = root / "disease_data" / "translations.json"
diseases_bak = root / "disease_data" / "diseases.json.bak"
translations_bak = root / "disease_data" / "translations.json.bak"

# ----------------------------------------------------------------------
# 1. Load existing files and verify backups
# ----------------------------------------------------------------------
assert diseases_bak.is_file(), "Backup diseases.json.bak is missing!"
assert translations_bak.is_file(), "Backup translations.json.bak is missing!"

with diseases_bak.open("r", encoding="utf-8") as f:
    d_bak = json.load(f)
paddy_records = [r for r in d_bak.get("diseases", []) if r.get("crop") == "paddy"]
assert len(paddy_records) == 13, f"Expected 13 Paddy records, found {len(paddy_records)}"

with translations_bak.open("r", encoding="utf-8") as f:
    t_bak = json.load(f)

# ----------------------------------------------------------------------
# 2. Define Audited Maize Disease Records (diseases.json)
# ----------------------------------------------------------------------
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
            "Small, circular to elongate golden-brown to cinnamon-brown powdery pustules (uredinia) on both leaf surfaces",
            "Pustules darken to brownish-black late in the season as teleutospores form",
            "Severe foliar infections cause chlorosis, premature leaf senescence, and reduced grain fill"
        ],
        "visual_identification": "Powdery pustules erupt through the leaf epidermis on both upper and lower leaf surfaces, releasing cinnamon-brown spores when wiped. Differs from Southern Rust (Puccinia polysora), which forms predominantly on the upper leaf surface with smaller, lighter orange pustules.",
        "possible_causes": [
            "Airborne fungal urediniospores transported long distances by wind currents",
            "Cool to moderate temperatures (16-25°C), high relative humidity (>95%), and extended dew periods (6+ hours of leaf wetness)"
        ],
        "favorable_conditions": "Moderate temperatures (16-25°C), persistent cloud cover, high relative humidity, and prolonged morning dew.",
        "prevention": [
            "Plant rust-resistant or tolerant corn hybrids adapted to the agro-ecological region",
            "Plant early in the season to evade peak spore migration periods",
            "Maintain balanced nitrogen fertilization; avoid excessive nitrogen that promotes overly lush, susceptible foliage"
        ],
        "cultural_management": [
            "Maintain optimal plant spacing to facilitate airflow within the canopy",
            "Routinely scout lower and middle canopy leaves from vegetative stage V8 through silking"
        ],
        "management": [
            "Prioritize intervention if pustules appear prior to tasseling/silking on susceptible hybrids under cool, moist weather"
        ],
        "biological_management": [
            "Biological management has limited efficacy against airborne obligate rust fungi like Puccinia sorghi.",
            "Preventive foliar spray of 5% Neem Seed Kernel Extract (NSKE) or certified Bacillus subtilis formulations at the very earliest sign of pustule appearance can offer mild protective suppression, but will not eradicate established infections.",
            "Biological seed treatments do not protect against foliar rust."
        ],
        "organic_management": [
            "Preventive foliar spray of 5% neem seed kernel extract (NSKE) or certified Bacillus subtilis bio-formulations at first pustule detection for mild protective suppression. Biological seed treatments do not control foliar rust."
        ],
        "chemical_management": [
            "Foliar fungicide application is warranted only when rust pustules appear prior to silking on susceptible hybrids under favorable cool, humid weather. The Central Insecticides Board & Registration Committee (CIB&RC, Govt. of India) has registered Azoxystrobin-based combinations (e.g. Azoxystrobin 18.2% + Cyproconazole 7.3% w/w SC at 1.0 mL/L; Major Uses of Pesticides - Fungicides registry) and Kresoxim-methyl 44.3% SC (1.0 mL/L) for maize rust and leaf blight. Consult your local agricultural extension officer and use only products registered for this crop and disease in your region. Follow the approved product label."
        ],
        "diagnostic_limitations": "Pustules can be visually confused with Southern Corn Rust (Puccinia polysora) or early Physoderma brown spot. Accurate diagnosis requires inspecting pustule distribution on both leaf surfaces or microscopic spore examination.",
        "safety_warnings": "Do not spray fungicides after grain has reached the dent stage as economic returns are negligible. Always adhere to mandatory pre-harvest intervals (PHI) and wear protective gear.",
        "severity_notes": "Yield losses range from 10% to 25% if significant leaf blighting occurs prior to or during silking; post-milk infections rarely justify treatment.",
        "source": "CIB&RC Major Uses of Pesticides (Fungicides, ppqs.gov.in) & ICAR-Indian Institute of Maize Research (IIMR) Technical Bulletins",
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
            "Lesions expand longitudinally between parallel leaf veins into characteristic rectangular, vein-delimited tan to gray necrotic lesions (1-6 cm long)",
            "Lesions turn grayish under high humidity due to conidial sporulation",
            "Extensive lesion coalescence blights entire leaves, causing premature senescence, stalk lodging, and reduced kernel fill"
        ],
        "visual_identification": "Strictly vein-bounded, rectangular lesions with blunt, squared-off ends that run parallel to leaf veins. Distinct from Northern Corn Leaf Blight, which produces large elliptical cigar-shaped lesions crossing veins.",
        "possible_causes": [
            "Fungal mycelium and conidia surviving in infected corn stover on the soil surface",
            "Warm, humid weather (25-32°C), high relative humidity (>90%), and extended periods of dew or rainfall"
        ],
        "favorable_conditions": "Warm temperatures (25-32°C), high relative humidity (>90%), continuous corn cropping, and heavy morning dews.",
        "prevention": [
            "Practice crop rotation with non-cereal host crops (soybeans, pulses) for at least 1-2 seasons",
            "Manage crop residue through clean tillage where conservation practices permit to accelerate stover breakdown",
            "Select corn hybrids with validated genetic resistance or tolerance to Gray Leaf Spot",
            "Avoid high planting densities that restrict canopy airflow and elevate microclimate humidity"
        ],
        "cultural_management": [
            "Scout lower and middle canopy leaves beginning 2-3 weeks before tasseling",
            "Maintain good field drainage and suppress grass weeds that contribute to canopy humidity"
        ],
        "management": [
            "Focus management on protecting the ear leaf and leaves above the ear during the critical grain filling window"
        ],
        "biological_management": [
            "Residue sanitation: Application of antagonistic Trichoderma species or cellulolytic microbial inoculants onto post-harvest corn stover helps accelerate residue decomposition and reduce overwintering Cercospora survival.",
            "Foliar biological sprays provide limited and inconsistent suppression under high disease pressure and must not be relied upon as standalone curative controls."
        ],
        "organic_management": [
            "Application of Trichoderma or bio-decomposer inoculants to crop residue post-harvest to accelerate stover breakdown and reduce fungal survival. Foliar bio-agents offer limited suppression under severe disease pressure."
        ],
        "chemical_management": [
            "No specific chemical fungicide has an exclusive CIB&RC label claim registered specifically for Gray Leaf Spot on maize in India. Consult your local agricultural extension officer and use only products registered for this crop and disease in your region. Follow the approved product label."
        ],
        "diagnostic_limitations": "Early pinpoint lesions can resemble eyespot (Kabatiella zeae) or young Northern Corn Leaf Blight. Wait until vein-delimited rectangular expansion occurs or inspect under magnification before confirming diagnosis.",
        "safety_warnings": "Do not apply unregistered off-label chemical fungicides. Follow all regional agricultural extension guidelines and mandatory environmental safety protocols.",
        "severity_notes": "One of the most destructive foliar diseases in continuous corn systems; causes significant yield losses and stalk lodging when lesions blight leaves above the ear.",
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
            "Outer ear husks in severe infections"
        ],
        "symptoms": [
            "Large, elongated, elliptical or cigar-shaped grayish-green to tan necrotic lesions (3-15 cm long)",
            "Lesions have smooth margins with tapered ends, crossing leaf veins without vein limitation",
            "Dark olive-green to black fungal spore mats develop in lesion centers during damp weather",
            "Extensive lesion coalescence causes complete leaf desiccation and burned canopy appearance"
        ],
        "visual_identification": "Large cigar-shaped or boat-shaped elliptical lesions with tapered ends that cross parallel veins freely. Unlike Gray Leaf Spot (which is vein-bound and rectangular) and Southern Corn Leaf Blight (which forms smaller, narrower oval lesions).",
        "possible_causes": [
            "Fungal conidia surviving in infected maize residue splashed by rain or dispersed by wind onto lower leaves",
            "Moderate temperatures (18-27°C), heavy dews, frequent rain, and prolonged leaf wetness (6-12 hours)"
        ],
        "favorable_conditions": "Moderate temperatures (18-27°C), heavy morning dews, frequent showers, and 6-12 hours of continuous leaf wetness.",
        "prevention": [
            "Cultivate adapted hybrids possessing specific Ht resistance genes (Ht1, Ht2, HtN) or polygenic resistance",
            "Implement 1 to 2-year crop rotation away from corn to diminish soil residue inoculum",
            "Ensure balanced potassium and nitrogen nutrition; avoid potassium deficiency which aggravates blight severity"
        ],
        "cultural_management": [
            "Routinely inspect lower canopy for cigar-shaped lesions from knee-high stage through grain fill",
            "Deeply incorporate crop residue post-harvest where agronomically appropriate"
        ],
        "management": [
            "Prioritize protection of the ear leaf and upper canopy leaves prior to silking if weather forecasts favor disease progression"
        ],
        "biological_management": [
            "Seed biopriming with Trichoderma viride (10 g/kg seed) or Pseudomonas fluorescens (10 g/kg seed) helps suppress early seed-borne inoculum and promotes seedling vigor.",
            "For foliar protection, preventive spray of 5% Neem Seed Kernel Extract (NSKE) or Bacillus subtilis bio-formulations at first lesion sighting provides moderate protective suppression under mild disease pressure."
        ],
        "organic_management": [
            "Seed biopriming with Trichoderma viride (10 g/kg seed) or Pseudomonas fluorescens (10 g/kg seed) to reduce seed-borne inoculum. Preventive spray of 5% NSKE at initial lesion appearance provides moderate protective suppression."
        ],
        "chemical_management": [
            "When 2 to 3 lesions appear on leaves below the ear before silking under humid weather forecasts, apply recommended fungicides registered by CIB&RC (Govt. of India) for maize leaf blight: Azoxystrobin 18.2% + Difenoconazole 11.4% w/w SC (1.0 mL/L; 500 mL/ha in 500 L water; 21-day PHI) or Carbendazim 12% + Mancozeb 63% WP. Consult your local agricultural extension officer and use only products registered for this crop and disease in your region. Follow the approved product label."
        ],
        "diagnostic_limitations": "Provisional Classification & Diagnostic Limitations: The training dataset labeled this class simply as 'Blight'. While visual characteristics (elongated cigar-shaped lesions) and dataset provenance (PlantVillage benchmark) strongly indicate Northern Corn Leaf Blight (Exserohilum turcicum), other maize diseases—including Southern Corn Leaf Blight (Bipolaris maydis), Stewart's bacterial wilt, and physiological leaf firing—can cause overlapping necrotic symptoms. Image-based deep learning predictions provide screening guidance only and must not be treated as definitive laboratory or microscopic confirmation. If severe blight symptoms develop, consult an agricultural extension specialist or plant pathology clinic.",
        "safety_warnings": "Observe mandatory pre-harvest intervals (PHI of at least 21 days for registered fungicides). Do not apply during windy conditions or allow drift near water bodies.",
        "severity_notes": "Can cause 30-50% grain yield reduction if severe blighting occurs at or before silking; late-season infections after dough stage have minimal yield impact.",
        "source": "CIB&RC Major Uses of Pesticides (Fungicides, ppqs.gov.in) & ICAR-IIMR Maize Pathology Bulletin",
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
        "visual_identification": "Leaf blades show uniform green pigmentation, intact lamina margins, and absence of fungal pustules, necrotic spots, vascular wilting, or insect-chewed patterns.",
        "possible_causes": [],
        "favorable_conditions": "Balanced soil fertility, well-drained loamy soil, adequate sunlight, and uniform moisture availability without waterlogging.",
        "prevention": [
            "Perform soil test-based balanced NPK fertilization with essential micronutrient (Zinc, Boron) supplementation",
            "Maintain optimal field drainage to prevent waterlogging, particularly during seedling and tasseling stages",
            "Conduct regular weekly scouting for invasive insect pests (e.g. Fall Armyworm) and early foliar spots",
            "Practice integrated weed management during the critical early crop competition window (first 30-45 days)"
        ],
        "cultural_management": [
            "Continue regular agronomic care, timely irrigation, and split application of nitrogen at knee-high and tasseling stages"
        ],
        "management": [
            "Maintain optimal plant health through balanced nutrition and routine crop scouting"
        ],
        "biological_management": [
            "Incorporate well-decomposed farmyard manure (FYM) or vermicompost (5-10 t/ha) during land preparation to enrich beneficial soil microbiota, enhance root development, and improve nutrient use efficiency.",
            "Maintain flowering borders and ecological diversity to conserve beneficial generalist predators (spiders, ladybird beetles, Trichogramma parasitoids) for natural suppression of insect vectors and pests."
        ],
        "organic_management": [
            "Incorporate well-decomposed farmyard manure (FYM) or vermicompost to foster beneficial soil microflora. Conserve natural predators through ecological field borders."
        ],
        "chemical_management": [
            "None required for healthy crops. Do not apply synthetic chemical fungicides or prophylactic pesticides to healthy plants."
        ],
        "diagnostic_limitations": "Visual assessment confirms absence of foliar disease symptoms at the time of inspection. Periodic scouting should continue throughout the growing season as weather conditions change.",
        "safety_warnings": "Avoid unnecessary chemical applications on healthy crops to preserve beneficial insect populations and prevent chemical resistance.",
        "severity_notes": "Not applicable - plant displays healthy vegetative and reproductive growth traits.",
        "source": "ICAR-Indian Institute of Maize Research (IIMR) & CIMMYT Maize Production Manual",
        "last_reviewed": "2026-11-17"
    }
]

# Write updated diseases.json
diseases_data = {"diseases": paddy_records + maize_records}
with diseases_file.open("w", encoding="utf-8") as f:
    json.dump(diseases_data, f, indent=2, ensure_ascii=False)
print(f"Updated {diseases_file}: {len(paddy_records)} Paddy + {len(maize_records)} Maize = {len(diseases_data['diseases'])} records.")

# ----------------------------------------------------------------------
# 3. Define Multilingual Translations (translations.json)
# ----------------------------------------------------------------------
# Preserve all existing UI and disease translations from translations.json.bak
trans_data = json.loads(translations_bak.read_text(encoding="utf-8"))

# Standardized English dictionary for all 4 Maize diseases
en_maize = {
    "common_rust": {
        "display_name": "Common Rust of Maize",
        "scientific_name": "Puccinia sorghi",
        "symptoms": [
            "Small circular to elongate golden-brown to cinnamon-brown powdery pustules on both leaf surfaces",
            "Pustules turn brownish-black late in the season as teliospores form",
            "Causes leaf chlorosis, premature senescence, and reduced grain fill"
        ],
        "visual_identification": "Powdery rust-colored pustules erupt on both upper and lower leaf surfaces, differing from Southern Rust which occurs mostly on upper surfaces.",
        "causes": "Airborne fungal spores carried by wind under cool, humid weather with prolonged dew.",
        "favorable_conditions": "Temperatures of 16-25°C, high humidity (>95%), and 6+ hours of dew.",
        "prevention": [
            "Plant rust-resistant or tolerant adapted corn hybrids",
            "Plant early to avoid peak airborne spore showers",
            "Maintain balanced nitrogen fertilization; avoid excessive nitrogen"
        ],
        "cultural_management": "Ensure adequate plant spacing for airflow and scout fields weekly from V8 to silking.",
        "biological_management": "Limited efficacy against airborne rust. Preventive spray of 5% NSKE or Bacillus subtilis at earliest onset provides mild protective suppression. Seed treatments do not protect against foliar rust.",
        "organic": [
            "Preventive spray of 5% neem seed kernel extract (NSKE) or Bacillus subtilis bio-formulations at first pustule detection. Biological seed treatments do not control foliar rust."
        ],
        "chemical": [
            "Foliar fungicide application is warranted only when rust pustules appear prior to silking on susceptible hybrids under favorable cool, humid weather. The Central Insecticides Board & Registration Committee (CIB&RC, Govt. of India) has registered Azoxystrobin-based combinations (e.g. Azoxystrobin 18.2% + Cyproconazole 7.3% w/w SC at 1.0 mL/L) and Kresoxim-methyl 44.3% SC (1.0 mL/L) for maize rust and leaf blight. Consult your local agricultural extension officer and use only products registered for this crop and disease in your region. Follow the approved product label."
        ],
        "diagnostic_limitations": "Can be visually confused with Southern Rust (Puccinia polysora); verify pustule distribution on both leaf surfaces.",
        "safety_warnings": "Do not spray after grain dent stage. Follow mandatory pre-harvest intervals and wear protective gear."
    },
    "gray_leaf_spot": {
        "display_name": "Gray Leaf Spot of Maize",
        "scientific_name": "Cercospora zeae-maydis",
        "symptoms": [
            "Small pinpoint tan lesions with faint haloes on lower leaves",
            "Distinct rectangular, vein-bounded tan to gray necrotic lesions (1-6 cm long)",
            "Lesions coalesce, blighting entire leaves and causing premature stalk lodging"
        ],
        "visual_identification": "Sharp rectangular lesions strictly bounded by leaf veins with squared ends running parallel to veins.",
        "causes": "Fungus overwintering in infected corn crop residue on the soil surface.",
        "favorable_conditions": "Warm temperatures (25-32°C), high relative humidity (>90%), and continuous corn cropping.",
        "prevention": [
            "Rotate crops with non-cereal host crops (soybeans, pulses) for 1-2 seasons",
            "Manage crop residue through clean tillage where conservation practices permit",
            "Select corn hybrids with proven genetic resistance or tolerance to Gray Leaf Spot",
            "Avoid overly dense planting stands to maintain canopy ventilation"
        ],
        "cultural_management": "Scout lower canopy 2-3 weeks before tasseling and control grass weeds to reduce humidity.",
        "biological_management": "Apply Trichoderma or bio-decomposers to post-harvest residue to accelerate stover breakdown. Foliar bio-agents have limited efficacy under high disease pressure.",
        "organic": [
            "Apply Trichoderma or bio-decomposer inoculants to crop residue post-harvest to accelerate stover breakdown and reduce fungal survival. Foliar bio-agents offer limited suppression under severe disease pressure."
        ],
        "chemical": [
            "No specific chemical fungicide has an exclusive CIB&RC label claim registered specifically for Gray Leaf Spot on maize in India. Consult your local agricultural extension officer and use only products registered for this crop and disease in your region. Follow the approved product label."
        ],
        "diagnostic_limitations": "Early pinpoint spots resemble eyespot or young Northern Leaf Blight; wait for vein-delimited rectangular expansion.",
        "safety_warnings": "Do not apply unregistered off-label fungicides. Follow regional agricultural extension guidelines."
    },
    "northern_leaf_blight": {
        "display_name": "Northern Corn Leaf Blight",
        "scientific_name": "Exserohilum turcicum (syn. Helminthosporium turcicum)",
        "symptoms": [
            "Large, elongated, cigar-shaped grayish-green to tan necrotic lesions (3-15 cm long)",
            "Lesions have smooth margins with tapered ends, crossing leaf veins freely",
            "Dark olive-green to black fungal spore mats develop in lesion centers during damp weather",
            "Extensive coalescence causes leaf desiccation and burned canopy appearance"
        ],
        "visual_identification": "Large cigar-shaped elliptical lesions with tapered ends that cross veins, unlike vein-bounded Gray Leaf Spot.",
        "causes": "Fungus surviving in infected maize residue splashed by rain or wind onto lower leaves.",
        "favorable_conditions": "Moderate temperatures (18-27°C), heavy dews, frequent rain, and 6-12 hours of leaf wetness.",
        "prevention": [
            "Plant adapted hybrids carrying Ht resistance genes or polygenic resistance",
            "Practice 1-2 year crop rotation away from corn to reduce soil residue inoculum",
            "Ensure balanced potassium and nitrogen nutrition; avoid potassium deficiency"
        ],
        "cultural_management": "Routinely inspect lower canopy from knee-high stage through grain fill; incorporate stover post-harvest.",
        "biological_management": "Seed biopriming with Trichoderma viride or Pseudomonas fluorescens (10 g/kg seed) reduces early seed-borne infection. Preventive foliar spray of 5% NSKE offers moderate protective suppression under mild pressure.",
        "organic": [
            "Seed biopriming with Trichoderma viride (10 g/kg seed) or Pseudomonas fluorescens (10 g/kg seed) to reduce seed-borne inoculum. Preventive spray of 5% NSKE at initial lesion appearance provides moderate protective suppression."
        ],
        "chemical": [
            "When 2 to 3 lesions appear on leaves below the ear before silking under humid weather forecasts, apply recommended fungicides registered by CIB&RC (Govt. of India) for maize leaf blight: Azoxystrobin 18.2% + Difenoconazole 11.4% w/w SC (1.0 mL/L; 500 mL/ha in 500 L water; 21-day PHI) or Carbendazim 12% + Mancozeb 63% WP. Consult your local agricultural extension officer and use only products registered for this crop and disease in your region. Follow the approved product label."
        ],
        "diagnostic_limitations": "Provisional Classification & Diagnostic Limitations: The training dataset labeled this class simply as 'Blight'. While visual characteristics (elongated cigar-shaped lesions) and dataset provenance (PlantVillage benchmark) strongly indicate Northern Corn Leaf Blight (Exserohilum turcicum), other maize diseases—including Southern Corn Leaf Blight (Bipolaris maydis), Stewart's bacterial wilt, and physiological leaf firing—can cause overlapping necrotic symptoms. Image-based deep learning predictions provide screening guidance only and must not be treated as definitive laboratory or microscopic confirmation. If severe blight symptoms develop, consult an agricultural extension specialist or plant pathology clinic.",
        "safety_warnings": "Observe mandatory pre-harvest intervals (21-day PHI). Wear protective gear and avoid spraying near water bodies."
    },
    "healthy": {
        "display_name": "Healthy Maize Plant",
        "scientific_name": "Zea mays (Healthy)",
        "symptoms": [
            "Uniform vibrant green leaves without chlorotic streaks, necrotic lesions, or pustules",
            "Strong, erect stalk with normal internode spacing and sturdy brace root development",
            "Normal vegetative and reproductive growth appropriate for hybrid phenological stage"
        ],
        "visual_identification": "Uniform green leaf tissue with intact lamina and complete absence of foliar lesions, pustules, or wilting.",
        "causes": "Normal physiological growth free of pathogenic infection.",
        "favorable_conditions": "Balanced soil fertility, well-drained loamy soil, adequate sunlight, and uniform moisture.",
        "prevention": [
            "Apply soil test-based balanced NPK and micronutrient (Zinc, Boron) fertilization",
            "Maintain optimal field drainage to prevent waterlogging, especially at seedling and tasseling stages",
            "Scout fields weekly for invasive pests (e.g. Fall Armyworm) and early disease spots",
            "Practice weed management during the critical first 30-45 days after emergence"
        ],
        "cultural_management": "Timely irrigation, balanced split application of nitrogen, and routine crop scouting.",
        "biological_management": "Incorporate well-decomposed FYM or vermicompost (5-10 t/ha) to enrich soil microbiota. Maintain flowering field borders to conserve beneficial natural insect predators.",
        "organic": [
            "Incorporate well-decomposed farmyard manure (FYM) or vermicompost to foster beneficial soil microflora. Conserve natural predators through ecological field borders."
        ],
        "chemical": [
            "None required for healthy crops. Do not apply synthetic chemical fungicides or prophylactic pesticides to healthy plants."
        ],
        "diagnostic_limitations": "Visual assessment confirms absence of foliar symptoms at the time of inspection. Routine field scouting should continue throughout the season.",
        "safety_warnings": "Do not spray unnecessary chemicals on healthy plants to preserve beneficial insect populations and prevent chemical resistance."
    }
}

# Regional language dictionaries
te_maize = {
    "common_rust": {
        "display_name": "మొక్కజొన్న కుంకుమ తెగులు (కామన్ రస్ట్)",
        "scientific_name": "Puccinia sorghi",
        "symptoms": [
            "ఆకుల పై మరియు కింది భాగాలలో గుండ్రని లేదా పొడవాటి ఎరుపు-గోధుమ రంగు పొక్కులు (కుంకుమ మచ్చలు) ఏర్పడతాయి",
            "పంట కాలం చివరలో ఈ పొక్కులు నల్లగా మారి ఆకులు త్వరగా ఎండిపోతాయి",
            "తీవ్రమైన దశలో ఆకులు ఎండిపోయి గింజ బరువు తగ్గుతుంది"
        ],
        "prevention": [
            "తెగులును తట్టుకునే రకాలను ఎంపిక చేసుకోండి",
            "సకాలంలో విత్తనం వేయడం ద్వారా తెగులు ఉధృతిని తగ్గించవచ్చు",
            "నత్రజని ఎరువులను అధికంగా వాడకుండా సమతుల్య ఎరువులు వేయండి"
        ],
        "organic": [
            "గాలి ద్వారా వ్యాపించే కుంకుమ తెగులుపై జీవ నియంత్రణ ప్రభావం పరిమితం. తెగులు ప్రారంభ దశలో 5% వేప గింజల కషాయం (NSKE) లేదా బాసిల్లస్ సబ్టిలిస్ ద్రావణాన్ని పిచికారీ చేయవచ్చు. విత్తనశుద్ధి ఆకులపై వచ్చే కుంకుమ తెగులును నిరోధించలేదు."
        ],
        "chemical": [
            "పూతకు ముందు ఆకులపై కుంకుమ పొక్కులు కనిపించినప్పుడు మాత్రమే రసాయన మందుల పిచికారీ అవసరం. CIB&RC (భారత ప్రభుత్వం) ఆమోదించిన అజోక్సీస్ట్రోబిన్ ఆధారిత మందులు (ఉదా: అజోక్సీస్ట్రోబిన్ 18.2% + సైప్రోకోనజోల్ 7.3% SC, 1 మి.లీ/లీ) లేదా క్రెసోక్సిమ్-మిథైల్ 44.3% SC (1 మి.లీ/లీ) ఉపయోగించవచ్చు. మీ ప్రాంతంలో ఈ పంట మరియు తెగులుకు రిజిస్టర్ అయిన మందుల వివరాలు, సరైన మోతాదు కోసం స్థానిక వ్యవసాయ విస్తరణాధికారిని సంప్రదించండి. లేబుల్ సూచనలను ఖచ్చితంగా పాటించండి."
        ]
    },
    "gray_leaf_spot": {
        "display_name": "మొక్కజొన్న బూడిద రంగు ఆకుమచ్చ తెగులు (గ్రే లీఫ్ స్పాట్)",
        "scientific_name": "Cercospora zeae-maydis",
        "symptoms": [
            "ఆకుల ఈనెల మధ్య దీర్ఘచతురస్రాకారంలో బూడిద లేదా గోధుమ రంగు మచ్చలు ఏర్పడతాయి",
            "మచ్చలు కలిసిపోయి ఆకులు పూర్తిగా ఎండిపోయి మొక్కలు త్వరగా చనిపోతాయి",
            "మొక్క కాండం బలహీనపడి పడిపోవడం మరియు గింజ ఊరకుండా పోవడం జరుగుతుంది"
        ],
        "prevention": [
            "పంట మార్పిడి పద్ధతిని పాటించండి (పప్పుధాన్యాలు లేదా సోయాబీన్ తో 1-2 సీజన్లు మార్పిడి)",
            "గత పంట వ్యర్థాలను పొలంలో లేకుండా శుభ్రం చేయండి లేదా లోతు దుక్కి చేయండి",
            "తట్టుకునే హైబ్రిడ్ రకాలను సాగు చేయండి",
            "ఎక్కువ మొక్కలు దగ్గరగా నాటకుండా సరైన గాలి వెలుతురు ఉండేలా చూడండి"
        ],
        "organic": [
            "పంట వ్యర్థాల నిర్మూలన: పంట కోత తర్వాత మిగిలిన వ్యర్థాలపై ట్రైకోడెర్మా లేదా బయో-డీకంపోజర్ చల్లడం ద్వారా శిలీంధ్రాల ఉనికిని తగ్గించవచ్చు. తీవ్రమైన దశలో ఆకులపై జీవ శిలీంద్రనాశినుల ప్రభావం పరిమితం."
        ],
        "chemical": [
            "భారతదేశంలో CIB&RC ద్వారా మొక్కజొన్నలో గ్రే లీఫ్ స్పాట్ కోసం ప్రత్యేకంగా ఎటువంటి రసాయన మందు రిజిస్టర్ కాలేదు. మీ ప్రాంతంలో ఈ పంటకు ఆమోదించబడిన రసాయన మందులు మరియు సరైన మోతాదు కొరకు మీ స్థానిక వ్యవసాయ విస్తరణాధికారిని సంప్రదించండి. ఆమోదించబడిన లేబుల్ సూచనలను మాత్రమే పాటించండి."
        ]
    },
    "northern_leaf_blight": {
        "display_name": "మొక్కజొన్న ఆకు ఎండు తెగులు (నార్తర్న్ లీఫ్ బ్లైట్)",
        "scientific_name": "Exserohilum turcicum (syn. Helminthosporium turcicum)",
        "symptoms": [
            "ఆకులపై పొడవాటి చుట్ట ఆకారపు (సిగార్ ఆకారపు) బూడిద-గోధుమ రంగు పెద్ద మచ్చలు (3-15 సెం.మీ) ఏర్పడతాయి",
            "మచ్చలు ఆకు ఈనెలతో సంబంధం లేకుండా వేగంగా విస్తరించి ఆకులను మాడ్చివేస్తాయి (కాలినట్లు కనిపిస్తాయి)",
            "తేమతో కూడిన వాతావరణంలో మచ్చల మధ్య ముదురు ఆకుపచ్చ లేదా నల్లటి బూజు ఏర్పడుతుంది"
        ],
        "prevention": [
            "Ht జన్యువులు కలిగిన తెగులును తట్టుకునే హైబ్రిడ్ విత్తనాలను ఎంచుకోండి",
            "పంట మార్పిడి పాటించండి మరియు సమతుల్య పొటాష్ ఎరువులను అందించండి",
            "హెచ్చరిక మరియు పరిమితులు: శిక్షణ డేటాసెట్ లో ఈ తెగులును 'బ్లైట్' అని మాత్రమే పేర్కొన్నారు. దీని లక్షణాలు నార్తర్న్ లీఫ్ బ్లైట్ తో సరిపోలినప్పటికీ, ఇతర ఆకు ఎండు తెగుళ్లు (సదరన్ బ్లైట్) కూడా ఇలాంటి లక్షణాలనే కలిగిస్తాయి. ఫోటో ఆధారిత నిర్ధారణ కేవలం ప్రాథమిక సూచన మాత్రమే, ఇది ప్రయోగశాల పరీక్ష కాదు. తీవ్రమైన లక్షణాలు ఉంటే వ్యవసాయ నిపుణులను సంప్రదించండి."
        ],
        "organic": [
            "విత్తనం ద్వారా వ్యాపించే తెగులు నివారణకు ట్రైకోడెర్మా విరిడే (10 గ్రా/కిలో విత్తనం) లేదా సుడోమోనాస్ తో విత్తనశుద్ధి చేయండి. ఆకులపై తొలి మచ్చలు కనిపించినప్పుడు 5% వేప గింజల కషాయం (NSKE) పిచికారీ చేయడం వల్ల రక్షణ లభిస్తుంది."
        ],
        "chemical": [
            "పూతకు ముందు కంకి కింద ఆకులపై 2-3 మచ్చలు కనిపించినప్పుడు, CIB&RC ఆమోదించిన అజోక్సీస్ట్రోబిన్ 18.2% + డైఫెనోకోనజోల్ 11.4% SC (1.0 మి.లీ/లీ, 21 రోజుల కోత వ్యవధి) లేదా కార్బెండజిమ్ 12% + మాంకోజెబ్ 63% WP పిచికారీ చేయవచ్చు. మీ ప్రాంతంలో రిజిస్టర్ అయిన మందుల వివరాలు మరియు మోతాదు కొరకు స్థానిక వ్యవసాయ అధికారిని సంప్రదించండి. లేబుల్ సూచనలను పాటించండి."
        ]
    },
    "healthy": {
        "display_name": "ఆరోగ్యకరమైన మొక్కజొన్న మొక్క",
        "scientific_name": "Zea mays (Healthy)",
        "symptoms": [
            "ఆకులు ఎటువంటి మచ్చలు, కుంకుమ పొక్కులు లేకుండా పచ్చగా, బలంగా ఉంటాయి",
            "మొక్క కాండం బలంగా ఉండి సాధారణ ఎదుగుదల కనబరుస్తుంది",
            "క్రిమికీటకాలు లేదా వ్యాధి లక్షణాలు ఏవీ కనిపించవు"
        ],
        "prevention": [
            "మట్టి పరీక్ష ఆధారంగా సమతుల్య ఎరువులు (NPK మరియు జింక్) అందించండి",
            "పొలంలో నీరు నిల్వ ఉండకుండా మురుగు నీటి కాల్వలను నిర్వహించండి",
            "క్రమం తప్పకుండా తెగుళ్లు, పురుగుల (కత్తెర పురుగు) కోసం పొలాన్ని పరిశీలించండి",
            "మొదటి 30-45 రోజుల కీలక దశలో కలుపు లేకుండా చూసుకోండి"
        ],
        "organic": [
            "నాణ్యమైన పశువుల ఎరువు లేదా వర్మీకంపోస్ట్ ను నేలకు అందించి నేల ఆరోగ్యాన్ని కాపాడండి. మిత్రపురుగులను సంరక్షించండి."
        ],
        "chemical": [
            "ఆరోగ్యకరమైన పంటకు ఎటువంటి రసాయన మందులు లేదా పురుగుమందులు అవసరం లేదు. అనవసరంగా రసాయనాలు వాడకండి."
        ]
    }
}

hi_maize = {
    "common_rust": {
        "display_name": "मक्का का सामान्य रतुआ (कॉमन रस्ट)",
        "scientific_name": "Puccinia sorghi",
        "symptoms": [
            "पत्तियों की दोनों सतहों पर छोटे, गोल से लेकर लंबे लाल-भूरे रंग के उभरे हुए फफोले (पुस्ट्यूल) दिखाई देते हैं",
            "रोग बढ़ने पर फफोले भूरे-काले रंग में बदल जाते हैं और पत्तियां सूखने लगती हैं",
            "गंभीर संक्रमण से पत्तियां समय से पहले सूख जाती हैं और दानों का वजन कम हो जाता है"
        ],
        "prevention": [
            "रोग प्रतिरोधी या सहनशील संकर किस्मों का चयन करें",
            "समय पर बुवाई करें ताकि फफूंद के बीजाणुओं के प्रसार से बचा जा सके",
            "संतुलित मात्रा में उर्वरकों का उपयोग करें; अत्यधिक नाइट्रोजन से बचें"
        ],
        "organic": [
            "हवा से फैलने वाले रतुआ रोग पर जैविक नियंत्रण का प्रभाव सीमित होता है। रोग की शुरुआती अवस्था में 5% नीम के बीज के अर्क (NSKE) या बैसिलस सबटिलिस का छिड़काव सुरक्षात्मक असर दे सकता है। जैविक बीज उपचार पत्तियों के रतुआ रोग को नहीं रोकता।"
        ],
        "chemical": [
            "फफूंदनाशक का छिड़काव केवल तभी करें जब भुट्टे में बाल (सिल्किंग) आने से पहले संवेदनशील किस्मों पर रतुआ के फफोले दिखें। केंद्रीय कीटनाशक बोर्ड (CIB&RC, भारत सरकार) द्वारा मक्का रतुआ और झुलसा के लिए एजोक्सीस्ट्रोबिन आधारित संयोजन (उदा. एजोक्सीस्ट्रोबिन 18.2% + साइप्रिकोनाजोल 7.3% SC, 1.0 मिली/लीटर) या क्रेसोक्सिम-मिथाइल 44.3% SC (1.0 मिली/लीटर) पंजीकृत हैं। अपने क्षेत्र में पंजीकृत उत्पाद और सही मात्रा के लिए स्थानीय कृषि प्रसार अधिकारी से सलाह लें। उत्पाद लेबल के निर्देशों का पालन करें।"
        ]
    },
    "gray_leaf_spot": {
        "display_name": "मक्का का ग्रे लीफ स्पॉट (धूसर पत्ती धब्बा)",
        "scientific_name": "Cercospora zeae-maydis",
        "symptoms": [
            "पत्तियों की नसों के बीच आयताकार भूरे या धूसर रंग के लंबे धब्बे (1-6 सेमी) बनते हैं",
            "धब्बे आपस में मिलकर पूरी पत्ती को सुखा देते हैं, जिससे पौधे कमजोर होकर गिर सकते हैं",
            "समय से पहले पत्तियां मरने से दानों का भराव ठीक से नहीं हो पाता"
        ],
        "prevention": [
            "दलहनी फसलों या सोयाबीन के साथ 1-2 वर्ष का फसल चक्र अपनाएं",
            "पिछली फसल के अवशेषों को नष्ट करें या गहरी जुताई कर मिट्टी में मिलाएं",
            "सहनशील संकर बीजों की बुवाई करें",
            "पौधों के बीच उचित दूरी रखें ताकि हवा का संचार बना रहे"
        ],
        "organic": [
            "फसल अवशेष प्रबंधन: फसल कटाई के बाद अवशेषों पर ट्राइकोडर्मा या बायो-डीकंपोजर डालने से फफूंद के जीवित रहने की संभावना कम होती है। गंभीर संक्रमण में पत्तियों पर जैविक छिड़काव का प्रभाव सीमित होता है।"
        ],
        "chemical": [
            "भारत में CIB&RC द्वारा मक्का में ग्रे लीफ स्पॉट के लिए विशेष रूप से कोई रासायनिक कवकनाशी पंजीकृत नहीं है। अपने क्षेत्र में इस फसल के लिए स्वीकृत रसायनों और सही मार्गदर्शन के लिए अपने स्थानीय कृषि प्रसार अधिकारी से परामर्श लें। केवल अनुमोदित उत्पाद लेबल का पालन करें।"
        ]
    },
    "northern_leaf_blight": {
        "display_name": "मक्का का उत्तरी पत्ती झुलसा (नार्दर्न लीफ ब्लाइट)",
        "scientific_name": "Exserohilum turcicum (syn. Helminthosporium turcicum)",
        "symptoms": [
            "पत्तियों पर लंबे, सिगार के आकार के (नाव जैसे) धूसर-हरे से भूरे रंग के बड़े धब्बे (3-15 सेमी) बनते हैं",
            "धब्बे नसों की सीमा को पार करते हुए तेजी से फैलते हैं और पत्तियां झुलसी हुई नजर आती हैं",
            "नम मौसम में धब्बों के केंद्र में गहरे जैतून-हरे से काले रंग के फफूंद बीजाणु बनते हैं"
        ],
        "prevention": [
            "Ht जीन युक्त रोग प्रतिरोधी किस्मों की बुवाई करें",
            "फसल चक्र अपनाएं और संतुलित पोटाश व नाइट्रोजन उर्वरक दें",
            "निदान सीमाएं एवं अनिश्चितता: डेटासेट में इसे केवल 'ब्लाइट' नाम दिया गया था। इसके लक्षण नार्दर्न लीफ ब्लाइट से मेल खाते हैं, लेकिन अन्य झुलसा रोग (जैसे साउदर्न ब्लाइट) भी ऐसे ही लक्षण पैदा कर सकते हैं। फोटो आधारित पहचान केवल एक प्रारंभिक जांच है, इसे प्रयोगशाला पुष्टि न मानें। गंभीर लक्षण होने पर कृषि विशेषज्ञ से संपर्क करें।"
        ],
        "organic": [
            "बीज जनित संक्रमण कम करने के लिए ट्राइकोडर्मा विरिडी (10 ग्राम/किग्रा बीज) या स्यूडोमोनास फ्लोरेसेंस से बीज शोधन करें। पत्तियों पर शुरुआती लक्षण दिखने पर 5% नीम अर्क (NSKE) का छिड़काव मध्यम सुरक्षा प्रदान करता है।"
        ],
        "chemical": [
            "जब बाल निकलने से पहले भुट्टे के नीचे की पत्तियों पर 2-3 धब्बे दिखें, तो CIB&RC द्वारा पंजीकृत फफूंदनाशक: एजोक्सीस्ट्रोबिन 18.2% + डाइफेनोकोनाजोल 11.4% SC (1.0 मिली/लीटर; 21 दिन की तुड़ाई पूर्व अवधि) या कार्बेन्डाजिम 12% + मैंकोजेब 63% WP का उपयोग किया जा सकता है। स्थानीय कृषि अधिकारी से परामर्श लें और उत्पाद लेबल के निर्देशों का कड़ाई से पालन करें।"
        ]
    },
    "healthy": {
        "display_name": "स्वस्थ मक्का का पौधा",
        "scientific_name": "Zea mays (Healthy)",
        "symptoms": [
            "पत्तियां किसी भी प्रकार के धब्बे या फफोले से मुक्त, चमकदार हरी और मजबूत होती हैं",
            "पौधे का तना मजबूत और सामान्य वानस्पतिक विकास प्रदर्शित करता है",
            "पौधे में किसी कीट या रोग के लक्षण नहीं होते"
        ],
        "prevention": [
            "मृदा परीक्षण के आधार पर संतुलित NPK और जिंक खाद का प्रयोग करें",
            "खेत में जलभराव न होने दें और उचित जल निकासी की व्यवस्था रखें",
            "कीटों (जैसे फॉल आर्मीवॉर्म) और रोगों की समय-समय पर निगरानी करें",
            "बुवाई के शुरुआती 30-45 दिनों में खरपतवार नियंत्रण पर ध्यान दें"
        ],
        "organic": [
            "अच्छी तरह सड़ी गोबर की खाद या वर्मीकम्पोस्ट (5-10 टन/हेक्टेयर) का प्रयोग करें। मित्र कीटों के संरक्षण के लिए खेत की मेड़ों पर जैव विविधता बनाए रखें।"
        ],
        "chemical": [
            "स्वस्थ फसल में किसी रासायनिक कीटनाशक या फफूंदनाशक के छिड़काव की आवश्यकता नहीं है। अनावश्यक रसायनों का प्रयोग न करें।"
        ]
    }
}

ta_maize = {
    "common_rust": {
        "display_name": "மக்காச்சோள பொது துரு நோய் (காமன் ரஸ்ட்)",
        "scientific_name": "Puccinia sorghi",
        "symptoms": [
            "இலைகளின் இருபுறங்களிலும் சிறிய, வட்டமான செம்பழுப்பு நிற கொப்புளங்கள் தோன்றும்",
            "பருவத்தின் இறுதியில் கொப்புளங்கள் கருப்பாக மாறி இலைகள் காய்ந்துவிடும்",
            "கடுமையான பாதிப்பில் இலைகள் காய்ந்து தானிய எடை குறையும்"
        ],
        "prevention": [
            "நோய் எதிர்ப்புத்திறன் கொண்ட கலப்பின விதைகளை பயிரிடுங்கள்",
            "பருவத்தில் சரியான நேரத்தில் விதைப்பு செய்யுங்கள்",
            "தழைச்சத்தை அளவுக்கு அதிகமாக இடுவதைத் தவிர்க்கவும்"
        ],
        "organic": [
            "காற்று மூலம் பரவும் துரு நோய்க்கு உயிரியல் கட்டுப்பாடு குறைந்த பலனையே தரும். ஆரம்ப நிலையில் 5% வேப்பங்கொட்டை சாறு (NSKE) தெளிப்பது சிறிய பாதுகாப்பு தரும். விதை நேர்த்தி இலை துரு நோயை கட்டுப்படுத்தாது."
        ],
        "chemical": [
            "பூப்பதற்கு முன் இலைகளில் கொப்புளங்கள் தென்பட்டால் மட்டுமே தெளிக்க வேண்டும். CIB&RC அங்கீகரித்த அசாசிஸ்ட்ரோபின் கலவை (அசாசிஸ்ட்ரோபின் 18.2% + சைப்ரோகோனசோல் 7.3% SC, 1.0 மி.லி/லிட்டர்) பயன்படுத்தலாம். வட்டார வேளாண் விரிவாக்க அலுவலரை அணுகி உங்கள் பகுதிக்கு அங்கீகரிக்கப்பட்ட மருந்துகளை லேபிள் வழிகாட்டுதலின்படி பயன்படுத்தவும்."
        ]
    },
    "gray_leaf_spot": {
        "display_name": "மக்காச்சோள சாம்பல் இலைப்புள்ளி நோய் (கிரே லீப் ஸ்பாட்)",
        "scientific_name": "Cercospora zeae-maydis",
        "symptoms": [
            "இலை நரம்புகளுக்கு இடையே செவ்வக வடிவிலான சாம்பல் அல்லது பழுப்பு நிற புள்ளிகள் (1-6 செ.மீ) தோன்றும்",
            "புள்ளிகள் ஒன்றுசேர்ந்து இலைகளை முற்றிலும் கருகச் செய்யும்",
            "தண்டு பலவீனமடைந்து சாய்ந்துவிடும் மற்றும் மகசூல் குறையும்"
        ],
        "prevention": [
            "பயறு வகைகளுடன் 1-2 பருவங்களுக்கு பயிர் சுழற்சி முறையை கடைப்பிடிக்கவும்",
            "பயிர்க் கழிவுகளை அகற்றவும் அல்லது ஆழ உழவு செய்யவும்",
            "எதிர்ப்புத்திறன் கொண்ட விதைகளை பயிரிடவும்"
        ],
        "organic": [
            "பயிர்க் கழிவுகளின் மேல் டிரைக்கோடெர்மா அல்லது மக்கும் நுண்ணுயிரிகளை தெளித்து உழவு செய்யவும். கடுமையான நோய் பாதிப்பில் இலை தெளிப்பு குறைந்த பலனையே தரும்."
        ],
        "chemical": [
            "இந்தியாவில் CIB&RC மூலம் மக்காச்சோள கிரே லீப் ஸ்பாட் நோய்க்கு என தனியாக ரசாயன மருந்துகள் அங்கீகரிக்கப்படவில்லை. உங்கள் பகுதிக்கு அங்கீகரிக்கப்பட்ட மருந்துகள் குறித்து வட்டார வேளாண் விரிவாக்க அலுவலரை அணுகி ஆலோசிக்கவும்."
        ]
    },
    "northern_leaf_blight": {
        "display_name": "மக்காச்சோள வடக்கு இலை கருகல் நோய் (நார்தர்ன் லீப் பிளைட்)",
        "scientific_name": "Exserohilum turcicum (syn. Helminthosporium turcicum)",
        "symptoms": [
            "இலைகளில் நீண்ட படகு அல்லது சுருட்டு வடிவ சாம்பல்-பழுப்பு நிற பெரிய கருகல் புள்ளிகள் (3-15 செ.மீ) தோன்றும்",
            "புள்ளிகள் நரம்புகளை கடந்து பரவி இலைகளை முற்றிலும் கருகச் செய்யும்",
            "ஈரமான காலநிலையில் புள்ளிகளின் நடுவே கரும்பச்சை அல்லது கருமை நிற பூஞ்சை படலம் உருவாகும்"
        ],
        "prevention": [
            "எதிர்ப்புத்திறன் கொண்ட கலப்பின ரகங்களை தேர்வு செய்யவும்",
            "சமச்சீர் உர மேலாண்மை மற்றும் பொட்டாஷ் இடவும்",
            "அடையாள வரம்புகள்: மூலத் தரவில் இது 'பிளைட்' என மட்டுமே குறிப்பிடப்பட்டுள்ளது. இதன் அறிகுறிகள் வடக்கு இலை கருகலுடன் ஒத்துப்போனாலும், பிற கருகல் நோய்களும் இதே போன்ற தோற்றத்தை ஏற்படுத்தலாம். புகைப்பட கணிப்பு ஆரம்ப வழிகாட்டுதல் மட்டுமே; ஆய்வக உறுதிப்படுத்தல் அல்ல. சந்தேகம் இருப்பின் வேளாண் அதிகாரிகளை அணுகவும்."
        ],
        "organic": [
            "டிரைக்கோடெர்மா விரிடி (10 கிராம்/கிலோ விதை) கொண்டு விதை நேர்த்தி செய்யவும். இலைகளில் ஆரம்ப அறிகுறிகள் தென்படும்போது 5% வேப்பங்கொட்டை சாறு தெளிக்கவும்."
        ],
        "chemical": [
            "பூப்பதற்கு முன் கதிர் இலைக்கு கீழே உள்ள இலைகளில் 2-3 புள்ளிகள் தென்படும்போது, CIB&RC அங்கீகரித்த அசாசிஸ்ட்ரோபின் 18.2% + டைபனோகோனசோல் 11.4% SC (1.0 மி.லி/லிட்டர்; 21 நாட்கள் அறுவடை இடைவெளி) பயன்படுத்தலாம். வேளாண் அலுவலரின் வழிகாட்டுதல்களைப் பின்பற்றவும்."
        ]
    },
    "healthy": {
        "display_name": "ஆரோக்கியமான மக்காச்சோள பயிர்",
        "scientific_name": "Zea mays (Healthy)",
        "symptoms": [
            "இலைகளில் எவ்வித புள்ளிகளும் பூஞ்சைகளும் இல்லாமல் பசுமையாகவும் ஆரோக்கியமாகவும் இருக்கும்",
            "தண்டு உறுதியாகவும் முறையான வளர்ச்சியுடனும் காணப்படும்"
        ],
        "prevention": [
            "மண் பரிசோதனை அடிப்படையில் சமச்சீர் உரம் மற்றும் துத்தநாகம் இடவும்",
            "பாசன நீர் தேங்காமல் வடிகால் வசதி அமைக்கவும்",
            "வழக்கமான கள ஆய்வு மேற்கொள்ளவும்"
        ],
        "organic": [
            "மட்கிய தொழுவுரம் அல்லது மண்புழு உரம் இடவும். நன்மை செய்யும் பூச்சிகளை பாதுகாக்கவும்."
        ],
        "chemical": [
            "ஆரோக்கியமான பயிர்களுக்கு எந்தவொரு ரசாயன பூஞ்சைக்கொல்லியோ அல்லது பூச்சிக்கொல்லியோ தேவையில்லை."
        ]
    }
}

kn_maize = {
    "common_rust": {
        "display_name": "ಮೆಕ್ಕೆಜೋಳದ ತುಕ್ಕು ರೋಗ (ಕಾಮನ್ ರಸ್ಟ್)",
        "scientific_name": "Puccinia sorghi",
        "symptoms": [
            "ಎಲೆಗಳ ಎರಡೂ ಬದಿಗಳಲ್ಲಿ ಸಣ್ಣ, ದುಂಡಗಿನ ಅಥವಾ ಉದ್ದನೆಯ ಕೆಂಪು-ಕಂದು ಬಣ್ಣದ ಪುಡಿ ತುಂಬಿದ ಗುಳ್ಳೆಗಳು ಕಾಣಿಸಿಕೊಳ್ಳುತ್ತವೆ",
            "ರೋಗ ಉಲ್ಬಣಿಸಿದಾಗ ಗುಳ್ಳೆಗಳು ಕಪ್ಪು ಬಣ್ಣಕ್ಕೆ ತಿರುಗಿ ಎಲೆಗಳು ಒಣಗುತ್ತವೆ",
            "ತೀವ್ರ ಹಂತದಲ್ಲಿ ಎಲೆಗಳು ನಾಶವಾಗಿ ಕಾಳುಗಳ ತೂಕ ಕಡಿಮೆಯಾಗುತ್ತದೆ"
        ],
        "prevention": [
            "ರೋಗ ನಿರೋಧಕ ತಳಿಗಳನ್ನು ಆಯ್ಕೆ ಮಾಡಿ",
            "ಸಕಾಲದಲ್ಲಿ ಬಿತ್ತನೆ ಮಾಡಿ ಮತ್ತು ಸಾರಜನಕ ಗೊಬ್ಬರದ ಅತಿಯಾದ ಬಳಕೆಯನ್ನು ತಪ್ಪಿಸಿ"
        ],
        "organic": [
            "ಗಾಳಿಯ ಮೂಲಕ ಹರಡುವ ತುಕ್ಕು ರೋಗಕ್ಕೆ ಜೈವಿಕ ನಿಯಂತ್ರಣದ ಪ್ರಭಾವ ಸೀಮಿತ. ಆರಂಭಿಕ ಹಂತದಲ್ಲಿ 5% ಬೇವಿನ ಬೀಜದ ಕಷಾಯ (NSKE) ಅಥವಾ ಬ್ಯಾಸಿಲಸ್ ಸಬ್ಟಿಲಿಸ್ ಸಿಂಪಡಿಸಬಹುದು. ಬೀಜೋಪಚಾರವು ಎಲೆ ತುಕ್ಕು ರೋಗವನ್ನು ನಿಯಂತ್ರಿಸುವುದಿಲ್ಲ."
        ],
        "chemical": [
            "ತೆನೆ ಮೂಡುವ ಮುನ್ನ ರೋಗದ ಗುಳ್ಳೆಗಳು ಕಂಡುಬಂದಾಗ ಮಾತ್ರ ಸಿಂಪರಣೆ ಅಗತ್ಯ. CIB&RC ನೋಂದಾಯಿತ ಅಜೋಕ್ಸಿಸ್ಟ್ರೋಬಿನ್ ಸಂಯೋಜನೆ (ಅಜೋಕ್ಸಿಸ್ಟ್ರೋಬಿನ್ 18.2% + ಸೈಪ್ರೊಕೊನಾಜೋಲ್ 7.3% SC, 1.0 ಮಿ.ಲೀ/ಲೀಟರ್) ಬಳಸಬಹುದು. ನಿಮ್ಮ ಭಾಗದ ಅಧಿಕೃತ ಔಷಧ ಮತ್ತು ಪ್ರಮಾಣಕ್ಕಾಗಿ ಸ್ಥಳೀಯ ಕೃಷಿ ಅಧಿಕಾರಿಯನ್ನು ಸಂಪರ್ಕಿಸಿ ಲೇಬಲ್ ಸೂಚನೆ ಪಾಲಿಸಿ."
        ]
    },
    "gray_leaf_spot": {
        "display_name": "ಮೆಕ್ಕೆಜೋಳದ ಬೂದು ಎಲೆ ಚುಕ್ಕೆ ರೋಗ (ಗ್ರೇ ಲೀಫ್ ಸ್ಪಾಟ್)",
        "scientific_name": "Cercospora zeae-maydis",
        "symptoms": [
            "ಎಲೆಯ ನರಗಳ ನಡುವೆ ಆಯತಾಕಾರದ ಬೂದು ಅಥವಾ ಕಂದು ಬಣ್ಣದ ಚುಕ್ಕೆಗಳು (1-6 ಸೆಂ.ಮೀ) ಉಂಟಾಗುತ್ತವೆ",
            "ಚುಕ್ಕೆಗಳು ಒಟ್ಟಾಗಿ ಹರಡಿ ಇಡೀ ಎಲೆಯು ಒಣಗಿ ಹೋಗುತ್ತದೆ",
            "ಸಸ್ಯದ ಕಾಂಡ ದುರ್ಬಲಗೊಂಡು ಬೀಳುವುದು ಮತ್ತು ಇಳುವರಿ ಕಡಿಮೆಯಾಗುತ್ತದೆ"
        ],
        "prevention": [
            "ದ್ವಿದಳ ಧಾನ್ಯಗಳೊಂದಿಗೆ 1-2 ಋತುಗಳ ಬೆಳೆ ಪರಿವರ್ತನೆ ಮಾಡಿ",
            "ಹಿಂದಿನ ಬೆಳೆಯ ಉಳಿಕೆಗಳನ್ನು ಆಳವಾಗಿ ಉಳುಮೆ ಮಾಡಿ ಮಣ್ಣಿನಲ್ಲಿ ಸೇರಿಸಿ",
            "ರೋಗ ನಿರೋಧಕ ಹೈಬ್ರಿಡ್ ತಳಿಗಳನ್ನು ಬೆಳೆಯಿರಿ"
        ],
        "organic": [
            "ಬೆಳೆ ತ್ಯಾಜ್ಯ ನಿರ್ವಹಣೆ: ಕೊಯ್ಲಿನ ನಂತರ ಬೆಳೆ ಉಳಿಕೆಗಳ ಮೇಲೆ ಟ್ರೈಕೋಡರ್ಮಾ ಸಿಂಪಡಿಸಿ ಉಳುಮೆ ಮಾಡಿ. ತೀವ್ರ ಹಂತದಲ್ಲಿ ಎಲೆಗಳ ಮೇಲಿನ ಜೈವಿಕ ಸಿಂಪರಣೆ ಸೀಮಿತ ಫಲಿತಾಂಶ ನೀಡುತ್ತದೆ."
        ],
        "chemical": [
            "ಭಾರತದಲ್ಲಿ CIB&RC ವತಿಯಿಂದ ಮೆಕ್ಕೆಜೋಳದ ಗ್ರೇ ಲೀಫ್ ಸ್ಪಾಟ್ ರೋಗಕ್ಕೆ ಯಾವುದೇ ನಿರ್ದಿಷ್ಟ ರಾಸಾಯನಿಕ ಶಿಲೀಂಧ್ರನಾಶಕ ನೋಂದಣಿಯಾಗಿಲ್ಲ. ನಿಮ್ಮ ಭಾಗಕ್ಕೆ ಸೂಕ್ತವಾದ ನೋಂದಾಯಿತ ಔಷಧಗಳಿಗಾಗಿ ಸ್ಥಳೀಯ ಕೃಷಿ ಅಧಿಕಾರಿಗಳನ್ನು ಸಂಪರ್ಕಿಸಿ."
        ]
    },
    "northern_leaf_blight": {
        "display_name": "ಮೆಕ್ಕೆಜೋಳದ ಉತ್ತರದ ಎಲೆ ಸುಟ್ಟ ರೋಗ (ನಾರ್ದರ್ನ್ ಲೀಫ್ ಬ್ಲೈಟ್)",
        "scientific_name": "Exserohilum turcicum (syn. Helminthosporium turcicum)",
        "symptoms": [
            "ಎಲೆಗಳ ಮೇಲೆ ಉದ್ದನೆಯ ಸುರುಳಿ (ಸಿಗಾರ್) ಆಕಾರದ ಬೂದು-ಕಂದು ಬಣ್ಣದ ದೊಡ್ಡ ಕಲೆಗಳು (3-15 ಸೆಂ.ಮೀ) ಉಂಟಾಗುತ್ತವೆ",
            "ಕಲೆಗಳು ನರಗಳನ್ನು ಮೀರಿ ಹರಡಿ ಎಲೆಗಳು ಸುಟ್ಟಂತೆ ಒಣಗುತ್ತವೆ",
            "ತೇವಾಂಶದ ವಾತಾವರಣದಲ್ಲಿ ಕಲೆಗಳ ಮಧ್ಯಭಾಗದಲ್ಲಿ ಕಡು ಹಸಿರು ಅಥವಾ ಕಪ್ಪು ಬಣ್ಣದ ಬೂజు ಬೆಳೆಯುತ್ತದೆ"
        ],
        "prevention": [
            "Ht ಜೀನ್ ಹೊಂದಿರುವ ರೋಗ ನಿರೋಧಕ ತಳಿಗಳನ್ನು ಬೆಳೆಯಿರಿ",
            "ಬೆಳೆ ಸರದಿ ಪಾಲಿಸಿ ಮತ್ತು ಪೊಟ್ಯಾಷ್ ಗೊಬ್ಬರವನ್ನು ಸಮತೋಲನದಲ್ಲಿ ನೀಡಿ",
            "ಮಿತಿಗಳು ಮತ್ತು ಎಚ್ಚರಿಕೆ: ಡೇಟಾಸೆಟ್‌ನಲ್ಲಿ ಇದನ್ನು ಕೇವಲ 'ಬ್ಲೈಟ್' ಎಂದು ನಮೂದಿಸಲಾಗಿದೆ. ಇದರ ಲಕ್ಷಣಗಳು ನಾರ್ದರ್ನ್ ಲೀಫ್ ಬ್ಲೈಟ್‌ಗೆ ಹೋಲುತ್ತವೆಯಾದರೂ, ಇತರ ಎಲೆ ರೋಗಗಳೂ ಇದೇ ರೀತಿಯ ಲಕ್ಷಣಗಳನ್ನು ಉಂಟುಮಾಡಬಹುದು. ಫೋಟೋ ಆಧಾರಿತ ಪತ್ತೆಯು ಕೇವಲ ಪ್ರಾಥಮಿಕ ತಪಾಸಣೆಯಾಗಿದ್ದು, ಪ್ರಯೋಗಾಲಯ ದೃಢೀಕರಣವಲ್ಲ. ತೀವ್ರ ಲಕ್ಷಣಗಳಿದ್ದಲ್ಲಿ ಕೃಷಿ ತಜ್ಞರನ್ನು ಭೇಟಿ ಮಾಡಿ."
        ],
        "organic": [
            "ಬೀಜ-ಮೂಲದ ಸೋಂಕು ತಡೆಗಟ್ಟಲು ಟ್ರೈಕೋಡರ್ಮಾ ವಿರಿಡೆ (10 ಗ್ರಾಂ/ಕೆಜಿ ಬೀಜ) ಯಿಂದ ಬೀಜೋಪಚಾರ ಮಾಡಿ. ಎಲೆಗಳ ಮೇಲೆ ಆರಂಭಿಕ ಚುಕ್ಕೆಗಳು ಕಂಡಾಗ 5% ಬೇವಿನ ಬೀಜದ ಕಷಾಯ ಸಿಂಪಡಿಸಿ."
        ],
        "chemical": [
            "ತೆನೆ ಬರುವ ಮುನ್ನ ಎಲೆಗಳ ಮೇಲೆ 2-3 ಚುಕ್ಕೆಗಳು ಕಂಡಾಗ, CIB&RC ಅನುಮೋದಿತ ಅಜೋಕ್ಸಿಸ್ಟ್ರೋಬಿನ್ 18.2% + ಡೈಫೆನೊಕೊನಾಜೋಲ್ 11.4% SC (1.0 ಮಿ.ಲೀ/ಲೀಟರ್; 21 ದಿನಗಳ ಕೊಯ್ಲು ಪೂರ್ವ ಅವಧಿ) ಬಳಸಬಹುದು. ಅಧಿಕೃತ ಲೇಬಲ್ ಸೂಚನೆಗಳನ್ನು ತಪ್ಪದೇ ಪಾಲಿಸಿ."
        ]
    },
    "healthy": {
        "display_name": "ಆರೋಗ್ಯಕರ ಮೆಕ್ಕೆಜೋಳದ ಸಸ್ಯ",
        "scientific_name": "Zea mays (Healthy)",
        "symptoms": [
            "ಎಲೆಗಳು ಯಾವುದೇ ಚುಕ್ಕೆ ಅಥವಾ ಗುಳ್ಳೆಗಳಿಲ್ಲದೆ ದಟ್ಟ ಹಸಿರಾಗಿದ್ದು ಬಲಿಷ್ಠವಾಗಿರುತ್ತವೆ",
            "ಕಾಂಡವು ಗಟ್ಟಿಯಾಗಿದ್ದು ಸಮರ್ಪಕ ಬೆಳವಣಿಗೆ ಹೊಂದಿರುತ್ತದೆ",
            "ಕೀಟ ಅಥವಾ ರೋಗದ ಯಾವುದೇ ಬಾಧೆ ಇರುವುದಿಲ್ಲ"
        ],
        "prevention": [
            "ಮಣ್ಣು ಪರೀಕ್ಷೆಯ ಆಧಾರದ ಮೇಲೆ ಸಮತೋಲಿತ ಗೊಬ್ಬರ (NPK ಮತ್ತು ಸತು) ನೀಡಿ",
            "ಜಮೀನಿನಲ್ಲಿ ನೀರು ನಿಲ್ಲದಂತೆ ಉತ್ತಮ ಬಸಿಗಾಲುವೆ ವ್ಯವಸ್ಥೆ ಕಲ್ಪಿಸಿ",
            "ನಿಯಮಿತವಾಗಿ ಬೆಳೆ ಪರಿಶೀಲನೆ ನಡೆಸಿ"
        ],
        "organic": [
            "ಉತ್ತಮವಾಗಿ ಕಳಿತ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ ಅಥವಾ ಎರೆಹುಳು ಗೊಬ್ಬರ ಬಳಸಿ. ಮಿತ್ರ ಕೀಟಗಳನ್ನು ಸಂರಕ್ಷಿಸಿ."
        ],
        "chemical": [
            "ಆರೋಗ್ಯಕರ ಬೆಳೆಗೆ ಯಾವುದೇ ರಾಸಾಯನಿಕ ಔಷಧಿ ಸಿಂಪಡಣೆ ಅಗತ್ಯವಿಲ್ಲ. ಅನಗತ್ಯವಾಗಿ ರಾಸಾಯನಿಕಗಳನ್ನು ಬಳಸಬೇಡಿ."
        ]
    }
}

# Attach English to translations.json under 'en'
if "en" not in trans_data["diseases"]:
    trans_data["diseases"]["en"] = {}
for did, data in en_maize.items():
    trans_data["diseases"]["en"][did] = data

# Attach Telugu, Hindi, Tamil, Kannada
for lang, mapping in [("te", te_maize), ("hi", hi_maize), ("ta", ta_maize), ("kn", kn_maize)]:
    for did, data in mapping.items():
        # Add backwards-compatible alias 'organic' and 'chemical' as well as new fields
        trans_data["diseases"][lang][did] = data

with translations_file.open("w", encoding="utf-8") as f:
    json.dump(trans_data, f, indent=2, ensure_ascii=False)

print(f"Updated {translations_file} with refined translations across all 5 languages.")

