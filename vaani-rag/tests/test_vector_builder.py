import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from ingestion.schemas import Chunk
from ingestion.vector_builder import build_vector_record

def test_build_vector_record_compaction():
    chunk = Chunk(
        chunk_id="en_adaptive_contenthash_0",
        parent_passage_id="parent_passage_123",
        text="Verification passage text.",
        language="en",
        strategy="adaptive",
        chunk_index=0,
        token_count=12,
        content_hash="contenthash",
        query_id="q_999",
        query_type="train",
        is_selected=True
    )
    
    mock_embedding = [0.05] * 1024
    record = build_vector_record(chunk, mock_embedding)
    
    assert record.id == "en_adaptive_contenthash_0"
    assert record.values == mock_embedding
    
    # Metadata fields assertion
    meta = record.metadata
    assert meta["language"] == "en"
    assert meta["text"] == "Verification passage text."
    assert meta["chunk_id"] == "en_adaptive_contenthash_0"
    assert meta["parent_passage_id"] == "parent_passage_123"
    assert meta["strategy"] == "adaptive"
    assert meta["content_hash"] == "contenthash"
    assert meta["token_count"] == 12
    
    # Evaluation metadata assertion
    assert meta["query_id"] == "q_999"
    assert meta["query_type"] == "train"
    assert meta["is_selected"] is True
