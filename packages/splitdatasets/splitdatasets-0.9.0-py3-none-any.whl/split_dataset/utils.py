import boto3
from typing import Tuple, Optional, List


def print_progress_bar(current: int, 
                       total: int, 
                       prefix: str = "Process", 
                       bar_width: int = 20) -> None:
    """
    Displays a textual progress bar in the console.

    Parameters
    ----------
    current : int
        Current progress value (e.g., current iteration or frame).
    total : int
        Total number of steps or items to complete.
    prefix : str, optional
        Text prefix displayed before the progress bar (default is "Process").
    bar_width : int, optional
        The total width (in characters) of the progress bar (default is 20).

    Raises
    ------
    TypeError
        If any parameter is of incorrect type.
    ValueError
        If current or total is negative, or total is zero.

    Example
    -------
    >>> print_progress_bar(30, 100)
    Process: [ 30%/100%] ███████--------------- [30/100]
    """
    if not isinstance(current, int) or not isinstance(total, int):
        raise TypeError("current and total must be integers.")
    if not isinstance(prefix, str):
        raise TypeError("prefix must be a string.")
    if not isinstance(bar_width, int):
        raise TypeError("bar_width must be an integer.")
    if current < 0 or total <= 0:
        raise ValueError("current must be >= 0 and total must be > 0.")
    if bar_width <= 0:
        raise ValueError("bar_width must be > 0.")

    percent = int((current / total) * 100)
    bar_filled = int(bar_width * current / total)
    bar = "█" * bar_filled + "-" * (bar_width - bar_filled)
    print(f"\r{prefix}: [{percent:>3}%/100%] {bar} [{current}/{total}]", end='', flush=True)



def normalize_ratios(train: float, val: float, test: float) -> Tuple[float, float, float]:
    """
    Normalize the provided train/val/test split ratios to ensure their sum is exactly 1.0.

    Behavior:
    ---------
    - If the sum is already close to 1.0, the original values are returned.
    - If the sum is greater than 1.0, the values are proportionally scaled down.
    - If the sum is less than 1.0, the remaining portion is added to the test ratio.

    Parameters:
    -----------
    train : float
        Proportion of the training set.
    val : float
        Proportion of the validation set.
    test : float
        Proportion of the test set.

    Returns:
    --------
    Tuple[float, float, float]
        A tuple of normalized (train, val, test) ratios whose sum is exactly 1.0.

    Raises:
    -------
    ValueError
        If the sum of all ratios is 0.
    """
    total = train + val + test
    if total == 0:
        raise ValueError("Сумма долей train/val/test не может быть 0.")
    elif abs(total - 1.0) < 1e-6:
        return train, val, test
    elif total > 1.0:
        return train / total, val / total, test / total
    else:
        remaining = 1.0 - total
        return train, val, test + remaining
    

def list_s3_files(s3,
                  bucket: str,
                  prefix: Optional[str] = None,
                  extensions: Optional[str]=(".jpg", ".jpeg", ".png")) -> List[str]:
    """Collects files from an S3 bucket with specified extensions.
    Parameters
    ----------
    s3 : boto3.client
        The S3 client.
    bucket : str
        The name of the S3 bucket.
    prefix : Optional[str], optional
        The prefix to filter files (default is None, which means no prefix).
    extensions : Optional[Tuple[str]], optional
        A tuple of file extensions to filter files (default is (".jpg", ".jpeg", ".png")). 
    Returns
    -------
    List[str]
        A list of file keys that match the specified extensions.
    """
    paginator = s3.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix)
    files = []
    for page in page_iterator:
        if 'Contents' in page:
            for obj in page.get('Contents', []):
                key = obj['Key']
                if any(key.endswith(ext) for ext in extensions):
                    files.append(key)
    return files


def copy_s3_file(s3, 
                 source_bucket: str, 
                 source_key: str, 
                 dest_bucket: str, 
                 dest_key: str) -> None:
    """
    Copies a file from one S3 bucket to another.

    Parameters
    ----------
    s3 : boto3.client
        The S3 client.
    source_bucket : str
        The name of the source bucket.
    source_key : str
        The key of the file in the source bucket.
    dest_bucket : str
        The name of the destination bucket.
    dest_key : str
        The key for the copied file in the destination bucket.
    """
    copy_source = {'Bucket': source_bucket, 'Key': source_key}
    s3.copy_object(CopySource=copy_source, Bucket=dest_bucket, Key=dest_key)
