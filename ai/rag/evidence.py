"""
ForgeGuard AI — Structured Maintenance Evidence Schema
Defines dataclasses and serialization schemas for grounded maintenance document
retrieval evidence passed to downstream reasoning agents.
"""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class MaintenanceEvidence:
    """
    Structured evidence representing a single retrieved section from a verified maintenance document.
    Preserves strict source provenance and relevance scoring.
    """
    source_document: str       # Document ID / filename (e.g. SOP-MNT-PUMP-042)
    chunk_id: str              # Unique chunk ID
    section: str               # Section title hierarchy (e.g. "4. Inspection & Maintenance Procedures > 4.1 Step-by-Step Bearing Inspection")
    retrieved_content: str     # Raw factual text from maintenance manual
    relevance_score: float     # Retrieval relevance score
    retrieval_query: str       # Original input query
    source_path: str = ""      # Absolute / relative file path

    def to_dict(self) -> Dict[str, Any]:
        """Convert evidence to standard dictionary format."""
        return {
            "source_document": self.source_document,
            "chunk_id": self.chunk_id,
            "section": self.section,
            "retrieved_content": self.retrieved_content,
            "relevance_score": round(float(self.relevance_score), 4),
            "retrieval_query": self.retrieval_query,
            "source_path": self.source_path
        }


@dataclass
class MaintenanceRetrievalReport:
    """Consolidated retrieval report containing multiple ranked maintenance evidence records."""
    query: str
    total_chunks_searched: int
    top_k: int
    retrieval_method: str
    results: List[MaintenanceEvidence] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert retrieval report to dictionary."""
        return {
            "query": self.query,
            "total_chunks_searched": self.total_chunks_searched,
            "top_k": self.top_k,
            "retrieval_method": self.retrieval_method,
            "results_count": len(self.results),
            "results": [r.to_dict() for r in self.results]
        }
