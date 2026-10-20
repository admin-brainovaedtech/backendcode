from google.cloud import storage
import os
from storage.gcs_storage import download_blob_to_temp


import dotenv

dotenv.load_dotenv()
BUCKET_NAME = os.getenv("GOOGLE_CLOUD_BUCKET_NAME")

def main():

   # pdf_path = download_blob_to_temp("documents/Class-9/Science/class9_science_motion.pdf")

    
    # Create a client to interact with Google Cloud Storage
    storage_client = storage.Client()

    # Get the bucket
    bucket = storage_client.bucket(BUCKET_NAME)

    print(f"Connected to bucket: {bucket.name}")
    print("\nDocuments found:")

    # List all files in the bucket
    blobs = bucket.list_blobs()

    found_files = False

    for blob in blobs:
        found_files = True
        print(f"- {blob.name}") 

    if not found_files:
        print("No documents found in the bucket.")

if __name__ == "__main__":
    main()  

   