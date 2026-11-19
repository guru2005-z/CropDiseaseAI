"""Dataset inspection, validation, and stratified splitting pipeline for CropDiseaseAI.

Inspects raw training and test data, performs non-destructive image validation
via Pillow and MD5 hashing, verifies data leakage across splits, and generates
metadata CSV splits alongside a comprehensive dataset_report.json.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from PIL import Image
from sklearn.model_selection import train_test_split


def inspect_train_csv(csv_path: Path) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Load and inspect train.csv for metadata, missing values, and column statistics.

    Args:
        csv_path: Path to raw train.csv.

    Returns:
        Tuple containing loaded DataFrame and dictionary of statistical findings.
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"train.csv not found at: {csv_path}")

    df = pd.read_csv(csv_path)

    total_rows = len(df)
    columns = df.columns.tolist()
    dtypes = {col: str(dtype) for col, dtype in df.dtypes.items()}
    missing_values = {col: int(df[col].isnull().sum()) for col in columns}
    duplicate_rows = int(df.duplicated().sum())

    # Class / label distribution
    label_col = "label" if "label" in df.columns else columns[1]
    class_counts = df[label_col].value_counts().to_dict()
    class_percentages = {
        cls: round((count / total_rows) * 100, 2)
        for cls, count in class_counts.items()
    }

    # Variety statistics
    variety_info: Dict[str, Any] = {}
    if "variety" in df.columns:
        variety_info = {
            "unique_varieties_count": int(df["variety"].nunique()),
            "variety_counts": {str(k): int(v) for k, v in df["variety"].value_counts().items()},
        }

    # Age statistics
    age_info: Dict[str, Any] = {}
    if "age" in df.columns:
        age_series = df["age"].dropna()
        age_info = {
            "count": int(age_series.count()),
            "min": float(age_series.min()),
            "max": float(age_series.max()),
            "mean": round(float(age_series.mean()), 2),
            "median": float(age_series.median()),
            "std": round(float(age_series.std()), 2),
            "q25": float(age_series.quantile(0.25)),
            "q75": float(age_series.quantile(0.75)),
        }

    inspection_results: Dict[str, Any] = {
        "total_rows": total_rows,
        "columns": columns,
        "data_types": dtypes,
        "missing_values": missing_values,
        "duplicate_rows": duplicate_rows,
        "unique_disease_labels": list(class_counts.keys()),
        "number_of_classes": len(class_counts),
        "class_counts": class_counts,
        "class_percentages": class_percentages,
        "variety_info": variety_info,
        "age_info": age_info,
    }

    return df, inspection_results


def verify_training_images(
    df: pd.DataFrame,
    train_img_dir: Path,
    project_root: Path,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Verify that every image referenced in train.csv exists inside train_images directory.

    Args:
        df: DataFrame loaded from train.csv.
        train_img_dir: Directory containing raw training images.
        project_root: Project root directory for computing relative paths.

    Returns:
        Updated DataFrame with 'image_path' and verification statistics dictionary.
    """
    if not train_img_dir.exists():
        raise FileNotFoundError(f"Training image directory not found: {train_img_dir}")

    # Gather all physical files in train_images
    physical_files = [f for f in train_img_dir.glob("**/*") if f.is_file()]
    physical_filename_map = {f.name: f for f in physical_files}

    missing_records: List[str] = []
    resolved_paths: List[str] = []

    label_col = "label" if "label" in df.columns else "disease"
    img_col = "image_id" if "image_id" in df.columns else "image"

    for _, row in df.iterrows():
        img_name = str(row[img_col])
        label_val = str(row[label_col])

        # Check standard hierarchical location first (train_images/<label>/<image_id>)
        standard_path = train_img_dir / label_val / img_name
        if standard_path.is_file():
            rel_path = standard_path.relative_to(project_root).as_posix()
            resolved_paths.append(rel_path)
        elif img_name in physical_filename_map:
            # Fallback to direct or alternate subdirectory location
            found_path = physical_filename_map[img_name]
            rel_path = found_path.relative_to(project_root).as_posix()
            resolved_paths.append(rel_path)
        else:
            missing_records.append(img_name)
            resolved_paths.append("")

    df_copy = df.copy()
    df_copy["image_path"] = resolved_paths

    csv_filenames = set(df[img_col].astype(str))
    unreferenced_files = [f.name for f in physical_files if f.name not in csv_filenames]

    verification_stats = {
        "csv_image_records": len(df),
        "actual_image_files": len(physical_files),
        "missing_images_count": len(missing_records),
        "missing_images_list": missing_records,
        "unreferenced_images_count": len(unreferenced_files),
        "unreferenced_images_sample": unreferenced_files[:10],
    }

    return df_copy, verification_stats


def validate_images(
    df: pd.DataFrame,
    project_root: Path,
) -> Tuple[Dict[str, Any], Dict[str, str]]:
    """Inspect every training image using Pillow and compute MD5 hashes.

    Args:
        df: DataFrame containing 'image_path' and 'image_id'.
        project_root: Project root path.

    Returns:
        Tuple containing validation statistics and a dictionary mapping image_id to MD5 hash.
    """
    corrupt_images: List[Dict[str, str]] = []
    modes: Dict[str, int] = defaultdict(int)
    formats: Dict[str, int] = defaultdict(int)
    widths: Dict[int, int] = defaultdict(int)
    heights: Dict[int, int] = defaultdict(int)
    dimensions: Dict[str, int] = defaultdict(int)
    id_to_hash: Dict[str, str] = {}

    img_col = "image_id" if "image_id" in df.columns else df.columns[0]

    for _, row in df.iterrows():
        img_id = str(row[img_col])
        rel_path = row["image_path"]

        if not rel_path:
            corrupt_images.append({"image_id": img_id, "error": "Missing file path"})
            continue

        full_path = project_root / rel_path

        # 1. Compute file hash
        try:
            with full_path.open("rb") as fp:
                file_hash = hashlib.md5(fp.read()).hexdigest()
            id_to_hash[img_id] = file_hash
        except Exception as exc:
            corrupt_images.append({"image_id": img_id, "error": f"Failed reading bytes: {exc}"})
            continue

        # 2. Inspect with Pillow
        try:
            with Image.open(full_path) as img:
                img_format = str(img.format)
                img_mode = str(img.mode)
                w, h = img.size

                formats[img_format] += 1
                modes[img_mode] += 1
                widths[w] += 1
                heights[h] += 1
                dimensions[f"{w}x{h}"] += 1
        except Exception as exc:
            corrupt_images.append({"image_id": img_id, "error": f"Corrupt image file: {exc}"})

    validation_summary = {
        "total_images_checked": len(df),
        "corrupt_images_count": len(corrupt_images),
        "corrupt_images": corrupt_images,
        "format_distribution": dict(formats),
        "mode_distribution": dict(modes),
        "dimension_distribution": dict(dimensions),
        "width_distribution": dict(widths),
        "height_distribution": dict(heights),
    }

    return validation_summary, id_to_hash


def inspect_test_data(test_dir: Path, submission_csv: Path) -> Dict[str, Any]:
    """Inspect unlabelled test images directory and sample_submission.csv.

    Args:
        test_dir: Path to test_images directory.
        submission_csv: Path to sample_submission.csv.

    Returns:
        Dictionary summarizing test dataset findings.
    """
    if not test_dir.exists():
        raise FileNotFoundError(f"Test directory not found: {test_dir}")
    if not submission_csv.exists():
        raise FileNotFoundError(f"sample_submission.csv not found: {submission_csv}")

    test_files = [f.name for f in test_dir.glob("*") if f.is_file()]
    sub_df = pd.read_csv(submission_csv)

    sub_img_col = "image_id" if "image_id" in sub_df.columns else sub_df.columns[0]
    sub_image_ids = set(sub_df[sub_img_col].astype(str))
    test_files_set = set(test_files)

    in_sub_not_files = list(sub_image_ids - test_files_set)
    in_files_not_sub = list(test_files_set - sub_image_ids)
    is_aligned = len(in_sub_not_files) == 0 and len(in_files_not_sub) == 0

    return {
        "test_images_count": len(test_files),
        "sample_submission_rows": len(sub_df),
        "sample_submission_columns": sub_df.columns.tolist(),
        "identifiers_match": is_aligned,
        "sample_submission_missing_files": len(in_sub_not_files),
        "unreferenced_test_files": len(in_files_not_sub),
        "note": "Competition test set contains no labels and remains isolated.",
    }


def create_stratified_splits(
    df: pd.DataFrame,
    target_col: str = "label",
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    random_state: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create reproducible 70% / 15% / 15% stratified splits of labeled data.

    Args:
        df: Input DataFrame with labels.
        target_col: Column name to stratify against.
        train_ratio: Proportion for train split.
        val_ratio: Proportion for validation split.
        test_ratio: Proportion for internal test split.
        random_state: Random state for deterministic reproduction.

    Returns:
        Tuple of (train_df, val_df, test_df).
    """
    if round(train_ratio + val_ratio + test_ratio, 4) != 1.0:
        raise ValueError("train_ratio + val_ratio + test_ratio must sum to 1.0")

    temp_ratio = val_ratio + test_ratio

    # Step 1: Split into train (70%) and temp (30%)
    train_df, temp_df = train_test_split(
        df,
        test_size=temp_ratio,
        random_state=random_state,
        stratify=df[target_col],
    )

    # Step 2: Split temp equally into val (15% overall) and test (15% overall)
    val_proportion_of_temp = val_ratio / temp_ratio
    val_df, test_df = train_test_split(
        temp_df,
        test_size=(1.0 - val_proportion_of_temp),
        random_state=random_state,
        stratify=temp_df[target_col],
    )

    return (
        train_df.reset_index(drop=True),
        val_df.reset_index(drop=True),
        test_df.reset_index(drop=True),
    )


def check_data_leakage(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
    id_to_hash: Dict[str, str],
    img_col: str = "image_id",
) -> Dict[str, Any]:
    """Verify zero overlap by filename and report exact duplicate hash occurrences across splits.

    Args:
        train_df: Training split DataFrame.
        val_df: Validation split DataFrame.
        test_df: Internal test split DataFrame.
        id_to_hash: Mapping of image_id to MD5 content hash.
        img_col: Filename column name.

    Returns:
        Dictionary of leakage checks and hash duplicate findings.
    """
    train_ids = set(train_df[img_col].astype(str))
    val_ids = set(val_df[img_col].astype(str))
    test_ids = set(test_df[img_col].astype(str))

    # Filename leakage check
    train_val_id_overlap = list(train_ids & val_ids)
    train_test_id_overlap = list(train_ids & test_ids)
    val_test_id_overlap = list(val_ids & test_ids)

    # Hash maps per split
    train_hash_to_ids: Dict[str, List[str]] = defaultdict(list)
    val_hash_to_ids: Dict[str, List[str]] = defaultdict(list)
    test_hash_to_ids: Dict[str, List[str]] = defaultdict(list)
    global_hash_to_ids: Dict[str, List[str]] = defaultdict(list)

    for img_id, h in id_to_hash.items():
        global_hash_to_ids[h].append(img_id)
        if img_id in train_ids:
            train_hash_to_ids[h].append(img_id)
        elif img_id in val_ids:
            val_hash_to_ids[h].append(img_id)
        elif img_id in test_ids:
            test_hash_to_ids[h].append(img_id)

    # Cross-split hash duplicates (identical images under different filenames across splits)
    train_val_hash_overlap = set(train_hash_to_ids.keys()) & set(val_hash_to_ids.keys())
    train_test_hash_overlap = set(train_hash_to_ids.keys()) & set(test_hash_to_ids.keys())
    val_test_hash_overlap = set(val_hash_to_ids.keys()) & set(test_hash_to_ids.keys())

    # Overall identical image duplicates in the dataset
    all_duplicate_hashes = {
        h: ids for h, ids in global_hash_to_ids.items() if len(ids) > 1
    }

    # Format cross-split duplicate findings
    cross_split_leakage_details: List[Dict[str, Any]] = []
    for h in (train_val_hash_overlap | train_test_hash_overlap | val_test_hash_overlap):
        cross_split_leakage_details.append(
            {
                "hash": h,
                "train_occurrences": train_hash_to_ids.get(h, []),
                "val_occurrences": val_hash_to_ids.get(h, []),
                "test_occurrences": test_hash_to_ids.get(h, []),
            }
        )

    return {
        "filename_leakage": {
            "train_val_overlap_count": len(train_val_id_overlap),
            "train_test_overlap_count": len(train_test_id_overlap),
            "val_test_overlap_count": len(val_test_id_overlap),
            "has_filename_leakage": bool(
                train_val_id_overlap or train_test_id_overlap or val_test_id_overlap
            ),
        },
        "content_hash_findings": {
            "total_unique_hashes": len(global_hash_to_ids),
            "duplicate_hashes_count": len(all_duplicate_hashes),
            "images_involved_in_duplicates": sum(len(ids) for ids in all_duplicate_hashes.values()),
            "train_val_hash_overlap_count": len(train_val_hash_overlap),
            "train_test_hash_overlap_count": len(train_test_hash_overlap),
            "val_test_hash_overlap_count": len(val_test_hash_overlap),
            "cross_split_duplicate_hashes_total": len(cross_split_leakage_details),
            "cross_split_details_sample": cross_split_leakage_details[:10],
        },
    }


def save_processed_splits(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
    output_dir: Path,
) -> Dict[str, Path]:
    """Save metadata CSV files under datasets/processed/paddy/.

    Args:
        train_df: Training split DataFrame.
        val_df: Validation split DataFrame.
        test_df: Internal test split DataFrame.
        output_dir: Output directory (datasets/processed/paddy/).

    Returns:
        Dictionary mapping split name to saved Path.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    train_path = output_dir / "train.csv"
    val_path = output_dir / "validation.csv"
    test_path = output_dir / "test.csv"

    train_df.to_csv(train_path, index=False)
    val_df.to_csv(val_path, index=False)
    test_df.to_csv(test_path, index=False)

    return {
        "train": train_path,
        "validation": val_path,
        "test": test_path,
    }


def generate_dataset_report(
    report_data: Dict[str, Any],
    output_path: Path,
) -> None:
    """Write structured JSON dataset report.

    Args:
        report_data: Dictionary containing all inspection, validation, and split data.
        output_path: Destination path for dataset_report.json.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fp:
        json.dump(report_data, fp, indent=2)


def run_pipeline(
    crop: str = "paddy",
    project_root: Optional[Path] = None,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    random_state: int = 42,
) -> Dict[str, Any]:
    """Execute end-to-end dataset inspection, validation, and splitting.

    Args:
        crop: Crop identifier (default: 'paddy').
        project_root: Project root Path.
        train_ratio: Stratified train split ratio.
        val_ratio: Stratified validation split ratio.
        test_ratio: Stratified internal test split ratio.
        random_state: Random state seed.

    Returns:
        Complete dataset report dictionary.
    """
    root = project_root or Path(__file__).resolve().parent.parent
    raw_dir = root / "datasets" / "raw" / crop
    processed_dir = root / "datasets" / "processed" / crop

    raw_train_csv = raw_dir / "train.csv"
    train_img_dir = raw_dir / "train_images"
    test_img_dir = raw_dir / "test_images"
    sample_sub_csv = raw_dir / "sample_submission.csv"

    print("=" * 80)
    print(f"CropDiseaseAI: Dataset Inspection and Validation Pipeline [{crop.upper()}]")
    print("=" * 80)

    # TASK 1: Inspect train.csv
    print("\n--- TASK 1: Inspecting train.csv ---")
    df_raw, csv_meta = inspect_train_csv(raw_train_csv)
    print(f"Total rows: {csv_meta['total_rows']}")
    print(f"Columns: {csv_meta['columns']}")
    print(f"Data types: {csv_meta['data_types']}")
    print(f"Missing values: {csv_meta['missing_values']}")
    print(f"Duplicate rows: {csv_meta['duplicate_rows']}")
    print(f"Unique disease classes ({csv_meta['number_of_classes']}): {csv_meta['unique_disease_labels']}")
    if csv_meta.get("variety_info"):
        print(f"Rice varieties count: {csv_meta['variety_info']['unique_varieties_count']}")
    if csv_meta.get("age_info"):
        print(f"Age stats: min={csv_meta['age_info']['min']}, max={csv_meta['age_info']['max']}, "
              f"mean={csv_meta['age_info']['mean']}, median={csv_meta['age_info']['median']}, std={csv_meta['age_info']['std']}")

    # TASK 2: Verify training images
    print("\n--- TASK 2: Verifying Training Images Existence ---")
    df_with_paths, img_verify_stats = verify_training_images(df_raw, train_img_dir, root)
    print(f"CSV records: {img_verify_stats['csv_image_records']}")
    print(f"Actual image files on disk: {img_verify_stats['actual_image_files']}")
    print(f"Missing images referenced by CSV: {img_verify_stats['missing_images_count']}")
    print(f"Unreferenced images on disk: {img_verify_stats['unreferenced_images_count']}")

    # TASK 3: Image validation using Pillow
    print("\n--- TASK 3: Image Validation (Pillow & Hashing) ---")
    img_val_stats, id_to_hash = validate_images(df_with_paths, root)
    print(f"Corrupt images count: {img_val_stats['corrupt_images_count']}")
    print(f"Format distribution: {img_val_stats['format_distribution']}")
    print(f"Mode distribution: {img_val_stats['mode_distribution']}")
    print(f"Dimension distribution: {img_val_stats['dimension_distribution']}")

    # TASK 4: Class distribution
    print("\n--- TASK 4: Class Distribution & Imbalance Analysis ---")
    print(f"{'Class Name':<30} | {'Count':<10} | {'Percentage':<10}")
    print("-" * 56)
    for cls_name, count in csv_meta["class_counts"].items():
        pct = csv_meta["class_percentages"][cls_name]
        print(f"{cls_name:<30} | {count:<10} | {pct:<9.2f}%")
    min_count = min(csv_meta["class_counts"].values())
    max_count = max(csv_meta["class_counts"].values())
    imbalance_ratio = round(max_count / min_count, 2)
    print(f"Class imbalance ratio (max/min): {imbalance_ratio}x "
          f"({max(csv_meta['class_counts'], key=csv_meta['class_counts'].get)} vs "
          f"{min(csv_meta['class_counts'], key=csv_meta['class_counts'].get)})")

    # TASK 5: Inspect test data
    print("\n--- TASK 5: Inspecting Unlabelled Competition Test Data ---")
    test_meta = inspect_test_data(test_img_dir, sample_sub_csv)
    print(f"Test images on disk: {test_meta['test_images_count']}")
    print(f"Sample submission rows: {test_meta['sample_submission_rows']}")
    print(f"Identifiers match perfectly: {test_meta['identifiersmatch'] if 'identifiersmatch' in test_meta else test_meta['identifiers_match']}")

    # TASK 6: Prepare stratified splits
    print("\n--- TASK 6: Creating Stratified Splits (70% / 15% / 15%) ---")
    train_df, val_df, test_df = create_stratified_splits(
        df_with_paths,
        target_col="label",
        train_ratio=train_ratio,
        val_ratio=val_ratio,
        test_ratio=test_ratio,
        random_state=random_state,
    )
    print(f"Training split count:   {len(train_df):<6} ({len(train_df)/len(df_with_paths)*100:.2f}%)")
    print(f"Validation split count: {len(val_df):<6} ({len(val_df)/len(df_with_paths)*100:.2f}%)")
    print(f"Internal test count:    {len(test_df):<6} ({len(test_df)/len(df_with_paths)*100:.2f}%)")

    # TASK 7: Check data leakage
    print("\n--- TASK 7: Data Leakage Verification ---")
    leakage_meta = check_data_leakage(train_df, val_df, test_df, id_to_hash, img_col="image_id")
    print(f"Filename leakage detected: {leakage_meta['filename_leakage']['has_filename_leakage']}")
    print(f"  Train-Val filename overlap:  {leakage_meta['filename_leakage']['train_val_overlap_count']}")
    print(f"  Train-Test filename overlap: {leakage_meta['filename_leakage']['train_test_overlap_count']}")
    print(f"  Val-Test filename overlap:   {leakage_meta['filename_leakage']['val_test_overlap_count']}")
    print(f"Image Content Hash Findings:")
    print(f"  Total unique image hashes:          {leakage_meta['content_hash_findings']['total_unique_hashes']}")
    print(f"  Duplicate hash sets in raw dataset: {leakage_meta['content_hash_findings']['duplicate_hashes_count']}")
    print(f"  Cross-split duplicate hashes:       {leakage_meta['content_hash_findings']['cross_split_duplicate_hashes_total']}")
    print(f"    Train-Val cross-split hashes:     {leakage_meta['content_hash_findings']['train_val_hash_overlap_count']}")
    print(f"    Train-Test cross-split hashes:    {leakage_meta['content_hash_findings']['train_test_hash_overlap_count']}")
    print(f"    Val-Test cross-split hashes:      {leakage_meta['content_hash_findings']['val_test_hash_overlap_count']}")

    # Save split CSVs
    print("\n--- Saving Metadata CSV Splits ---")
    saved_csvs = save_processed_splits(train_df, val_df, test_df, processed_dir)
    for split_name, path in saved_csvs.items():
        print(f"Saved {split_name} split to: {path.relative_to(root)}")

    # TASK 8: Create dataset report JSON
    report_dict: Dict[str, Any] = {
        "crop": crop,
        "total_labeled_images": csv_meta["total_rows"],
        "class_names": csv_meta["unique_disease_labels"],
        "number_of_classes": csv_meta["number_of_classes"],
        "class_counts": csv_meta["class_counts"],
        "class_percentages": csv_meta["class_percentages"],
        "class_imbalance_ratio": imbalance_ratio,
        "train_count": len(train_df),
        "validation_count": len(val_df),
        "internal_test_count": len(test_df),
        "corrupt_image_count": img_val_stats["corrupt_images_count"],
        "missing_image_count": img_verify_stats["missing_images_count"],
        "duplicate_row_count": csv_meta["duplicate_rows"],
        "duplicate_image_hash_findings": leakage_meta["content_hash_findings"],
        "filename_leakage": leakage_meta["filename_leakage"],
        "image_format_information": img_val_stats["format_distribution"],
        "image_mode_information": img_val_stats["mode_distribution"],
        "image_size_information": {
            "dimensions": img_val_stats["dimension_distribution"],
            "widths": img_val_stats["width_distribution"],
            "heights": img_val_stats["height_distribution"],
        },
        "variety_information": csv_meta.get("variety_info", {}),
        "age_statistics": csv_meta.get("age_info", {}),
        "competition_test_set_metadata": test_meta,
        "random_seed": random_state,
        "split_percentages": {
            "train": round(train_ratio * 100, 2),
            "validation": round(val_ratio * 100, 2),
            "internal_test": round(test_ratio * 100, 2),
        },
    }

    report_path = processed_dir / "dataset_report.json"
    generate_dataset_report(report_dict, report_path)
    print(f"\n--- TASK 8: Generated Dataset Report ---")
    print(f"Report saved to: {report_path.relative_to(root)}")

    print("\n" + "=" * 80)
    print("Dataset Inspection and Preparation Completed Successfully.")
    print("=" * 80)

    return report_dict


def main() -> None:
    """CLI entry point for dataset preparation and validation."""
    parser = argparse.ArgumentParser(
        description="Inspect, validate, and prepare stratified splits for crop disease datasets."
    )
    parser.add_argument(
        "--crop",
        type=str,
        default="paddy",
        help="Crop identifier (default: paddy).",
    )
    parser.add_argument(
        "--train-ratio",
        type=float,
        default=0.70,
        help="Proportion of training split (default: 0.70).",
    )
    parser.add_argument(
        "--val-ratio",
        type=float,
        default=0.15,
        help="Proportion of validation split (default: 0.15).",
    )
    parser.add_argument(
        "--test-ratio",
        type=float,
        default=0.15,
        help="Proportion of test split (default: 0.15).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible shuffling (default: 42).",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    run_pipeline(
        crop=args.crop,
        project_root=project_root,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio,
        random_state=args.seed,
    )


if __name__ == "__main__":
    main()
