"""Integration unit tests for FastAPI REST endpoints and handlers."""

import pytest
from fastapi import HTTPException
from api.main import (
    root,
    health_check,
    serve_ui,
    list_crops,
    list_crop_diseases,
    get_all_translations,
    get_language_translations,
    predictor,
)


def test_root_endpoint() -> None:
    res = root()
    assert res.status == "healthy"
    assert "operational" in res.message


def test_health_endpoint() -> None:
    res = health_check()
    assert res.status == "healthy"
    assert "running" in res.message


def test_list_crops_endpoint() -> None:
    crops = list_crops()
    assert isinstance(crops, list)
    paddy = next((c for c in crops if c["crop_id"] == "paddy"), None)
    assert paddy is not None
    assert paddy["model_available"] is True
    assert paddy["status"] == "ready"
    assert paddy["class_count"] == 10


def test_list_crop_diseases_endpoint() -> None:
    diseases = list_crop_diseases("paddy")
    assert isinstance(diseases, list)
    assert len(diseases) >= 10
    disease_ids = {d["disease_id"] for d in diseases}
    assert "blast" in disease_ids
    assert "bacterial_leaf_blight" in disease_ids
    assert "dead_heart" in disease_ids
    assert "normal" in disease_ids


def test_list_unsupported_crop_diseases() -> None:
    with pytest.raises(HTTPException) as exc_info:
        list_crop_diseases("sugarcane")
    assert exc_info.value.status_code == 404


def test_ui_endpoint() -> None:
    response = serve_ui()
    assert response.status_code == 200
    assert "CropDiseaseAI" in response.body.decode("utf-8")
    assert "Diagnose Leaf" in response.body.decode("utf-8")


def test_translations_endpoints() -> None:
    all_trans = get_all_translations()
    assert "languages" in all_trans
    assert "te" in all_trans["languages"]
    assert "hi" in all_trans["languages"]
    assert "ta" in all_trans["languages"]
    assert "kn" in all_trans["languages"]

    # Test Telugu
    te_trans = get_language_translations("te")
    assert te_trans["lang"] == "te"
    assert "మొక్క ఆరోగ్యాన్ని విశ్లేషించండి" in te_trans["ui"]["analyze_btn"]
    assert "వరి అగ్గితెగులు" in te_trans["diseases"]["blast"]["display_name"]

    # Test unsupported language
    with pytest.raises(HTTPException) as exc_info:
        get_language_translations("french")
    assert exc_info.value.status_code == 404


