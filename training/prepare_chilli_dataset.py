"""Chilli Dataset Preparation and Stratified Splitting Script.

Parses genuine original field images from:
datasets/raw/chilli/Chili Leaf Disease Original Dataset

Performs:
1. Image validation & corruption checks
2. Normalized class name mapping
3. Duplicate hash detection
4. Stratified 70% Train, 15% Validation, 15% Test split (seed=42)
5. Generates train.csv, validation.csv, test.csv in datasets/chilli/
"""

import hashlib
import json
import os
from pathlib import Path
from PIL import Image
import pandas as pd
# Imports

RAW_DIR = Path("datasets/raw/chilli/Chili Leaf Disease Original Dataset")
OUTPUT_DIR = Path("datasets/chilli")
CLASSES_MAPPING = {
    "Bacterial Spot": "bacterial_spot",
    "Cercospora Leaf Spot": "cercospora_leaf_spot",
    "Curl Virus": "curl_virus",
    "Healthy Leaf": "healthy",
    "Nutrition Deficiency": "nutrition_deficiency",
    "White spot": "white_spot",
}

def compute_file_hash(path: Path) -> str:
    hasher = hashlib.md5()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def main():
    print("=== CHILLI DATASET PREPARATION ===")
    assert RAW_DIR.exists(), f"Raw directory {RAW_DIR} not found!"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    records = []
    seen_hashes = {}
    duplicates = []
    corrupted = []

    print("\nScanning raw images...")
    for raw_folder_name, normalized_class in CLASSES_MAPPING.items():
        folder = RAW_DIR / raw_folder_name
        if not folder.exists():
            print(f"Warning: Folder {folder} does not exist!")
            continue

        valid_files = [f for f in folder.iterdir() if f.suffix.lower() in [".jpg", ".jpeg", ".png"]]
        print(f"Found {len(valid_files)} images in '{raw_folder_name}' -> '{normalized_class}'")

        for img_path in valid_files:
            try:
                with Image.open(img_path) as img:
                    w, h = img.size
                    mode = img.mode
                    if mode != "RGB":
                        img = img.convert("RGB")
            except Exception as e:
                corrupted.append((str(img_path), str(e)))
                continue

            file_hash = compute_file_hash(img_path)
            if file_hash in seen_hashes:
                duplicates.append((str(img_path), seen_hashes[file_hash]))
            else:
                seen_hashes[file_hash] = str(img_path)

            rel_path = str(img_path.as_posix())
            records.append({
                "image_path": rel_path,
                "raw_class": raw_folder_name,
                "label": normalized_class,
                "width": w,
                "height": h,
                "md5": file_hash,
            })

    print(f"\nTotal valid images scanned: {len(records)}")
    print(f"Corrupted images: {len(corrupted)}")
    print(f"Exact duplicates detected: {len(duplicates)}")

    df = pd.DataFrame(records)
    print("\nClass distribution in original dataset:")
    print(df["label"].value_counts())

    # Stratified Split: 70% Train, 15% Validation, 15% Test
    # Using deterministic random sampling per class
    train_dfs = []
    val_dfs = []
    test_dfs = []

    for label, group in df.groupby("label"):
        shuffled = group.sample(frac=1.0, random_state=42).reset_index(drop=True)
        n = len(shuffled)
        n_train = int(round(n * 0.70))
        n_val = int(round(n * 0.15))
        # Ensure at least 1 in val and test
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

    print("\nSplit counts:")
    print(f"Train:      {len(train_df)} ({len(train_df)/len(df)*100:.1f}%)")
    print(f"Validation: {len(val_df)} ({len(val_df)/len(df)*100:.1f}%)")
    print(f"Test:       {len(test_df)} ({len(test_df)/len(df)*100:.1f}%)")

    # Save CSVs
    train_df.to_csv(OUTPUT_DIR / "train.csv", index=False)
    val_df.to_csv(OUTPUT_DIR / "validation.csv", index=False)
    test_df.to_csv(OUTPUT_DIR / "test.csv", index=False)
    print(f"\nCSVs successfully written to {OUTPUT_DIR}")

    # Generate classes json
    sorted_classes = sorted(list(set(df["label"])))
    class_indices = {cls: idx for idx, cls in enumerate(sorted_classes)}
    with open("models/chilli_classes.json", "w", encoding="utf-8") as f:
        json.dump(class_indices, f, indent=2)
    print(f"Class mapping saved to models/chilli_classes.json: {class_indices}")

if __name__ == "__main__":
    main()
