"""Comprehensive automated unit and integration tests for Maize API and predictor.

Verifies:
1. Maize registration and configuration in crops.json.
2. Maize model file existence and loadability via CropPredictor.
3. Class mapping alignment between models/maize_classes.json and crops.json.
4. Curated disease knowledge base records for all 4 maize conditions.
5. Multilingual translations across en, te, hi, ta, and kn.
6. Diagnostic limitations and provisional classification traceability.
7. REST API endpoints (/crops, /diseases/maize, /predict/maize).
8. Input validation, corrupted image handling, unsupported crop handling, and error codes.
9. Live end-to-end inference on synthetic and real maize leaf samples.
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


def test_crops_config_maize_schema(project_root: Path) -> None:
    """Verify crops.json contains valid maize configuration with all 4 classes."""
    config_file = project_root / "config" / "crops.json"
    assert config_file.exists(), "config/crops.json does not exist"

    with config_file.open("r", encoding="utf-8") as f:
        data = json.load(f)

    assert "crops" in data
    assert "maize" in data["crops"]

    maize = data["crops"]["maize"]
    assert maize["display_name"] == "Maize / Corn"
    assert maize["model_path"] == "models/maize_model.keras"
    assert maize["image_size"] == [224, 224]
    assert isinstance(maize["class_names"], list)
    assert len(maize["class_names"]) == 4

    expected_classes = ["common_rust", "gray_leaf_spot", "healthy", "northern_leaf_blight"]
    assert sorted(maize["class_names"]) == sorted(expected_classes)
    assert maize["confidence_threshold"] == 0.60
    assert maize["status"] == "ready"


def test_maize_model_availability(project_root: Path) -> None:
    """Verify CropPredictor reports maize model is available on disk and ready."""
    test_predictor = CropPredictor(project_root=project_root)
    supported = test_predictor.get_supported_crops()

    maize_info = next((c for c in supported if c["crop_id"] == "maize"), None)
    assert maize_info is not None
    assert maize_info["model_available"] is True
    assert maize_info["status"] == "ready"
    assert maize_info["class_count"] == 4
    assert maize_info["expected_image_size"] == [224, 224]


def test_maize_class_mapping_order(project_root: Path) -> None:
    """Verify models/maize_classes.json exactly matches the 4 classes and indices."""
    classes_file = project_root / "models" / "maize_classes.json"
    assert classes_file.exists(), "models/maize_classes.json does not exist"

    with classes_file.open("r", encoding="utf-8") as f:
        mapping = json.load(f)

    assert len(mapping) == 4
    expected_mapping = {
        "0": "common_rust",
        "1": "gray_leaf_spot",
        "2": "healthy",
        "3": "northern_leaf_blight",
    }
    assert mapping == expected_mapping


def test_maize_all_classes_curated_records(project_root: Path) -> None:
    """Verify that all 4 maize classes have complete, curated records in diseases.json."""
    test_predictor = CropPredictor(project_root=project_root)
    maize_classes = ["common_rust", "gray_leaf_spot", "healthy", "northern_leaf_blight"]

    required_fields = {
        "crop",
        "disease_id",
        "display_name",
        "scientific_name",
        "disease_type",
        "affected_parts",
        "symptoms",
        "possible_causes",
        "prevention",
        "management",
        "organic_management",
        "chemical_management",
        "severity_notes",
        "source",
        "last_reviewed",
    }

    for cls_name in maize_classes:
        info = test_predictor.get_disease_info("maize", cls_name)
        assert info is not None, f"Missing record for maize class '{cls_name}'"
        assert info["crop"] == "maize"
        assert info["disease_id"] == cls_name
        assert len(info["symptoms"]) > 0
        assert len(info["prevention"]) > 0
        assert len(info["management"]) > 0
        assert len(info["chemical_management"]) > 0

        missing = required_fields - set(info.keys())
        assert not missing, f"Maize record '{cls_name}' is missing fields: {missing}"


def test_maize_northern_leaf_blight_provisional_limitations(project_root: Path) -> None:
    """Verify provisional classification limitations note is preserved for northern_leaf_blight."""
    test_predictor = CropPredictor(project_root=project_root)
    info = test_predictor.get_disease_info("maize", "northern_leaf_blight")

    assert "diagnostic_limitations" in info
    limitations = info["diagnostic_limitations"]
    assert limitations is not None
    assert "Provisional Classification" in limitations
    assert "Blight" in limitations
    assert "PlantVillage" in limitations


def test_maize_translations_all_five_languages(project_root: Path) -> None:
    """Verify translations exist for all 4 maize diseases across en, te, hi, ta, kn."""
    translations_file = project_root / "disease_data" / "translations.json"
    assert translations_file.exists(), "disease_data/translations.json not found"

    with translations_file.open("r", encoding="utf-8") as f:
        data = json.load(f)

    assert "diseases" in data
    languages = ["en", "te", "hi", "ta", "kn"]
    maize_classes = ["common_rust", "gray_leaf_spot", "healthy", "northern_leaf_blight"]

    for lang in languages:
        assert lang in data["diseases"], f"Language '{lang}' missing in disease translations"
        lang_dict = data["diseases"][lang]
        for cls_name in maize_classes:
            assert cls_name in lang_dict, f"Disease '{cls_name}' missing in '{lang}' translations"
            record = lang_dict[cls_name]
            assert "display_name" in record and record["display_name"]
            assert "symptoms" in record and len(record["symptoms"]) > 0
            assert "prevention" in record and len(record["prevention"]) > 0
            assert "limitations" in record and record["limitations"]
            if cls_name != "healthy":
                assert "causes" in record and len(record["causes"]) > 0


def test_maize_api_crops_endpoint() -> None:
    """Verify GET /crops endpoint includes maize with expected fields."""
    crops = list_crops()
    maize = next((c for c in crops if c["crop_id"] == "maize"), None)
    assert maize is not None
    assert maize["display_name"] == "Maize / Corn"
    assert maize["model_available"] is True
    assert maize["status"] == "ready"
    assert maize["class_count"] == 4


def test_maize_api_diseases_endpoint() -> None:
    """Verify GET /diseases/maize returns curated records for all 4 maize conditions."""
    diseases = list_crop_diseases("maize")
    assert isinstance(diseases, list)
    assert len(diseases) == 4

    disease_ids = {d["disease_id"] for d in diseases}
    assert disease_ids == {"common_rust", "gray_leaf_spot", "healthy", "northern_leaf_blight"}


def test_maize_api_unsupported_crop_404() -> None:
    """Verify requesting an unregistered crop raises HTTP 404."""
    with pytest.raises(HTTPException) as exc_info:
        list_crop_diseases("sorghum")
    assert exc_info.value.status_code == 404


def test_maize_prediction_invalid_image_raises(project_root: Path) -> None:
    """Verify predictor raises ValueError on corrupted or invalid image bytes."""
    test_predictor = CropPredictor(project_root=project_root)
    with pytest.raises(ValueError):
        test_predictor.predict("maize", b"not_an_image_data")


def test_maize_missing_model_raises(project_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify ModelNotFoundError is raised if maize model file is absent."""
    test_predictor = CropPredictor(project_root=project_root)
    test_predictor._crops_config["maize"]["model_path"] = "models/non_existent_maize.keras"

    img = Image.new("RGB", (224, 224), color=(120, 200, 90))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")

    with pytest.raises(ModelNotFoundError):
        test_predictor.predict("maize", buf.getvalue())


def test_end_to_end_maize_prediction_synthetic(project_root: Path) -> None:
    """Verify live inference runs end-to-end on synthetic image and returns valid schema."""
    import os
    if "KERAS_HOME" not in os.environ:
        os.environ["KERAS_HOME"] = str(project_root / ".keras")

    test_predictor = CropPredictor(project_root=project_root)
    img = Image.new("RGB", (224, 224), color=(60, 180, 75))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    image_bytes = buf.getvalue()

    result = test_predictor.predict("maize", image_bytes)

    assert result["crop"] == "maize"
    assert result["crop_display_name"] == "Maize / Corn"
    assert result["predicted_disease_id"] in [
        "common_rust",
        "gray_leaf_spot",
        "healthy",
        "northern_leaf_blight",
    ]
    assert 0.0 <= result["confidence"] <= 1.0
    assert result["confidence_threshold"] == 0.60
    assert isinstance(result["is_healthy"], bool)
    assert len(result["probabilities"]) == 4

    prob_sum = sum(result["probabilities"].values())
    assert abs(prob_sum - 1.0) < 0.05, f"Probabilities do not sum to ~1.0: {prob_sum}"

    curated = result["curated_information"]
    assert curated["crop"] == "maize"
    assert curated["disease_id"] == result["predicted_disease_id"]


def test_end_to_end_maize_real_image_smoke_test(project_root: Path) -> None:
    """Verify live inference on real leaf image yields expected disease prediction."""
    sample_path = project_root / "datasets" / "raw" / "maize" / "Common_Rust" / "Corn_Common_Rust (1).jpg"
    if not sample_path.is_file():
        pytest.skip("Sample image not found; skipping real image smoke test.")

    test_predictor = CropPredictor(project_root=project_root)
    image_bytes = sample_path.read_bytes()

    result = test_predictor.predict("maize", image_bytes)
    assert result["crop"] == "maize"
    assert result["predicted_disease_id"] == "common_rust"
    assert result["confidence"] >= 0.60
    assert result["is_healthy"] is False
    assert result["curated_information"]["display_name"] == "Common Rust of Maize"

