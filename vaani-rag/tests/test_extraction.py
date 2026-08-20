import sys
import pytest
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from ingestion.passage_extractor import extract_passages_from_row

def test_extraction_basic():
    row = {
        "query_id": 1,
        "query_type": "test",
        "source_lang": "en",
        "target_lang": "hi_IN",
        "passages": {
            "English_passages": ["Eng1", "Eng2"],
            "Translated_passages": ["Hi1", "Hi2"],
            "is_selected": [1, 0]
        }
    }
    
    passages = list(extract_passages_from_row(row, 0))
    
    assert len(passages) == 4  # 2 English, 2 Hindi
    
    eng_passages = [p for p in passages if p.language == "en"]
    hi_passages = [p for p in passages if p.language == "hi"]
    
    assert len(eng_passages) == 2
    assert eng_passages[0].text == "Eng1"
    assert eng_passages[0].is_selected == True
    
    assert len(hi_passages) == 2
    assert hi_passages[1].text == "Hi2"
    assert hi_passages[1].is_selected == False
    assert hi_passages[1].target_lang == "hi_IN"

def test_extraction_alignment_mismatch():
    row = {
        "target_lang": "mr_IN",
        "passages": {
            "English_passages": ["Eng1", "Eng2"],
            "Translated_passages": ["Mr1"],
            "is_selected": [1, 0]
        }
    }
    
    passages = list(extract_passages_from_row(row, 1))
    
    # Should use minimum length which is 1
    assert len(passages) == 2 # 1 English, 1 Marathi
    assert passages[0].language == "en"
    assert passages[0].text == "Eng1"
    assert passages[1].language == "mr"
    assert passages[1].text == "Mr1"

def test_extraction_no_target_lang_match():
    # If target_lang is neither hi nor mr, it should only extract english
    row = {
        "target_lang": "bn_IN",
        "passages": {
            "English_passages": ["Eng1"],
            "Translated_passages": ["Bn1"],
            "is_selected": [1]
        }
    }
    
    passages = list(extract_passages_from_row(row, 2))
    assert len(passages) == 1
    assert passages[0].language == "en"
    assert passages[0].text == "Eng1"
