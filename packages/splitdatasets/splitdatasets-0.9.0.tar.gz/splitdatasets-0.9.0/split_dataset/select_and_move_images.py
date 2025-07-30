import shutil
import random
import argparse

from pathlib import Path
from typing import Optional, Tuple
from .utils import print_progress_bar


def select_and_move_images(source_dir: Path,
                           target_dir: Path,
                           count: int = 100,
                           prefix: Optional[str] = None,
                           extensions: Tuple[str]=(".jpg",".jpeg",".png"),
                           seed: Optional[int] = None) -> None:
    """
    Randomly selects and copies a number of image files to a new directory with optional renaming.

    Parameters
    ----------
    source_dir : Path
        Directory containing source images.
    target_dir : Path
        Directory where selected images will be copied.
    count : int, default=100
        Number of images to copy.
    prefix : str, optional
        If set, files will be renamed to prefix_0001.jpg, prefix_0002.jpg, etc.
        If not set, original filenames will be preserved.
    extensions : tuple of str, default=(".jpg", ".jpeg", ".png")
        Allowed image extensions.
    seed : int, optional
        Random seed for reproducibility.

    Raises
    ------
    ValueError
        If parameters are invalid or not enough files.
    """
    
    if not source_dir.exists() or not source_dir.is_dir():
        raise ValueError(f"Source directory {source_dir} does not exist or is not a directory.")
    if count <= 0:
        raise ValueError("Count must be a positive integer.")
    if prefix is not None and not isinstance(prefix, str):
        raise ValueError("Prefix must be a string or None.")

    if seed is not None:
        random.seed(seed)

    files = [f for f in source_dir.iterdir() if f.suffix.lower() in extensions and f.is_file()]
    if len(files) < count:
        raise ValueError(f"Not enough files in {source_dir} to select {count} images.")

    target_dir.mkdir(parents=True, exist_ok=True)
    selected = random.sample(files, count)

    print_progress_bar(0, count, prefix="Copying images: ")

    for idx, src in enumerate(selected):

        if prefix:
            new_name = f"{prefix}_{idx + 1:04d}{src.suffix.lower()}"
        else:
            new_name = src.name
        
        target_path = target_dir / new_name
        shutil.copy(src, target_path)
        
        print_progress_bar(idx + 1, count, prefix="Copying images: ")

    print()

def main():
    parser = argparse.ArgumentParser(description="Select and move images from one directory to another.")
    parser.add_argument("source_dir", type=Path, help="Source directory containing images.")
    parser.add_argument("target_dir", type=Path, help="Target directory to copy selected images.")
    parser.add_argument("--count", type=int, default=100, help="Number of images to select and copy.")
    parser.add_argument("--prefix", type=str, default=None, help="Prefix for renamed files.")
    parser.add_argument("--extensions", type=str, nargs='*', default=[".jpg", ".jpeg", ".png"], help="Allowed image extensions.")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility.")

    args = parser.parse_args()
    select_and_move_images(source_dir=args.source_dir, 
                           target_dir=args.target_dir, 
                           count=args.count, 
                           prefix=args.prefix, 
                           extensions=tuple(args.extensions), 
                           seed=args.seed)

if __name__ == "__main__":
    main()
    