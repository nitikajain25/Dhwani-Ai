import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from ingestion.schemas import Passage
from ingestion.cleaner import clean_text, clean_passage

def test_clean_text_spaces_and_newlines():
    raw_text = "   Hello    World!  \n  This\t  is   \r  clean.   "
    expected = "Hello World! This is clean."
    assert clean_text(raw_text) == expected

def test_clean_text_indic_unicode():
    # Test Devnagari unicode integrity and normalizer
    indic_raw = "मराठी   आणि \n  हिंदी   मजकूर"
    expected = "मराठी आणि हिंदी मजकूर"
    assert clean_text(indic_raw) == expected

def test_clean_passage_hash_recalculation():
    passage = Passage(
        passage_id="en_passage_mockhash_0_0",
        text="   Some   raw passage content.  ",
        language="en",
        query_id="q1",
        original_record_index=0,
        content_hash="mockhash"
    )
    
    cleaned = clean_passage(passage)
    assert cleaned is not None
    assert cleaned.text == "Some raw passage content."
    assert cleaned.content_hash != "mockhash"
    assert len(cleaned.content_hash) == 64
    assert cleaned.passage_id != "en_passage_mockhash_0_0"
    assert "en_passage_" in cleaned.passage_id
