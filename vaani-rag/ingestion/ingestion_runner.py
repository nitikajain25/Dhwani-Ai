from collections import defaultdict

from ingestion.config import (
    CHUNKING_STRATEGY,
    EMBEDDING_MODEL,
    EMBEDDING_BATCH_SIZE,
)
from ingestion.logging_config import logger
from ingestion.local_passage_stream import stream_all_passages
from ingestion.chunker import chunk_passage
from ingestion.embedder import BGEM3Embedder
from ingestion.embedding_store import EmbeddingBatchStore
from ingestion.batch_processor import BatchProcessor
from ingestion.checkpoint import (
    save_checkpoint,
    load_checkpoint,
)


class IngestionRunner:
    """
    Production local ingestion orchestrator.

    Pipeline:

        Local Parquet
            ↓
        Passage extraction
            ↓
        Cleaning
            ↓
        Deduplication
            ↓
        Chunking
            ↓
        BGE-M3 embedding
            ↓
        VectorRecord
            ↓
        JSONL batch storage
            ↓
        Checkpoint

    Pinecone upload is NOT performed here yet.
    """

    def __init__(
        self,
        max_rows_per_language: int | None = None,
        batch_size: int = EMBEDDING_BATCH_SIZE,
    ):
        self.max_rows_per_language = max_rows_per_language
        self.batch_size = batch_size

        logger.info("=" * 70)
        logger.info("INITIALIZING VAANIRAG INGESTION RUNNER")
        logger.info("=" * 70)

        self.embedder = BGEM3Embedder()

        self.store = EmbeddingBatchStore()

        self.processor = BatchProcessor(
            embedder=self.embedder,
            store=self.store,
        )

    # ============================================================
    # CHUNK COLLECTION
    # ============================================================

    def collect_chunks(self):
        """
        Collects passages and converts them into chunks.

        Also tracks statistics separately by language.
        """

        logger.info(
            "Starting passage → chunk stage."
        )

        chunks = []

        stats = {
            "rows": {
                "hi": self.max_rows_per_language or 0,
                "mr": self.max_rows_per_language or 0,
            },
            "passages": {
                "en": 0,
                "hi": 0,
                "mr": 0,
            },
            "chunks": {
                "en": 0,
                "hi": 0,
                "mr": 0,
            },
        }

        # --------------------------------------------------------
        # IMPORTANT:
        #
        # stream_all_passages() yields:
        #
        #   en
        #   hi
        #   mr
        #
        # but does not currently expose row counters.
        #
        # Therefore we accurately count passages/chunks here,
        # while row counts remain the configured limits.
        # --------------------------------------------------------

        passages = stream_all_passages(
            max_rows_per_language=self.max_rows_per_language,
            batch_size=2,
        )

        for passage in passages:

            language = passage.language

            if language not in stats["passages"]:
                stats["passages"][language] = 0

            stats["passages"][language] += 1

            passage_chunks = chunk_passage(
                passage,
                strategy=CHUNKING_STRATEGY,
            )

            for chunk in passage_chunks:

                chunks.append(chunk)

                if chunk.language not in stats["chunks"]:
                    stats["chunks"][chunk.language] = 0

                stats["chunks"][chunk.language] += 1

        logger.info(
            "Chunk collection complete. "
            f"Chunks={len(chunks)}"
        )

        logger.info(
            f"Passages by language: "
            f"{stats['passages']}"
        )

        logger.info(
            f"Chunks by language: "
            f"{stats['chunks']}"
        )

        return chunks, stats

    # ============================================================
    # CHECKPOINT HELPERS
    # ============================================================

    def save_running_checkpoint(
        self,
        completed_batches,
        stats,
        last_batch_id,
        last_vector_count,
        status="running",
    ):
        """
        Saves the current production checkpoint.
        """

        save_checkpoint(
            dataset_name="msmarco-xi-local",

            languages=[
                "en",
                "hi",
                "mr",
            ],

            chunking_strategy=CHUNKING_STRATEGY,

            embedding_model=EMBEDDING_MODEL,

            embedding_dimension=1024,

            rows_processed={
                "hi": stats["rows"]["hi"],
                "mr": stats["rows"]["mr"],
            },

            passages_processed={
                "en": stats["passages"]["en"],
                "hi": stats["passages"]["hi"],
                "mr": stats["passages"]["mr"],
            },

            chunks_processed={
                "en": stats["chunks"]["en"],
                "hi": stats["chunks"]["hi"],
                "mr": stats["chunks"]["mr"],
            },

            vectors_uploaded={
                "en": 0,
                "hi": 0,
                "mr": 0,
            },

            last_successful_batch={
                "batch_id": last_batch_id,
                "vector_count": last_vector_count,
            },

            completed_batches=completed_batches,

            status=status,

            run_id="local_ingestion",
        )

    # ============================================================
    # MAIN RUNNER
    # ============================================================

    def run(self):

        logger.info("=" * 70)
        logger.info("STARTING VAANIRAG INGESTION")
        logger.info("=" * 70)

        # --------------------------------------------------------
        # Load previous checkpoint
        # --------------------------------------------------------

        checkpoint = load_checkpoint()

        if checkpoint:

            completed_batches = set(
                checkpoint.get(
                    "completed_batches",
                    [],
                )
            )

            logger.info(
                f"Previous checkpoint detected. "
                f"Completed batches="
                f"{len(completed_batches)}"
            )

        else:

            completed_batches = set()

            logger.info(
                "No previous checkpoint found. "
                "Starting fresh."
            )

        # --------------------------------------------------------
        # Collect chunks
        # --------------------------------------------------------

        chunks, stats = self.collect_chunks()

        if not chunks:

            logger.warning(
                "No chunks were produced. "
                "Nothing to process."
            )

            return

        # --------------------------------------------------------
        # Create batches
        # --------------------------------------------------------

        batches = []

        for start in range(
            0,
            len(chunks),
            self.batch_size,
        ):

            batch = chunks[
                start:start + self.batch_size
            ]

            batch_number = (
                start // self.batch_size
            ) + 1

            batch_id = (
                f"ingestion_batch_"
                f"{batch_number:06d}"
            )

            batches.append(
                (
                    batch_id,
                    batch,
                )
            )

        logger.info(
            f"Total chunks : {len(chunks)}"
        )

        logger.info(
            f"Total batches: {len(batches)}"
        )

        # --------------------------------------------------------
        # Process batches
        # --------------------------------------------------------

        completed_batches_list = list(
            completed_batches
        )

        total_new_vectors = 0

        last_successful_batch = None
        last_successful_vector_count = 0

        for batch_id, batch_chunks in batches:

            # ----------------------------------------------------
            # Resume logic
            # ----------------------------------------------------

            if batch_id in completed_batches:

                logger.info(
                    f"SKIP {batch_id} "
                    f"(already completed)"
                )

                continue

            logger.info("=" * 70)

            logger.info(
                f"PROCESSING {batch_id}"
            )

            logger.info(
                f"Chunks in batch: "
                f"{len(batch_chunks)}"
            )

            # ----------------------------------------------------
            # Process batch
            #
            # If this throws an exception:
            #
            #   - batch is NOT marked completed
            #   - checkpoint is NOT advanced
            #
            # Therefore restart will retry this batch.
            # ----------------------------------------------------

            result = self.processor.process_batch(
                chunks=batch_chunks,
                batch_id=batch_id,
            )

            vector_count = result["vector_count"]

            total_new_vectors += vector_count

            logger.info(
                f"{batch_id} completed. "
                f"Vectors={vector_count}"
            )

            # ----------------------------------------------------
            # Mark successful
            # ----------------------------------------------------

            completed_batches_list.append(
                batch_id
            )

            last_successful_batch = batch_id
            last_successful_vector_count = vector_count

            # ----------------------------------------------------
            # Save checkpoint AFTER successful persistence
            # ----------------------------------------------------

            self.save_running_checkpoint(
                completed_batches=completed_batches_list,
                stats=stats,
                last_batch_id=batch_id,
                last_vector_count=vector_count,
                status="running",
            )

        # --------------------------------------------------------
        # Determine final last batch
        # --------------------------------------------------------

        if last_successful_batch is None:

            if completed_batches_list:

                last_successful_batch = (
                    completed_batches_list[-1]
                )

                # If everything was already completed,
                # read its stored batch count.

                try:

                    last_successful_vector_count = (
                        self.store.count_records(
                            last_successful_batch
                        )
                    )

                except Exception:

                    last_successful_vector_count = 0

        # --------------------------------------------------------
        # FINAL CHECKPOINT
        # --------------------------------------------------------

        self.save_running_checkpoint(
            completed_batches=completed_batches_list,
            stats=stats,
            last_batch_id=last_successful_batch,
            last_vector_count=last_successful_vector_count,
            status="completed",
        )

        # --------------------------------------------------------
        # FINAL SUMMARY
        # --------------------------------------------------------

        logger.info("=" * 70)
        logger.info("VAANIRAG INGESTION COMPLETE")
        logger.info("=" * 70)

        logger.info(
            f"Passages by language: "
            f"{stats['passages']}"
        )

        logger.info(
            f"Chunks by language: "
            f"{stats['chunks']}"
        )

        logger.info(
            f"Total chunks: "
            f"{len(chunks)}"
        )

        logger.info(
            f"New vectors: "
            f"{total_new_vectors}"
        )

        logger.info(
            f"Completed batches: "
            f"{len(completed_batches_list)}"
        )