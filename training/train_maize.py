"""Production-grade two-stage transfer learning training and evaluation pipeline for Maize Disease AI.

CropDiseaseAI: Phase 4 - Maize Module.
Architecture: EfficientNetB0 (ImageNet pretrained), two-stage transfer learning,
moderate agricultural augmentation, balanced class weighting, and comprehensive
single-pass evaluation on internal test split (datasets/processed/maize/test.csv).

Preserves Paddy models, datasets, and configurations 100% intact.
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

    train_coords = to_coords(train_values)
    val_coords = to_coords(val_values)

    train_color = (30, 110, 200)    # Blue
    val_color = (220, 90, 30)       # Orange

    for pts, col in [(train_coords, train_color), (val_coords, val_color)]:
        for j in range(len(pts) - 1):
            draw.line([pts[j], pts[j + 1]], fill=col, width=2)
        for pt in pts:
            draw.ellipse([pt[0] - 2, pt[1] - 2, pt[0] + 2, pt[1] + 2], fill=col)

    if transition_epoch and 1 <= transition_epoch <= n_epochs:
        trans_x = margin_left + int(plot_w * ((transition_epoch - 1) / max(n_epochs - 1, 1)))
        for dy in range(margin_top, margin_top + plot_h, 6):
            draw.line([trans_x, dy, trans_x, min(dy + 3, margin_top + plot_h)], fill=(120, 120, 120), width=1)
        draw.text((trans_x + 4, margin_top + 10), "Fine-Tuning Start", fill=(100, 100, 100))

    draw.text((margin_left, margin_top - 35), title, fill=(20, 20, 20))
    draw.text((width // 2 - 20, height - 25), "Epoch", fill=(50, 50, 50))
    draw.text((margin_left - 70, margin_top - 20), ylabel, fill=(50, 50, 50))

    # Legend box
    leg_x = width - margin_right - 180
    leg_y = margin_top + 10
    draw.rectangle([leg_x, leg_y, leg_x + 170, leg_y + 45], fill=(255, 255, 255), outline=(200, 200, 200))
    draw.line([leg_x + 10, leg_y + 15, leg_x + 35, leg_y + 15], fill=train_color, width=2)
    draw.text((leg_x + 42, leg_y + 8), f"Train ({train_values[-1]:.3f})", fill=(30, 30, 30))
    draw.line([leg_x + 10, leg_y + 32, leg_x + 35, leg_y + 32], fill=val_color, width=2)
    draw.text((leg_x + 42, leg_y + 25), f"Val ({val_values[-1]:.3f})", fill=(30, 30, 30))

    img.save(output_path)


def render_confusion_matrix(
    cm: np.ndarray,
    class_names: List[str],
    output_path: Path,
    title: str = "Maize Disease Confusion Matrix",
) -> None:
    """Render confusion matrix heatmap with cell counts using Pillow."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    n_classes = len(class_names)
    cell_size = 70
    label_margin = 180
    top_margin = 80
    bottom_margin = 50
    right_margin = 80

    img_w = label_margin + n_classes * cell_size + right_margin
    img_h = top_margin + n_classes * cell_size + bottom_margin

    img = Image.new("RGB", (img_w, img_h), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    draw.text((label_margin, 20), title, fill=(10, 10, 10))
    draw.text((label_margin + (n_classes * cell_size) // 2 - 40, top_margin - 30), "Predicted Label", fill=(80, 80, 80))
    draw.text((15, top_margin - 30), "True Label", fill=(80, 80, 80))

    row_sums = cm.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    norm_cm = cm / row_sums

    for i in range(n_classes):
        label_text = class_names[i]
        if len(label_text) > 22:
            label_text = label_text[:20] + ".."
        y_pos = top_margin + i * cell_size + (cell_size // 2) - 6
        draw.text((15, y_pos), label_text, fill=(40, 40, 40))

        x_header_pos = label_margin + i * cell_size + (cell_size // 2) - 4
        draw.text((x_header_pos, top_margin - 15), str(i), fill=(100, 100, 100))

    for i in range(n_classes):
        for j in range(n_classes):
            cell_x = label_margin + j * cell_size
            cell_y = top_margin + i * cell_size
            val = int(cm[i, j])
            intensity = float(norm_cm[i, j])

            r = int(255 - intensity * (255 - 25))
            g = int(255 - intensity * (255 - 75))
            b = int(255 - intensity * (255 - 190))

            draw.rectangle(
                [cell_x, cell_y, cell_x + cell_size - 1, cell_y + cell_size - 1],
                fill=(r, g, b),
                outline=(210, 210, 210),
            )

            text_col = (255, 255, 255) if intensity > 0.55 else (20, 20, 20)
            text_str = str(val)
            tw = len(text_str) * 7
            draw.text((cell_x + (cell_size - tw) // 2, cell_y + (cell_size // 2) - 6), text_str, fill=text_col)

    # Class Legend
    legend_y = top_margin + n_classes * cell_size + 15
    legend_items = [f"[{idx}] {name}" for idx, name in enumerate(class_names)]
    draw.text((label_margin, legend_y), " | ".join(legend_items), fill=(80, 80, 80))

    img.save(output_path)


def build_tf_dataset(
    df: pd.DataFrame,
    class_to_idx: Dict[str, int],
    project_root: Path,
    batch_size: int = 32,
    is_training: bool = True,
    seed: int = 42,
) -> Any:
    """Build tf.data.Dataset pipeline."""
    import tensorflow as tf

    paths = [str(project_root / p) for p in df["image_path"]]
    labels = [class_to_idx[l] for l in df["label"]]

    def _load_and_preprocess(img_path: str, label_idx: int) -> Tuple[tf.Tensor, tf.Tensor]:
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


def build_maize_model(num_classes: int) -> Tuple[Any, Any]:
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

    model = models.Model(inputs=inputs, outputs=outputs, name="maize_efficientnetb0")
    return model, base_model


class MaizeDiseaseTrainer:
    """Manages two-stage transfer learning and single-pass evaluation for Maize."""

    def __init__(
        self,
        project_root: Optional[Path] = None,
        seed: int = 42,
    ) -> None:
        self.crop = "maize"
        self.project_root = project_root or Path(__file__).resolve().parent.parent
        self.seed = seed
        self.models_dir = self.project_root / "models"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir = self.models_dir / "reports" / "maize"
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
        print("CropDiseaseAI: Two-Stage Transfer Learning Pipeline [MAIZE]")
        print("=" * 80)

        # 1. Load splits
        processed_dir = self.project_root / "datasets" / "processed" / "maize"
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
        classes_file = self.models_dir / "maize_classes.json"
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
        model, base_model = build_maize_model(num_classes=num_classes)
        model_checkpoint_path = self.models_dir / "maize_model.keras"

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
                patience=4,
                restore_best_weights=True,
                verbose=1,
            ),
            callbacks.ReduceLROnPlateau(
                monitor="val_loss",
                factor=0.2,
                patience=2,
                min_lr=1e-6,
                verbose=1,
            ),
            callbacks.ModelCheckpoint(
                filepath=str(model_checkpoint_path),
                monitor="val_loss",
                mode="min",
                save_best_only=True,
                verbose=1,
            ),
        ]

        history1 = model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=stage1_epochs,
            class_weight=class_weight_dict,
            callbacks=stage1_callbacks,
            verbose=1,
        )

        stage1_completed_epochs = len(history1.history["loss"])
        print(f"\nStage 1 finished after {stage1_completed_epochs} epochs.")

        # ==========================================
        # STAGE 2: Fine-Tuning
        # ==========================================
        print("\n" + "=" * 50)
        print("STAGE 2: Fine-Tuning (Top 25 Backbone Layers Unfrozen)")
        print(f"Fine-tuning Learning Rate: 1e-5 | Max Epochs: {stage2_epochs}")
        print("=" * 50)

        base_model.trainable = True
        for layer in base_model.layers[:-25]:
            layer.trainable = False
        for layer in base_model.layers[-25:]:
            if isinstance(layer, layers.BatchNormalization):
                layer.trainable = False
            else:
                layer.trainable = True

        unfrozen_count = sum(1 for l in base_model.layers if l.trainable)
        print(f"Unfrozen backbone layers: {unfrozen_count} (BatchNormalization layers remain frozen)")

        model.compile(
            optimizer=optimizers.Adam(learning_rate=1e-5),
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"],
        )

        best_stage1_val_loss = float(min(history1.history["val_loss"]))
        stage2_checkpoint = callbacks.ModelCheckpoint(
            filepath=str(model_checkpoint_path),
            monitor="val_loss",
            mode="min",
            save_best_only=True,
            verbose=1,
        )
        stage2_checkpoint.best = best_stage1_val_loss

        stage2_callbacks = [
            callbacks.EarlyStopping(
                monitor="val_loss",
                patience=4,
                restore_best_weights=True,
                verbose=1,
            ),
            callbacks.ReduceLROnPlateau(
                monitor="val_loss",
                factor=0.2,
                patience=2,
                min_lr=1e-7,
                verbose=1,
            ),
            stage2_checkpoint,
        ]

        history2 = model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=stage2_epochs,
            class_weight=class_weight_dict,
            callbacks=stage2_callbacks,
            verbose=1,
        )

        # 5. Combined Histories
        comb_loss = [float(v) for v in history1.history["loss"] + history2.history["loss"]]
        comb_val_loss = [float(v) for v in history1.history["val_loss"] + history2.history["val_loss"]]
        comb_acc = [float(v) for v in history1.history["accuracy"] + history2.history["accuracy"]]
        comb_val_acc = [float(v) for v in history1.history["val_accuracy"] + history2.history["val_accuracy"]]

        lr1 = [float(v) for v in history1.history.get("learning_rate", history1.history.get("lr", []))]
        lr2 = [float(v) for v in history2.history.get("learning_rate", history2.history.get("lr", []))]
        comb_lr = lr1 + lr2

        training_history_data = {
            "crop": "maize",
            "architecture": "EfficientNetB0",
            "stage1_epochs_run": stage1_completed_epochs,
            "stage2_epochs_run": len(history2.history["loss"]),
            "total_epochs": len(comb_loss),
            "transition_epoch": stage1_completed_epochs,
            "loss": comb_loss,
            "val_loss": comb_val_loss,
            "accuracy": comb_acc,
            "val_accuracy": comb_val_acc,
            "learning_rate": comb_lr,
            "best_val_loss": round(float(min(comb_val_loss)), 4),
            "best_val_accuracy": round(float(max(comb_val_acc)), 4),
        }

        history_file = self.models_dir / "maize_training_history.json"
        with history_file.open("w", encoding="utf-8") as f:
            json.dump(training_history_data, f, indent=2)
        print(f"\nTraining history saved to: {history_file.relative_to(self.project_root)}")

        # 6. Render Curves
        acc_png_path = self.reports_dir / "training_accuracy.png"
        loss_png_path = self.reports_dir / "training_loss.png"

        render_curve_plot(
            train_values=comb_acc,
            val_values=comb_val_acc,
            title="Maize Disease Classification - Accuracy",
            ylabel="Accuracy",
            output_path=acc_png_path,
            transition_epoch=stage1_completed_epochs,
        )
        print(f"Accuracy plot saved to: {acc_png_path.relative_to(self.project_root)}")

        render_curve_plot(
            train_values=comb_loss,
            val_values=comb_val_loss,
            title="Maize Disease Classification - Loss",
            ylabel="Cross-Entropy Loss",
            output_path=loss_png_path,
            transition_epoch=stage1_completed_epochs,
        )
        print(f"Loss plot saved to: {loss_png_path.relative_to(self.project_root)}")

        # 7. Single-Pass Evaluation on Test Split
        print("\n" + "=" * 50)
        print("SINGLE-PASS INTERNAL TEST EVALUATION (dataset: datasets/processed/maize/test.csv)")
        print("=" * 50)

        print(f"Loading best checkpointed model from {model_checkpoint_path.relative_to(self.project_root)}...")
        best_model = tf.keras.models.load_model(str(model_checkpoint_path))

        y_true = np.array([class_to_idx[l] for l in test_df["label"]], dtype=np.int32)
        image_paths = test_df["image_path"].tolist()
        resolved_paths = [str(self.project_root / p) for p in image_paths]

        def _load_img(path: str) -> tf.Tensor:
            raw = tf.io.read_file(path)
            img = tf.image.decode_jpeg(raw, channels=3)
            img = tf.image.resize(img, [224, 224])
            return img

        test_ds = tf.data.Dataset.from_tensor_slices(resolved_paths)
        test_ds = test_ds.map(_load_img, num_parallel_calls=tf.data.AUTOTUNE)
        test_ds = test_ds.batch(batch_size).prefetch(tf.data.AUTOTUNE)

        print("Generating test set predictions...")
        y_proba = best_model.predict(test_ds, verbose=1)
        y_pred = np.argmax(y_proba, axis=1)
        confidences = np.max(y_proba, axis=1)

        # Metrics
        acc = float(accuracy_score(y_true, y_pred))
        p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(
            y_true, y_pred, average="macro", zero_division=0
        )
        p_weighted, r_weighted, f1_weighted, _ = precision_recall_fscore_support(
            y_true, y_pred, average="weighted", zero_division=0
        )

        cm = confusion_matrix(y_true, y_pred)
        cm_list = cm.tolist()

        clf_report_dict = classification_report(
            y_true, y_pred, target_names=class_names, output_dict=True, zero_division=0
        )
        clf_report_text = classification_report(
            y_true, y_pred, target_names=class_names, zero_division=0
        )

        per_class_metrics: Dict[str, Dict[str, float]] = {}
        f1_scores = {}
        for cls_name in class_names:
            cls_data = clf_report_dict[cls_name]
            per_class_metrics[cls_name] = {
                "precision": round(float(cls_data["precision"]), 4),
                "recall": round(float(cls_data["recall"]), 4),
                "f1_score": round(float(cls_data["f1-score"]), 4),
                "support": int(cls_data["support"]),
            }
            f1_scores[cls_name] = float(cls_data["f1-score"])

        best_class = max(f1_scores, key=f1_scores.get)
        worst_class = min(f1_scores, key=f1_scores.get)

        confused_pairs = []
        for i in range(len(class_names)):
            for j in range(len(class_names)):
                if i != j and cm[i, j] > 0:
                    confused_pairs.append(
                        {
                            "true_class": class_names[i],
                            "predicted_class": class_names[j],
                            "count": int(cm[i, j]),
                        }
                    )
        confused_pairs.sort(key=lambda x: x["count"], reverse=True)

        is_correct = (y_pred == y_true)
        misclassified_rows = []
        for idx in range(len(test_df)):
            if not is_correct[idx]:
                misclassified_rows.append(
                    {
                        "image_path": image_paths[idx],
                        "true_class": class_names[y_true[idx]],
                        "predicted_class": class_names[y_pred[idx]],
                        "predicted_confidence": round(float(confidences[idx]), 4),
                    }
                )

        misclassified_df = pd.DataFrame(misclassified_rows)
        misclassified_csv_path = self.reports_dir / "misclassified.csv"
        misclassified_df.to_csv(misclassified_csv_path, index=False)
        print(f"Misclassified samples logged to: {misclassified_csv_path.relative_to(self.project_root)} ({len(misclassified_rows)} samples)")

        correct_conf = confidences[is_correct]
        incorrect_conf = confidences[~is_correct]
        correct_mean_conf = float(np.mean(correct_conf)) if len(correct_conf) > 0 else 0.0
        incorrect_mean_conf = float(np.mean(incorrect_conf)) if len(incorrect_conf) > 0 else 0.0

        confidence_analysis = {
            "mean_confidence_correct": round(correct_mean_conf, 4),
            "mean_confidence_incorrect": round(incorrect_mean_conf, 4),
            "confidence_distribution": {
                "min": round(float(np.min(confidences)), 4),
                "max": round(float(np.max(confidences)), 4),
                "mean": round(float(np.mean(confidences)), 4),
                "std": round(float(np.std(confidences)), 4),
                "median": round(float(np.median(confidences)), 4),
                "q25": round(float(np.percentile(confidences, 25)), 4),
                "q75": round(float(np.percentile(confidences, 75)), 4),
            },
            "confidence_brackets": {
                "below_0.50": int(np.sum(confidences < 0.50)),
                "0.50_to_0.70": int(np.sum((confidences >= 0.50) & (confidences < 0.70))),
                "0.70_to_0.90": int(np.sum((confidences >= 0.70) & (confidences < 0.90))),
                "0.90_to_1.00": int(np.sum(confidences >= 0.90)),
            },
        }

        # Save artifacts
        cm_png_path = self.reports_dir / "confusion_matrix.png"
        render_confusion_matrix(cm, class_names, cm_png_path, title="Maize Disease Confusion Matrix")
        print(f"Confusion matrix plot saved to: {cm_png_path.relative_to(self.project_root)}")

        report_txt_path = self.reports_dir / "classification_report.txt"
        report_txt_path.write_text(clf_report_text, encoding="utf-8")
        print(f"Classification report saved to: {report_txt_path.relative_to(self.project_root)}")

        metrics_summary = {
            "crop": "maize",
            "test_samples_total": len(test_df),
            "overall_accuracy": round(acc, 4),
            "macro_precision": round(float(p_macro), 4),
            "macro_recall": round(float(r_macro), 4),
            "macro_f1": round(float(f1_macro), 4),
            "weighted_precision": round(float(p_weighted), 4),
            "weighted_recall": round(float(r_weighted), 4),
            "weighted_f1": round(float(f1_weighted), 4),
            "best_performing_class": {
                "class": best_class,
                "f1_score": round(f1_scores[best_class], 4),
            },
            "worst_performing_class": {
                "class": worst_class,
                "f1_score": round(f1_scores[worst_class], 4),
            },
            "per_class_metrics": per_class_metrics,
            "top_confused_pairs": confused_pairs[:10],
            "confidence_analysis": confidence_analysis,
            "misclassified_samples_count": len(misclassified_rows),
            "confusion_matrix": cm_list,
        }

        metrics_json_path = self.reports_dir / "metrics.json"
        with metrics_json_path.open("w", encoding="utf-8") as f:
            json.dump(metrics_summary, f, indent=2)
        print(f"Metrics summary saved to: {metrics_json_path.relative_to(self.project_root)}")

        print("\n" + "=" * 50)
        print("MAIZE EVALUATION SUMMARY:")
        print(f"  Test Accuracy:     {acc * 100:.2f}%")
        print(f"  Macro F1-Score:    {f1_macro * 100:.2f}%")
        print(f"  Weighted F1-Score: {f1_weighted * 100:.2f}%")
        print(f"  Best Class:        {best_class} (F1: {f1_scores[best_class]:.4f})")
        print(f"  Worst Class:       {worst_class} (F1: {f1_scores[worst_class]:.4f})")
        print("=" * 50)

        return {
            "training_history": training_history_data,
            "evaluation_results": metrics_summary,
            "class_names": class_names,
            "model_path": str(model_checkpoint_path.relative_to(self.project_root)),
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="Train Maize disease classification model.")
    parser.add_argument("--stage1-epochs", type=int, default=15, help="Max Stage 1 epochs (default: 15).")
    parser.add_argument("--stage2-epochs", type=int, default=10, help="Max Stage 2 epochs (default: 10).")
    parser.add_argument("--batch-size", type=int, default=32, help="Mini-batch size (default: 32).")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42).")
    args = parser.parse_args()

    trainer = MaizeDiseaseTrainer(seed=args.seed)
    results = trainer.train_and_evaluate(
        stage1_epochs=args.stage1_epochs,
        stage2_epochs=args.stage2_epochs,
        batch_size=args.batch_size,
    )
    print("\nMaize training and evaluation pipeline completed successfully.")


if __name__ == "__main__":
    main()

