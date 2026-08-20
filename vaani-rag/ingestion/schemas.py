from typing import Optional, List
from pydantic import BaseModel, Field

class Passage(BaseModel):
    """
    Represents a raw passage extracted from the MSMARCO-XI dataset records.
    """
    passage_id: str = Field(..., description="Deterministic unique passage identifier")
    text: str = Field(..., description="Cleaned passage text content")
    language: str = Field(..., description="Language of the passage (en, hi, mr)")
    query_id: Optional[str] = Field(None, description="Original query ID the passage is associated with")
    query_type: Optional[str] = Field(None, description="Original query type")
    source_lang: Optional[str] = Field(None, description="Source language of dataset row")
    target_lang: Optional[str] = Field(None, description="Target language of dataset row")
    is_selected: Optional[bool] = Field(False, description="Relevance flag (evaluation metadata)")
    original_record_index: int = Field(..., description="Index of the row in the source stream")
    content_hash: str = Field(..., description="SHA-256 hash of the cleaned passage text")


class Chunk(BaseModel):
    """
    Represents a chunk extracted from a Passage using a specific chunking strategy.
    """
    chunk_id: str = Field(..., description="Deterministic chunk ID (e.g. hi_adaptive_<hash>_0)")
    parent_passage_id: str = Field(..., description="ID of the parent passage")
    text: str = Field(..., description="Chunk text content")
    language: str = Field(..., description="Language of the chunk")
    strategy: str = Field(..., description="Strategy name used for chunking")
    chunk_index: int = Field(..., description="Zero-based index of chunk within parent passage")
    token_count: int = Field(..., description="Estimated or actual token count")
    content_hash: str = Field(..., description="SHA-256 hash of the chunk text")
    query_id: Optional[str] = Field(None, description="Evaluation query ID")
    query_type: Optional[str] = Field(None, description="Evaluation query type")
    is_selected: Optional[bool] = Field(None, description="Evaluation relevance label")


class VectorRecord(BaseModel):
    """
    Represents a Pinecone vector upload payload.
    """
    id: str = Field(..., description="Unique vector record ID (identical to chunk_id)")
    values: List[float] = Field(..., description="1024-dimensional float list embedding values")
    metadata: dict = Field(..., description="Compact metadata containing text and source mapping")
