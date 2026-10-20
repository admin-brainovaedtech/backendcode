import tempfile
import os

from google.cloud import storage
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


BUCKET_NAME = os.getenv("GOOGLE_CLOUD_BUCKET_NAME")
print(f"Using bucket: {BUCKET_NAME}")


def download_blob_to_temp(blob_name: str) -> Path:
    """
    Downloads a file from Google Cloud Storage
    to a temporary local PDF file.
    """

    client = storage.Client()
    print(f"BlobName: {blob_name}")
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name)

    if not blob.exists():
        raise FileNotFoundError(
            f"File not found in bucket: {blob_name}"
        )

    suffix = Path(blob_name).suffix

    temp_file = tempfile.NamedTemporaryFile(
        suffix=suffix,
        delete=False
    )

    temp_path = Path(temp_file.name)

    temp_file.close()

    blob.download_to_filename(temp_path)

    print(f"Downloaded from Cloud Storage: {blob_name}")
    print(f"Temporary file: {temp_path}")

    return temp_path

def list_pdf_blobs(prefix: str):
    """
    Returns all PDF objects under the specified
    Cloud Storage prefix.
    """

    client = storage.Client()

    bucket = client.bucket(BUCKET_NAME)

    blobs = bucket.list_blobs(prefix=prefix)

    pdf_files = []

    for blob in blobs:

        if blob.name.lower().endswith(".pdf"):

            pdf_files.append(blob.name)

    return pdf_files