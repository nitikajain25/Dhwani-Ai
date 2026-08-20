import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import numpy as np

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from ingestion.embedder import BGEM3Embedder

@patch("ingestion.embedder.SentenceTransformer")
def test_embedder_singleton_and_init(mock_transformer):
    mock_inst = MagicMock()
    # Mock the test embedding dimension check: shape is 1x1024
    mock_inst.encode.return_value = np.ones((1, 1024), dtype=np.float32)
    mock_transformer.return_value = mock_inst

    # Force reset Singleton for clean testing
    BGEM3Embedder._instance = None
    
    embedder = BGEM3Embedder(model_name="BAAI/bge-m3", batch_size=16)
    
    assert embedder.dimension == 1024
    assert embedder.device in ("cuda", "mps", "cpu")
    
    # Test singleton reuse
    embedder_second = BGEM3Embedder(model_name="BAAI/bge-m3", batch_size=16)
    assert embedder is embedder_second

@patch("ingestion.embedder.SentenceTransformer")
def test_embedder_batch_encoding(mock_transformer):
    mock_inst = MagicMock()
    mock_inst.encode.side_effect = [
        np.ones((1, 1024), dtype=np.float32),  # test verify call
        np.ones((3, 1024), dtype=np.float32)   # actual encode call
    ]
    mock_transformer.return_value = mock_inst

    BGEM3Embedder._instance = None
    embedder = BGEM3Embedder(model_name="BAAI/bge-m3", batch_size=16)
    
    texts = ["text1", "text2", "text3"]
    embeddings = embedder.embed_texts(texts)
    
    assert len(embeddings) == 3
    assert len(embeddings[0]) == 1024
