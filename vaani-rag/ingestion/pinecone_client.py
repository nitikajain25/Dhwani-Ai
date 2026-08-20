from pinecone import Pinecone, ServerlessSpec
from ingestion.config import (
    PINECONE_API_KEY, 
    PINECONE_INDEX_NAME, 
    PINECONE_CLOUD, 
    PINECONE_REGION
)
from ingestion.logging_config import logger

def get_pinecone_client() -> Pinecone:
    """
    Initializes and returns the Pinecone client.
    Fails fast if the API Key is not set.
    """
    if not PINECONE_API_KEY or PINECONE_API_KEY == "mock-api-key-for-dry-run":
        logger.error("PINECONE_API_KEY is missing or set to mock. Cannot connect to Pinecone Cloud.")
        raise ValueError("Missing PINECONE_API_KEY environment variable.")
        
    try:
        return Pinecone(api_key=PINECONE_API_KEY)
    except Exception as e:
        logger.critical(f"Failed to initialize Pinecone client: {e}")
        raise e

def verify_and_get_index(pc: Pinecone, index_name: str = PINECONE_INDEX_NAME) -> any:
    """
    Connects to an existing index or creates it if missing.
    Performs rigorous validations on existing indices to prevent mismatches.
    """
    try:
        indexes = pc.list_indexes()
        target_index = None
        
        for idx in indexes:
            # Safely handle object attribute access vs dict access across SDK updates
            name = getattr(idx, "name", None) or (idx.get("name") if isinstance(idx, dict) else str(idx))
            if name == index_name:
                target_index = idx
                break
                
        if target_index is not None:
            # 1. Validate compatible properties
            dim = getattr(target_index, "dimension", None) or (target_index.get("dimension") if isinstance(target_index, dict) else None)
            metric = getattr(target_index, "metric", None) or (target_index.get("metric") if isinstance(target_index, dict) else None)
            
            # If properties cannot be read or are wrong, validate carefully
            if dim is not None and dim != 1024:
                logger.critical(f"Index '{index_name}' exists but has dimension {dim}. Expected 1024.")
                raise ValueError(f"Incompatible index dimension {dim}. Expected 1024.")
            if metric is not None and metric != "cosine":
                logger.critical(f"Index '{index_name}' exists but uses metric {metric}. Expected 'cosine'.")
                raise ValueError(f"Incompatible index metric {metric}. Expected 'cosine'.")
                
            logger.info(f"Reusing compatible existing Pinecone index '{index_name}'")
        else:
            # 2. Create Serverless index
            logger.info(f"Index '{index_name}' not found. Creating a serverless instance ({PINECONE_CLOUD}/{PINECONE_REGION})...")
            pc.create_index(
                name=index_name,
                dimension=1024,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud=PINECONE_CLOUD,
                    region=PINECONE_REGION
                )
            )
            logger.info(f"Successfully created Pinecone index '{index_name}'")
            
        return pc.Index(index_name)
        
    except Exception as e:
        logger.error(f"Error accessing or creating Pinecone index '{index_name}': {e}")
        raise e
