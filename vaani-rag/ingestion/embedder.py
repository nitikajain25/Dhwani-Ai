import time
from pathlib import Path
from typing import List, Optional

import numpy as np
import openvino as ov
from transformers import AutoTokenizer

from ingestion.logging_config import logger


class BGEM3Embedder:
    """
    DhawaniRAG BGE-M3 embedding backend.

    Production backend:
        BGE-M3 -> OpenVINO -> Intel GPU

    The model is expected to be an OpenVINO-exported BGE-M3 model
    containing:
        - openvino_model.xml
        - openvino_model.bin
        - tokenizer.json
        - tokenizer_config.json

    Dense embeddings:
        last_hidden_state[:, 0, :]
        followed by L2 normalization.

    Output dimension:
        1024
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False

        return cls._instance

    def __init__(
        self,
        model_name: str = "BAAI/bge-m3",
        batch_size: int = 32,
        model_path: Optional[str] = None,
        device: str = "GPU",
        max_length: int = 8192,
    ):
        if self._initialized:
            return

        self.model_name = model_name
        self.batch_size = batch_size
        self.device = device
        self.max_length = max_length

        project_root = Path(__file__).resolve().parent.parent

        if model_path:
            self.model_path = Path(model_path)
        else:
            self.model_path = project_root / "models" / "bge-m3-openvino"

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"OpenVINO BGE-M3 model not found at: {self.model_path}"
            )

        xml_path = self.model_path / "openvino_model.xml"

        if not xml_path.exists():
            raise FileNotFoundError(
                f"OpenVINO model file not found: {xml_path}"
            )

        logger.info("=" * 70)
        logger.info("Loading BGE-M3 OpenVINO embedding backend")
        logger.info(f"Model path: {self.model_path}")
        logger.info(f"Requested device: {self.device}")
        logger.info("=" * 70)

        # ------------------------------------------------------------
        # 1. OpenVINO runtime
        # ------------------------------------------------------------

        self.core = ov.Core()

        available_devices = self.core.available_devices

        logger.info(f"Available OpenVINO devices: {available_devices}")

        if self.device not in available_devices:
            raise RuntimeError(
                f"Requested OpenVINO device '{self.device}' is not available. "
                f"Available devices: {available_devices}"
            )

        # ------------------------------------------------------------
        # 2. Tokenizer
        # ------------------------------------------------------------

        t0 = time.time()

        logger.info("Loading tokenizer...")

        self.tokenizer = AutoTokenizer.from_pretrained(
            str(self.model_path),
            local_files_only=True,
        )

        logger.info(
            f"Tokenizer loaded in {time.time() - t0:.2f}s"
        )

        # ------------------------------------------------------------
        # 3. Load and compile OpenVINO model
        # ------------------------------------------------------------

        t0 = time.time()

        logger.info(
            f"Compiling BGE-M3 OpenVINO model on {self.device}..."
        )

        model = self.core.read_model(str(xml_path))

        self.compiled_model = self.core.compile_model(
            model,
            self.device,
        )

        logger.info(
            f"Model compiled in {time.time() - t0:.2f}s"
        )

        # ------------------------------------------------------------
        # 4. Discover model inputs
        # ------------------------------------------------------------

        self.input_ids_name = None
        self.attention_mask_name = None

        for inp in self.compiled_model.inputs:
            name = inp.get_any_name()

            if name == "input_ids":
                self.input_ids_name = name

            elif name == "attention_mask":
                self.attention_mask_name = name

        if self.input_ids_name is None:
            raise RuntimeError(
                "OpenVINO model does not expose an input_ids input."
            )

        if self.attention_mask_name is None:
            raise RuntimeError(
                "OpenVINO model does not expose an attention_mask input."
            )

        # ------------------------------------------------------------
        # 5. Determine output
        # ------------------------------------------------------------

        self.output = self.compiled_model.output(0)

        output_shape = self.output.partial_shape

        logger.info(
            f"BGE-M3 output shape: {output_shape}"
        )

        # BGE-M3 dense embedding dimension
        self.dimension = 1024

        # ------------------------------------------------------------
        # 6. Validate with a real inference
        # ------------------------------------------------------------

        test_embedding = self._embed_batch(
            ["DhawaniRAG embedding verification"]
        )

        if test_embedding.shape != (1, 1024):
            raise ValueError(
                f"Unexpected embedding shape: {test_embedding.shape}. "
                f"Expected (1, 1024)."
            )

        norm = np.linalg.norm(test_embedding[0])

        if not np.isfinite(norm):
            raise ValueError(
                "Embedding validation failed: norm is not finite."
            )

        if abs(norm - 1.0) > 1e-4:
            raise ValueError(
                f"Embedding normalization failed. Norm={norm}"
            )

        logger.info(
            "BGE-M3 embedding validation successful."
        )

        logger.info(
            f"Embedding dimension: {self.dimension}"
        )

        logger.info(
            f"Embedding device: {self.device}"
        )

        self.dtype = "float32"

        self._initialized = True

    # =================================================================
    # INTERNAL EMBEDDING
    # =================================================================

    def _embed_batch(self, texts: List[str]) -> np.ndarray:
        """
        Embed one batch using OpenVINO.
        """

        if not texts:
            return np.empty(
                (0, self.dimension),
                dtype=np.float32,
            )

        encoded = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=self.max_length,
            return_tensors="np",
        )

        input_ids = np.asarray(
            encoded["input_ids"],
            dtype=np.int64,
        )

        attention_mask = np.asarray(
            encoded["attention_mask"],
            dtype=np.int64,
        )

        result = self.compiled_model(
            {
                self.input_ids_name: input_ids,
                self.attention_mask_name: attention_mask,
            }
        )

        # last_hidden_state:
        # [batch, sequence_length, hidden_dimension]

        last_hidden_state = np.asarray(
            result[self.output],
            dtype=np.float32,
        )

        if last_hidden_state.ndim != 3:
            raise RuntimeError(
                f"Unexpected model output shape: "
                f"{last_hidden_state.shape}"
            )

        # BGE-M3 dense representation:
        # first token / CLS representation
        embeddings = last_hidden_state[:, 0, :]

        if embeddings.shape[1] != self.dimension:
            raise RuntimeError(
                f"Unexpected embedding dimension: "
                f"{embeddings.shape[1]}"
            )

        # L2 normalization
        norms = np.linalg.norm(
            embeddings,
            axis=1,
            keepdims=True,
        )

        if np.any(norms == 0):
            raise RuntimeError(
                "Zero-norm embedding encountered."
            )

        embeddings = embeddings / norms

        embeddings = embeddings.astype(
            np.float32,
            copy=False,
        )

        # Final numerical validation
        if not np.all(np.isfinite(embeddings)):
            raise RuntimeError(
                "Embedding contains NaN or infinite values."
            )

        return embeddings

    # =================================================================
    # PUBLIC API
    # =================================================================

    def embed_texts(
        self,
        texts: List[str],
    ) -> List[List[float]]:
        """
        Embed multiple texts in batches.

        Returns:
            List[List[float]]
        """

        if not texts:
            return []

        all_embeddings = []

        total = len(texts)

        for start in range(
            0,
            total,
            self.batch_size,
        ):
            batch = texts[
                start:start + self.batch_size
            ]

            t0 = time.time()

            embeddings = self._embed_batch(batch)

            elapsed = time.time() - t0

            logger.debug(
                f"Embedded batch of {len(batch)} texts "
                f"in {elapsed:.4f}s "
                f"({len(batch) / elapsed:.2f} embeddings/s)"
            )

            all_embeddings.append(embeddings)

        combined = np.vstack(
            all_embeddings
        )

        return combined.tolist()

    def embed_query(
        self,
        text: str,
    ) -> List[float]:
        """
        Embed one query using exactly the same
        BGE-M3/OpenVINO representation as documents.
        """

        if not text or not text.strip():
            raise ValueError(
                "Query text cannot be empty."
            )

        embedding = self._embed_batch(
            [text]
        )[0]

        return embedding.tolist()

    def get_dimension(self) -> int:
        return self.dimension

    def get_device(self) -> str:
        return self.device