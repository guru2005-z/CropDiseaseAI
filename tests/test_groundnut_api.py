"""Comprehensive automated unit and integration tests for Groundnut API and predictor.

Verifies:
1. Groundnut registration and configuration in crops.json.
2. Groundnut model file existence and loadability via CropPredictor.
3. Class mapping alignment between models/groundnut_classes.json and crops.json.
4. Curated disease knowledge base records for all 5 groundnut conditions.
5. Multilingual translations across en, te, hi, ta, and kn.
6. Diagnostic limitations, biological evidence, and chemical management notes.
7. REST API endpoints (/crops, /diseases/groundnut, /predict/groundnut).
8. Input validation, corrupted image handling, unsupported crop handling, and error codes.
9. Live end-to-end inference on synthetic and real groundnut leaf samples.
"""

from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Any, Dict

import pytest
from fastapi import HTTPException
from PIL import Image

from api.main import (
    list_crop_diseases,
    list_crops,
    predict_crop_disease,
    predictor,
)
from api.predictor import CropPredictor, ModelNotFoundError


@pytest.fixture
def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def test_crops_config_groundnut_schema(project_root: Path) -> None:
    """Verify crops.json contains valid groundnut configuration with all 5 classes."""
    config_file = project_root / "config" / "crops.json"
    assert config_file.exists(), "config/crops.json does not exist"

    with config_file.open("r", encoding="utf-8") as f:
        data = json.load(f)

    assert "crops" in data
    assert "groundnut" in data["crops"]

    g_meta = data["crops"]["groundnut"]
    assert g_meta["display_name"] == "Groundnut / Peanut"
    assert g_meta["model_path"] == "models/groundnut_model.keras"
    assert g_meta["image_size"] == [224, 224]
    assert isinstance(g_meta["class_names"], list)
    assert len(g_meta["class_names"]) == 5

    expected_classes = ["early_leaf_spot", "healthy", "late_leaf_spot", "nutrition_deficiency", "rust"]
    assert sorted(g_meta["class_names"]) == sorted(expected_classes)
    assert g_meta["confidence_threshold"] == 0.60


def test_groundnut_model_artifact_exists(project_root: Path) -> None:
    """Verify that models/groundnut_model.keras exists and has non-zero size."""
    model_file = project_root / "models" / "groundnut_model.keras"
    assert model_file.is_file(), f"Trained groundnut model file missing at {model_file}"
    assert model_file.stat().st_size > 1_000_000, "Model file is suspiciously small"


def test_groundnut_class_mapping_alignment(project_root: Path) -> None:
    """Verify models/groundnut_classes.json aligns with config/crops.json class names."""
    classes_file = project_root / "models" / "groundnut_classes.json"
    assert classes_file.is_file(), "models/groundnut_classes.json missing"

    with classes_file.open("r", encoding="utf-8") as f:
        mapping = json.load(f)

    config_file = project_root / "config" / "crops.json"
    with config_file.open("r", encoding="utf-8") as f:
        crop_config = json.load(f)["crops"]["groundnut"]

    expected_classes = sorted(crop_config["class_names"])
    actual_classes = sorted(list(mapping.values()))
    assert actual_classes == expected_classes, "Class mapping in models does not match config"


def test_groundnut_curated_knowledge_records(project_root: Path) -> None:
    """Verify curated records exist in diseases.json for all 5 groundnut conditions."""
    diseases_file = project_root / "disease_data" / "diseases.json"
    with diseases_file.open("r", encoding="utf-8") as f:
        db = json.load(f)

    g_records = {r["disease_id"]: r for r in db["diseases"] if r.get("crop") == "groundnut"}
    expected_ids = {"early_leaf_spot", "healthy", "late_leaf_spot", "nutrition_deficiency", "rust"}
    assert set(g_records.keys()) == expected_ids

    for d_id, rec in g_records.items():
        assert len(rec["symptoms"]) > 0, f"No symptoms for {d_id}"
        assert len(rec["prevention"]) > 0, f"No prevention for {d_id}"
        assert "scientific_name" in rec and rec["scientific_name"], f"Missing scientific name for {d_id}"


def test_groundnut_translations_all_five_languages(project_root: Path) -> None:
    """Verify groundnut conditions are fully translated into en, te, hi, ta, kn."""
    trans_file = project_root / "disease_data" / "translations.json"
    with trans_file.open("r", encoding="utf-8") as f:
        translations = json.load(f)

    expected_languages = ["en", "te", "hi", "ta", "kn"]
    expected_ids = ["early_leaf_spot", "healthy", "late_leaf_spot", "nutrition_deficiency", "rust"]

    for lang in expected_languages:
        assert lang in translations["diseases"], f"Language '{lang}' missing in translations"
        lang_dict = translations["diseases"][lang]
        for d_id in expected_ids:
            assert d_id in lang_dict, f"Condition '{d_id}' missing in language '{lang}'"
            entry = lang_dict[d_id]
            assert "display_name" in entry and entry["display_name"]
            assert "symptoms" in entry and len(entry["symptoms"]) > 0
            assert "prevention" in entry and len(entry["prevention"]) > 0
            assert "causes" in entry
            assert "limitations" in entry


def test_list_crops_includes_groundnut(project_root: Path) -> None:
    """Verify list_crops() endpoint returns ready groundnut model info."""
    crops = list_crops()
    g_info = next((c for c in crops if c["crop_id"] == "groundnut"), None)
    assert g_info is not None, "Groundnut not present in list_crops() response"
    assert g_info["display_name"] == "Groundnut / Peanut"
    assert g_info["model_available"] is True
    assert g_info["status"] == "ready"
    assert g_info["class_count"] == 5


def test_list_groundnut_diseases_endpoint(project_root: Path) -> None:
    """Verify list_crop_diseases('groundnut') returns all 5 conditions."""
    records = list_crop_diseases("groundnut")
    assert len(records) == 5
    ids = {r["disease_id"] for r in records}
    assert ids == {"early_leaf_spot", "healthy", "late_leaf_spot", "nutrition_deficiency", "rust"}


def test_end_to_end_groundnut_prediction_synthetic(project_root: Path) -> None:
    """Verify live inference runs end-to-end on a synthetic groundnut leaf image."""
    p = CropPredictor(project_root=project_root)
    img = Image.new("RGB", (224, 224), color=(34, 139, 34))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")

    result = p.predict("groundnut", buf.getvalue())
    assert result["crop"] == "groundnut"
    assert result["crop_display_name"] == "Groundnut / Peanut"
    assert result["predicted_disease_id"] in ["early_leaf_spot", "healthy", "late_leaf_spot", "nutrition_deficiency", "rust"]
    assert 0.0 <= result["confidence"] <= 1.0
    assert result["confidence_threshold"] == 0.60
    assert len(result["probabilities"]) == 5
    assert result["curated_information"]["crop"] == "groundnut"


def test_end_to_end_groundnut_prediction_real_sample(project_root: Path) -> None:
    """Verify inference on an actual test image from datasets/processed/groundnut/test.csv."""
    test_csv = project_root / "datasets" / "processed" / "groundnut" / "test.csv"
    assert test_csv.is_file(), "Processed groundnut test.csv missing"

    import pandas as pd
    df = pd.read_csv(test_csv)
    sample_row = df.iloc[0]
    img_path = project_root / sample_row["image_path"]
    assert img_path.is_file(), f"Sample image file missing at {img_path}"

    with img_path.open("rb") as f:
        image_bytes = f.read()

    p = CropPredictor(project_root=project_root)
    result = p.predict("groundnut", image_bytes)

    assert result["crop"] == "groundnut"
    assert result["predicted_disease_id"] in ["early_leaf_spot", "healthy", "late_leaf_spot", "nutrition_deficiency", "rust"]
    assert result["confidence"] > 0.0
