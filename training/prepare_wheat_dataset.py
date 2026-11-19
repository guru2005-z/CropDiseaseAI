"""Wheat Dataset Preparation and Stratified Splitting Script.

Parses field images from:
datasets/raw/wheat/

Classes:
- WheatLeafRust/.../diseased -> leaf_rust
- Ndeficient/.../deficiency -> nitrogen_deficiency
- WheatLeafRust/.../control + Ndeficient/.../control -> healthy

Performs:
1. Image validation & corruption checks
2. Normalized class consolidation
3. Duplicate hash detection & deduplication (zero data leakage)
4. Stratified 70% Train, 15% Validation, 15% Test split (seed=42)
5. Generates train.csv, validation.csv, test.csv in datasets/wheat/ and datasets/processed/wheat/
6. Generates models/wheat_classes.json
"""

import hashlib
import json
from pathlib import Path
from PIL import Image
import pandas as pd

RAW_DIR = Path("datasets/raw/wheat")
OUTPUT_DIRS = [Path("datasets/wheat"), Path("datasets/processed/wheat")]

def compute_file_hash(path: Path) -> str:
    hasher = hashlib.md5()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def main():
    print("=== WHEAT DATASET PREPARATION ===")
    assert RAW_DIR.exists(), f"Raw directory {RAW_DIR} not found!"
    for out in OUTPUT_DIRS:
        out.mkdir(parents=True, exist_ok=True)

    records = []
    seen_hashes = {}
    duplicates = []
    corrupted = []

    print("\nScanning raw wheat images...")
    valid_files = [p for p in RAW_DIR.rglob("*") if p.is_file() and p.suffix.lower() in [".jpg", ".jpeg", ".png"]]
    print(f"Total image files discovered: {len(valid_files)}")

    for img_path in valid_files:
        # Determine consolidated class from folder path
        parts = [p.lower() for p in img_path.parts]
        if "diseased" in parts:
            normalized_class = "leaf_rust"
        elif "deficiency" in parts:
            normalized_class = "nitrogen_deficiency"
        elif "control" in parts:
            normalized_class = "healthy"
        else:
            print(f"Warning: Unknown category for {img_path}")
            continue

        try:
            with Image.open(img_path) as img:
                w, h = img.size
                mode = img.mode
        except Exception as e:
            corrupted.append((str(img_path), str(e)))
            continue

        file_hash = compute_file_hash(img_path)
        if file_hash in seen_hashes:
            duplicates.append((str(img_path), seen_hashes[file_hash]))
            continue  # Deduplicate to prevent cross-split leakage
        else:
            seen_hashes[file_hash] = str(img_path)

        rel_path = str(img_path.as_posix())
        records.append({
            "image_path": rel_path,
            "raw_class": img_path.parent.name,
            "label": normalized_class,
            "width": w,
            "height": h,
            "md5": file_hash,
        })

    print(f"\nTotal valid unique images scanned: {len(records)}")
    print(f"Corrupted images: {len(corrupted)}")
    print(f"Exact duplicates omitted: {len(duplicates)}")

    df = pd.DataFrame(records)
    print("\nClass distribution in unique wheat dataset:")
    print(df["label"].value_counts())

    # Stratified Split: 70% Train, 15% Validation, 15% Test
    train_dfs = []
    val_dfs = []
    test_dfs = []

    for label, group in df.groupby("label"):
        shuffled = group.sample(frac=1.0, random_state=42).reset_index(drop=True)
        n = len(shuffled)
        n_train = int(round(n * 0.70))
        n_val = int(round(n * 0.15))
        n_train = max(1, min(n - 2, n_train))
        n_val = max(1, min(n - n_train - 1, n_val))
        n_test = n - n_train - n_val

        train_part = shuffled.iloc[:n_train].copy()
        val_part = shuffled.iloc[n_train:n_train + n_val].copy()
        test_part = shuffled.iloc[n_train + n_val:].copy()

        train_dfs.append(train_part)
        val_dfs.append(val_part)
        test_dfs.append(test_part)

    train_df = pd.concat(train_dfs).sample(frac=1.0, random_state=42).reset_index(drop=True)
    val_df = pd.concat(val_dfs).sample(frac=1.0, random_state=42).reset_index(drop=True)
    test_df = pd.concat(test_dfs).sample(frac=1.0, random_state=42).reset_index(drop=True)

    # Verify zero data leakage
    train_set = set(train_df["image_path"])
    val_set = set(val_df["image_path"])
    test_set = set(test_df["image_path"])

    assert len(train_set.intersection(val_set)) == 0, "Train-Val Leakage!"
    assert len(train_set.intersection(test_set)) == 0, "Train-Test Leakage!"
    assert len(val_set.intersection(test_set)) == 0, "Val-Test Leakage!"

    # Verify MD5 disjointness
    train_md5 = set(train_df["md5"])
    val_md5 = set(val_df["md5"])
    test_md5 = set(test_df["md5"])
    assert len(train_md5.intersection(val_md5)) == 0, "Train-Val MD5 Leakage!"
    assert len(train_md5.intersection(test_md5)) == 0, "Train-Test MD5 Leakage!"
    assert len(val_md5.intersection(test_md5)) == 0, "Val-Test MD5 Leakage!"

    print("\nSplit counts:")
    print(f"Train:      {len(train_df)} ({len(train_df)/len(df)*100:.1f}%)")
    print(f"Validation: {len(val_df)} ({len(val_df)/len(df)*100:.1f}%)")
    print(f"Test:       {len(test_df)} ({len(test_df)/len(df)*100:.1f}%)")

    # Save CSVs to both datasets/wheat and datasets/processed/wheat
    for out in OUTPUT_DIRS:
        train_df.to_csv(out / "train.csv", index=False)
        val_df.to_csv(out / "validation.csv", index=False)
        val_df.to_csv(out / "val.csv", index=False)
        test_df.to_csv(out / "test.csv", index=False)
        print(f"CSVs successfully written to {out}")

    # Generate standard integer-keyed classes json
    sorted_classes = sorted(list(set(df["label"])))
    class_indices = {str(idx): cls for idx, cls in enumerate(sorted_classes)}
    with open("models/wheat_classes.json", "w", encoding="utf-8") as f:
        json.dump(class_indices, f, indent=2)
    print(f"\nClass mapping saved to models/wheat_classes.json: {class_indices}")

if __name__ == "__main__":
    main()
