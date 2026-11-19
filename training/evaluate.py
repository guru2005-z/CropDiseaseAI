"""Evaluation and reporting module for CropDiseaseAI models.

Computes comprehensive classification metrics, confusion matrices, per-class
performance, misclassified image logs, confidence distributions, and renders
visual reports (curves and confusion matrix heatmaps) using Pillow without
external GUI or dependency conflicts.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)


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
    """Render a clean training/validation curve image using Pillow.

    Args:
        train_values: List of metric values per epoch on train set.
        val_values: List of metric values per epoch on validation set.
        title: Plot title.
        ylabel: Y-axis label name.
        output_path: Destination path for PNG file.
        transition_epoch: Epoch index where fine-tuning started.
        width: Image width in pixels.
        height: Image height in pixels.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    margin_left = 80
    margin_right = 50
    margin_top = 60
    margin_bottom = 60

    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom

    # Determine bounds
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
            y = margin_top + plot_h - int(plot_h * ((v - y_min) / (y_max - y_min)))
            coords.append((x, y))
        return coords

    train_coords = to_coords(train_values)
    val_coords = to_coords(val_values)

    # Draw curves
    train_color = (30, 110, 220)   # Blue
    val_color = (220, 90, 30)       # Orange

    for pts, col in [(train_coords, train_color), (val_coords, val_color)]:
        for j in range(len(pts) - 1):
            draw.line([pts[j], pts[j + 1]], fill=col, width=2)
        for pt in pts:
            draw.ellipse([pt[0] - 2, pt[1] - 2, pt[0] + 2, pt[1] + 2], fill=col)

    # Draw Stage Transition line if specified
    if transition_epoch and 1 <= transition_epoch <= n_epochs:
        trans_x = margin_left + int(plot_w * ((transition_epoch - 1) / max(n_epochs - 1, 1)))
        for dy in range(margin_top, margin_top + plot_h, 6):
            draw.line([trans_x, dy, trans_x, min(dy + 3, margin_top + plot_h)], fill=(120, 120, 120), width=1)
        draw.text((trans_x + 4, margin_top + 10), "Fine-Tuning Start", fill=(100, 100, 100))

    # Title & Legend
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
) -> None:
    """Render confusion matrix heatmap with cell counts using Pillow.

    Args:
        cm: 2D numpy array containing integer confusion matrix.
        class_names: Ordered list of class labels.
        output_path: Destination path for confusion_matrix.png.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    n_classes = len(class_names)
    cell_size = 54
    label_margin = 170
    top_margin = 70
    bottom_margin = 40
    right_margin = 70

    img_w = label_margin + n_classes * cell_size + right_margin
    img_h = top_margin + n_classes * cell_size + bottom_margin

    img = Image.new("RGB", (img_w, img_h), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Title
    draw.text((label_margin, 20), "Paddy Disease Confusion Matrix", fill=(10, 10, 10))
    draw.text((label_margin + (n_classes * cell_size) // 2 - 40, top_margin - 22), "Predicted Label", fill=(80, 80, 80))
    draw.text((15, top_margin - 22), "True Label", fill=(80, 80, 80))

    # Row normalize for heatmap shading
    row_sums = cm.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    norm_cm = cm / row_sums

    for i in range(n_classes):
        # Y axis label
        label_text = class_names[i]
        if len(label_text) > 22:
            label_text = label_text[:20] + ".."
        y_pos = top_margin + i * cell_size + (cell_size // 2) - 6
        draw.text((15, y_pos), label_text, fill=(40, 40, 40))

        # Column header index
        x_header_pos = label_margin + i * cell_size + (cell_size // 2) - 4
        draw.text((x_header_pos, top_margin - 12), str(i), fill=(100, 100, 100))

        for j in range(n_classes):
            cell_x = label_margin + j * cell_size
            cell_y = top_margin + i * cell_size
            val = int(cm[i, j])
            intensity = float(norm_cm[i, j])

            # Color gradient: white -> deep navy blue
            r = int(255 - intensity * (255 - 25))
            g = int(255 - intensity * (255 - 75))
            b = int(255 - intensity * (255 - 190))

            draw.rectangle(
                [cell_x, cell_y, cell_x + cell_size - 1, cell_y + cell_size - 1],
                fill=(r, g, b),
                outline=(210, 210, 210),
            )

            # Contrast text color
            text_col = (255, 255, 255) if intensity > 0.55 else (20, 20, 20)
            text_str = str(val)
            tw = len(text_str) * 6
            draw.text((cell_x + (cell_size - tw) // 2, cell_y + (cell_size // 2) - 6), text_str, fill=text_col)

    img.save(output_path)


class PaddyModelEvaluator:
    """Evaluates Paddy disease models and generates all required reports."""

    def __init__(self, project_root: Optional[Path] = None) -> None:
        self.project_root = project_root or Path(__file__).resolve().parent.parent
        self.reports_dir = self.project_root / "models" / "reports" / "paddy"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def load_classes(self, class_file: Path) -> List[str]:
        """Load class index mapping."""
        with class_file.open("r", encoding="utf-8") as f:
            mapping = json.load(f)
        # Sort by integer keys
        sorted_pairs = sorted([(int(k), v) for k, v in mapping.items()], key=lambda x: x[0])
        return [pair[1] for pair in sorted_pairs]

    def evaluate_model(
        self,
        model: Any,
        test_csv_path: Path,
        class_names: List[str],
        batch_size: int = 32,
    ) -> Dict[str, Any]:
        """Evaluate model against internal test split and save all artifacts.

        Args:
            model: Trained tf.keras.Model.
            test_csv_path: Path to datasets/processed/paddy/test.csv.
            class_names: List of disease class labels in index order.
            batch_size: Batch size for inference.

        Returns:
            Dictionary containing computed metrics and analysis findings.
        """
        import tensorflow as tf

        test_df = pd.read_csv(test_csv_path)
        class_to_idx = {name: i for i, name in enumerate(class_names)}
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

        print("Generating predictions on internal test set...")
        y_proba = model.predict(test_ds, verbose=1)
        y_pred = np.argmax(y_proba, axis=1)
        confidences = np.max(y_proba, axis=1)

        # 1. Overall Metrics
        acc = float(accuracy_score(y_true, y_pred))
        p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(
            y_true, y_pred, average="macro", zero_division=0
        )
        p_weighted, r_weighted, f1_weighted, _ = precision_recall_fscore_support(
            y_true, y_pred, average="weighted", zero_division=0
        )

        # 2. Confusion Matrix
        cm = confusion_matrix(y_true, y_pred)
        cm_list = cm.tolist()

        # 3. Per-class report
        clf_report_dict = classification_report(
            y_true, y_pred, target_names=class_names, output_dict=True, zero_division=0
        )
        clf_report_text = classification_report(
            y_true, y_pred, target_names=class_names, zero_division=0
        )

        # Per-class summary
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

        # Commonly confused disease pairs (top off-diagonal entries)
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

        # 4. Misclassified Images
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

        # 5. Confidence Analysis
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

        # 6. Save Reports and Visualizations
        cm_png_path = self.reports_dir / "confusion_matrix.png"
        render_confusion_matrix(cm, class_names, cm_png_path)

        report_txt_path = self.reports_dir / "classification_report.txt"
        report_txt_path.write_text(clf_report_text, encoding="utf-8")

        metrics_summary = {
            "crop": "paddy",
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

        return metrics_summary


def main() -> None:
    """CLI evaluation entry point."""
    parser = argparse.ArgumentParser(description="Evaluate Paddy disease classification model.")
    parser.add_argument("--crop", type=str, default="paddy", help="Crop name (default: paddy).")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    model_path = project_root / "models" / f"{args.crop}_model.keras"
    classes_path = project_root / "models" / f"{args.crop}_classes.json"
    test_csv_path = project_root / "datasets" / "processed" / args.crop / "test.csv"

    if not model_path.exists():
        print(f"Error: Model not found at: {model_path}. Train model first with train.py.")
        return

    import tensorflow as tf

    evaluator = PaddyModelEvaluator(project_root)
    class_names = evaluator.load_classes(classes_path)
    model = tf.keras.models.load_model(str(model_path))

    metrics = evaluator.evaluate_model(
        model=model,
        test_csv_path=test_csv_path,
        class_names=class_names,
    )
    print("\n--- Evaluation Complete ---")
    print(f"Overall Accuracy: {metrics['overall_accuracy'] * 100:.2f}%")
    print(f"Macro F1 Score:   {metrics['macro_f1']:.4f}")
    print(f"Weighted F1:      {metrics['weighted_f1']:.4f}")


if __name__ == "__main__":
    main()
