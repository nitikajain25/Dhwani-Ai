import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from ingestion.schemas import Passage
from ingestion.deduplicator import Deduplicator

def test_deduplicator_metrics():
    dedup = Deduplicator()

    passage_1 = Passage(
        passage_id="en_passage_hashA_0_0",
        text="This is a unique passage.",
        language="en",
        query_id="10",
        original_record_index=0,
        content_hash="hashA"
    )
    
    passage_2 = Passage(
        passage_id="en_passage_hashB_0_1",
        text="This is another unique passage.",
        language="en",
        query_id="10",
        original_record_index=0,
        content_hash="hashB"
    )
    
    passage_3 = Passage(
        passage_id="en_passage_hashA_1_0",
        text="This is a unique passage.",  # Duplicate of passage_1
        language="en",
        query_id="11",
        original_record_index=1,
        content_hash="hashA"
    )

    # 1. Assert uniqueness checks
    assert dedup.is_duplicate(passage_1) is False
    assert dedup.is_duplicate(passage_2) is False
    assert dedup.is_duplicate(passage_3) is True

    # 2. Assert telemetry calculation
    stats = dedup.get_stats()
    assert stats["raw_passages"] == 3
    assert stats["duplicates"] == 1
    assert stats["unique_passages"] == 2
    assert stats["duplicate_percentage"] == 33.33
