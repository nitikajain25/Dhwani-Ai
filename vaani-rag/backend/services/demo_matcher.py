import re
import difflib
from backend.data.demo_questions import DEMO_QUESTIONS

def normalize_text(text: str) -> str:
    # Remove non-alphanumeric (keep spaces) and lowercase
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()
    return text

def match_demo_question(transcript: str, threshold: float = 0.6):
    """
    Matches the transcript against DEMO_QA.
    Returns the matching dictionary or None if no match is above the threshold.
    """
    norm_transcript = normalize_text(transcript)
    
    best_match = None
    best_score = 0.0
    
    for item in DEMO_QUESTIONS:
        norm_q = normalize_text(item["question"])
        
        # We can use difflib for string similarity
        # A simple token overlap + difflib
        ratio = difflib.SequenceMatcher(None, norm_transcript, norm_q).ratio()
        
        if ratio > best_score:
            best_score = ratio
            best_match = item
            
    if best_score >= threshold:
        return best_match
    return None
