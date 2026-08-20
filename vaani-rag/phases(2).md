# VaaniRAG — Project Phases

## Phase 0 — Requirements + Dataset Inspection

### Goal

Understand the actual MS MARCO-XI structure before full ingestion.

### Tasks

- Inspect English, Hindi, and Marathi configurations.
- Confirm columns and nested passage structure.
- Confirm what one row represents.
- Confirm how `English_passages` and `Translated_passages` are populated.
- Determine which passages are searchable.
- Determine which fields become metadata.
- Estimate selected-language record counts.
- Build a small representative sample.

### Exit criteria

We can explain:

```text
one dataset row
→ passages
→ chunks
→ vectors
```

Do not start full ingestion before this is complete.

---

## Phase 1 — Repository + Environment

### Goal

Create a reproducible development environment.

### Tasks

- GitHub repository.
- `.gitignore`.
- `.env.example`.
- requirements.
- ingestion package.
- backend skeleton.
- frontend skeleton.
- tests.
- Colab notebook.

### Exit criteria

Fresh Colab can clone the repo and install dependencies.

---

## Phase 2 — Embedding + Chunking Proof

### Goal

Prove that the local embedding pipeline works.

### Tasks

- Load BGE-M3.
- Verify CUDA/T4 when available.
- Test English/Hindi/Marathi.
- Verify 1024-dimensional vectors.
- Validate NaN/Inf/shape.
- Benchmark batch sizes.
- Run all chunking strategies on a sample.

### Exit criteria

A small sample can be:

```text
dataset
→ chunk
→ BGE-M3
→ valid vectors
```

---

## Phase 3 — Tiny RAG Proof of Concept

### Goal

Prove retrieval before scaling.

### Dataset

Approximately 1,000 records or a similarly small representative subset.

### Pipeline

```text
records
→ prepare
→ chunks
→ BGE-M3
→ Pinecone
→ query embedding
→ vector search
→ evidence
```

### Exit criteria

Known questions return relevant evidence.

---

## Phase 4 — Scalable Offline Ingestion

### Goal

Make ingestion safe for millions of records.

### Tasks

- Streaming reader.
- Language filtering.
- Cleaning.
- Deduplication.
- Adaptive chunking.
- Batched BGE-M3 embedding.
- Vector validation.
- Batched Pinecone upsert.
- SQLite deduplication.
- Checkpointing.
- Retry logic.
- Progress/throughput metrics.

### Scale tests

```text
1K
→ 10K
→ 100K
→ larger benchmark
→ final selected corpus
```

Never jump directly from 100 rows to the entire corpus.

---

## Phase 5 — Vector Retrieval Optimization

### Goal

Minimize retrieval latency.

### Tasks

- Tune Pinecone index configuration.
- Tune Top-K.
- Test language filters.
- Measure query embedding.
- Measure Pinecone search.
- Test whether reranking helps.
- Test whether hybrid retrieval helps.

### Exit criteria

A measured retrieval configuration is selected.

---

## Phase 6 — Retrieval Evaluation

### Goal

Prove retrieval quality.

### Metrics

- Recall@5.
- Recall@10.
- MRR.
- NDCG where appropriate.
- English performance.
- Hindi performance.
- Marathi performance.

Use known relevant passages from the dataset/evaluation sample.

---

## Phase 7 — Hybrid Retrieval (Optional)

### Goal

Improve exact-name/entity/keyword retrieval if dense retrieval misses them.

### Decision

Only keep hybrid retrieval if:

```text
quality improves
AND
latency remains acceptable
```

Do not add it just because it is a common RAG feature.

---

## Phase 8 — Reranking (Optional)

### Goal

Improve Top-K precision.

Pipeline:

```text
Pinecone
→ Top 20
→ reranker
→ Top 5
```

Only keep the reranker if the measured quality gain justifies its latency.

---

## Phase 9 — RAG Generation

### Goal

Produce grounded answers.

### Tasks

- Context construction.
- Grounded system prompt.
- Structured LLM output.
- Source mapping.
- Insufficient-evidence behavior.
- Hallucination/grounding check.
- Bounded retry.
- Streaming.

### Exit criteria

The system answers from retrieved evidence and refuses/qualifies when evidence is insufficient.

---

## Phase 10 — Harness + Guardrails

### Goal

Turn individual model calls into a robust application workflow.

### Tasks

- Request validation.
- STT orchestration.
- Retrieval orchestration.
- Retry policy.
- Timeout policy.
- Structured output validation.
- Grounding validation.
- Off-topic handling.
- Unsafe-input handling.
- Failure recovery.

### Exit criteria

A failure in one component produces a controlled result rather than a crash or fabricated answer.

---

## Phase 11 — Voice

### Goal

Support voice end-to-end.

### Tasks

- Microphone capture.
- Sarvam or ElevenLabs STT.
- Display transcribed query.
- Feed transcript into normal RAG path.
- Optional TTS.

### Exit criteria

```text
voice
→ transcript
→ retrieval
→ grounded answer
```

works reliably.

---

## Phase 12 — Frontend

### Goal

Create the judge-facing experience.

### UI

- Language selector.
- Text input.
- Voice button.
- Transcript display.
- Answer.
- Evidence/source cards.
- Retrieval latency.
- End-to-end telemetry.
- Loading state.
- Error state.

---

## Phase 13 — Full Benchmark

### Goal

Produce defensible performance numbers.

Run a reasonable query set rather than one request.

Record:

```text
STT
query embedding
Pinecone retrieval
reranking
LLM
TTS
end-to-end
```

Report:

```text
P50
P70
P100
```

Also report retrieval quality.

Do not mix component numbers without clearly labeling them.

---

## Phase 14 — Final Hardening

### Tasks

- Test empty input.
- Test unsupported language.
- Test no-result retrieval.
- Test unsafe/off-topic input.
- Test STT failure.
- Test vector DB timeout.
- Test LLM timeout.
- Test invalid LLM output.
- Test grounding failure.
- Test Colab restart/resume.
- Remove debug output.
- Verify secrets are absent from Git.

---

## Phase 15 — Demo + Submission

### Demo sequence

1. Open application.
2. Ask English text question.
3. Show retrieved evidence.
4. Ask Hindi or Marathi question.
5. Demonstrate voice input.
6. Show transcript.
7. Show grounded answer.
8. Show evidence.
9. Show latency telemetry.
10. Explain offline indexing architecture.

### Submission checklist

- GitHub link.
- Live working link.
- 90-second team/process video.
- End-to-end demo video.
- Required Instagram post.
- Required X post.
- Required LinkedIn post.
- Every team member posts as required.
- Every post includes `#RAGInGoa`.

Deadline:

**August 22, 2026, 11:59 PM**
