"""Ingest curated agricultural knowledge into Pinecone vector database.

Indexes:
- All 35 curated conditions from disease_data/diseases.json across:
  - Paddy / Rice
  - Maize / Corn
  - Groundnut / Peanut
  - Chilli / Pepper
  - Banana / Plantain
  - Wheat / Cereal
- Verified Government Extension & Scheme Guidelines:
  - ANGRAU Groundnut Package of Practices
  - ICAR-IIRR Rice Integrated Pest Management
  - PM-KISAN Direct Benefit Income Support
  - PMFBY Crop Insurance & Calamity Claims
  - Krishi Vigyan Kendra Soil Nutrient & Fertilizer Handout

Uses:
- Serverless Embedding: Pinecone Hosted 'llama-text-embed-v2' (Dimension: 384)
- Cloud Index: market-forecaster
- Namespace: agricultural-rag (isolated from any other app data)
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from pinecone import Pinecone

ROOT = Path(__file__).resolve().parent.parent

# Load local .env if present
_env_file = ROOT / ".env"
if _env_file.is_file():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_file)
    except ImportError:
        pass

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "cropdisease-rag")
NAMESPACE = os.getenv("PINECONE_NAMESPACE", "agricultural-rag")
EMBED_MODEL = "llama-text-embed-v2"
EMBED_DIM = 384

GOV_DOCUMENTS = [
    {
        "id": "gov_angrau_groundnut_practices",
        "crop": "groundnut",
        "disease_id": "package_of_practices",
        "display_name": "ANGRAU Groundnut Agronomic Package of Practices",
        "scientific_name": "Arachis hypogaea Agronomy",
        "disease_type": "extension_guideline",
        "source": "ANGRAU Extension Directorate, Guntur (AP)",
        "text": (
            "CROP: Groundnut (Arachis hypogaea)\n"
            "TOPIC: ANGRAU Package of Practices, Sowing, Gypsum & Pest Management\n"
            "SOURCE: ANGRAU Extension Directorate, Guntur (AP)\n"
            "RECOMMENDATIONS: Recommended seed rate for Spanish bunch groundnut is 45-50 kg/acre. "
            "Treat seeds with Trichoderma viride @ 4 g/kg seed or Imidacloprid 600 FS @ 2 ml/kg to guard against root rot and stem borer. "
            "Apply Gypsum at 200 kg/acre at 40-45 days after sowing (pegging stage) to ensure calcium availability for shell formation, "
            "prevent pop pods, and ensure bold kernel development. Critical irrigation stages are flowering (25-30 DAS) and pod development (50-70 DAS)."
        ),
    },
    {
        "id": "gov_icar_rice_ipm",
        "crop": "paddy",
        "disease_id": "ipm_protocols",
        "display_name": "ICAR-IIRR Paddy Integrated Pest Management Protocols",
        "scientific_name": "Oryza sativa IPM",
        "disease_type": "extension_guideline",
        "source": "ICAR - Indian Institute of Rice Research (IIRR), Rajendranagar, Hyderabad",
        "text": (
            "CROP: Paddy / Rice (Oryza sativa)\n"
            "TOPIC: ICAR-IIRR Integrated Pest Management Protocols for South Indian Paddy\n"
            "SOURCE: ICAR - Indian Institute of Rice Research (IIRR), Hyderabad\n"
            "RECOMMENDATIONS: For yellow stem borer in paddy, clip seedling leaf tips before transplanting to eliminate egg masses. "
            "Install pheromone traps @ 8/acre for monitoring moth flights. If dead hearts exceed 10% economic threshold, apply Cartap Hydrochloride 4G "
            "@ 10 kg/acre or Chlorantraniliprole 18.5 SC @ 60 ml/acre in 200L water. For Brown Plant Hopper (BPH), create 30 cm alleyways "
            "every 2 metres to permit sunlight and aeration; drain field water for 2-3 days. Strictly avoid synthetic pyrethroids which cause BPH resurgence."
        ),
    },
    {
        "id": "gov_pm_kisan_scheme",
        "crop": "general",
        "disease_id": "pm_kisan_income_support",
        "display_name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN) Guidelines",
        "scientific_name": "Government of India DBT Scheme",
        "disease_type": "government_scheme",
        "source": "Ministry of Agriculture & Farmers Welfare, Government of India",
        "text": (
            "PROGRAM: Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)\n"
            "TOPIC: Income Support, Eligibility, e-KYC and Direct Benefit Transfer (DBT)\n"
            "SOURCE: Ministry of Agriculture & Farmers Welfare, Government of India\n"
            "GUIDELINES: PM-KISAN provides income support of ₹6,000 per year in three equal 4-monthly installments of ₹2,000 directly to "
            "bank accounts of eligible landholding farmer families via Direct Benefit Transfer (DBT). Mandatory requirements include: "
            "1. Aadhaar-seeded active bank account. "
            "2. Mandatory e-KYC verification through OTP via PM-KISAN portal/app or biometric authentication at Common Service Centres (CSC). "
            "3. Land registry (RoR/1B document) record verification linking with state revenue land records."
        ),
    },
    {
        "id": "gov_pmfby_crop_insurance",
        "crop": "general",
        "disease_id": "pmfby_insurance_guidelines",
        "display_name": "Pradhan Mantri Fasal Bima Yojana (PMFBY) Crop Insurance",
        "scientific_name": "National Crop Insurance Framework",
        "disease_type": "crop_insurance",
        "source": "National Crop Insurance Portal, Government of India",
        "text": (
            "PROGRAM: Pradhan Mantri Fasal Bima Yojana (PMFBY) Crop Insurance\n"
            "TOPIC: Premium Rates, Localized Calamities, Claim Timelines and Toll-Free Support\n"
            "SOURCE: National Crop Insurance Portal, Ministry of Agriculture & Farmers Welfare\n"
            "RULES: Farmers pay a uniform subsidized maximum premium rate of 2.0% of sum insured for Kharif food and oilseed crops, "
            "1.5% for Rabi food and oilseed crops, and 5% for annual commercial/horticultural crops. "
            "In event of localized natural calamities (hailstorm, cloudburst, land-slide, inundation, post-harvest unseasonal rain), "
            "individual loss intimation must be submitted strictly within 72 hours via the Crop Insurance App, toll-free helpline (14447), "
            "or nearest commercial/cooperative bank branch with geo-tagged photographic evidence."
        ),
    },
    {
        "id": "gov_kvk_soil_fertility",
        "crop": "general",
        "disease_id": "soil_fertility_management",
        "display_name": "KVK Soil Nutrient & Balanced Fertilizer Management",
        "scientific_name": "Soil Health & Nutrient Advisory",
        "disease_type": "extension_guideline",
        "source": "Krishi Vigyan Kendra (KVK) & District Agricultural Advisory Committee",
        "text": (
            "TOPIC: Soil Nutrient & Balanced Fertilizer Management\n"
            "SOURCE: Krishi Vigyan Kendra (KVK) & State Agricultural Extension\n"
            "GUIDELINES: Always apply chemical fertilizers based on Soil Health Card soil test recommendations. "
            "For red sandy loam soils, apply 1/3 of Nitrogen and 100% of Phosphorus and Potash as basal at the time of sowing. "
            "Top dress remaining Nitrogen in two equal splits at 30 and 50 days after sowing following intercultivation/weeding. "
            "For micronutrient zinc-deficient soils, apply Zinc Sulphate (ZnSO4) @ 20-25 kg/acre once in 3 crop cycles. "
            "Caution: Never mix Zinc Sulphate directly with DAP (Di-Ammonium Phosphate) in the same tank or bag, as zinc phosphate precipitates out into insoluble form."
        ),
    },
]


def main() -> None:
    print("=" * 80)
    print("AgriConnect & CropDiseaseAI: Pinecone Knowledge Base Ingestion")
    print("Embedding Model: Pinecone Serverless 'llama-text-embed-v2' (384-dim)")
    print("=" * 80)

    # 1. Load diseases.json
    diseases_file = ROOT / "disease_data" / "diseases.json"
    assert diseases_file.exists(), f"Missing {diseases_file}"
    with open(diseases_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    diseases = data.get("diseases", [])
    print(f"Loaded {len(diseases)} curated plant disease records from {diseases_file}")

    # 2. Connect to Pinecone
    print(f"Connecting to Pinecone index '{INDEX_NAME}' (Namespace: '{NAMESPACE}')...")
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(INDEX_NAME)

    docs_to_embed = []
    vector_metadata_list = []

    # Prepare disease documents
    for d in diseases:
        crop = d.get("crop", "").capitalize()
        disease_id = d.get("disease_id", "")
        display_name = d.get("display_name", "")
        scientific_name = d.get("scientific_name", "")
        disease_type = d.get("disease_type", "")
        symptoms = " ".join(d.get("symptoms", []))
        prevention = " ".join(d.get("prevention", []))
        organic = " ".join(d.get("organic_management", []))
        chemical = " ".join(d.get("chemical_management", []))
        severity = d.get("severity_notes", "")
        source = d.get("source", "")

        doc_text = (
            f"CROP: {crop}\n"
            f"CONDITION / DISEASE: {display_name} (ID: {disease_id})\n"
            f"SCIENTIFIC PATHOGEN: {scientific_name} (Type: {disease_type})\n"
            f"SYMPTOMS & SIGNS: {symptoms}\n"
            f"CULTURAL PREVENTION: {prevention}\n"
            f"ORGANIC & BIOLOGICAL MANAGEMENT: {organic}\n"
            f"REGULATED CHEMICAL CONTROL (DOSAGES & ACTIVE INGREDIENTS): {chemical}\n"
            f"ECONOMIC SEVERITY & IMPACT: {severity}\n"
            f"VERIFIED CITATION SOURCE: {source}"
        )

        vector_id = f"agri_{d.get('crop')}_{disease_id}"
        docs_to_embed.append(doc_text)
        vector_metadata_list.append({
            "id": vector_id,
            "crop": d.get("crop", "").lower(),
            "disease_id": disease_id,
            "display_name": display_name,
            "scientific_name": scientific_name,
            "disease_type": disease_type,
            "source": source,
            "text": doc_text,
        })

    # Prepare Government documents
    for g in GOV_DOCUMENTS:
        docs_to_embed.append(g["text"])
        vector_metadata_list.append({
            "id": g["id"],
            "crop": g["crop"],
            "disease_id": g["disease_id"],
            "display_name": g["display_name"],
            "scientific_name": g["scientific_name"],
            "disease_type": g["disease_type"],
            "source": g["source"],
            "text": g["text"],
        })

    print(f"Total documents to embed & upsert: {len(docs_to_embed)}")

    # 3. Generate embeddings via Pinecone hosted inference
    print("Generating 384-dim embeddings via Pinecone Serverless Inference...")
    batch_size = 20
    vectors_to_upsert = []

    for i in range(0, len(docs_to_embed), batch_size):
        chunk_texts = docs_to_embed[i : i + batch_size]
        chunk_meta = vector_metadata_list[i : i + batch_size]

        res = pc.inference.embed(
            model=EMBED_MODEL,
            inputs=chunk_texts,
            parameters={"input_type": "passage", "dimension": EMBED_DIM},
        )

        for meta, embed_obj in zip(chunk_meta, res):
            vectors_to_upsert.append({
                "id": meta["id"],
                "values": embed_obj.values,
                "metadata": meta,
            })
        print(f"  Embedded {min(i + batch_size, len(docs_to_embed))} / {len(docs_to_embed)} documents...")

    # 4. Upsert vectors to Pinecone
    print(f"\nUpserting {len(vectors_to_upsert)} vectors to namespace '{NAMESPACE}'...")
    for i in range(0, len(vectors_to_upsert), batch_size):
        batch = vectors_to_upsert[i : i + batch_size]
        index.upsert(vectors=batch, namespace=NAMESPACE)
        print(f"  Upserted batch {i + 1} to {min(i + batch_size, len(vectors_to_upsert))}")

    # 5. Verify stats
    print("\nVerifying Pinecone index stats...")
    stats = index.describe_index_stats()
    ns_stats = stats.get("namespaces", {}).get(NAMESPACE, {})
    print(f"Total vectors in namespace '{NAMESPACE}': {ns_stats.get('vectorCount', 0)}")
    print("=" * 80)
    print("INGESTION COMPLETE! Pinecone Cloud Vector Base is now live and populated.")
    print("=" * 80)


if __name__ == "__main__":
    main()
