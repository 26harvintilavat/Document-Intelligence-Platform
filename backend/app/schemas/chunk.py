from datetime import datetime
from pydantic import BaseModel, Field

class DocumentChunk(BaseModel):
    id: str = Field(..., description="Unique chunk ID")
    document_id: str = Field(..., description="Parent document ID")
    chunk_index: int = Field(..., description="Chunk position inside the document")
    text: str = Field(..., description="Chunk text content")
    character_start: int = Field(..., description="Start character position")
    character_end: int = Field(..., description="End character position")
    created_at: datetime = Field(..., description="Chunk creation timestamp")

class ChunkDocumentResponse(BaseModel):
    document_id: str
    chunk_count: int
    chunks: list[DocumentChunk]

class ChunkListResponse(BaseModel):
    document_id: str
    chunk_count: int
    chunks: list[DocumentChunk]