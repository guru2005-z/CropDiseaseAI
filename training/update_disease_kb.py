"""Script to populate Groundnut diseases in diseases.json and translations.json."""

from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DISEASES_JSON = PROJECT_ROOT / "disease_data" / "diseases.json"
TRANSLATIONS_JSON = PROJECT_ROOT / "disease_data" / "translations.json"

GROUNDNUT_DISEASES = [
    {
        "crop": "groundnut",
        "disease_id": "early_leaf_spot",
        "display_name": "Early Leaf Spot of Groundnut (Tikka Disease)",
        "scientific_name": "Cercospora arachidicola (syn. Mycosphaerella arachidis)",
        "disease_type": "Fungal",
        "affected_parts": ["Leaflets", "Petioles", "Stems"],
        "symptoms": [
            "Subcircular reddish-brown to dark-brown spots (1-10 mm diameter) predominantly on upper leaf surfaces",
            "Distinct, prominent bright yellow chlorotic halo characteristically surrounding each lesion",
            "Severe infection leads to leaflet chlorosis, premature defoliation, and reduced pod yield"
        ],
        "visual_identification": (
            "Subcircular reddish-brown spots with prominent bright yellow halos appearing primarily on the upper leaflet "
            "surface about 3 to 4 weeks after emergence. Distinct from Late Leaf Spot, which produces darker, nearly black "
            "spots on the lower leaf surface with indistinct or absent halos."
        ),
        "possible_causes": [
            "Soil-borne conidia and infected groundnut crop residue from previous seasons",
            "Prolonged high relative humidity (>80%), moderate temperatures (25-30°C), and extended leaf wetness from rain or dew"
        ],
        "favorable_conditions": "Warm temperatures (25-30°C), persistent relative humidity (>80%), and frequent rainfall or heavy morning dew.",
        "prevention": [
            "Practice 2-year crop rotation with non-legume crops (sorghum, maize, or pearl millet)",
            "Perform deep summer ploughing to bury crop residue and fungal conidia",
            "Sow disease-tolerant or resistant cultivars (e.g., Kadiri-6, Girnar, ICGV series) adapted to the agro-climatic zone",
            "Maintain optimal spacing (30 x 10 cm) to allow canopy aeration and reduce microclimate humidity"
        ],
        "cultural_management": [
            "Eradicate volunteer groundnut plants and remove infected debris post-harvest",
            "Avoid overhead sprinkler irrigation late in the evening to prevent prolonged leaf wetness"
        ],
        "management": [
            "Initiate scouting 3-4 weeks after sowing; apply intervention when spot incidence reaches economic threshold level (5-10% infected leaflets)"
        ],
        "biological_management": [
            "Seed treatment with Trichoderma viride or Trichoderma harzianum (4-5 g/kg seed) or Pseudomonas fluorescens (10 g/kg seed) to suppress early soil-borne inoculum.",
            "Preventive foliar application of 5% Neem Seed Kernel Extract (NSKE; 50 g/L) or neem oil (3%) at initial lesion onset offers moderate protective suppression. (Reference: ICAR-DGR Technical Bulletin on Groundnut Diseases)."
        ],
        "organic_management": [
            "Seed biopriming with Trichoderma viride (4-5 g/kg seed). Foliar application of 5% Neem Seed Kernel Extract (NSKE) at earliest lesion appearance provides protective suppression under mild disease pressure."
        ],
        "chemical_management": [
            "When leaf spots reach economic threshold (5-10% leaflet severity), apply CIB&RC / PPQS registered fungicides: (1) Carbendazim 12% + Mancozeb 63% WP: 1,000 g formulation/ha in 500 L water (2.0 g/L); Pre-Harvest Interval (PHI): 30 days. (2) Tebuconazole 25.9% m/m EC: 500-750 mL/ha in 500 L water (1.0-1.5 mL/L); Pre-Harvest Interval (PHI): 49 days. (3) Hexaconazole 5% SC: 1,000 mL/ha in 500 L water (2.0 mL/L); Pre-Harvest Interval (PHI): 30 days. Consult your local agricultural extension officer and follow the approved product label."
        ],
        "diagnostic_limitations": "Early leaf spot lesions can be confused with early stages of Late Leaf Spot or chemical phytotoxicity burn. Confirmatory identification requires inspecting the yellow halo on the upper surface and microscopic verification of Cercospora conidia.",
        "safety_warnings": "Observe mandatory Pre-Harvest Intervals (30 days for Carbendazim+Mancozeb WP; 49 days for Tebuconazole EC). Wear protective equipment during preparation and spraying. Do not feed treated crop stover to cattle before the PHI has elapsed.",
        "severity_notes": "One of the two major foliar diseases comprising the Groundnut Tikka complex; can cause 15% to 50% pod and haulm yield reduction if left unmanaged.",
        "source": "ICAR-Directorate of Groundnut Research (ICAR-DGR), Junagadh & CIB&RC Major Uses of Pesticides (ppqs.gov.in)",
        "last_reviewed": "2026-11-18"
    },
    {
        "crop": "groundnut",
        "disease_id": "late_leaf_spot",
        "display_name": "Late Leaf Spot of Groundnut (Tikka Disease)",
        "scientific_name": "Phaeoisariopsis personata (syn. Cercosporidium personatum / Mycosphaerella berkeleyi)",
        "disease_type": "Fungal",
        "affected_parts": ["Leaflets", "Petioles", "Stems", "Pegs"],
        "symptoms": [
            "Nearly circular, dark brown to carbonaceous black spots (1-6 mm diameter) appearing primarily on lower leaf surfaces",
            "Lesions typically lack a distinct yellow halo or possess only a very narrow, faint halo",
            "Dense carbonaceous velvety concentric rings of fungal conidiophores visible on the underside of spots",
            "Severe infection leads to rapid extensive defoliation, leaving bare stems with only top leaflets intact"
        ],
        "visual_identification": (
            "Dark brown to jet-black spots that are distinctly darker and more pronounced on the abaxial (lower) leaf surface, "
            "with rough velvety cushions of conidiophores. Differs from Early Leaf Spot, which is lighter reddish-brown with a "
            "prominent bright yellow halo predominantly on the upper leaf surface."
        ),
        "possible_causes": [
            "Crop residue, infected seed pods, and wind-borne conidia surviving in soil from previous groundnut cultivation",
            "High relative humidity (>85%), temperatures between 20-26°C, and prolonged leaf wetness (8+ hours)"
        ],
        "favorable_conditions": "Cooler to moderate temperatures (20-26°C), persistent cloud cover, relative humidity exceeding 85%, and frequent morning dews.",
        "prevention": [
            "Rotate crops with non-host cereals (pearl millet, sorghum, maize) for 2 seasons",
            "Adopt wider row spacing (30-40 cm) to facilitate air circulation and rapid leaf drying",
            "Cultivate tolerant varieties (e.g. Girnar-2, Girnar-3, GPBD-4, ICGV series)",
            "Collect and burn or deeply bury infected haulms post-harvest"
        ],
        "cultural_management": [
            "Intercrop groundnut with pearl millet or pigeon pea (4:1 or 6:1 ratio) to slow aerial spore dispersal",
            "Avoid water stress during vegetative growth followed by excessive canopy moisture"
        ],
        "management": [
            "Regularly inspect lower canopy leaves starting 50-60 days after sowing (flowering/pegging stages); treat when 2-3 spots per leaf are observed"
        ],
        "biological_management": [
            "Seed biopriming with Trichoderma viride or T. harzianum (4-5 g/kg seed) plus Pseudomonas fluorescens (10 g/kg seed).",
            "Preventive foliar spray of 5% Neem Seed Kernel Extract (NSKE) or Trichoderma viride formulation (5 g/L) provides partial disease suppression under low-to-moderate disease pressure. (Reference: ICAR-DGR Junagadh & ICRISAT Groundnut Pathology)."
        ],
        "organic_management": [
            "Seed biopriming with Trichoderma viride (4 g/kg seed). Foliar application of 5% NSKE at initial spot sighting on lower leaves to slow lesion multiplication."
        ],
        "chemical_management": [
            "When disease appears on lower leaves at flowering/pegging stages, spray registered fungicides: (1) Tebuconazole 25.9% m/m EC: 500-750 mL/ha in 500 L water (1.0-1.5 mL/L); Pre-Harvest Interval (PHI): 49 days. (2) Carbendazim 12% + Mancozeb 63% WP: 1,000 g formulation/ha in 500 L water (2.0 g/L); Pre-Harvest Interval (PHI): 30 days. (3) Difenoconazole 25% EC: 500 mL/ha in 500 L water (1.0 mL/L); Pre-Harvest Interval (PHI): 30 days. Consult local extension authorities and adhere strictly to label guidelines."
        ],
        "diagnostic_limitations": "Late leaf spot frequently co-occurs with groundnut rust in the field, forming a destructive disease complex. Lesions must be distinguished from early leaf spot by checking lower surface cushion texture and darker coloration.",
        "safety_warnings": "Adhere strictly to Pre-Harvest Intervals (49 days for Tebuconazole EC; 30 days for Carbendazim+Mancozeb WP). Avoid spraying during windy conditions or before rain. Wear protective mask and gloves.",
        "severity_notes": "Generally more destructive than Early Leaf Spot; severe defoliation during pod development can result in yield losses up to 50-70% and severely degrades haulm fodder quality.",
        "source": "ICAR-Directorate of Groundnut Research (ICAR-DGR), Junagadh & CIB&RC Major Uses of Pesticides (ppqs.gov.in)",
        "last_reviewed": "2026-11-18"
    },
    {
        "crop": "groundnut",
        "disease_id": "rust",
        "display_name": "Groundnut Foliar Rust",
        "scientific_name": "Puccinia arachidis",
        "disease_type": "Fungal",
        "affected_parts": ["Lower leaf surfaces primarily", "Upper leaf surfaces", "Petioles", "Stems"],
        "symptoms": [
            "Small, circular, raised blisters or pustules (uredinia) measuring 0.5-1.5 mm on the lower leaf surface",
            "Pustules rupture the epidermis to expose bright orange to cinnamon-brown powdery mass of urediniospores",
            "Corresponding upper leaf surface shows pale yellow chlorotic flecks directly above the pustules",
            "Infected leaves curl upward, turn necrotic, dry out, and appear burned while remaining attached to the plant (no premature defoliation, unlike Tikka leaf spots)"
        ],
        "visual_identification": (
            "Raised circular blisters on lower leaf surfaces discharging reddish-brown powdery spores when rubbed with a finger. "
            "Unlike Early and Late Leaf Spots which cause extensive leaf dropping, rust-infected leaves dry up, curl, and remain attached to the stem."
        ),
        "possible_causes": [
            "Airborne fungal urediniospores carried over long distances by wind currents",
            "Moderate temperatures (20-25°C), high relative humidity (>85%), and extended periods of free water on leaf surfaces"
        ],
        "favorable_conditions": "Temperatures between 20-25°C, relative humidity above 85%, frequent light showers or heavy night dews, and dense planting.",
        "prevention": [
            "Sow rust-resistant/tolerant cultivars (e.g., GPBD-4, ICGV-91114, Girnar-1, ALR-3)",
            "Avoid staggered sowings in neighboring fields to prevent continuous disease cycle",
            "Intercrop groundnut with non-host cereals (pearl millet, sorghum, maize)",
            "Eradicate self-sown groundnut plants between crop seasons"
        ],
        "cultural_management": [
            "Maintain adequate plant spacing to facilitate airflow within the canopy",
            "Avoid excess nitrogen application that produces dense, succulent foliage"
        ],
        "management": [
            "Scout crops weekly from 40 days after sowing; initiate preventive measures when the first pustules appear on lower leaves"
        ],
        "biological_management": [
            "Foliar spray of fungal hyperparasites such as Acremonium persicinum or Verticillium lecanii (1 x 10^8 spores/mL) has demonstrated biocontrol potential in research trials against Puccinia arachidis.",
            "Preventive spray of 5% Neem Seed Kernel Extract (NSKE; 50 g/L) or Neem oil (3%) inhibits urediniospore germination and provides mild protective suppression under low disease pressure. (Reference: ICAR-DGR Technical Bulletin on Groundnut Rust)."
        ],
        "organic_management": [
            "Foliar spray of 5% Neem Seed Kernel Extract (NSKE) or 3% neem oil upon observing initial pustules. Plant resistant cultivars such as GPBD-4."
        ],
        "chemical_management": [
            "Apply registered fungicides when pustules appear on lower leaves: (1) Hexaconazole 5% SC: 1,000 mL/ha in 500 L water (2.0 mL/L); Pre-Harvest Interval (PHI): 30 days. (2) Tebuconazole 25.9% m/m EC: 500-750 mL/ha in 500 L water (1.0-1.5 mL/L); Pre-Harvest Interval (PHI): 49 days. (3) Mancozeb 75% WP: 1,000-1,250 g/ha in 500 L water (2.0-2.5 g/L); Pre-Harvest Interval (PHI): 30 days. Consult local extension authorities and adhere strictly to label guidelines."
        ],
        "diagnostic_limitations": "Early rust flecks can resemble early leaf spots or mite feeding stipples before pustules erupt. Rubbing the spot with a white tissue to check for orange-brown spore residue confirms active sporulation.",
        "safety_warnings": "Observe mandatory Pre-Harvest Intervals (30 days for Hexaconazole SC and Mancozeb WP; 49 days for Tebuconazole EC). Wear protective equipment during application.",
        "severity_notes": "Can cause up to 50% pod yield reduction and severely damages fodder quality when combined with Late Leaf Spot; early vegetative rust infection causes severe economic losses.",
        "source": "ICAR-Directorate of Groundnut Research (ICAR-DGR), Junagadh & CIB&RC Major Uses of Pesticides (ppqs.gov.in)",
        "last_reviewed": "2026-11-18"
    },
    {
        "crop": "groundnut",
        "disease_id": "nutrition_deficiency",
        "display_name": "Nutrient Deficiency in Groundnut (Abiotic Chlorosis)",
        "scientific_name": "Abiotic Nutrient Deficiency (Arachis hypogaea)",
        "disease_type": "Abiotic",
        "affected_parts": ["Young emerging leaves (Iron/Zinc)", "Mature leaves (Nitrogen/Potassium)", "General canopy"],
        "symptoms": [
            "Iron Chlorosis: Vivid interveinal yellowing of young apical leaflets while main veins remain sharply green; in severe cases, entire leaflets turn pale ivory-white",
            "Zinc Deficiency: Stunted plant growth, small crinkled leaflets ('little leaf' appearance), and chlorotic mottling between veins",
            "Nitrogen Deficiency: Uniform pale green to light yellow discoloration of older basal leaves progressing upward throughout the canopy with reduced nodulation",
            "Complete absence of fungal pustules, necrotic spots with yellow halos, or pathogenic fruiting bodies"
        ],
        "visual_identification": (
            "Patterned chlorosis (interveinal yellowing or generalized leaf yellowing) without discrete necrotic spots, "
            "fungal pustules, concentric rings, or spore mats. Tissues remain supple and intact without fungal sporulation."
        ),
        "possible_causes": [
            "High soil pH / calcareous soils (>7.5 pH) immobilizing iron and zinc in insoluble carbonate forms",
            "Imbalanced fertilizer application, low soil organic matter, or poor soil drainage causing temporary root hypoxia"
        ],
        "favorable_conditions": "Calcareous black clay soils, high bicarbonate levels in irrigation water, prolonged saturated soil conditions, and low organic carbon.",
        "prevention": [
            "Perform soil testing prior to sowing to determine exact micronutrient and macronutrient status",
            "Apply well-decomposed farmyard manure (FYM; 10-12 t/ha) or vermicompost to improve soil organic carbon and nutrient chelation",
            "Apply Gypsum (400-500 kg/ha) in two splits: 50% at sowing and 50% at flowering/pegging (40-45 DAS) for calcium and sulfur supply",
            "Inoculate seed with Rhizobium and Phosphate Solubilizing Bacteria (PSB) biofertilizers"
        ],
        "cultural_management": [
            "Avoid over-irrigation and waterlogging in heavy soils which precipitates iron chlorosis",
            "Ensure proper field drainage and intercultural hoeing to aerate the root zone"
        ],
        "management": [
            "Identify specific deficiency pattern (interveinal vs general) and apply targeted foliar micronutrient correction promptly"
        ],
        "biological_management": [
            "Biofertilizer seed inoculation: Seed treatment with Bradyrhizobium groundnut culture (200-250 g/10 kg seed) and Phosphate Solubilizing Bacteria (PSB; 200 g/10 kg seed) enhances biological nitrogen fixation and phosphorus uptake.",
            "Incorporate bio-enriched compost with mycorrhizal fungi (VAM) to improve root absorption of zinc, iron, and phosphorus."
        ],
        "organic_management": [
            "Apply well-decomposed FYM (10-12 t/ha) enriched with Trichoderma and Pseudomonas. Use Rhizobium and PSB seed treatment. Incorporate green manure crops (sunnhemp or sesbania) before sowing."
        ],
        "chemical_management": [
            "This is a non-infectious physiological condition; DO NOT apply synthetic fungicides. Apply targeted nutrient sprays: (1) Iron Chlorosis: Foliar spray of Ferrous Sulphate (FeSO4, 0.5% = 5 g/L) + Citric acid (0.1% = 1 g/L) at 30 and 45 days after sowing (2-3 sprays at 7-10 day intervals). (2) Zinc Deficiency: Foliar spray of Zinc Sulphate (ZnSO4, 0.5% = 5 g/L) or soil application of Zinc Sulphate (25 kg/ha at sowing). (3) General Chlorosis: Foliar spray of 19:19:19 water-soluble NPK (1.0% = 10 g/L)."
        ],
        "diagnostic_limitations": "Interveinal chlorosis caused by iron deficiency can be confused with Groundnut Bud Necrosis Virus (GBNV) chlorotic ring mottling or early spider mite infestation. Absence of concentric ring necrosis and lack of insect webbing confirms nutritional etiology.",
        "safety_warnings": "Always neutralize ferrous sulphate spray solution with citric acid to prevent iron precipitation. Do not apply fertilizer sprays during hot midday hours to prevent foliar salt burn; spray early morning or late afternoon.",
        "severity_notes": "Severe iron chlorosis in calcareous soils can reduce pod yield by 20% to 40% and severely impairs root nodulation; timely foliar correction restores vegetative vigor within 7-10 days.",
        "source": "ICAR-Directorate of Groundnut Research (ICAR-DGR), Junagadh & TNAU Agronomy Groundnut Portal",
        "last_reviewed": "2026-11-18"
    },
    {
        "crop": "groundnut",
        "disease_id": "healthy",
        "display_name": "Healthy Groundnut Foliage",
        "scientific_name": "Arachis hypogaea (Healthy)",
        "disease_type": "None",
        "affected_parts": [],
        "symptoms": [
            "Uniform vibrant green tetrafoliate leaves with intact leaflets and smooth margins",
            "Sturdy erect or spreading stems with healthy flowering nodes and normal peg penetration",
            "Complete absence of fungal spots, rust pustules, chlorotic streaks, or deficiency yellowing"
        ],
        "visual_identification": (
            "Leaflets exhibit uniform deep green coloration, firm turgid texture, and clean upper and lower surfaces "
            "free from pustules, necrotic spots, chlorotic halos, or chewing damage."
        ),
        "possible_causes": [],
        "favorable_conditions": "Well-drained sandy loam to loamy soil (pH 6.0-7.5), optimal daytime temperatures (25-30°C), adequate soil moisture during pegging, and full sunlight.",
        "prevention": [
            "Maintain balanced soil fertility (NPK: 20-40-40 kg/ha or soil test recommendation)",
            "Apply gypsum (400-500 kg/ha) at flowering/pegging for pod filling and shell hardness",
            "Perform regular weekly scouting for foliar spots, leaf miners, and sucking pests",
            "Ensure optimal field drainage to prevent water stagnation"
        ],
        "cultural_management": [
            "Continue routine agronomic care, timely weeding up to 35-40 DAS (avoid hoeing after pegging), and critical-stage irrigations (flowering, pegging, pod development)"
        ],
        "management": [
            "Maintain optimum crop health through balanced nutrition, timely irrigations, and routine IPM monitoring"
        ],
        "biological_management": [
            "Maintain soil biological health by applying well-composted farmyard manure (FYM; 7.5-10 t/ha) during final land preparation.",
            "Conserve natural biological control agents (ladybird beetles, spiders, predatory mites) by avoiding prophylactic chemical pesticide sprays on healthy crops."
        ],
        "organic_management": [
            "Apply compost or vermicompost (2.5 t/ha). Inoculate seeds with Rhizobium and PSB biofertilizers. Avoid unwarranted chemical applications to preserve soil microbiome and beneficial insects."
        ],
        "chemical_management": [
            "None required for healthy crops. Do NOT apply prophylactic synthetic chemical fungicides or pesticides to healthy foliage."
        ],
        "diagnostic_limitations": "Visual health indicates absence of foliar disease symptoms at the time of observation. Continue weekly monitoring, especially during flowering and pod development as weather changes.",
        "safety_warnings": "Avoid unwarranted chemical applications on healthy plants to preserve beneficial soil and canopy biodiversity and prevent pesticide resistance.",
        "severity_notes": "Not applicable - plant displays normal healthy vegetative and reproductive growth characteristics.",
        "source": "ICAR-Directorate of Groundnut Research (ICAR-DGR), Junagadh & ICRISAT Groundnut Production Guidelines",
        "last_reviewed": "2026-11-18"
    }
]


def update_diseases_json():
    with open(DISEASES_JSON, "r", encoding="utf-8") as f:
        db = json.load(f)

    # Filter existing groundnut if any
    existing = [d for d in db["diseases"] if d.get("crop") != "groundnut"]
    existing.extend(GROUNDNUT_DISEASES)
    db["diseases"] = existing

    with open(DISEASES_JSON, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

    print(f"Updated {DISEASES_JSON}. Total diseases in registry: {len(db['diseases'])}")


if __name__ == "__main__":
    update_diseases_json()
