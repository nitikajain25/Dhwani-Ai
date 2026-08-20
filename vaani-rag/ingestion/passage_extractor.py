import hashlib
from typing import Iterator, Dict, Any, List, Tuple
from ingestion.schemas import Passage
from ingestion.logging_config import logger

def calculate_hash(text: str) -> str:
    """Calculates SHA-256 hash of text."""
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()

def extract_passages_from_row(
    row: Dict[str, Any], 
    record_index: int
) -> Iterator[Passage]:
    """
    Parses a raw dataset row and extracts individual Passage objects.
    Yields both English and translated passages from the same row.
    """
    query_id = str(row.get("query_id", ""))
    query_type = row.get("query_type", "")
    source_lang = row.get("source_lang", "")
    target_lang_raw = str(row.get("target_lang", ""))
    
    target_lang = None
    if target_lang_raw.startswith("hi_"):
        target_lang = "hi"
    elif target_lang_raw.startswith("mr_"):
        target_lang = "mr"
        
    passages_field = row.get("passages")
    if passages_field is None:
        logger.warning(f"Row {record_index} has no 'passages' field. Skipping.")
        return

    extracted_items: List[Tuple[str, str, Any]] = []

    if isinstance(passages_field, dict):
        # Column-oriented format (dict of lists)
        is_selected_list = passages_field.get("is_selected")
        english_list = passages_field.get("English_passages", passages_field.get("english_passages"))
        translated_list = passages_field.get("Translated_passages", passages_field.get("translated_passages"))
        
        is_selected_list = is_selected_list if is_selected_list is not None else []
        english_list = english_list if english_list is not None else []
        translated_list = translated_list if translated_list is not None else []
        
        len_eng = len(english_list)
        len_trans = len(translated_list)
        len_sel = len(is_selected_list)
        
        if len_eng != len_trans or (len_sel > 0 and len_sel != len_eng):
            logger.warning(
                f"Row {record_index}: Mismatched passage list lengths - "
                f"Eng: {len_eng}, Trans: {len_trans}, Sel: {len_sel}."
            )
            
        # Use minimum to avoid out-of-bounds mapping errors when lists differ in length
        num_passages = min(len_eng, len_trans)
        if num_passages == 0:
            num_passages = max(len_eng, len_trans)
            
        for i in range(num_passages):
            eng_text = english_list[i] if i < len_eng else ""
            trans_text = translated_list[i] if i < len_trans else ""
            sel = is_selected_list[i] if i < len_sel else 0
            extracted_items.append((eng_text, trans_text, sel))
            
    elif isinstance(passages_field, list):
        # Row-oriented format (list of dicts)
        for p in passages_field:
            if isinstance(p, dict):
                eng_text = p.get("English_passages", p.get("english_passages", ""))
                trans_text = p.get("Translated_passages", p.get("translated_passages", ""))
                sel = p.get("is_selected", 0)
                extracted_items.append((eng_text, trans_text, sel))
    else:
        logger.error(f"Row {record_index}: 'passages' field is of unsupported type: {type(passages_field)}")
        return

    # Yield individual passages
    for idx, (eng_text, trans_text, sel) in enumerate(extracted_items):
        
        # 1. Emit English passage
        if isinstance(eng_text, str) and eng_text.strip():
            cleaned_en = eng_text.strip()
            content_hash_en = calculate_hash(cleaned_en)
            yield Passage(
                passage_id=f"en_passage_{content_hash_en[:16]}_{record_index}_{idx}",
                text=cleaned_en,
                language="en",
                query_id=query_id,
                query_type=query_type,
                source_lang=source_lang,
                target_lang=target_lang_raw,
                is_selected=bool(sel),
                original_record_index=record_index,
                content_hash=content_hash_en
            )
            
        # 2. Emit Translated passage if target_lang is matched (hi or mr)
        if target_lang and isinstance(trans_text, str) and trans_text.strip():
            cleaned_trans = trans_text.strip()
            content_hash_trans = calculate_hash(cleaned_trans)
            yield Passage(
                passage_id=f"{target_lang}_passage_{content_hash_trans[:16]}_{record_index}_{idx}",
                text=cleaned_trans,
                language=target_lang,
                query_id=query_id,
                query_type=query_type,
                source_lang=source_lang,
                target_lang=target_lang_raw,
                is_selected=bool(sel),
                original_record_index=record_index,
                content_hash=content_hash_trans
            )
