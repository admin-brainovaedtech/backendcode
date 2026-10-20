from storage.gcs_storage import list_pdf_blobs


def main():

    prefix = "documents/class-9/science/"

    pdf_files = list_pdf_blobs(prefix)

    print("\nPDF files found:")
    print("----------------")

    for pdf in pdf_files:
        print(pdf)

    print(f"\nTotal PDFs: {len(pdf_files)}")


if __name__ == "__main__":
    main()