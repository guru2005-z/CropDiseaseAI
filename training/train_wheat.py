"""Production-grade two-stage transfer learning training and evaluation pipeline for Wheat Disease AI.

CropDiseaseAI: Wheat Module.
Architecture: EfficientNetB0 (ImageNet pretrained), two-stage transfer learning,
moderate agricultural augmentation, balanced class weighting, and comprehensive
single-pass evaluation on internal test split (datasets/processed/wheat/test.csv).

Preserves Paddy, Maize, Groundnut, Chilli, and Banana models, datasets, and configurations 100% intact.
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

    min_v = max(0.0, min(all_vals) * 0.9)
    max_v = max(all_vals) * 1.05
    if max_v == min_v:
        max_v += 1.0

    n_epochs = len(train_values)

    draw.rectangle(
        [(margin_left, margin_top), (margin_left + plot_w, margin_top + plot_h)],
        fill=(250, 250, 250),
        outline=(210, 210, 210),
        width=1,
    )

    for i in range(5):
        val = min_v + (max_v - min_v) * (i / 4.0)
        y = margin_top + plot_h - int((val - min_v) / (max_v - min_v) * plot_h)
        draw.line([(margin_left, y), (margin_left + plot_w, y)], fill=(230, 230, 230), width=1)
        draw.text((margin_left - 65, y - 6), f"{val:.2f}", fill=(100, 100, 100))

    for ep in range(1, n_epochs + 1):
        if n_epochs > 1:
            x = margin_left + int((ep - 1) / (n_epochs - 1) * plot_w)
        else:
            x = margin_left + plot_w // 2
        draw.line([(x, margin_top), (x, margin_top + plot_h)], fill=(240, 240, 240), width=1)
        if ep == 1 or ep % 2 == 0 or ep == n_epochs:
            draw.text((x - 6, margin_top + plot_h + 8), str(ep), fill=(100, 100, 100))

    if transition_epoch and 1 < transition_epoch <= n_epochs:
        trans_x = margin_left + int((transition_epoch - 1) / (n_epochs - 1) * plot_w)
        draw.line([(trans_x, margin_top), (trans_x, margin_top + plot_h)], fill=(200, 80, 80), width=2)
        draw.text((trans_x - 45, margin_top + 10), "Stage 2 (Fine-Tune)", fill=(180, 50, 50))

    def _val_to_pt(epoch_idx: int, val: float) -> Tuple[int, int]:
        x = margin_left + int(epoch_idx / (n_epochs - 1) * plot_w) if n_epochs > 1 else margin_left + plot_w // 2
        y = margin_top + plot_h - int((val - min_v) / (max_v - min_v) * plot_h)
        return (x, y)

    if n_epochs > 1:
        train_pts = [_val_to_pt(i, v) for i, v in enumerate(train_values)]
        draw.line(train_pts, fill=(30, 120, 220), width=3)
        for pt in train_pts:
            draw.ellipse([(pt[0] - 3, pt[1] - 3), (pt[0] + 3, pt[1] + 3)], fill=(20, 90, 180))

        val_pts = [_val_to_pt(i, v) for i, v in enumerate(val_values)]
        draw.line(val_pts, fill=(220, 80, 40), width=3)
        for pt in val_pts:
            draw.ellipse([(pt[0] - 3, pt[1] - 3), (pt[0] + 3, pt[1] + 3)], fill=(180, 50, 20))

    draw.text((margin_left, margin_top - 40), title, fill=(20, 20, 20))
    draw.text((margin_left + plot_w // 2 - 20, margin_top + plot_h + 30), "Epoch", fill=(50, 50, 50))
    draw.text((margin_left - 70, margin_top - 40), ylabel, fill=(50, 50, 50))

    leg_x = margin_left + plot_w - 200
    leg_y = margin_top + 10
    draw.rectangle([(leg_x, leg_y), (leg_x + 190, leg_y + 45)], fill=(255, 255, 255), outline=(200, 200, 200))
    draw.line([(leg_x + 10, leg_y + 15), (leg_x + 35, leg_y + 15)], fill=(30, 120, 220), width=3)
    draw.text((leg_x + 45, leg_y + 9), "Training", fill=(40, 40, 40))
    draw.line([(leg_x + 10, leg_y + 32), (leg_x + 35, leg_y + 32)], fill=(220, 80, 40), width=3)
    draw.text((leg_x + 45, leg_y + 26), "Validation", fill=(40, 40, 40))

    img.save(output_path)


def render_confusion_matrix_plot(
    cm: np.ndarray,
    class_names: List[str],
    output_path: Path,
    title: str = "Wheat Disease AI - Test Confusion Matrix",
) -> None:
    """Render a clean confusion matrix heatmap using Pillow."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    n_classes = len(class_names)
    cell_size = 110
    margin_left = 180
    margin_bottom = 90
    margin_top = 70
    margin_right = 50

    width = margin_left + n_classes * cell_size + margin_right
    height = margin_top + n_classes * cell_size + margin_bottom

    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    draw.text((margin_left, 20), title, fill=(20, 20, 20))

    max_val = max(1, int(np.max(cm)))

    for r in range(n_classes):
        for c in range(n_classes):
            val = int(cm[r, c])
            intensity = val / max_val
            if r == c:
                red = int(245 - 200 * intensity)
                green = int(250 - 90 * intensity)
                blue = int(245 - 200 * intensity)
            else:
                red = 255
                green = int(255 - 180 * intensity)
                blue = int(255 - 180 * intensity)

            x0 = margin_left + c * cell_size
            y0 = margin_top + r * cell_size
            x1 = x0 + cell_size
            y1 = y0 + cell_size

            draw.rectangle([(x0, y0), (x1, y1)], fill=(red, green, blue), outline=(210, 210, 210))
            text_color = (255, 255, 255) if intensity > 0.6 else (30, 30, 30)
            val_str = str(val)
            draw.text((x0 + cell_size // 2 - 8, y0 + cell_size // 2 - 8), val_str, fill=text_color)

    for r, name in enumerate(class_names):
        y = margin_top + r * cell_size + cell_size // 2 - 8
        draw.text((20, y), name, fill=(50, 50, 50))
    draw.text((20, margin_top - 25), "True Label →", fill=(30, 30, 30))

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
    """Build tf.data.Dataset pipeline."""
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


def build_wheat_model(num_classes: int) -> Tuple[Any, Any]:
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

    model = models.Model(inputs=inputs, outputs=outputs, name="wheat_efficientnetb0")
    return model, base_model


class WheatDiseaseTrainer:
    """Manages two-stage transfer learning and single-pass evaluation for Wheat."""

    def __init__(
        self,
        project_root: Optional[Path] = None,
        seed: int = 42,
    ) -> None:
        self.crop = "wheat"
        self.project_root = project_root or Path(__file__).resolve().parent.parent
        self.seed = seed
        self.models_dir = self.project_root / "models"
        self.reports_dir = self.models_dir / "reports" / "wheat"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        set_reproducible_seed(self.seed)

        # Load class mappings
        classes_path = self.models_dir / "wheat_classes.json"
        with open(classes_path, "r", encoding="utf-8") as f:
            mapping = json.load(f)
        if all(k.isdigit() for k in mapping.keys()):
            self.class_names = [mapping[str(i)] for i in range(len(mapping))]
        else:
            self.class_names = sorted(list(mapping.keys()))
        self.class_to_idx = {name: i for i, name in enumerate(self.class_names)}
        self.idx_to_class = {i: name for i, name in enumerate(self.class_names)}
        self.num_classes = len(self.class_names)

        # Load CSV splits
        self.train_csv = self.project_root / "datasets" / "processed" / "wheat" / "train.csv"
        self.val_csv = self.project_root / "datasets" / "processed" / "wheat" / "validation.csv"
        self.test_csv = self.project_root / "datasets" / "processed" / "wheat" / "test.csv"

        self.df_train = pd.read_csv(self.train_csv)
        self.df_val = pd.read_csv(self.val_csv)
        self.df_test = pd.read_csv(self.test_csv)

        # Balanced class weights
        y_train = [self.class_to_idx[l] for l in self.df_train["label"]]
        classes_arr = np.arange(self.num_classes)
        weights_arr = compute_class_weight("balanced", classes=classes_arr, y=y_train)
        self.class_weights: Dict[int, float] = {int(c): float(w) for c, w in zip(classes_arr, weights_arr)}

    def run_training_pipeline(
        self,
        stage1_epochs: int = 10,
        stage2_epochs: int = 6,
        batch_size: int = 32,
        stage1_lr: float = 1e-3,
        stage2_lr: float = 1e-4,
    ) -> Dict[str, Any]:
        """Execute Stage 1 feature extraction and Stage 2 fine-tuning."""
        import tensorflow as tf
        from tensorflow.keras import callbacks, optimizers

        print("=" * 80)
        print("CropDiseaseAI: Two-Stage Transfer Learning Pipeline [WHEAT]")
        print("=" * 80)
        print(f"Loaded {len(self.df_train)} train, {len(self.df_val)} val, {len(self.df_test)} test samples across {self.num_classes} classes.")
        print(f"Classes: {self.class_names}")
        print(f"Balanced Class Weights: {self.class_weights}")

        train_ds = build_tf_dataset(self.df_train, self.class_to_idx, self.project_root, batch_size=batch_size, is_training=True, seed=self.seed)
        val_ds = build_tf_dataset(self.df_val, self.class_to_idx, self.project_root, batch_size=batch_size, is_training=False, seed=self.seed)
        test_ds = build_tf_dataset(self.df_test, self.class_to_idx, self.project_root, batch_size=batch_size, is_training=False, seed=self.seed)

        model, base_model = build_wheat_model(self.num_classes)

        best_weights_path = self.models_dir / "wheat_best_weights.weights.h5"
        checkpoint_cb = callbacks.ModelCheckpoint(
            filepath=str(best_weights_path),
            monitor="val_accuracy",
            mode="max",
            save_best_only=True,
            save_weights_only=True,
            verbose=1,
        )

        # STAGE 1: Feature Extraction
        print("\n--- STAGE 1: Feature Extraction (Backbone Frozen) ---")
        model.compile(
            optimizer=optimizers.Adam(learning_rate=stage1_lr),
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"],
        )

        history1 = model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=stage1_epochs,
            class_weight=self.class_weights,
            callbacks=[checkpoint_cb],
        )

        # STAGE 2: Fine-Tuning
        print(f"\n--- STAGE 2: Fine-Tuning (Unthawing Top 25 Layers at LR={stage2_lr}) ---")
        base_model.trainable = True
        for layer in base_model.layers[:-25]:
            layer.trainable = False

        model.compile(
            optimizer=optimizers.Adam(learning_rate=stage2_lr),
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"],
        )

        history2 = model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=stage1_epochs + stage2_epochs,
            initial_epoch=stage1_epochs,
            class_weight=self.class_weights,
            callbacks=[checkpoint_cb],
        )

        # Restore best weights and save final artifact
        if best_weights_path.exists():
            print(f"Loading best weights from {best_weights_path}")
            model.load_weights(str(best_weights_path))

        final_model_path = self.models_dir / "wheat_model.keras"
        model.save(final_model_path)
        print(f"Saved complete production model artifact to: {final_model_path}")

        # Combine histories
        train_acc = history1.history["accuracy"] + history2.history["accuracy"]
        val_acc = history1.history["val_accuracy"] + history2.history["val_accuracy"]
        train_loss = history1.history["loss"] + history2.history["loss"]
        val_loss = history1.history["val_loss"] + history2.history["val_loss"]

        render_curve_plot(
            train_acc, val_acc, "Wheat Disease AI - Training & Validation Accuracy", "Accuracy",
            self.reports_dir / "accuracy_curve.png", transition_epoch=stage1_epochs + 1
        )
        render_curve_plot(
            train_loss, val_loss, "Wheat Disease AI - Training & Validation Loss", "Loss",
            self.reports_dir / "loss_curve.png", transition_epoch=stage1_epochs + 1
        )

        # Single-pass evaluation on Test Set
        print("\n" + "=" * 80)
        print("INDEPENDENT EVALUATION ON TEST SET (datasets/processed/wheat/test.csv)")
        print("=" * 80)

        y_true_all: List[int] = []
        y_pred_all: List[int] = []

        for images, labels in test_ds:
            preds = model.predict(images, verbose=0)
            preds_idx = np.argmax(preds, axis=-1)
            y_true_all.extend(labels.numpy().tolist())
            y_pred_all.extend(preds_idx.tolist())

        y_true = np.array(y_true_all)
        y_pred = np.array(y_pred_all)

        test_acc = float(accuracy_score(y_true, y_pred))
        prec_macro, rec_macro, f1_macro, _ = precision_recall_fscore_support(y_true, y_pred, average="macro", zero_division=0)
        prec_weighted, rec_weighted, f1_weighted, _ = precision_recall_fscore_support(y_true, y_pred, average="weighted", zero_division=0)

        cm = confusion_matrix(y_true, y_pred, labels=np.arange(self.num_classes))
        render_confusion_matrix_plot(cm, self.class_names, self.reports_dir / "confusion_matrix.png")

        per_class_metrics: Dict[str, Dict[str, float]] = {}
        for idx, cls_name in enumerate(self.class_names):
            y_t_binary = (y_true == idx).astype(int)
            y_p_binary = (y_pred == idx).astype(int)
            p, r, f, s = precision_recall_fscore_support(y_t_binary, y_p_binary, average="binary", zero_division=0)
            per_class_metrics[cls_name] = {
                "precision": round(float(p), 4),
                "recall": round(float(r), 4),
                "f1_score": round(float(f), 4),
                "support": int(np.sum(y_true == idx)),
            }

        eval_report = {
            "crop": "wheat",
            "model_architecture": "EfficientNetB0 (Two-Stage Transfer Learning)",
            "test_sample_count": len(y_true),
            "overall_accuracy": round(test_acc, 4),
            "macro_precision": round(float(prec_macro), 4),
            "macro_recall": round(float(rec_macro), 4),
            "macro_f1": round(float(f1_macro), 4),
            "weighted_f1": round(float(f1_weighted), 4),
            "classes": self.class_names,
            "per_class": per_class_metrics,
            "confusion_matrix": cm.tolist(),
        }

        report_file = self.reports_dir / "test_evaluation_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(eval_report, f, indent=2)

        print(f"\nOverall Test Accuracy: {test_acc * 100:.2f}%")
        print(f"Macro Precision:       {prec_macro * 100:.2f}%")
        print(f"Macro Recall:          {rec_macro * 100:.2f}%")
        print(f"Macro F1-Score:        {f1_macro * 100:.2f}%")
        print(f"Weighted F1-Score:     {f1_weighted * 100:.2f}%")
        print("\nPer-Class Performance:")
        for cls_name, m in per_class_metrics.items():
            print(f"  • {cls_name:<24} -> Prec: {m['precision']*100:.2f}% | Rec: {m['recall']*100:.2f}% | F1: {m['f1_score']*100:.2f}% | Support: {m['support']}")

        print(f"\nReports & plots generated in: {self.reports_dir}")
        return eval_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Train Wheat Disease AI Transfer Learning Model.")
    parser.add_argument("--stage1-epochs", type=int, default=10, help="Epochs for feature extraction.")
    parser.add_argument("--stage2-epochs", type=int, default=6, help="Epochs for fine-tuning.")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size.")
    args = parser.parse_args()

    trainer = WheatDiseaseTrainer()
    trainer.run_training_pipeline(
        stage1_epochs=args.stage1_epochs,
        stage2_epochs=args.stage2_epochs,
        batch_size=args.batch_size,
    )


if __name__ == "__main__":
    main()
