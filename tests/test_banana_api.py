"""Comprehensive automated unit and integration tests for Banana API and predictor.

Verifies:
1. Banana registration and configuration in crops.json.
2. Banana class mapping alignment (models/banana_classes.json).
3. Curated disease knowledge base records for all 4 banana conditions.
4. Multilingual translations across en, te, hi, ta, and kn.
5. REST API endpoints (/crops, /diseases/banana).
6. Model file existence and live inference when model artifact is present.
"""

from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Any, Dict

import pytest
from PIL import Image

from api.main import (
    list_crop_diseases,
    list_crops,
)
from api.predictor import CropPredictor


@pytest.fixture
def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def test_crops_config_banana_schema(project_root: Path) -> None:
    """Verify crops.json contains valid banana configuration with all 4 classes."""
    config_file = project_root / "config" / "crops.json"
    assert config_file.exists(), "config/crops.json does not exist"

    with config_file.open("r", encoding="utf-8") as f:
        data = json.load(f)

    assert "crops" in data
    assert "banana" in data["crops"]

    b_meta = data["crops"]["banana"]
    assert b_meta["display_name"] == "Banana / Plantain"
    assert b_meta["model_path"] == "models/banana_model.keras"
    assert b_meta["image_size"] == [224, 224]
    assert isinstance(b_meta["class_names"], list)
    assert len(b_meta["class_names"]) == 4

    expected_classes = [
        "cordana_leaf_spot",
        "healthy",
        "pestalotiopsis_leaf_spot",
        "sigatoka_leaf_spot",
    ]
    assert sorted(b_meta["class_names"]) == sorted(expected_classes)
    assert b_meta["confidence_threshold"] == 0.60


def test_banana_class_mapping_alignment(project_root: Path) -> None:
    """Verify models/banana_classes.json aligns with config/crops.json class names."""
    classes_file = project_root / "models" / "banana_classes.json"
    assert classes_file.is_file(), "models/banana_classes.json missing"

    with classes_file.open("r", encoding="utf-8") as f:
        mapping = json.load(f)

    config_file = project_root / "config" / "crops.json"
    with config_file.open("r", encoding="utf-8") as f:
        crop_config = json.load(f)["crops"]["banana"]

    expected_classes = sorted(crop_config["class_names"])
    if all(k.isdigit() for k in mapping.keys()):
        actual_classes = sorted(list(mapping.values()))
    else:
        actual_classes = sorted(list(mapping.keys()))
    assert actual_classes == expected_classes, "Class mapping in models does not match config"


def test_banana_curated_knowledge_records(project_root: Path) -> None:
    """Verify curated records exist in diseases.json for all 4 banana conditions."""
    diseases_file = project_root / "disease_data" / "diseases.json"
    with diseases_file.open("r", encoding="utf-8") as f:
        db = json.load(f)

    b_records = {r["disease_id"]: r for r in db["diseases"] if r.get("crop") == "banana"}
    expected_ids = {
        "cordana_leaf_spot",
        "healthy",
        "pestalotiopsis_leaf_spot",
        "sigatoka_leaf_spot",
    }
    assert set(b_records.keys()) == expected_ids

    for d_id, rec in b_records.items():
        assert len(rec["symptoms"]) > 0, f"No symptoms for {d_id}"
        assert len(rec["prevention"]) > 0, f"No prevention for {d_id}"
        assert "scientific_name" in rec and rec["scientific_name"], f"Missing scientific name for {d_id}"
        assert "source" in rec and rec["source"], f"Missing source for {d_id}"


def test_banana_multilingual_translations(project_root: Path) -> None:
    """Verify translations exist across Telugu, Hindi, Tamil, Kannada, and English."""
    translations_file = project_root / "disease_data" / "translations.json"
    with translations_file.open("r", encoding="utf-8") as f:
        tr = json.load(f)

    languages = ["te", "hi", "ta", "kn", "en"]
    for lang in languages:
        assert lang in tr["diseases"], f"Missing language: {lang}"
        lang_dict = tr["diseases"][lang]
        for c_id in ["cordana_leaf_spot", "pestalotiopsis_leaf_spot", "sigatoka_leaf_spot"]:
            assert c_id in lang_dict, f"Missing translation for {c_id} in {lang}"
            assert "display_name" in lang_dict[c_id]
            assert len(lang_dict[c_id]["display_name"]) > 0


def test_banana_api_endpoints(project_root: Path) -> None:
    """Verify FastAPI endpoints list banana and return its diseases."""
    crops = list_crops()
    banana_info = next((c for c in crops if c["crop_id"] == "banana"), None)
    assert banana_info is not None
    assert banana_info["display_name"] == "Banana / Plantain"
    assert banana_info["class_count"] == 4

    diseases = list_crop_diseases("banana")
    assert len(diseases) == 4
    disease_ids = {d["disease_id"] for d in diseases}
    assert "sigatoka_leaf_spot" in disease_ids
    assert "cordana_leaf_spot" in disease_ids


def test_banana_model_artifact_exists(project_root: Path) -> None:
    """Verify that models/banana_model.keras exists and has non-zero size."""
    model_file = project_root / "models" / "banana_model.keras"
    assert model_file.is_file(), f"Trained banana model file missing at {model_file}"
    assert model_file.stat().st_size > 1_000_000, "Model file is suspiciously small"


def test_banana_prediction_end_to_end(project_root: Path) -> None:
    """Verify live inference runs end-to-end on a synthetic leaf image and returns valid prediction."""
    img = Image.new("RGB", (224, 224), color=(34, 139, 34))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    image_bytes = buf.getvalue()

    local_predictor = CropPredictor(project_root=project_root)
    result = local_predictor.predict("banana", image_bytes)

    assert result["crop"] == "banana"
    assert "predicted_disease_id" in result
    assert result["predicted_disease_id"] in local_predictor.get_crop_config("banana")["class_names"]
    assert 0.0 <= result["confidence"] <= 1.0
    assert isinstance(result["is_healthy"], bool)
    assert len(result["probabilities"]) == 4
