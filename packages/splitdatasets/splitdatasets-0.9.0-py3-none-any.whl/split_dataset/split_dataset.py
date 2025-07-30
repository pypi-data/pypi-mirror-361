import shutil
import random
import argparse
from pathlib import Path
from typing import Optional, Tuple
from .utils import print_progress_bar, normalize_ratios


def split_dataset(source_dir: str,
                  target_dir: str,
                  labels_dir: Optional[str] = None,
                  train_ratio: float = 0.7,
                  val_ratio: float = 0.2,
                  test_ratio: float = 0.1,
                  image_extensions: Tuple[str] = (".jpg", ".jpeg", ".png"),
                  seed: Optional[int] = None) -> None:
    """
    Splits a dataset of images into training, validation, and test subsets, 
    optionally copying corresponding label files.

    Parameters
    ----------
    source_dir : str
        Path to the directory containing the image files.
    target_dir : str
        Path to the target base directory where train/val/test folders will be created.
    labels_dir : str, optional
        Path to the directory containing label files (with filenames matching the images).
        If not provided, only image files will be copied.
    train_ratio : float
        Proportion of the dataset to include in the training set (default: 0.7).
    val_ratio : float
        Proportion of the dataset to include in the validation set (default: 0.2).
    test_ratio : float
        Proportion of the dataset to include in the test set (default: 0.1).
    image_extensions : tuple
        Allowed image file extensions to include in the dataset.
    seed : int, optional
        Random seed value for reproducibility. If not set, a random shuffle will be used.
    """


    assert abs(1 - (train_ratio + val_ratio + test_ratio)) < 1e-6, \
        "Train, validation, and test ratios must sum to 1."
    
    if seed is not None:
        random.seed(seed)

    source_dir = Path(source_dir)
    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    if labels_dir:
        labels_dir = Path(labels_dir)
        assert labels_dir.is_dir(), f"Labels directory {labels_dir} does not exist."

    image_files = [f for f in source_dir.iterdir() if f.suffix.lower() in image_extensions]
    if not image_files:
        raise ValueError(f"No images found in {source_dir} with extensions {image_extensions}.")
    
    random.shuffle(image_files)
    total_files = len(image_files)

    train_end = int(total_files * train_ratio)
    val_end = train_end + int(total_files * val_ratio)

    splits = {
        'train': image_files[:train_end],
        'val': image_files[train_end:val_end],
        'test': image_files[val_end:]
    }

    idx = 0
    for split_name, files in splits.items():
        img_dir = target_dir / 'images' / split_name
        img_dir.mkdir(parents=True, exist_ok=True)

        if labels_dir:
            label_dir = target_dir / 'labels' / split_name
            label_dir.mkdir(parents=True, exist_ok=True)

        for file in files:
            shutil.copy(file, img_dir / file.name)
            
            if labels_dir:
                label_file = labels_dir / file.with_suffix('.txt').name
                if label_file.exists():
                    shutil.copy(label_file, label_dir / label_file.name)
                else:
                    print(f"[WARN] Label file {label_file} does not exist for image {file.name}.")
            
            idx += 1
            print_progress_bar(idx, total_files, f"Splitting dataset")
    
    print()


def main():
    parser = argparse.ArgumentParser(description="Split dataset into train, val, and test sets.")
    parser.add_argument("source_dir", type=str, help="Source directory containing images.")
    parser.add_argument("target_dir", type=str, help="Target directory for the split dataset.")
    parser.add_argument("--labels_dir", type=str, default=None, help="Directory containing labels (optional).")
    parser.add_argument("--train_ratio", type=float, default=0.7, help="Ratio of training data.")
    parser.add_argument("--val_ratio", type=float, default=0.2, help="Ratio of validation data.")
    parser.add_argument("--test_ratio", type=float, default=0.1, help="Ratio of testing data.")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility.")

    args = parser.parse_args()
    
    train_r, val_r, test_r = normalize_ratios(args.train_ratio, args.val_ratio, args.test_ratio)

    split_dataset(
        source_dir=args.source_dir,
        target_dir=args.target_dir,
        labels_dir=args.labels_dir,
        train_ratio=train_r,
        val_ratio=val_r,
        test_ratio=test_r,
        seed=args.seed
    )
            

if __name__ == "__main__":
    main()
    