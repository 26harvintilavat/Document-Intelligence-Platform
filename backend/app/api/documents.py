from typing import Annotated
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.document import DocumentListResponse, UploadDocumentsResponse
from app.services.document_storage_service import (
    list_uploaded_documents,
    save_uploaded_pdf,
)

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