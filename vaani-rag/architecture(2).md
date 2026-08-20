# VaaniRAG — Application Flow & Architecture

## 1. Architecture Principle

VaaniRAG is divided into two fundamentally different systems:

```text
                    VaaniRAG
                       |
             +---------+---------+
             |                   |
             v                   v
        OFFLINE PHASE       ONLINE PHASE
        Build knowledge     Answer users
             |                   |
             v                   v
       Vector database      Retrieval + LLM
```

The offline pipeline is run when the dataset/index is created or updated. It is **not** run when a normal user logs in.

## 2. Offline Architecture

```text
Hugging Face MS MARCO-XI
        |
        v
Streaming Dataset Loader
        |
        v
Language Filter
(en / hi / mr)
        |
        v
Passage Extraction
        |
        v
Text Cleaning + Validation
        |
        v
Deduplication
(SQLite for large runs)
        |
        v
Chunking Strategy Router
        |
        +--> Original
        +--> Sentence-aware
        +--> Fixed-overlap
        +--> Semantic (experimental)
        |
        v
Adaptive Strategy
        |
        v
BGE-M3 Embedding
(local GPU)
        |
        v
Vector Validation
        |
        v
Deterministic Vector IDs
        |
        v
Pinecone Cloud
        |
        v
ANN Vector Index
        |
        v
Searchable Knowledge Base
```

### Important offline rule

Chunking and embedding are expensive preprocessing operations.

They happen:

- during initial index creation;
- when the dataset version changes;
- when the chunking/embedding configuration changes and a new index is intentionally built.

They do **not** happen for every new user or login.

## 3. Online Architecture

```text
Browser
  |
  +---------------- Text ----------------+
  |                                      |
  +--- Voice --> STT --------------------+
                         |
                         v
                  Query Text
                         |
                         v
                Input Validation
                         |
                         v
              Language Handling
                         |
                         v
               Query Embedding
                         |
                         v
               Pinecone Search
                         |
                         v
              Metadata Filtering
                         |
                         v
                   Top-K
                         |
                         v
             Optional Reranking
                         |
                         v
               Evidence Check
                         |
                +--------+--------+
                |                 |
             enough?           not enough
                |                 |
                v                 v
               LLM          Safe fallback
                |
                v
         Grounding Validator
                |
         +------+------+
         |             |
       valid        unsupported
         |             |
         v             v
      Answer       Safe fallback /
                    regeneration
         |
         +----> Sources
         |
         +----> Optional TTS
         |
         v
       Browser
```

## 4. Harness Architecture

The online request should not be a single `prompt -> answer` call.

Use a controller/service similar to:

```text
Request
  ↓
validate_request()
  ↓
stt_if_needed()
  ↓
validate_query()
  ↓
embed_query()
  ↓
retrieve()
  ↓
check_evidence()
  ↓
generate_answer()
  ↓
validate_answer_schema()
  ↓
check_grounding()
  ↓
return_response()
```

Recoverable failures get bounded retries.

Non-recoverable failures return structured errors.

## 5. Recommended Technology Stack

| Layer | Choice | Purpose |
|---|---|---|
| Frontend | Next.js + TypeScript | Judge-facing web app |
| UI | Tailwind CSS | Fast consistent styling |
| Backend | FastAPI + Python | RAG API/orchestration |
| Data processing | Hugging Face Datasets + Python | Dataset streaming |
| Data utilities | PyArrow / Polars where useful | Efficient processing |
| Embeddings | `BAAI/bge-m3` | Multilingual dense vectors |
| Embedding runtime | PyTorch + CUDA | Local GPU embedding |
| Vector DB | Pinecone Cloud | Hosted vector storage/search |
| ANN | Pinecone-managed index | Approximate vector search |
| STT | Sarvam or ElevenLabs | Voice → text |
| LLM | Fast hosted LLM | Grounded answer generation |
| TTS | Optional Indic-capable provider | Text → speech |
| API streaming | SSE | Stream response/telemetry |
| Offline checkpoint state | SQLite + checkpoint files | Resumable ingestion |
| Tests | pytest | Unit/integration tests |
| Evaluation | Python scripts | Retrieval + latency benchmarks |
| Dev environment | Google Colab T4 for ingestion experiments | GPU processing |
| Deployment | Docker where useful | Reproducibility |

Do not add LangChain merely for orchestration. The harness can be implemented directly with small service modules.

## 6. Pinecone Vector Record

Conceptually:

```json
{
  "id": "hi_<sha256>",
  "values": [1024-dimensional BGE-M3 vector],
  "metadata": {
    "text": "searchable chunk",
    "language": "hi",
    "dataset": "MSMARCO-XI",
    "query_id": "1185869",
    "passage_id": "..."
  }
}
```

Keep metadata compact and flat.

The vector is for similarity search.

The metadata contains the evidence that the application sends to the LLM.

## 7. Deterministic IDs

Use:

```text
<language>_<sha256(chunk_text)>
```

Examples:

```text
en_abc123...
hi_def456...
mr_789abc...
```

Do not use row position as the primary vector ID.

Deterministic IDs make retries and resumed ingestion safer.

## 8. Chunking Architecture

The system must not depend on one naive fixed-size chunker.

Available strategies:

```text
Original
Sentence-aware
Fixed-overlap
Semantic
Adaptive
```

Initial production default:

```text
short passage
    → original

medium passage
    → sentence-aware

long passage
    → fixed-overlap
```

Semantic chunking is experimental and should be benchmarked before becoming part of the production adaptive path.

Oversized passages must not be silently truncated. They should be routed to safe fixed-overlap chunking.

## 9. Folder Structure

```text
vaani-rag/
│
├── ingestion/
│   ├── config.py
│   ├── schemas.py
│   ├── dataset_loader.py
│   ├── passage_extractor.py
│   ├── cleaner.py
│   ├── deduplicator.py
│   ├── chunker.py
│   ├── embedder.py
│   ├── validator.py
│   ├── vector_builder.py
│   ├── pinecone_client.py
│   ├── pinecone_uploader.py
│   ├── checkpoint.py
│   ├── metrics.py
│   ├── pipeline.py
│   └── strategies/
│       ├── original.py
│       ├── sentence.py
│       ├── fixed_overlap.py
│       ├── semantic.py
│       └── adaptive.py
│
├── backend/
│   └── app/
│       ├── api/
│       ├── services/
│       ├── schemas/
│       └── core/
│
├── frontend/
│   ├── app/
│   ├── components/
│   └── services/
│
├── scripts/
│   ├── inspect_dataset.py
│   ├── test_embedding.py
│   ├── validate_pinecone.py
│   └── benchmark_ingestion.py
│
├── tests/
│
├── notebooks/
│   └── msmarco_xi_ingestion_colab.ipynb
│
├── evaluation/
│   ├── datasets/
│   ├── scripts/
│   └── results/
│
├── outputs/
│   ├── checkpoints/
│   ├── logs/
│   └── dedup.sqlite
│
├── docs/
│   ├── prd.md
│   ├── architecture.md
│   ├── rules.md
│   ├── phases.md
│   ├── design.md
│   └── memory.md
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## 10. Storage Architecture

Use separate storage responsibilities.

```text
Raw dataset
    ↓
Hugging Face / external storage

Searchable chunks + embeddings
    ↓
Pinecone

Application users/sessions/history
    ↓
Optional PostgreSQL

Ingestion checkpoints/dedup state
    ↓
SQLite / local outputs
```

Do not put the full embedding collection in a normal application SQL database.

## 11. Google Colab Role

Google Colab is an **offline ingestion environment**, not the production application server.

Expected workflow:

```text
GitHub
  ↓
Colab
  ↓
T4 GPU
  ↓
Hugging Face streaming dataset
  ↓
BGE-M3
  ↓
Pinecone Cloud
```

Colab can be restarted without losing already-uploaded vectors because vector IDs are deterministic and ingestion is checkpointed.

## 12. Latency Architecture

Measure:

```text
STT
Query embedding
Pinecone search
Filtering
Reranking
LLM generation
TTS
End-to-end
```

The challenge target is <200 ms for the requested full pipeline. Internally, retrieval should be optimized and reported separately because STT, hosted LLM generation, and TTS can dominate end-to-end time.

Never report a fabricated or single best-case latency.

## 13. Offline-to-Online Boundary

Offline:

```text
Dataset
→ clean
→ deduplicate
→ chunk
→ embed
→ index
```

Online:

```text
Query
→ embed
→ retrieve
→ ground
→ generate
```

The user query must never trigger full corpus chunking or embedding.
