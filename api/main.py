"""FastAPI REST API application for CropDiseaseAI.

Exposes endpoints for crop disease identification and curated management
recommendations.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from api.predictor import CropPredictor, ModelNotFoundError

app = FastAPI(
    title="CropDiseaseAI API",
    description=(
        "Production-quality modular Crop Disease Prediction and Curated Recommendation System. "
        "Provides probabilistic plant leaf health analysis joined with curated agronomic records."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

predictor = CropPredictor()
_static_dir = Path(__file__).resolve().parent / "static"
_index_html_path = _static_dir / "index.html"
_translations_file = Path(__file__).resolve().parent.parent / "disease_data" / "translations.json"
_translations_cache: Dict[str, Any] = {}
if _translations_file.is_file():
    with _translations_file.open("r", encoding="utf-8") as _f:
        _translations_cache = json.load(_f)


# --- Pydantic Response Schemas ---


class RagSourceDoc(BaseModel):
    title: str
    source: str
    relevance_score: float
    excerpt: str


class RagQueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)
    crop: Optional[str] = None
    top_k: int = Field(default=3, ge=1, le=10)
    language: str = "en"


class RagQueryResponse(BaseModel):
    question: str
    answer: str
    grounded: bool
    confidence: float
    sources: List[RagSourceDoc]
    disclaimer: str
    latency_ms: Optional[int] = None
    model: Optional[str] = None


class HealthResponse(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "healthy"})
    message: str = Field(..., json_schema_extra={"example": "CropDiseaseAI service is operational"})
    version: str = Field(..., json_schema_extra={"example": "0.1.0"})


class CropInfo(BaseModel):
    crop_id: str
    display_name: str
    model_path: str
    model_available: bool
    expected_image_size: List[int]
    class_count: int
    status: str


class CuratedDiseaseInfo(BaseModel):
    crop: str
    disease_id: str
    display_name: str
    scientific_name: Optional[str] = None
    disease_type: str
    affected_parts: List[str]
    symptoms: List[str]
    possible_causes: List[str]
    prevention: List[str]
    management: List[str]
    organic_management: List[str]
    chemical_management: List[str]
    severity_notes: str
    diagnostic_limitations: Optional[str] = None
    source: str
    last_reviewed: str


class PredictionResponse(BaseModel):
    crop: str
    crop_display_name: str
    is_healthy: bool
    predicted_disease_id: str
    confidence: float
    confidence_threshold: float
    is_low_confidence: bool
    safety_warning: Optional[str] = None
    probabilities: Dict[str, float]
    curated_information: CuratedDiseaseInfo
    disclaimer: str = (
        "Predictions are probabilistic and should be cross-verified in the field. "
        "Chemical recommendations, when shown, are retrieved from curated bulletins "
        "and never hallucinated by ML models. Always consult certified extension personnel."
    )


# --- Endpoints ---


@app.get("/", response_class=HTMLResponse, tags=["UI"])
@app.get("/ui", response_class=HTMLResponse, tags=["UI"])
@app.get("/app", response_class=HTMLResponse, tags=["UI"])
def serve_ui() -> HTMLResponse:
    """Serve the interactive CropDiseaseAI web application interface."""
    if not _index_html_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="UI template not found.",
        )
    return HTMLResponse(content=_index_html_path.read_text(encoding="utf-8"))


@app.get("/health", response_model=HealthResponse, tags=["General"])
@app.get("/status", response_model=HealthResponse, tags=["General"])
def health_check() -> HealthResponse:
    """Readiness and liveness probe."""
    return HealthResponse(
        status="healthy",
        message="CropDiseaseAI service is operational.",
        version="0.1.0",
    )


@app.get("/crops", response_model=List[CropInfo], tags=["Crops"])
def list_crops() -> List[Dict[str, Any]]:
    """List all configured crops and current model readiness."""
    return predictor.get_supported_crops()


@app.get("/diseases/{crop_name}", response_model=List[CuratedDiseaseInfo], tags=["Knowledge"])
def list_crop_diseases(crop_name: str) -> List[Dict[str, Any]]:
    """Retrieve all curated disease knowledge records for a specific crop."""
    crop_id = crop_name.lower()
    if not predictor.is_crop_supported(crop_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crop '{crop_name}' is not registered in the system.",
        )

    records = [
        info
        for (c, _), info in predictor._diseases_catalog.items()
        if c == crop_id
    ]
    return records


@app.get("/translations", tags=["i18n"])
def get_all_translations() -> Dict[str, Any]:
    """Retrieve full translation catalog for all supported languages."""
    return _translations_cache


@app.get("/translations/{lang}", tags=["i18n"])
def get_language_translations(lang: str) -> Dict[str, Any]:
    """Retrieve UI and disease translations for a specific language (en, te, hi, ta, kn)."""
    lang_key = lang.lower()
    languages = _translations_cache.get("languages", {})
    if lang_key not in languages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Language '{lang}' is not supported. Supported: {list(languages.keys())}",
        )
    return {
        "lang": lang_key,
        "language_name": languages[lang_key],
        "ui": _translations_cache.get("ui", {}).get(lang_key, {}),
        "diseases": _translations_cache.get("diseases", {}).get(lang_key, {}),
    }


@app.post(
    "/predict/{crop_name}",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    tags=["Prediction"],
)
async def predict_crop_disease(
    crop_name: str,
    file: UploadFile = File(..., description="Image file of the plant/leaf (JPEG, PNG)."),
) -> Dict[str, Any]:
    """Predict plant health/disease from leaf image and return curated recommendations."""
    crop_id = crop_name.lower()

    if not predictor.is_crop_supported(crop_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crop '{crop_name}' is not supported. Check /crops for available crops.",
        )

    if not predictor.is_model_available(crop_id):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                f"Model for crop '{crop_name}' has not been trained yet. "
                f"Train the model using training/train.py before invoking predictions."
            ),
        )

    contents = await file.read()
    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    try:
        prediction_result = predictor.predict(crop_name=crop_id, image_bytes=contents)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except ModelNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))

    return prediction_result


@app.post(
    "/rag/query",
    response_model=RagQueryResponse,
    status_code=status.HTTP_200_OK,
    tags=["RAG Assistant"],
)
@app.post(
    "/chat",
    response_model=RagQueryResponse,
    status_code=status.HTTP_200_OK,
    tags=["RAG Assistant"],
)
def query_agricultural_rag(body: RagQueryRequest) -> Dict[str, Any]:
    """Query Pinecone vector database and synthesize ICAR/ANGRAU grounded guidance via Groq LLM."""
    try:
        from services.pinecone_rag_service import AgriculturalRAGBot
        bot = AgriculturalRAGBot.get_instance()
        return bot.ask(
            question=body.question,
            crop_filter=body.crop,
            top_k=body.top_k,
            user_lang=body.language,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG service error: {exc}",
        )
