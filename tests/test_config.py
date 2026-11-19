"""Tests for configuration, disease catalog, model readiness, and prediction service."""

import io
import json
from pathlib import Path
from PIL import Image
import pytest
from api.predictor import CropPredictor, ModelNotFoundError


@pytest.fixture
def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def test_crops_config_schema(project_root: Path) -> None:
    """Verify crops.json contains valid paddy configuration with all 10 classes."""
    config_file = project_root / "config" / "crops.json"
    assert config_file.exists(), "config/crops.json does not exist"

    with config_file.open("r", encoding="utf-8") as f:
        data = json.load(f)

    assert "crops" in data
    assert "paddy" in data["crops"]
    assert "chilli" in data["crops"]

    paddy = data["crops"]["paddy"]
    assert "model_path" in paddy
    assert "image_size" in paddy
    assert "class_names" in paddy
    assert len(paddy["image_size"]) == 2
    assert isinstance(paddy["class_names"], list)
    assert len(paddy["class_names"]) == 10
    assert "normal" in paddy["class_names"]
    assert "blast" in paddy["class_names"]


def test_diseases_data_schema(project_root: Path) -> None:
    """Verify disease_data/diseases.json matches the expected schema."""
    diseases_file = project_root / "disease_data" / "diseases.json"
    assert diseases_file.exists(), "disease_data/diseases.json does not exist"

    with diseases_file.open("r", encoding="utf-8") as f:
        data = json.load(f)

    assert "diseases" in data
    assert len(data["diseases"]) > 0

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

    for record in data["diseases"]:
        missing = required_fields - set(record.keys())
        assert not missing, f"Disease record '{record.get('disease_id')}' missing fields: {missing}"


def test_all_crop_classes_have_curated_records(project_root: Path) -> None:
    """Verify that every class configured for paddy has a matching record in diseases.json."""
    predictor = CropPredictor(project_root=project_root)
    paddy_config = predictor.get_crop_config("paddy")
    class_names = paddy_config["class_names"]

    for cls_name in class_names:
        info = predictor.get_disease_info("paddy", cls_name)
        assert info is not None
        assert info["disease_id"] == cls_name
        assert len(info["symptoms"]) > 0
        assert info["scientific_name"] is not None


def test_paddy_model_readiness(project_root: Path) -> None:
    """Verify CropPredictor detects the trained paddy model and reports ready status."""
    predictor = CropPredictor(project_root=project_root)
    supported = predictor.get_supported_crops()
    paddy_info = next((c for c in supported if c["crop_id"] == "paddy"), None)

    assert paddy_info is not None
    assert paddy_info["model_available"] is True
    assert paddy_info["status"] == "ready"
    assert paddy_info["class_count"] == 10


def test_unsupported_crop(project_root: Path) -> None:
    """Verify unsupported crops raise clean errors."""
    predictor = CropPredictor(project_root=project_root)
    assert predictor.is_crop_supported("sugarcane") is False
    with pytest.raises(KeyError):
        predictor.get_crop_config("sugarcane")


def test_untrained_crop_behavior(project_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify CropPredictor handles crops whose model binary does not exist."""
    predictor = CropPredictor(project_root=project_root)
    # Mock a crop configuration where model file does not exist
    predictor._crops_config["fake_crop"] = {
        "display_name": "Fake Crop",
        "model_path": "models/non_existent_model.keras",
        "image_size": [224, 224],
        "class_names": ["healthy", "diseased"],
        "confidence_threshold": 0.70,
        "status": "model_not_trained",
    }

    assert predictor.is_crop_supported("fake_crop") is True
    assert predictor.is_model_available("fake_crop") is False

    # Attempting to predict raises ModelNotFoundError
    img = Image.new("RGB", (224, 224), color=(100, 150, 80))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    with pytest.raises(ModelNotFoundError):
        predictor.predict("fake_crop", buf.getvalue())


def test_end_to_end_paddy_prediction(project_root: Path) -> None:
    """Verify live inference runs end-to-end on a test image and returns valid prediction."""
    import os
    if "KERAS_HOME" not in os.environ:
        os.environ["KERAS_HOME"] = str(project_root / ".keras")
    try:
        import tensorflow as tf
    except (ImportError, PermissionError, OSError) as exc:
        pytest.skip(f"TensorFlow native binaries restricted in this environment: {exc}")

    predictor = CropPredictor(project_root=project_root)
    img = Image.new("RGB", (224, 224), color=(34, 139, 34))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    image_bytes = buf.getvalue()

    try:
        result = predictor.predict("paddy", image_bytes)
    except (ImportError, PermissionError, OSError) as exc:
        pytest.skip(f"TensorFlow execution blocked by environment policies: {exc}")

    assert result["crop"] == "paddy"
    assert "predicted_disease_id" in result
    assert result["predicted_disease_id"] in predictor.get_crop_config("paddy")["class_names"]
    assert 0.0 <= result["confidence"] <= 1.0
    assert isinstance(result["is_healthy"], bool)
    assert len(result["probabilities"]) == 10
    assert result["curated_information"]["crop"] == "paddy"
    assert result["curated_information"]["disease_id"] == result["predicted_disease_id"]
