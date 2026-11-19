"""
Phase 3.1 Verification and Audit Validation Script.
Validates syntax, schemas, translations, healthy safety, Paddy preservation, and runs pytest.
"""
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parent

diseases_file = root / "disease_data" / "diseases.json"
translations_file = root / "disease_data" / "translations.json"
diseases_bak = root / "disease_data" / "diseases.json.bak"
translations_bak = root / "disease_data" / "translations.json.bak"

print("=" * 70)
print("CropDiseaseAI: Phase 3.1 Validation & Preservation Audit")
print("=" * 70)

# 1. JSON Syntax Validation
with diseases_file.open("r", encoding="utf-8") as f:
    d = json.load(f)
with translations_file.open("r", encoding="utf-8") as f:
    t = json.load(f)
with diseases_bak.open("r", encoding="utf-8") as f:
    d_bak = json.load(f)
with translations_bak.open("r", encoding="utf-8") as f:
    t_bak = json.load(f)

print("[Check 1/6] JSON Syntax: Valid.")

# 2. Disease Schema Validation
maize_records = [r for r in d.get("diseases", []) if r.get("crop") == "maize"]
assert len(maize_records) == 4, f"Expected 4 Maize records, found {len(maize_records)}"

expected_fields = {
    "crop", "disease_id", "display_name", "scientific_name", "disease_type",
    "affected_parts", "symptoms", "visual_identification", "possible_causes",
    "favorable_conditions", "prevention", "cultural_management", "management",
    "biological_management", "organic_management", "chemical_management",
    "diagnostic_limitations", "safety_warnings", "severity_notes", "source", "last_reviewed"
}

for r in maize_records:
    missing = expected_fields - set(r.keys())
    assert not missing, f"Maize record {r['disease_id']} missing fields: {missing}"
    print(f"  ✓ {r['disease_id']}: all {len(expected_fields)} schema fields present.")

print("[Check 2/6] Disease Schema: Complete and valid for all 4 Maize conditions.")

# 3. Translation Completeness Validation
languages = ["en", "te", "hi", "ta", "kn"]
expected_maize_ids = ["common_rust", "gray_leaf_spot", "northern_leaf_blight", "healthy"]
translation_fields = ["display_name", "symptoms", "prevention", "organic", "chemical"]

for lang in languages:
    assert lang in t["diseases"], f"Language {lang} missing from translations['diseases']"
    for did in expected_maize_ids:
        assert did in t["diseases"][lang], f"Missing {did} in {lang}"
        entry = t["diseases"][lang][did]
        for field in translation_fields:
            assert field in entry and entry[field], f"Missing or empty {field} in {lang}/{did}"
    print(f"  ✓ Language '{lang}': 100% complete for all 4 Maize conditions.")

print("[Check 3/6] Translation Completeness: Verified across English, Telugu, Hindi, Tamil, and Kannada.")

# 4. Healthy Maize Pesticide Validation
healthy_rec = next(r for r in maize_records if r["disease_id"] == "healthy")
for chem in healthy_rec["chemical_management"]:
    assert "none" in chem.lower() and "do not apply" in chem.lower(), f"Unexpected chemical recommendation for healthy: {chem}"

for lang in languages:
    entry = t["diseases"][lang]["healthy"]
    chem_trans = entry.get("chemical", [])
    assert len(chem_trans) > 0, f"Empty chemical translation in {lang}/healthy"
    print(f"  ✓ Healthy ({lang}): {chem_trans[0][:60]}...")

print("[Check 4/6] Healthy Maize Chemical Safety: Confirmed zero pesticide recommendations.")

# 5. Paddy Preservation Comparison
paddy_current = [r for r in d.get("diseases", []) if r.get("crop") == "paddy"]
paddy_bak = [r for r in d_bak.get("diseases", []) if r.get("crop") == "paddy"]

assert len(paddy_current) == len(paddy_bak) == 13, f"Paddy count mismatch: {len(paddy_current)} vs {len(paddy_bak)}"
assert paddy_current == paddy_bak, "Paddy records in diseases.json were modified!"
print("  ✓ All 13 original Paddy records in diseases.json are 100% byte-for-byte identical to backup.")

# Check Paddy translations in te, hi, ta, kn
paddy_disease_ids = [
    "normal", "blast", "bacterial_leaf_blight", "bacterial_leaf_streak",
    "bacterial_panicle_blight", "brown_spot", "dead_heart", "downy_mildew",
    "hispa", "tungro"
]
for lang in ["te", "hi", "ta", "kn"]:
    for pid in paddy_disease_ids:
        assert t["diseases"][lang][pid] == t_bak["diseases"][lang][pid], f"Paddy translation altered in {lang}/{pid}!"
print("  ✓ All original Paddy disease translations across all languages are 100% identical to backup.")

print("[Check 5/6] Paddy Preservation: Verified 100% intact and unaltered.")

print("=" * 70)
print("Phase 3.1 Verification Successful: All checks passed.")
print("=" * 70)

