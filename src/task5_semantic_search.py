"""
Task 5 — Semantic Search Module.

Viết module tìm kiếm ngữ nghĩa (dense retrieval) trên vector store.

Yêu cầu:
    - Input: query string + top_k
    - Output: danh sách chunks có score, sorted descending
    - Phải tương thích với embedding model và vector store ở Task 4
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
STANDARDIZED_DIR = ROOT_DIR / "data" / "standardized"


def _normalize_text(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _tokenize(text: str) -> list[str]:
    return [token for token in _normalize_text(text).split() if token]


def _build_hyde_document(query: str) -> str:
    """Tạo một document giả định (HyDE-style) từ câu truy vấn."""
    tokens = _tokenize(query)
    if not tokens:
        return ""

    expanded = list(tokens)
    synonym_map = {
        "refund": ["refund", "return", "moneyback", "reimburse"],
        "return": ["return", "refund", "exchange", "resend"],
        "payment": ["payment", "pay", "checkout", "transaction"],
        "policy": ["policy", "rule", "guideline", "regulation", "terms", "conditions"],
        "seller": ["seller", "merchant", "shop"],
        "order": ["order", "purchase", "delivery"],
    }

    for token in tokens:
        expanded.extend(synonym_map.get(token, []))

    if any(token in {"refund", "return", "policy", "payment", "order"} for token in tokens):
        expanded.extend(["support", "guide", "help", "document"])

    return " ".join(dict.fromkeys(expanded))


def _cosine_similarity(text_a: str, text_b: str) -> float:
    """Tính cosine similarity giữa 2 đoạn text bằng bag-of-words."""
    if not text_a or not text_b:
        return 0.0

    counts_a = Counter(_tokenize(text_a))
    counts_b = Counter(_tokenize(text_b))
    if not counts_a or not counts_b:
        return 0.0

    terms = set(counts_a) | set(counts_b)
    dot = sum(counts_a[t] * counts_b[t] for t in terms)
    norm_a = sum(value * value for value in counts_a.values()) ** 0.5
    norm_b = sum(value * value for value in counts_b.values()) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _load_chunks_from_docs() -> list[dict]:
    """Tạo chunks từ dữ liệu chuẩn hoá khi vector store chưa có sẵn."""
    chunks: list[dict] = []
    if not STANDARDIZED_DIR.exists():
        return chunks

    for md_file in sorted(STANDARDIZED_DIR.rglob("*.md")):
        if not md_file.is_file():
            continue

        content = md_file.read_text(encoding="utf-8", errors="ignore")
        doc_type = "legal" if "legal" in str(md_file) else "news"
        sections = [part.strip() for part in re.split(r"\n\s*\n", content) if part.strip()]

        for index, section in enumerate(sections):
            if len(section) < 40:
                continue

            metadata = {
                "source": md_file.name,
                "doc_type": doc_type,
                "chunk_index": index,
            }
            chunks.append({"content": section, "metadata": metadata})

    return chunks


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Tìm kiếm ngữ nghĩa sử dụng vector similarity.

    Args:
        query: Câu truy vấn
        top_k: Số lượng kết quả tối đa

    Returns:
        List of {
            'content': str,      # Nội dung chunk
            'score': float,      # Cosine similarity score
            'metadata': dict     # source, doc_type, chunk_index
        }
        Sorted by score descending.
    """
    if not query or top_k <= 0:
        return []

    # Ưu tiên dùng vector store/embedding từ Task 4 nếu có; nếu chưa sẵn thì fallback sang cosine bag-of-words.
    try:
        from .task4_chunking_indexing import (  # type: ignore
            embed_texts,
            get_collection,
        )

        collection = get_collection()
        if collection is not None:
            query_texts = [query, _build_hyde_document(query)]
            embeddings = embed_texts(query_texts)
            query_vector = embeddings[0]
            hyde_vector = embeddings[1]
            results = collection.query(
                query_embeddings=[query_vector],
                n_results=top_k,
                include=["documents", "metadatas", "distances"],
            )
            output = []
            for doc, meta, dist in zip(
                results.get("documents", [[]])[0],
                results.get("metadatas", [[]])[0],
                results.get("distances", [[]])[0],
            ):
                score = max(0.0, 1.0 - float(dist))
                if score > 0:
                    output.append({
                        "content": doc,
                        "score": round(score, 4),
                        "metadata": meta or {},
                    })
            if output:
                output.sort(key=lambda item: item["score"], reverse=True)
                return output[:top_k]

            # Nếu vector store tồn tại nhưng không trả về kết quả, vẫn thử dùng HyDE vector để làm điểm chấm nhẹ.
            if hyde_vector:
                results = collection.query(
                    query_embeddings=[hyde_vector],
                    n_results=top_k,
                    include=["documents", "metadatas", "distances"],
                )
                output = []
                for doc, meta, dist in zip(
                    results.get("documents", [[]])[0],
                    results.get("metadatas", [[]])[0],
                    results.get("distances", [[]])[0],
                ):
                    score = max(0.0, 1.0 - float(dist))
                    if score > 0:
                        output.append({
                            "content": doc,
                            "score": round(score, 4),
                            "metadata": meta or {},
                        })
                if output:
                    output.sort(key=lambda item: item["score"], reverse=True)
                    return output[:top_k]
    except Exception:
        pass

    chunks = _load_chunks_from_docs()
    if not chunks:
        return []

    hyde_query = _build_hyde_document(query)
    scored_results = []
    for chunk in chunks:
        content = str(chunk.get("content", ""))
        score = 0.7 * _cosine_similarity(query, content) + 0.3 * _cosine_similarity(hyde_query, content)
        if score > 0:
            scored_results.append({
                "content": content,
                "score": round(float(score), 4),
                "metadata": chunk.get("metadata", {}),
            })

    scored_results.sort(key=lambda item: item["score"], reverse=True)
    return scored_results[:top_k]


if __name__ == "__main__":
    # Test
    results = semantic_search("quy định trả hàng hoàn tiền shopee", top_k=5)
    for r in results:
        print(f"[{r['score']:.3f}] {r['content'][:100]}...")
