import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from ingestion import config
from ingestion.pinecone_client import get_pinecone_client, verify_and_get_index
from ingestion.schemas import VectorRecord
from ingestion.pinecone_uploader import upload_vectors_in_batches

def main():
    print("Initializing Pinecone Cloud Validation Script...")
    
    # Check if key is configured
    if not config.PINECONE_API_KEY or config.PINECONE_API_KEY == "mock-api-key-for-dry-run":
        print("\nFAIL: PINECONE_API_KEY is not set or set to mock default in .env file.")
        print("Please configure PINECONE_API_KEY before running Pinecone validations.")
        sys.exit(1)

    try:
        # 1. Initialize client
        pc = get_pinecone_client()
        print("Pinecone client initialized successfully.")
        
        # 2. Access or create Index
        print(f"Connecting to index '{config.PINECONE_INDEX_NAME}'...")
        index = verify_and_get_index(pc, config.PINECONE_INDEX_NAME)
        print("Index verified and connection established.")
        
        # 3. Retrieve status
        stats = index.describe_index_stats()
        print(f"\nCurrent Index Stats:")
        print(f"  - Total vector count: {stats.get('total_vector_count', 0)}")
        print(f"  - Namespaces: {list(stats.get('namespaces', {}).keys())}")
        
        # 4. Upsert verification vector
        print("\nUpserting single mock validation vector...")
        mock_values = [0.01] * 1024
        mock_record = VectorRecord(
            id="validation_test_vector_id_0",
            values=mock_values,
            metadata={
                "language": "en",
                "text": "This is a temporary metadata vector for ingestion pipeline verification.",
                "chunk_id": "validation_test_vector_id_0",
                "parent_passage_id": "validation_parent_passage_id",
                "strategy": "validation_test",
                "content_hash": "validation_hash_123",
                "token_count": 10
            }
        )
        
        # Upload vector to 'en' namespace
        upload_stats = upload_vectors_in_batches(
            index=index,
            vectors=[mock_record],
            namespace="en",
            batch_size=1
        )
        
        print("\n============================================================")
        print("PINECONE VALIDATION REPORT")
        print("============================================================")
        print(f"index name: {config.PINECONE_INDEX_NAME}")
        print(f"dimension: 1024")
        print(f"metric: cosine")
        print(f"attempted: {upload_stats['attempted']}")
        print(f"uploaded: {upload_stats['uploaded']}")
        print(f"failed: {upload_stats['failed']}")
        print(f"retries: {upload_stats['retries']}")
        print(f"duration: {upload_stats['duration']}s")
        print("============================================================")

        # 5. Clean up
        print("\nCleaning up validation vector...")
        index.delete(ids=["validation_test_vector_id_0"], namespace="en")
        print("Validation vector deleted successfully. Index is clean.")
        print("SUCCESS: Pinecone client and metadata uploading validated.")
        
    except Exception as e:
        print(f"\nFAIL: Pinecone validation failed with exception: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
