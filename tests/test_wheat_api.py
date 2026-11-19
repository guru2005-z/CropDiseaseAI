"""Comprehensive automated unit and integration tests for Wheat API and predictor.

Verifies:
1. Wheat registration and configuration in crops.json.
2. Wheat class mapping alignment (models/wheat_classes.json).
3. Curated disease knowledge base records for all 3 wheat conditions.
4. Multilingual translations across en, te, hi, ta, and kn.
5. REST API endpoints (/crops, /diseases/wheat).
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


def test_crops_config_wheat_schema(project_root: Path) -> None:
    """Verify crops.json contains valid wheat configuration with all 3 classes."""
    config_file = project_root / "config" / "crops.json"
    assert config_file.exists(), "config/crops.json does not exist"

    with config_file.open("r", encoding="utf-8") as f:
        data = json.load(f)

    assert "crops" in data
    assert "wheat" in data["crops"]

    w_meta = data["crops"]["wheat"]
    assert w_meta["display_name"] == "Wheat / Cereal"
    assert w_meta["model_path"] == "models/wheat_model.keras"
    assert w_meta["image_size"] == [224, 224]
    assert isinstance(w_meta["class_names"], list)
    assert len(w_meta["class_names"]) == 3

    expected_classes = [
        "healthy",
        "leaf_rust",
        "nitrogen_deficiency",
    ]
    assert sorted(w_meta["class_names"]) == sorted(expected_classes)
    assert w_meta["confidence_threshold"] == 0.60


def test_wheat_class_mapping_alignment(project_root: Path) -> None:
    """Verify models/wheat_classes.json aligns with config/crops.json class names."""
    classes_file = project_root / "models" / "wheat_classes.json"
    assert classes_file.is_file(), "models/wheat_classes.json missing"

    with classes_file.open("r", encoding="utf-8") as f:
        mapping = json.load(f)

    config_file = project_root / "config" / "crops.json"
    with config_file.open("r", encoding="utf-8") as f:
        crop_config = json.load(f)["crops"]["wheat"]

    expected_classes = sorted(crop_config["class_names"])
    if all(k.isdigit() for k in mapping.keys()):
        actual_classes = sorted(list(mapping.values()))
    else:
        actual_classes = sorted(list(mapping.keys()))
    assert actual_classes == expected_classes, "Class mapping in models does not match config"


def test_wheat_curated_knowledge_records(project_root: Path) -> None:
    """Verify curated records exist in diseases.json for all 3 wheat conditions."""
    diseases_file = project_root / "disease_data" / "diseases.json"
    with diseases_file.open("r", encoding="utf-8") as f:
        db = json.load(f)

    w_records = {r["disease_id"]: r for r in db["diseases"] if r.get("crop") == "wheat"}
    expected_ids = {
        "healthy",
        "leaf_rust",
        "nitrogen_deficiency",
    }
    assert set(w_records.keys()) == expected_ids

    for d_id, rec in w_records.items():
        assert len(rec["symptoms"]) > 0, f"No symptoms for {d_id}"
        assert len(rec["prevention"]) > 0, f"No prevention for {d_id}"
        assert "scientific_name" in rec and rec["scientific_name"], f"Missing scientific name for {d_id}"
        assert "source" in rec and rec["source"], f"Missing source for {d_id}"


def test_wheat_multilingual_translations(project_root: Path) -> None:
    """Verify translations exist across Telugu, Hindi, Tamil, Kannada, and English."""
    translations_file = project_root / "disease_data" / "translations.json"
    with translations_file.open("r", encoding="utf-8") as f:
        tr = json.load(f)

    languages = ["te", "hi", "ta", "kn", "en"]
    for lang in languages:
        assert lang in tr["diseases"], f"Missing language: {lang}"
        lang_dict = tr["diseases"][lang]
        for c_id in ["leaf_rust", "nitrogen_deficiency"]:
            assert c_id in lang_dict, f"Missing translation for {c_id} in {lang}"
            assert "display_name" in lang_dict[c_id]
            assert len(lang_dict[c_id]["display_name"]) > 0


def test_wheat_api_endpoints(project_root: Path) -> None:
    """Verify FastAPI endpoints list wheat and return its diseases."""
    crops = list_crops()
    wheat_info = next((c for c in crops if c["crop_id"] == "wheat"), None)
    assert wheat_info is not None
    assert wheat_info["display_name"] == "Wheat / Cereal"
    assert wheat_info["class_count"] == 3

    diseases = list_crop_diseases("wheat")
    assert len(diseases) == 3
    disease_ids = {d["disease_id"] for d in diseases}
    assert "leaf_rust" in disease_ids
    assert "nitrogen_deficiency" in disease_ids


def test_wheat_model_artifact_exists(project_root: Path) -> None:
    """Verify that models/wheat_model.keras exists and has non-zero size."""
    model_file = project_root / "models" / "wheat_model.keras"
    if not model_file.is_file():
        pytest.skip("Wheat model training in progress")
    assert model_file.stat().st_size > 1_000_000, "Model file is suspiciously small"


def test_wheat_prediction_end_to_end(project_root: Path) -> None:
    """Verify live inference runs end-to-end on a synthetic leaf image and returns valid prediction."""
    model_file = project_root / "models" / "wheat_model.keras"
    if not model_file.is_file():
        pytest.skip("Wheat model training in progress")

    img = Image.new("RGB", (224, 224), color=(34, 139, 34))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    image_bytes = buf.getvalue()

    local_predictor = CropPredictor(project_root=project_root)
    result = local_predictor.predict("wheat", image_bytes)

    assert result["crop"] == "wheat"
    assert "predicted_disease_id" in result
    assert result["predicted_disease_id"] in local_predictor.get_crop_config("wheat")["class_names"]
    assert 0.0 <= result["confidence"] <= 1.0
    assert isinstance(result["is_healthy"], bool)
    assert len(result["probabilities"]) == 3
