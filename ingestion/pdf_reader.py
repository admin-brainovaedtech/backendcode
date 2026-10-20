import pymupdf
from .text_cleaner import clean_text

def extract_text_from_pdf(pdf_path):
    document = pymupdf.open(pdf_path)

    pages = []

    for page_number, page in enumerate(document, start=1):
        text = page.get_text("text")

        pages.append({
            "page_number": page_number,
            "text": text
        })

    document.close()

    return pages


if __name__ == "__main__":
    pdf_path = "documents/Class 9/Science/class9_science_motion.pdf"

    pages = extract_text_from_pdf(pdf_path)

    print(f"Total pages: {len(pages)}")

    for page in pages[:2]:
        print("\n--- PAGE", page["page_number"], "---")
        print(page["text"][:1000])