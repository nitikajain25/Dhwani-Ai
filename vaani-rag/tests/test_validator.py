import sys
import math
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from ingestion.validator import validate_embeddings

def test_validator_valid_vector():
    # Valid L2 Normalized vector (1.0 at index 0, rest 0.0)
    valid_vector = [0.0] * 1024
    valid_vector[0] = 1.0
    
    is_valid, reason = validate_embeddings([valid_vector])
    assert is_valid is True
    assert reason == ""

def test_validator_invalid_dimension():
    # Wrong dimension size (512 instead of 1024)
    invalid_dim = [0.0] * 512
    is_valid, reason = validate_embeddings([invalid_dim])
    assert is_valid is False
    assert "dimension" in reason

def test_validator_nan_value():
    invalid_vector = [0.0] * 1024
    invalid_vector[5] = float("nan")
    is_valid, reason = validate_embeddings([invalid_vector])
    assert is_valid is False
    assert "NaN" in reason

def test_validator_inf_value():
    invalid_vector = [0.0] * 1024
    invalid_vector[10] = float("inf")
    is_valid, reason = validate_embeddings([invalid_vector])
    assert is_valid is False
    assert "Infinite" in reason

def test_validator_unnormalized():
    # All values set to 1.0 (L2 norm is sqrt(1024) = 32.0, not ~1.0)
    invalid_vector = [1.0] * 1024
    is_valid, reason = validate_embeddings([invalid_vector])
    assert is_valid is False
    assert "normalized" in reason
