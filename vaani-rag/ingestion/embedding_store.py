import json
from pathlib import Path
from typing import List

from ingestion.config import EMBEDDINGS_DIR
from ingestion.schemas import VectorRecord
from ingestion.logging_config import logger


class EmbeddingBatchStore:
    """
    Persists embedding batches as JSONL files.

    One JSON object = one VectorRecord.
    One file = one completed embedding batch.
    """

    def __init__(self, output_dir: Path = EMBEDDINGS_DIR):
        self.output_dir = output_dir
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def batch_path(self, batch_id: str) -> Path:
        return self.output_dir / f"{batch_id}.jsonl"

    def exists(self, batch_id: str) -> bool:
        """
        Returns True if the batch file already exists.
        """
        return self.batch_path(batch_id).exists()

    def save_batch(
        self,
        batch_id: str,
        records: List[VectorRecord],
    ) -> Path:
        """
        Atomically writes a VectorRecord batch.

        The final batch file only appears after the complete
        temporary file has been written successfully.
        """

        if not records:
            raise ValueError(
                "Cannot save an empty embedding batch."
            )

        final_path = self.batch_path(batch_id)
        temp_path = final_path.with_suffix(".tmp")

        try:
            with open(
                temp_path,
                "w",
                encoding="utf-8",
            ) as f:

                for record in records:
                    f.write(
                        json.dumps(
                            record.model_dump(),
                            ensure_ascii=False,
                        )
                    )
                    f.write("\n")

                f.flush()

            # Atomic replacement.
            temp_path.replace(final_path)

            logger.info(
                f"Saved embedding batch '{batch_id}' "
                f"with {len(records)} records."
            )

            return final_path

        except Exception:
            if temp_path.exists():
                temp_path.unlink()

            raise

    def load_batch(
        self,
        batch_id: str,
    ) -> List[VectorRecord]:
        """
        Loads a previously persisted embedding batch.
        """

        path = self.batch_path(batch_id)

        if not path.exists():
            raise FileNotFoundError(
                f"Embedding batch not found: {path}"
            )

        records = []

        with open(
            path,
            "r",
            encoding="utf-8",
        ) as f:

            for line in f:
                line = line.strip()

                if not line:
                    continue

                data = json.loads(line)

                records.append(
                    VectorRecord.model_validate(data)
                )

        return records

    def count_records(
        self,
        batch_id: str,
    ) -> int:
        """
        Counts VectorRecords stored in a batch.
        """

        path = self.batch_path(batch_id)

        if not path.exists():
            return 0

        count = 0

        with open(
            path,
            "r",
            encoding="utf-8",
        ) as f:

            for line in f:
                if line.strip():
                    count += 1

        return count