#!/usr/bin/env python3
"""
ForgeGuard AI — End-to-End RAG Pipeline Runner
Coordinates document loading, section-aware chunking, indexing, and retrieval,
producing structured MaintenanceEvidence objects for downstream multimodal reasoning.

Usage:
  python3 ai/rag/run_rag.py --query "What should I inspect when vibration and temperature increase?"
  python3 ai/rag/run_rag.py --query "What safety procedure should be followed before maintenance?" --output results/rag_evidence.json
"""

import argparse
import json
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai.rag.chunker import SectionAwareChunker
from ai.rag.document_loader import DocumentLoader
from ai.rag.knowledge_base import MaintenanceKnowledgeBase


def run_rag_pipeline(
    query: str,
    docs_dir: str = "data/maintenance_docs",
    top_k: int = 3
):
    """
    Execute full RAG pipeline:
    1. Document Loading -> 2. Section Chunking -> 3. Local KB Indexing -> 4. BM25 Retrieval -> 5. Structured Evidence
    """
    loader = DocumentLoader()
    chunker = SectionAwareChunker()
    kb = MaintenanceKnowledgeBase()

    docs_path = Path(docs_dir)
    if not docs_path.exists():
        raise FileNotFoundError(f"Maintenance documentation directory not found: {docs_path}")

    # 1. Load Documents
    documents = loader.load_directory(docs_path)

    # 2. Section-Aware Chunking & 3. Knowledge Base Indexing
    total_chunks = 0
    for doc in documents:
        chunks = chunker.chunk_document(doc)
        kb.add_chunks(chunks)
        kb.documents[doc.document_id] = doc
        total_chunks += len(chunks)

    # 4. Lexical Retrieval
    report = kb.query(query_text=query, top_k=top_k)

    return report, len(documents), total_chunks


def main():
    parser = argparse.ArgumentParser(
        description="ForgeGuard AI End-to-End Maintenance Knowledge Retrieval Pipeline"
    )
    parser.add_argument(
        "--query", "-q",
        required=True,
        help="Query string for maintenance knowledge retrieval"
    )
    parser.add_argument(
        "--top-k", "-k",
        type=int,
        default=3,
        help="Number of top relevant sections to retrieve (default: 3)"
    )
    parser.add_argument(
        "--docs-dir", "-d",
        default="data/maintenance_docs",
        help="Directory containing maintenance markdown documents"
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Path to save output JSON evidence report (e.g. results/rag_evidence.json)"
    )

    args = parser.parse_args()

    print("=" * 78)
    print("  FORGEGUARD AI — RAG KNOWLEDGE PIPELINE")
    print("  Document Loader -> Section Chunker -> Local KB -> BM25 Retriever")
    print("=" * 78)

    report, num_docs, num_chunks = run_rag_pipeline(
        query=args.query,
        docs_dir=args.docs_dir,
        top_k=args.top_k
    )

    print(f"[*] Indexed {num_docs} document(s) into {num_chunks} section chunks.")
    print(f"[*] Query: \"{args.query}\" (Top-{args.top_k})\n")

    print("-" * 78)
    print(f"RETRIEVED GROUNDED EVIDENCE ({len(report.results)} chunks)")
    print("-" * 78)

    for idx, evidence in enumerate(report.results, 1):
        print(f"\n[Evidence {idx}] Relevance: {evidence.relevance_score:.4f} | Chunk: {evidence.chunk_id}")
        print(f"  Document: {evidence.source_document}")
        print(f"  Section:  {evidence.section}")
        print(f"  Snippet:  {evidence.retrieved_content.splitlines()[0] if evidence.retrieved_content else ''}")

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, indent=2)
        print(f"\n[+] Structured RAG evidence written to: {out_path.resolve()}")

    print("\n" + "=" * 78 + "\n")


if __name__ == "__main__":
    main()
