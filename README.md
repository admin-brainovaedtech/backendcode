# Brainova RAG

Brainova RAG is a Python prototype for processing educational documents into clean, searchable text chunks. The current ingestion pipeline extracts text from the Class 9 Science `Motion` chapter PDF and stores the resulting chunks as JSON.

## Features

- Extract text from PDF documents with PyMuPDF
- Clean extracted text
- Split text into overlapping word-based chunks
- Store chunks with CBSE, class, subject, chapter, and page metadata
- Test Gemini and Supabase connectivity

## Project Structure

```text
brainova-rag/
├── app/                         # Application code (currently empty)
├── data/                        # Generated data files
├── documents/                   # Source educational documents
├── ingestion/
│   ├── chunker.py               # Text chunking
│   ├── ingest.py                # Ingestion entry point
│   ├── pdf_reader.py            # PDF text extraction
│   └── text_cleaner.py          # Text cleanup
├── test_gemini.py               # Gemini API smoke test
├── test_supabase.py             # Supabase connection smoke test
├── requirements.txt
└── .env                         # Local secrets, not committed
```

## Requirements

- Python 3.10 or newer
- A virtual environment is recommended
- Gemini and Supabase credentials for the API smoke tests

## Setup

From the `brainova-rag` directory:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install pymupdf
```

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your-gemini-api-key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-key
GOOGLE_CLOUD_BUCKET_NAME=your-gcs-bucket-name
GCS_PDF_PATH=documents/Class 9/Science/motions.pdf
```

Do not commit `.env` or API credentials.

## Run PDF Ingestion

The current pipeline downloads this object from Google Cloud Storage:

```text
documents/Class 9/Science/motions.pdf
```

Set `GCS_PDF_PATH` in `.env` when the uploaded object uses a different name.

Run it from the project root:

```powershell
python ingestion/ingest.py
```

The generated output is written to:

```text
data/motion_chunks.json
```

The script prints the total number of chunks and previews the first three chunks.

You can also run it as a package module:

```powershell
python -m ingestion.ingest
```

## Test External Services

Gemini:

```powershell
python test_gemini.py
```

Supabase:

```powershell
python test_supabase.py
```

These scripts require the corresponding values in `.env` and make live API connections.

## Notes

- Chunking currently uses 600 words per chunk with 100 words of overlap.
- Generated files belong in `data/`; source PDFs belong in `documents/`.
- The `app/` directory is reserved for the application layer as the project develops.
