import math
from typing import List, Tuple
from ingestion.logging_config import logger

def validate_embeddings(embeddings: List[List[float]], expected_dim: int = 1024) -> Tuple[bool, str]:
    """
    Validates a batch of generated embeddings against database safety constraints.
    Checks:
    - Non-emptiness
    - Correct dimensional length (default: 1024)
    - Absence of NaN or Infinite values
    - L2 normalization compliance (L2 norm should be ~ 1.0)
    
    Args:
        embeddings: List of embedding lists.
        expected_dim: Expected dimension of the embedding.
        
    Returns:
        Tuple of (is_valid: bool, error_reason: str)
    """
    if not embeddings:
        return False, "Embeddings batch is empty"

    for idx, vector in enumerate(embeddings):
        # 1. Non-empty check
        if not vector:
            return False, f"Vector at batch index {idx} is empty or None"
            
        # 2. Dimension check
        if len(vector) != expected_dim:
            return False, f"Vector at batch index {idx} has dimension {len(vector)}, expected {expected_dim}"
            
        l2_sum = 0.0
        for val in vector:
            # 3. NaN check
            if math.isnan(val):
                return False, f"Vector at batch index {idx} contains NaN value"
            # 4. Inf check
            if math.isinf(val):
                return False, f"Vector at batch index {idx} contains Infinite value"
            l2_sum += val * val
            
        # 5. Normalization check: L2 norm = sqrt(sum(v_i^2)) should be ~ 1.0
        l2_norm = math.sqrt(l2_sum)
        if abs(l2_norm - 1.0) > 1e-3:
            return False, f"Vector at batch index {idx} is not normalized (L2 norm is {l2_norm:.5f})"
            
    return True, ""
