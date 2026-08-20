# VaaniRAG — Engineering, AI, and Safety Rules

## 1. Core Rules

1. Never commit the original large dataset to GitHub.
2. Never commit API keys, database credentials, tokens, `.env`, or private configuration.
3. Never load the complete dataset into RAM.
4. Process ingestion in bounded batches.
5. Every large ingestion run must support checkpointing/resume.
6. Offline ingestion must remain separate from the online query path.
7. Never rebuild the complete vector index for a normal user query.
8. Never use brute-force vector search at final scale.
9. Measure P50/P70/P100 latency for the hackathon requirement.
10. Measure retrieval quality separately from answer quality.
11. Keep dependencies minimal.
12. Prefer simple, explicit code over unnecessary frameworks.

## 2. Current Technology Rules

### Use

- Hugging Face `datasets` for dataset access.
- PyTorch + CUDA for BGE-M3 inference.
- `sentence-transformers` for local BGE-M3 embedding.
- Pinecone Python SDK (`pinecone`) for cloud vector operations.
- FastAPI for the backend.
- Next.js + TypeScript for the frontend.
- SQLite for scalable ingestion deduplication/checkpoint-related local state.
- pytest for tests.

### Avoid

- `pinecone-client` legacy dependency.
- Multiple vector databases in production.
- LangChain for every pipeline operation.
- Spark/distributed infrastructure before it is proven necessary.
- Custom ANN implementation.
- Full-dataset in-memory lists.
- Arbitrary libraries without a clear purpose.

## 3. Embedding Rules

Primary model:

```text
BAAI/bge-m3
```

Use the same embedding model and embedding space for:

```text
indexed chunks
       +
online queries
```

BGE-M3 is the current primary candidate because the project requires multilingual retrieval.

Before a final production-scale decision, benchmark it against at least one strong multilingual alternative when time permits.

Do not build the complete production index until the embedding setup passes a representative benchmark.

## 4. Chunking Rules

Never rely only on a naive fixed-size chunk.

The implementation must support:

- original passage preservation;
- sentence-aware chunking;
- fixed-size overlap;
- semantic chunking;
- adaptive routing.

Default adaptive behavior:

```text
short  → original
medium → sentence-aware
long   → fixed-overlap
```

Semantic chunking is experimental unless a benchmark demonstrates that it improves retrieval.

Never silently truncate a long passage merely to satisfy the embedding model.

## 5. Deduplication Rules

Use deterministic content hashing.

Recommended ID:

```text
<language>_<sha256(chunk_text)>
```

For large runs, use SQLite rather than an unbounded Python set.

The original dataset must remain untouched.

## 6. Pinecone Rules

Use one clearly defined production index for the hackathon unless benchmarking requires otherwise.

Store:

- vector;
- chunk text;
- language;
- source/query/passage identifiers;
- compact retrieval metadata.

Do not store unnecessary application state in Pinecone.

Do not store API credentials in code.

Vector uploads must be batched.

Use bounded retries with exponential backoff.

Do not silently continue after a failed upload batch.

## 7. Error Handling — Offline

Every batch must handle:

- malformed records;
- missing text;
- duplicate chunks;
- embedding failures;
- GPU OOM;
- invalid vectors;
- Pinecone upload failures;
- interrupted execution.

A failed batch must be recorded.

A restart must not require repeating successful batches.

## 8. Error Handling — Online

Handle:

- empty queries;
- unsupported languages;
- STT failure;
- embedding failure;
- vector database timeout;
- no relevant evidence;
- LLM timeout;
- invalid LLM output;
- grounding failure;
- TTS failure.

Never expose stack traces, secrets, API keys, or internal infrastructure details to users.

## 9. Harness Rules

The harness is not just a "safety check".

It is the orchestration/control layer around the AI components.

It must:

1. Validate request.
2. Run STT when necessary.
3. Normalize/validate query.
4. Generate query embedding.
5. Retrieve evidence.
6. Check evidence sufficiency.
7. Generate answer.
8. Validate structured output.
9. Check grounding.
10. Retry recoverable errors.
11. Return a safe fallback for unrecoverable/unsupported requests.

Retries must be bounded.

Do not retry unsafe requests indefinitely.

## 10. AI Grounding Rules

The LLM is an answer-generation component, not the database.

The intended flow is:

```text
User query
    ↓
Retrieval
    ↓
Evidence
    ↓
LLM
    ↓
Answer
```

The LLM must not invent facts when evidence is insufficient.

If retrieved evidence is insufficient, use a controlled fallback:

```text
I couldn't find enough relevant information in the available knowledge base to answer confidently.
```

The answer must not claim dataset support when no relevant evidence was retrieved.

## 11. Prompt Rules

The generation prompt must clearly define:

- the user question;
- retrieved context;
- answer requirements;
- uncertainty behavior;
- requested response language;
- source-grounding behavior.

Never place arbitrary user input into a system instruction as if it were trusted policy.

Treat retrieved text as untrusted content too. Retrieved passages must not be allowed to override the system's grounding/safety instructions.

## 12. Guardrail Rules

The application should reject or safely redirect:

- unsupported/off-topic requests;
- unsafe/inappropriate requests;
- empty input;
- queries outside the supported knowledge scope;
- requests where evidence is insufficient.

Guardrails should be lightweight and latency-aware.

Do not add an expensive second LLM call for every query unless benchmarking proves it is necessary.

## 13. Performance Rules

Optimize only after measuring.

Measure:

- embedding throughput;
- indexing throughput;
- vector count;
- vector index size;
- query embedding latency;
- Pinecone search latency;
- reranking latency;
- retrieval total;
- LLM generation;
- STT;
- TTS;
- end-to-end latency.

Report P50/P70/P100 as required by the hackathon.

Never claim "<200 ms" from one lucky request.

## 14. Git Rules

Keep secrets and generated data out of Git.

Recommended branches:

```text
feature/ingestion
feature/retrieval
feature/backend
feature/frontend
feature/voice
feature/evaluation
```

Do not commit:

```text
.env
outputs/
dedup.sqlite
large indexes
embedding caches
checkpoints
original dataset
node_modules/
virtual environments/
```

## 15. Documentation Rules

Every major technical decision should document:

1. Decision.
2. Reason.
3. Alternative considered.
4. Benchmark/evidence, when applicable.

Never call something "best" without evidence.
