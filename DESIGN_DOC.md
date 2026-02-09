# Design Document: Aaran's Digital Twin

## Key Design Decisions

### 1. RAG vs Fine-Tuning

**Decision:** Use RAG instead of fine-tuning.

**Why:**
- Faster updates (re-run script vs retrain model)
- Source transparency (shows what sources were used)
- Less hallucination (grounded in real documents)

### 2. Static vs Dynamic Data

**Decision:** Slides ingested once into ChromaDB. Calendar fetched live every request.

**Why:**
- Slides use RAG  which require pre-computed embeddings
- Calendar changes constantly, so it must be live for accuracy
- Calendar's "today's events" data is directly entered into prompt

### 3. Two-Layer Privacy

**Decision:** Privacy enforced at data layer AND LLM layer.

**Layers:**
- Layer 1 (Data): Events past 5PM are not sent to LLM (personal)
- Layer 2 (LLM): Prompt instructs LLM to decline personal questions

**Why:**
- Defense in depth - if one layer fails, the other catches it
- LLM guardrails can be tricked
- Data filtering is 100% reliable
- Together they provide strong privacy protection

### 4. ChromaDB for Vector Storage

**Decision:** Use ChromaDB as the vector database.

**Why:**
- Good enough for MVP (Simple + Free)
- Persistent, so data survives server restarts

### 5. Mood Engine Logic

**Decision:** Use simple if/else logic for availability detection

**Why:**
- Calendar data is structured so simple rules work well
- Interpretable and fast

---

## Evaluation

**Verify code works**
- RAG: Responses cite correct source documents, no hallucination (for both profile and slide data)
- Calendar: Status matches real calendar state
- Privacy: "Weekend plans?" is declined, after-5PM events never leak
