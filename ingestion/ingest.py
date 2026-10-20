import json
from pathlib import Path

from ingestion.pdf_reader import extract_text_from_pdf
from ingestion.text_cleaner import clean_text
from ingestion.chunker import create_chunks
from storage.gcs_storage import (
    download_blob_to_temp,
    list_pdf_blobs
)

from config.document_mapping import DOCUMENT_MAPPING


PROJECT_ROOT = Path(__file__).resolve().parent.parent

GCS_PREFIX = "documents/class-9/science/"

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "class9_science_chunks.json"
)


def get_document_metadata(pdf_path):
    """
    Get metadata for a PDF from DOCUMENT_MAPPING.
    """

    file_name = Path(pdf_path).name

    subject_mapping = DOCUMENT_MAPPING.get(
        "class-9",
        {}
    ).get(
        "science",
        {}
    )

    return subject_mapping.get(file_name)


def ingest_all():

    pdf_files = list_pdf_blobs(GCS_PREFIX)

    print(f"Found {len(pdf_files)} PDF files")

    all_chunks = []

    for index, gcs_pdf_path in enumerate(
        pdf_files,
        start=1
    ):

        file_name = Path(gcs_pdf_path).name

        print()
        print("=" * 70)
        print(
            f"[{index}/{len(pdf_files)}] "
            f"Processing: {file_name}"
        )
        print("=" * 70)

        metadata = get_document_metadata(
            gcs_pdf_path
        )

        if not metadata:

            print(
                f"WARNING: No mapping found for "
                f"{file_name}"
            )

            print("Skipping document.")

            continue

        print(
            f"Chapter {metadata['chapter_number']}: "
            f"{metadata['chapter']}"
        )

        pdf_path = download_blob_to_temp(
            gcs_pdf_path
        )

        try:

            pages = extract_text_from_pdf(
                pdf_path
            )

            document_chunks = 0

            for page in pages:

                text = clean_text(
                    page["text"]
                )

                if not text:
                    continue

                chunks = create_chunks(
                    text
                )

                for chunk in chunks:

                    all_chunks.append({

                        "board": "CBSE",

                        "class": "9",

                        "subject": "Science",

                        "chapter_number":
                            metadata[
                                "chapter_number"
                            ],

                        "chapter":
                            metadata[
                                "chapter"
                            ],

                        "document":
                            file_name,

                        "page":
                            page[
                                "page_number"
                            ],

                        "content":
                            chunk
                    })

                    document_chunks += 1

            print(
                f"Pages processed: {len(pages)}"
            )

            print(
                f"Chunks created: "
                f"{document_chunks}"
            )

        finally:

            pdf_path.unlink(
                missing_ok=True
            )

    return all_chunks


def save_chunks(chunks):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            chunks,
            file,
            ensure_ascii=False,
            indent=2
        )

    print()
    print(
        f"Saved {len(chunks)} chunks to:"
    )

    print(OUTPUT_FILE)


if __name__ == "__main__":

    chunks = ingest_all()

    print()
    print("=" * 70)
    print("INGESTION COMPLETE")
    print("=" * 70)

    print(
        f"Total chunks: {len(chunks)}"
    )

    save_chunks(chunks)