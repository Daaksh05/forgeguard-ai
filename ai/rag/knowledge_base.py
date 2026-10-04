"""
ForgeGuard AI — Local Maintenance Knowledge Base
Provides a modular local knowledge base abstraction for indexing and querying
maintenance SOPs, manuals, and troubleshooting guidelines.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ai.rag.chunker import DocumentChunk, SectionAwareChunker
from ai.rag.document_loader import Document, DocumentLoader
from ai.rag.evidence import MaintenanceEvidence, MaintenanceRetrievalReport
from ai.rag.retriever import BM25Retriever


class MaintenanceKnowledgeBase:
    """
    Lightweight local knowledge base indexing maintenance documents and exposing
    a structured retrieval interface.
    """

    def __init__(self, retrieval_engine: Optional[BM25Retriever] = None):
        self.documents: Dict[str, Document] = {}
        self.chunks: List[DocumentChunk] = []
        self.chunker = SectionAwareChunker()
        self.loader = DocumentLoader()
        self.retriever = retrieval_engine or BM25Retriever()
        self._is_indexed = False

    def load_and_index_document(self, file_path: Union[str, Path]) -> int:
        """
        Load a markdown document from disk, chunk it, and index it into the knowledge base.
        Returns the number of chunks added.
        """
        doc = self.loader.load_document(file_path)
        return self.add_document(doc)

    def load_and_index_directory(
        self,
        dir_path: Union[str, Path],
        glob_pattern: str = "*.md",
        exclude_patterns: Optional[List[str]] = None
    ) -> int:
        """
        Load and index all matching maintenance markdown documents from a directory.
        Excludes non-maintenance files (e.g. README.md, visual_evidence_spec.md).
        Returns the total number of chunks indexed.
        """
        docs = self.loader.load_directory(
            dir_path,
            glob_pattern=glob_pattern,
            exclude_patterns=exclude_patterns
        )
        total_chunks = 0
        for doc in docs:
            total_chunks += self.add_document(doc, rebuild_index=False)
        self._rebuild_index()
        return total_chunks

    def add_document(self, document: Document, rebuild_index: bool = True) -> int:
        """
        Add a Document object, generate section-aware chunks, and update the index.
        """
        self.documents[document.document_id] = document
        new_chunks = self.chunker.chunk_document(document)
        self.chunks.extend(new_chunks)

        if rebuild_index:
            self._rebuild_index()

        return len(new_chunks)

    def add_chunks(self, chunks: List[DocumentChunk]):
        """
        Add pre-computed DocumentChunk objects directly.
        """
        self.chunks.extend(chunks)
        self._rebuild_index()

    def _rebuild_index(self):
        """Re-index all accumulated chunks in the retrieval engine."""
        self.retriever.index_chunks(self.chunks)
        self._is_indexed = True

    def query(
        self,
        query_text: str,
        top_k: int = 3
    ) -> MaintenanceRetrievalReport:
        """
        Query the knowledge base and return ranked MaintenanceEvidence results.
        """
        if not self._is_indexed:
            self._rebuild_index()

        results = self.retriever.retrieve(query=query_text, top_k=top_k)

        return MaintenanceRetrievalReport(
            query=query_text,
            total_chunks_searched=len(self.chunks),
            top_k=top_k,
            retrieval_method="Lexical BM25 (Explainable Term Frequency / IDF)",
            results=results
        )

    def get_stats(self) -> Dict[str, Any]:
        """Return knowledge base summary statistics."""
        return {
            "total_documents": len(self.documents),
            "document_ids": list(self.documents.keys()),
            "total_chunks": len(self.chunks),
            "retrieval_engine": type(self.retriever).__name__
        }


def create_default_knowledge_base(
    docs_dir: Union[str, Path] = "data/maintenance_docs",
    exclude_patterns: Optional[List[str]] = None
) -> MaintenanceKnowledgeBase:
    """
    Factory function initializing the knowledge base with all standard maintenance documents.
    Defaults to loading genuine maintenance procedures (e.g. pump_bearing_maintenance.md)
    while excluding non-maintenance specs (README.md, visual_evidence_spec.md).
    """
    kb = MaintenanceKnowledgeBase()
    path = Path(docs_dir)
    if path.exists():
        kb.load_and_index_directory(path, exclude_patterns=exclude_patterns)
    return kb
