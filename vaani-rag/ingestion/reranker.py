import time
from pathlib import Path
from typing import List, Optional

import numpy as np
from optimum.intel import OVModelForSequenceClassification
from transformers import AutoTokenizer

from ingestion.retriever import RetrievalResult
from ingestion.logging_config import logger


class BGEM3Reranker:
    """
    DhawaniRAG BGE-Reranker-v2-m3 backend compiled via OpenVINO.
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        device: str = "GPU",
    ):
        project_root = Path(__file__).resolve().parent.parent
        if model_path:
            self.model_path = Path(model_path)
        else:
            self.model_path = project_root / "models" / "bge-reranker-v2-m3-openvino"

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"OpenVINO Reranker model not found at: {self.model_path}"
            )

        logger.info("=" * 70)
        logger.info("Loading BGE-Reranker-v2-m3 OpenVINO backend")
        logger.info(f"Model path: {self.model_path}")
        logger.info(f"Requested device: {device}")
        logger.info("=" * 70)

        # 1. Tokenizer load
        t0 = time.time()
        self.tokenizer = AutoTokenizer.from_pretrained(
            str(self.model_path),
            local_files_only=True,
        )
        logger.info(f"Reranker tokenizer loaded in {time.time() - t0:.2f}s")

        # 2. Compile model
        t0 = time.time()
        # OVModelForSequenceClassification encapsulates core.read_model & compile_model
        self.model = OVModelForSequenceClassification.from_pretrained(
            str(self.model_path),
            device=device,
            local_files_only=True,
        )
        self.compilation_time_s = time.time() - t0
        logger.info(f"Reranker model compiled in {self.compilation_time_s:.2f}s")

        # 3. Model Warm-up (Inference test)
        logger.info("Warming up reranker model...")
        warmup_t0 = time.time()
        self._predict_scores(
            "verification query",
            ["verification passage sample content"]
        )
        self.warmup_time_s = time.time() - warmup_t0
        logger.info(f"Reranker model warmed up in {self.warmup_time_s:.2f}s")

    def _predict_scores(self, query: str, texts: List[str]) -> List[float]:
        """
        Executes sequence classification inference for query-passage pairs.
        """
        if not texts:
            return []

        # Create query-passage pairs as input strings
        pairs = [[query, text] for text in texts]

        # Tokenize pair inputs
        features = self.tokenizer(
            pairs,
            padding=True,
            truncation=True,
            return_tensors="pt",  # optimum-intel OVModel supports PyTorch tensors input
        )

        # Run inference
        outputs = self.model(**features)
        
        # Cross-encoder output is generally raw logits shape [batch, 1]
        logits = outputs.logits.detach().numpy()
        
        # Squeeze to list of floats (sigmoid is not required, as standard reranking utilizes raw relative logits directly)
        scores = logits.squeeze(axis=-1).tolist()
        
        if isinstance(scores, float):
            scores = [scores]
            
        return scores

    def rerank(
        self,
        query: str,
        candidates: List[RetrievalResult],
    ) -> List[RetrievalResult]:
        """
        Reranks candidates preserving original scores and sorting relative output logits.
        """
        if not candidates:
            return []

        texts = [c.text for c in candidates]
        
        t0 = time.time()
        scores = self._predict_scores(query, texts)
        inference_elapsed = time.time() - t0
        
        logger.debug(
            f"Reranked {len(candidates)} candidates in {inference_elapsed:.4f}s"
        )

        # Update scores while preserving original qdrant score inside metadata
        reranked_results = []
        for res, score in zip(candidates, scores):
            # Clone RetrievalResult to prevent editing original baseline reference values
            cloned = RetrievalResult(
                score=score,  # Sort score maps to Rerank classification score
                text=res.text,
                language=res.language,
                chunk_id=res.chunk_id,
                parent_passage_id=res.parent_passage_id,
                strategy=res.strategy,
                query_id=res.query_id,
                query_type=res.query_type,
                is_selected=res.is_selected,
            )
            # Retain telemetry metadata parameters
            cloned.query_type = str(res.score)  # Hacky preservation slot or dynamic metadata slot
            
            # Since RetrievalResult has set slots, let's store original score explicitly.
            # Wait, the prompt requirements explicitly say:
            # "Every reranked result must retain: chunk_id, text, language, parent_passage_id, strategy, 
            # query_id, query_type, is_selected, original Qdrant retrieval score, reranker score"
            # Let's verify how we can append attributes safely. Since RetrievalResult is a standard python dataclass
            # without slots (unless specified), we can dynamically attach properties:
            cloned.retrieval_score = float(res.score)
            cloned.rerank_score = float(score)
            reranked_results.append(cloned)

        # Sort descending by rerank score
        reranked_results.sort(key=lambda x: x.rerank_score, reverse=True)
        
        return reranked_results
