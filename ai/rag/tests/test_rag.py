"""
ForgeGuard AI — Unit Tests for Maintenance Knowledge Retrieval (RAG)
Covers:
- Document loading & metadata extraction
- Section-aware chunking preserving markdown headers and tables
- PUMP_001 Failure Scenario Queries:
  1. Rising vibration (ISO 10816 thresholds & symptoms)
  2. High bearing temperature (Thermal rules & limits)
  3. Lubrication problems (Polyurea grease & purge protocols)
  4. Bearing inspection (Step-by-step 4-point inspection)
  5. Safety / LOTO (400V electrical isolation & PPE)
- Empty query handling
- Top-k parameter behavior
- Source metadata preservation
- Relevance score ordering
"""

import unittest
from pathlib import Path

from ai.rag.chunker import SectionAwareChunker
from ai.rag.document_loader import DocumentLoader
from ai.rag.evidence import MaintenanceEvidence, MaintenanceRetrievalReport
from ai.rag.knowledge_base import MaintenanceKnowledgeBase, create_default_knowledge_base
from ai.rag.retriever import BM25Retriever, tokenize


class TestMaintenanceRAG(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.docs_dir = Path("data/maintenance_docs")
        cls.main_sop_path = cls.docs_dir / "pump_bearing_maintenance.md"
        cls.kb = create_default_knowledge_base(cls.docs_dir)

    def test_document_loader(self):
        """Verify DocumentLoader correctly parses file content and extracts metadata."""
        loader = DocumentLoader()
        doc = loader.load_document(self.main_sop_path)

        self.assertEqual(doc.document_id, "SOP-MNT-PUMP-042")
        self.assertIn("Centrifugal Pump Bearing Maintenance", doc.title)
        self.assertIn("Safety Warnings & Isolation (LOTO)", doc.content)
        self.assertEqual(doc.metadata.get("revision"), "2.4")

    def test_maintenance_documents_only_indexed(self):
        """Verify only genuine maintenance knowledge documents are indexed, excluding README and visual specs."""
        stats = self.kb.get_stats()
        self.assertEqual(stats["total_documents"], 1, "Only pump_bearing_maintenance.md should be indexed")
        self.assertIn("SOP-MNT-PUMP-042", stats["document_ids"])
        self.assertNotIn("visual_evidence_spec", stats["document_ids"])
        self.assertNotIn("README", stats["document_ids"])

    def test_section_aware_chunker(self):
        """Verify chunker preserves section hierarchy, table boundaries, and headers."""
        loader = DocumentLoader()
        doc = loader.load_document(self.main_sop_path)
        chunker = SectionAwareChunker()
        chunks = chunker.chunk_document(doc)

        self.assertGreaterEqual(len(chunks), 7)
        sections = [c.section for c in chunks]

        # Verify key section titles are captured
        self.assertTrue(any("Safety Warnings & Isolation (LOTO)" in s for s in sections))
        self.assertTrue(any("Maintenance Intervals & Schedule" in s for s in sections))
        self.assertTrue(any("Diagnostic Thresholds" in s for s in sections))
        self.assertTrue(any("Step-by-Step Bearing Inspection" in s for s in sections))
        self.assertTrue(any("Re-lubrication Protocol" in s for s in sections))
        self.assertTrue(any("Corrective Action Matrix" in s for s in sections))

        # Check chunk ID format
        for chunk in chunks:
            self.assertTrue(chunk.chunk_id.startswith("SOP-MNT-PUMP-042_chk_"))
            self.assertEqual(chunk.document_id, "SOP-MNT-PUMP-042")

    def test_query_rising_vibration(self):
        """Scenario Query 1: Rising vibration thresholds and ISO 10816 standards."""
        query = "What are the ISO vibration velocity thresholds for centrifugal pump bearing degradation?"
        report = self.kb.query(query, top_k=3)

        self.assertGreater(len(report.results), 0)
        top_result = report.results[0]
        # Should retrieve Diagnostic Thresholds or Symptoms section
        self.assertTrue(
            "Diagnostic Thresholds" in top_result.section or "Symptoms" in top_result.section or "Corrective Action" in top_result.section
        )
        self.assertTrue("ISO 10816-3" in top_result.retrieved_content or "Vibration Velocity" in top_result.retrieved_content)
        self.assertEqual(top_result.source_document, "SOP-MNT-PUMP-042")

    def test_query_high_bearing_temperature(self):
        """Scenario Query 2: Bearing housing temperature evaluation rules."""
        query = "What are the temperature evaluation rules and emergency shutdown limits for bearing housing?"
        report = self.kb.query(query, top_k=3)

        self.assertGreater(len(report.results), 0)
        top_sections = [r.section for r in report.results]
        self.assertTrue(any("Temperature Evaluation Rules" in s or "Safety Warnings" in s or "Corrective Action" in s for s in top_sections))
        
        # Verify content contains factual temperature limits (55-68C, >75C, or >90C)
        matched_content = "".join([r.retrieved_content for r in report.results])
        self.assertTrue("75" in matched_content and "90" in matched_content)

    def test_query_lubrication_problems(self):
        """Scenario Query 3: Polyurea grease protocol and lubrication check."""
        query = "What type of grease should be used for re-lubrication and what is the protocol?"
        report = self.kb.query(query, top_k=3)

        self.assertGreater(len(report.results), 0)
        top_sections = [r.section for r in report.results]
        self.assertTrue(any("Re-lubrication Protocol" in s or "Lubrication Service" in s for s in top_sections))

        matched_content = "".join([r.retrieved_content for r in report.results])
        self.assertIn("Polyurea", matched_content)
        self.assertIn("NLGI Grade 2", matched_content)

    def test_query_bearing_inspection(self):
        """Scenario Query 4: Step-by-step bearing inspection procedures."""
        query = "What are the step-by-step bearing inspection procedures including ultrasonic and thermal check?"
        report = self.kb.query(query, top_k=3)

        self.assertGreater(len(report.results), 0)
        top_result = report.results[0]
        self.assertIn("Inspection & Maintenance Procedures", top_result.section)
        self.assertIn("Auditory & Ultrasonic Check", top_result.retrieved_content)

    def test_query_safety_loto(self):
        """Scenario Query 5: Safety procedure and Lockout/Tagout (LOTO)."""
        query = "What safety procedures and Lockout Tagout LOTO rules must be followed before inspection?"
        report = self.kb.query(query, top_k=3)

        self.assertGreater(len(report.results), 0)
        top_result = report.results[0]
        self.assertIn("Safety Warnings & Isolation (LOTO)", top_result.section)
        self.assertIn("Lockout/Tagout", top_result.retrieved_content)
        self.assertIn("400V", top_result.retrieved_content)

    def test_empty_query_handling(self):
        """Verify empty or whitespace-only query returns zero results gracefully."""
        report_empty = self.kb.query("", top_k=3)
        self.assertEqual(len(report_empty.results), 0)

        report_spaces = self.kb.query("   ", top_k=3)
        self.assertEqual(len(report_spaces.results), 0)

    def test_top_k_parameter(self):
        """Verify top_k parameter strictly controls the number of returned chunks."""
        query = "bearing vibration temperature maintenance"
        report_k1 = self.kb.query(query, top_k=1)
        self.assertEqual(len(report_k1.results), 1)

        report_k2 = self.kb.query(query, top_k=2)
        self.assertEqual(len(report_k2.results), 2)

    def test_relevance_score_ordering(self):
        """Verify results are returned in strictly descending order of relevance score."""
        query = "bearing housing temperature vibration maintenance inspection"
        report = self.kb.query(query, top_k=5)
        self.assertGreaterEqual(len(report.results), 2)

        scores = [r.relevance_score for r in report.results]
        for i in range(len(scores) - 1):
            self.assertGreaterEqual(scores[i], scores[i + 1], "Scores must be strictly descending")

    def test_source_metadata_preservation(self):
        """Verify retrieved evidence preserves source document ID, chunk ID, section, and query."""
        query = "Lockout Tagout procedure"
        report = self.kb.query(query, top_k=1)
        self.assertEqual(len(report.results), 1)
        ev = report.results[0]

        self.assertEqual(ev.source_document, "SOP-MNT-PUMP-042")
        self.assertTrue(ev.chunk_id.startswith("SOP-MNT-PUMP-042_chk_"))
        self.assertEqual(ev.retrieval_query, query)
        self.assertTrue(len(ev.section) > 0)
        self.assertTrue(len(ev.retrieved_content) > 0)


if __name__ == "__main__":
    unittest.main()
