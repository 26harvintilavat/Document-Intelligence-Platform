import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException

from app.core.config import settings
from app.schemas.chunk import DocumentChunk

def ensure_chunk_storage_ready() -> None:
    settings.chunk_storage_dir.mkdir(parents=True, exist_ok=True)

def get_extracted_text_path(document_id: str) -> Path:
    return settings.extracted_text_dir / f"{document_id}.txt"

def get_chunk_file_path(document_id: str) -> Path:
    return settings.chunk_storage_dir / f"{document_id}.json"

def load_extracted_text(document_id: str) -> str:
    extracted_text_path = get_extracted_text_path(document_id)

    if not extracted_text_path.exists():
        raise HTTPException (
            status_code=404,
            detail=(
                f"No extracted text found for document ID {document_id}."
                "Run text extraction before chunking."
            ),
        )
    
    text = extracted_text_path.read_text(encoding="utf-8")

    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail=f"Extracted text for document ID {document_id} is empty.",
        )
    
    return text

def split_text_into_chunks(
        text: str,
        document_id: str,
        chunk_size: int,
        chunk_overlap: int,
) -> list[DocumentChunk]:
    
    if chunk_size <= 0:
        raise HTTPException(status_code=500, detail="Chunk size must be greater than 0.")
    
    if chunk_overlap < 0:
        raise HTTPException(status_code=500, detail="Chunk overlap cannot be negative.")
    
    if chunk_overlap > chunk_size:
        raise HTTPException(
            status_code=500, 
            detail="Chunk overlap must be smaller than chunk size."
        )
    
    chunks: list[DocumentChunk] = []
    start = 0
    chunk_index = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk_text = text[start:end].strip()

        if chunk_text:
            chunks.append(
                DocumentChunk(
                    id=str(uuid4()),
                    document_id=document_id,
                    chunk_index=chunk_index,
                    text=chunk_text,
                    character_start=start,
                    character_end=end,
                    created_at=datetime.now(timezone.utc),
                )
            )
            chunk_index+=1

        if end == text_length:
            break

        start = end - chunk_overlap

    return chunks

def save_chunks(document_id: str, chunks: list[DocumentChunk]) -> None:
    ensure_chunk_storage_ready()

    chunk_file_path = get_chunk_file_path(document_id)

    serialized_chunks = [chunk.model_dump(mode="json") for chunk in chunks]

    chunk_file_path.write_text(
        json.dumps(serialized_chunks, indent=2),
        encoding="utf-8",
    )

def load_chunks(document_id: str) -> list[DocumentChunk]:
    ensure_chunk_storage_ready()

    chunk_file_path = get_chunk_file_path(document_id)

    if not chunk_file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"No chunks found for document ID {document_id}.",
        )

    raw_data = chunk_file_path.read_text(encoding="utf-8")

    if not raw_data.strip():
        return []

    chunks = json.loads(raw_data)
    return [DocumentChunk.model_validate(chunk) for chunk in chunks]

def chunk_document(document_id: str) -> list[DocumentChunk]:
    text = load_extracted_text(document_id)

    chunks = split_text_into_chunks(
        text=text,
        document_id=document_id,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )

    if not chunks:
        raise HTTPException(
            status_code=400,
            detail=f"No chunks were created for document ID {document_id}.",
        )

    save_chunks(document_id=document_id, chunks=chunks)

    return chunks