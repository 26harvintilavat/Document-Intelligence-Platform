from datetime import datetime
from pydantic import BaseModel, Field

class DocumentMetadata(BaseModel):
    id: str = Field(..., description="Unique document ID")
    original_filename: str = Field(..., description="Original uploaded file name")
    stored_filename: str = Field(..., description="Internal stored file name")
    content_type: str | None = Field(default=None, description="Uploaded file content type")
    size_bytes: int = Field(..., description="File size in bytes")
    uploaded_at: datetime = Field(..., description="Upload timestamp")
    upload_status: str = Field(default="uploaded", description="Current document status")

class UploadDocumentsResponse(BaseModel):
    count: int
    documents: list[DocumentMetadata]

class DocumentListResponse(BaseModel):
    count: int
    documents: list[DocumentMetadata]