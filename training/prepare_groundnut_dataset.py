"""Groundnut dataset preparation, duplicate quarantine, and stratified splitting pipeline.

Processes unaugmented raw field images from datasets/raw/groundnut/Raw_Data,
performs non-destructive image verification, calculates SHA-256 hashes,
creates stratified train/val/test partitions (70/15/15), guarantees zero
cross-split data leakage, and outputs metadata CSVs and audit reports.
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
    "early_leaf_spot": "early_leaf_spot",
    "healthy leaf": "healthy",
    "late leaf spot": "late_leaf_spot",
    "nutrition deficiency": "nutrition_deficiency",
    "rust": "rust",
}

LABEL_PROVENANCE: Dict[str, Dict[str, str]] = {
    "early_leaf_spot": {
        "raw_folder": "early_leaf_spot",
        "scientific_name": "Cercospora arachidicola (syn. Mycosphaerella arachidis)",
        "provenance": "Mendeley Data (DOI: 10.17632/22p2vcbxfk.3) / Data in Brief (2023) - Koppal, Karnataka",
        "evidence": (
            "Digital photographs captured in natural groundnut fields with assistance of plant pathologists. "
            "Characterized by circular to subcircular reddish-brown lesions surrounded by prominent yellow chlorotic halos."
        ),
        "uncertainty_note": "Standard plant pathology classification for Cercospora arachidicola on Arachis hypogaea.",
    },
    "healthy": {
        "raw_folder": "healthy leaf",
        "scientific_name": "Arachis hypogaea (Healthy)",
        "provenance": "Mendeley Data (DOI: 10.17632/22p2vcbxfk.3) / Data in Brief (2023) - Koppal, Karnataka",
        "evidence": "Uniform green vegetative foliage free of foliar pathogens, spot necrotic lesions, or rust pustules.",
        "uncertainty_note": "Unambiguous label representing normal physiological groundnut vegetative health.",
    },
    "late_leaf_spot": {
        "raw_folder": "late leaf spot",
        "scientific_name": "Phaeoisariopsis personata (syn. Cercosporidium personatum / Mycosphaerella berkeleyi)",
        "provenance": "Mendeley Data (DOI: 10.17632/22p2vcbxfk.3) / Data in Brief (2023) - Koppal, Karnataka",
        "evidence": (
            "Dark brown to black subcircular lesions on lower leaf surfaces, typically lacking or with narrow chlorotic halos, "
            "bearing conspicuous carbonaceous conidial fruiting cushions."
        ),
        "uncertainty_note": "Distinguished from early leaf spot by darker carbonaceous appearance and primary abaxial sporulation.",
    },
    "nutrition_deficiency": {
        "raw_folder": "nutrition deficiency",
        "scientific_name": "Abiotic Nutrient Deficiency (Arachis hypogaea)",
        "provenance": "Mendeley Data (DOI: 10.17632/22p2vcbxfk.3) / Data in Brief (2023) - Koppal, Karnataka",
        "evidence": "Interveinal chlorosis, generalized leaflet yellowing, or nutrient imbalance without fungal spore bodies.",
        "uncertainty_note": "Physiological disorder; not an infectious pathogen.",
    },
    "rust": {
        "raw_folder": "rust",
        "scientific_name": "Puccinia arachidis",
        "provenance": "Mendeley Data (DOI: 10.17632/22p2vcbxfk.3) / Data in Brief (2023) - Koppal, Karnataka",
        "evidence": "Prominent cinnamon-brown to orange-brown pustules (uredinia) rupturing abaxial epidermal leaf surfaces.",
        "uncertainty_note": "Unambiguous obligate biotrophic rust pathogen of peanut foliage.",
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


def prepare_groundnut_dataset(
    project_root: Path,
    seed: int = 42,
) -> Dict[str, Any]:
    """Main pipeline to prepare, quarantine, split, and generate Groundnut artifacts."""
    raw_dir = project_root / "datasets" / "raw" / "groundnut" / "Raw_Data"
    output_dir = project_root / "datasets" / "processed" / "groundnut"

    if not raw_dir.is_dir():
        raise FileNotFoundError(f"Raw groundnut directory does not exist: {raw_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("CropDiseaseAI: Phase 2 Groundnut Dataset Preparation Pipeline")
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
    print(f"  Clean records pool:   {len(clean_records)}")
    print(f"  Quarantined instances: {exclusion_manifest['total_quarantined_images']}")

    # 3. Create stratified splits (70/15/15)
    print("\n[Step 3/5] Partitioning into stratified splits (Train 70%, Val 15%, Test 15%)...")
    train_recs, val_recs, test_recs = create_stratified_splits(clean_records, seed=seed)
    print(f"  Train set:      {len(train_recs)} images")
    print(f"  Validation set: {len(val_recs)} images")
    print(f"  Test set:       {len(test_recs)} images")

    # 4. Strict leakage verification
    print("\n[Step 4/5] Verifying zero cross-split data leakage...")
    leakage_audit = verify_zero_leakage(train_recs, val_recs, test_recs)
    print(f"  Zero leakage confirmed: {leakage_audit['zero_leakage_verified']}")
    if not leakage_audit["zero_leakage_verified"]:
        raise RuntimeError(f"FATAL: Cross-split data leakage detected! {leakage_audit}")

    # 5. Save outputs
    print("\n[Step 5/5] Generating metadata CSVs, audit manifest, and summary reports...")
    save_split_csv(train_recs, output_dir / "train.csv", project_root)
    save_split_csv(val_recs, output_dir / "validation.csv", project_root)
    save_split_csv(test_recs, output_dir / "test.csv", project_root)

    # Save duplicate manifest
    with (output_dir / "duplicate_manifest.json").open("w", encoding="utf-8") as f:
        json.dump(exclusion_manifest, f, indent=2)

    # Calculate class distribution per split
    def get_counts(recs: List[Dict[str, Any]]) -> Dict[str, int]:
        c = Counter(r["label"] for r in recs)
        return dict(sorted(c.items()))

    final_report = {
        "crop": "groundnut",
        "dataset_name": "Dataset of groundnut plant leaf images for classification and detection",
        "source_reference": "Data in Brief, Vol 48, 2023, 109185 (Mendeley Data DOI: 10.17632/22p2vcbxfk.3)",
        "preparation_timestamp": datetime.now(timezone.utc).isoformat(),
        "random_seed": seed,
        "split_ratios": {"train": 0.70, "validation": 0.15, "test": 0.15},
        "classes": sorted(list(CLASS_MAPPING.values())),
        "class_mapping": CLASS_MAPPING,
        "label_provenance": LABEL_PROVENANCE,
        "scan_summary": scan_summary,
        "quarantine_summary": {
            "total_quarantined": exclusion_manifest["total_quarantined_images"],
            "cross_class_duplicate_hashes": len(exclusion_manifest["quarantine_details"]),
            "intra_class_duplicate_hashes": len(exclusion_manifest["intra_class_duplicates"]),
        },
        "split_counts": {
            "train": len(train_recs),
            "validation": len(val_recs),
            "test": len(test_recs),
            "total_clean": len(clean_records),
        },
        "class_distribution_per_split": {
            "train": get_counts(train_recs),
            "validation": get_counts(val_recs),
            "test": get_counts(test_recs),
            "total": get_counts(clean_records),
        },
        "leakage_audit": leakage_audit,
    }

    with (output_dir / "dataset_report.json").open("w", encoding="utf-8") as f:
        json.dump(final_report, f, indent=2)

    print("\nDataset preparation completed successfully!")
    print(f"Artifacts saved in {output_dir}/")
    return final_report


if __name__ == "__main__":
    from collections import Counter
    parser = argparse.ArgumentParser(description="Prepare Groundnut Dataset for CropDiseaseAI")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible stratified splitting")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    prepare_groundnut_dataset(project_root, seed=args.seed)
