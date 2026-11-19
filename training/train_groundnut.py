"""Production-grade two-stage transfer learning training and evaluation pipeline for Groundnut Disease AI.

CropDiseaseAI: Groundnut Module.
Architecture: EfficientNetB0 (ImageNet pretrained), two-stage transfer learning,
moderate agricultural augmentation, balanced class weighting, and comprehensive
single-pass evaluation on internal test split (datasets/processed/groundnut/test.csv).

Preserves Paddy and Maize models, datasets, and configurations 100% intact.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
import random
import sys
from typing import Any, Dict, List, Optional, Tuple

_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Ensure KERAS_HOME points to local workspace .keras
os.environ["KERAS_HOME"] = str(_project_root / ".keras")
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

site_packages = _project_root / "venv" / "Lib" / "site-packages"
if site_packages.exists() and str(site_packages) not in sys.path:
    sys.path.insert(0, str(site_packages))

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)
from sklearn.utils.class_weight import compute_class_weight


def set_reproducible_seed(seed: int = 42) -> None:
    """Set random seeds across Python, NumPy, and TensorFlow."""
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    import tensorflow as tf
    tf.random.set_seed(seed)


def render_curve_plot(
    train_values: List[float],
    val_values: List[float],
    title: str,
    ylabel: str,
    output_path: Path,
    transition_epoch: Optional[int] = None,
    width: int = 800,
    height: int = 500,
) -> None:
    """Render a clean training/validation curve image using Pillow."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    margin_left = 80
    margin_right = 50
    margin_top = 60
    margin_bottom = 60

    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom

    all_vals = train_values + val_values
    if not all_vals:
        img.save(output_path)
        return

    min_val = min(all_vals)
    max_val = max(all_vals)
    val_range = max(max_val - min_val, 1e-5)
    y_min = max(0.0, min_val - 0.05 * val_range)
    y_max = max_val + 0.05 * val_range

    n_epochs = max(len(train_values), 1)

    # Draw border / axes
    draw.rectangle(
        [margin_left, margin_top, margin_left + plot_w, margin_top + plot_h],
        outline=(180, 180, 180),
        width=1,
    )

    # Gridlines and Y ticks
    n_y_ticks = 5
    for i in range(n_y_ticks + 1):
        y_val = y_min + (y_max - y_min) * (i / n_y_ticks)
        py = margin_top + plot_h - int(plot_h * (i / n_y_ticks))
        draw.line([margin_left, py, margin_left + plot_w, py], fill=(235, 235, 235), width=1)
        draw.text((margin_left - 65, py - 6), f"{y_val:.3f}", fill=(80, 80, 80))

    # Gridlines and X ticks
    step_x = max(1, n_epochs // 10)
    for ep in range(1, n_epochs + 1, step_x):
        px = margin_left + int(plot_w * ((ep - 1) / max(n_epochs - 1, 1)))
        draw.line([px, margin_top, px, margin_top + plot_h], fill=(235, 235, 235), width=1)
        draw.text((px - 6, margin_top + plot_h + 8), str(ep), fill=(80, 80, 80))

    def to_coords(values: List[float]) -> List[Tuple[int, int]]:
        coords = []
        for idx, v in enumerate(values):
            x = margin_left + int(plot_w * (idx / max(n_epochs - 1, 1)))
            norm_y = (v - y_min) / (y_max - y_min)
            y = margin_top + plot_h - int(plot_h * norm_y)
            coords.append((x, y))
        return coords

    # Train curve (Blue)
    train_coords = to_coords(train_values)
    for i in range(len(train_coords) - 1):
        draw.line([train_coords[i], train_coords[i + 1]], fill=(31, 119, 180), width=2)
    for pt in train_coords:
        draw.ellipse([pt[0] - 2, pt[1] - 2, pt[0] + 2, pt[1] + 2], fill=(31, 119, 180))

    # Val curve (Orange)
    val_coords = to_coords(val_values)
    for i in range(len(val_coords) - 1):
        draw.line([val_coords[i], val_coords[i + 1]], fill=(255, 127, 14), width=2)
    for pt in val_coords:
        draw.ellipse([pt[0] - 2, pt[1] - 2, pt[0] + 2, pt[1] + 2], fill=(255, 127, 14))

    # Stage transition marker
    if transition_epoch and 1 <= transition_epoch <= n_epochs:
        trans_x = margin_left + int(plot_w * ((transition_epoch - 1) / max(n_epochs - 1, 1)))
        draw.line([trans_x, margin_top, trans_x, margin_top + plot_h], fill=(214, 39, 40), width=1)
        draw.text((trans_x + 5, margin_top + 10), "Fine-Tuning", fill=(214, 39, 40))

    # Title & Legend
    draw.text((margin_left, 20), title, fill=(20, 20, 20))
    draw.line([width - 240, 25, width - 210, 25], fill=(31, 119, 180), width=2)
    draw.text((width - 200, 20), "Train", fill=(50, 50, 50))
    draw.line([width - 130, 25, width - 100, 25], fill=(255, 127, 14), width=2)
    draw.text((width - 90, 20), "Validation", fill=(50, 50, 50))

    img.save(output_path)


def render_confusion_matrix_plot(
    cm: np.ndarray,
    class_names: List[str],
    output_path: Path,
    title: str = "Groundnut Confusion Matrix (Test Set)",
) -> None:
    """Render confusion matrix visualization using Pillow."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    n_classes = len(class_names)
    cell_size = 85
    margin_left = 180
    margin_top = 80
    margin_right = 60
    margin_bottom = 100

    width = margin_left + n_classes * cell_size + margin_right
    height = margin_top + n_classes * cell_size + margin_bottom

    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    draw.text((margin_left, 30), title, fill=(20, 20, 20))
    max_val = max(int(cm.max()), 1)

    for i in range(n_classes):
        for j in range(n_classes):
            val = int(cm[i, j])
            x0 = margin_left + j * cell_size
            y0 = margin_top + i * cell_size
            x1 = x0 + cell_size
            y1 = y0 + cell_size

            ratio = val / max_val
            r = int(255 - ratio * (255 - 33))
            g = int(255 - ratio * (255 - 102))
            b = int(255 - ratio * (255 - 172))

            draw.rectangle([x0, y0, x1, y1], fill=(r, g, b), outline=(200, 200, 200), width=1)
            text_color = (255, 255, 255) if ratio > 0.55 else (30, 30, 30)
            txt = str(val)
            draw.text((x0 + cell_size // 2 - 10, y0 + cell_size // 2 - 8), txt, fill=text_color)

    for i, name in enumerate(class_names):
        y = margin_top + i * cell_size + cell_size // 2 - 6
        draw.text((20, y), name, fill=(50, 50, 50))

    for j, name in enumerate(class_names):
        x = margin_left + j * cell_size + 5
        draw.text((x, margin_top + n_classes * cell_size + 15), name, fill=(50, 50, 50))

    draw.text((margin_left, margin_top + n_classes * cell_size + 55), "Predicted Label", fill=(30, 30, 30))
    img.save(output_path)


def build_tf_dataset(
    df: pd.DataFrame,
    class_to_idx: Dict[str, int],
    project_root: Path,
    batch_size: int = 32,
    is_training: bool = False,
    seed: int = 42,
) -> Any:
    """Build high-performance tf.data.Dataset pipeline."""
    import tensorflow as tf

    paths = [str(project_root / p) for p in df["image_path"]]
    labels = [class_to_idx[l] for l in df["label"]]

    def _load_and_preprocess(img_path, label_idx):
        img_raw = tf.io.read_file(img_path)
        img = tf.image.decode_jpeg(img_raw, channels=3)
        img = tf.image.resize(img, [224, 224])
        return img, label_idx

    ds = tf.data.Dataset.from_tensor_slices((paths, labels))
    if is_training:
        ds = ds.shuffle(buffer_size=1024, seed=seed, reshuffle_each_iteration=True)
    ds = ds.map(_load_and_preprocess, num_parallel_calls=tf.data.AUTOTUNE)
    ds = ds.batch(batch_size)
    ds = ds.prefetch(tf.data.AUTOTUNE)
    return ds


def build_groundnut_model(num_classes: int) -> Tuple[Any, Any]:
    """Build EfficientNetB0 transfer learning architecture with moderate augmentation."""
    import tensorflow as tf
    from tensorflow.keras import layers, models
    from tensorflow.keras.applications import EfficientNetB0

    inputs = layers.Input(shape=(224, 224, 3), name="input_image")

    # Moderate agricultural augmentation
    x = layers.RandomFlip("horizontal", name="aug_random_flip")(inputs)
    x = layers.RandomRotation(0.08, fill_mode="reflect", name="aug_random_rotation")(x)
    x = layers.RandomZoom(0.08, fill_mode="reflect", name="aug_random_zoom")(x)
    x = layers.RandomContrast(0.10, name="aug_random_contrast")(x)

    base_model = EfficientNetB0(
        weights="imagenet",
        include_top=False,
        input_tensor=x,
    )
    base_model.trainable = False

    x = layers.GlobalAveragePooling2D(name="global_avg_pool")(base_model.output)
    x = layers.Dropout(0.3, name="top_dropout")(x)
    outputs = layers.Dense(num_classes, activation="softmax", name="classification_head")(x)

    model = models.Model(inputs=inputs, outputs=outputs, name="groundnut_efficientnetb0")
    return model, base_model


class GroundnutDiseaseTrainer:
    """Manages two-stage transfer learning and single-pass evaluation for Groundnut."""

    def __init__(
        self,
        project_root: Optional[Path] = None,
        seed: int = 42,
    ) -> None:
        self.crop = "groundnut"
        self.project_root = project_root or Path(__file__).resolve().parent.parent
        self.seed = seed
        self.models_dir = self.project_root / "models"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir = self.models_dir / "reports" / "groundnut"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def train_and_evaluate(
        self,
        stage1_epochs: int = 15,
        stage2_epochs: int = 10,
        batch_size: int = 32,
    ) -> Dict[str, Any]:
        """Execute full training, fine-tuning, and internal test evaluation."""
        import tensorflow as tf
        from tensorflow.keras import callbacks, layers, optimizers

        set_reproducible_seed(self.seed)
        print("=" * 80)
        print("CropDiseaseAI: Two-Stage Transfer Learning Pipeline [GROUNDNUT]")
        print("=" * 80)

        # 1. Load splits
        processed_dir = self.project_root / "datasets" / "processed" / "groundnut"
        train_df = pd.read_csv(processed_dir / "train.csv")
        val_df = pd.read_csv(processed_dir / "validation.csv")
        test_df = pd.read_csv(processed_dir / "test.csv")

        class_names = sorted(train_df["label"].unique().tolist())
        num_classes = len(class_names)
        class_to_idx = {name: i for i, name in enumerate(class_names)}
        idx_to_class = {str(i): name for i, name in enumerate(class_names)}

        print(f"Number of training samples:      {len(train_df)}")
        print(f"Number of validation samples:    {len(val_df)}")
        print(f"Number of internal test samples: {len(test_df)}")
        print(f"Number of classes: {num_classes}")
        print(f"Class names: {class_names}")

        print("\nClass distribution (training split):")
        train_counts = train_df["label"].value_counts()
        for c in class_names:
            print(f"  {c:<25}: {train_counts.get(c, 0)} ({train_counts.get(c, 0)/len(train_df)*100:.2f}%)")

        # Save class mapping
        classes_file = self.models_dir / "groundnut_classes.json"
        with classes_file.open("w", encoding="utf-8") as f:
            json.dump(idx_to_class, f, indent=2)
        print(f"\nClass mapping saved to: {classes_file.relative_to(self.project_root)}")

        # 2. Balanced Class Weights
        y_train_idx = [class_to_idx[l] for l in train_df["label"]]
        class_weights_arr = compute_class_weight(
            class_weight="balanced",
            classes=np.unique(y_train_idx),
            y=y_train_idx,
        )
        class_weight_dict = {int(i): float(round(w, 4)) for i, w in enumerate(class_weights_arr)}
        print("\nCalculated balanced class weights:")
        for idx, cls_name in enumerate(class_names):
            print(f"  [{idx}] {cls_name:<25}: {class_weight_dict[idx]}")

        # 3. tf.data Pipelines
        print("\nBuilding tf.data pipelines...")
        train_ds = build_tf_dataset(
            train_df, class_to_idx, self.project_root, batch_size=batch_size, is_training=True, seed=self.seed
        )
        val_ds = build_tf_dataset(
            val_df, class_to_idx, self.project_root, batch_size=batch_size, is_training=False
        )

        # 4. Build Model
        print("\nBuilding EfficientNetB0 transfer learning architecture...")
        model, base_model = build_groundnut_model(num_classes=num_classes)
        model_checkpoint_path = self.models_dir / "groundnut_model.keras"

        # ==========================================
        # STAGE 1: Feature Extraction
        # ==========================================
        print("\n" + "=" * 50)
        print("STAGE 1: Feature Extraction (Backbone Frozen)")
        print(f"Initial Learning Rate: 1e-3 | Max Epochs: {stage1_epochs}")
        print("=" * 50)

        model.compile(
            optimizer=optimizers.Adam(learning_rate=1e-3),
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"],
        )

        stage1_callbacks = [
            callbacks.EarlyStopping(
                monitor="val_loss",
                patience=5,
                restore_best_weights=True,
                verbose=1,
            ),
            callbacks.ModelCheckpoint(
                filepath=str(model_checkpoint_path),
                monitor="val_loss",
                save_best_only=True,
                verbose=1,
            ),
            callbacks.ReduceLROnPlateau(
                monitor="val_loss",
                factor=0.5,
                patience=2,
                min_lr=1e-6,
                verbose=1,
            ),
        ]

        h1 = model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=stage1_epochs,
            class_weight=class_weight_dict,
            callbacks=stage1_callbacks,
            verbose=1,
        )

        s1_completed_epochs = len(h1.history["loss"])
        print(f"\nStage 1 completed in {s1_completed_epochs} epochs.")
        print(f"Best Stage 1 Val Loss: {min(h1.history['val_loss']):.4f} | Val Acc: {max(h1.history['val_accuracy']):.4f}")

        # ==========================================
        # STAGE 2: Fine-Tuning
        # ==========================================
        print("\n" + "=" * 50)
        print("STAGE 2: Fine-Tuning (Top 30 Layers Unfrozen)")
        print(f"Reduced Learning Rate: 1e-4 | Max Epochs: {stage2_epochs}")
        print("=" * 50)

        base_model.trainable = True
        # Freeze all layers except top 30
        for layer in base_model.layers[:-30]:
            layer.trainable = False

        model.compile(
            optimizer=optimizers.Adam(learning_rate=1e-4),
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"],
        )

        stage2_callbacks = [
            callbacks.EarlyStopping(
                monitor="val_loss",
                patience=4,
                restore_best_weights=True,
                verbose=1,
            ),
            callbacks.ModelCheckpoint(
                filepath=str(model_checkpoint_path),
                monitor="val_loss",
                save_best_only=True,
                verbose=1,
            ),
            callbacks.ReduceLROnPlateau(
                monitor="val_loss",
                factor=0.5,
                patience=2,
                min_lr=1e-7,
                verbose=1,
            ),
        ]

        total_target_epochs = s1_completed_epochs + stage2_epochs
        h2 = model.fit(
            train_ds,
            validation_data=val_ds,
            initial_epoch=s1_completed_epochs,
            epochs=total_target_epochs,
            class_weight=class_weight_dict,
            callbacks=stage2_callbacks,
            verbose=1,
        )

        # Merge history
        merged_history = {
            "loss": h1.history["loss"] + h2.history["loss"],
            "accuracy": h1.history["accuracy"] + h2.history["accuracy"],
            "val_loss": h1.history["val_loss"] + h2.history["val_loss"],
            "val_accuracy": h1.history["val_accuracy"] + h2.history["val_accuracy"],
            "lr": [float(x) for x in (h1.history.get("learning_rate", h1.history.get("lr", [])) +
                                      h2.history.get("learning_rate", h2.history.get("lr", [])))],
            "transition_epoch": s1_completed_epochs,
        }

        # Save training history
        history_path = self.models_dir / "groundnut_training_history.json"
        with history_path.open("w", encoding="utf-8") as f:
            json.dump(merged_history, f, indent=2)

        # Render curves
        render_curve_plot(
            train_values=merged_history["loss"],
            val_values=merged_history["val_loss"],
            title="Groundnut Loss Progression",
            ylabel="Sparse Categorical Crossentropy",
            output_path=self.reports_dir / "loss_curve.png",
            transition_epoch=s1_completed_epochs,
        )
        render_curve_plot(
            train_values=merged_history["accuracy"],
            val_values=merged_history["val_accuracy"],
            title="Groundnut Accuracy Progression",
            ylabel="Accuracy",
            output_path=self.reports_dir / "accuracy_curve.png",
            transition_epoch=s1_completed_epochs,
        )

        # ==========================================
        # STAGE 3: Final Single-Pass Test Evaluation
        # ==========================================
        print("\n" + "=" * 50)
        print("STAGE 3: Single-Pass Evaluation on Internal Test Split")
        print("=" * 50)

        # Reload best checkpoint
        best_model = tf.keras.models.load_model(str(model_checkpoint_path))
        test_ds = build_tf_dataset(
            test_df, class_to_idx, self.project_root, batch_size=batch_size, is_training=False
        )

        y_probs = best_model.predict(test_ds, verbose=1)
        y_pred = np.argmax(y_probs, axis=1)
        y_true = np.array([class_to_idx[l] for l in test_df["label"]])

        acc = float(accuracy_score(y_true, y_pred))
        precision_m, recall_m, f1_m, _ = precision_recall_fscore_support(y_true, y_pred, average="macro")
        precision_w, recall_w, f1_w, _ = precision_recall_fscore_support(y_true, y_pred, average="weighted")
        per_class_p, per_class_r, per_class_f1, per_class_supp = precision_recall_fscore_support(
            y_true, y_pred, average=None, labels=range(num_classes)
        )

        cm = confusion_matrix(y_true, y_pred, labels=range(num_classes))
        clf_report = classification_report(y_true, y_pred, target_names=class_names, digits=4)

        print("\n--- INTERNAL TEST METRICS ---")
        print(f"Accuracy:    {acc * 100:.2f}%")
        print(f"Macro F1:    {f1_m * 100:.2f}%")
        print(f"Weighted F1: {f1_w * 100:.2f}%")
        print("\nClassification Report:\n", clf_report)

        # Save classification report
        with (self.reports_dir / "classification_report.txt").open("w", encoding="utf-8") as f:
            f.write(clf_report)

        # Render confusion matrix
        render_confusion_matrix_plot(
            cm=cm,
            class_names=class_names,
            output_path=self.reports_dir / "confusion_matrix.png",
            title="Groundnut Test Confusion Matrix",
        )

        # Misclassified images audit
        misclassified = []
        for idx, (t, p) in enumerate(zip(y_true, y_pred)):
            if t != p:
                misclassified.append({
                    "image_id": test_df.iloc[idx]["image_id"],
                    "image_path": test_df.iloc[idx]["image_path"],
                    "true_label": class_names[t],
                    "predicted_label": class_names[p],
                    "true_probability": float(round(y_probs[idx][t], 4)),
                    "predicted_probability": float(round(y_probs[idx][p], 4)),
                })

        misclassified_df = pd.DataFrame(misclassified)
        misclassified_df.to_csv(self.reports_dir / "misclassified.csv", index=False)
        print(f"Misclassified samples: {len(misclassified)} / {len(test_df)}")

        # Comprehensive metrics JSON
        metrics = {
            "crop": "groundnut",
            "model_architecture": "EfficientNetB0 (Two-Stage Transfer Learning)",
            "test_sample_count": len(test_df),
            "accuracy": float(round(acc, 4)),
            "macro_precision": float(round(precision_m, 4)),
            "macro_recall": float(round(recall_m, 4)),
            "macro_f1": float(round(f1_m, 4)),
            "weighted_f1": float(round(f1_w, 4)),
            "per_class": {
                name: {
                    "precision": float(round(per_class_p[i], 4)),
                    "recall": float(round(per_class_r[i], 4)),
                    "f1_score": float(round(per_class_f1[i], 4)),
                    "support": int(per_class_supp[i]),
                }
                for i, name in enumerate(class_names)
            },
            "confusion_matrix": cm.tolist(),
            "class_names": class_names,
            "misclassified_count": len(misclassified),
        }

        with (self.reports_dir / "metrics.json").open("w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)

        print("\nAll model artifacts and reports successfully saved to:")
        print(f"  Model:   {model_checkpoint_path.relative_to(self.project_root)}")
        print(f"  Reports: {self.reports_dir.relative_to(self.project_root)}")

        return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Groundnut Model for CropDiseaseAI")
    parser.add_argument("--stage1-epochs", type=int, default=12, help="Stage 1 feature extraction epochs")
    parser.add_argument("--stage2-epochs", type=int, default=8, help="Stage 2 fine-tuning epochs")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    trainer = GroundnutDiseaseTrainer(seed=args.seed)
    trainer.train_and_evaluate(
        stage1_epochs=args.stage1_epochs,
        stage2_epochs=args.stage2_epochs,
        batch_size=args.batch_size,
    )
