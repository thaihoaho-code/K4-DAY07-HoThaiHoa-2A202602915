from __future__ import annotations

import math
import re
# import numpy as np


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        # Split into sentences, group into chunks
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        chunks: list[str] = []
        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            chunk = " ".join(sentences[i : i + self.max_sentences_per_chunk])
            chunks.append(chunk)
        return chunks


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = max(1, chunk_size)

    def _fallback_chunks(self, text: str) -> list[str]:
        if not text:
            return []
        chunks: list[str] = []
        for start in range(0, len(text), self.chunk_size):
            chunk = text[start : start + self.chunk_size]
            if chunk:
                chunks.append(chunk)
        return chunks

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        normalized = text.strip()
        if not normalized:
            return []
        if len(normalized) <= self.chunk_size:
            return [normalized]
        return self._split(normalized, list(self.separators))

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if not current_text:
            return []
        current_text = current_text.strip()
        if not current_text:
            return []
        if len(current_text) <= self.chunk_size:
            return [current_text]

        if not remaining_separators:
            return self._fallback_chunks(current_text)

        separator = remaining_separators[0]
        if separator == "":
            return self._fallback_chunks(current_text)

        parts = [part.strip() for part in current_text.split(separator) if part.strip()]
        if len(parts) <= 1:
            return self._split(current_text, remaining_separators[1:])

        merged: list[str] = []
        current_piece = ""

        for part in parts:
            candidate = f"{current_piece}{separator}{part}".strip() if current_piece else part
            if len(candidate) <= self.chunk_size:
                current_piece = candidate
                continue

            if current_piece:
                merged.append(current_piece)
                current_piece = part
            else:
                if len(part) > self.chunk_size:
                    merged.extend(self._split(part, remaining_separators[1:]))
                else:
                    current_piece = part

        if current_piece:
            merged.append(current_piece)

        final_chunks: list[str] = []
        buffer = ""
        for piece in merged:
            if not piece:
                continue
            if not buffer:
                buffer = piece
                continue
            combined = f"{buffer} {piece}".strip()
            if len(combined) <= self.chunk_size:
                buffer = combined
            else:
                final_chunks.append(buffer)
                buffer = piece

        if buffer:
            final_chunks.append(buffer)

        result: list[str] = []
        for chunk in final_chunks:
            if len(chunk) <= self.chunk_size:
                result.append(chunk)
            else:
                result.extend(self._split(chunk, remaining_separators[1:]))

        return result




def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    dot_product = _dot(vec_a, vec_b)
    norm_a = math.sqrt(_dot(vec_a, vec_a))
    norm_b = math.sqrt(_dot(vec_b, vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        if not text:
            return {
                "fixed_size": {"count": 0, "avg_length": 0, "chunks": []},
                "by_sentences": {"count": 0, "avg_length": 0, "chunks": []},
                "recursive": {"count": 0, "avg_length": 0, "chunks": []},
            }

        fixed_chunker = FixedSizeChunker(
            chunk_size=chunk_size,
            overlap=min(50, max(0, chunk_size - 1)),
        )
        sentence_chunker = SentenceChunker(max_sentences_per_chunk=3)
        recursive_chunker = RecursiveChunker(chunk_size=chunk_size)

        strategies = {
            "fixed_size": fixed_chunker.chunk(text),
            "by_sentences": sentence_chunker.chunk(text),
            "recursive": recursive_chunker.chunk(text),
        }

        comparison = {}

        for strategy_name, chunks in strategies.items():
            lengths = [len(chunk) for chunk in chunks]
            comparison[strategy_name] = {
                "count": len(chunks),
                "avg_length": (sum(lengths) / len(lengths) if lengths else 0),
                "chunks": chunks,
            }

        return comparison