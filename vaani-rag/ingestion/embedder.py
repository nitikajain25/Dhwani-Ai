import time
import torch
from typing import List
from sentence_transformers import SentenceTransformer
from ingestion.logging_config import logger

class BGEM3Embedder:
    """
    Singleton wrapper for the BAAI/bge-m3 model.
    Ensures model is loaded once and shared across stages.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(BGEM3Embedder, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_name: str = "BAAI/bge-m3", batch_size: int = 16):
        if self._initialized:
            return
            
        self.model_name = model_name
        self.batch_size = batch_size
        
        # 1. Detect device
        if torch.cuda.is_available():
            self.device = "cuda"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            self.device = "mps"
        else:
            self.device = "cpu"
            
        logger.info(f"Loading embedding model '{model_name}' on device '{self.device}'...")
        t0 = time.time()
        
        # Load local model
        self.model = SentenceTransformer(model_name, device=self.device)
        logger.info(f"Embedding model loaded successfully in {time.time() - t0:.2f}s")
        
        # 2. Verify dimension and dtype programmatically
        # Run a small test embedding to read dimensions
        test_run = self.model.encode(["verification"], normalize_embeddings=True)
        self.dimension = test_run.shape[1]
        self.dtype = str(test_run.dtype)
        
        logger.info(
            f"Embedding Config | Name: {self.model_name} | Device: {self.device} "
            f"| Dimension: {self.dimension} | Dtype: {self.dtype}"
        )
        
        if self.dimension != 1024:
            logger.critical(
                f"FATAL: Dimension of model is {self.dimension}, but VaaniRAG requires 1024. Failing fast."
            )
            raise ValueError(f"Incompatible embedding model dimension: {self.dimension}. Expected 1024.")
            
        self._initialized = True

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Embeds a list of texts in batches. Handles CUDA Out-Of-Memory errors
        gracefully by reducing batch size dynamically.
        """
        if not texts:
            return []
            
        current_batch_size = self.batch_size
        
        while current_batch_size >= 1:
            try:
                embeddings = self.model.encode(
                    texts,
                    batch_size=current_batch_size,
                    show_progress_bar=False,
                    normalize_embeddings=True,
                    convert_to_numpy=True
                )
                return embeddings.tolist()
            except RuntimeError as e:
                # Catch CUDA Out of Memory
                err_msg = str(e).lower()
                if "out of memory" in err_msg and self.device == "cuda":
                    logger.warning(
                        f"CUDA Out of Memory hit with batch size {current_batch_size}. "
                        f"Halving batch size to {current_batch_size // 2} and emptying cache."
                    )
                    torch.cuda.empty_cache()
                    current_batch_size //= 2
                    if current_batch_size < 1:
                        logger.critical("Batch size dropped below 1 during CUDA OOM recovery. Aborting.")
                        raise e
                else:
                    logger.error(f"Embedding generation failed: {e}")
                    raise e
                    
        raise RuntimeError("Embedding generation failed due to persistent OOM errors.")

    def embed_query(self, text: str) -> List[float]:
        """
        Embeds a single query string. Used for evaluation or downstream retrieval.
        """
        emb = self.model.encode(
            [text],
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        return emb[0].tolist()
