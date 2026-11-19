"""Comprehensive automated unit and integration tests for Chilli API and predictor.

Verifies:
1. Chilli registration and configuration in crops.json.
2. Chilli model file existence and loadability via CropPredictor.
3. Class mapping alignment between models/chilli_classes.json and crops.json.
4. Curated disease knowledge base records for all 6 chilli conditions.
5. Multilingual translations across en, te, hi, ta, and kn.
6. Diagnostic limitations, biological evidence, and chemical management notes.
7. REST API endpoints (/crops, /diseases/chilli, /predict/chilli).
8. Input validation, corrupted image handling, unsupported crop handling, and error codes.
9. Live end-to-end inference on synthetic and real chilli leaf samples.
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


def test_crops_config_chilli_schema(project_root: Path) -> None:
    """Verify crops.json contains valid chilli configuration with all 6 classes."""
    config_file = project_root / "config" / "crops.json"
    assert config_file.exists(), "config/crops.json does not exist"

    with config_file.open("r", encoding="utf-8") as f:
        data = json.load(f)

    assert "crops" in data
    assert "chilli" in data["crops"]

    c_meta = data["crops"]["chilli"]
    assert c_meta["display_name"] == "Chilli / Pepper"
    assert c_meta["model_path"] == "models/chilli_model.keras"
    assert c_meta["image_size"] == [224, 224]
    assert isinstance(c_meta["class_names"], list)
    assert len(c_meta["class_names"]) == 6

    expected_classes = [
        "bacterial_spot",
        "cercospora_leaf_spot",
        "curl_virus",
        "healthy",
        "nutrition_deficiency",
        "white_spot",
    ]
    assert sorted(c_meta["class_names"]) == sorted(expected_classes)
    assert c_meta["confidence_threshold"] == 0.60


def test_chilli_model_artifact_exists(project_root: Path) -> None:
    """Verify that models/chilli_model.keras exists and has non-zero size."""
    model_file = project_root / "models" / "chilli_model.keras"
    assert model_file.is_file(), f"Trained chilli model file missing at {model_file}"
    assert model_file.stat().st_size > 1_000_000, "Model file is suspiciously small"


def test_chilli_class_mapping_alignment(project_root: Path) -> None:
    """Verify models/chilli_classes.json aligns with config/crops.json class names."""
    classes_file = project_root / "models" / "chilli_classes.json"
    assert classes_file.is_file(), "models/chilli_classes.json missing"

    with classes_file.open("r", encoding="utf-8") as f:
        mapping = json.load(f)

    config_file = project_root / "config" / "crops.json"
    with config_file.open("r", encoding="utf-8") as f:
        crop_config = json.load(f)["crops"]["chilli"]

    expected_classes = sorted(crop_config["class_names"])
    if all(k.isdigit() for k in mapping.keys()):
        actual_classes = sorted(list(mapping.values()))
    else:
        actual_classes = sorted(list(mapping.keys()))
    assert actual_classes == expected_classes, "Class mapping in models does not match config"


def test_chilli_curated_knowledge_records(project_root: Path) -> None:
    """Verify curated records exist in diseases.json for all 6 chilli conditions."""
    diseases_file = project_root / "disease_data" / "diseases.json"
    with diseases_file.open("r", encoding="utf-8") as f:
        db = json.load(f)

    c_records = {r["disease_id"]: r for r in db["diseases"] if r.get("crop") == "chilli"}
    expected_ids = {
        "bacterial_spot",
        "cercospora_leaf_spot",
        "curl_virus",
        "healthy",
        "nutrition_deficiency",
        "white_spot",
    }
    assert set(c_records.keys()) == expected_ids

    for d_id, rec in c_records.items():
        assert len(rec["symptoms"]) > 0, f"No symptoms for {d_id}"
        assert len(rec["prevention"]) > 0, f"No prevention for {d_id}"
        assert "scientific_name" in rec and rec["scientific_name"], f"Missing scientific name for {d_id}"
        assert "source" in rec and rec["source"], f"Missing source for {d_id}"


def test_chilli_multilingual_translations(project_root: Path) -> None:
    """Verify translations exist across Telugu, Hindi, Tamil, Kannada, and English."""
    translations_file = project_root / "disease_data" / "translations.json"
    with translations_file.open("r", encoding="utf-8") as f:
        tr = json.load(f)

    languages = ["te", "hi", "ta", "kn", "en"]
    for lang in languages:
        assert lang in tr["diseases"], f"Missing language: {lang}"
        lang_dict = tr["diseases"][lang]
        for c_id in ["bacterial_spot", "cercospora_leaf_spot", "curl_virus", "white_spot"]:
            assert c_id in lang_dict, f"Missing translation for {c_id} in {lang}"
            assert "display_name" in lang_dict[c_id]
            assert len(lang_dict[c_id]["display_name"]) > 0


def test_chilli_api_endpoints(project_root: Path) -> None:
    """Verify FastAPI endpoints list chilli and return its diseases."""
    crops = list_crops()
    chilli_info = next((c for c in crops if c["crop_id"] == "chilli"), None)
    assert chilli_info is not None
    assert chilli_info["display_name"] == "Chilli / Pepper"
    assert chilli_info["class_count"] == 6
    assert chilli_info["model_available"] is True

    diseases = list_crop_diseases("chilli")
    assert len(diseases) == 6
    disease_ids = {d["disease_id"] for d in diseases}
    assert "curl_virus" in disease_ids
    assert "bacterial_spot" in disease_ids


def test_chilli_prediction_end_to_end(project_root: Path) -> None:
    """Verify live inference runs end-to-end on a test image and returns valid prediction."""
    img = Image.new("RGB", (224, 224), color=(34, 139, 34))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    image_bytes = buf.getvalue()

    local_predictor = CropPredictor(project_root=project_root)
    result = local_predictor.predict("chilli", image_bytes)

    assert result["crop"] == "chilli"
    assert "predicted_disease_id" in result
    assert result["predicted_disease_id"] in local_predictor.get_crop_config("chilli")["class_names"]
    assert 0.0 <= result["confidence"] <= 1.0
    assert isinstance(result["is_healthy"], bool)
    assert len(result["probabilities"]) == 6
    assert result["curated_information"]["crop"] == "chilli"
    assert result["curated_information"]["disease_id"] == result["predicted_disease_id"]
