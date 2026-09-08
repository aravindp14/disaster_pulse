import boto3
from pathlib import Path

def upload_to_s3(
        local_file: str | Path,
        bucket: str,
        s3_key: str
) -> str:

    """
    Upload a local file to s3.

    Parameters
    ------------
    local_file: Path to the local file.
    bucket: S3 bucket name.
    s3_key: Destination object key.

    Returns
    ------------
    str -> S3 URI of the uploaded object
    """

    local_path = Path(local_file)

    if not local_path.exists():
        raise FileNotFoundError(
            f"Local file not found: {local_path}"
        )

    s3 = boto3.client("s3")

    s3.upload_file(
        str(local_path),
        bucket,
        s3_key
    )

    s3_uri = f"s3//{bucket}/{s3_key}"

    return s3_uri