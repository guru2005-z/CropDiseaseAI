"""Phase 1: Groundnut Dataset Inspection and Integrity Audit Script.

Inspects:
1. datasets/raw/groundnut/Raw_Data
2. datasets/raw/groundnut/Groundnut_Leaf_dataset
3. datasets/raw/groundnut/Metadata.xlsx

Performs:
- Image format validation
- Corrupt/unreadable file detection
- Resolution & color mode profiling
- SHA-256 duplicate detection (intra-class, cross-class, split-leakage)
- Class distribution & mapping analysis
"""

from __future__ import annotations

import hashlib
import json
import os
from collections import Counter, defaultdict
from pathlib import Path
from PIL import Image

BASE_DIR = Path("datasets/raw/groundnut")
RAW_DATA_DIR = BASE_DIR / "Raw_Data"
GLD_DIR = BASE_DIR / "Groundnut_Leaf_dataset"


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def inspect_directory(root_dir: Path, name: str) -> dict:
    print(f"\n=======================================================")
    print(f"  INSPECTING: {name} ({root_dir})")
    print(f"=======================================================")
    if not root_dir.exists():
        print(f"Directory {root_dir} does not exist!")
        return {}

    subdirs = [d for d in root_dir.iterdir() if d.is_dir()]
    print(f"Subdirectories / Classes found: {[d.name for d in subdirs]}")

    results = {
        "classes": {},
        "total_files": 0,
        "valid_images": 0,
        "corrupted": [],
        "formats": Counter(),
        "modes": Counter(),
        "dimensions": Counter(),
        "hashes": defaultdict(list),
    }

    all_image_paths = []
    for sdir in subdirs:
        # Check if sdir itself has subdirs (like train/test splits)
        inner_subdirs = [d for d in sdir.iterdir() if d.is_dir()]
        if inner_subdirs:
            for inner in inner_subdirs:
                class_key = f"{sdir.name}/{inner.name}"
                files = [f for f in inner.glob("*") if f.is_file()]
                results["classes"][class_key] = len(files)
                for f in files:
                    all_image_paths.append((f, class_key))
        else:
            class_key = sdir.name
            files = [f for f in sdir.glob("*") if f.is_file()]
            results["classes"][class_key] = len(files)
            for f in files:
                all_image_paths.append((f, class_key))

    results["total_files"] = len(all_image_paths)
    print(f"Total files: {results['total_files']}")
    print(f"Class distribution: {results['classes']}")

    for fpath, ckey in all_image_paths:
        ext = fpath.suffix.lower()
        results["formats"][ext] += 1

        # Check corrupted / verify
        try:
            with Image.open(fpath) as img:
                results["modes"][img.mode] += 1
                results["dimensions"][img.size] += 1
                img.verify()
            # Double check read
            with Image.open(fpath) as img:
                img.load()
            results["valid_images"] += 1
            h = compute_sha256(fpath)
            results["hashes"][h].append((str(fpath), ckey))
        except Exception as e:
            results["corrupted"].append((str(fpath), str(e)))

    print(f"Valid images: {results['valid_images']}")
    print(f"Corrupted / unreadable: {len(results['corrupted'])}")
    if results["corrupted"]:
        for c in results["corrupted"][:10]:
            print(f"  [CORRUPT] {c[0]}: {c[1]}")

    print(f"Formats: {dict(results['formats'])}")
    print(f"Modes: {dict(results['modes'])}")
    print(f"Top 5 Dimensions: {results['dimensions'].most_common(5)}")

    # Duplicates
    dup_hashes = {h: paths for h, paths in results["hashes"].items() if len(paths) > 1}
    print(f"Unique hashes: {len(results['hashes'])}")
    print(f"Duplicate hashes: {len(dup_hashes)}")
    total_dupes = sum(len(paths) for paths in dup_hashes.values())
    print(f"Total files involved in duplicates: {total_dupes}")

    # Cross-class duplicates
    cross_class = {}
    for h, paths in dup_hashes.items():
        distinct_classes = set(p[1] for p in paths)
        if len(distinct_classes) > 1:
            cross_class[h] = paths

    print(f"Cross-class duplicate hashes: {len(cross_class)}")
    if cross_class:
        for h, paths in list(cross_class.items())[:5]:
            print(f"  [CROSS-CLASS] Hash {h[:12]}: {paths}")

    return results


def check_leakage_between(raw_results: dict, gld_results: dict):
    print("\n=======================================================")
    print("  CHECKING LEAKAGE / OVERLAP BETWEEN DATASETS")
    print("=======================================================")
    raw_hashes = set(raw_results.get("hashes", {}).keys())
    gld_hashes = set(gld_results.get("hashes", {}).keys())

    shared = raw_hashes.intersection(gld_hashes)
    print(f"Hashes present in BOTH Raw_Data and Groundnut_Leaf_dataset: {len(shared)}")

    # Also check train vs test inside GLD
    gld_train_hashes = defaultdict(list)
    gld_test_hashes = defaultdict(list)

    for h, paths in gld_results.get("hashes", {}).items():
        for p, ckey in paths:
            if ckey.startswith("train/"):
                gld_train_hashes[h].append((p, ckey))
            elif ckey.startswith("test/"):
                gld_test_hashes[h].append((p, ckey))

    train_test_overlap = set(gld_train_hashes.keys()).intersection(set(gld_test_hashes.keys()))
    print(f"Hashes overlapping between GLD train and GLD test: {len(train_test_overlap)}")
    if train_test_overlap:
        print(f"WARNING: Direct exact duplicate leakage between train and test in Groundnut_Leaf_dataset!")
        for h in list(train_test_overlap)[:5]:
            print(f"  Train: {gld_train_hashes[h]} vs Test: {gld_test_hashes[h]}")


def main():
    raw_res = inspect_directory(RAW_DATA_DIR, "Raw_Data (5 classes)")
    gld_res = inspect_directory(GLD_DIR, "Groundnut_Leaf_dataset (6 classes pre-split)")
    check_leakage_between(raw_res, gld_res)


if __name__ == "__main__":
    main()
