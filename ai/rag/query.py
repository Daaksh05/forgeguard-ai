#!/usr/bin/env python3
"""
ForgeGuard AI — Maintenance Knowledge Retrieval Query CLI
Queries the local maintenance knowledge base using transparent lexical BM25 retrieval.

Usage:
  python3 ai/rag/query.py --query "What should I inspect when vibration and temperature increase?"
  python3 ai/rag/query.py --query "What safety procedure should be followed before maintenance?" --top-k 2
"""

import argparse
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai.rag.knowledge_base import create_default_knowledge_base


def print_banner():
    print("=" * 78)
    print("  FORGEGUARD AI — MAINTENANCE KNOWLEDGE RETRIEVAL (RAG)")
    print("  Method: Explainable Lexical BM25 | Source: Factual Plant SOPs")
    print("=" * 78)


def main():
    parser = argparse.ArgumentParser(
        description="ForgeGuard AI Maintenance Knowledge Query Interface"
    )
    parser.add_argument(
        "--query", "-q",
        required=True,
        help="Maintenance question or condition query"
    )
    parser.add_argument(
        "--top-k", "-k",
        type=int,
        default=3,
        help="Maximum number of relevant sections to retrieve (default: 3)"
    )
    parser.add_argument(
        "--docs-dir", "-d",
        default="data/maintenance_docs",
        help="Path to maintenance documents directory (default: data/maintenance_docs)"
    )

    args = parser.parse_args()

    print_banner()
    docs_path = Path(args.docs_dir)
    if not docs_path.exists():
        print(f"[-] Error: Maintenance docs directory not found: {docs_path}", file=sys.stderr)
        sys.exit(1)

    kb = create_default_knowledge_base(docs_path)
    stats = kb.get_stats()
    print(f"[*] Ingested {stats['total_documents']} maintenance documents ({stats['total_chunks']} section chunks)")
    print(f"[*] Executing query: \"{args.query}\" (Top-{args.top_k})\n")

    report = kb.query(args.query, top_k=args.top_k)

    if not report.results:
        print("[-] No relevant maintenance sections found matching query.")
        print("=" * 78 + "\n")
        return

    print("-" * 78)
    print(f"RETRIEVED MAINTENANCE EVIDENCE ({len(report.results)} Results)")
    print("-" * 78)

    for idx, evidence in enumerate(report.results, 1):
        print(f"\n[Result {idx}] Relevance Score: {evidence.relevance_score:.4f}")
        print(f"  Source Document:  {evidence.source_document}")
        print(f"  Chunk ID:         {evidence.chunk_id}")
        print(f"  Section:          {evidence.section}")
        print(f"  Source Path:      {evidence.source_path}")
        print("\n  --- Factual Document Content ---")
        for line in evidence.retrieved_content.splitlines():
            print(f"  | {line}")

    print("\n" + "=" * 78 + "\n")


if __name__ == "__main__":
    main()
