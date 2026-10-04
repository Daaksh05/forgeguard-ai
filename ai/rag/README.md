# RAG Module — Maintenance Knowledge Retrieval (Phase 6A)

> **Module**: `ai/rag`  
> **Status**: Operational Lexical RAG Engine  
> **Retrieval Method**: Explainable Okapi BM25 Lexical Retrieval with Section Hierarchy Boosting (Zero Heavyweight Dependencies)

---

## 1. Purpose

The **Maintenance Knowledge Retrieval (RAG) Layer** indexes and retrieves factual engineering standard operating procedures (SOPs), troubleshooting matrices, and safety protocols from equipment manuals.

When anomalous sensor telemetry (Phase 4) and visual defect signatures (Phase 5) are identified, this layer supplies grounded, verbatim maintenance instructions directly to the ForgeGuard AI multimodal reasoning agent—eliminating hallucinations and ensuring compliant maintenance actions.

```
+-------------------------------------------------------------------------------+
|                      Maintenance Documentation on Disk                        |
|       (data/maintenance_docs/pump_bearing_maintenance.md, SOP-MNT-PUMP-042)    |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                         DocumentLoader (document_loader.py)                   |
|                   Extracts title, document ID, revisions & metadata           |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                       SectionAwareChunker (chunker.py)                        |
|          Splits along H1/H2/H3 boundaries preserving tables and procedures    |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                   MaintenanceKnowledgeBase (knowledge_base.py)                |
|                    Indexes chunk corpus into local BM25 engine                |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                       BM25Retriever (retriever.py)                            |
|             Explainable TF-IDF scoring with section title weight boosting     |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                    Structured MaintenanceEvidence (evidence.py)               |
|            (source_document, chunk_id, section, content, relevance_score)     |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                      Multimodal Reasoning Agent (Phase 6B)                    |
+-------------------------------------------------------------------------------+
```

---

## 2. Current Knowledge Sources

All maintenance procedures are ingested strictly from factual on-disk maintenance documents without fabrication:

| Document ID | Title | File Path | Focus Area | Status in Maintenance RAG |
| :--- | :--- | :--- | :--- | :--- |
| `SOP-MNT-PUMP-042` | Centrifugal Pump Bearing Maintenance & Inspection | `data/maintenance_docs/pump_bearing_maintenance.md` | ISO 10816-3 thresholds, 4-point inspection, polyurea re-lubrication, LOTO safety rules. | **Active Knowledge Source** (Indexed) |
| `visual_evidence_spec` | Visual Evidence & Computer Vision Specification | `data/maintenance_docs/visual_evidence_spec.md` | Optical defect catalog and visual specifications for Phase 5 Vision subsystem. | Excluded from Maintenance RAG (Preserved for Vision) |
| `README` | Maintenance Documents Overview | `data/maintenance_docs/README.md` | Directory scope, asset registry, and SOP index. | Excluded from Maintenance RAG |

---

## 3. Architecture & Components

### 3.1 Document Loader (`ai/rag/document_loader.py`)
- Reads raw markdown documents from disk.
- Extracts document metadata, formal revision IDs, target equipment, and titles.

### 3.2 Section-Aware Chunker (`ai/rag/chunker.py`)
- Splits along natural markdown header boundaries (`#`, `##`, `###`) rather than arbitrary character counts.
- Preserves table rows, diagnostic lists, and caution callouts within a single cohesive chunk.
- Builds hierarchical section trails (e.g. `Standard Operating Procedure > 4. Inspection & Maintenance Procedures > 4.1 Step-by-Step Bearing Inspection`).

### 3.3 Local Knowledge Base (`ai/rag/knowledge_base.py`)
- In-memory knowledge base abstraction.
- Modular architecture allowing documents to be dynamically indexed or replaced.

### 3.4 Lexical BM25 Retriever (`ai/rag/retriever.py`)
- Computes Okapi BM25 relevance scores:
  $$IDF(t) = \ln\left(1 + \frac{N - n(t) + 0.5}{n(t) + 0.5}\right)$$
  $$Score(D, Q) = \sum_{t \in Q} IDF(t) \cdot \frac{f(t, D) \cdot (k_1 + 1)}{f(t, D) + k_1 \cdot (1 - b + b \cdot \frac{|D|}{\text{avgdl}})}$$
- Applies a $1.8\times$ section title boost when query keywords match the chapter/section header.

---

## 4. Structured Maintenance Evidence Schema

Every retrieved result strictly maintains source provenance and verbatim text:

```json
{
  "source_document": "SOP-MNT-PUMP-042",
  "chunk_id": "SOP-MNT-PUMP-042_chk_007",
  "section": "Standard Operating Procedure: Centrifugal Pump Bearing Maintenance & Inspection > 4. Inspection & Maintenance Procedures > 4.1 Step-by-Step Bearing Inspection",
  "retrieved_content": "## 4. Inspection & Maintenance Procedures\n\n### 4.1 Step-by-Step Bearing Inspection\n1. **Auditory & Ultrasonic Check**:\n   - Apply ultrasonic contact probe to the top of the drive-end bearing housing.\n   - Normal reading: <45 dB. If >60 dB with rhythmic popping, inner ring defect is present.\n2. **Thermal Imaging & Contact Probe**:\n   - Measure temperature at 3 points: Drive-end housing, Non-drive-end housing, and Motor frame.\n   - Temperature gradient between DE and NDE bearing should not exceed 12°C.\n3. **Lubrication Film & Seal Inspection**:\n   - Inspect outer labyrinth seals for grease leakage, weeping, or black residue.\n   - Clean the grease relief valve and inspect purged lubricant for metallic particles using a magnetic wand.\n4. **Coupling & Shaft Runout**:\n   - Remove coupling guard and check flexible elastomeric spider insert for shredding or angular misalignment (<0.05 mm permissible).",
  "relevance_score": 3.5331,
  "retrieval_query": "What should I inspect when vibration and temperature increase?",
  "source_path": "data/maintenance_docs/pump_bearing_maintenance.md"
}
```

---

## 5. Usage Commands

### Query CLI Interface
```bash
# Query maintenance procedures
python3 ai/rag/query.py \
    --query "What should I inspect when vibration and temperature increase?" \
    --top-k 3

# Query safety & LOTO protocols
python3 ai/rag/query.py \
    --query "What safety procedure should be followed before maintenance?" \
    --top-k 2
```

### End-to-End Pipeline & JSON Export
```bash
python3 ai/rag/run_rag.py \
    --query "What are the recommended bearing inspection steps?" \
    --output results/rag_maintenance_evidence.json
```

### Run Tests
```bash
python3 -m unittest discover -s ai/rag/tests -v
```

---

## 6. Example Queries & Retrieved Sections

| Query | Top Retrieved Section | Document Reference |
| :--- | :--- | :--- |
| *"What should I inspect when vibration and temperature increase?"* | `4.1 Step-by-Step Bearing Inspection` | `SOP-MNT-PUMP-042` (§4.1) |
| *"What are the recommended bearing inspection steps?"* | `4.1 Step-by-Step Bearing Inspection` | `SOP-MNT-PUMP-042` (§4.1) |
| *"What should be checked when lubrication is suspected?"* | `3.2 Diagnostic Thresholds (ISO 10816-3)` & `4.2 Re-lubrication Protocol` | `SOP-MNT-PUMP-042` (§3.2, §4.2) |
| *"What safety procedure should be followed before maintenance?"* | `1. Safety Warnings & Isolation (LOTO)` | `SOP-MNT-PUMP-042` (§1) |

---

## 7. Limitations & Future Upgrade Path

> **IMPORTANT DISCLAIMER**: The current implementation uses lightweight lexical retrieval (Okapi BM25) and is not yet a production semantic vector database.

- **Current Limitations**: Lexical retrieval relies on term matching, synonym coverage, and token overlap. Queries using abstract phrasing without domain keywords may yield lower relevance.
- **Future Upgrade Path**:
  - Integrate an embedding model (e.g., BGE, MiniLM, or AMD ROCm-accelerated embedding models).
  - Add vector indexing (e.g. FAISS, Chroma, or Qdrant) for dense semantic vector search.
  - Implement hybrid search (BM25 + Dense Vectors + Cross-Encoder Re-ranking).
