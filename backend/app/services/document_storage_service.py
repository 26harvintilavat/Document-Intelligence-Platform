import json
import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile

from app.core.config import settings
from app.schemas.document import DocumentMetadata

PDF_CONTENT_TYPES = {
    "application/pdf", 
    "application/x-pdf",
    "application/octet-stream",
}

def ensure_storage_ready() -> None:
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.document_index_path.parent.mkdir(parents=True, exist_ok=True)

    if not settings.document_index_path.exists():
        settings.document_index_path.write_text("[]", encoding="utf-8")

def sanitize_filename(filename: str) -> str:
    filename_only = Path(filename).name
    return re.sub(r"[^a-zA-Z0-9_.-]", "_", filename_only)

def load_document_index() -> list[DocumentMetadata]:
    ensure_storage_ready()

    raw_data = settings.document_index_path.read_text(encoding="utf-8")

    if not raw_data.strip():
        return []
    
    documents = json.loads(raw_data)
    return [DocumentMetadata.model_validate(document) for document in documents]

def save_document_index(documents: list[DocumentMetadata]) -> None:
    ensure_storage_ready()

    serialized_documents = [
        document.model_dump(mode="json") for document in documents
    ]

    settings.document_index_path.write_text(
        json.dumps(serialized_documents, indent=2),
        encoding="utf-8",
    )

def validate_pdf_upload(file: UploadFile) -> None:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file must have a filename")
    
    file_suffix = Path(file.filename).suffix.lower()

    if file_suffix != ".pdf":
        raise HTTPException(
            status_code=400,
            detail=f"Only PDF files are allowed. Invalid file: {file.filename}"
        )
    
    if file.content_type and file.content_type not in PDF_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid PDF content type for {file.filename}: {file.content_type}",
        )
    
async def save_uploaded_pdf(file: UploadFile) -> DocumentMetadata:
    ensure_storage_ready()
    validate_pdf_upload(file)

    document_id = str(uuid4())
    safe_original_filename = sanitize_filename(file.filename)
    stored_filename = f"{document_id}.pdf"
    destination_path = settings.upload_dir/stored_filename

    max_size_bytes = settings.max_upload_size_mb * 1024 * 1024
    size_bytes = 0

    try:
        with destination_path.open("wb") as output_file:
            while chunk := await file.read(1024 * 1024):
                size_bytes += len(chunk)

                if size_bytes > max_size_bytes:
                    output_file.close()
                    destination_path.unlike(missing_ok=True)

                    raise HTTPException(
                        status_code=413,
                        detail=(
                            f"File {file.filename} is too large."
                            f"Maximum size is {settings.max_upload_size_mb} MB."
                        ),
                    )
                output_file.write(chunk)

        if size_bytes == 0:
            destination_path.unlike(missing_ok=True)
            raise HTTPException(
                status_code=400,
                detail=f"File {file.filename} is empty."
            )
        
        document = DocumentMetadata(
            id=document_id,
            original_filename=safe_original_filename,
            stored_filename=stored_filename,
            content_type=file.content_type,
            size_bytes=size_bytes,
            uploaded_at=datetime.now(timezone.utc),
            upload_status="uploaded",
        )

        documents = load_document_index()
        documents.append(document)
        save_document_index(documents)

        return document
    
    finally:
        await file.close()

def list_uploaded_documents() -> list[DocumentMetadata]:
    return load_document_index()