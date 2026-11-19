"""Maize dataset preparation, duplicate quarantine, and stratified splitting pipeline.

Excludes cross-class duplicate images, performs reproducible stratified splitting,
prevents cross-split data leakage, and outputs metadata CSVs and audit reports.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd
from PIL import Image
from sklearn.model_selection import train_test_split


CLASS_MAPPING: Dict[str, str] = {
    "Blight": "northern_leaf_blight",
    "Common_Rust": "common_rust",
    "Gray_Leaf_Spot": "gray_leaf_spot",
    "Healthy": "healthy",
}

LABEL_PROVENANCE: Dict[str, Dict[str, str]] = {
    "northern_leaf_blight": {
        "raw_folder": "Blight",
        "scientific_name": "Exserohilum turcicum (syn. Helminthosporium turcicum)",
        "provenance": "PlantVillage Corn benchmark dataset / Kaggle Corn Leaf Infection",
        "evidence": (
            "Filename pattern 'Corn_Blight (x).jpg' corresponds to PlantVillage "
            "'Corn_(Maize)___Northern_Leaf_Blight'. Foliar lesions display large, elongated, "
            "cigar-shaped elliptical necrotic patches characteristic of NCLB."
        ),
        "uncertainty_note": (
            "Raw folder name is abbreviated to 'Blight'. While visual features and dataset "
            "provenance confirm Northern Corn Leaf Blight, advisory documentation will also note "
            "related foliar blights (e.g. Bipolaris maydis / Southern Blight) for field safety."
        ),
    },
    "common_rust": {
        "raw_folder": "Common_Rust",
        "scientific_name": "Puccinia sorghi",
        "provenance": "PlantVillage Corn benchmark dataset",
        "evidence": "Distinct reddish-brown to dark-brown pustules on upper and lower leaf surfaces.",
        "uncertainty_note": "Unambiguous label matching standard plant pathology classifications.",
    },
    "gray_leaf_spot": {
        "raw_folder": "Gray_Leaf_Spot",
        "scientific_name": "Cercospora zeae-maydis",
        "provenance": "PlantVillage Corn benchmark dataset",
        "evidence": "Classic rectangular, vein-delimited necrotic tan/gray lesions.",
        "uncertainty_note": "Unambiguous label matching standard plant pathology classifications.",
    },
    "healthy": {
        "raw_folder": "Healthy",
        "scientific_name": "Zea mays (Healthy)",
        "provenance": "PlantVillage Corn benchmark dataset",
        "evidence": "Uniform green leaf tissue free of chlorotic or necrotic lesions.",
        "uncertainty_note": "Unambiguous label representing normal physiological maize vegetative health.",
    },
}


def compute_sha256(file_path: Path) -> str:
    """Compute SHA-256 hash of a file."""
    hasher = hashlib.sha256()
    with file_path.open("rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def scan_raw_dataset(raw_dir: Path) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Scan raw images, compute hashes, verify readability, and collect metadata."""
    records: List[Dict[str, Any]] = []
    corrupted_files: List[Dict[str, str]] = []
    format_counts: Dict[str, int] = defaultdict(int)
    mode_counts: Dict[str, int] = defaultdict(int)
    dim_counts: Dict[str, int] = defaultdict(int)

    for folder_name, class_id in CLASS_MAPPING.items():
        class_folder = raw_dir / folder_name
        if not class_folder.is_dir():
            raise FileNotFoundError(f"Expected class folder not found: {class_folder}")

        for entry in class_folder.iterdir():
            if not entry.is_file():
                continue

            ext = entry.suffix.lower()
            format_counts[ext] += 1

            # Readability check and hash calculation
            try:
                sha256 = compute_sha256(entry)
                with Image.open(entry) as img:
                    img.verify()
                with Image.open(entry) as img:
                    w, h = img.size
                    mode = img.mode
                    mode_counts[mode] += 1
                    dim_counts[f"{w}x{h}"] += 1

                records.append({
                    "image_id": entry.name,
                    "raw_folder": folder_name,
                    "label": class_id,
                    "sha256": sha256,
                    "width": w,
                    "height": h,
                    "mode": mode,
                    "abs_path": entry.resolve(),
                })
            except Exception as exc:
                corrupted_files.append({
                    "file": str(entry),
                    "error": str(exc),
                })

    scan_summary = {
        "total_files_scanned": len(records) + len(corrupted_files),
        "valid_files_count": len(records),
        "corrupted_files_count": len(corrupted_files),
        "corrupted_files": corrupted_files,
        "format_distribution": dict(format_counts),
        "mode_distribution": dict(mode_counts),
        "top_resolutions": sorted(dim_counts.items(), key=lambda x: x[1], reverse=True)[:5],
    }

    return records, scan_summary


def detect_and_quarantine_duplicates(
    records: List[Dict[str, Any]],
    project_root: Path,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Identify cross-class duplicates and isolate them from the dataset pool."""
    hash_to_records: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for rec in records:
        hash_to_records[rec["sha256"]].append(rec)

    cross_class_dupes: List[Dict[str, Any]] = []
    intra_class_dupes: List[Dict[str, Any]] = []
    excluded_hashes: set[str] = set()

    for sha, recs in hash_to_records.items():
        if len(recs) > 1:
            classes = set(r["label"] for r in recs)
            if len(classes) > 1:
                # Contradictory labels: MUST quarantine all instances
                excluded_hashes.add(sha)
                cross_class_dupes.append({
                    "sha256": sha,
                    "conflicting_classes": list(classes),
                    "affected_files": [
                        {
                            "image_id": r["image_id"],
                            "raw_folder": r["raw_folder"],
                            "assigned_label": r["label"],
                            "relative_path": str(r["abs_path"].relative_to(project_root)).replace("\\", "/"),
                        }
                        for r in recs
                    ],
                    "exclusion_reason": (
                        "Exact bitwise duplicate image assigned to conflicting classes "
                        f"({', '.join(classes)}). Quarantined to prevent ground-truth contamination."
                    ),
                })
            else:
                intra_class_dupes.append({
                    "sha256": sha,
                    "class": list(classes)[0],
                    "file_count": len(recs),
                    "files": [r["image_id"] for r in recs],
                })

    # Filter out quarantined records
    clean_records: List[Dict[str, Any]] = []
    quarantined_records: List[Dict[str, Any]] = []

    for rec in records:
        if rec["sha256"] in excluded_hashes:
            quarantined_records.append(rec)
        else:
            clean_records.append(rec)

    manifest = {
        "quarantine_policy": "EXCLUDE_CROSS_CLASS_DUPLICATES",
        "quarantine_timestamp": datetime.now(timezone.utc).isoformat(),
        "total_quarantined_images": len(quarantined_records),
        "total_quarantined_unique_hashes": len(excluded_hashes),
        "quarantine_details": cross_class_dupes,
        "intra_class_duplicates": intra_class_dupes,
    }

    return clean_records, manifest


def create_stratified_splits(
    records: List[Dict[str, Any]],
    seed: int = 42,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Create reproducible stratified train, validation, and test partitions."""
    assert abs((train_ratio + val_ratio + test_ratio) - 1.0) < 1e-6, "Split ratios must sum to 1.0"

    df = pd.DataFrame(records)

    # First split: train vs (val + test)
    val_plus_test_ratio = val_ratio + test_ratio
    train_df, val_test_df = train_test_split(
        df,
        test_size=val_plus_test_ratio,
        stratify=df["label"],
        random_state=seed,
    )

    # Second split: val vs test (50/50 of the remaining 30%)
    relative_test_ratio = test_ratio / val_plus_test_ratio
    val_df, test_df = train_test_split(
        val_test_df,
        test_size=relative_test_ratio,
        stratify=val_test_df["label"],
        random_state=seed,
    )

    train_records = train_df.to_dict(orient="records")
    val_records = val_df.to_dict(orient="records")
    test_records = test_df.to_dict(orient="records")

    return train_records, val_records, test_records


def verify_zero_leakage(
    train: List[Dict[str, Any]],
    val: List[Dict[str, Any]],
    test: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Verify strictly zero SHA-256 hash overlap across train, val, and test splits."""
    train_hashes = set(r["sha256"] for r in train)
    val_hashes = set(r["sha256"] for r in val)
    test_hashes = set(r["sha256"] for r in test)

    train_val_overlap = train_hashes.intersection(val_hashes)
    train_test_overlap = train_hashes.intersection(test_hashes)
    val_test_overlap = val_hashes.intersection(test_hashes)

    zero_leakage = (
        len(train_val_overlap) == 0
        and len(train_test_overlap) == 0
        and len(val_test_overlap) == 0
    )

    return {
        "zero_leakage_verified": zero_leakage,
        "train_val_hash_overlap_count": len(train_val_overlap),
        "train_test_hash_overlap_count": len(train_test_overlap),
        "val_test_hash_overlap_count": len(val_test_overlap),
    }


def save_split_csv(
    records: List[Dict[str, Any]],
    output_csv: Path,
    project_root: Path,
) -> None:
    """Format and save split DataFrame with relative image paths."""
    formatted = []
    for r in records:
        rel_path = str(r["abs_path"].relative_to(project_root)).replace("\\", "/")
        formatted.append({
            "image_id": r["image_id"],
            "label": r["label"],
            "raw_class": r["raw_folder"],
            "sha256": r["sha256"],
            "image_path": rel_path,
        })
    df = pd.DataFrame(formatted)
    df.sort_values(by=["label", "image_id"], inplace=True)
    df.to_csv(output_csv, index=False)


def prepare_maize_dataset(
    project_root: Path,
    seed: int = 42,
) -> Dict[str, Any]:
    """Main pipeline to prepare, quarantine, split, and generate Maize artifacts."""
    raw_dir = project_root / "datasets" / "raw" / "maize"
    output_dir = project_root / "datasets" / "processed" / "maize"

    if not raw_dir.is_dir():
        raise FileNotFoundError(f"Raw maize directory does not exist: {raw_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("CropDiseaseAI: Phase 2 Maize Dataset Preparation Pipeline")
    print("=" * 70)
    print(f"Project root: {project_root}")
    print(f"Raw dataset:  {raw_dir}")
    print(f"Output dir:   {output_dir}")

    # 1. Scan and compute hashes
    print("\n[Step 1/5] Scanning raw images and verifying file integrity...")
    records, scan_summary = scan_raw_dataset(raw_dir)
    print(f"  Total files scanned: {scan_summary['total_files_scanned']}")
    print(f"  Valid files:         {scan_summary['valid_files_count']}")
    print(f"  Corrupted files:     {scan_summary['corrupted_files_count']}")

    # 2. Detect & quarantine cross-class duplicates
    print("\n[Step 2/5] Detecting and quarantining cross-class duplicates...")
    clean_records, exclusion_manifest = detect_and_quarantine_duplicates(records, project_root)
    print(f"  Quarantined files:   {exclusion_manifest['total_quarantined_images']}")
    print(f"  Clean images pool:   {len(clean_records)}")

    # 3. Stratified splitting
    print("\n[Step 3/5] Performing stratified splitting (70% train / 15% val / 15% test)...")
    train_records, val_records, test_records = create_stratified_splits(clean_records, seed=seed)
    print(f"  Train split count:   {len(train_records)} ({len(train_records)/len(clean_records)*100:.2f}%)")
    print(f"  Val split count:     {len(val_records)} ({len(val_records)/len(clean_records)*100:.2f}%)")
    print(f"  Test split count:    {len(test_records)} ({len(test_records)/len(clean_records)*100:.2f}%)")

    # 4. Verify zero cross-split leakage
    print("\n[Step 4/5] Auditing cross-split hash leakage...")
    leakage_audit = verify_zero_leakage(train_records, val_records, test_records)
    print(f"  Zero leakage confirmed: {leakage_audit['zero_leakage_verified']}")
    assert leakage_audit["zero_leakage_verified"], "Cross-split leakage detected!"

    # 5. Save artifacts
    print("\n[Step 5/5] Generating dataset artifacts and metadata...")
    train_csv = output_dir / "train.csv"
    val_csv = output_dir / "validation.csv"
    test_csv = output_dir / "test.csv"
    report_json = output_dir / "dataset_report.json"
    manifest_json = output_dir / "exclusion_manifest.json"

    save_split_csv(train_records, train_csv, project_root)
    save_split_csv(val_records, val_csv, project_root)
    save_split_csv(test_records, test_csv, project_root)

    with manifest_json.open("w", encoding="utf-8") as f:
        json.dump(exclusion_manifest, f, indent=2)

    # Class distribution statistics
    def get_class_counts(recs: List[Dict[str, Any]]) -> Dict[str, int]:
        counts: Dict[str, int] = defaultdict(int)
        for r in recs:
            counts[r["label"]] += 1
        return dict(counts)

    overall_clean_counts = get_class_counts(clean_records)
    train_counts = get_class_counts(train_records)
    val_counts = get_class_counts(val_records)
    test_counts = get_class_counts(test_records)

    per_class_summary = {}
    for cls_name, total_cnt in sorted(overall_clean_counts.items()):
        per_class_summary[cls_name] = {
            "clean_total": total_cnt,
            "train": train_counts.get(cls_name, 0),
            "val": val_counts.get(cls_name, 0),
            "test": test_counts.get(cls_name, 0),
            "pct_of_dataset": round(total_cnt / len(clean_records) * 100, 2),
        }

    dataset_report = {
        "crop": "maize",
        "scientific_name": "Zea mays",
        "preparation_timestamp": datetime.now(timezone.utc).isoformat(),
        "random_seed": seed,
        "raw_dataset_source": str(raw_dir.relative_to(project_root)).replace("\\", "/"),
        "total_original_images": scan_summary["total_files_scanned"],
        "valid_images_scanned": scan_summary["valid_files_count"],
        "corrupted_images_count": scan_summary["corrupted_files_count"],
        "quarantined_images_count": exclusion_manifest["total_quarantined_images"],
        "clean_dataset_size": len(clean_records),
        "split_policy": "stratified_random_split_with_duplicate_quarantine",
        "split_ratios": {
            "train": 0.70,
            "validation": 0.15,
            "test": 0.15,
        },
        "split_counts": {
            "train": len(train_records),
            "validation": len(val_records),
            "test": len(test_records),
            "total": len(clean_records),
        },
        "leakage_audit": leakage_audit,
        "per_class_distribution": per_class_summary,
        "class_mapping_and_provenance": LABEL_PROVENANCE,
        "format_distribution": scan_summary["format_distribution"],
        "color_mode_distribution": scan_summary["mode_distribution"],
        "top_resolutions": scan_summary["top_resolutions"],
        "artifacts_generated": {
            "train_csv": str(train_csv.relative_to(project_root)).replace("\\", "/"),
            "validation_csv": str(val_csv.relative_to(project_root)).replace("\\", "/"),
            "test_csv": str(test_csv.relative_to(project_root)).replace("\\", "/"),
            "dataset_report_json": str(report_json.relative_to(project_root)).replace("\\", "/"),
            "exclusion_manifest_json": str(manifest_json.relative_to(project_root)).replace("\\", "/"),
        },
    }

    with report_json.open("w", encoding="utf-8") as f:
        json.dump(dataset_report, f, indent=2)

    print(f"  Artifacts written to: {output_dir.relative_to(project_root)}")
    print("=" * 70)
    print("Phase 2 Dataset Preparation Complete: ALL CHECKS PASSED.")
    print("=" * 70)

    return dataset_report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare Maize dataset splits.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility.")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    prepare_maize_dataset(root, seed=args.seed)

