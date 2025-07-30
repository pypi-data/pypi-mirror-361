import boto3
import random
import argparse
from io import BytesIO
from pathlib import Path
from typing import List, Tuple, Optional

from .utils import (print_progress_bar, 
                    normalize_ratios,
                    copy_s3_file,
                    list_s3_files)


def split_dataset_s3(bucket: str,
                     source_prefix: str,
                     target_prefix: str,
                     endpoint: str,
                     access_key: str,
                     secret_key: str,
                     labels_prefix: Optional[str] = None,
                     train_ratio: float = 0.7,
                     val_ratio: float = 0.2,
                     test_ratio: float = 0.1,
                     image_extensions: Tuple[str] = (".jpg", ".jpeg", ".png"),
                     seed: Optional[int] = None) -> None:
    
    s3 = boto3.client('s3', 
                      endpoint_url=endpoint,
                      aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key)
    
    assert abs(1 - (train_ratio + val_ratio + test_ratio)) < 1e-6, \
        "Train, validation, and test ratios must sum to 1."
    
    if seed is not None:
        random.seed(seed)

    image_keys = list_s3_files(s3, bucket, source_prefix, image_extensions)
    if not image_keys:
        raise ValueError(f"No images found in bucket {bucket} with prefix {source_prefix} and extensions {image_extensions}.")

    random.shuffle(image_keys)
    total_files = len(image_keys)
    train_end = int(total_files * train_ratio)
    val_end = train_end + int(total_files * val_ratio)

    splits = {
        'train': image_keys[:train_end],
        'val': image_keys[train_end:val_end],
        'test': image_keys[val_end:]
    }

    idx = 0
    for split_name, keys in splits.items():
        for img_key in keys:
            filename = Path(img_key).name
            image_target_key = f"{target_prefix}/images/{split_name}/{filename}"
            copy_s3_file(s3, bucket, img_key, bucket, image_target_key)
            
            if labels_prefix:
                label_key = f"{labels_prefix}/{Path(filename).with_suffix('.txt').name}"
                label_target_key = f"{target_prefix}/labels/{split_name}/{Path(label_key).name}"

                try:
                    s3.head_object(Bucket=bucket, Key=label_key)
                    copy_s3_file(s3, bucket, label_key, bucket, label_target_key)
                except s3.exceptions.ClientError:
                    print(f"[WARN] Label not found for {filename}")

            idx += 1
            print_progress_bar(idx, total_files, prefix=f"Splitting dataset")

    print()


def main():
    parser = argparse.ArgumentParser(description="Split S3 dataset into train, val, and test sets.")
    parser.add_argument('--bucket', required=True, help='S3 bucket name')
    parser.add_argument('--source_prefix', required=True, help='Source prefix in the S3 bucket')
    parser.add_argument('--target_prefix', required=True, help='Target prefix in the S3 bucket')
    parser.add_argument('--endpoint', required=True, help='S3 endpoint URL')
    parser.add_argument("--access_key", type=str, required=True, help="S3 access key")
    parser.add_argument("--secret_key", type=str, required=True, help="S3 secret key")
    parser.add_argument('--labels_prefix', default=None, help='Prefix for labels in the S3 bucket')
    parser.add_argument('--train_ratio', type=float, default=0.7, help='Proportion of the training set')
    parser.add_argument('--val_ratio', type=float, default=0.2, help='Proportion of the validation set')
    parser.add_argument('--test_ratio', type=float, default=0.1, help='Proportion of the test set')
    parser.add_argument('--seed', type=int, default=None, help='Random seed for reproducibility')

    args = parser.parse_args()
    
    train_r, val_r, test_r = normalize_ratios(args.train_ratio, args.val_ratio, args.test_ratio)

    split_dataset_s3(
        bucket=args.bucket,
        source_prefix=args.source_prefix,
        target_prefix=args.target_prefix,
        endpoint=args.endpoint,
        access_key=args.access_key,
        secret_key=args.secret_key,
        labels_prefix=args.labels_prefix,
        train_ratio=train_r,
        val_ratio=val_r,
        test_ratio=test_r,
        seed=args.seed
    )

if __name__ == "__main__":
    main()
    