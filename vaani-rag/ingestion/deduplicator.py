import sqlite3
import os
from typing import Dict, Any
from ingestion.schemas import Passage
from ingestion.logging_config import logger
from ingestion.config import OUTPUT_DIR

class Deduplicator:
    """
    Tracks seen passage text hashes to perform global and intra-batch deduplication.
    Ensures identical passages (especially English text extracted from multiple Indic config records)
    are only stored once. Supports both in-memory and SQLite-backed deduplication.
    """
    def __init__(self, use_sqlite: bool = False):
        self.raw_count = 0
        self.duplicate_count = 0
        self.use_sqlite = use_sqlite
        
        if self.use_sqlite:
            db_path = OUTPUT_DIR / "dedup.sqlite"
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            self.cursor.execute("CREATE TABLE IF NOT EXISTS hashes (hash TEXT PRIMARY KEY)")
            self.conn.commit()
            logger.info(f"Initialized SQLite deduplicator at {db_path}")
        else:
            self.seen_hashes = set()
            logger.info("Initialized in-memory deduplicator")

    def is_duplicate(self, passage: Passage) -> bool:
        """
        Registers a passage and checks if its hash has already been seen.
        """
        self.raw_count += 1
        h = passage.content_hash
        
        if self.use_sqlite:
            self.cursor.execute("SELECT 1 FROM hashes WHERE hash = ?", (h,))
            if self.cursor.fetchone():
                self.duplicate_count += 1
                return True
            self.cursor.execute("INSERT INTO hashes (hash) VALUES (?)", (h,))
            return False
        else:
            if h in self.seen_hashes:
                self.duplicate_count += 1
                return True
            
            self.seen_hashes.add(h)
            return False

    def commit(self):
        """Commits the SQLite transaction."""
        if self.use_sqlite:
            self.conn.commit()

    def get_stats(self) -> Dict[str, Any]:
        """
        Computes and returns deduplication metrics.
        """
        if self.use_sqlite:
            self.cursor.execute("SELECT COUNT(*) FROM hashes")
            unique_count = self.cursor.fetchone()[0]
        else:
            unique_count = len(self.seen_hashes)
            
        duplicate_percentage = (self.duplicate_count / self.raw_count * 100.0) if self.raw_count > 0 else 0.0
        
        return {
            "raw_passages": self.raw_count,
            "duplicates": self.duplicate_count,
            "unique_passages": unique_count,
            "duplicate_percentage": round(duplicate_percentage, 2)
        }

    def close(self):
        """Closes the database connection if open."""
        if self.use_sqlite and hasattr(self, 'conn') and self.conn:
            try:
                self.conn.close()
                logger.info("Closed SQLite deduplicator connection.")
            except Exception as e:
                logger.error(f"Error closing SQLite deduplicator: {e}")

