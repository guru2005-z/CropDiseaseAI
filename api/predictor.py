"""Prediction and curated recommendation retrieval service for CropDiseaseAI.

Loads crop configurations, executes model inference (only when trained models
exist on disk), applies safety confidence checks, and joins predictions with
curated disease management records.
"""

from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from PIL import Image


class ModelNotFoundError(FileNotFoundError):
    """Raised when inference is requested for a crop whose model file does not exist."""
    pass


class CropPredictor:
    """Coordinates crop image inference and curated disease knowledge lookup."""

    def __init__(self, project_root: Optional[Path] = None) -> None:
        self.project_root = project_root or Path(__file__).resolve().parent.parent
        self.config_path = self.project_root / "config" / "crops.json"
        self.disease_data_path = self.project_root / "disease_data" / "diseases.json"

        self._crops_config: Dict[str, Any] = self._load_crops_config()
        self._diseases_catalog: Dict[Tuple[str, str], Dict[str, Any]] = self._load_diseases()
        self._loaded_models: Dict[str, Any] = {}

    def _load_crops_config(self) -> Dict[str, Any]:
        """Load crop registry and configuration."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with self.config_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("crops", {})

    def _load_diseases(self) -> Dict[Tuple[str, str], Dict[str, Any]]:
        """Load curated disease records indexed by (crop, disease_id)."""
        if not self.disease_data_path.exists():
            raise FileNotFoundError(f"Disease data file not found: {self.disease_data_path}")

        with self.disease_data_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        catalog: Dict[Tuple[str, str], Dict[str, Any]] = {}
        for record in data.get("diseases", []):
            key = (record.get("crop", "").lower(), record.get("disease_id", "").lower())
            catalog[key] = record
        return catalog

    def reload_config(self) -> None:
        """Reload configurations and disease catalogs from disk."""
        self._crops_config = self._load_crops_config()
        self._diseases_catalog = self._load_diseases()

    def get_supported_crops(self) -> List[Dict[str, Any]]:
        """Return list of registered crops and current model availability."""
        results = []
        for crop_id, meta in self._crops_config.items():
            model_path = self.project_root / meta["model_path"]
            results.append(
                {
                    "crop_id": crop_id,
                    "display_name": meta.get("display_name", crop_id),
                    "model_path": meta.get("model_path"),
                    "model_available": model_path.is_file(),
                    "expected_image_size": meta.get("image_size"),
                    "class_count": len(meta.get("class_names", [])),
                    "status": "ready" if model_path.is_file() else "model_not_trained",
                }
            )
        return results

    def is_crop_supported(self, crop_name: str) -> bool:
        """Check if crop is defined in the configuration."""
        return crop_name.lower() in self._crops_config

    def is_model_available(self, crop_name: str) -> bool:
        """Check if model binary file exists on disk."""
        crop_id = crop_name.lower()
        if not self.is_crop_supported(crop_id):
            return False
        model_rel_path = self._crops_config[crop_id]["model_path"]
        model_full_path = self.project_root / model_rel_path
        return model_full_path.is_file()

    def get_crop_config(self, crop_name: str) -> Dict[str, Any]:
        """Retrieve crop configuration or raise KeyError."""
        crop_id = crop_name.lower()
        if not self.is_crop_supported(crop_id):
            raise KeyError(
                f"Crop '{crop_name}' is not supported. Supported crops: {list(self._crops_config.keys())}"
            )
        return self._crops_config[crop_id]

    def _get_or_load_model(self, crop_name: str) -> Any:
        """Load Keras model only if it exists on disk."""
        crop_id = crop_name.lower()
        if crop_id in self._loaded_models:
            return self._loaded_models[crop_id]

        crop_config = self.get_crop_config(crop_id)
        model_file = self.project_root / crop_config["model_path"]

        if not model_file.is_file():
            raise ModelNotFoundError(
                f"Model for '{crop_name}' does not exist yet at: {model_file}. "
                f"Train the model using training/train.py before running inference."
            )

        import os
        if "KERAS_HOME" not in os.environ:
            os.environ["KERAS_HOME"] = str(self.project_root / ".keras")

        import tensorflow as tf

        model = tf.keras.models.load_model(str(model_file))
        self._loaded_models[crop_id] = model
        return model

    def preprocess_image(self, image_bytes: bytes, target_size: Tuple[int, int]) -> np.ndarray:
        """Validate, resize, and convert input image bytes to normalized array."""
        try:
            image = Image.open(io.BytesIO(image_bytes))
        except Exception as exc:
            raise ValueError("Invalid image file. Ensure a valid PNG/JPEG is uploaded.") from exc

        if image.mode != "RGB":
            image = image.convert("RGB")

        image = image.resize(target_size, Image.Resampling.BILINEAR)
        arr = np.asarray(image, dtype=np.float32)
        # Add batch dimension: (1, height, width, channels)
        batch = np.expand_dims(arr, axis=0)
        return batch

    def get_disease_info(self, crop_name: str, disease_id: str) -> Dict[str, Any]:
        """Fetch curated disease information from the disease catalog."""
        key = (crop_name.lower(), disease_id.lower())
        if key in self._diseases_catalog:
            return self._diseases_catalog[key]

        # Fallback schema if specific record is not found in catalog
        return {
            "crop": crop_name,
            "disease_id": disease_id,
            "display_name": disease_id.replace("_", " ").title(),
            "scientific_name": None,
            "disease_type": "Unknown",
            "affected_parts": [],
            "symptoms": ["Record not yet curated for this condition."],
            "possible_causes": [],
            "prevention": ["Consult local agricultural extension office."],
            "management": ["[Awaiting expert curation]"],
            "organic_management": ["[Awaiting expert curation]"],
            "chemical_management": ["[Awaiting expert curation]"],
            "severity_notes": "Curated information is currently pending agronomic review.",
            "diagnostic_limitations": None,
            "source": "CropDiseaseAI Catalog",
            "last_reviewed": "N/A",
        }

    def predict(self, crop_name: str, image_bytes: bytes) -> Dict[str, Any]:
        """Perform end-to-end inference and join with curated recommendations.

        Args:
            crop_name: Target crop identifier (e.g., 'paddy').
            image_bytes: Raw image file bytes.

        Returns:
            Dictionary containing prediction results, probabilities, safety
            warnings (if low confidence), and curated disease information.
        """
        crop_id = crop_name.lower()
        crop_config = self.get_crop_config(crop_id)

        model = self._get_or_load_model(crop_id)
        target_size: Tuple[int, int] = tuple(crop_config["image_size"])  # type: ignore[assignment]
        
        # Load class names from model classes mapping if present, otherwise fall back to config
        classes_file = self.project_root / "models" / f"{crop_id}_classes.json"
        if classes_file.is_file():
            with classes_file.open("r", encoding="utf-8") as f:
                mapping = json.load(f)
            if all(k.isdigit() for k in mapping.keys()):
                class_names: List[str] = [mapping[str(i)] for i in range(len(mapping))]
            else:
                inv = {int(v): k for k, v in mapping.items()}
                class_names = [inv[i] for i in range(len(mapping))]
        else:
            class_names = crop_config["class_names"]

        threshold: float = float(crop_config.get("confidence_threshold", 0.60))

        processed_batch = self.preprocess_image(image_bytes, target_size=target_size)
        raw_preds = model.predict(processed_batch, verbose=0)[0]
        top_idx = int(np.argmax(raw_preds))
        predicted_disease_id = class_names[top_idx]
        confidence = float(raw_preds[top_idx])

        # Probabilistic safety evaluation
        is_low_confidence = confidence < threshold
        is_healthy = predicted_disease_id.lower() in ("healthy", "normal")

        probabilities = {
            cls_name: round(float(prob), 4)
            for cls_name, prob in zip(class_names, raw_preds)
        }

        curated_info = self.get_disease_info(crop_id, predicted_disease_id)

        response: Dict[str, Any] = {
            "crop": crop_id,
            "crop_display_name": crop_config.get("display_name", crop_id),
            "is_healthy": is_healthy,
            "predicted_disease_id": predicted_disease_id,
            "confidence": round(confidence, 4),
            "confidence_threshold": threshold,
            "is_low_confidence": is_low_confidence,
            "safety_warning": (
                "Prediction confidence is below recommended threshold. "
                "Do not make agricultural interventions without secondary field confirmation."
                if is_low_confidence
                else None
            ),
            "probabilities": probabilities,
            "curated_information": curated_info,
        }
        return response
