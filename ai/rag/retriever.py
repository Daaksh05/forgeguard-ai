"""
ForgeGuard AI — Lexical Retrieval Engine
Transparent, explainable BM25 / TF-IDF lexical retrieval engine for industrial
maintenance manuals. Operates with zero heavyweight dependencies or black-box models.
"""

import math
import re
from typing import Dict, List, Set, Tuple

from ai.rag.chunker import DocumentChunk
from ai.rag.evidence import MaintenanceEvidence, MaintenanceRetrievalReport


# Standard English and markdown stop words
STOP_WORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than",
    "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this",
    "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't",
    "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's",
    "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom",
    "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll",
    "you're", "you've", "your", "yours", "yourself", "yourselves"
}


def tokenize(text: str) -> List[str]:
    """
    Tokenize text into lowercase alphanumeric words, filtering out common stop words.
    Preserves industrial acronyms, numbers, and technical terms.
    """
    if not text:
        return []
    words = re.findall(r"\b[A-Za-z0-9\-_]{2,}\b", text.lower())
    return [w for w in words if w not in STOP_WORDS]


class BM25Retriever:
    """
    Explainable Okapi BM25 Lexical Retrieval Engine.
    Computes term frequency-inverse document frequency with document length normalization.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75, title_boost: float = 1.8):
        self.k1 = k1
        self.b = b
        self.title_boost = title_boost
        self.chunks: List[DocumentChunk] = []
        self.corpus_size = 0
        self.avg_doc_len = 0.0
        self.doc_lengths: List[int] = []
        self.doc_token_freqs: List[Dict[str, int]] = []
        self.title_token_freqs: List[Dict[str, int]] = []
        self.idf: Dict[str, float] = {}

    def index_chunks(self, chunks: List[DocumentChunk]):
        """
        Build lexical BM25 inverted index from document chunks.
        """
        self.chunks = chunks
        self.corpus_size = len(chunks)
        if self.corpus_size == 0:
            self.avg_doc_len = 0.0
            return

        self.doc_lengths = []
        self.doc_token_freqs = []
        self.title_token_freqs = []
        doc_freqs: Dict[str, int] = {}

        total_length = 0
        for chunk in chunks:
            # Tokenize body and section header
            body_tokens = tokenize(chunk.content)
            title_tokens = tokenize(chunk.section)

            length = len(body_tokens)
            self.doc_lengths.append(length)
            total_length += length

            # Body term frequencies
            tf: Dict[str, int] = {}
            for t in body_tokens:
                tf[t] = tf.get(t, 0) + 1
            self.doc_token_freqs.append(tf)

            # Title term frequencies
            title_tf: Dict[str, int] = {}
            for t in title_tokens:
                title_tf[t] = title_tf.get(t, 0) + 1
            self.title_token_freqs.append(title_tf)

            # Document frequency for IDF
            unique_terms = set(body_tokens) | set(title_tokens)
            for t in unique_terms:
                doc_freqs[t] = doc_freqs.get(t, 0) + 1

        self.avg_doc_len = total_length / self.corpus_size if self.corpus_size > 0 else 0.0

        # Calculate BM25 IDF for all terms in vocabulary
        self.idf = {}
        for term, df in doc_freqs.items():
            # Standard BM25 IDF with smoothing
            val = math.log(1.0 + (self.corpus_size - df + 0.5) / (df + 0.5))
            self.idf[term] = max(0.1, val)

    def retrieve(
        self,
        query: str,
        top_k: int = 3
    ) -> List[MaintenanceEvidence]:
        """
        Score all indexed chunks against query and return top_k ranked MaintenanceEvidence records.
        """
        if not query or not query.strip() or self.corpus_size == 0:
            return []

        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        scores: List[Tuple[float, int]] = []

        for idx, chunk in enumerate(self.chunks):
            doc_len = self.doc_lengths[idx]
            tf_map = self.doc_token_freqs[idx]
            title_tf_map = self.title_token_freqs[idx]

            score = 0.0
            for term in query_tokens:
                if term not in self.idf:
                    continue

                term_idf = self.idf[term]
                term_tf = tf_map.get(term, 0)
                title_tf = title_tf_map.get(term, 0)

                # Effective frequency with section title boost
                effective_tf = term_tf + (title_tf * self.title_boost)

                if effective_tf > 0:
                    numerator = effective_tf * (self.k1 + 1.0)
                    denominator = effective_tf + self.k1 * (1.0 - self.b + self.b * (doc_len / max(1.0, self.avg_doc_len)))
                    score += term_idf * (numerator / denominator)

            if score > 0.0:
                scores.append((score, idx))

        # Sort descending by relevance score
        scores.sort(key=lambda x: x[0], reverse=True)

        results: List[MaintenanceEvidence] = []
        for score, idx in scores[:top_k]:
            chunk = self.chunks[idx]
            results.append(MaintenanceEvidence(
                source_document=chunk.document_id,
                chunk_id=chunk.chunk_id,
                section=chunk.section,
                retrieved_content=chunk.content,
                relevance_score=round(score, 4),
                retrieval_query=query,
                source_path=chunk.source_path
            ))

        return results
