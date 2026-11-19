"""Banana Dataset Preparation and Stratified Splitting Script.

Parses genuine original field images from:
datasets/raw/banana/OriginalSet

Classes:
- cordana -> cordana_leaf_spot
- healthy -> healthy
- pestalotiopsis -> pestalotiopsis_leaf_spot
- sigatoka -> sigatoka_leaf_spot

Performs:
1. Image validation & corruption checks
2. Normalized class name mapping
3. Duplicate hash detection & deduplication (zero data leakage)
4. Stratified 70% Train, 15% Validation, 15% Test split (seed=42)
5. Generates train.csv, validation.csv, test.csv in datasets/banana/ and datasets/processed/banana/
6. Generates models/banana_classes.json
"""

import hashlib
import json
from pathlib import Path
from PIL import Image
import pandas as pd

RAW_DIR = Path("datasets/raw/banana/OriginalSet")
OUTPUT_DIRS = [Path("datasets/banana"), Path("datasets/processed/banana")]
CLASSES_MAPPING = {
    "cordana": "cordana_leaf_spot",
    "healthy": "healthy",
    "pestalotiopsis": "pestalotiopsis_leaf_spot",
    "sigatoka": "sigatoka_leaf_spot",
}

def compute_file_hash(path: Path) -> str:
    hasher = hashlib.md5()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def main():
    print("=== BANANA DATASET PREPARATION ===")
    assert RAW_DIR.exists(), f"Raw directory {RAW_DIR} not found!"
    for out in OUTPUT_DIRS:
        out.mkdir(parents=True, exist_ok=True)

    records = []
    seen_hashes = {}
    duplicates = []
    corrupted = []

    print("\nScanning raw images in OriginalSet...")
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
                "raw_class": raw_folder_name,
                "label": normalized_class,
                "width": w,
                "height": h,
                "md5": file_hash,
            })

    print(f"\nTotal valid unique images scanned: {len(records)}")
    print(f"Corrupted images: {len(corrupted)}")
    print(f"Exact duplicates omitted: {len(duplicates)}")

    df = pd.DataFrame(records)
    print("\nClass distribution in unique original dataset:")
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

    # Save CSVs to both datasets/banana and datasets/processed/banana
    for out in OUTPUT_DIRS:
        train_df.to_csv(out / "train.csv", index=False)
        val_df.to_csv(out / "validation.csv", index=False)
        val_df.to_csv(out / "val.csv", index=False)
        test_df.to_csv(out / "test.csv", index=False)
        print(f"CSVs successfully written to {out}")

    # Generate standard integer-keyed classes json
    sorted_classes = sorted(list(set(df["label"])))
    class_indices = {str(idx): cls for idx, cls in enumerate(sorted_classes)}
    with open("models/banana_classes.json", "w", encoding="utf-8") as f:
        json.dump(class_indices, f, indent=2)
    print(f"\nClass mapping saved to models/banana_classes.json: {class_indices}")

if __name__ == "__main__":
    main()
