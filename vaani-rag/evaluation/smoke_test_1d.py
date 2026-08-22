import sys
import os
import json
import time
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Prevent terminal encoding failures
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from ingestion.rag_pipeline import RAGBaselinePipeline

def run_smoke_test():
    print("=" * 60)
    print("PHASE 1D SMOKE TEST")
    print("=" * 60)

    try:
        pipeline = RAGBaselinePipeline()
        print("Pipeline initialized successfully.\n")
    except Exception as e:
        print(f"Failed to initialize pipeline: {e}")
        return

    test_queries = [
        {"desc": "English query", "lang": "en", "q": "What is photosynthesis?"},
        {"desc": "Hindi query", "lang": "hi", "q": "प्रकाश संश्लेषण क्या है?"},
        {"desc": "Marathi query", "lang": "mr", "q": "प्रकाशसंश्लेषण म्हणजे काय?"},
        {"desc": "Clearly answerable query", "lang": "en", "q": "How do plants produce glucose?"},
        {"desc": "Clearly unsupported query", "lang": "en", "q": "What is the capital of Mars and how does it relate to the Matrix?"},
    ]

    for item in test_queries:
        print("-" * 50)
        print(f"Test: {item['desc']}")
        print(f"Query ({item['lang'].upper()}): {item['q']}")
        
        response = pipeline.generate_answer(query=item['q'], language=item['lang'], top_k=5)
        
        print(f"Success Flag: {response.success}")
        print(f"Retrieved Chunks: {len(response.retrieved_candidates)}")
        print(f"Answer: {response.answer}")
        if response.error_message:
            print(f"Error Message: {response.error_message}")
        
        # Avoid instant rate limits
        time.sleep(2.0)

if __name__ == "__main__":
    run_smoke_test()
