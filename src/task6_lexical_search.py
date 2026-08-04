"""
Task 6 — Lexical Search Module (BM25).

Mặc định sử dụng BM25. Nếu dùng phương pháp khác (TF-IDF, Elasticsearch,
Weaviate BM25 built-in), hãy giải thích cơ chế trong buổi demo → +5 bonus.

Cài đặt:
    pip install rank-bm25

BM25 hoạt động thế nào:
    - Term Frequency (TF): từ xuất hiện nhiều trong document → điểm cao
    - Inverse Document Frequency (IDF): từ hiếm → quan trọng hơn
    - Document length normalization: document dài không bị ưu tiên quá mức
    - Formula: score(q,d) = Σ IDF(qi) * (tf(qi,d) * (k1+1)) / (tf(qi,d) + k1*(1-b+b*|d|/avgdl))
    - k1=1.5 (term saturation), b=0.75 (length normalization)
"""

import math
import re
from collections import Counter
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
STANDARDIZED_DIR = ROOT_DIR / "data" / "standardized"

# TODO: Load corpus từ data/standardized/ hoặc từ vector store
CORPUS: list[dict] = []  # List of {'content': str, 'metadata': dict}


def _normalize_text(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


def _tokenize(text: str) -> list[str]:
    return [token for token in _normalize_text(text).split() if token]


def _load_corpus_from_docs() -> list[dict]:
    """Load chunks from standardized markdown documents."""
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
            if len(section) < 20:
                continue

            chunks.append({
                "content": section,
                "metadata": {
                    "source": md_file.name,
                    "doc_type": doc_type,
                    "chunk_index": index,
                },
            })

    return chunks


def build_bm25_index(corpus: list[dict]):
    """
    Xây dựng BM25 index từ corpus.

    Args:
        corpus: List of {'content': str, 'metadata': dict}
    """
    if not corpus:
        return {"corpus": [], "tokenized_corpus": [], "idf": {}, "avgdl": 0.0, "doc_lengths": []}

    tokenized_corpus = [_tokenize(item.get("content", "")) for item in corpus]
    doc_lengths = [len(tokens) for tokens in tokenized_corpus]
    avgdl = sum(doc_lengths) / len(doc_lengths) if doc_lengths else 0.0

    doc_freq = Counter()
    for tokens in tokenized_corpus:
        doc_freq.update(set(tokens))

    idf = {}
    n_docs = len(tokenized_corpus)
    for term, df in doc_freq.items():
        idf[term] = math.log((n_docs - df + 0.5) / (df + 0.5) + 1.0)

    return {
        "corpus": corpus,
        "tokenized_corpus": tokenized_corpus,
        "idf": idf,
        "avgdl": avgdl,
        "doc_lengths": doc_lengths,
        "k1": 1.5,
        "b": 0.75,
    }


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Tìm kiếm từ khóa sử dụng BM25.

    Args:
        query: Câu truy vấn
        top_k: Số lượng kết quả tối đa

    Returns:
        List of {
            'content': str,
            'score': float,      # BM25 score
            'metadata': dict
        }
        Sorted by score descending.
    """
    if not query or top_k <= 0:
        return []

    global CORPUS
    if not CORPUS:
        CORPUS = _load_corpus_from_docs()

    if not CORPUS:
        return []

    index = build_bm25_index(CORPUS)
    query_terms = _tokenize(query)
    if not query_terms:
        return []

    scores = []
    for idx, tokens in enumerate(index["tokenized_corpus"]):
        doc_length = index["doc_lengths"][idx]
        avgdl = index["avgdl"]
        score = 0.0
        tf_counter = Counter(tokens)
        for term in query_terms:
            if term not in index["idf"]:
                continue
            tf = tf_counter.get(term, 0)
            if tf == 0:
                continue

            denominator = tf + index["k1"] * (1 - index["b"] + index["b"] * doc_length / avgdl) if avgdl > 0 else tf + index["k1"]
            score += index["idf"][term] * (tf * (index["k1"] + 1) / denominator)

        if score > 0:
            scores.append((score, idx))

    scores.sort(key=lambda item: item[0], reverse=True)
    results = []
    for score, idx in scores[:top_k]:
        results.append({
            "content": CORPUS[idx]["content"],
            "score": round(float(score), 6),
            "metadata": CORPUS[idx]["metadata"],
        })

    return results


if __name__ == "__main__":
    # Test
    results = lexical_search("phương thức thanh toán shopee", top_k=5)
    for r in results:
        print(f"[{r['score']:.3f}] {r['content'][:100]}...")
