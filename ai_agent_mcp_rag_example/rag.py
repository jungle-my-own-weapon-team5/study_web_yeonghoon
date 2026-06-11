from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path


TOKEN_PATTERN = re.compile(r"[A-Za-z0-9가-힣_]+")


@dataclass(frozen=True)
class Chunk:
    id: str
    source: str
    text: str


@dataclass(frozen=True)
class SearchResult:
    chunk: Chunk
    score: float


def tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    for match in TOKEN_PATTERN.finditer(text):
        token = match.group(0).lower()
        tokens.append(token)

        ascii_prefix = re.match(r"([a-z0-9_]+)[가-힣]+$", token)
        if ascii_prefix:
            tokens.append(ascii_prefix.group(1))
    return tokens


def load_markdown_documents(data_dir: Path) -> list[tuple[str, str]]:
    documents: list[tuple[str, str]] = []
    for path in sorted(data_dir.glob("*.md")):
        documents.append((str(path), path.read_text(encoding="utf-8")))
    return documents


def chunk_text(source: str, text: str, max_words: int = 90) -> list[Chunk]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    chunks: list[Chunk] = []
    buffer: list[str] = []
    word_count = 0

    def flush() -> None:
        nonlocal buffer, word_count
        if not buffer:
            return
        chunk_id = f"{source}#chunk-{len(chunks) + 1}"
        chunks.append(Chunk(id=chunk_id, source=source, text="\n\n".join(buffer)))
        buffer = []
        word_count = 0

    for paragraph in paragraphs:
        paragraph_words = tokenize(paragraph)
        if buffer and word_count + len(paragraph_words) > max_words:
            flush()
        buffer.append(paragraph)
        word_count += len(paragraph_words)

    flush()
    return chunks


class RagIndex:
    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks
        self._chunk_tokens = [tokenize(chunk.text) for chunk in chunks]
        self._document_frequency = self._build_document_frequency()

    @classmethod
    def from_directory(cls, data_dir: Path) -> "RagIndex":
        chunks: list[Chunk] = []
        for source, text in load_markdown_documents(data_dir):
            chunks.extend(chunk_text(source, text))
        return cls(chunks)

    def search(self, query: str, top_k: int = 3) -> list[SearchResult]:
        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        query_terms = set(query_tokens)
        scored: list[SearchResult] = []
        for chunk, chunk_tokens in zip(self.chunks, self._chunk_tokens):
            score = self._score(query_terms, chunk_tokens)
            if score > 0:
                scored.append(SearchResult(chunk=chunk, score=score))

        scored.sort(key=lambda result: result.score, reverse=True)
        return scored[:top_k]

    def _build_document_frequency(self) -> dict[str, int]:
        document_frequency: dict[str, int] = {}
        for tokens in self._chunk_tokens:
            for token in set(tokens):
                document_frequency[token] = document_frequency.get(token, 0) + 1
        return document_frequency

    def _score(self, query_terms: set[str], chunk_tokens: list[str]) -> float:
        if not chunk_tokens:
            return 0.0

        token_counts: dict[str, int] = {}
        for token in chunk_tokens:
            token_counts[token] = token_counts.get(token, 0) + 1

        score = 0.0
        total_chunks = max(len(self.chunks), 1)
        for term in query_terms:
            term_frequency = token_counts.get(term, 0)
            if term_frequency == 0:
                continue
            inverse_document_frequency = math.log((1 + total_chunks) / (1 + self._document_frequency.get(term, 0))) + 1
            score += term_frequency * inverse_document_frequency
        return score / math.sqrt(len(chunk_tokens))


def default_index() -> RagIndex:
    return RagIndex.from_directory(Path(__file__).parent / "data")
