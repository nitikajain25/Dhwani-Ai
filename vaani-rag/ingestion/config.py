import os
from pathlib import Path
from dotenv import load_dotenv

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ============================================================
# Output Directories
# ============================================================

OUTPUT_DIR = PROJECT_ROOT / "outputs"
CHUNKS_DIR = OUTPUT_DIR / "chunks"
EMBEDDINGS_DIR = OUTPUT_DIR / "embeddings"
MANIFESTS_DIR = OUTPUT_DIR / "manifests"
CHECKPOINTS_DIR = OUTPUT_DIR / "checkpoints"
LOGS_DIR = OUTPUT_DIR / "logs"

for directory in [
    OUTPUT_DIR,
    CHUNKS_DIR,
    EMBEDDINGS_DIR,
    MANIFESTS_DIR,
    CHECKPOINTS_DIR,
    LOGS_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)


# ============================================================
# Embedding Configuration
# ============================================================

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "BAAI/bge-m3",
)

EMBEDDING_BACKEND = os.getenv(
    "EMBEDDING_BACKEND",
    "openvino",
).lower()

EMBEDDING_DEVICE = os.getenv(
    "EMBEDDING_DEVICE",
    "GPU",
).upper()

EMBEDDING_MODEL_PATH = os.getenv(
    "EMBEDDING_MODEL_PATH",
    str(PROJECT_ROOT / "models" / "bge-m3-openvino"),
)

EMBEDDING_TRANSFORMERS_MODEL_PATH = os.getenv(
    "EMBEDDING_TRANSFORMERS_MODEL_PATH",
    str(PROJECT_ROOT / "models" / "bge-m3"),
)

EMBEDDING_BATCH_SIZE = int(
    os.getenv("EMBEDDING_BATCH_SIZE", "32")
)

EMBEDDING_MAX_LENGTH = int(
    os.getenv("EMBEDDING_MAX_LENGTH", "8192")
)


# ============================================================
# Qdrant Configuration
# ============================================================

QDRANT_URL = os.getenv(
    "QDRANT_URL",
    "",
)

QDRANT_API_KEY = os.getenv(
    "QDRANT_API_KEY",
    "",
)

QDRANT_COLLECTION_NAME = os.getenv(
    "QDRANT_COLLECTION_NAME",
    "vaani_rag",
)