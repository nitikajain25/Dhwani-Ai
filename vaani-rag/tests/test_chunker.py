import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from ingestion.schemas import Passage
from ingestion.chunker import chunk_passage

def test_strategy_original():
    passage = Passage(
        passage_id="en_p_1",
        text="This is a test passage that should not be split under the original strategy.",
        language="en",
        original_record_index=0,
        content_hash="hash1"
    )
    chunks = chunk_passage(passage, strategy="original")
    assert len(chunks) == 1
    assert chunks[0].text == passage.text
    assert chunks[0].strategy == "original"

def test_strategy_sentence():
    passage = Passage(
        passage_id="en_p_2",
        text="This is sentence one. Sentence two has different ideas! Sentence three is final.",
        language="en",
        original_record_index=0,
        content_hash="hash2"
    )
    # Target size small to split sentences
    chunks = chunk_passage(passage, strategy="sentence", target_size=10, min_size=2)
    assert len(chunks) > 1
    assert chunks[0].strategy == "sentence"
    assert "sentence one" in chunks[0].text.lower()

def test_strategy_fixed_overlap():
    passage = Passage(
        passage_id="en_p_3",
        text="alpha beta gamma delta epsilon zeta eta theta iota kappa",
        language="en",
        original_record_index=0,
        content_hash="hash3"
    )
    # Using tiny parameters to force multiple splits
    chunks = chunk_passage(passage, strategy="fixed_overlap", chunk_size=5, chunk_overlap=2)
    assert len(chunks) > 1
    assert chunks[0].strategy == "fixed_overlap"

def test_strategy_adaptive_short():
    passage = Passage(
        passage_id="en_p_4",
        text="Tiny text.",
        language="en",
        original_record_index=0,
        content_hash="hash4"
    )
    # Under short limit, should keep original text structure
    chunks = chunk_passage(passage, strategy="adaptive", short_limit=50)
    assert len(chunks) == 1
    assert chunks[0].strategy == "adaptive"
