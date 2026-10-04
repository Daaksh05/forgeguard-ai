"""
ForgeGuard AI — Section-Aware Markdown Chunker
Splits technical maintenance manuals along natural markdown section boundaries (H1/H2/H3)
to preserve complete engineering tables, safety cautions, and troubleshooting steps.
"""

import re
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from ai.rag.document_loader import Document


@dataclass
class DocumentChunk:
    """A semantic section chunk from a maintenance document."""
    chunk_id: str
    document_id: str
    section: str
    content: str
    source_path: str = ""
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk to standard dictionary."""
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "section": self.section,
            "content": self.content,
            "source_path": self.source_path,
            "metadata": self.metadata
        }


class SectionAwareChunker:
    """
    Chunks markdown documents by splitting on markdown headers (H1, H2, H3),
    preserving hierarchical section context and structured content.
    """

    def __init__(self, min_chunk_chars: int = 40):
        self.min_chunk_chars = min_chunk_chars

    def chunk_document(self, document: Document) -> List[DocumentChunk]:
        """
        Split a Document into section-aware chunks based on markdown heading structure.
        """
        raw_text = document.content
        lines = raw_text.splitlines()

        chunks: List[DocumentChunk] = []
        current_h1 = document.title
        current_h2 = ""
        current_h3 = ""
        current_lines: List[str] = []
        chunk_index = 1

        def has_substantive_body(line_list: List[str]) -> bool:
            """Check if lines contain substantive text beyond just headers or dividers."""
            substantive = [
                l.strip() for l in line_list
                if l.strip() and not l.strip().startswith("#") and l.strip() != "---"
            ]
            return len(substantive) > 0

        def flush_current_chunk():
            nonlocal chunk_index, current_lines
            content = "\n".join(current_lines).strip()
            # Emits chunk only if it has substantive body content or sufficient length
            if len(content) >= self.min_chunk_chars and has_substantive_body(current_lines):
                # Build hierarchical section path
                section_parts = [p for p in [current_h1, current_h2, current_h3] if p]
                section_title = " > ".join(section_parts) if section_parts else "Overview"
                
                chunk_id = f"{document.document_id}_chk_{chunk_index:03d}"
                chunks.append(DocumentChunk(
                    chunk_id=chunk_id,
                    document_id=document.document_id,
                    section=section_title,
                    content=content,
                    source_path=document.source_path,
                    metadata={
                        "h1": current_h1,
                        "h2": current_h2,
                        "h3": current_h3,
                        "char_count": len(content),
                        "chunk_index": chunk_index
                    }
                ))
                chunk_index += 1
                current_lines = []

        for line in lines:
            stripped = line.strip()
            # Detect Markdown Headings
            if stripped.startswith("### "):
                flush_current_chunk()
                current_h3 = stripped[4:].strip()
                current_lines.append(line)
            elif stripped.startswith("## "):
                flush_current_chunk()
                current_h2 = stripped[3:].strip()
                current_h3 = ""
                current_lines.append(line)
            elif stripped.startswith("# ") and not current_lines:
                # Top level document H1 header
                current_h1 = stripped[2:].strip()
                current_lines.append(line)
            else:
                current_lines.append(line)

        # Flush final accumulated chunk
        flush_current_chunk()

        return chunks

    def chunk_documents(self, documents: List[Document]) -> List[DocumentChunk]:
        """Chunk a collection of documents."""
        all_chunks: List[DocumentChunk] = []
        for doc in documents:
            all_chunks.extend(self.chunk_document(doc))
        return all_chunks
