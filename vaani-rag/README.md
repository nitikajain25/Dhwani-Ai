# DhawaniRAG Offline Ingestion Pipeline

This directory contains the robust, resumable, and benchmarkable offline multilingual data ingestion pipeline for the **DhawaniRAG** application. 

The pipeline extracts Hindi, Marathi, and English passages from the AI4Bharat `MSMARCO-XI` dataset, cleanses and deduplicates them, segments them using pluggable chunking strategies, embeds them locally on a T4 GPU using `BAAI/bge-m3`, validates the vectors, and uploads them to a serverless Pinecone index categorized by language namespace.

---

## Conceptual Architecture

```mermaid
graph TD
    subgraph OFFLINE PIPELINE (This Module)
        HF[Hugging Face: ai4bharat/MSMARCO-XI]
        Extract[Passage Extraction]
        Clean[Deterministic Cleaning]
        Dedup[SHA-256 Deduplication]
        Chunk[Chunking strategies: Adaptive, etc.]
        Embed[Local BGE-M3 Embedder: T4 GPU]
        Val[Strict Vector Validation]
        Pinecone[(Pinecone Index: vaani-rag)]
        
        HF --> Extract
        Extract --> Clean
        Clean --> Dedup
        Dedup --> Chunk
        Chunk --> Embed
        Embed --> Val
        Val -->|Upload| Pinecone
    end

    subgraph RUNTIME APPLICATION (Built Later)
        Voice[User Voice Input]
        STT[Sarvam STT]
        Query[Text Query]
        EmbedQ[Local BGE-M3 Embedder]
        Retrieval[Pinecone Namespace Retrieval]
        LLM[Groq LLM Generation]
        Answer[Voice/Text Output]
        
        Voice --> STT
        STT --> Query
        Query --> EmbedQ
        EmbedQ --> Retrieval
        Retrieval --> LLM
        Pinecone -.->|Search Context| Retrieval
        LLM --> Answer
    end
```

---

## Technical Specifications

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Dataset Source** | Hugging Face `ai4bharat/MSMARCO-XI` | High-quality Indic translated MS MARCO dataset. |
| **Languages** | English (`en`), Hindi (`hi`), Marathi (`mr`) | Targeted multilingual corpus configuration. |
| **Primary Index Unit** | Passages (not Queries/Answers) | Passage text represents the core ground-truth knowledge source. |
| **Embedding Model** | `BAAI/bge-m3` via `sentence-transformers` | Runs locally, supports multilingual semantics, outputs 1024-dim dense vectors. |
| **Vector DB** | Pinecone Cloud | Uses a single index `vaani-rag` with namespaces `en`, `hi`, `mr`. |
| **Type Safety** | `pydantic` | Rigorous schema verification at trust boundaries. |

---

## Chunking Strategies

The pipeline implements five pluggable chunking strategies matching the same interface:
1. **`ORIGINAL_PASSAGE`**: Preserves the passage as a single retrieval unit. Safe max limit: 8192 tokens.
2. **`SENTENCE_AWARE`**: Splits on sentence boundaries (multilingual safe: `.!?।॥`) and groups them into target token sizes (default: 384 tokens), preventing broken sentences.
3. **`FIXED_OVERLAP`**: standard sliding token window (384 size, 64 overlap). Falls back to word-level estimation if offline.
4. **`SEMANTIC`**: Splits into sentences, embeds all sentences in a single batched call, calculates cosine similarity between adjacent sentences, and cuts chunks where similarity is below threshold.
5. **`ADAPTIVE`** (Default Production Candidate): Dynamically selects chunking based on passage length (Short -> Original, Medium -> Sentence-Aware, Long -> Fixed Overlap, Very Long -> Semantic).

---

## Key Features

### 1. Resumability & Memory Safety
Ingestion works in a two-pass stream:
- **Pass 1**: Reads Hugging Face stream, extracts, cleans, deduplicates, and chunks. Saves chunk outputs to local JSONL files.
- **Pass 2**: Reads chunk files in batches, generates embeddings, validates, and uploads.
This approach prevents loading millions of records or dense vectors into RAM. If Colab disconnects, the checkpoint tracks processed row indexes per language. On restart, it fast-forwards using `skip(N)`.

### 2. Cost Safety Safeguards
Pinecone cloud vector uploads can incur costs. By default:
- `--dry-run` is `True` (runs local extraction, deduplication, embedding, and validation, but skips Pinecone upload).
- Capped at 100 rows per language.
- Scaling checks: If total vectors to upload exceed **100,000**, the pipeline halts and requires `CONFIRM_LARGE_UPLOAD=True` in `.env` to prevent accidental cost overruns.

---

## Project Structure

```
vaani-rag/
│
├── ingestion/
│   ├── __init__.py
│   ├── config.py           # dotenv configuration loading
│   ├── schemas.py          # Passage, Chunk, and Vector Pydantic schemas
│   ├── logging_config.py   # Console and file logging configuration
│   ├── dataset_loader.py   # Streaming dataset parser
│   ├── passage_extractor.py# Passage extraction adaptor
│   ├── cleaner.py          # Deterministic unicode-safe cleaner
│   ├── deduplicator.py     # SHA-256 exact matching deduplicator
│   ├── chunker.py          # Chunker routing entry point
│   ├── strategies/         # Pluggable chunking strategies
│   ├── embedder.py         # Local BGE-M3 embedder wrapper
│   ├── validator.py        # 1024-dim, NaN, Inf, and normalization validation
│   ├── vector_builder.py   # Compiles Pinecone payload records
│   ├── pinecone_client.py  # Pinecone index initializer
│   ├── pinecone_uploader.py# Backoff retry batch upsert
│   ├── checkpoint.py       # Pipeline progress save/load
│   └── pipeline.py         # End-to-end flow orchestrator
│
├── scripts/
│   ├── inspect_dataset.py  # Prints dataset columns and stats
│   ├── test_embedding.py   # Measures local embedding throughput
│   ├── validate_pinecone.py# Verifies connection and metadata uploads
│   └── benchmark_ingestion.py# Compares all 5 chunking strategies
│
├── tests/                  # Offline mock unit tests
└── notebooks/
    └── msmarco_xi_ingestion_colab.ipynb  # Google Colab user interface
```

---

## Local Setup & Quickstart

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Configuration
Copy `.env.example` to `.env` and fill in credentials:
```bash
cp .env.example .env
```
Default parameters inside `.env` are configured to execute in safe dry-run mode.

### 3. Run Verification Tests
Verify all mock units are green:
```bash
pytest tests/
```

### 4. Run Dataset Schema Inspector
```bash
python scripts/inspect_dataset.py
```

### 5. Run Embedding Test
```bash
python scripts/test_embedding.py
```

### 6. Run Ingestion Pipeline (Dry Run)
```bash
python -m ingestion.pipeline --languages en,hi,mr --max-rows 100 --strategy adaptive --dry-run
```

---

## Troubleshooting

- **CUDA Out of Memory (OOM)**: The embedder will log OOM warnings, halve the batch size, and retry automatically. If it still crashes, lower `EMBEDDING_BATCH_SIZE` to 8 or 4 in your `.env`.
- **Pinecone Rate Limiting (429)**: The uploader uses exponential backoff. If uploads timeout, the script will retry the failed batch up to 5 times.
- **English Passages Duplication**: English passages are extracted from the source configurations of Hindi and Marathi records. The Deduplicator globally ensures no duplicate English content is embedded or stored.
