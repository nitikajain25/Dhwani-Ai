# VaaniRAG — Project Requirements Document

## 1. Project Overview

**Project:** VaaniRAG — Multilingual Voice-Enabled Retrieval-Augmented Generation System

VaaniRAG is a hackathon project that lets a user ask a question by **voice or text**, retrieves relevant evidence from the AI4Bharat MS MARCO-XI dataset, and generates a grounded answer.

The core pipeline is:

```text
Voice / Text
    ↓
Speech-to-Text (voice only)
    ↓
Query validation + language handling
    ↓
Query embedding
    ↓
Vector retrieval
    ↓
Evidence / context selection
    ↓
Grounded LLM answer
    ↓
Optional Text-to-Speech
    ↓
User
```

The large dataset is processed **offline**. The online application must never re-chunk or re-index the entire corpus for a user query.

The challenge requires the system to demonstrate a practical large-scale multilingual RAG architecture, strong chunking/retrieval decisions, orchestration/harnessing, guardrails, and measured latency.

## 2. Dataset

Primary dataset:

- Hugging Face: `ai4bharat/MSMARCO-XI`
- MS MARCO translated into Indic languages.
- Dataset contains query, answer, query type, translation metadata, original English content, and passage lists.
- The exact searchable-record structure must be verified from the actual dataset before full ingestion.

### Initial language scope

For the hackathon build, the initial scope is:

- English (`en`)
- Hindi (`hi`)
- Marathi (`mr`)

This is an intentional scope reduction to make ingestion, benchmarking, and the live demo practical.

English handling must be based on the actual dataset structure. In the current ingestion design, English passages may be extracted from the `English_passages` fields contained in Hindi/Marathi records rather than downloading an unnecessary duplicate English configuration. This must be validated against the inspected dataset schema before production ingestion.

## 3. Target Users

### Primary users

- Students and general users asking factual questions.
- Users who prefer Hindi, Marathi, or English.
- Users who prefer speaking instead of typing.
- Hackathon judges evaluating retrieval quality, latency, architecture, and UX.

### Secondary users

- Developers/researchers interested in multilingual RAG.
- Evaluators inspecting evidence, benchmark metrics, and system behavior.

## 4. Core User Experience

A user should be able to:

1. Open the application.
2. Select a supported language or use automatic language handling.
3. Type a question or speak a question.
4. See the recognized text when voice input is used.
5. Receive a concise answer grounded in retrieved evidence.
6. Inspect the retrieved evidence/source snippets.
7. See useful latency telemetry.
8. Ask another question without restarting the application.

## 5. Functional Requirements

### FR-01 — Text Query

Accept natural-language text queries in English, Hindi, and Marathi.

### FR-02 — Voice Query

Accept microphone input and use the selected voice-to-text provider.

The hackathon permits **Sarvam or ElevenLabs** for speech-to-text. The implementation should keep the STT provider behind an interface so it can be changed without rewriting retrieval logic.

### FR-03 — Multilingual Retrieval

Use a multilingual embedding model for both indexed chunks and online queries.

Primary embedding candidate:

`BAAI/bge-m3`

The embedding model must be loaded locally for offline ingestion and may also be loaded locally for online query embedding if latency testing supports it.

### FR-04 — Retrieval

Retrieve semantically relevant chunks from the cloud vector database.

Initial retrieval mode:

- dense vector search;
- language metadata filtering;
- configurable Top-K.

Hybrid retrieval and reranking are optional optimizations and should only be kept if benchmarks show a quality benefit that does not violate the latency objective.

### FR-05 — Grounded Generation

The LLM receives only the selected retrieved evidence plus the user query and instructions.

The LLM is an answer generator, not the knowledge database.

### FR-06 — Sources

The response must preserve chunk IDs and source metadata so the UI can display evidence.

### FR-07 — Harness / Orchestration

The online pipeline must run through a structured harness that:

- validates input;
- performs STT when required;
- embeds the query;
- retrieves evidence;
- checks retrieval sufficiency;
- calls the LLM;
- validates the structured LLM response;
- performs grounding/unsupported-claim checks;
- retries recoverable failures with bounded retries;
- returns a controlled fallback when the system cannot answer safely.

### FR-08 — Guardrails

The system must handle:

- empty/invalid input;
- unsupported language;
- off-topic or unsupported questions;
- unsafe/inappropriate requests;
- STT failures;
- embedding failures;
- vector database timeouts;
- LLM timeouts;
- hallucination/ungrounded-answer detection;
- insufficient retrieved evidence.

When evidence is insufficient, the system should prefer a controlled response such as:

> I couldn't find enough relevant information in the available knowledge base to answer confidently.

The system must not claim that information came from the dataset if it was not retrieved.

### FR-09 — Optional Voice Output

Voice output may be added using an Indic-capable TTS provider if it does not make the demo unnecessarily slow or unreliable.

### FR-10 — Benchmarking

The project must record latency over a meaningful test set.

Required reporting:

- P50
- P70
- P100

The challenge's stated target is **under 200 ms for the full requested process**. Because STT, hosted LLM generation, and TTS have very different latency characteristics, component-level latency must also be reported separately so the team can identify the true bottleneck.

## 6. Non-Functional Requirements

### Performance

- Optimize the online retrieval path for sub-200 ms operation.
- Measure every major component rather than reporting a single best-case query.
- Do not claim a latency number without a benchmark.
- Offline chunking and indexing are preprocessing operations and must not run per user query.

### Scalability

- Never load the complete dataset into RAM.
- Stream/batch the dataset.
- Use checkpointing and resumability.
- Release embedding batches after vector upload.
- Use deterministic vector IDs so retries are safe.

### Reliability

A failed ingestion batch must not require restarting the entire dataset.

### Reproducibility

The repository must contain code/configuration sufficient to reproduce ingestion against the official Hugging Face dataset.

## 7. Out of Scope for the Hackathon MVP

- Fine-tuning an LLM unless benchmarks prove it is necessary.
- Indexing all available Indic languages.
- Building a general internet search engine.
- Rebuilding the vector index for every user.
- Storing the original ~55 GB dataset in GitHub.
- Creating a custom ANN algorithm.
- Adding multiple vector databases without benchmark justification.

## 8. Submission Requirements

The project must support:

- GitHub repository.
- Live working application.
- 90-second team/process video.
- Demo video showing the end-to-end product.
- Required social promotion by every team member on Instagram, X, and LinkedIn.
- `#RAGInGoa` on every required post.

Hackathon deadline:

**August 22, 2026, 11:59 PM**

## 9. Success Criteria

VaaniRAG is successful when:

- the selected English/Hindi/Marathi data can be processed end-to-end;
- chunks are indexed correctly;
- BGE-M3 embeddings are generated consistently;
- vector retrieval returns relevant evidence;
- the system can answer text and voice queries;
- answers are grounded in retrieved context;
- guardrails prevent unsupported answers;
- harness retries and failure handling work;
- P50/P70/P100 latency is measured;
- the live demo is reproducible and reliable.
