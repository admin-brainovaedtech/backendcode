from storage.gcs_storage import list_pdf_blobs, download_blob_to_temp
from ingestion.pdf_reader import extract_text_from_pdf


PREFIX = "documents/class-9/science/"


def main():

    pdf_files = list_pdf_blobs(PREFIX)

    print(f"\nFound {len(pdf_files)} PDF files\n")

    for pdf_file in pdf_files:

        print("=" * 70)
        print(pdf_file)
        print("=" * 70)

        temp_path = download_blob_to_temp(pdf_file)

        try:

            pages = extract_text_from_pdf(temp_path)

            if pages:

                first_page = pages[0]["text"]

                print(first_page[:1000])

            else:

                print("No pages found.")

        finally:

            temp_path.unlink(missing_ok=True)

        print()


if __name__ == "__main__":
    main()