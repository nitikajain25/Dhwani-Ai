import sys
from typing import List
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from ingestion.logging_config import logger
from ingestion.dataset_loader import load_dataset_stream
from ingestion.passage_extractor import extract_passages_from_row

def inspect_schema(max_inspect: int = 100):
    """
    Inspects columns, data structures, and extraction statistics for the 'default' configuration.
    """
    logger.info(f"Inspecting dataset 'default' configuration (single stream)")
    
    try:
        stream = load_dataset_stream(split="train")
    except Exception as e:
        logger.error(f"Failed to stream dataset: {e}")
        return

    rows_inspected = 0
    hi_rows = 0
    mr_rows = 0
    
    eng_extracted = 0
    selected_passages = 0
    passage_lengths: List[int] = []

    for idx, row in enumerate(stream):
        if idx >= max_inspect:
            break
            
        # 1. Print detailed schema structure from the first record
        if rows_inspected == 0:
            print(f"\n============================================================")
            print(f"SCHEMA SUMMARY FOR CONFIG 'default'")
            print(f"============================================================")
            print(f"All columns: {list(row.keys())}")
            print("\nFields types:")
            for col, val in row.items():
                print(f"  - '{col}': {type(val).__name__}")
                if col == "passages":
                    print(f"    * Inner passages structure details:")
                    if isinstance(val, dict):
                        for inner_k, inner_v in val.items():
                            val_desc = f"list of length {len(inner_v)}" if isinstance(inner_v, list) else type(inner_v).__name__
                            print(f"      - '{inner_k}': {val_desc}")
                    elif isinstance(val, list):
                        if val:
                            print(f"      - list containing elements of type: {type(val[0]).__name__}")
                            if isinstance(val[0], dict):
                                print(f"      - inner keys: {list(val[0].keys())}")
            print("============================================================\n")

        # 2. Schema examples
        if rows_inspected < 3:
            target = row.get("target_lang", "")
            source = row.get("source_lang", "")
            print(f"Example {rows_inspected + 1}: target_lang='{target}', source_lang='{source}'")

        target_lang_raw = str(row.get("target_lang", ""))
        if target_lang_raw.startswith("hi_"):
            hi_rows += 1
        elif target_lang_raw.startswith("mr_"):
            mr_rows += 1
            
        passages = list(extract_passages_from_row(row, idx))
        
        for p in passages:
            if p.language == "en":
                eng_extracted += 1
            if p.is_selected:
                selected_passages += 1
            passage_lengths.append(len(p.text))

        rows_inspected += 1

    # 3. Calculate statistics
    avg_len = sum(passage_lengths) / len(passage_lengths) if passage_lengths else 0.0
    passage_lengths.sort()
    med_len = passage_lengths[len(passage_lengths) // 2] if passage_lengths else 0
    max_len = passage_lengths[-1] if passage_lengths else 0

    print("\n------------------------------------------------------------")
    print(f"INSPECTION REPORT")
    print("------------------------------------------------------------")
    print(f"rows inspected: {rows_inspected}")
    print(f"Hindi rows found: {hi_rows}")
    print(f"Marathi rows found: {mr_rows}")
    print(f"English passages extracted: {eng_extracted}")
    print(f"selected passages total: {selected_passages}")
    print(f"average passage length (chars): {round(avg_len, 2)}")
    print(f"median passage length (chars): {med_len}")
    print(f"maximum passage length (chars): {max_len}")
    print("------------------------------------------------------------\n")

if __name__ == "__main__":
    inspect_schema(100)
