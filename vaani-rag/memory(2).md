# VaaniRAG — Project Memory

## 1. Project

**VaaniRAG — Multilingual Voice-Enabled Large-Scale RAG**

## 2. Current Status

The project is in the **offline ingestion validation / Google Colab setup stage**.

The ingestion code has been created and revised by the coding agent.

The current task is to verify the code in Google Colab before scaling ingestion or connecting the production vector index.

## 3. Confirmed Product Scope

Initial supported dataset languages:

```text
English
Hindi
Marathi
```

The hackathon dataset is:

```text
ai4bharat/MSMARCO-XI
```

The system is voice-enabled and must support text input as well.

## 4. Confirmed Architecture

### Offline

```text
Hugging Face
→ language filter
→ extraction
→ cleaning
→ deduplication
→ adaptive chunking
→ BGE-M3
→ validation
→ deterministic IDs
→ Pinecone
```

### Online

```text
Text / Voice
→ STT
→ query validation
→ query embedding
→ Pinecone retrieval
→ optional reranking
→ evidence check
→ LLM
→ grounding validation
→ answer + sources
→ optional TTS
```

## 5. Confirmed Technology Choices

### Embedding

`BAAI/bge-m3`

Used locally for embedding.

Expected vector dimension:

```text
1024
```

### Vector database

**Pinecone Cloud**

The ingestion pipeline uses the current `pinecone` Python package.

### GPU development

Google Colab with an NVIDIA T4 when available.

The notebook should not hard-fail merely because Colab provides a different compatible NVIDIA GPU.

### Voice-to-text

One of:

- Sarvam;
- ElevenLabs.

The final provider will be selected/configured for the live application.

### Backend

FastAPI + Python.

### Frontend

Next.js + TypeScript + Tailwind CSS.

### LLM

Fast hosted LLM, selected based on latency, multilingual quality, cost, and hackathon availability.

### TTS

Optional Indic-capable TTS.

## 6. Offline Pipeline Implementation Status

The coding agent has implemented/revised:

- streaming dataset processing;
- batch embedding/upload;
- SQLite deduplication for larger runs;
- checkpoint-aware pipeline;
- online memory-safe metrics;
- vector validation;
- deterministic language + SHA-256 IDs;
- adaptive chunking;
- long-passage routing to fixed-overlap chunking;
- Pinecone integration;
- Colab notebook;
- dataset inspection script;
- embedding test script;
- Pinecone validation script;
- ingestion benchmark script.

## 7. Recent Fixes

The latest agent report states:

- `pinecone-client` was replaced by `pinecone`;
- Colab notebook was rewritten for fresh-runtime reproducibility;
- embedding/upload batch size was set to 64;
- SQLite deduplication was added;
- the dangerous global chunk list was removed;
- metrics were made memory-safe;
- long passages no longer get silently truncated;
- deterministic vector IDs were added.

## 8. Current Test Status

Local syntax/import compilation passed:

```text
python -m compileall ingestion/
```

Local pytest is currently blocked by a Windows environment-level NumPy/PyTorch `blas_fpe_check` crash.

This is not yet evidence of a pipeline assertion failure.

The next test environment is Google Colab/Linux.

## 9. Current Colab Status

A Colab attempt has encountered two setup problems:

### GPU check

The notebook contained an overly strict assertion requiring the GPU name to contain `T4`.

The diagnostic should instead verify:

```text
CUDA available
+
NVIDIA GPU name
```

A compatible non-T4 GPU should not automatically be rejected.

### GitHub clone

The notebook attempted to clone the repository but failed with:

```text
fatal: could not read Username for 'https://github.com'
```

The likely cause is a private/incorrect repository URL or missing GitHub authentication.

The next action is to inspect and fix the notebook's `git clone` cell before running ingestion.

## 10. Current Immediate Task

Do not run full ingestion.

First complete:

1. Fix GitHub clone in Colab.
2. Confirm repository directory.
3. Install requirements.
4. Verify CUDA/GPU.
5. Run:
   ```text
   python scripts/inspect_dataset.py
   ```
6. Run:
   ```text
   python scripts/test_embedding.py
   ```
7. Run the safe dry run:
   ```text
   python -m ingestion.pipeline --languages en,hi,mr --max-rows 100 --strategy adaptive --dry-run
   ```

Do not upload to Pinecone during the first dry run.

## 11. Dry-Run Safety

Initial processing limit:

```text
100 rows per language
```

Pinecone upload must be disabled for this test.

Only after the output is inspected should the pipeline move to a small Pinecone proof of concept.

## 12. Current Chunking Decision

Available strategies:

```text
original
sentence
fixed_overlap
semantic
adaptive
```

Default:

```text
adaptive
```

Adaptive routing should prefer:

```text
short  → original
medium → sentence-aware
long   → fixed-overlap
```

Semantic chunking remains experimental unless benchmark results justify it.

## 13. Current Vector ID Decision

Use:

```text
<language>_<sha256(chunk_text)>
```

This provides deterministic IDs and avoids using dataset row indexes as vector IDs.

## 14. Important Conceptual Decisions

### Offline processing

Offline processing happens when building/updating the knowledge index.

It does not happen when:

- a new user opens the application;
- an old user logs in;
- a user asks a normal query.

### Embeddings

An embedding model converts text into a numerical vector representing semantic information.

The vector database stores those vectors and uses approximate nearest-neighbor search to find chunks similar to the user's query vector.

### LLM

The LLM does not search the entire dataset.

It receives:

```text
user question
+
retrieved evidence
```

and generates a grounded answer.

### Hallucination

A hallucination occurs when the model generates unsupported or incorrect information, especially information not supported by retrieved evidence.

VaaniRAG should reduce this risk through:

- retrieval;
- evidence sufficiency checks;
- strict prompts;
- structured output;
- grounding validation;
- safe fallback.

### Harness

The harness is the orchestration layer around the models and tools.

It is responsible for:

- validation;
- sequencing;
- retries;
- timeouts;
- structured outputs;
- failure recovery;
- grounding checks;
- safe fallbacks.

It is broader than a simple safety check.

## 15. Storage Decision

Use separate responsibilities:

```text
Hugging Face / external storage
→ raw dataset

Pinecone
→ vectors + searchable chunk metadata

SQLite
→ ingestion dedup/checkpoint state

Optional PostgreSQL
→ users/sessions/query history if required
```

Do not store the entire RAG vector collection in PostgreSQL.

## 16. Files Currently Expected

```text
docs/
├── prd.md
├── architecture.md
├── rules.md
├── phases.md
├── design.md
└── memory.md
```

## 17. Hackathon Constraints

Launch:

**August 13, 2026**

Deadline:

**August 22, 2026, 11:59 PM**

Required:

- GitHub repository;
- live working link;
- 90-second process/team video;
- demo video;
- Instagram/X/LinkedIn promotion by every team member;
- `#RAGInGoa` on every required post.

## 18. Next Milestones

```text
CURRENT
Colab setup
   ↓
Dataset inspection
   ↓
BGE-M3 verification
   ↓
100-row dry run
   ↓
Small Pinecone proof
   ↓
Retrieval benchmark
   ↓
Scale ingestion
   ↓
Backend harness
   ↓
Guardrails
   ↓
Voice
   ↓
Frontend
   ↓
Latency benchmark
   ↓
Deployment
   ↓
Demo
   ↓
Submission
```

## 19. Update Rule

When a meaningful decision or milestone changes, append:

```text
## YYYY-MM-DD — Update

### Completed
- ...

### Current Work
- ...

### Decisions
- ...

### Problems
- ...

### Next
- ...
```

Do not erase historical decisions unless they were intentionally changed.
