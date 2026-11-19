"""Production-grade two-stage transfer learning training pipeline for Paddy Disease AI.

Uses EfficientNetB0 with ImageNet pretrained weights, moderate agricultural
data augmentation, balanced class weighting, two-stage fine-tuning, and robust
callbacks. Followed by single-pass evaluation on internal test split.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from pathlib import Path

# Ensure project root is on sys.path for direct script execution
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from training.evaluate import PaddyModelEvaluator, render_curve_plot
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.utils.class_weight import compute_class_weight


def set_reproducible_seed(seed: int = 42) -> None:
    """Set random seeds across Python, NumPy, and TensorFlow."""
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    import tensorflow as tf

    tf.random.set_seed(seed)


def verify_dataset_prerequisites(crop: str, project_root: Path) -> Dict[str, pd.DataFrame]:
    """Verify presence and validity of processed split files before training.

    Args:
        crop: Crop identifier (e.g., 'paddy').
        project_root: Root directory of CropDiseaseAI.

    Returns:
        Dictionary mapping split name to loaded DataFrame.

    Raises:
        FileNotFoundError: If any required file is missing or unreadable.
    """
    processed_dir = project_root / "datasets" / "processed" / crop
    required_files = {
        "train": processed_dir / "train.csv",
        "validation": processed_dir / "validation.csv",
        "test": processed_dir / "test.csv",
        "report": processed_dir / "dataset_report.json",
    }

    missing = [name for name, path in required_files.items() if not path.exists()]
    if missing:
        raise FileNotFoundError(
            f"Required dataset preparation files missing for '{crop}': {missing}. "
            f"Run training/prepare_dataset.py first."
        )

    dfs = {
        "train": pd.read_csv(required_files["train"]),
        "validation": pd.read_csv(required_files["validation"]),
        "test": pd.read_csv(required_files["test"]),
    }

    # Verify column presence
    for split_name, df in dfs.items():
        if "image_path" not in df.columns or "label" not in df.columns:
            raise ValueError(
                f"Required columns 'image_path' and 'label' missing in {split_name}.csv"
            )

    # Verify sample paths exist
    sample_paths = dfs["train"]["image_path"].head(10).tolist()
    for rel_path in sample_paths:
        abs_path = project_root / rel_path
        if not abs_path.is_file():
            raise FileNotFoundError(f"Image referenced in train.csv not found on disk: {abs_path}")

    return dfs


def print_hardware_status() -> None:
    """Detect and print TensorFlow version and CPU/GPU hardware details."""
    import tensorflow as tf

    print("--- Hardware & Environment ---")
    print(f"TensorFlow version: {tf.__version__}")
    physical_gpus = tf.config.list_physical_devices("GPU")
    print(f"Physical GPU devices: {physical_gpus}")
    if physical_gpus:
        print(f"TensorFlow detects GPU: {physical_gpus}")
    else:
        print("TensorFlow is training on CPU.")
    print("------------------------------\n")


def build_tf_dataset(
    df: pd.DataFrame,
    class_to_idx: Dict[str, int],
    project_root: Path,
    batch_size: int = 32,
    is_training: bool = True,
    seed: int = 42,
) -> Any:
    """Build optimized tf.data.Dataset pipeline.

    Args:
        df: DataFrame containing 'image_path' and 'label'.
        class_to_idx: Mapping of class name to integer target.
        project_root: Project root path.
        batch_size: Mini-batch size.
        is_training: If True, shuffle with buffer.
        seed: Random seed for shuffling.

    Returns:
        Configured tf.data.Dataset ready for model.fit.
    """
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


def build_efficientnet_model(num_classes: int) -> Tuple[Any, Any]:
    """Build transfer learning model with EfficientNetB0 backbone and moderate augmentation.

    Args:
        num_classes: Dynamic number of disease output classes.

    Returns:
        Tuple of (full_model, base_backbone_model).
    """
    import tensorflow as tf
    from tensorflow.keras import layers, models
    from tensorflow.keras.applications import EfficientNetB0

    inputs = layers.Input(shape=(224, 224, 3), name="input_image")

    # Moderate agricultural image augmentation (active only during training)
    x = layers.RandomFlip("horizontal", name="aug_random_flip")(inputs)
    x = layers.RandomRotation(0.08, fill_mode="reflect", name="aug_random_rotation")(x)
    x = layers.RandomZoom(0.08, fill_mode="reflect", name="aug_random_zoom")(x)
    x = layers.RandomContrast(0.10, name="aug_random_contrast")(x)

    # Pretrained EfficientNetB0 backbone
    base_model = EfficientNetB0(
        weights="imagenet",
        include_top=False,
        input_tensor=x,
    )
    base_model.trainable = False

    # Classification head
    x = layers.GlobalAveragePooling2D(name="global_avg_pool")(base_model.output)
    x = layers.Dropout(0.3, name="top_dropout")(x)
    outputs = layers.Dense(num_classes, activation="softmax", name="classification_head")(x)

    model = models.Model(inputs=inputs, outputs=outputs, name="paddy_efficientnetb0")
    return model, base_model


class PaddyDiseaseTrainer:
    """Manages two-stage transfer learning training for Paddy Disease classification."""

    def __init__(
        self,
        crop: str = "paddy",
        project_root: Optional[Path] = None,
        seed: int = 42,
    ) -> None:
        self.crop = crop
        self.project_root = project_root or Path(__file__).resolve().parent.parent
        self.seed = seed
        self.models_dir = self.project_root / "models"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir = self.models_dir / "reports" / crop
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
        print(f"CropDiseaseAI: Two-Stage Transfer Learning Pipeline [{self.crop.upper()}]")
        print("=" * 80)

        # 1. Hardware Status
        print_hardware_status()

        # 2. Verify Prerequisites
        print("Verifying dataset split files...")
        dfs = verify_dataset_prerequisites(self.crop, self.project_root)
        train_df = dfs["train"]
        val_df = dfs["validation"]
        test_df = dfs["test"]

        # Extract classes dynamically from dataset
        class_names = sorted(train_df["label"].unique().tolist())
        num_classes = len(class_names)
        class_to_idx = {name: i for i, name in enumerate(class_names)}
        idx_to_class = {str(i): name for i, name in enumerate(class_names)}

        print(f"Number of training samples:   {len(train_df)}")
        print(f"Number of validation samples: {len(val_df)}")
        print(f"Number of internal test samples: {len(test_df)}")
        print(f"Number of classes: {num_classes}")
        print(f"Class names: {class_names}")
        print("\nClass distribution (training split):")
        train_counts = train_df["label"].value_counts()
        for c in class_names:
            print(f"  {c:<25}: {train_counts.get(c, 0)} ({train_counts.get(c, 0)/len(train_df)*100:.2f}%)")

        # Save class mapping
        classes_file = self.models_dir / f"{self.crop}_classes.json"
        with classes_file.open("w", encoding="utf-8") as f:
            json.dump(idx_to_class, f, indent=2)
        print(f"\nExact class mapping saved to: {classes_file.relative_to(self.project_root)}")

        # 3. Class Imbalance Weights
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

        # 4. Build Data Pipelines
        print("\nBuilding tf.data pipelines...")
        train_ds = build_tf_dataset(
            train_df, class_to_idx, self.project_root, batch_size=batch_size, is_training=True, seed=self.seed
        )
        val_ds = build_tf_dataset(
            val_df, class_to_idx, self.project_root, batch_size=batch_size, is_training=False
        )

        # 5. Build Model
        print("\nBuilding EfficientNetB0 transfer learning architecture...")
        model, base_model = build_efficientnet_model(num_classes=num_classes)
        model_checkpoint_path = self.models_dir / f"{self.crop}_model.keras"

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
        # Keep lower layers frozen, unfreeze top 25 non-BatchNorm layers
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

        # 6. Combine Training Histories
        comb_loss = [float(v) for v in history1.history["loss"] + history2.history["loss"]]
        comb_val_loss = [float(v) for v in history1.history["val_loss"] + history2.history["val_loss"]]
        comb_acc = [float(v) for v in history1.history["accuracy"] + history2.history["accuracy"]]
        comb_val_acc = [float(v) for v in history1.history["val_accuracy"] + history2.history["val_accuracy"]]

        # Extract learning rate info safely
        lr1 = [float(v) for v in history1.history.get("learning_rate", history1.history.get("lr", []))]
        lr2 = [float(v) for v in history2.history.get("learning_rate", history2.history.get("lr", []))]
        comb_lr = lr1 + lr2

        training_history_data = {
            "crop": self.crop,
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

        history_file = self.models_dir / f"{self.crop}_training_history.json"
        with history_file.open("w", encoding="utf-8") as f:
            json.dump(training_history_data, f, indent=2)
        print(f"\nTraining history saved to: {history_file.relative_to(self.project_root)}")

        # 7. Generate Training & Validation Plots
        acc_png_path = self.reports_dir / "training_accuracy.png"
        loss_png_path = self.reports_dir / "training_loss.png"

        render_curve_plot(
            train_values=comb_acc,
            val_values=comb_val_acc,
            title="Paddy Disease Classification - Accuracy",
            ylabel="Accuracy",
            output_path=acc_png_path,
            transition_epoch=stage1_completed_epochs,
        )
        print(f"Accuracy plot saved to: {acc_png_path.relative_to(self.project_root)}")

        render_curve_plot(
            train_values=comb_loss,
            val_values=comb_val_loss,
            title="Paddy Disease Classification - Loss",
            ylabel="Cross-Entropy Loss",
            output_path=loss_png_path,
            transition_epoch=stage1_completed_epochs,
        )
        print(f"Loss plot saved to: {loss_png_path.relative_to(self.project_root)}")

        # 8. Load Best Checkpointed Model for Evaluation
        print(f"\nLoading best checkpointed model from {model_checkpoint_path.relative_to(self.project_root)} for final evaluation...")
        best_model = tf.keras.models.load_model(str(model_checkpoint_path))

        # 9. Internal Test Set Evaluation (ONLY ONCE)
        print("\n" + "=" * 50)
        print("INTERNAL TEST EVALUATION (dataset: datasets/processed/paddy/test.csv)")
        print("=" * 50)

        evaluator = PaddyModelEvaluator(self.project_root)
        test_csv_path = self.project_root / "datasets" / "processed" / self.crop / "test.csv"
        evaluation_results = evaluator.evaluate_model(
            model=best_model,
            test_csv_path=test_csv_path,
            class_names=class_names,
            batch_size=batch_size,
        )

        return {
            "training_history": training_history_data,
            "evaluation_results": evaluation_results,
            "class_names": class_names,
            "model_path": str(model_checkpoint_path.relative_to(self.project_root)),
        }


def main() -> None:
    """CLI entry point for model training."""
    parser = argparse.ArgumentParser(description="Train Paddy disease classification model.")
    parser.add_argument("--crop", type=str, default="paddy", help="Crop identifier (default: paddy).")
    parser.add_argument("--stage1-epochs", type=int, default=15, help="Max Stage 1 epochs (default: 15).")
    parser.add_argument("--stage2-epochs", type=int, default=10, help="Max Stage 2 fine-tuning epochs (default: 10).")
    parser.add_argument("--batch-size", type=int, default=32, help="Mini-batch size (default: 32).")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42).")
    args = parser.parse_args()

    trainer = PaddyDiseaseTrainer(crop=args.crop, seed=args.seed)
    results = trainer.train_and_evaluate(
        stage1_epochs=args.stage1_epochs,
        stage2_epochs=args.stage2_epochs,
        batch_size=args.batch_size,
    )
    print("\nTraining and evaluation pipeline finished successfully.")


if __name__ == "__main__":
    main()
