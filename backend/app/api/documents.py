from typing import Annotated
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.document import DocumentListResponse, UploadDocumentsResponse
from app.services.document_storage_service import (
    list_uploaded_documents,
    save_uploaded_pdf,
)
from app.services.pdf_text_extraction_service import extract_text_from_pdf

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload", response_model=UploadDocumentsResponse)
async def upload_documents(
    file: UploadFile = File(..., description="PDF file to upload"),):
    if not file:
        raise HTTPException(status_code=400, detail="At least one PDF file is required.")
    
    uploaded_document = await save_uploaded_pdf(file)

    return UploadDocumentsResponse(
        count=1,
        documents=[uploaded_document],
    )

@router.get("", response_model=DocumentListResponse)
def get_documents():
    documents = list_uploaded_documents()

    return DocumentListResponse(
        count=len(documents),
        documents=documents,
    )

@router.post("/{document_id}/extract-text")
def extract_document_text(document_id: str):
    documents = list_uploaded_documents()

    document = None

    for item in documents:
        if item.id == document_id:
            document = item
            break

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    
    try:
        extracted_text_path = extract_text_from_pdf(
            pdf_path=f"app/storage/uploads/{document.stored_filename}",
            document_id=document.id,
        )

        return {
            "message": "Text extracted successfully.",
            "document_id": document.id,
            "filename": document.original_filename,
            "extracted_text_path": extracted_text_path,
        }
    
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))
    
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract text from PDF: {str(error)}",
        )