from pathlib import Path
import fitz # PyMuPDF

EXTRACTED_TEXT_DIR = Path("backend/app/storage/extracted_text")

def extract_text_from_pdf(pdf_path: str, document_id: str) -> str:
    EXTRACTED_TEXT_DIR.mkdir(parents=True, exist_ok=True)

    pdf_file_path = Path(pdf_path)

    if not pdf_file_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    extracted_text = []

    pdf_document = fitz.open(pdf_file_path)

    for page_number in range(len(pdf_document)):
        page = pdf_document[page_number]
        text = page.get_text()
        extracted_text.append(f"\n--- Page {page_number + 1} ---\n")
        extracted_text.append(text)

    pdf_document.close()

    output_file_path = EXTRACTED_TEXT_DIR / f"{document_id}.txt"

    output_file_path.write_text(
        "\n".join(extracted_text),
        encoding="utf-8"
    )

    return str(output_file_path)
