"""
ForgeGuard AI — Maintenance Document Loader
Reads technical maintenance manuals, SOPs, and engineering specifications from disk
into structured document records.
"""

import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


@dataclass
class Document:
    """Structured representation of an ingested maintenance document."""
    document_id: str
    source_path: str
    title: str
    content: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary."""
        return asdict(self)


def extract_document_metadata(content: str, file_path: Path) -> Tuple_Title_Id_Meta:
    pass


class DocumentLoader:
    """
    Loads and parses maintenance markdown documents from disk.
    """

    def __init__(self, base_dir: Optional[Union[str, Path]] = None):
        self.base_dir = Path(base_dir) if base_dir else None

    def load_document(self, file_path: Union[str, Path]) -> Document:
        """
        Load a single markdown document from disk.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Maintenance document not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            raw_content = f.read()

        title, doc_id, meta = self._extract_metadata(raw_content, path)

        return Document(
            document_id=doc_id,
            source_path=str(path),
            title=title,
            content=raw_content,
            metadata=meta
        )

    def load_directory(
        self,
        dir_path: Union[str, Path],
        glob_pattern: str = "*.md",
        exclude_patterns: Optional[List[str]] = None
    ) -> List[Document]:
        """
        Load all matching maintenance documents from a directory, skipping non-maintenance files.
        """
        target_dir = Path(dir_path)
        if not target_dir.exists() or not target_dir.is_dir():
            raise NotADirectoryError(f"Directory not found: {target_dir}")

        excludes = exclude_patterns if exclude_patterns is not None else ["README*", "*visual_evidence_spec*"]
        documents: List[Document] = []
        for file_path in sorted(target_dir.glob(glob_pattern)):
            if file_path.is_file():
                # Check if excluded
                if any(file_path.match(pat) for pat in excludes):
                    continue
                documents.append(self.load_document(file_path))
        return documents

    def _extract_metadata(self, content: str, path: Path):
        """Extract title, document ID, and header metadata from markdown content."""
        lines = content.splitlines()
        title = path.stem.replace("_", " ").title()
        doc_id = path.stem

        # Extract title from first H1 header
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("# "):
                title = stripped[2:].strip()
                break

        meta: Dict[str, Any] = {
            "filename": path.name,
            "file_size_bytes": path.stat().st_size
        }

        # Extract Document ID if explicitly declared in blockquote / headers (e.g. Document ID: `SOP-MNT-PUMP-042`)
        doc_id_match = re.search(r"\*\*Document ID\*\*:\s*`?([A-Za-z0-9\-_]+)`?", content)
        if doc_id_match:
            doc_id = doc_id_match.group(1)
            meta["declared_document_id"] = doc_id

        revision_match = re.search(r"\*\*Revision\*\*:\s*([0-9\.]+)", content)
        if revision_match:
            meta["revision"] = revision_match.group(1)

        equipment_match = re.search(r"\*\*Target Equipment\*\*:\s*([^\n|]+)", content)
        if equipment_match:
            meta["target_equipment"] = equipment_match.group(1).strip()

        return title, doc_id, meta
