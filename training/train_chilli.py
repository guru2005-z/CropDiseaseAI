"""Production-grade two-stage transfer learning training and evaluation pipeline for Chilli Disease AI.

CropDiseaseAI: Chilli Module.
Architecture: EfficientNetB0 (ImageNet pretrained), two-stage transfer learning,
moderate agricultural augmentation, balanced class weighting, and comprehensive
single-pass evaluation on internal test split (datasets/processed/chilli/test.csv).

Preserves Paddy, Maize, and Groundnut models, datasets, and configurations 100% intact.
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
        y_px = margin_top + plot_h - int(plot_h * (i / n_y_ticks))
        draw.line([(margin_left, y_px), (margin_left + plot_w, y_px)], fill=(235, 235, 235), width=1)
        draw.text((margin_left - 65, y_px - 6), f"{y_val:.2f}", fill=(80, 80, 80))

    # X ticks
    for ep in range(0, n_epochs, max(1, n_epochs // 5)):
        x_px = margin_left + int(plot_w * (ep / max(1, n_epochs - 1)))
        draw.line([(x_px, margin_top + plot_h), (x_px, margin_top + plot_h + 5)], fill=(120, 120, 120), width=1)
        draw.text((x_px - 8, margin_top + plot_h + 8), str(ep + 1), fill=(80, 80, 80))

    # Draw transition line if two-stage
    if transition_epoch is not None and 0 < transition_epoch < n_epochs:
        trans_x = margin_left + int(plot_w * (transition_epoch / max(1, n_epochs - 1)))
        draw.line([(trans_x, margin_top), (trans_x, margin_top + plot_h)], fill=(200, 150, 0), width=2)
        draw.text((trans_x + 5, margin_top + 10), "Stage 2 Fine-Tuning", fill=(180, 120, 0))

    def to_coords(values: List[float]) -> List[Tuple[int, int]]:
        coords = []
        for idx, val in enumerate(values):
            x = margin_left + int(plot_w * (idx / max(1, n_epochs - 1)))
            y = margin_top + plot_h - int(plot_h * ((val - y_min) / (y_max - y_min)))
            coords.append((x, y))
        return coords

    # Draw train curve (blue)
    train_pts = to_coords(train_values)
    for i in range(len(train_pts) - 1):
        draw.line([train_pts[i], train_pts[i + 1]], fill=(31, 119, 180), width=2)
    for pt in train_pts:
        draw.ellipse([pt[0] - 3, pt[1] - 3, pt[0] + 3, pt[1] + 3], fill=(31, 119, 180))

    # Draw val curve (orange)
    val_pts = to_coords(val_values)
    for i in range(len(val_pts) - 1):
        draw.line([val_pts[i], val_pts[i + 1]], fill=(255, 127, 14), width=2)
    for pt in val_pts:
        draw.ellipse([pt[0] - 3, pt[1] - 3, pt[0] + 3, pt[1] + 3], fill=(255, 127, 14))

    # Title & Legend
    draw.text((margin_left, 20), title, fill=(20, 20, 20))
    draw.text((margin_left + plot_w - 220, 25), "― Training", fill=(31, 119, 180))
    draw.text((margin_left + plot_w - 120, 25), "― Validation", fill=(255, 127, 14))
    draw.text((margin_left + plot_w // 2 - 25, margin_top + plot_h + 30), "Epoch", fill=(40, 40, 40))
    draw.text((15, margin_top + plot_h // 2), ylabel, fill=(40, 40, 40))

    img.save(output_path)


def render_confusion_matrix_plot(
    cm: np.ndarray,
    class_names: List[str],
    output_path: Path,
    title: str = "Chilli Confusion Matrix",
) -> None:
    """Render a publication-ready confusion matrix heatmap image using Pillow."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    n_classes = len(class_names)
    cell_size = 75
    margin_left = 180
    margin_top = 80
    margin_right = 60
    margin_bottom = 140

    width = margin_left + n_classes * cell_size + margin_right
    height = margin_top + n_classes * cell_size + margin_bottom

    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    max_count = int(cm.max()) if cm.max() > 0 else 1

    # Title
    draw.text((margin_left, 30), title, fill=(20, 20, 20))

    # Draw cells
    for r in range(n_classes):
        for c in range(n_classes):
            val = int(cm[r, c])
            ratio = val / max_count
            intensity = int(255 - (ratio * 180))
            if r == c:
                fill_color = (intensity, 230, intensity)
            else:
                fill_color = (255, intensity, intensity)

            x0 = margin_left + c * cell_size
            y0 = margin_top + r * cell_size
            x1 = x0 + cell_size
            y1 = y0 + cell_size

            draw.rectangle([x0, y0, x1, y1], fill=fill_color, outline=(200, 200, 200), width=1)
            draw.text((x0 + cell_size // 3, y0 + cell_size // 3), str(val), fill=(0, 0, 0))

    # Y Labels (True)
    for r, name in enumerate(class_names):
        y = margin_top + r * cell_size + cell_size // 3
        draw.text((20, y), name, fill=(50, 50, 50))

    draw.text((20, margin_top - 25), "True Label →", fill=(30, 30, 30))

    # X Labels (Predicted)
    for c, name in enumerate(class_names):
        x = margin_left + c * cell_size + 10
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


def build_chilli_model(num_classes: int) -> Tuple[Any, Any]:
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

    model = models.Model(inputs=inputs, outputs=outputs, name="chilli_efficientnetb0")
    return model, base_model


class ChilliDiseaseTrainer:
    """Manages two-stage transfer learning and single-pass evaluation for Chilli."""

    def __init__(
        self,
        project_root: Optional[Path] = None,
        seed: int = 42,
    ) -> None:
        self.crop = "chilli"
        self.project_root = project_root or Path(__file__).resolve().parent.parent
        self.seed = seed
        self.models_dir = self.project_root / "models"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir = self.models_dir / "reports" / "chilli"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def train_and_evaluate(
        self,
        stage1_epochs: int = 12,
        stage2_epochs: int = 8,
        batch_size: int = 32,
    ) -> Dict[str, Any]:
        """Execute full training, fine-tuning, and internal test evaluation."""
        import tensorflow as tf
        from tensorflow.keras import callbacks, layers, optimizers

        set_reproducible_seed(self.seed)
        print("=" * 80)
        print("CropDiseaseAI: Two-Stage Transfer Learning Pipeline [CHILLI]")
        print("=" * 80)

        # 1. Load splits
        processed_dir = self.project_root / "datasets" / "processed" / "chilli"
        train_df = pd.read_csv(processed_dir / "train.csv")
        val_df = pd.read_csv(processed_dir / "validation.csv")
        test_df = pd.read_csv(processed_dir / "test.csv")

        classes_path = self.models_dir / "chilli_classes.json"
        with open(classes_path, "r", encoding="utf-8") as f:
            class_to_idx = json.load(f)

        idx_to_class = {v: k for k, v in class_to_idx.items()}
        class_names = [idx_to_class[i] for i in range(len(class_to_idx))]
        num_classes = len(class_names)

        print(f"Loaded {len(train_df)} train, {len(val_df)} val, {len(test_df)} test samples across {num_classes} classes.")
        print(f"Classes: {class_names}")

        # Compute balanced class weights
        train_labels = [class_to_idx[l] for l in train_df["label"]]
        class_weights_arr = compute_class_weight(
            class_weight="balanced",
            classes=np.unique(train_labels),
            y=train_labels,
        )
        class_weight_dict = {i: float(w) for i, w in enumerate(class_weights_arr)}
        print(f"Balanced Class Weights: {class_weight_dict}")

        # 2. Build Datasets
        train_ds = build_tf_dataset(train_df, class_to_idx, self.project_root, batch_size=batch_size, is_training=True, seed=self.seed)
        val_ds = build_tf_dataset(val_df, class_to_idx, self.project_root, batch_size=batch_size, is_training=False, seed=self.seed)
        test_ds = build_tf_dataset(test_df, class_to_idx, self.project_root, batch_size=batch_size, is_training=False, seed=self.seed)

        # 3. Build Model
        model, base_model = build_chilli_model(num_classes)
        model.compile(
            optimizer=optimizers.Adam(learning_rate=1e-3),
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"],
        )
        model.summary(print_fn=lambda x: None)

        best_weights_path = self.models_dir / "chilli_best_weights.weights.h5"
        final_model_path = self.models_dir / "chilli_model.keras"

        checkpoint_cb = callbacks.ModelCheckpoint(
            filepath=str(best_weights_path),
            monitor="val_accuracy",
            mode="max",
            save_best_only=True,
            save_weights_only=True,
            verbose=1,
        )
        early_stop_cb = callbacks.EarlyStopping(
            monitor="val_loss",
            patience=5,
            restore_best_weights=True,
            verbose=1,
        )
        reduce_lr_cb = callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=2,
            min_lr=1e-6,
            verbose=1,
        )

        # Stage 1: Feature Extraction
        print("\n--- STAGE 1: Feature Extraction (Backbone Frozen) ---")
        hist1 = model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=stage1_epochs,
            class_weight=class_weight_dict,
            callbacks=[checkpoint_cb, early_stop_cb, reduce_lr_cb],
            verbose=1,
        )

        # Stage 2: Fine-Tuning Top Layers
        print("\n--- STAGE 2: Fine-Tuning Top 25 Layers ---")
        base_model.trainable = True
        for layer in base_model.layers[:-25]:
            layer.trainable = False

        model.compile(
            optimizer=optimizers.Adam(learning_rate=1e-4),
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"],
        )

        hist2 = model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=stage1_epochs + stage2_epochs,
            initial_epoch=len(hist1.history["loss"]),
            class_weight=class_weight_dict,
            callbacks=[checkpoint_cb, early_stop_cb, reduce_lr_cb],
            verbose=1,
        )

        # Restore absolute best weights and save final model
        if best_weights_path.exists():
            print(f"Loading best weights from {best_weights_path}")
            model.load_weights(str(best_weights_path))

        model.save(str(final_model_path))
        print(f"Saved complete production model artifact to: {final_model_path}")

        # Combine histories for report
        total_train_loss = hist1.history["loss"] + hist2.history["loss"]
        total_val_loss = hist1.history["val_loss"] + hist2.history["val_loss"]
        total_train_acc = hist1.history["accuracy"] + hist2.history["accuracy"]
        total_val_acc = hist1.history["val_accuracy"] + hist2.history["val_accuracy"]
        transition_ep = len(hist1.history["loss"])

        render_curve_plot(
            total_train_loss,
            total_val_loss,
            "Chilli Disease AI: Loss Curve",
            "Loss",
            self.reports_dir / "loss_curve.png",
            transition_epoch=transition_ep,
        )
        render_curve_plot(
            total_train_acc,
            total_val_acc,
            "Chilli Disease AI: Accuracy Curve",
            "Accuracy",
            self.reports_dir / "accuracy_curve.png",
            transition_epoch=transition_ep,
        )

        # 4. Comprehensive Evaluation on Unseen Test Split
        print("\n" + "=" * 80)
        print("INDEPENDENT EVALUATION ON TEST SET (datasets/processed/chilli/test.csv)")
        print("=" * 80)

        y_true = []
        y_pred = []
        y_prob = []

        for batch_imgs, batch_lbls in test_ds:
            preds = model.predict(batch_imgs, verbose=0)
            y_prob.extend(preds)
            y_pred.extend(np.argmax(preds, axis=-1))
            y_true.extend(batch_lbls.numpy())

        y_true = np.array(y_true)
        y_pred = np.array(y_pred)
        y_prob = np.array(y_prob)

        acc = accuracy_score(y_true, y_pred)
        precision, recall, f1, support = precision_recall_fscore_support(
            y_true, y_pred, average=None, labels=range(num_classes)
        )
        macro_p, macro_r, macro_f1, _ = precision_recall_fscore_support(y_true, y_pred, average="macro")
        weight_p, weight_r, weight_f1, _ = precision_recall_fscore_support(y_true, y_pred, average="weighted")
        cm = confusion_matrix(y_true, y_pred, labels=range(num_classes))

        render_confusion_matrix_plot(cm, class_names, self.reports_dir / "confusion_matrix.png")

        print(f"\nOverall Test Accuracy: {acc * 100:.2f}%")
        print(f"Macro Precision:       {macro_p * 100:.2f}%")
        print(f"Macro Recall:          {macro_r * 100:.2f}%")
        print(f"Macro F1-Score:        {macro_f1 * 100:.2f}%")
        print(f"Weighted F1-Score:     {weight_f1 * 100:.2f}%\n")

        per_class_metrics = {}
        for idx, cname in enumerate(class_names):
            per_class_metrics[cname] = {
                "precision": round(float(precision[idx]), 4),
                "recall": round(float(recall[idx]), 4),
                "f1_score": round(float(f1[idx]), 4),
                "support": int(support[idx]),
            }
            print(f"  • {cname:22s} -> Prec: {precision[idx]*100:.2f}% | Rec: {recall[idx]*100:.2f}% | F1: {f1[idx]*100:.2f}% | Support: {support[idx]}")

        # Save JSON Metrics Report
        report_data = {
            "crop": "chilli",
            "model_architecture": "EfficientNetB0 (Two-Stage Transfer Learning)",
            "test_sample_count": len(test_df),
            "overall_accuracy": round(float(acc), 4),
            "macro_precision": round(float(macro_p), 4),
            "macro_recall": round(float(macro_r), 4),
            "macro_f1": round(float(macro_f1), 4),
            "weighted_f1": round(float(weight_f1), 4),
            "classes": class_names,
            "per_class": per_class_metrics,
            "confusion_matrix": cm.tolist(),
        }

        with open(self.reports_dir / "test_evaluation_report.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)

        print(f"\nReports & plots generated in: {self.reports_dir}")
        return report_data


def main():
    parser = argparse.ArgumentParser(description="Train and evaluate Chilli Disease AI model")
    parser.add_argument("--stage1-epochs", type=int, default=12)
    parser.add_argument("--stage2-epochs", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()

    trainer = ChilliDiseaseTrainer()
    trainer.train_and_evaluate(
        stage1_epochs=args.stage1_epochs,
        stage2_epochs=args.stage2_epochs,
        batch_size=args.batch_size,
    )


if __name__ == "__main__":
    main()
