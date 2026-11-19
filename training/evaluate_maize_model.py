"""Production evaluation and artifact generation script for CropDiseaseAI - Maize Module (Phase 4).

Generates:
1. models/maize_training_history.json (from completed epochs 1-18)
2. models/reports/maize/training_accuracy.png
3. models/reports/maize/training_loss.png
4. models/reports/maize/confusion_matrix.png
5. models/reports/maize/classification_report.txt
6. models/reports/maize/metrics.json
7. models/reports/maize/misclassified.csv
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sys
from typing import Dict, List, Tuple

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
from PIL import Image, ImageDraw
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)
import tensorflow as tf
from tensorflow.keras.models import load_model

from training.train_maize import render_curve_plot, render_confusion_matrix


def parse_training_history_from_log(log_path: Path) -> Dict:
    """Extract metrics for all completed epochs from task-1064.log."""
    text = log_path.read_text(encoding="utf-8", errors="ignore")
    pattern = re.compile(
        r"(\d+)/(\d+)\s+.*?-\s+accuracy:\s+([0-9.]+)\s+-\s+loss:\s+([0-9.]+)\s+-\s+val_accuracy:\s+([0-9.]+)\s+-\s+val_loss:\s+([0-9.]+)(?:\s+-\s+(?:learning_rate|lr):\s+([0-9.eE+-]+))?"
    )
    matches = pattern.findall(text)
    
    accuracies = [float(m[2]) for m in matches]
    losses = [float(m[3]) for m in matches]
    val_accuracies = [float(m[4]) for m in matches]
    val_losses = [float(m[5]) for m in matches]
    lrs = [float(m[6]) if m[6] else 0.001 for m in matches]

    history_data = {
        "crop": "maize",
        "architecture": "EfficientNetB0",
        "stage1_epochs_run": 15,
        "stage2_epochs_run": len(matches) - 15,
        "total_epochs": len(matches),
        "transition_epoch": 15,
        "loss": losses,
        "val_loss": val_losses,
        "accuracy": accuracies,
        "val_accuracy": val_accuracies,
        "learning_rate": lrs,
        "best_epoch": 15,
        "best_val_loss": round(float(min(val_losses)), 4),
        "best_val_accuracy": round(float(max(val_accuracies)), 4),
    }
    return history_data


def main() -> None:
    print("=" * 80)
    print("CropDiseaseAI: Maize Phase 4 Final Single-Pass Evaluation & Artifact Generation")
    print("=" * 80)

    models_dir = _project_root / "models"
    reports_dir = models_dir / "reports" / "maize"
    reports_dir.mkdir(parents=True, exist_ok=True)

    # 1. Parse training history and generate history JSON
    log_path = Path(r"C:\Users\vamsi\.gemini\antigravity\brain\e34cdf28-8ed1-44e2-a536-362892ec6aef\.system_generated\tasks\task-1064.log")
    history_data = parse_training_history_from_log(log_path)
    history_file = models_dir / "maize_training_history.json"
    with history_file.open("w", encoding="utf-8") as f:
        json.dump(history_data, f, indent=2)
    print(f"[1/7] Saved training history ({history_data['total_epochs']} completed epochs) to: {history_file.relative_to(_project_root)}")

    # 2. Render training curves
    acc_png = reports_dir / "training_accuracy.png"
    loss_png = reports_dir / "training_loss.png"
    render_curve_plot(
        train_values=history_data["accuracy"],
        val_values=history_data["val_accuracy"],
        title="Maize Disease Classification - Accuracy",
        ylabel="Accuracy",
        output_path=acc_png,
        transition_epoch=15,
    )
    print(f"[2/7] Saved accuracy curves to: {acc_png.relative_to(_project_root)}")

    render_curve_plot(
        train_values=history_data["loss"],
        val_values=history_data["val_loss"],
        title="Maize Disease Classification - Loss",
        ylabel="Cross-Entropy Loss",
        output_path=loss_png,
        transition_epoch=15,
    )
    print(f"[3/7] Saved loss curves to: {loss_png.relative_to(_project_root)}")

    # 3. Load model and class mapping
    classes_file = models_dir / "maize_classes.json"
    with classes_file.open("r", encoding="utf-8") as f:
        idx_to_class = json.load(f)
    class_names = [idx_to_class[str(i)] for i in range(len(idx_to_class))]
    class_to_idx = {name: i for i, name in enumerate(class_names)}
    print(f"Loaded class mapping: {class_to_idx}")

    model_file = models_dir / "maize_model.keras"
    print(f"Loading best checkpoint model from: {model_file.relative_to(_project_root)}")
    model = load_model(str(model_file))
    print(f"Model successfully loaded! Input shape: {model.input_shape}, Output shape: {model.output_shape}")

    # 4. Load internal test set
    test_csv = _project_root / "datasets" / "processed" / "maize" / "test.csv"
    test_df = pd.read_csv(test_csv)
    print(f"\nInternal test dataset: {test_csv.relative_to(_project_root)} ({len(test_df)} samples)")

    y_true = np.array([class_to_idx[l] for l in test_df["label"]], dtype=np.int32)
    resolved_paths = [str(_project_root / p) for p in test_df["image_path"]]

    def _load_img(p: str) -> tf.Tensor:
        raw = tf.io.read_file(p)
        img = tf.image.decode_jpeg(raw, channels=3)
        img = tf.image.resize(img, [224, 224])
        return img

    test_ds = tf.data.Dataset.from_tensor_slices(resolved_paths)
    test_ds = test_ds.map(_load_img, num_parallel_calls=tf.data.AUTOTUNE)
    test_ds = test_ds.batch(32).prefetch(tf.data.AUTOTUNE)

    print("Running single-pass evaluation inference on test split...")
    y_proba = model.predict(test_ds, verbose=1)
    y_pred = np.argmax(y_proba, axis=1)
    confidences = np.max(y_proba, axis=1)

    # 5. Compute Metrics
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
        c_data = clf_report_dict[cls_name]
        per_class_metrics[cls_name] = {
            "precision": round(float(c_data["precision"]), 4),
            "recall": round(float(c_data["recall"]), 4),
            "f1_score": round(float(c_data["f1-score"]), 4),
            "support": int(c_data["support"]),
        }
        f1_scores[cls_name] = float(c_data["f1-score"])

    best_class = max(f1_scores, key=f1_scores.get)
    worst_class = min(f1_scores, key=f1_scores.get)

    confused_pairs = []
    for i in range(len(class_names)):
        for j in range(len(class_names)):
            if i != j and cm[i, j] > 0:
                confused_pairs.append({
                    "true_class": class_names[i],
                    "predicted_class": class_names[j],
                    "count": int(cm[i, j]),
                })
    confused_pairs.sort(key=lambda x: x["count"], reverse=True)

    is_correct = (y_pred == y_true)
    misclassified_rows = []
    for idx in range(len(test_df)):
        if not is_correct[idx]:
            misclassified_rows.append({
                "image_path": test_df["image_path"].iloc[idx],
                "true_class": class_names[y_true[idx]],
                "predicted_class": class_names[y_pred[idx]],
                "predicted_confidence": round(float(confidences[idx]), 4),
            })

    misclassified_df = pd.DataFrame(misclassified_rows)
    misclassified_csv = reports_dir / "misclassified.csv"
    misclassified_df.to_csv(misclassified_csv, index=False)
    print(f"[4/7] Saved misclassified samples ({len(misclassified_rows)} errors) to: {misclassified_csv.relative_to(_project_root)}")

    correct_conf = confidences[is_correct]
    incorrect_conf = confidences[~is_correct]

    confidence_analysis = {
        "mean_confidence_correct": round(float(np.mean(correct_conf)), 4) if len(correct_conf) > 0 else 0.0,
        "mean_confidence_incorrect": round(float(np.mean(incorrect_conf)), 4) if len(incorrect_conf) > 0 else 0.0,
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

    # Render confusion matrix
    cm_png = reports_dir / "confusion_matrix.png"
    render_confusion_matrix(cm, class_names, cm_png, title="Maize Disease Confusion Matrix")
    print(f"[5/7] Saved confusion matrix to: {cm_png.relative_to(_project_root)}")

    # Classification report text
    report_txt = reports_dir / "classification_report.txt"
    report_txt.write_text(clf_report_text, encoding="utf-8")
    print(f"[6/7] Saved classification report text to: {report_txt.relative_to(_project_root)}")

    # Metrics JSON
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

    metrics_json = reports_dir / "metrics.json"
    with metrics_json.open("w", encoding="utf-8") as f:
        json.dump(metrics_summary, f, indent=2)
    print(f"[7/7] Saved metrics JSON to: {metrics_json.relative_to(_project_root)}")

    print("\n" + "=" * 50)
    print("FINAL MAIZE EVALUATION RESULTS:")
    print(f"  Test Accuracy:     {acc * 100:.2f}%")
    print(f"  Macro F1-Score:    {f1_macro * 100:.2f}%")
    print(f"  Weighted F1-Score: {f1_weighted * 100:.2f}%")
    print(f"  Best Class:        {best_class} (F1: {f1_scores[best_class]:.4f})")
    print(f"  Worst Class:       {worst_class} (F1: {f1_scores[worst_class]:.4f})")
    print("=" * 50)
    print("\nClassification Report:\n")
    print(clf_report_text)
    print("\nConfusion Matrix:")
    print(cm)


if __name__ == "__main__":
    main()

